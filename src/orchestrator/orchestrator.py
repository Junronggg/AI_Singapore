from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.agents.anomaly_agent import AnomalyDetectionAgent
from src.agents.decision_agent import DecisionSupportAgent
from src.agents.diagnosis_agent import RootCauseDiagnosisAgent
from src.agents.monitoring_agent import MonitoringAgent
from src.agents.predictive_agent import PredictiveMaintenanceAgent
from src.orchestrator.incident_manager import IncidentManager


class MultiAgentOrchestrator:
    def __init__(self, model_dir: Path, feature_cols: List[str], scaler):
        self.feature_cols = feature_cols
        self.scaler = scaler

        self.monitoring_agent = MonitoringAgent(feature_cols=feature_cols)
        self.anomaly_agent = AnomalyDetectionAgent(model_dir=model_dir)
        self.diagnosis_agent = RootCauseDiagnosisAgent(feature_cols=feature_cols, top_k=5)
        self.predictive_agent = PredictiveMaintenanceAgent()
        self.decision_agent = DecisionSupportAgent()
        self.incident_manager = IncidentManager(max_history=50)

    def process_row(self, row: pd.Series, timestamp_col: str) -> Dict:
        monitoring_result = self.monitoring_agent.inspect_row(row)

        if not monitoring_result["is_valid"]:
            return {
                "timestamp": str(row[timestamp_col]),
                "status": "INVALID_INPUT",
                "monitoring": monitoring_result,
            }

        x_raw = row[self.feature_cols].astype(float).values.reshape(1, -1)
        x_scaled = self.scaler.transform(x_raw)

        anomaly_result = self.anomaly_agent.run(x_scaled)
        persistence_count = self.incident_manager.update(anomaly_result["is_anomaly"])

        diagnosis_result = self.diagnosis_agent.diagnose(
            row_scaled=x_scaled,
            anomaly_result=anomaly_result,
        )

        predictive_result = self.predictive_agent.run(
            anomaly_result=anomaly_result,
            diagnosis_result=diagnosis_result,
            persistence_count=persistence_count,
        )

        decision_result = self.decision_agent.recommend(
            diagnosis_result=diagnosis_result,
            predictive_result=predictive_result,
        )

        return {
            "timestamp": str(row[timestamp_col]),
            "status": "OK",
            "monitoring": monitoring_result,
            "anomaly": anomaly_result,
            "diagnosis": diagnosis_result,
            "predictive": predictive_result,
            "decision": decision_result,
            "incident_state": {
                "persistence_count": persistence_count,
                "recent_anomaly_ratio": self.incident_manager.recent_anomaly_ratio(),
            },
        }