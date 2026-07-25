"""
Module 4 — In-Memory NetworkX MultiDiGraph Engine
===================================================
Loads PostgreSQL relational graph nodes/edges into an in-memory NetworkX
MultiDiGraph (`G`) for fast Graph Analytics, Centrality, and path algorithms.
Maintains a thread-safe in-memory cache refreshed on new project ingestion.
"""

import logging
import networkx as nx
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# Global thread-safe in-memory cache for the NetworkX MultiDiGraph
_CACHED_GRAPH: Optional[nx.MultiDiGraph] = None


def invalidate_graph_cache():
    """Resets the cached NetworkX graph instance."""
    global _CACHED_GRAPH
    _CACHED_GRAPH = None
    log.info("NetworkX in-memory graph cache invalidated.")


def load_graph(db: Session) -> nx.MultiDiGraph:
    """
    Reads all rows from `graph_nodes` and `graph_edges` in PostgreSQL
    and constructs a NetworkX MultiDiGraph.
    """
    G = nx.MultiDiGraph()

    # 1. Fetch nodes
    nodes_query = text("SELECT id, node_type, name FROM graph_nodes")
    nodes_rows = db.execute(nodes_query).fetchall()

    for node_id, node_type, name in nodes_rows:
        G.add_node(
            node_id,
            id=node_id,
            type=node_type,
            name=name,
        )

    # 2. Fetch edges
    edges_query = text("SELECT id, from_node, to_node, relationship, confidence FROM graph_edges")
    edges_rows = db.execute(edges_query).fetchall()

    for edge_id, from_node, to_node, relationship, confidence in edges_rows:
        if G.has_node(from_node) and G.has_node(to_node):
            G.add_edge(
                from_node,
                to_node,
                key=edge_id,
                relationship=relationship,
                confidence=float(confidence or 1.0),
            )

    log.info("Built NetworkX MultiDiGraph: %d nodes, %d edges.", G.number_of_nodes(), G.number_of_edges())
    return G


def get_cached_graph(db: Session, force_reload: bool = False) -> nx.MultiDiGraph:
    """
    Returns the in-memory NetworkX MultiDiGraph, loading it from DB if uninitialized.
    """
    global _CACHED_GRAPH
    if _CACHED_GRAPH is None or force_reload:
        _CACHED_GRAPH = load_graph(db)
    return _CACHED_GRAPH


def get_graph_metrics(G: nx.MultiDiGraph) -> dict:
    """
    Computes statistical and structural metrics for the graph:
    - Node count & Edge count
    - Graph density
    - Node type breakdown
    - Relationship breakdown
    - Top 10 nodes by degree centrality
    """
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    if num_nodes == 0:
        return {
            "nodes_count": 0,
            "edges_count": 0,
            "density": 0.0,
            "node_type_distribution": {},
            "relationship_distribution": {},
            "top_centrality_nodes": [],
        }

    # Density for directed graph
    density = float(nx.density(G))

    # Node type distribution
    node_types: dict[str, int] = {}
    for _, data in G.nodes(data=True):
        ntype = data.get("type", "Unknown")
        node_types[ntype] = node_types.get(ntype, 0) + 1

    # Relationship distribution
    rel_types: dict[str, int] = {}
    for _, _, data in G.edges(data=True):
        rel = data.get("relationship", "Unknown")
        rel_types[rel] = rel_types.get(rel, 0) + 1

    # Degree centrality top nodes
    try:
        deg_centrality = nx.degree_centrality(G)
        top_central_ids = sorted(deg_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

        top_centrality_nodes = [
            {
                "id": nid,
                "name": G.nodes[nid].get("name", str(nid)),
                "type": G.nodes[nid].get("type", "Unknown"),
                "degree": G.degree(nid),
                "centrality_score": round(float(score), 4),
            }
            for nid, score in top_central_ids
        ]
    except Exception as e:
        log.warning("Could not calculate degree centrality: %s", e)
        top_centrality_nodes = []

    return {
        "nodes_count": num_nodes,
        "edges_count": num_edges,
        "density": round(density, 6),
        "node_type_distribution": node_types,
        "relationship_distribution": rel_types,
        "top_centrality_nodes": top_centrality_nodes,
    }


def export_d3_graph(
    G: nx.MultiDiGraph,
    max_nodes: int = 500,
    node_type_filter: Optional[list[str]] = None
) -> dict:
    """
    Exports NetworkX MultiDiGraph as JSON compatible with D3.js / Canvas force visualizers:
    {
      "nodes": [ { "id": 1, "name": "CNN", "type": "Algorithm", "degree": 5 } ],
      "links": [ { "source": 1, "target": 2, "relationship": "USES_ALGORITHM" } ]
    }
    """
    selected_nodes = set()

    for nid, data in G.nodes(data=True):
        ntype = data.get("type", "")
        if node_type_filter and len(node_type_filter) > 0:
            if ntype.lower() in [t.lower() for t in node_type_filter]:
                selected_nodes.add(nid)
        else:
            selected_nodes.add(nid)

        if len(selected_nodes) >= max_nodes:
            break

    # Format nodes
    nodes_payload = [
        {
            "id": nid,
            "name": G.nodes[nid].get("name", str(nid)),
            "type": G.nodes[nid].get("type", "Unknown"),
            "degree": G.degree(nid),
        }
        for nid in selected_nodes
    ]

    # Format edges between selected nodes
    links_payload = []
    seen_edges = set()

    for u, v, data in G.edges(data=True):
        if u in selected_nodes and v in selected_nodes:
            rel = data.get("relationship", "CONNECTED")
            edge_key = (u, v, rel)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                links_payload.append({
                    "source": u,
                    "target": v,
                    "relationship": rel,
                    "confidence": data.get("confidence", 1.0),
                })

    return {
        "total_graph_nodes": G.number_of_nodes(),
        "total_graph_edges": G.number_of_edges(),
        "returned_nodes": len(nodes_payload),
        "returned_links": len(links_payload),
        "nodes": nodes_payload,
        "links": links_payload,
    }


def get_node_neighborhood(G: nx.MultiDiGraph, query: str, radius: int = 1) -> dict:
    """
    Finds a node by name or integer ID and extracts its subgraph up to `radius` hops.
    """
    target_node = None

    # Search by ID or name
    try:
        target_id = int(query)
        if G.has_node(target_id):
            target_node = target_id
    except ValueError:
        pass

    if target_node is None:
        q_lower = str(query).strip().lower()
        for nid, data in G.nodes(data=True):
            if data.get("name", "").strip().lower() == q_lower:
                target_node = nid
                break

    if target_node is None:
        return {"error": f"Node {query!r} not found in knowledge graph."}

    # Extract ego subgraph
    subgraph_nodes = set(nx.single_source_shortest_path_length(G.to_undirected(), target_node, cutoff=radius).keys())
    subG = G.subgraph(subgraph_nodes)

    sub_d3 = export_d3_graph(subG, max_nodes=1000)

    target_data = G.nodes[target_node]
    return {
        "target_node": {
            "id": target_node,
            "name": target_data.get("name"),
            "type": target_data.get("type"),
            "degree": G.degree(target_node),
        },
        "radius": radius,
        "neighborhood_nodes": len(subgraph_nodes),
        "graph": sub_d3,
    }
