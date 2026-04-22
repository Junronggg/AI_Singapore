from typing import List

import pandas as pd


def validate_non_empty_dataframe(df: pd.DataFrame, name: str) -> None:
    if df.empty:
        raise ValueError(f"{name} is empty.")


def validate_required_columns(df: pd.DataFrame, required_cols: List[str], name: str) -> None:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")