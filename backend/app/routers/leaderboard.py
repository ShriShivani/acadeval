from fastapi import APIRouter
from sqlalchemy import func

from app.dependencies import DB, CurrentUser
from app.models.project import Project, PipelineStatus
from app.models.evaluation import EvaluationReport
from app.models.user import User, UserRole
from app.schemas.user import LeaderboardEntry

router = APIRouter(tags=["Leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(current_user: CurrentUser, db: DB):
    """Top 20 reviewed projects ranked by overall score, department-wide."""
    results = (
        db.query(Project, EvaluationReport, User)
        .join(EvaluationReport, Project.id == EvaluationReport.project_id)
        .join(User, Project.student_id == User.id)
        .filter(Project.pipeline_status == PipelineStatus.reviewed)
        .order_by(EvaluationReport.overall_score.desc())
        .limit(20)
        .all()
    )

    entries = []
    for rank, (project, report, student) in enumerate(results, start=1):
        entries.append(
            LeaderboardEntry(
                rank=rank,
                studentName=student.name,
                rollNo=student.roll_no or "",
                projectTitle=project.title,
                domain=project.domain,
                overallScore=report.overall_score,
                badges=report.badges or [],
                isCurrentUser=(student.id == current_user.id),
            )
        )
    return entries
