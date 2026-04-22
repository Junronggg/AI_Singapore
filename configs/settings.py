from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "water-multi-agent-system"
    DEBUG: bool = True

    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    DATA_RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
    DATA_PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    SAMPLE_MESSAGES_DIR: Path = PROJECT_ROOT / "data" / "sample_messages"

    TRAIN_FILE: str = "SWaT.A10_OTDataset_19-Feb-2026_0930_1735.csv"
    VAL_FILE: str = "SWaT.A10_OTDataset_20-Feb-2026_0905_1710.csv"
    A12_FILE: str = "11-Mar-2026_0900_1700.csv"

    MAX_MISSING_RATIO: float = 0.2
    ADD_TIME_FEATURES: bool = True
    SAVE_INTERMEDIATE_CSV: bool = True

    REDIS_ENABLED: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CHANNEL: str = "processed_telemetry"

    INFLUX_ENABLED: bool = False
    INFLUX_URL: str = "http://localhost:8086"
    INFLUX_TOKEN: str = ""
    INFLUX_ORG: str = ""
    INFLUX_BUCKET: str = "swat"

    RANDOM_SEED: int = 42


settings = Settings()

settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_MESSAGES_DIR.mkdir(parents=True, exist_ok=True)