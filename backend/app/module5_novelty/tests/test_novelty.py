import networkx as nx
import pytest
from app.module5_novelty.services.feature_rarity import FeatureRarityService
from app.module5_novelty.services.graph_density import GraphDensityService
from app.module5_novelty.services.new_connection import NewConnectionService
from app.module5_novelty.services.normalization import NormalizationService
from app.module5_novelty.services.novelty_combiner import NoveltyCombiner
from app.module5_novelty.services.explanation_generator import ExplanationGenerator

@pytest.fixture
def sample_graph():
    # Build a simple MultiDiGraph
    # Project 1 (P1) -> USES_ALGORITHM -> A1, USES_APPLICATION -> AP1
    # Project 2 (P2) -> USES_ALGORITHM -> A1, USES_APPLICATION -> AP2
    # Project 3 (P3) -> USES_ALGORITHM -> A2, USES_APPLICATION -> AP1
    # New Project (P_NEW) -> USES_ALGORITHM -> A2, USES_APPLICATION -> AP2
    G = nx.MultiDiGraph()
    
    G.add_node(1, type="Project", name="P1")
    G.add_node(2, type="Project", name="P2")
    G.add_node(3, type="Project", name="P3")
    G.add_node(4, type="Project", name="P_NEW")
    
    G.add_node(10, type="Algorithm", name="A1")
    G.add_node(11, type="Algorithm", name="A2")
    
    G.add_node(20, type="Application", name="AP1")
    G.add_node(21, type="Application", name="AP2")
    
    # Edges
    G.add_edge(1, 10, relationship="USES_ALGORITHM", confidence=1.0)
    G.add_edge(1, 20, relationship="TARGETS_APPLICATION", confidence=1.0)
    
    G.add_edge(2, 10, relationship="USES_ALGORITHM", confidence=1.0)
    G.add_edge(2, 21, relationship="TARGETS_APPLICATION", confidence=1.0)
    
    G.add_edge(3, 11, relationship="USES_ALGORITHM", confidence=1.0)
    G.add_edge(3, 20, relationship="TARGETS_APPLICATION", confidence=1.0)
    
    # New Project connections
    G.add_edge(4, 11, relationship="USES_ALGORITHM", confidence=1.0)
    G.add_edge(4, 21, relationship="TARGETS_APPLICATION", confidence=1.0)
    
    return G

def test_feature_rarity(sample_graph):
    # P_NEW connects to A2 (used by P3) and AP2 (used by P2).
    # Degree of A2 is 1 (P3). Rarity for A2 is 1 / (1 + 1) = 0.5
    # Degree of AP2 is 1 (P2). Rarity for AP2 is 1 / (1 + 1) = 0.5
    # Average rarity should be 0.5
    res = FeatureRarityService.calculate_rarity(sample_graph, 4)
    assert res["feature_rarity"] == 0.5

def test_graph_density(sample_graph):
    res = GraphDensityService.calculate_density(sample_graph, 4)
    assert isinstance(res["density"], float)
    assert 0.0 <= res["density"] <= 1.0

def test_new_connection(sample_graph):
    # A2 and AP2 are connected to P_NEW
    res = NewConnectionService.calculate_connection(sample_graph, 4)
    assert "aa_score" in res
    assert "new_connection" in res
    assert isinstance(res["is_new"], bool)

def test_normalization():
    raw = {
        "graph_distance": 1.5,
        "feature_rarity": -0.2,
        "relationship_rarity": None,
        "graph_density": float("nan"),
        "new_connection": 0.75
    }
    normalized = NormalizationService.normalize_signals(raw)
    assert normalized["graph_distance"] == 1.0
    assert normalized["feature_rarity"] == 0.0
    assert normalized["relationship_rarity"] == 0.5
    assert normalized["graph_density"] == 0.5
    assert normalized["new_connection"] == 0.75

def test_novelty_combiner():
    normalized = {
        "graph_distance": 0.8,
        "feature_rarity": 0.7,
        "relationship_rarity": 0.9,
        "graph_density": 0.2,
        "new_connection": 0.4
    }
    # Unweighted average: (0.8 + 0.7 + 0.9 + 0.2 + 0.4) / 5 = 0.6
    # novelty_score should be 60.0
    score = NoveltyCombiner.combine_signals(normalized)
    assert score == 60.0

def test_explanation_generator():
    normalized = {
        "graph_distance": 0.8,
        "feature_rarity": 0.7,
        "relationship_rarity": 0.9,
        "graph_density": 0.1,
        "new_connection": 0.4
    }
    reasons = ExplanationGenerator.generate_explanations(normalized)
    assert len(reasons) > 0
    assert "Far from existing projects (high structural distance)" in reasons
    assert "Rare technology or method (unique algorithms/tools)" in reasons
    assert "Unique relationship (components rarely combined historically)" in reasons
    assert "Sparse graph domain region (situated in a less crowded neighborhood)" in reasons
