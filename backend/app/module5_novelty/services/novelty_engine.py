import logging
from sqlalchemy.orm import Session
from app.module5_novelty.services.graph_loader import GraphLoader
from app.module5_novelty.services.graph_distance import GraphDistanceService
from app.module5_novelty.services.feature_rarity import FeatureRarityService
from app.module5_novelty.services.relationship_rarity import RelationshipRarityService
from app.module5_novelty.services.graph_density import GraphDensityService
from app.module5_novelty.services.new_connection import NewConnectionService
from app.module5_novelty.services.normalization import NormalizationService
from app.module5_novelty.services.novelty_combiner import NoveltyCombiner
from app.module5_novelty.services.explanation_generator import ExplanationGenerator
from app.module5_novelty.repository.novelty_repository import NoveltyRepository

log = logging.getLogger(__name__)

class NoveltyEngine:
    @staticmethod
    def calculate_novelty(db: Session, payload: dict) -> dict:
        """
        Main orchestration entrypoint for Module 5 Graph-Based Novelty Engine.
        """
        project_id = payload["project_id"]
        
        # Step 1: Load graph from database into NetworkX MultiDiGraph
        G = GraphLoader.load_graph(db)
        
        # Find node ID of the target project in G
        target_node_id = None
        for nid, attr in G.nodes(data=True):
            if attr.get("type") == "Project" and str(attr.get("name")) == str(project_id):
                target_node_id = nid
                break
                
        if target_node_id is None:
            # Fallback or create temporary project node if missing
            log.warning("Project ID %r not found in graph nodes. Creating transient evaluation context.", project_id)
            # Find the max integer ID to assign to the target project node
            max_id = max(G.nodes) if list(G.nodes) else 0
            target_node_id = max_id + 1
            G.add_node(target_node_id, type="Project", name=project_id)
            
        # Step 2: Compute isolated signal services
        # 1. Graph Distance
        dist_res = GraphDistanceService.calculate_distance(G, target_node_id)
        raw_graph_distance = dist_res["distance"]
        similar_projects = dist_res["similar_projects"]
        
        # 2. Feature Rarity
        rarity_res = FeatureRarityService.calculate_rarity(G, target_node_id)
        raw_feature_rarity = rarity_res["feature_rarity"]
        
        # 3. Relationship Rarity
        rel_res = RelationshipRarityService.calculate_rarity(db, G, target_node_id)
        raw_relationship_rarity = rel_res["relationship_rarity"]
        
        # 4. Graph Density
        density_res = GraphDensityService.calculate_density(G, target_node_id)
        raw_graph_density = density_res["density"]
        
        # 5. New-Connection Discovery
        conn_res = NewConnectionService.calculate_connection(G, target_node_id)
        raw_new_connection = conn_res["new_connection"]
        
        # Step 3: Normalize signals
        raw_signals = {
            "graph_distance": raw_graph_distance,
            "feature_rarity": raw_feature_rarity,
            "relationship_rarity": raw_relationship_rarity,
            "graph_density": raw_graph_density,
            "new_connection": raw_new_connection
        }
        
        normalized = NormalizationService.normalize_signals(raw_signals)
        
        # Step 4: Combine signals to calculate novelty score
        novelty_score = NoveltyCombiner.combine_signals(normalized)
        
        # Calculate confidence based on the number of entities connected to project
        num_entities = len([v for _, v in G.out_edges(target_node_id)])
        confidence = float(min(0.95, 0.5 + 0.1 * num_entities))
        
        # Step 5: Save results to PostgreSQL database
        result_data = {
            "project_id": str(project_id),
            "graph_distance": normalized["graph_distance"],
            "feature_rarity": normalized["feature_rarity"],
            "relationship_rarity": normalized["relationship_rarity"],
            "graph_density": normalized["graph_density"],
            "new_connection": normalized["new_connection"],
            "novelty_score": novelty_score,
            "confidence": confidence,
            "similar_projects": similar_projects
        }
        
        db_obj = NoveltyRepository.save_novelty_result(db, result_data)
        
        # Step 6: Generate report explanations
        reasons = ExplanationGenerator.generate_explanations(normalized)
        
        response = db_obj.to_dict()
        response["reasons"] = reasons
        
        return response
