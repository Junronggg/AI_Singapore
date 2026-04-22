from pathlib import Path
from typing import Dict, List

import pandas as pd

from configs.settings import settings
from src.common.logger import get_logger
from src.common.schemas import ProcessedTelemetryMessage
from src.common.utils import save_json

logger = get_logger(__name__)


class TelemetryPublisher:
    def dataframe_to_messages(
        self,
        df: pd.DataFrame,
        timestamp_col: str,
        feature_cols: List[str],
        split_name: str,
        include_label: bool = True,
    ) -> List[dict]:
        messages = []

        for _, row in df.iterrows():
            values = {col: float(row[col]) for col in feature_cols}
            payload = {
                "timestamp": row[timestamp_col],
                "split": split_name,
                "values": values,
            }

            if include_label and "label" in df.columns:
                payload["label"] = int(row["label"])

            msg = ProcessedTelemetryMessage(**payload)
            messages.append(msg.model_dump(mode="json"))

        return messages

    def save_sample_message(self, message: Dict, filename: str = "processed_telemetry.json") -> None:
        output_path = settings.SAMPLE_MESSAGES_DIR / filename
        save_json(message, output_path)
        logger.info("Saved sample message to %s", output_path)

    def publish(self, messages: List[dict]) -> None:
        if not messages:
            logger.warning("No messages to publish.")
            return

        logger.info("Prepared %d telemetry messages for downstream agents.", len(messages))
        self.save_sample_message(messages[0], "processed_telemetry.json")