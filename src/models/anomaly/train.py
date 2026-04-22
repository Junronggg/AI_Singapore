from pathlib import Path
from typing import Dict

import numpy as np
from sklearn.ensemble import IsolationForest

from src.common.logger import get_logger
from src.common.utils import load_joblib, save_joblib, save_json
from src.models.anomaly.model import AnomalyModelBundle

logger = get_logger(__name__)


class AnomalyTrainer:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        X_train: np.ndarray,
        X_val: np.ndarray,
        contamination: float = 0.01,
        random_state: int = 42,
    ) -> Dict:
        logger.info("Training IsolationForest anomaly model...")
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        model.fit(X_train)

        # decision_function: higher = more normal, lower = more abnormal
        val_scores = model.decision_function(X_val)

        # use low percentile of normal validation scores as threshold
        threshold = float(np.percentile(val_scores, 5))

        bundle = AnomalyModelBundle(model=model, threshold=threshold)

        save_joblib(bundle, self.model_dir / "anomaly_bundle.pkl")

        metadata = {
            "model_type": "IsolationForest",
            "threshold": threshold,
            "contamination": contamination,
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
        }
        save_json(metadata, self.model_dir / "anomaly_metadata.json")

        logger.info("Saved anomaly model to %s", self.model_dir / "anomaly_bundle.pkl")
        logger.info("Anomaly threshold: %.6f", threshold)

        return metadata