from collections import deque
from typing import Deque


class IncidentManager:
    def __init__(self, max_history: int = 50):
        self.anomaly_history: Deque[bool] = deque(maxlen=max_history)

    def update(self, is_anomaly: bool) -> int:
        self.anomaly_history.append(bool(is_anomaly))
        return self.persistence_count()

    def persistence_count(self) -> int:
        return sum(self.anomaly_history)

    def recent_anomaly_ratio(self) -> float:
        if not self.anomaly_history:
            return 0.0
        return sum(self.anomaly_history) / len(self.anomaly_history)