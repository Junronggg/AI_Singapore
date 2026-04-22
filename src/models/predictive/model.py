from dataclasses import dataclass


@dataclass
class PredictiveRiskResult:
    risk_score: float
    risk_level: str
    maintenance_priority: str