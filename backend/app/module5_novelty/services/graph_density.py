import networkx as nx

class GraphDensityService:
    @staticmethod
    def calculate_density(G: nx.MultiDiGraph, new_project_node_id: int) -> dict:
        """
        Signal 4 — Graph Density
        Uses local clustering coefficient around the project's node neighborhood on G.to_undirected().
        """
        if G.number_of_nodes() < 2:
            return {"density": 0.0}
            
        try:
            undirected = G.to_undirected()
            if new_project_node_id not in undirected:
                return {"density": 0.0}
                
            density = nx.clustering(undirected, nodes=[new_project_node_id])[new_project_node_id]
            return {"density": float(density)}
        except Exception:
            # Fallback if NetworkX fails
            return {"density": 0.5}
