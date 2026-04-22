from typing import Dict, List

import numpy as np
import pandas as pd


class RootCauseDiagnosisAgent:
    def __init__(self, feature_cols: List[str], top_k: int = 5):
        self.feature_cols = feature_cols
        self.top_k = top_k

    def diagnose(self, row_scaled: np.ndarray, anomaly_result: Dict) -> Dict:
        """
        For MVP:
        Use absolute scaled feature magnitude as proxy for contribution.
        """
        if row_scaled.ndim > 1:
            row_scaled = row_scaled[0]

        abs_vals = np.abs(row_scaled)
        ranked_idx = np.argsort(-abs_vals)[: self.top_k]

        top_features = [
            {
                "feature": self.feature_cols[i],
                "score": float(abs_vals[i]),
            }
            for i in ranked_idx
        ]

        likely_cause = top_features[0]["feature"] if top_features else None

        return {
            "likely_root_cause": likely_cause,
            "top_contributing_features": top_features,
            "affected_feature_count": len(top_features),
        }