from pathlib import Path
from typing import Dict

import pandas as pd

from configs.settings import settings
from src.common.logger import get_logger
from src.common.validators import validate_non_empty_dataframe

logger = get_logger(__name__)


class SWaTLoader:
    def __init__(self, raw_dir: Path | None = None):
        self.raw_dir = raw_dir or settings.DATA_RAW_DIR

    def _read_csv(self, filename: str) -> pd.DataFrame:
        file_path = self.raw_dir / filename
        logger.info("Loading file: %s", file_path)
        df = pd.read_csv(file_path, low_memory=False, encoding="utf-8-sig")
        validate_non_empty_dataframe(df, filename)
        return df

    def load_all(self) -> Dict[str, pd.DataFrame]:
        return {
            "train_normal": self._read_csv(settings.TRAIN_FILE),
            "val_normal": self._read_csv(settings.VAL_FILE),
            "a12_full": self._read_csv(settings.A12_FILE),
        }