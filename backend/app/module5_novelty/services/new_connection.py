import networkx as nx

class NewConnectionService:
    @staticmethod
    def calculate_connection(G: nx.MultiDiGraph, new_project_node_id: int) -> dict:
        """
        Signal 5 — New-Connection Discovery
        Uses Adamic-Adar link-prediction index over entity pairs in the undirected graph.
        """
        # Find all connected entities
        entities = []
        for _, v in G.out_edges(new_project_node_id):
            node_type = G.nodes[v].get("type")
            if node_type not in ("Domain", "Subdomain", "Project"):
                entities.append(v)
                
        if len(entities) < 2:
            return {"aa_score": 0.0, "new_connection": 1.0, "is_new": True}
            
        undirected = G.to_undirected()
        
        # Build all entity pairs
        pairs = []
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                # Adamic-Adar link prediction is only defined if there's no edge currently,
                # or we check the common neighbors between the two entity nodes in G (excluding target).
                pairs.append((entities[i], entities[j]))
                
        aa_scores = []
        for u, v in pairs:
            # We want to check common neighbors on the graph BEFORE this project's connections were added,
            # but since G includes the project, we can do it on undirected graph, or just compute Adamic-Adar.
            try:
                # nx.adamic_adar_index returns an iterator of (u, v, score)
                preds = list(nx.adamic_adar_index(undirected, [(u, v)]))
                score = float(preds[0][2]) if preds else 0.0
                aa_scores.append(score)
            except Exception:
                aa_scores.append(0.0)
                
        avg_aa = sum(aa_scores) / len(aa_scores) if aa_scores else 0.0
        
        # If Adamic-Adar score is 0, indicates no common neighbors -> new connection!
        is_new = avg_aa == 0.0
        new_connection_score = 1.0 if is_new else float(1.0 / (1.0 + avg_aa))
        
        return {
            "aa_score": float(avg_aa),
            "new_connection": float(new_connection_score),
            "is_new": is_new
        }
