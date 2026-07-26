import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VivaSession(Base):
    __tablename__ = "viva_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    
    # Question pool generated from project knowledge graph
    questions: Mapped[list] = mapped_column(JSONB, default=list)
    # Detailed answer records containing multi-dimensional evaluations
    answers: Mapped[list] = mapped_column(JSONB, default=list)
    # Historical scores and metrics
    scores: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Research metrics: Knowledge Coverage Score (KCS) & CAT state
    kcs: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    current_difficulty: Mapped[str] = mapped_column(String(32), default="Easy")
    difficulty_progression: Mapped[list] = mapped_column(JSONB, default=list)
    consecutive_correct: Mapped[int] = mapped_column(default=0)
    consecutive_wrong: Mapped[int] = mapped_column(default=0)
    
    # Session lifecycle & output report
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship("Project", back_populates="viva_sessions")
