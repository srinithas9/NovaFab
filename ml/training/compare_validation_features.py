from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

VALIDATION_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "splits"
    / "validation.csv"
)

df = pd.read_csv(VALIDATION_PATH)

feature_columns = [
    column
    for column in df.columns
    if column not in {"target", "date"}
]

positive = df[df["target"] == 1][feature_columns]
negative = df[df["target"] == 0][feature_columns]

comparison = pd.DataFrame(
    {
        "positive_mean": positive.mean(),
        "negative_mean": negative.mean(),
    }
)

comparison["difference"] = (
    comparison["positive_mean"]
    - comparison["negative_mean"]
)

comparison["abs_difference"] = (
    comparison["difference"].abs()
)

print("=" * 80)
print("VALIDATION FEATURE COMPARISON")
print("=" * 80)

print()
print("Top features where positive and negative days differ:")
print()

print(
    comparison
    .sort_values("abs_difference", ascending=False)
    .head(20)
    .round(4)
    .to_string()
)
