"""
Module 13 — External Integrations Router
==========================================
Exposes REST endpoints for the three external integrations:

  GET  /api/integrations/trend/{topic}         — Semantic Scholar trend lookup (cached)
  GET  /api/integrations/trend/search          — Raw paper search
  POST /api/integrations/trend/refresh         — Manually trigger bulk cache refresh (HOD only)
  GET  /api/integrations/github/similar        — GitHub prior-art search for a project
  GET  /api/integrations/moodle/status         — Moodle connectivity check
  POST /api/integrations/moodle/sync           — Manually trigger Moodle submission import (HOD only)
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.dependencies import CurrentUser, CurrentFacultyOrHOD, DB
from app.models.project import Project

log = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["Module 13 — External Integrations"])


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC SCHOLAR
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/trend/{topic}", summary="Get cached trend data for a research topic")
def get_trend(topic: str, current_user: CurrentUser):
    """
    Returns trend signals from Semantic Scholar for a topic string.
    Result is served from the local cache when available (TTL 7 days).
    """
    from app.services.semantic_scholar import ss_client
    result = ss_client.get_topic_trend(topic)
    return result


@router.get("/trend/search/papers", summary="Search Semantic Scholar papers by keyword")
def search_papers(
    q: str = Query(..., description="Search query string"),
    limit: int = Query(5, ge=1, le=20),
    current_user: CurrentUser = None,
):
    """
    Live paper search against Semantic Scholar (not cached).
    Returns up to `limit` recent papers matching the query.
    """
    from app.services.semantic_scholar import ss_client
    papers = ss_client.search_papers(q, limit=limit)
    return {"query": q, "papers": papers, "count": len(papers)}


@router.post("/trend/refresh", summary="Manually trigger weekly trend cache refresh (HOD only)")
def refresh_trends(current_user: CurrentFacultyOrHOD):
    """
    Re-fetches and re-caches Semantic Scholar trend data for all default topics.
    This is the same operation the weekly Celery beat task runs automatically.
    """
    from app.services.trend_scorer import trend_scorer_service
    try:
        summary = trend_scorer_service.refresh_trend_data()
        ok = sum(1 for v in summary.values() if v == "refreshed")
        return {"status": "ok", "refreshed": ok, "total": len(summary), "detail": summary}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Trend refresh failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/github/similar", summary="Find similar public GitHub repos for a project")
def github_similar(
    project_id: str = Query(..., description="AcadEval project UUID"),
    current_user: CurrentUser = None,
    db: DB = None,
):
    """
    Uses the project's extracted entity list (algorithms, technologies, frameworks)
    to search GitHub for similar public repositories.  Result appears in the
    Novelty Report as a supporting `github_signal` block — it does NOT affect
    the numeric Novelty Index.
    """
    import uuid as _uuid
    from app.services.github_client import github_client

    project = db.query(Project).filter(Project.id == _uuid.UUID(project_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    entities = project.extracted_entities or {}
    terms: list[str] = []
    for key in ("algorithms", "technologies", "frameworks", "libraries"):
        terms.extend(entities.get(key, []))

    if not terms:
        # Fall back to project title words if no entities extracted yet
        terms = project.title.split()[:5]

    signal = github_client.find_similar_repos(terms)
    return {
        "project_id": project_id,
        "project_title": project.title,
        "github_signal": signal,
    }


@router.get("/github/search", summary="Direct GitHub repo search by keyword")
def github_search(
    q: str = Query(..., description="Search terms"),
    language: Optional[str] = Query(None, description="Language filter e.g. Python"),
    current_user: CurrentUser = None,
):
    """Ad-hoc GitHub repo search — useful for faculty exploring a topic."""
    from app.services.github_client import github_client
    terms = q.split()
    result = github_client.find_similar_repos(terms, language=language)
    return result
