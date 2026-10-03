from datetime import timedelta
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"

SENSOR_PATH = PROCESSED_DIR / "sensor_features.csv"
PRODUCTION_PATH = PROCESSED_DIR / "production_features.csv"
QUALITY_PATH = PROCESSED_DIR / "quality_features.csv"
MAINTENANCE_FEATURE_PATH = (
    PROCESSED_DIR / "maintenance_features.csv"
)
MAINTENANCE_RAW_PATH = (
    RAW_DIR / "maintenance_records.csv"
)

OUTPUT_PATH = PROCESSED_DIR / "ml_dataset.csv"


def load_feature_tables() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load all independently generated feature tables."""

    sensor = pd.read_csv(SENSOR_PATH)
    production = pd.read_csv(PRODUCTION_PATH)
    quality = pd.read_csv(
        QUALITY_PATH
    )
    maintenance_features = pd.read_csv(
        MAINTENANCE_FEATURE_PATH
    )

    return (
        sensor,
        production,
        quality,
        maintenance_features,
    )


def merge_features(
    sensor: pd.DataFrame,
    production: pd.DataFrame,
    quality: pd.DataFrame,
    maintenance_features: pd.DataFrame,
) -> pd.DataFrame:
    """Merge feature tables at the machine-day grain."""

    keys = ["machine_code", "date"]

    dataset = sensor.merge(
        production,
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    dataset = dataset.merge(
        quality,
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    dataset = dataset.merge(
        maintenance_features,
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    return dataset


def add_target(
    dataset: pd.DataFrame,
    maintenance: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the 7-day corrective-maintenance target.

    Target:
        1 = corrective maintenance scheduled within
            the next 7 days
        0 = no corrective maintenance within
            the next 7 days

    Maintenance records are used ONLY to create the target.
    They are not merged into the feature columns.
    """

    maintenance = maintenance.copy()

    maintenance["scheduled_date"] = pd.to_datetime(
        maintenance["scheduled_date"]
    ).dt.date

    corrective = maintenance[
        maintenance["maintenance_type"] == "CORRECTIVE"
    ].copy()

    corrective_events = {}

    for _, row in corrective.iterrows():
        key = row["machine_code"]

        if key not in corrective_events:
            corrective_events[key] = []

        corrective_events[key].append(
            row["scheduled_date"]
        )

    def calculate_target(row: pd.Series) -> int:
        machine = row["machine_code"]
        current_date = pd.to_datetime(
            row["date"]
        ).date()

        future_dates = corrective_events.get(
            machine,
            [],
        )

        for maintenance_date in future_dates:
            if (
                maintenance_date > current_date
                and maintenance_date
                <= current_date + timedelta(days=7)
            ):
                return 1

        return 0

    dataset["target"] = dataset.apply(
        calculate_target,
        axis=1,
    )

    return dataset


def validate_dataset(
    dataset: pd.DataFrame,
    source_tables: list[pd.DataFrame],
) -> None:
    """Validate grain, joins, target distribution, and feature integrity."""

    expected_rows = 9 * 273

    assert len(dataset) == expected_rows, (
        f"Expected {expected_rows} rows, "
        f"got {len(dataset)}"
    )

    assert dataset["machine_code"].nunique() == 9

    assert dataset["date"].nunique() == 273

    # Every source feature table must have exactly one
    # record per machine-day.
    for table in source_tables:
        duplicate_count = table.duplicated(
            subset=["machine_code", "date"]
        ).sum()

        assert duplicate_count == 0, (
            "Duplicate machine-day found in feature table."
        )

    # Target must be binary.
    assert set(
        dataset["target"].unique()
    ).issubset({0, 1})

    # Target must contain both positive and negative examples.
    positive_count = int(
        dataset["target"].sum()
    )

    negative_count = int(
        (dataset["target"] == 0).sum()
    )

    assert positive_count > 0, (
        "Target contains no positive examples."
    )

    assert negative_count > 0, (
        "Target contains no negative examples."
    )

    # Features must not contain missing values.
    feature_columns = [
        column
        for column in dataset.columns
        if column not in {
            "machine_code",
            "date",
            "target",
        }
    ]

    assert not dataset[
        feature_columns
    ].isna().any().any(), (
        "Feature dataset contains unexpected missing values."
    )

    # Check that target exists after target creation.
    assert "target" in dataset.columns


def main() -> None:
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        sensor,
        production,
        quality,
        maintenance_features,
    ) = load_feature_tables()

    dataset = merge_features(
        sensor,
        production,
        quality,
        maintenance_features,
    )

    maintenance = pd.read_csv(
        MAINTENANCE_RAW_PATH
    )

    dataset = add_target(
        dataset,
        maintenance,
    )

    validate_dataset(
        dataset,
        [
            sensor,
            production,
            quality,
            maintenance_features,
        ],
    )

    dataset.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print("FINAL ML DATASET BUILD COMPLETE")
    print("=" * 60)

    print(
        f"Rows:             {len(dataset):,}"
    )

    print(
        f"Columns:          {len(dataset.columns)}"
    )

    print(
        f"Machines:         "
        f"{dataset['machine_code'].nunique()}"
    )

    print(
        f"Machine-days:     "
        f"{dataset['date'].nunique()}"
    )

    print()
    print("Target distribution:")

    print(
        dataset["target"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("Target percentage:")

    print(
        dataset["target"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    print()
    print("Dataset columns:")

    for column in dataset.columns:
        print(
            f"  - {column}"
        )

    print()
    print("Sample:")

    print(
        dataset.head(3).to_string(
            index=False
        )
    )

    print()
    print(
        f"Output file: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()