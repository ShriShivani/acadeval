import logging
import joblib
import numpy as np
from app.module5_novelty import config

log = logging.getLogger(__name__)

class NoveltyCombiner:
    @staticmethod
    def combine_signals(normalized_signals: dict) -> float:
        """
        Combines the 5 normalized signals into a single score.
        If a Ridge regression model exists at RIDGE_MODEL_PATH, it uses it for prediction.
        Otherwise, falls back to the unweighted average (V1).
        """
        keys = ["graph_distance", "feature_rarity", "relationship_rarity", "graph_density", "new_connection"]
        
        # Ensure all signals exist in dict
        features = []
        for key in keys:
            features.append(normalized_signals.get(key, 0.5))
            
        # Try loading Ridge regression model (V2)
        if config.RIDGE_MODEL_PATH.exists():
            try:
                model = joblib.load(config.RIDGE_MODEL_PATH)
                # Model predicts on scale [0, 1] or [0, 100]. Let's format input
                X = np.array([features])
                score = float(model.predict(X)[0])
                # Ensure predicted score is bounded between 0 and 100
                return round(np.clip(score, 0.0, 100.0), 1)
            except Exception as e:
                log.warning("Failed to load Ridge regression model: %s. Falling back to average.", e)
                
        # Default V1: Unweighted average scaled to 0-100
        avg_score = sum(features) / len(features)
        return round(float(avg_score * 100.0), 1)
