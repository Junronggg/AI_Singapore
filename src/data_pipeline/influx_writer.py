import pandas as pd

from configs.settings import settings
from src.common.logger import get_logger

logger = get_logger(__name__)


class InfluxWriter:
    def __init__(self):
        self.enabled = settings.INFLUX_ENABLED

    def write_dataframe(self, df: pd.DataFrame, measurement: str) -> None:
        if not self.enabled:
            logger.info("InfluxDB disabled. Skipping write for measurement=%s", measurement)
            return

        logger.info("Would write %d rows to InfluxDB measurement=%s", len(df), measurement)
        # Add real InfluxDB logic later if needed.