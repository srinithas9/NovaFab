from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "raw" / "quality_inspections.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "quality_features.csv"


def load_quality_data() -> pd.DataFrame:
    """Load quality inspections and create the machine-day key."""
    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["inspection_time"],
    )

    df["date"] = df["inspection_time"].dt.date

    return df


def build_quality_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate quality inspections into one row per machine per day.

    The resulting features describe the quality behavior observed
    during that machine-day.
    """

    grouped = df.groupby(["machine_code", "date"])

    features = grouped.agg(
        inspection_count=("result", "count"),
        failed_inspections=("result", lambda x: (x == "FAIL").sum()),
        review_inspections=("result", lambda x: (x == "REVIEW").sum()),
        total_defects=("defect_count", "sum"),
        average_defects=("defect_count", "mean"),
    ).reset_index()

    features["failure_rate"] = (
        features["failed_inspections"]
        / features["inspection_count"]
    )

    features["review_rate"] = (
        features["review_inspections"]
        / features["inspection_count"]
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

    assert (features["inspection_count"] > 0).all()
    assert (features["failed_inspections"] >= 0).all()
    assert (features["review_inspections"] >= 0).all()
    assert (features["total_defects"] >= 0).all()
    assert (features["average_defects"] >= 0).all()

    assert (
        features["failed_inspections"]
        <= features["inspection_count"]
    ).all()

    assert (
        features["review_inspections"]
        <= features["inspection_count"]
    ).all()

    assert features["failure_rate"].between(0, 1).all()
    assert features["review_rate"].between(0, 1).all()

    numeric_columns = [
        "inspection_count",
        "failed_inspections",
        "review_inspections",
        "total_defects",
        "average_defects",
        "failure_rate",
        "review_rate",
    ]

    assert not features[numeric_columns].isna().any().any()


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_data = load_quality_data()
    features = build_quality_features(raw_data)

    validate_features(features)

    features.to_csv(OUTPUT_PATH, index=False)

    print("=" * 60)
    print("QUALITY FEATURE BUILD COMPLETE")
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
                "failure_rate",
                "review_rate",
                "total_defects",
                "average_defects",
            ]
        ]
        .describe()
        .round(4)
        .to_string()
    )

    print()
    print("Sample:")
    print(features.head(3).to_string(index=False))


if __name__ == "__main__":
    main()