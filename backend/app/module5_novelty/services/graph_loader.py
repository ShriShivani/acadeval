import networkx as nx
from sqlalchemy.orm import Session
from app.module5_novelty.repository.graph_repository import GraphRepository

class GraphLoader:
    @staticmethod
    def load_graph(db: Session) -> nx.MultiDiGraph:
        G = nx.MultiDiGraph()
        nodes = GraphRepository.get_nodes(db)
        for node in nodes:
            G.add_node(
                node["id"],
                id=node["id"],
                type=node["node_type"],
                name=node["name"]
            )
        
        edges = GraphRepository.get_edges(db)
        for edge in edges:
            if G.has_node(edge["from_node"]) and G.has_node(edge["to_node"]):
                G.add_edge(
                    edge["from_node"],
                    edge["to_node"],
                    key=edge["id"],
                    relationship=edge["relationship"],
                    confidence=edge["confidence"]
                )
        return G
