from pathlib import Path

import pandas as pd

from configs.settings import settings
from src.common.logger import get_logger
from src.common.utils import load_joblib, load_json
from src.orchestrator.orchestrator import MultiAgentOrchestrator

logger = get_logger(__name__)


def main():
    processed_dir = settings.DATA_PROCESSED_DIR
    model_dir = Path("src/models/anomaly/saved")

    metadata = load_json(processed_dir / "metadata.json")
    scaler = load_joblib(processed_dir / "scaler.pkl")

    feature_cols = metadata["feature_cols"]
    timestamp_col = metadata["timestamp_col"]

    df_attack = pd.read_csv(processed_dir / "attack_test_processed.csv")
    df_attack[timestamp_col] = pd.to_datetime(df_attack[timestamp_col], errors="coerce")

    orchestrator = MultiAgentOrchestrator(
        model_dir=model_dir,
        feature_cols=feature_cols,
        scaler=scaler,
    )

    print("\n===== LOCAL DEMO OUTPUT =====\n")

    for i in range(min(10, len(df_attack))):
        row = df_attack.iloc[i]
        result = orchestrator.process_row(row=row, timestamp_col=timestamp_col)

        print(f"Row {i}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Status: {result['status']}")

        if result["status"] == "OK":
            print(f"Anomaly score: {result['anomaly']['anomaly_score']:.6f}")
            print(f"Is anomaly: {result['anomaly']['is_anomaly']}")
            print(f"Likely root cause: {result['diagnosis']['likely_root_cause']}")
            print(f"Risk level: {result['predictive']['risk_level']}")
            print(f"Recommendation: {result['decision']['recommended_action']}")
        else:
            print(f"Monitoring issue: {result['monitoring']}")

        print("-" * 60)


if __name__ == "__main__":
    main()