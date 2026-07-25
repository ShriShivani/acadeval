"""
Module 4 — Project Knowledge Graph Router
==========================================
REST API endpoints for inspecting, visualising, exporting, and managing
the Project Knowledge Graph.

Routes:
  GET  /api/graph/summary        — overall graph metrics (density, nodes, edges, top centrality)
  GET  /api/graph/visualization  — D3 force payload ({nodes:[], links:[]}) for UI visualizer
  GET  /api/graph/node/{query}    — 1-hop / 2-hop neighborhood of a specific node
  POST /api/graph/rebuild        — trigger bulk re-ingestion of all projects into the graph
  GET  /api/graph/export         — export graph structure as JSON
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response
from app.dependencies import DB, CurrentUser, CurrentFacultyOrHOD
from app.services.graph_networkx import (
    get_cached_graph,
    get_graph_metrics,
    export_d3_graph,
    get_node_neighborhood,
    invalidate_graph_cache,
)
from app.services.graph_builder import bulk_rebuild_graph

log = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["Module 4 — Knowledge Graph Construction"])


@router.get("/summary", summary="Get overall Knowledge Graph metrics")
def get_summary(current_user: CurrentUser, db: DB, refresh: bool = Query(False)):
    """
    Returns summary statistics for the Knowledge Graph:
    total nodes, total edges, graph density, node type breakdown,
    relationship type breakdown, and top nodes by degree centrality.
    """
    try:
        G = get_cached_graph(db, force_reload=refresh)
        metrics = get_graph_metrics(G)
        return {
            "status": "ok",
            "metrics": metrics,
        }
    except Exception as e:
        log.error("Failed to compute graph summary: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate graph summary: {e}")


@router.get("/visualization", summary="Get D3.js/Cytoscape format payload for graph visualization")
def get_visualization(
    current_user: CurrentUser,
    db: DB,
    limit: int = Query(300, ge=10, le=1000, description="Max nodes to return"),
    node_types: Optional[str] = Query(None, description="Comma-separated node types to include (e.g. Algorithm,Technology)"),
):
    """
    Returns nodes and links formatted for force-directed graph rendering.
    """
    try:
        G = get_cached_graph(db)
        type_filter = [t.strip() for t in node_types.split(",")] if node_types else None
        d3_data = export_d3_graph(G, max_nodes=limit, node_type_filter=type_filter)
        return {
            "status": "ok",
            **d3_data,
        }
    except Exception as e:
        log.error("Failed to export visualization graph: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load graph visualization data: {e}")


@router.get("/node/{query}", summary="Get neighborhood subgraph for a specific node")
def inspect_node(
    query: str,
    current_user: CurrentUser,
    db: DB,
    radius: int = Query(1, ge=1, le=3, description="Hops to include around target node"),
):
    """
    Returns the target node's details and its surrounding 1-hop or 2-hop neighborhood.
    """
    try:
        G = get_cached_graph(db)
        res = get_node_neighborhood(G, query=query, radius=radius)
        if "error" in res:
            raise HTTPException(status_code=404, detail=res["error"])
        return {
            "status": "ok",
            **res,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to inspect node %r: %s", query, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving node neighborhood: {e}")


@router.post("/rebuild", summary="Bulk re-ingest all project proposals into Knowledge Graph")
def rebuild_knowledge_graph(current_user: CurrentFacultyOrHOD, db: DB):
    """
    Clears PostgreSQL `graph_nodes` & `graph_edges` and re-ingests all stored projects.
    Requires Faculty or HOD role.
    """
    try:
        res = bulk_rebuild_graph(db)
        invalidate_graph_cache()
        return {
            "status": "rebuilt",
            "result": res,
        }
    except Exception as e:
        log.error("Bulk graph rebuild failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Graph rebuild failed: {e}")


@router.get("/export", summary="Export full Knowledge Graph as JSON payload")
def export_graph_data(current_user: CurrentUser, db: DB):
    """
    Exports the complete NetworkX graph structure as JSON.
    """
    try:
        G = get_cached_graph(db)
        d3_data = export_d3_graph(G, max_nodes=5000)
        return {
            "status": "ok",
            **d3_data,
        }
    except Exception as e:
        log.error("Graph export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
