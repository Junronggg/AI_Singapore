from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.common.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    def add_time_features(self, df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
        df = df.copy()
        ts = pd.to_datetime(df[timestamp_col], errors="coerce")

        df["hour"] = ts.dt.hour
        df["minute"] = ts.dt.minute
        df["second"] = ts.dt.second

        total_seconds = df["hour"] * 3600 + df["minute"] * 60 + df["second"]
        seconds_in_day = 24 * 3600

        df["time_sin"] = np.sin(2 * np.pi * total_seconds / seconds_in_day)
        df["time_cos"] = np.cos(2 * np.pi * total_seconds / seconds_in_day)

        return df

    def fit_scaler(self, train_df: pd.DataFrame, feature_cols: List[str]) -> StandardScaler:
        scaler = StandardScaler()
        scaler.fit(train_df[feature_cols])
        return scaler

    def transform_split(
        self,
        df: pd.DataFrame,
        feature_cols: List[str],
        scaler: StandardScaler,
    ) -> np.ndarray:
        return scaler.transform(df[feature_cols])

    def attach_labels(self, df: pd.DataFrame, label: int) -> pd.DataFrame:
        df = df.copy()
        df["label"] = label
        return df