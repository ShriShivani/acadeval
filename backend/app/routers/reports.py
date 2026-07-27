from typing import List
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
        novelty=report.novelty_score or 75.0,
        feasibility=report.feasibility_score or 80.0,
        completeness=None if is_abstract else (report.completeness_score or 70.0),
        technicalDepth=report.technical_depth_score or 82.0,
        clarity=report.clarity_score or 80.0,
        similarityRisk=report.similarity_risk_score or 15.0,
        publicationPotential=report.publication_potential_score or 85.0,
    )
    roadmap = [
        ImprovementWeek(week=w.get("week", idx + 1), focus=w.get("focus", "Task"), actions=w.get("actions", []))
        for idx, w in enumerate(report.improvement_roadmap or [])
        if isinstance(w, dict)
    ]

    wq = None
    if report.writing_quality and isinstance(report.writing_quality, dict):
        raw_wq = report.writing_quality
        readability = raw_wq.get("readability") or raw_wq.get("metrics", {}).get("readability") or 75.0
        passive_count = raw_wq.get("passiveVoiceCount") or raw_wq.get("metrics", {}).get("passive_voice_count") or 5
        tone_flags = raw_wq.get("toneFlags") or raw_wq.get("flags") or []
        wq = WritingQuality(
            readability=float(readability),
            passiveVoiceCount=int(passive_count),
            toneFlags=[str(f) for f in tone_flags],
        )

    cit = None
    if report.citations and isinstance(report.citations, dict):
        raw_cit = report.citations
        ieee = raw_cit.get("ieeeCompliancePercent") or raw_cit.get("summary", {}).get("ieee_compliance_percent") or 85.0
        missing = raw_cit.get("missingReferences") or raw_cit.get("flags") or []
        cit = CitationInfo(
            ieeeCompliancePercent=float(ieee),
            missingReferences=[str(m) for m in missing],
        )

    return PublicEvaluationReport(
        projectId=str(project.id),
        title=project.title,
        domain=project.domain or "General CSE",
        submissionType=project.submission_type,
        pipelineStatus=project.pipeline_status,
        isPreliminary=bool(project.is_preliminary),
        overallScore=report.overall_score or 75.0,
        grade=report.grade or "A",
        dimensionScores=scores,
        missingSections=report.missing_sections or [],
        similarity=SimilarityInfo(
            internalScore=report.similarity_internal or 0.0,
            externalScore=report.similarity_external or 0.0,
            isDuplicate=bool(report.is_duplicate),
        ),
        feasibilityRating=report.feasibility_rating or "High",
        noveltyVerdict=report.novelty_verdict or "Novel",
        writingQuality=wq,
        citations=cit,
        strengths=report.strengths or ["Strong technical structure"],
        weaknesses=report.weaknesses or ["Add baseline comparison"],
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
            author=getattr(n, "author_user", None).name if getattr(n, "author_user", None) else "Faculty",
            role=n.role or "guide",
            text=n.text or "",
            timestamp=n.timestamp.isoformat() if hasattr(n, "timestamp") and n.timestamp else "",
        )
        for n in (project.notes or [])
    ]

    overrides = [
        ScoreOverrideEntry(
            dimension=o.dimension,
            oldValue=o.old_value,
            newValue=o.new_value,
            by=o.changed_by_name,
            comment=o.comment,
            timestamp=o.timestamp.isoformat() if hasattr(o, "timestamp") and o.timestamp else "",
        )
        for o in (report.score_overrides or [])
        if hasattr(o, "dimension")
    ]

    annotations = [
        ExplainabilityAnnotation(
            sentence=a.get("sentence", ""),
            weight=float(a.get("weight", 0.0)),
            reason=a.get("reason", "")
        )
        for a in (report.explainability_annotations or [])
        if isinstance(a, dict)
    ]

    return InternalEvaluationReport(
        **public.model_dump(),
        facultyNotes=notes,
        explainabilityAnnotations=annotations,
        flaggingReasons=report.flagging_reasons or [],
        assignedGuide=project.guide.name if getattr(project, "guide", None) else "Guide Unassigned",
        assignedReviewer=project.reviewer.name if getattr(project, "reviewer", None) else None,
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


@router.get("/projects/my/reports", response_model=List[PublicEvaluationReport])
def get_my_reports(current_user: CurrentUser, db: DB):
    """Student: list evaluation reports for all own submissions."""
    projects = (
        db.query(Project)
        .filter(Project.student_id == current_user.id)
        .order_by(Project.submitted_on.desc())
        .all()
    )
    reports = []
    for p in projects:
        rep = _get_or_create_report(p, db)
        reports.append(_report_to_public(p, rep))
    return reports


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
