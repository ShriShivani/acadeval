class ExplanationGenerator:
    @staticmethod
    def generate_explanations(normalized_signals: dict) -> list[str]:
        """
        Produces bulleted reasons explaining the novelty score based on individual signal thresholds.
        """
        reasons = []
        
        if normalized_signals.get("graph_distance", 0.0) >= 0.6:
            reasons.append("Far from existing projects (high structural distance)")
            
        if normalized_signals.get("feature_rarity", 0.0) >= 0.6:
            reasons.append("Rare technology or method (unique algorithms/tools)")
            
        if normalized_signals.get("relationship_rarity", 0.0) >= 0.6:
            reasons.append("Unique relationship (components rarely combined historically)")
            
        if normalized_signals.get("graph_density", 0.0) < 0.4:
            # Low local density means sparse neighborhood -> novel region
            reasons.append("Sparse graph domain region (situated in a less crowded neighborhood)")
            
        if normalized_signals.get("new_connection", 0.0) >= 0.6:
            reasons.append("Cross-domain connection (introduces highly unexpected linkages)")
            
        if not reasons:
            reasons.append("Mainstream project structure with standard, common components")
            
        return reasons
