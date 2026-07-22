from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import DB, CurrentUser, CurrentFacultyOrHOD
from app.models.project import Project
from app.models.evaluation import EvaluationReport
from app.models.user import UserRole
from app.schemas.report import PublicEvaluationReport, InternalEvaluationReport, DimensionScores

router = APIRouter(tags=["Reports"])


def _empty_dimension_scores(is_abstract: bool) -> DimensionScores:
    return DimensionScores(
        novelty=0,
        feasibility=0,
        completeness=None if is_abstract else 0,
        technicalDepth=0,
        clarity=0,
        similarityRisk=0,
        publicationPotential=0,
    )


def _report_to_public(project: Project, report: EvaluationReport) -> PublicEvaluationReport:
    from app.schemas.report import SimilarityInfo, WritingQuality, CitationInfo, ImprovementWeek
    is_abstract = project.submission_type.value == "abstract"
    scores = DimensionScores(
        novelty=report.novelty_score,
        feasibility=report.feasibility_score,
        completeness=None if is_abstract else report.completeness_score,
        technicalDepth=report.technical_depth_score,
        clarity=report.clarity_score,
        similarityRisk=report.similarity_risk_score,
        publicationPotential=report.publication_potential_score,
    )
    roadmap = [ImprovementWeek(**w) for w in (report.improvement_roadmap or [])]
    wq = WritingQuality(**report.writing_quality) if report.writing_quality else None
    cit = CitationInfo(**report.citations) if report.citations else None

    return PublicEvaluationReport(
        projectId=str(project.id),
        title=project.title,
        domain=project.domain,
        submissionType=project.submission_type,
        pipelineStatus=project.pipeline_status,
        isPreliminary=project.is_preliminary,
        overallScore=report.overall_score,
        grade=report.grade,
        dimensionScores=scores,
        missingSections=report.missing_sections or [],
        similarity=SimilarityInfo(
            internalScore=report.similarity_internal,
            externalScore=report.similarity_external,
            isDuplicate=report.is_duplicate,
        ),
        feasibilityRating=report.feasibility_rating,
        noveltyVerdict=report.novelty_verdict,
        writingQuality=wq,
        citations=cit,
        strengths=report.strengths or [],
        weaknesses=report.weaknesses or [],
        improvementRoadmap=roadmap,
        badges=report.badges or [],
        percentileRanks=report.percentile_ranks or {},
    )


def _report_to_internal(
    project: Project, report: EvaluationReport
) -> InternalEvaluationReport:
    from app.schemas.report import FacultyNote, ExplainabilityAnnotation, ScoreOverrideEntry
    public = _report_to_public(project, report)

    notes = [
        FacultyNote(
            author=n.author_user.name,
            role=n.role,
            text=n.text,
            timestamp=n.timestamp.isoformat(),
        )
        for n in project.notes
    ]

    overrides = [
        ScoreOverrideEntry(
            dimension=o.dimension,
            oldValue=o.old_value,
            newValue=o.new_value,
            by=o.changed_by_name,
            comment=o.comment,
            timestamp=o.timestamp.isoformat(),
        )
        for o in (report.score_overrides or [])
    ]

    annotations = [
        ExplainabilityAnnotation(**a)
        for a in (report.explainability_annotations or [])
    ]

    return InternalEvaluationReport(
        **public.model_dump(),
        facultyNotes=notes,
        explainabilityAnnotations=annotations,
        flaggingReasons=report.flagging_reasons or [],
        assignedGuide=project.guide.name if project.guide else "",
        assignedReviewer=project.reviewer.name if project.reviewer else None,
        scoreOverrideHistory=overrides,
    )


def _get_project_or_404(project_id: str, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_or_create_report(project: Project, db: Session) -> EvaluationReport:
    """Return existing report or create a stub (Phase 1 — AI not yet wired)."""
    if project.evaluation:
        return project.evaluation

    stub = EvaluationReport(
        project_id=project.id,
        overall_score=0,
        grade="",
        novelty_score=0,
        feasibility_score=0,
        completeness_score=None if project.submission_type.value == "abstract" else 0,
        technical_depth_score=0,
        clarity_score=0,
        similarity_risk_score=0,
        publication_potential_score=0,
        strengths=["AI evaluation pending"],
        weaknesses=["AI evaluation pending"],
        improvement_roadmap=[
            {"week": 1, "focus": "Submit full document", "actions": ["Complete all sections", "Upload to the system"]}
        ],
    )
    db.add(stub)
    db.commit()
    db.refresh(stub)
    return stub


@router.get("/projects/{project_id}/report/public", response_model=PublicEvaluationReport)
def get_public_report(project_id: str, current_user: CurrentUser, db: DB):
    """Student-safe report — never includes internal fields."""
    project = _get_project_or_404(project_id, db)

    # Students can only read their own reports
    if current_user.role == UserRole.student and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    report = _get_or_create_report(project, db)
    return _report_to_public(project, report)


@router.get("/projects/{project_id}/report/internal", response_model=InternalEvaluationReport)
def get_internal_report(project_id: str, current_user: CurrentFacultyOrHOD, db: DB):
    """Full internal report — faculty/HOD only."""
    project = _get_project_or_404(project_id, db)
    report = _get_or_create_report(project, db)
    return _report_to_internal(project, report)
