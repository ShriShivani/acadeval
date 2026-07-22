from typing import Optional
from pydantic import BaseModel
from app.models.appeal import AppealStatus


class AppealCreate(BaseModel):
    projectId: str
    dimension: str
    originalScore: float
    studentJustification: str


class AppealResolve(BaseModel):
    action: str          # "approve" | "reject"
    resolvedScore: Optional[float] = None
    facultyResponse: str


class AppealOut(BaseModel):
    appealId: str
    projectId: str
    projectTitle: str
    dimension: str
    originalScore: float
    studentJustification: str
    status: AppealStatus
    facultyResponse: Optional[str] = None
    resolvedScore: Optional[float] = None
    createdAt: str
    resolvedAt: Optional[str] = None

    model_config = {"from_attributes": True}
