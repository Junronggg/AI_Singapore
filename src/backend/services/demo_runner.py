import threading
import time
from pathlib import Path

import pandas as pd

from configs.settings import settings
from src.backend import state
from src.common.logger import get_logger
from src.common.utils import load_joblib, load_json
from src.orchestrator.orchestrator import MultiAgentOrchestrator

logger = get_logger(__name__)


class DemoRunner:
    def __init__(self):
        self.thread = None
        self.stop_flag = False

    def _build_dashboard_response(self, result: dict) -> dict:
        if result["status"] != "OK":
            return {
                "timestamp": result.get("timestamp"),
                "system_status": "INVALID",
                "incident_id": "N/A",
                "status": "INVALID_INPUT",
                "severity": "UNKNOWN",
                "affected_asset": "Unknown",
                "zone": "Unknown",
                "anomaly_score": 0.0,
                "failure_risk_score": 0.0,
                "maintenance_horizon_hours": 24,
                "root_cause_summary": "Input data quality issue detected.",
                "confidence": 0.0,
                "recommended_action": "Check telemetry pipeline and retry.",
                "last_updated": result.get("timestamp"),
                "likely_root_cause": "Unknown",
                "affected_components": [],
                "persistence_count": 0,
                "audit_trace": [
                    "Telemetry ingested from replay stream.",
                    "Monitoring agent flagged invalid input.",
                    "Further agent processing skipped.",
                ],
                "recommended_actions": [
                    {
                        "action": "Check input data quality",
                        "priority": "P1",
                        "impact": "No operational action yet",
                        "approval_required": "No",
                    }
                ],
                "digital_twin_nodes": [
                    {"name": "Reservoir", "status": "normal"},
                    {"name": "Valve V12", "status": "normal"},
                    {"name": "Pump P101", "status": "warning"},
                    {"name": "Sensor FIT101", "status": "normal"},
                    {"name": "Pipe Segment A", "status": "normal"},
                ],
                "plain_explanation": "The system could not analyze this row because the telemetry input was invalid.",
            }

        anomaly = result["anomaly"]
        diagnosis = result["diagnosis"]
        predictive = result["predictive"]
        decision = result["decision"]
        incident_state = result["incident_state"]

        risk_level = predictive["risk_level"]
        if risk_level == "HIGH":
            system_status = "Critical"
            severity = "HIGH"
        elif risk_level == "MEDIUM":
            system_status = "Warning"
            severity = "MEDIUM"
        else:
            system_status = "Normal"
            severity = "LOW"

        top_features = [x["feature"] for x in diagnosis["top_contributing_features"]]
        likely_root_cause = diagnosis["likely_root_cause"] or "Unknown"

        # dashboard-friendly anomaly score
        display_anomaly_score = max(0.0, min(1.0, 0.3 - anomaly["anomaly_score"] * 4.0))

        # severity rule aligned with chart threshold
        if display_anomaly_score > 0.29:
            system_status = "Critical"
            severity = "HIGH"
            incident_status = "ACTIVE"
        elif display_anomaly_score > 0.15:
            system_status = "Warning"
            severity = "MEDIUM"
            incident_status = "MONITORING"
        else:
            system_status = "Normal"
            severity = "LOW"
            incident_status = "MONITORING"

        recommended_actions = [
            {
                "action": decision["recommended_action"],
                "priority": predictive["maintenance_priority"],
                "impact": "Low operational disruption" if risk_level != "HIGH" else "Potential operational disruption",
                "approval_required": "Yes" if risk_level in {"HIGH", "MEDIUM"} else "No",
            },
            {
                "action": f"Monitor {likely_root_cause} closely for the next 10 minutes",
                "priority": "P2",
                "impact": "No disruption",
                "approval_required": "No",
            },
            {
                "action": "Schedule maintenance review",
                "priority": "P2" if risk_level != "LOW" else "P3",
                "impact": "Planned intervention",
                "approval_required": "Yes",
            },
        ]

        audit_trace = [
            "Telemetry ingested from SWaT replay stream.",
            "Monitoring agent validated incoming row.",
            "Anomaly detection agent scored the telemetry snapshot.",
            "Root cause diagnosis agent ranked the most abnormal features.",
            "Predictive maintenance agent estimated maintenance risk.",
            "Decision support agent generated operator recommendation.",
        ]

        digital_twin_nodes = [
            {"name": "Reservoir", "status": "normal"},
            {"name": "Valve V12", "status": "warning" if risk_level != "LOW" else "normal"},
            {"name": "Pump P101", "status": "critical" if risk_level == "HIGH" else ("warning" if risk_level == "MEDIUM" else "normal")},
            {"name": "Sensor FIT101", "status": "warning" if anomaly["is_anomaly"] else "normal"},
            {"name": "Pipe Segment A", "status": "normal"},
        ]

        return {
            "timestamp": result["timestamp"],
            "system_status": system_status,
            "incident_id": "INC_001",
            "status": "ACTIVE" if anomaly["is_anomaly"] else "MONITORING",
            "severity": severity,
            "affected_asset": likely_root_cause,
            "zone": "ZONE_A",
            "anomaly_score": max(0.0, min(1.0, -anomaly["anomaly_score"] * 2 + 0.2)),
            "raw_anomaly_score": anomaly["anomaly_score"],
            "failure_risk_score": predictive["risk_score"],
            "maintenance_horizon_hours": 24 if risk_level == "HIGH" else (48 if risk_level == "MEDIUM" else 72),
            "root_cause_summary": f"Likely abnormal behavior centered around {likely_root_cause}.",
            "confidence": min(0.95, 0.55 + 0.08 * len(top_features)),
            "recommended_action": decision["recommended_action"],
            "last_updated": result["timestamp"],
            "likely_root_cause": likely_root_cause,
            "affected_components": top_features,
            "persistence_count": incident_state["persistence_count"],
            "audit_trace": audit_trace,
            "recommended_actions": recommended_actions,
            "digital_twin_nodes": digital_twin_nodes,
            "plain_explanation": (
                f"The system observed unusual behavior in {likely_root_cause}. "
                f"Based on the current anomaly score and recent persistence, the risk level is {risk_level.lower()}."
            ),
        }

    def _run_loop(self, speed_seconds: float = 0.2):
        import numpy as np
        import pandas as pd
        from pathlib import Path

        processed_dir = settings.DATA_PROCESSED_DIR
        metadata = load_json(processed_dir / "metadata.json")
        scaler = load_joblib(processed_dir / "scaler.pkl")

        feature_cols = metadata["feature_cols"]
        timestamp_col = metadata["timestamp_col"]

        model_dir = Path("src/models/anomaly/saved")
        df = pd.read_csv(processed_dir / "attack_test_processed.csv")
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

        orchestrator = MultiAgentOrchestrator(
            model_dir=model_dir,
            feature_cols=feature_cols,
            scaler=scaler,
        )

        # reset old state every time demo starts
        state.HISTORY = []
        state.LATEST_RESULT = {}

        # ---------------------------------
        # 1. Find the strongest anomaly row
        # ---------------------------------
        x_df = df[feature_cols].astype(float)
        x_scaled = scaler.transform(x_df)

        # IsolationForest decision_function:
        # lower = more abnormal
        inferencer = orchestrator.anomaly_agent.inferencer
        raw_scores = inferencer.bundle.model.decision_function(x_scaled)

        peak_idx = int(np.argmin(raw_scores))
        peak_time = df.iloc[peak_idx][timestamp_col]

        logger.info("Most anomalous row index: %s", peak_idx)
        logger.info("Most anomalous timestamp: %s", peak_time)
        logger.info("Most anomalous raw score: %s", float(raw_scores[peak_idx]))

        # ---------------------------------
        # 2. Replay short window around it
        # ---------------------------------
        pre_attack_seconds = 10
        post_attack_seconds = 60

        start_idx = max(0, peak_idx - pre_attack_seconds)
        end_idx = min(len(df), peak_idx + post_attack_seconds)

        demo_df = df.iloc[start_idx:end_idx].copy().reset_index(drop=True)

        # choose some real sensor columns for frontend if available
        preferred_sensor_cols = [c for c in ["FIT101.Pv", "LIT101.Pv", "AIT201.Pv", "AIT503.Pv"] if c in df.columns]
        if not preferred_sensor_cols:
            preferred_sensor_cols = feature_cols[:3]

        logger.info(
            "Replay window: %s -> %s",
            demo_df.iloc[0][timestamp_col],
            demo_df.iloc[-1][timestamp_col],
        )

        # ---------------------------------
        # 3. Replay live
        # ---------------------------------
        for _, row in demo_df.iterrows():
            if self.stop_flag:
                break

            result = orchestrator.process_row(row=row, timestamp_col=timestamp_col)
            dashboard_result = self._build_dashboard_response(result)

            # attach real sensor snapshot
            sensor_snapshot = {}
            for col in preferred_sensor_cols:
                try:
                    sensor_snapshot[col] = float(row[col])
                except Exception:
                    sensor_snapshot[col] = None

            dashboard_result["sensor_snapshot"] = sensor_snapshot
            dashboard_result["threshold"] = 0.20
            dashboard_result["is_anomaly"] = bool(result.get("anomaly", {}).get("is_anomaly", False))
            dashboard_result["raw_model_score"] = float(result.get("anomaly", {}).get("anomaly_score", 0.0))

            state.LATEST_RESULT = dashboard_result
            state.HISTORY.append(dashboard_result)

            if len(state.HISTORY) > 300:
                state.HISTORY = state.HISTORY[-300:]

            time.sleep(speed_seconds)

        state.DEMO_RUNNING = False
        logger.info("Demo replay stopped.")

    def start(self, speed_seconds: float = 1.0):
        if state.DEMO_RUNNING:
            return False

        self.stop_flag = False
        state.DEMO_RUNNING = True
        self.thread = threading.Thread(target=self._run_loop, kwargs={"speed_seconds": speed_seconds}, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.stop_flag = True
        state.DEMO_RUNNING = False