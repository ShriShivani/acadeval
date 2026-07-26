import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrendBaseRecord(Base):
    """
    Module 8 — AcadEval_TrendBase PostgreSQL Table
    Stores yearly paper counts and citation counts per research topic / technology.
    """
    __tablename__ = "acadeval_trendbase"
    __table_args__ = (
        UniqueConstraint("topic", "year", name="uq_trendbase_topic_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    paper_count: Mapped[int] = mapped_column(Integer, default=0)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
