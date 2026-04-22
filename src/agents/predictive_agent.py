from typing import Dict

from src.models.predictive.infer import PredictiveRiskModel


class PredictiveMaintenanceAgent:
    def __init__(self):
        self.model = PredictiveRiskModel()

    def run(
        self,
        anomaly_result: Dict,
        diagnosis_result: Dict,
        persistence_count: int,
    ) -> Dict:
        result = self.model.compute(
            anomaly_score=anomaly_result["anomaly_score"],
            is_anomaly=anomaly_result["is_anomaly"],
            affected_feature_count=diagnosis_result["affected_feature_count"],
            persistence_count=persistence_count,
        )

        return {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "maintenance_priority": result.maintenance_priority,
        }