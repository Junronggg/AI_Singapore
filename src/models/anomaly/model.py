from dataclasses import dataclass
from typing import Optional

from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyModelBundle:
    model: IsolationForest
    threshold: float