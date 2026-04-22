from pathlib import Path
from typing import Dict

import numpy as np

from src.common.logger import get_logger
from src.common.utils import load_joblib
from src.models.anomaly.model import AnomalyModelBundle

logger = get_logger(__name__)


class AnomalyInferencer:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.bundle: AnomalyModelBundle = load_joblib(self.model_dir / "anomaly_bundle.pkl")

    def predict_one(self, x: np.ndarray) -> Dict:
        if x.ndim == 1:
            x = x.reshape(1, -1)

        score = float(self.bundle.model.decision_function(x)[0])
        is_anomaly = score < self.bundle.threshold

        return {
            "anomaly_score": score,
            "is_anomaly": bool(is_anomaly),
            "threshold": float(self.bundle.threshold),
        }

    def predict_batch(self, X: np.ndarray) -> Dict:
        scores = self.bundle.model.decision_function(X)
        flags = scores < self.bundle.threshold

        return {
            "scores": scores.tolist(),
            "flags": flags.astype(int).tolist(),
            "threshold": float(self.bundle.threshold),
        }