import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.dependencies import DB, CurrentUser
from app.module5_novelty.services.novelty_engine import NoveltyEngine

log = logging.getLogger(__name__)

router = APIRouter(prefix="/novelty", tags=["Module 5 — Graph-Based Novelty Engine"])

class CalculateRequest(BaseModel):
    project_id: str = Field(..., example="P204")

class CalculateResponse(BaseModel):
    status: str
    novelty_score: float
    report: dict

@router.post("/calculate", response_model=CalculateResponse, summary="Calculate graph-based novelty score using NetworkX MultiDiGraph")
def calculate_novelty_score(payload: CalculateRequest, db: DB, current_user: CurrentUser):
    """
    Calculates the 5 explainable novelty signals for a project using Node2Vec and NetworkX graph metrics.
    Stores the result in AcadEval_NovelBench and returns the final score.
    """
    try:
        report = NoveltyEngine.calculate_novelty(db, {"project_id": payload.project_id})
        return {
            "status": "completed",
            "novelty_score": report["novelty_score"],
            "report": report
        }
    except Exception as e:
        log.error("Failed to calculate novelty score for project %s: %s", payload.project_id, e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during graph-based novelty scoring: {e}"
        )
