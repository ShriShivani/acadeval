from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import DB, CurrentUser, CurrentStudent, CurrentFacultyOrHOD
from app.models.appeal import Appeal, AppealStatus
from app.models.project import Project
from app.models.user import UserRole
from app.schemas.appeal import AppealCreate, AppealResolve, AppealOut

router = APIRouter(tags=["Appeals"])


def _to_out(appeal: Appeal) -> AppealOut:
    return AppealOut(
        appealId=str(appeal.id),
        projectId=str(appeal.project_id),
        projectTitle=appeal.project.title,
        dimension=appeal.dimension,
        originalScore=appeal.original_score,
        studentJustification=appeal.student_justification,
        status=appeal.status,
        facultyResponse=appeal.faculty_response,
        resolvedScore=appeal.resolved_score,
        createdAt=appeal.created_at.isoformat(),
        resolvedAt=appeal.resolved_at.isoformat() if appeal.resolved_at else None,
    )


@router.get("/appeals", response_model=list[AppealOut])
def list_appeals(current_user: CurrentUser, db: DB):
    """Students see their own; faculty/HOD see all in their scope."""
    q = db.query(Appeal)
    if current_user.role == UserRole.student:
        q = q.filter(Appeal.student_id == current_user.id)
    return [_to_out(a) for a in q.order_by(Appeal.created_at.desc()).all()]


@router.post("/appeals", response_model=AppealOut, status_code=status.HTTP_201_CREATED)
def create_appeal(payload: AppealCreate, current_user: CurrentStudent, db: DB):
    # Validate project ownership
    project = db.query(Project).filter(
        Project.id == payload.projectId,
        Project.student_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    appeal = Appeal(
        project_id=project.id,
        student_id=current_user.id,
        dimension=payload.dimension,
        original_score=payload.originalScore,
        student_justification=payload.studentJustification,
    )
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return _to_out(appeal)


@router.patch("/appeals/{appeal_id}", response_model=AppealOut)
def resolve_appeal(
    appeal_id: str,
    payload: AppealResolve,
    current_user: CurrentFacultyOrHOD,
    db: DB,
):
    appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    if payload.action == "approve":
        appeal.status = AppealStatus.resolved
        appeal.resolved_score = payload.resolvedScore
    elif payload.action == "reject":
        appeal.status = AppealStatus.rejected
    else:
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")

    appeal.faculty_response = payload.facultyResponse
    appeal.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appeal)
    return _to_out(appeal)
