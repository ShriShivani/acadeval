import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class NovelBench(Base):
    __tablename__ = "AcadEval_NovelBench"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(50), nullable=False, unique=True, index=True)
    graph_distance = Column(Float, nullable=False)
    feature_rarity = Column(Float, nullable=False)
    relationship_rarity = Column(Float, nullable=False)
    graph_density = Column(Float, nullable=False)
    new_connection = Column(Float, nullable=False)
    novelty_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    similar_projects = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "graph_distance": self.graph_distance,
            "feature_rarity": self.feature_rarity,
            "relationship_rarity": self.relationship_rarity,
            "graph_density": self.graph_density,
            "new_connection": self.new_connection,
            "novelty_score": self.novelty_score,
            "confidence": self.confidence,
            "similar_projects": self.similar_projects
        }
