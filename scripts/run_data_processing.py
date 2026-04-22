import json

from configs.settings import settings
from src.common.logger import get_logger
from src.common.utils import save_csv, save_joblib, save_json, save_npy
from src.data_pipeline.cleaner import DataCleaner
from src.data_pipeline.features import FeatureEngineer
from src.data_pipeline.influx_writer import InfluxWriter
from src.data_pipeline.loader import SWaTLoader
from src.data_pipeline.publisher import TelemetryPublisher

logger = get_logger(__name__)


def main():
    loader = SWaTLoader()
    cleaner = DataCleaner()
    feature_engineer = FeatureEngineer()
    publisher = TelemetryPublisher()
    influx_writer = InfluxWriter()

    raw = loader.load_all()

    # Clean all
    for key in raw:
        raw[key] = cleaner.clean_column_names(raw[key])

    timestamp_col = cleaner.find_timestamp_column(raw["train_normal"])

    for key in raw:
        raw[key] = cleaner.parse_timestamp(raw[key], timestamp_col)

    if settings.ADD_TIME_FEATURES:
        for key in raw:
            raw[key] = feature_engineer.add_time_features(raw[key], timestamp_col)

    for key in raw:
        raw[key] = cleaner.convert_to_numeric(raw[key], exclude_cols=[timestamp_col])

    a12_normal, attack_test = cleaner.split_a12_normal_attack(raw["a12_full"])

    splits = {
        "train_normal": raw["train_normal"],
        "val_normal": raw["val_normal"],
        "a12_normal": a12_normal,
        "attack_test": attack_test,
    }

    splits, _ = cleaner.align_common_columns(splits, timestamp_col=timestamp_col)

    train_df = splits["train_normal"]
    val_df = splits["val_normal"]
    a12_normal_df = splits["a12_normal"]
    attack_df = splits["attack_test"]

    train_df, drop_info = cleaner.drop_bad_columns(
        train_df,
        exclude_cols=[timestamp_col],
        max_missing_ratio=settings.MAX_MISSING_RATIO,
        drop_constant=True,
    )

    feature_cols = [c for c in train_df.columns if c != timestamp_col]

    val_df = val_df[[timestamp_col] + feature_cols].copy()
    a12_normal_df = a12_normal_df[[timestamp_col] + feature_cols].copy()
    attack_df = attack_df[[timestamp_col] + feature_cols].copy()

    train_df, other_filled, fill_values = cleaner.fill_missing_with_train_median(
        train_df=train_df,
        other_dfs={
            "val_normal": val_df,
            "a12_normal": a12_normal_df,
            "attack_test": attack_df,
        },
        feature_cols=feature_cols,
    )

    val_df = other_filled["val_normal"]
    a12_normal_df = other_filled["a12_normal"]
    attack_df = other_filled["attack_test"]

    train_df = feature_engineer.attach_labels(train_df, 0)
    val_df = feature_engineer.attach_labels(val_df, 0)
    a12_normal_df = feature_engineer.attach_labels(a12_normal_df, 0)
    attack_df = feature_engineer.attach_labels(attack_df, 1)

    scaler = feature_engineer.fit_scaler(train_df, feature_cols)

    X_train = feature_engineer.transform_split(train_df, feature_cols, scaler)
    X_val = feature_engineer.transform_split(val_df, feature_cols, scaler)
    X_a12_normal = feature_engineer.transform_split(a12_normal_df, feature_cols, scaler)
    X_attack = feature_engineer.transform_split(attack_df, feature_cols, scaler)

    y_train = train_df["label"].to_numpy()
    y_val = val_df["label"].to_numpy()
    y_a12_normal = a12_normal_df["label"].to_numpy()
    y_attack = attack_df["label"].to_numpy()

    save_csv(train_df, settings.DATA_PROCESSED_DIR / "train_normal_processed.csv")
    save_csv(val_df, settings.DATA_PROCESSED_DIR / "val_normal_processed.csv")
    save_csv(a12_normal_df, settings.DATA_PROCESSED_DIR / "a12_normal_processed.csv")
    save_csv(attack_df, settings.DATA_PROCESSED_DIR / "attack_test_processed.csv")

    save_npy(X_train, settings.DATA_PROCESSED_DIR / "X_train.npy")
    save_npy(X_val, settings.DATA_PROCESSED_DIR / "X_val.npy")
    save_npy(X_a12_normal, settings.DATA_PROCESSED_DIR / "X_a12_normal.npy")
    save_npy(X_attack, settings.DATA_PROCESSED_DIR / "X_attack.npy")

    save_npy(y_train, settings.DATA_PROCESSED_DIR / "y_train.npy")
    save_npy(y_val, settings.DATA_PROCESSED_DIR / "y_val.npy")
    save_npy(y_a12_normal, settings.DATA_PROCESSED_DIR / "y_a12_normal.npy")
    save_npy(y_attack, settings.DATA_PROCESSED_DIR / "y_attack.npy")

    save_joblib(scaler, settings.DATA_PROCESSED_DIR / "scaler.pkl")

    metadata = {
        "timestamp_col": timestamp_col,
        "feature_cols": feature_cols,
        "num_features": len(feature_cols),
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "a12_normal_rows": len(a12_normal_df),
        "attack_rows": len(attack_df),
        "drop_info": drop_info,
        "fill_values": fill_values,
    }
    save_json(metadata, settings.DATA_PROCESSED_DIR / "metadata.json")

    train_messages = publisher.dataframe_to_messages(
        train_df.head(5),
        timestamp_col=timestamp_col,
        feature_cols=feature_cols,
        split_name="train_normal",
    )
    publisher.publish(train_messages)

    influx_writer.write_dataframe(train_df.head(100), "train_normal_processed")

    logger.info("Data processing completed successfully.")
    logger.info("Processed feature count: %d", len(feature_cols))


if __name__ == "__main__":
    main()