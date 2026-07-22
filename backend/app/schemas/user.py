from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole


class UserOut(BaseModel):
    userId: str
    name: str
    email: str
    rollNo: Optional[str] = None
    role: UserRole
    department: str
    isActive: bool
    joinedAt: str

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: UserRole


class LeaderboardEntry(BaseModel):
    rank: int
    studentName: str
    rollNo: str
    projectTitle: str
    domain: str
    overallScore: float
    badges: list[str]
    isCurrentUser: bool = False
