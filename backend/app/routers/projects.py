import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies import DB, CurrentUser, CurrentStudent, CurrentFaculty, CurrentFacultyOrHOD
from app.models.project import Project, ProjectFile, PipelineStatus, SubmissionType
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectSummary, ProjectStatusResponse, UploadResponse,
    BatchUploadResponse, BatchJobStatusResponse,
)
from app.utils.files import save_upload_file, get_file_type

router = APIRouter(tags=["Projects"])


def _to_summary(project: Project) -> ProjectSummary:
    score = project.evaluation.overall_score if project.evaluation else None
    return ProjectSummary(
        projectId=str(project.id),
        studentName=project.student.name,
        rollNo=project.student.roll_no or "",
        title=project.title,
        submissionType=project.submission_type,
        domain=project.domain,
        submittedOn=project.submitted_on.date().isoformat(),
        pipelineStatus=project.pipeline_status,
        overallScore=score,
    )


@router.get("/projects/my", response_model=List[ProjectSummary])
def get_my_projects(current_user: CurrentStudent, db: DB):
    """Student: list own submissions."""
    projects = (
        db.query(Project)
        .filter(Project.student_id == current_user.id)
        .order_by(Project.submitted_on.desc())
        .all()
    )
    return [_to_summary(p) for p in projects]


@router.get("/projects", response_model=List[ProjectSummary])
def get_all_projects(current_user: CurrentFacultyOrHOD, db: DB):
    """Guide/Reviewer/HOD: list all projects (guides/reviewers see only assigned)."""
    q = db.query(Project)
    if current_user.role == UserRole.guide:
        q = q.filter(Project.assigned_guide_id == current_user.id)
    elif current_user.role == UserRole.reviewer:
        q = q.filter(Project.assigned_reviewer_id == current_user.id)
    projects = q.order_by(Project.submitted_on.desc()).all()
    return [_to_summary(p) for p in projects]


@router.get("/projects/{project_id}/status", response_model=ProjectStatusResponse)
def get_project_status(project_id: str, current_user: CurrentUser, db: DB):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectStatusResponse(status=project.pipeline_status.value)


@router.post("/projects/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_project(
    current_user: CurrentStudent,
    db: DB,
    background_tasks: BackgroundTasks,
    mode: str = Form(...),
    domain: str = Form(...),
    title: Optional[str] = Form(None),
    teamMembers: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    githubUrl: Optional[str] = Form(None),
    relatedSubmissionId: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
):
    # Derive title from file name if not provided
    effective_title = title
    if not effective_title and files:
        effective_title = files[0].filename or "Uploaded Project"
    if not effective_title:
        effective_title = f"{domain} Project"

    project = Project(
        student_id=current_user.id,
        title=effective_title,
        domain=domain,
        submission_type=SubmissionType(mode),
        github_url=githubUrl,
        related_submission_id=uuid.UUID(relatedSubmissionId) if relatedSubmissionId else None,
        pipeline_status=PipelineStatus.uploaded,
        assigned_guide_id=None,  # auto-assign logic goes in Phase 2
    )
    db.add(project)
    db.flush()  # get project.id before saving files

    # Save uploaded files
    for upload_file in files:
        if upload_file.filename:
            storage_path = await save_upload_file(upload_file, str(project.id))
            pf = ProjectFile(
                project_id=project.id,
                file_type=get_file_type(upload_file.filename),
                original_filename=upload_file.filename,
                storage_path=storage_path,
            )
            db.add(pf)

    db.commit()
    db.refresh(project)

    # Background: move status to ai_processing (Phase 2 will hand off to Celery)
    background_tasks.add_task(_mark_ai_processing, project.id)

    return UploadResponse(projectId=str(project.id))


def _mark_ai_processing(project_id: uuid.UUID):
    """Placeholder background task — Phase 2 will enqueue Celery job here."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.pipeline_status = PipelineStatus.ai_processing
            db.commit()
    finally:
        db.close()


# ── Batch upload ──────────────────────────────────────────────────────────────

_batch_store: dict[str, dict] = {}   # in-memory; Phase 2 → Redis


@router.post("/projects/batch", response_model=BatchUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_upload(
    current_user: CurrentFaculty,
    db: DB,
    files: List[UploadFile] = File(...),
):
    batch_id = str(uuid.uuid4())
    _batch_store[batch_id] = {
        "total": len(files),
        "processed": 0,
        "failed": 0,
        "status": "queued",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    return BatchUploadResponse(batchId=batch_id, totalFiles=len(files))


@router.get("/projects/batch/{batch_id}/status", response_model=BatchJobStatusResponse)
def get_batch_status(batch_id: str, current_user: CurrentFacultyOrHOD):
    info = _batch_store.get(batch_id)
    if not info:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchJobStatusResponse(
        batchId=batch_id,
        totalFiles=info["total"],
        processed=info["processed"],
        failed=info["failed"],
        status=info["status"],
        startedAt=info["started_at"],
    )
