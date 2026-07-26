import json
import logging
import networkx as nx
from node2vec import Node2Vec
from app.module5_novelty import config

log = logging.getLogger(__name__)

def load_cached_embeddings() -> dict[str, list[float]]:
    path = config.EMBEDDINGS_CACHE_PATH
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.warning("Failed to load cached embeddings: %s", e)
        return {}

def save_embeddings_cache(cache: dict[str, list[float]]):
    path = config.EMBEDDINGS_CACHE_PATH
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        log.warning("Failed to save embeddings cache: %s", e)

def compute_node2vec_embeddings(G: nx.Graph) -> dict[str, list[float]]:
    """Runs Node2Vec on the NetworkX graph and returns project node embeddings."""
    project_nodes = [nid for nid, attr in G.nodes(data=True) if attr.get("type") == "Project"]
    if not project_nodes:
        return {}

    # If G has very few nodes or edges, node2vec might fail. Handle G size.
    if G.number_of_nodes() < 2 or G.number_of_edges() == 0:
        # Fallback trivial embeddings for small/empty graphs
        log.warning("Graph too small for Node2Vec. Using fallback zero embeddings.")
        return {str(nid): [0.0] * config.EMBEDDING_DIM for nid in project_nodes}

    try:
        # Precompute walks on the undirected representation of G
        undirected_G = G.to_undirected()
        
        # Adjust parameters if graph is extremely small to prevent walk index errors
        walk_len = min(config.WALK_LENGTH, undirected_G.number_of_nodes())
        
        n2v = Node2Vec(
            undirected_G,
            dimensions=config.EMBEDDING_DIM,
            walk_length=walk_len,
            num_walks=config.NUM_WALKS,
            workers=1,
            quiet=True
        )
        model = n2v.fit(window=config.WINDOW, min_count=config.MIN_COUNT, batch_words=4)
        
        embeddings = {}
        for nid in project_nodes:
            nid_str = str(nid)
            if nid_str in model.wv:
                embeddings[nid_str] = [float(val) for val in model.wv[nid_str]]
            else:
                embeddings[nid_str] = [0.0] * config.EMBEDDING_DIM
        return embeddings
    except Exception as e:
        log.error("Failed to run Node2Vec: %s", e, exc_info=True)
        # Fallback to zero vectors
        return {str(nid): [0.0] * config.EMBEDDING_DIM for nid in project_nodes}

def get_project_embeddings(G: nx.Graph, force_recompute: bool = False) -> dict[str, list[float]]:
    """Retrieves project embeddings. Recomputes Node2Vec only if cache is invalid or missing projects."""
    cache = load_cached_embeddings()
    project_nodes_strs = {str(nid) for nid, attr in G.nodes(data=True) if attr.get("type") == "Project"}
    
    # Check if we have cached embeddings for all project nodes in G
    has_all_cached = project_nodes_strs.issubset(cache.keys())
    
    if force_recompute or not has_all_cached or not cache:
        log.info("Computing Node2Vec embeddings (cache missing/stale)...")
        new_embeddings = compute_node2vec_embeddings(G)
        cache.update(new_embeddings)
        # Clean up any cached items no longer in graph
        cache = {k: v for k, v in cache.items() if k in project_nodes_strs}
        save_embeddings_cache(cache)
    
    return cache
