from src.models.predictive.model import PredictiveRiskResult


class PredictiveRiskModel:
    def compute(
        self,
        anomaly_score: float,
        is_anomaly: bool,
        affected_feature_count: int,
        persistence_count: int,
    ) -> PredictiveRiskResult:
        """
        Convert anomaly results into a simple maintenance risk score.
        Lower anomaly_score means more abnormal.
        """

        anomaly_component = max(0.0, min(1.0, -anomaly_score * 5.0))
        feature_component = min(1.0, affected_feature_count / 10.0)
        persistence_component = min(1.0, persistence_count / 20.0)
        anomaly_flag_component = 1.0 if is_anomaly else 0.0

        risk_score = (
            0.4 * anomaly_component
            + 0.2 * feature_component
            + 0.2 * persistence_component
            + 0.2 * anomaly_flag_component
        )

        if risk_score >= 0.75:
            risk_level = "HIGH"
            priority = "P1"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            priority = "P2"
        else:
            risk_level = "LOW"
            priority = "P3"

        return PredictiveRiskResult(
            risk_score=float(risk_score),
            risk_level=risk_level,
            maintenance_priority=priority,
        )