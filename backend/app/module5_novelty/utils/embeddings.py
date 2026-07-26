import networkx as nx
from app.module5_novelty.utils.node2vec_model import get_project_embeddings

def get_node_embeddings(G: nx.Graph, force_recompute: bool = False) -> dict[str, list[float]]:
    return get_project_embeddings(G, force_recompute=force_recompute)
