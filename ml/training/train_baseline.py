from pathlib import Path

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


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
        if column not in {
            TARGET_COLUMN,
            DATE_COLUMN,
        }
    ]

    X_train = train[feature_columns]
    y_train = train[TARGET_COLUMN]

    X_validation = validation[feature_columns]
    y_validation = validation[TARGET_COLUMN]

    return (
        X_train,
        y_train,
        X_validation,
        y_validation,
        feature_columns,
    )


def build_model():
    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_model(
    model,
    X_validation,
    y_validation,
):
    probabilities = model.predict_proba(
        X_validation
    )[:, 1]

    predictions = (
        probabilities >= 0.50
    ).astype(int)

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

    roc_auc = roc_auc_score(
        y_validation,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_validation,
        probabilities,
    )

    print()
    print("=" * 70)
    print("BASELINE VALIDATION RESULTS")
    print("=" * 70)

    print()
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")

    print()
    print("Confusion matrix:")
    print(
        confusion_matrix(
            y_validation,
            predictions,
        )
    )

    print()
    print("Classification report:")
    print(
        classification_report(
            y_validation,
            predictions,
            zero_division=0,
        )
    )


def main():
    train, validation = load_data()

    print("=" * 70)
    print("PREDICTIVE MAINTENANCE BASELINE")
    print("=" * 70)

    print()
    print(
        f"Training rows:   {len(train):,}"
    )

    print(
        f"Validation rows: {len(validation):,}"
    )

    print(
        f"Training positives: "
        f"{train[TARGET_COLUMN].sum()}"
    )

    print(
        f"Validation positives: "
        f"{validation[TARGET_COLUMN].sum()}"
    )

    (
        X_train,
        y_train,
        X_validation,
        y_validation,
        feature_columns,
    ) = prepare_features(
        train,
        validation,
    )

    print()
    print(
        f"Features used: {len(feature_columns)}"
    )

    model = build_model()

    model.fit(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_validation,
        y_validation,
    )


if __name__ == "__main__":
    main()