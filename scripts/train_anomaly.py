from pathlib import Path

import numpy as np

from configs.settings import settings
from src.common.logger import get_logger
from src.models.anomaly.train import AnomalyTrainer

logger = get_logger(__name__)


def main():
    processed_dir = settings.DATA_PROCESSED_DIR
    model_dir = Path("src/models/anomaly/saved")
    model_dir.mkdir(parents=True, exist_ok=True)

    X_train = np.load(processed_dir / "X_train.npy")
    X_val = np.load(processed_dir / "X_val.npy")

    trainer = AnomalyTrainer(model_dir=model_dir)
    metadata = trainer.train(
        X_train=X_train,
        X_val=X_val,
        contamination=0.01,
        random_state=settings.RANDOM_SEED,
    )

    logger.info("Training complete: %s", metadata)


if __name__ == "__main__":
    main()