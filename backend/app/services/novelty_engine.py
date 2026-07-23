"""
Module 4 — Graph-Based Novelty Engine
=======================================
Computes 5 explainable graph novelty signals directly from Neo4j (Section 7.4):
1. Graph Distance          — FastRP node embeddings (GDS), Jaccard-over-entities fallback
2. Feature Rarity          — 1 / (count of other projects using this entity + 1)
3. Relationship Rarity     — 1 / (CO_OCCURS edge weight for this entity pair + 1)
4. Graph Density           — GDS local clustering coefficient around the sub-domain
                              neighbourhood, sibling-count fallback
5. New-Connection Discovery — common-neighbours / Adamic-Adar over entity pairs

There is no in-memory fallback: every signal reads live from Neo4j
(`graph_service.session()`), which raises GraphUnavailableError if Neo4j can't
be reached. GDS-specific calls (FastRP, local clustering coefficient) degrade
to a plain-Cypher equivalent if the GDS plugin isn't installed or the call
fails for any other reason — the `distance_method`/`density_method` fields in
the output record which path actually ran, so results stay explainable.
"""

import logging
import math

from app.services.graph_db import graph_service

log = logging.getLogger(__name__)

GDS_GRAPH_NAME = "acadeval_novelty_graph"
FASTRP_DIMENSIONS = 64
SIMILAR_PROJECTS_TOP_K = 5


class NoveltyEngineService:
    def compute_novelty_signals(self, project_id: str, extracted_entities: dict, domain: str,
                                 sub_domain: str = "") -> dict:
        entity_pairs = graph_service.entity_label_name_pairs(extracted_entities)

        with graph_service.session() as session:
            signal_1, distance_method, similar_projects = self._signal_graph_distance(session, project_id)
            signal_2 = self._signal_feature_rarity(session, entity_pairs)
            signal_3 = self._signal_relationship_rarity(session, entity_pairs)
            signal_4, density_method = self._signal_graph_density(session, project_id, sub_domain)
            signal_5 = self._signal_new_connection_discovery(session, entity_pairs)

        weights = [0.25, 0.20, 0.20, 0.15, 0.20]
        composite_score = round(
            (signal_1 * weights[0] + signal_2 * weights[1] + signal_3 * weights[2]
             + signal_4 * weights[3] + signal_5 * weights[4]) * 100.0, 1
        )

        if composite_score >= 75.0:
            novelty_band = "Highly Novel"
        elif composite_score >= 50.0:
            novelty_band = "Moderately Novel"
        else:
            novelty_band = "Low Novelty / Incremental"

        explanation_bullets = [
            f"Graph Distance Signal ({round(signal_1*100, 1)}%, via {distance_method}): "
            f"Measures structural separation from historical project proposals.",
            f"Feature Rarity Signal ({round(signal_2*100, 1)}%): Assesses how unique the selected "
            f"algorithms/technologies are across the corpus.",
            f"Relationship Rarity Signal ({round(signal_3*100, 1)}%): Checks how rarely these specific "
            f"entity pairs co-occur.",
            f"Graph Density Signal ({round(signal_4*100, 1)}%, via {density_method}): Evaluates domain "
            f"neighborhood sparsity (higher sparsity indicates untapped areas).",
            f"New-Connection Discovery ({round(signal_5*100, 1)}%): Adamic-Adar metric indicating novel "
            f"cross-domain feature synthesis.",
        ]

        return {
            "signal_1_graph_distance": round(signal_1, 4),
            "signal_2_feature_rarity": round(signal_2, 4),
            "signal_3_relationship_rarity": round(signal_3, 4),
            "signal_4_graph_density": round(signal_4, 4),
            "signal_5_new_connection_discovery": round(signal_5, 4),
            "composite_novelty_score": composite_score,
            "novelty_band": novelty_band,
            "explanation_bullets": explanation_bullets,
            "similar_projects": similar_projects,
            "distance_method": distance_method,
            "density_method": density_method,
        }

    # ── Signal 1: Graph Distance ───────────────────────────────────────────────
    def _signal_graph_distance(self, session, project_id: str):
        try:
            embeddings = self._fastrp_embeddings(session)
            if project_id not in embeddings:
                return 0.90, "fastrp", []
            others = {pid: vec for pid, vec in embeddings.items() if pid != project_id}
            if not others:
                return 0.90, "fastrp", []
            target = embeddings[project_id]
            similarities = {pid: self._cosine(target, vec) for pid, vec in others.items()}
            mean_distance = 1.0 - (sum(similarities.values()) / len(similarities))
            top = sorted(similarities.items(), key=lambda kv: kv[1], reverse=True)[:SIMILAR_PROJECTS_TOP_K]
            similar_projects = self._similar_projects_payload(session, top)
            return max(0.0, min(1.0, mean_distance)), "fastrp", similar_projects
        except Exception as e:
            log.warning("FastRP graph distance failed (%s); falling back to Jaccard-over-entities.", e)

        entity_sets = session.run(
            """
            MATCH (p:Project)-->(e)
            WHERE NOT e:Domain AND NOT e:Subdomain
            RETURN p.id AS project_id, collect(DISTINCT e.name) AS entity_names
            """
        ).data()
        entity_map = {row["project_id"]: set(row["entity_names"]) for row in entity_sets}
        project_entities = entity_map.get(project_id, set())
        others = {pid: ents for pid, ents in entity_map.items() if pid != project_id}
        if not others:
            return 0.90, "jaccard_fallback", []

        distances = {}
        for pid, ents in others.items():
            if ents and project_entities:
                jaccard_sim = len(project_entities & ents) / float(len(project_entities | ents))
                distances[pid] = 1.0 - jaccard_sim
            else:
                distances[pid] = 1.0
        mean_distance = sum(distances.values()) / len(distances)
        top = sorted(distances.items(), key=lambda kv: kv[1])[:SIMILAR_PROJECTS_TOP_K]
        similar_projects = self._similar_projects_payload(session, [(pid, 1.0 - d) for pid, d in top])
        return max(0.0, min(1.0, mean_distance)), "jaccard_fallback", similar_projects

    def _fastrp_embeddings(self, session) -> dict[str, list[float]]:
        try:
            session.run("CALL gds.graph.drop($name, false)", name=GDS_GRAPH_NAME).consume()
        except Exception:
            pass
        session.run(
            "CALL gds.graph.project($name, '*', '*') YIELD graphName",
            name=GDS_GRAPH_NAME,
        ).consume()
        rows = session.run(
            """
            CALL gds.fastRP.stream($name, {embeddingDimension: $dim, randomSeed: 42})
            YIELD nodeId, embedding
            WITH gds.util.asNode(nodeId) AS n, embedding
            WHERE 'Project' IN labels(n)
            RETURN n.id AS project_id, embedding
            """,
            name=GDS_GRAPH_NAME, dim=FASTRP_DIMENSIONS,
        ).data()
        return {row["project_id"]: row["embedding"] for row in rows}

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _similar_projects_payload(self, session, ranked: list[tuple[str, float]]) -> list[dict]:
        if not ranked:
            return []
        ids = [pid for pid, _ in ranked]
        rows = session.run(
            "MATCH (p:Project) WHERE p.id IN $ids RETURN p.id AS id, p.title AS title",
            ids=ids,
        ).data()
        titles = {row["id"]: row["title"] for row in rows}
        return [
            {"project_id": pid, "title": titles.get(pid, pid), "similarity_score": round(sim, 4)}
            for pid, sim in ranked
        ]

    # ── Signal 2: Feature Rarity ───────────────────────────────────────────────
    def _signal_feature_rarity(self, session, entity_pairs: list[tuple[str, str]]) -> float:
        if not entity_pairs:
            return 0.50
        pair_params = [{"label": label, "name": name} for label, name in entity_pairs]
        result = session.run(
            """
            UNWIND $entities AS ent
            MATCH (e) WHERE ent.label IN labels(e) AND e.name = ent.name
            MATCH (e)<-[]-(proj:Project)
            WITH e, count(DISTINCT proj) AS deg
            RETURN avg(1.0 / (deg + 1)) AS rarity
            """,
            entities=pair_params,
        ).single()
        return result["rarity"] if result and result["rarity"] is not None else 0.50

    # ── Signal 3: Relationship Rarity ──────────────────────────────────────────
    def _signal_relationship_rarity(self, session, entity_pairs: list[tuple[str, str]]) -> float:
        pairs = [
            {"a_label": entity_pairs[i][0], "a_name": entity_pairs[i][1],
             "b_label": entity_pairs[j][0], "b_name": entity_pairs[j][1]}
            for i in range(len(entity_pairs))
            for j in range(i + 1, len(entity_pairs))
        ]
        if not pairs:
            return 0.50
        result = session.run(
            """
            UNWIND $pairs AS pair
            MATCH (a) WHERE pair.a_label IN labels(a) AND a.name = pair.a_name
            MATCH (b) WHERE pair.b_label IN labels(b) AND b.name = pair.b_name
            OPTIONAL MATCH (a)-[r:CO_OCCURS]-(b)
            RETURN avg(1.0 / (coalesce(r.weight, 0) + 1)) AS relationship_rarity
            """,
            pairs=pairs,
        ).single()
        return result["relationship_rarity"] if result and result["relationship_rarity"] is not None else 0.50

    # ── Signal 4: Graph Density ────────────────────────────────────────────────
    def _signal_graph_density(self, session, project_id: str, sub_domain: str):
        if not sub_domain:
            return 0.80, "no_subdomain"

        try:
            try:
                session.run("CALL gds.graph.drop($name, false)", name=GDS_GRAPH_NAME).consume()
            except Exception:
                pass
            session.run(
                "CALL gds.graph.project($name, '*', '*') YIELD graphName",
                name=GDS_GRAPH_NAME,
            ).consume()
            result = session.run(
                """
                CALL gds.localClusteringCoefficient.stream($name)
                YIELD nodeId, localClusteringCoefficient
                WITH gds.util.asNode(nodeId) AS n, localClusteringCoefficient AS lcc
                WHERE 'Project' IN labels(n) AND n.sub_domain = $sub_domain AND n.id <> $project_id
                RETURN avg(lcc) AS avg_clustering, count(n) AS sibling_count
                """,
                name=GDS_GRAPH_NAME, sub_domain=sub_domain, project_id=project_id,
            ).single()
            if result and result["sibling_count"]:
                return max(0.0, min(1.0, 1.0 - result["avg_clustering"])), "gds_clustering_coefficient"
            return 0.80, "gds_clustering_coefficient"
        except Exception as e:
            log.warning("GDS local clustering coefficient failed (%s); falling back to sibling count.", e)

        result = session.run(
            """
            MATCH (sd:Subdomain {name: $sub_domain})<-[:HAS_SUBDOMAIN]-(proj:Project)
            WHERE proj.id <> $project_id
            RETURN count(proj) AS sibling_count
            """,
            sub_domain=sub_domain, project_id=project_id,
        ).single()
        sibling_count = result["sibling_count"] if result else 0
        return 1.0 / (1.0 + sibling_count), "sibling_count_fallback"

    # ── Signal 5: New-Connection Discovery (common neighbours / Adamic-Adar) ──
    def _signal_new_connection_discovery(self, session, entity_pairs: list[tuple[str, str]]) -> float:
        pairs = [
            {"a_label": entity_pairs[i][0], "a_name": entity_pairs[i][1],
             "b_label": entity_pairs[j][0], "b_name": entity_pairs[j][1]}
            for i in range(len(entity_pairs))
            for j in range(i + 1, len(entity_pairs))
        ]
        if not pairs:
            return 0.75

        result = session.run(
            """
            UNWIND $pairs AS pair
            MATCH (a) WHERE pair.a_label IN labels(a) AND a.name = pair.a_name
            MATCH (b) WHERE pair.b_label IN labels(b) AND b.name = pair.b_name
            OPTIONAL MATCH (a)--(common)--(b)
            WHERE common IS NOT NULL AND common <> a AND common <> b
            WITH pair, common
            OPTIONAL MATCH (common)--(x)
            WITH pair, common, count(DISTINCT x) AS common_degree
            WITH pair, sum(CASE WHEN common_degree > 1 THEN 1.0 / log(common_degree) ELSE 0.0 END) AS aa_val
            RETURN avg(1.0 / (1.0 + aa_val)) AS new_connection_score
            """,
            pairs=pairs,
        ).single()
        return result["new_connection_score"] if result and result["new_connection_score"] is not None else 0.75


# Singleton instance
novelty_engine_service = NoveltyEngineService()
