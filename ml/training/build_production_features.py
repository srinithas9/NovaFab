from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "raw" / "production_runs.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "production_features.csv"


def load_production_data() -> pd.DataFrame:
    """Load production runs and derive the machine-day key."""
    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["start_time", "end_time"],
    )

    df["date"] = df["start_time"].dt.date

    return df


def build_production_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate production activity into one row per machine per day.

    Efficiency:
        produced quantity / target quantity

    Rejection rate:
        rejected quantity / produced quantity
    """

    grouped = df.groupby(["machine_code", "date"])

    features = grouped.agg(
        production_runs=("batch_number", "count"),
        target_quantity=("target_quantity", "sum"),
        produced_quantity=("produced_quantity", "sum"),
        rejected_quantity=("rejected_quantity", "sum"),
    ).reset_index()

    features["production_efficiency"] = (
        features["produced_quantity"]
        / features["target_quantity"]
    )

    features["rejection_rate"] = (
        features["rejected_quantity"]
        / features["produced_quantity"]
    )

    return features


def validate_features(features: pd.DataFrame) -> None:
    """Run structural and business-rule checks."""

    expected_rows = 9 * 273

    assert len(features) == expected_rows, (
        f"Expected {expected_rows} machine-days, "
        f"got {len(features)}"
    )

    assert features["machine_code"].nunique() == 9
    assert features["date"].nunique() == 273

    assert (features["production_runs"] > 0).all()
    assert (features["target_quantity"] > 0).all()
    assert (features["produced_quantity"] > 0).all()
    assert (features["rejected_quantity"] >= 0).all()

    assert (
        features["produced_quantity"]
        >= features["rejected_quantity"]
    ).all()

    assert features["production_efficiency"].between(0, 1).all()
    assert features["rejection_rate"].between(0, 1).all()

    numeric_columns = [
        "production_runs",
        "target_quantity",
        "produced_quantity",
        "rejected_quantity",
        "production_efficiency",
        "rejection_rate",
    ]

    assert not features[numeric_columns].isna().any().any()


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_data = load_production_data()
    features = build_production_features(raw_data)

    validate_features(features)

    features.to_csv(OUTPUT_PATH, index=False)

    print("=" * 60)
    print("PRODUCTION FEATURE BUILD COMPLETE")
    print("=" * 60)
    print(f"Input rows:       {len(raw_data):,}")
    print(f"Output rows:      {len(features):,}")
    print(f"Machines:         {features['machine_code'].nunique()}")
    print(f"Machine-days:     {features['date'].nunique()}")
    print(f"Output file:      {OUTPUT_PATH}")
    print()
    print("Feature columns:")

    for column in features.columns:
        print(f"  - {column}")

    print()
    print("Feature summary:")
    print(
        features[
            [
                "production_efficiency",
                "rejection_rate",
            ]
        ].describe().round(4).to_string()
    )

    print()
    print("Sample:")
    print(features.head(3).to_string(index=False))


if __name__ == "__main__":
    main()