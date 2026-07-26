import logging
import networkx as nx
import numpy as np
from app.module5_novelty.utils.embeddings import get_node_embeddings
from app.module5_novelty.utils.similarity import calculate_cosine_similarity_matrix

log = logging.getLogger(__name__)

class GraphDistanceService:
    @staticmethod
    def calculate_distance(G: nx.MultiDiGraph, new_project_node_id: int, force_recompute: bool = False) -> dict:
        """
        Signal 1 — Graph Distance
        Generates Node2Vec structural embeddings, and compares vectors via cosine similarity.
        """
        embeddings = get_node_embeddings(G, force_recompute=force_recompute)
        target_key = str(new_project_node_id)
        
        if target_key not in embeddings:
            log.warning("Project node %s not found in embeddings.", new_project_node_id)
            return {
                "distance": 1.0,
                "closest_project": None,
                "similar_projects": []
            }
        
        target_vec = embeddings[target_key]
        
        # Get all other project nodes and their embeddings
        other_projects = [
            (nid, attr.get("name", str(nid)))
            for nid, attr in G.nodes(data=True)
            if attr.get("type") == "Project" and nid != new_project_node_id
        ]
        
        if not other_projects:
            return {
                "distance": 1.0,
                "closest_project": None,
                "similar_projects": []
            }
            
        other_ids = [str(nid) for nid, _ in other_projects]
        other_vecs = [embeddings[oid] for oid in other_ids if oid in embeddings]
        
        if not other_vecs:
            return {
                "distance": 1.0,
                "closest_project": None,
                "similar_projects": []
            }
            
        sims = calculate_cosine_similarity_matrix(target_vec, other_vecs)
        max_sim = float(sims.max())
        graph_distance = float(1.0 - max_sim)
        
        # Determine closest project
        closest_idx = int(sims.argmax())
        closest_project_id = other_projects[closest_idx][1]  # Using Project Name/Code (e.g. P103)
        
        # Get sorted similar projects
        sorted_indices = np.argsort(-sims)
        similar_projects = [other_projects[idx][1] for idx in sorted_indices[:5]]
        
        return {
            "distance": float(np.clip(graph_distance, 0.0, 1.0)),
            "closest_project": closest_project_id,
            "similar_projects": similar_projects
        }
