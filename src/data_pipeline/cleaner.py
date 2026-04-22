import re
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


TEXT_TO_NUMERIC = {
    "on": 1,
    "off": 0,
    "open": 1,
    "closed": 0,
    "close": 0,
    "true": 1,
    "false": 0,
    "yes": 1,
    "no": 0,
    "active": 1,
    "inactive": 0,
    "alarm": 1,
    "normal": 0,
}


class DataCleaner:
    def standardize_column_name(self, col: str) -> str:
        col = str(col).strip()
        col = re.sub(r"\s+", "_", col)
        return col

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [self.standardize_column_name(c) for c in df.columns]
        return df

    def find_timestamp_column(self, df: pd.DataFrame) -> str:
        candidates = [
            "t_stamp",
            "timestamp",
            "time",
            "datetime",
            "date_time",
        ]

        normalized_to_original = {str(col).strip().lower(): col for col in df.columns}

        for cand in candidates:
            if cand in normalized_to_original:
                return normalized_to_original[cand]

        for col in df.columns:
            low = str(col).strip().lower()
            if "stamp" in low or "time" in low or "date" in low:
                return col

        raise ValueError(f"No timestamp column found. Available columns: {list(df.columns)}")

    def normalize_text_value(self, value):
        if pd.isna(value):
            return np.nan

        if isinstance(value, str):
            s = value.strip().lower()
            if s in TEXT_TO_NUMERIC:
                return TEXT_TO_NUMERIC[s]
            try:
                return float(s)
            except ValueError:
                return np.nan

        return value

    def convert_to_numeric(self, df: pd.DataFrame, exclude_cols: List[str]) -> pd.DataFrame:
        df = df.copy()

        for col in df.columns:
            if col in exclude_cols:
                continue

            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].map(self.normalize_text_value)

            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def parse_timestamp(self, df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
        df = df.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
        df = df.dropna(subset=[timestamp_col]).sort_values(timestamp_col).reset_index(drop=True)
        return df

    def split_a12_normal_attack(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        half = len(df) // 2
        df_normal = df.iloc[:half].copy().reset_index(drop=True)
        df_attack = df.iloc[half:].copy().reset_index(drop=True)
        return df_normal, df_attack

    def align_common_columns(self, dfs: Dict[str, pd.DataFrame], timestamp_col: str) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
        column_sets = []
        for df in dfs.values():
            cols = set(df.columns)
            cols.discard(timestamp_col)
            column_sets.append(cols)

        common_cols = sorted(list(set.intersection(*column_sets)))

        aligned = {}
        for name, df in dfs.items():
            aligned[name] = df[[timestamp_col] + common_cols].copy()

        return aligned, common_cols

    def drop_bad_columns(
        self,
        df: pd.DataFrame,
        exclude_cols: List[str],
        max_missing_ratio: float = 0.2,
        drop_constant: bool = True,
    ) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
        df = df.copy()

        dropped_missing = []
        dropped_constant = []

        feature_cols = [c for c in df.columns if c not in exclude_cols]

        for col in feature_cols:
            if df[col].isna().mean() > max_missing_ratio:
                dropped_missing.append(col)

        df = df.drop(columns=dropped_missing, errors="ignore")

        if drop_constant:
            feature_cols = [c for c in df.columns if c not in exclude_cols]
            for col in feature_cols:
                if df[col].nunique(dropna=True) <= 1:
                    dropped_constant.append(col)

            df = df.drop(columns=dropped_constant, errors="ignore")

        info = {
            "dropped_missing": dropped_missing,
            "dropped_constant": dropped_constant,
        }
        return df, info

    def fill_missing_with_train_median(
        self,
        train_df: pd.DataFrame,
        other_dfs: Dict[str, pd.DataFrame],
        feature_cols: List[str],
    ) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], Dict[str, float]]:
        train_df = train_df.copy()
        other_dfs = {k: v.copy() for k, v in other_dfs.items()}

        fill_values = {}
        for col in feature_cols:
            median_val = train_df[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            fill_values[col] = float(median_val)

        train_df[feature_cols] = train_df[feature_cols].fillna(fill_values)

        for name, df in other_dfs.items():
            df[feature_cols] = df[feature_cols].fillna(fill_values)
            other_dfs[name] = df

        return train_df, other_dfs, fill_values