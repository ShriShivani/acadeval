import os
from pathlib import Path

# Embedding & Walk Configurations
EMBEDDING_DIM = 64
WALK_LENGTH = 15
NUM_WALKS = 100
WINDOW = 5
MIN_COUNT = 1

# Weights directory setup
ROOT_DIR = Path(__file__).resolve().parent
WEIGHTS_DIR = ROOT_DIR / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

RIDGE_MODEL_PATH = WEIGHTS_DIR / "ridge_novelty_combiner.joblib"
EMBEDDINGS_CACHE_PATH = WEIGHTS_DIR / "project_embeddings_cache.json"

# Default weights for unweighted average (v1)
DEFAULT_WEIGHTS = {
    "graph_distance": 0.2,
    "feature_rarity": 0.2,
    "relationship_rarity": 0.2,
    "graph_density": 0.2,
    "new_connection": 0.2
}
