import numpy as np

class NormalizationService:
    @staticmethod
    def normalize_signals(raw_signals: dict) -> dict:
        """
        Clips all signals to strictly be within [0, 1] and checks for NaN/None values,
        replacing them with a neutral 0.5 value if necessary.
        """
        normalized = {}
        for key, val in raw_signals.items():
            if val is None or np.isnan(val):
                normalized[key] = 0.5
            else:
                # Ensure it fits in [0.0, 1.0] range
                normalized[key] = float(np.clip(val, 0.0, 1.0))
        return normalized
