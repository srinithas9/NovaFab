from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "raw" / "maintenance_records.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "maintenance_features.csv"


def load_maintenance_data() -> pd.DataFrame:
    """Load maintenance records and normalize dates."""

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["scheduled_date", "completed_date"],
    )

    df["scheduled_date"] = df["scheduled_date"].dt.date

    return df


def build_maintenance_features(
    maintenance: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build historical maintenance features for every machine-day.

    Only maintenance events that occurred before the prediction date
    are allowed to contribute to the features.

    This prevents future-information leakage.
    """

    machines = sorted(maintenance["machine_code"].unique())

    dates = pd.date_range(
        start="2026-01-01",
        end="2026-09-30",
        freq="D",
    ).date

    rows = []

    for machine_code in machines:
        machine_maintenance = maintenance[
            maintenance["machine_code"] == machine_code
        ].copy()

        for current_date in dates:

            # Only completed maintenance before the prediction date
            historical = machine_maintenance[
                (
                    machine_maintenance["completed_date"].notna()
                )
                & (
                    machine_maintenance["completed_date"].dt.date
                    < current_date
                )
            ]

            if historical.empty:
                rows.append(
                    {
                        "machine_code": machine_code,
                        "date": current_date,
                        "days_since_last_maintenance": -1,
                        "previous_maintenance_count": 0,
                        "previous_corrective_count": 0,
                        "previous_preventive_count": 0,
                        "previous_inspection_count": 0,
                    }
                )
                continue

            last_maintenance_date = (
                historical["completed_date"]
                .max()
                .date()
            )

            days_since_last = (
                current_date - last_maintenance_date
            ).days

            rows.append(
                {
                    "machine_code": machine_code,
                    "date": current_date,
                    "days_since_last_maintenance": days_since_last,
                    "previous_maintenance_count": len(historical),
                    "previous_corrective_count": (
                        historical["maintenance_type"]
                        .eq("CORRECTIVE")
                        .sum()
                    ),
                    "previous_preventive_count": (
                        historical["maintenance_type"]
                        .eq("PREVENTIVE")
                        .sum()
                    ),
                    "previous_inspection_count": (
                        historical["maintenance_type"]
                        .eq("INSPECTION")
                        .sum()
                    ),
                }
            )

    return pd.DataFrame(rows)


def validate_features(features: pd.DataFrame) -> None:
    """Run structural and leakage-related checks."""

    expected_rows = 9 * 273

    assert len(features) == expected_rows, (
        f"Expected {expected_rows} machine-days, "
        f"got {len(features)}"
    )

    assert features["machine_code"].nunique() == 9
    assert features["date"].nunique() == 273

    numeric_columns = [
        "days_since_last_maintenance",
        "previous_maintenance_count",
        "previous_corrective_count",
        "previous_preventive_count",
        "previous_inspection_count",
    ]

    assert not features[numeric_columns].isna().any().any()

    assert (
        features["previous_maintenance_count"] >= 0
    ).all()

    assert (
        features["previous_corrective_count"] >= 0
    ).all()

    assert (
        features["previous_preventive_count"] >= 0
    ).all()

    assert (
        features["previous_inspection_count"] >= 0
    ).all()

    assert (
        features["previous_corrective_count"]
        <= features["previous_maintenance_count"]
    ).all()

    assert (
        features["previous_preventive_count"]
        <= features["previous_maintenance_count"]
    ).all()

    assert (
        features["previous_inspection_count"]
        <= features["previous_maintenance_count"]
    ).all()


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    maintenance = load_maintenance_data()

    features = build_maintenance_features(
        maintenance
    )

    validate_features(features)

    features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print("MAINTENANCE FEATURE BUILD COMPLETE")
    print("=" * 60)
    print(f"Input rows:       {len(maintenance):,}")
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
                "days_since_last_maintenance",
                "previous_maintenance_count",
                "previous_corrective_count",
                "previous_preventive_count",
                "previous_inspection_count",
            ]
        ]
        .describe()
        .round(2)
        .to_string()
    )

    print()
    print("First machine-day:")
    print(
        features.head(1).to_string(index=False)
    )

    print()
    print("Latest machine-days:")
    print(
        features.tail(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()