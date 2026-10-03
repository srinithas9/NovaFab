from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[2]

SPLIT_DIR = BASE_DIR / "data" / "processed" / "splits"

TRAIN_PATH = SPLIT_DIR / "train.csv"
VALIDATION_PATH = SPLIT_DIR / "validation.csv"


TARGET_COLUMN = "target"
DATE_COLUMN = "date"


train = pd.read_csv(TRAIN_PATH)
validation = pd.read_csv(VALIDATION_PATH)

feature_columns = [
    column
    for column in train.columns
    if column not in {TARGET_COLUMN, DATE_COLUMN}
]

X_train = train[feature_columns]
y_train = train[TARGET_COLUMN]

X_validation = validation[feature_columns]
y_validation = validation[TARGET_COLUMN]

model = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
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

model.fit(X_train, y_train)

probabilities = model.predict_proba(X_validation)[:, 1]

validation_result = validation[
    [DATE_COLUMN, TARGET_COLUMN]
].copy()

validation_result["probability"] = probabilities

print("=" * 70)
print("BASELINE MODEL DIAGNOSTICS")
print("=" * 70)

print()
print("Probability summary:")
print(
    pd.Series(probabilities)
    .describe()
    .round(4)
    .to_string()
)

print()
print("Probability by actual class:")

print()
print("Actual NEGATIVE:")
print(
    validation_result.loc[
        validation_result[TARGET_COLUMN] == 0,
        "probability"
    ]
    .describe()
    .round(4)
    .to_string()
)

print()
print("Actual POSITIVE:")
print(
    validation_result.loc[
        validation_result[TARGET_COLUMN] == 1,
        "probability"
    ]
    .describe()
    .round(4)
    .to_string()
)

print()
print("Top 15 positive examples by predicted probability:")
print(
    validation_result
    .sort_values("probability", ascending=False)
    .head(15)
    .to_string(index=False)
)

print()
print("Actual positive examples:")
print(
    validation_result[
        validation_result[TARGET_COLUMN] == 1
    ]
    .sort_values("probability", ascending=False)
    .to_string(index=False)
)

classifier = model.named_steps["model"]

coefficients = pd.DataFrame(
    {
        "feature": feature_columns,
        "coefficient": classifier.coef_[0],
    }
)

coefficients["absolute_coefficient"] = (
    coefficients["coefficient"].abs()
)

print()
print("Top 15 features by absolute coefficient:")
print(
    coefficients
    .sort_values(
        "absolute_coefficient",
        ascending=False,
    )
    .head(15)
    .to_string(index=False)
)

print()
print("=" * 70)
