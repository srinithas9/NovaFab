from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "raw" / "sensor_readings.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sensor_features.csv"

SENSOR_COLUMNS = [
    "temperature",
    "vibration",
    "pressure",
    "power_consumption",
]


def load_sensor_data() -> pd.DataFrame:
    """Load raw sensor readings and create the machine-day key."""
    df = pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])

    df["date"] = df["timestamp"].dt.date

    return df


def build_sensor_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw sensor readings into one row per machine per day.

    Each feature represents sensor behavior observed during that day.
    """

    grouped = df.groupby(["machine_code", "date"])

    features = grouped[SENSOR_COLUMNS].agg(
        [
            "mean",
            "std",
            "min",
            "max",
        ]
    )

    features.columns = [
        f"{sensor}_{stat}"
        for sensor, stat in features.columns
    ]

    features = features.reset_index()

    return features


def validate_features(features: pd.DataFrame) -> None:
    """Run basic structural checks on the generated feature dataset."""

    expected_rows = 9 * 273

    assert len(features) == expected_rows, (
        f"Expected {expected_rows} machine-days, "
        f"got {len(features)}"
    )

    assert features["machine_code"].nunique() == 9

    assert features["date"].nunique() == 273

    feature_columns = [
        column
        for column in features.columns
        if column not in {"machine_code", "date"}
    ]

    assert not features[feature_columns].isna().any().any(), (
        "Sensor feature dataset contains unexpected NaN values."
    )

    assert (features["temperature_mean"] > 0).all()
    assert (features["vibration_mean"] >= 0).all()
    assert (features["pressure_mean"] > 0).all()
    assert (features["power_consumption_mean"] > 0).all()


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_data = load_sensor_data()
    features = build_sensor_features(raw_data)

    validate_features(features)

    features.to_csv(OUTPUT_PATH, index=False)

    print("=" * 60)
    print("SENSOR FEATURE BUILD COMPLETE")
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
    print("Sample:")
    print(features.head(3).to_string(index=False))


if __name__ == "__main__":
    main()