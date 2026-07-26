import logging
import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy import text

log = logging.getLogger(__name__)

class RelationshipRarityService:
    @staticmethod
    def calculate_rarity(db: Session, G: nx.MultiDiGraph, new_project_node_id: int) -> dict:
        """
        Signal 3 — Relationship Rarity
        Counts how many projects share the exact same entity pair via a direct SQL query.
        """
        # Find all connected entities (excluding domain/subdomain)
        entities = []
        for _, v in G.out_edges(new_project_node_id):
            node_type = G.nodes[v].get("type")
            if node_type not in ("Domain", "Subdomain", "Project"):
                entities.append(v)
                
        if len(entities) < 2:
            return {"relationship_rarity": 1.0}  # No pairs -> maximally rare
            
        rarity_scores = []
        
        # Build pairs of distinct entities
        pairs = []
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                pairs.append((entities[i], entities[j]))
                
        # To avoid making many separate queries, we query the SQL counts
        sql = """
            SELECT e1.to_node AS node_a, e2.to_node AS node_b, COUNT(DISTINCT e1.from_node) AS pair_count
            FROM graph_edges e1
            JOIN graph_edges e2 ON e1.from_node = e2.from_node
            WHERE e1.from_node <> :new_project_id
              AND e1.to_node IN :entity_ids 
              AND e2.to_node IN :entity_ids
              AND e1.to_node < e2.to_node
            GROUP BY e1.to_node, e2.to_node
        """
        
        try:
            # SQL IN parameter requires a tuple
            entity_ids_tuple = tuple(entities)
            res = db.execute(
                text(sql),
                {
                    "new_project_id": new_project_node_id,
                    "entity_ids": entity_ids_tuple
                }
            ).fetchall()
            
            # Map of (node_a, node_b) -> pair_count
            counts = {}
            for node_a, node_b, count in res:
                # Ensure ordered key
                k = (min(node_a, node_b), max(node_a, node_b))
                counts[k] = count
                
            for e_a, e_b in pairs:
                k = (min(e_a, e_b), max(e_a, e_b))
                pair_count = counts.get(k, 0)
                rarity_scores.append(1.0 / (pair_count + 1))
                
        except Exception as e:
            log.error("Failed to query relationship rarity: %s", e)
            # Fallback to local graph calculations if SQL fails
            for e_a, e_b in pairs:
                # Find common incoming project nodes
                projects_a = {src for src, _ in G.in_edges(e_a) if G.nodes[src].get("type") == "Project" and src != new_project_node_id}
                projects_b = {src for src, _ in G.in_edges(e_b) if G.nodes[src].get("type") == "Project" and src != new_project_node_id}
                pair_count = len(projects_a & projects_b)
                rarity_scores.append(1.0 / (pair_count + 1))
                
        avg_rarity = sum(rarity_scores) / len(rarity_scores) if rarity_scores else 1.0
        return {"relationship_rarity": float(avg_rarity)}
