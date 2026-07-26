import networkx as nx

class FeatureRarityService:
    @staticmethod
    def calculate_rarity(G: nx.MultiDiGraph, new_project_node_id: int) -> dict:
        """
        Signal 2 — Feature Rarity
        For every entity node the new project connects to, rarity is the inverse
        of its in-degree from other project nodes.
        """
        # Find all connected entities
        connected_entities = []
        for u, v, data in G.out_edges(new_project_node_id, data=True):
            node_type = G.nodes[v].get("type")
            if node_type != "Domain" and node_type != "Subdomain":
                connected_entities.append(v)
                
        if not connected_entities:
            # Default fallback if project connects to no entities
            return {"feature_rarity": 0.5}
            
        rarity_scores = []
        for entity_id in connected_entities:
            # Compute degree centrality focusing only on incoming project nodes
            incoming_projects = 0
            for src, _, _ in G.in_edges(entity_id, data=True):
                if G.nodes[src].get("type") == "Project" and src != new_project_node_id:
                    incoming_projects += 1
            
            # rarity = 1 / (degree + 1)
            rarity_scores.append(1.0 / (incoming_projects + 1))
            
        avg_rarity = sum(rarity_scores) / len(rarity_scores)
        return {"feature_rarity": float(avg_rarity)}
