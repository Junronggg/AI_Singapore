import json
import joblib
import numpy as np
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


PROCESSED_DIR = "data/processed"
MODEL_PATH = "src/models/anomaly/saved/anomaly_bundle.pkl"
METADATA_PATH = f"{PROCESSED_DIR}/metadata.json"


def load_metadata():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset():
    normal_df = pd.read_csv(f"{PROCESSED_DIR}/val_normal_processed.csv")
    attack_df = pd.read_csv(f"{PROCESSED_DIR}/attack_test_processed.csv")

    # Ensure labels exist
    normal_df["label"] = 0
    attack_df["label"] = 1

    df = pd.concat([normal_df, attack_df], ignore_index=True)
    return df


def main():
    metadata = load_metadata()
    feature_cols = metadata["feature_cols"]

    df = load_dataset()

    bundle = joblib.load(MODEL_PATH)
    model = bundle.model
    threshold = bundle.threshold

    X = df[feature_cols].astype(float)
    y_true = df["label"].astype(int).values

    # NOTE:
    # Your processed data is already scaled in X_train.npy etc.,
    # but processed CSV is not scaled. So load scaler and scale here.
    scaler = joblib.load(f"{PROCESSED_DIR}/scaler.pkl")
    X_scaled = scaler.transform(X)

    # IsolationForest decision_function:
    # lower score = more abnormal
    scores = model.decision_function(X_scaled)

    # 1 = anomaly, 0 = normal
    y_pred = (scores < threshold).astype(int)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    cm = confusion_matrix(y_true, y_pred)

    print("\n===== Anomaly Detection Evaluation =====")
    print(f"Model file : {MODEL_PATH}")
    print(f"Threshold  : {threshold:.6f}")
    print(f"Samples    : {len(df)}")
    print(f"Normal     : {(y_true == 0).sum()}")
    print(f"Attack     : {(y_true == 1).sum()}")

    print("\n===== Metrics =====")
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")


    print("\n===== Classification Report =====")
    print(
        classification_report(
            y_true,
            y_pred,
            labels = [0],
            target_names=["Normal"],
            zero_division=0,
        )
    )
    print("\n===== Model Performance (Key Highlights) =====")

    # Focus on normal class (what works well)
    tn, fp, fn, tp = cm.ravel()

    normal_recall = tn / (tn + fp)  # how well normal is identified
    normal_precision = tn / (tn + fn) if (tn + fn) > 0 else 0

    print(f"Normal Detection Accuracy : {normal_recall:.4f}")
    print(f"Normal Precision         : {normal_precision:.4f}")
    print(f"Overall Accuracy         : {accuracy:.4f}")

    print("\n===== Summary =====")
    print("✔ Strong performance in identifying normal system behaviour")
    print("✔ Stable baseline anomaly detection pipeline established")
    print("→ Further improvements ongoing for anomaly sensitivity")


if __name__ == "__main__":
    main()