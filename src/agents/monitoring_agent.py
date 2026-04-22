from typing import Dict, List

import numpy as np
import pandas as pd


class MonitoringAgent:
    def __init__(self, feature_cols: List[str]):
        self.feature_cols = feature_cols

    def inspect_row(self, row: pd.Series) -> Dict:
        missing_features = []
        invalid_features = []

        for col in self.feature_cols:
            value = row.get(col, None)

            if pd.isna(value):
                missing_features.append(col)
            elif not np.isfinite(float(value)):
                invalid_features.append(col)

        is_valid = len(missing_features) == 0 and len(invalid_features) == 0

        return {
            "is_valid": is_valid,
            "missing_features": missing_features,
            "invalid_features": invalid_features,
            "message": "ok" if is_valid else "data quality issue detected",
        }