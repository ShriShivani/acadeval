from typing import Optional
from pydantic import BaseModel


class VivaQuestion(BaseModel):
    questionId: str
    text: str
    category: str
    difficulty: str   # "Easy" | "Medium" | "Hard"


class VivaAnswerSubmit(BaseModel):
    sessionId: str
    questionId: str
    answer: str


class VivaAnswerResult(BaseModel):
    questionId: str
    score: int        # 0-5
    maxScore: int = 5
    feedback: str
    keyPoints: list[str] = []
