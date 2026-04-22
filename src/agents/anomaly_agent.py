from pathlib import Path
from typing import Dict

import numpy as np

from src.models.anomaly.infer import AnomalyInferencer


class AnomalyDetectionAgent:
    def __init__(self, model_dir: Path):
        self.inferencer = AnomalyInferencer(model_dir=model_dir)

    def run(self, x: np.ndarray) -> Dict:
        return self.inferencer.predict_one(x)