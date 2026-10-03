from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "data" / "processed" / "ml_dataset.csv"


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    feature_columns = [
        column
        for column in df.columns
        if column not in {
            "machine_code",
            "date",
            "target",
        }
    ]

    print("=" * 70)
    print("PREDICTIVE MAINTENANCE EDA")
    print("=" * 70)

    print()
    print("Dataset:")
    print(f"Rows:       {len(df):,}")
    print(f"Features:   {len(feature_columns)}")
    print(f"Machines:   {df['machine_code'].nunique()}")
    print(f"Date range: {df['date'].min()} → {df['date'].max()}")

    print()
    print("Target distribution:")
    print(
        df["target"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("Target rate:")
    print(
        df["target"]
        .mean()
        .round(4)
    )

    print()
    print("=" * 70)
    print("FEATURE COMPARISON: NEGATIVE VS POSITIVE CASES")
    print("=" * 70)

    negative = df[df["target"] == 0]
    positive = df[df["target"] == 1]

    comparison = pd.DataFrame(
        {
            "negative_mean": negative[feature_columns].mean(),
            "positive_mean": positive[feature_columns].mean(),
        }
    )

    comparison["absolute_difference"] = (
        comparison["positive_mean"]
        - comparison["negative_mean"]
    )

    comparison["relative_difference_pct"] = (
        comparison["absolute_difference"]
        / comparison["negative_mean"].replace(0, pd.NA)
    ) * 100

    comparison = comparison.sort_values(
        "relative_difference_pct",
        ascending=False,
    )

    print(
        comparison.round(3).to_string()
    )

    print()
    print("=" * 70)
    print("CORRECTIVE-MAINTENANCE CASES BY MACHINE")
    print("=" * 70)

    machine_summary = (
        df.groupby("machine_code")
        .agg(
            machine_days=("target", "size"),
            positive_days=("target", "sum"),
            positive_rate=("target", "mean"),
        )
        .sort_values(
            "positive_days",
            ascending=False,
        )
    )

    machine_summary["positive_rate"] = (
        machine_summary["positive_rate"] * 100
    ).round(2)

    print(
        machine_summary.to_string()
    )

    print()
    print("=" * 70)
    print("CORRELATION WITH TARGET")
    print("=" * 70)

    correlations = (
        df[feature_columns + ["target"]]
        .corr(numeric_only=True)["target"]
        .drop("target")
        .sort_values(
            key=lambda values: values.abs(),
            ascending=False,
        )
    )

    print(
        correlations.round(4).to_string()
    )

    print()
    print("=" * 70)
    print("MISSING VALUES")
    print("=" * 70)

    missing = (
        df[feature_columns]
        .isna()
        .sum()
        .sort_values(ascending=False)
    )

    print(missing.to_string())

    print()
    print("=" * 70)
    print("HIGHLY CORRELATED FEATURE PAIRS")
    print("=" * 70)

    correlation_matrix = df[feature_columns].corr()

    pairs = []

    for i, feature_a in enumerate(feature_columns):
        for feature_b in feature_columns[i + 1:]:
            correlation = correlation_matrix.loc[
                feature_a,
                feature_b,
            ]

            if abs(correlation) >= 0.90:
                pairs.append(
                    (
                        feature_a,
                        feature_b,
                        correlation,
                    )
                )

    if pairs:
        pairs.sort(
            key=lambda item: abs(item[2]),
            reverse=True,
        )

        for feature_a, feature_b, correlation in pairs:
            print(
                f"{feature_a:<35} "
                f"{feature_b:<35} "
                f"{correlation:.3f}"
            )
    else:
        print("No feature pairs with |correlation| >= 0.90.")


if __name__ == "__main__":
    main()