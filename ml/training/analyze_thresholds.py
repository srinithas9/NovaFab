from pathlib import Path

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)


BASE_DIR = Path(__file__).resolve().parents[2]

SPLIT_DIR = BASE_DIR / "data" / "processed" / "splits"

TRAIN_PATH = SPLIT_DIR / "train.csv"
VALIDATION_PATH = SPLIT_DIR / "validation.csv"

TARGET_COLUMN = "target"
DATE_COLUMN = "date"


def load_data():
    train = pd.read_csv(TRAIN_PATH)
    validation = pd.read_csv(VALIDATION_PATH)

    return train, validation


def prepare_features(train, validation):
    feature_columns = [
        column
        for column in train.columns
        if column not in {TARGET_COLUMN, DATE_COLUMN}
    ]

    X_train = train[feature_columns]
    y_train = train[TARGET_COLUMN]

    X_validation = validation[feature_columns]
    y_validation = validation[TARGET_COLUMN]

    return X_train, y_train, X_validation, y_validation


def build_model():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )


def main():
    train, validation = load_data()

    X_train, y_train, X_validation, y_validation = prepare_features(
        train,
        validation,
    )

    model = build_model()

    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_validation)[:, 1]

    pr_auc = average_precision_score(
        y_validation,
        probabilities,
    )

    thresholds = [
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
    ]

    results = []

    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)

        precision = precision_score(
            y_validation,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_validation,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_validation,
            predictions,
            zero_division=0,
        )

        predicted_positive = int(predictions.sum())

        results.append(
            {
                "threshold": threshold,
                "predicted_positive": predicted_positive,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )

    results_df = pd.DataFrame(results)

    print("=" * 70)
    print("RANDOM FOREST THRESHOLD ANALYSIS")
    print("=" * 70)

    print()
    print(f"Validation rows: {len(validation):,}")
    print(f"Actual positives: {y_validation.sum()}")
    print(f"PR-AUC: {pr_auc:.4f}")

    print()
    print(
        results_df.to_string(
            index=False,
            formatters={
                "threshold": "{:.2f}".format,
                "precision": "{:.4f}".format,
                "recall": "{:.4f}".format,
                "f1": "{:.4f}".format,
            },
        )
    )


if __name__ == "__main__":
    main()