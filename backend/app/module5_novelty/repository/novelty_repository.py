from sqlalchemy.orm import Session
from app.module5_novelty.models.novelty_models import NovelBench

class NoveltyRepository:
    @staticmethod
    def save_novelty_result(db: Session, result_data: dict) -> NovelBench:
        existing = db.query(NovelBench).filter(NovelBench.project_id == result_data["project_id"]).first()
        if existing:
            existing.graph_distance = result_data["graph_distance"]
            existing.feature_rarity = result_data["feature_rarity"]
            existing.relationship_rarity = result_data["relationship_rarity"]
            existing.graph_density = result_data["graph_density"]
            existing.new_connection = result_data["new_connection"]
            existing.novelty_score = result_data["novelty_score"]
            existing.confidence = result_data["confidence"]
            existing.similar_projects = result_data["similar_projects"]
            db.commit()
            db.refresh(existing)
            return existing
        else:
            db_obj = NovelBench(**result_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    @staticmethod
    def get_novelty_result(db: Session, project_id: str) -> NovelBench | None:
        return db.query(NovelBench).filter(NovelBench.project_id == project_id).first()
