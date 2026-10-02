
from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")

EXPECTED_MACHINES = 9
EXPECTED_DAYS = 273
EXPECTED_READINGS_PER_SHIFT = 32

EXPECTED_SENSOR_ROWS = (
    EXPECTED_MACHINES
    * EXPECTED_DAYS
    * EXPECTED_READINGS_PER_SHIFT
)


def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {path}"
        )

    return pd.read_csv(path)


def validate_sensor_data() -> None:
    print("\n--- SENSOR DATA VALIDATION ---")

    df = load_csv("sensor_readings.csv")

    expected_columns = {
        "machine_code",
        "timestamp",
        "temperature",
        "vibration",
        "pressure",
        "power_consumption",
    }

    assert expected_columns.issubset(df.columns)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    print(f"Rows: {len(df):,}")
    print(f"Expected rows: {EXPECTED_SENSOR_ROWS:,}")

    assert len(df) == EXPECTED_SENSOR_ROWS

    machine_count = df["machine_code"].nunique()

    print(f"Machines: {machine_count}")
    print(f"Expected machines: {EXPECTED_MACHINES}")

    assert machine_count == EXPECTED_MACHINES

    duplicate_count = df.duplicated(
        subset=["machine_code", "timestamp"]
    ).sum()

    print(
        f"Duplicate machine/timestamp rows: "
        f"{duplicate_count}"
    )

    assert duplicate_count == 0

    for machine_code, machine_df in df.groupby(
        "machine_code"
    ):
        machine_df = machine_df.sort_values("timestamp")

        intervals = (
            machine_df["timestamp"]
            .diff()
            .dropna()
            .dt.total_seconds()
            / 60
        )

        valid_intervals = intervals[
            intervals <= 60
        ]

        invalid_intervals = valid_intervals[
            valid_intervals != 15
        ]

        assert len(invalid_intervals) == 0, (
            f"{machine_code} contains invalid "
            f"intra-shift intervals."
        )

    print("15-minute intra-shift intervals: PASS")

    hours = df["timestamp"].dt.hour
    minutes = df["timestamp"].dt.minute

    valid_time = (
        (hours >= 8)
        & (hours < 16)
        & minutes.isin([0, 15, 30, 45])
    )

    invalid_times = (~valid_time).sum()

    print(f"Invalid shift timestamps: {invalid_times}")

    assert invalid_times == 0

    numeric_columns = [
        "temperature",
        "vibration",
        "pressure",
        "power_consumption",
    ]

    for column in numeric_columns:
        negative_count = (
            df[column].dropna() < 0
        ).sum()

        print(
            f"{column} negative values: "
            f"{negative_count}"
        )

        assert negative_count == 0

    print("\nMissing-value rates:")

    for column in numeric_columns:
        missing_rate = df[column].isna().mean()

        print(
            f"{column}: "
            f"{missing_rate:.2%}"
        )


def validate_production_data() -> None:
    print("\n--- PRODUCTION DATA VALIDATION ---")

    df = load_csv("production_runs.csv")

    expected_rows = (
        EXPECTED_MACHINES * EXPECTED_DAYS
    )

    print(f"Rows: {len(df):,}")
    print(f"Expected rows: {expected_rows:,}")

    assert len(df) == expected_rows

    assert (df["target_quantity"] > 0).all()
    assert (df["produced_quantity"] >= 0).all()
    assert (df["rejected_quantity"] >= 0).all()

    assert (
        df["rejected_quantity"]
        <= df["produced_quantity"]
    ).all()

    print("Production quantity rules: PASS")


def validate_quality_data() -> None:
    print("\n--- QUALITY DATA VALIDATION ---")

    df = load_csv("quality_inspections.csv")

    expected_rows = (
        EXPECTED_MACHINES * EXPECTED_DAYS
    )

    print(f"Rows: {len(df):,}")
    print(f"Expected rows: {expected_rows:,}")

    assert len(df) == expected_rows

    valid_results = {
        "PASS",
        "REVIEW",
        "FAIL",
    }

    invalid_results = (
        set(df["result"]) - valid_results
    )

    print(
        f"Invalid inspection results: "
        f"{len(invalid_results)}"
    )

    assert not invalid_results

    assert (df["defect_count"] >= 0).all()

    print("Quality rules: PASS")


def validate_maintenance_data() -> None:
    print("\n--- MAINTENANCE DATA VALIDATION ---")

    df = load_csv("maintenance_records.csv")

    valid_types = {
        "PREVENTIVE",
        "CORRECTIVE",
        "INSPECTION",
    }

    invalid_types = (
        set(df["maintenance_type"])
        - valid_types
    )

    print(
        f"Invalid maintenance types: "
        f"{len(invalid_types)}"
    )

    assert not invalid_types

    valid_statuses = {
        "SCHEDULED",
        "IN_PROGRESS",
        "COMPLETED",
    }

    invalid_statuses = (
        set(df["status"])
        - valid_statuses
    )

    print(
        f"Invalid maintenance statuses: "
        f"{len(invalid_statuses)}"
    )

    assert not invalid_statuses

    print(f"Maintenance records: {len(df):,}")
    print("Maintenance rules: PASS")


def validate_defect_data() -> None:
    print("\n--- DEFECT DATA VALIDATION ---")

    df = load_csv("defects.csv")

    valid_severities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    invalid_severities = (
        set(df["severity"])
        - valid_severities
    )

    print(
        f"Invalid defect severities: "
        f"{len(invalid_severities)}"
    )

    assert not invalid_severities

    print(f"Defect records: {len(df):,}")
    print("Defect rules: PASS")


def validate_cross_dataset_integrity() -> None:
    """
    Validate relationships between raw datasets.

    These checks simulate the foreign-key relationships
    that will exist later in PostgreSQL.
    """

    print("\n--- CROSS-DATASET INTEGRITY ---")

    factories = load_csv("factories.csv")
    machines = load_csv("machines.csv")
    sensors = load_csv("sensor_readings.csv")
    production = load_csv("production_runs.csv")
    quality = load_csv("quality_inspections.csv")
    defects = load_csv("defects.csv")
    maintenance = load_csv(
        "maintenance_records.csv"
    )

    # ---------------------------------------------------------
    # Factory -> Machine
    # ---------------------------------------------------------

    factory_codes = set(
        factories["factory_code"]
    )

    orphan_machines = set(
        machines["factory_code"]
    ) - factory_codes

    print(
        f"Orphan machine factory references: "
        f"{len(orphan_machines)}"
    )

    assert not orphan_machines

    # ---------------------------------------------------------
    # Machine -> Sensor
    # ---------------------------------------------------------

    machine_codes = set(
        machines["machine_code"]
    )

    orphan_sensor_machines = set(
        sensors["machine_code"]
    ) - machine_codes

    print(
        f"Orphan sensor machine references: "
        f"{len(orphan_sensor_machines)}"
    )

    assert not orphan_sensor_machines

    # ---------------------------------------------------------
    # Machine -> Production
    # ---------------------------------------------------------

    orphan_production_machines = set(
        production["machine_code"]
    ) - machine_codes

    print(
        f"Orphan production machine references: "
        f"{len(orphan_production_machines)}"
    )

    assert not orphan_production_machines

    # ---------------------------------------------------------
    # Machine -> Maintenance
    # ---------------------------------------------------------

    orphan_maintenance_machines = set(
        maintenance["machine_code"]
    ) - machine_codes

    print(
        f"Orphan maintenance machine references: "
        f"{len(orphan_maintenance_machines)}"
    )

    assert not orphan_maintenance_machines

    # ---------------------------------------------------------
    # Production -> Quality
    # ---------------------------------------------------------

    production_batches = set(
        production["batch_number"]
    )

    quality_batches = set(
        quality["batch_number"]
    )

    orphan_quality_batches = (
        quality_batches - production_batches
    )

    print(
        f"Orphan quality batch references: "
        f"{len(orphan_quality_batches)}"
    )

    assert not orphan_quality_batches

    # ---------------------------------------------------------
    # Quality -> Defect
    #
    # Defects are linked to inspections through the
    # batch_number in the raw CSV representation.
    # ---------------------------------------------------------

    defect_batches = set(
        defects["batch_number"]
    )

    orphan_defect_batches = (
        defect_batches - quality_batches
    )

    print(
        f"Orphan defect batch references: "
        f"{len(orphan_defect_batches)}"
    )

    assert not orphan_defect_batches

    # ---------------------------------------------------------
    # Every production batch should have one inspection
    # ---------------------------------------------------------

    quality_batch_counts = (
        quality["batch_number"]
        .value_counts()
    )

    duplicate_quality_batches = (
        quality_batch_counts[
            quality_batch_counts > 1
        ]
    )

    print(
        f"Duplicate quality inspections per batch: "
        f"{len(duplicate_quality_batches)}"
    )

    assert len(duplicate_quality_batches) == 0

    # ---------------------------------------------------------
    # Every production batch should have one machine
    # ---------------------------------------------------------

    production_batch_counts = (
        production.groupby("batch_number")[
            "machine_code"
        ]
        .nunique()
    )

    ambiguous_batches = (
        production_batch_counts[
            production_batch_counts > 1
        ]
    )

    print(
        f"Batches linked to multiple machines: "
        f"{len(ambiguous_batches)}"
    )

    assert len(ambiguous_batches) == 0

    print(
        "Cross-dataset relationship checks: PASS"
    )


def validate_all() -> None:
    print("=" * 60)
    print("NovaFab Raw Data Validation")
    print("=" * 60)

    validate_sensor_data()
    validate_production_data()
    validate_quality_data()
    validate_maintenance_data()
    validate_defect_data()
    validate_cross_dataset_integrity()

    print("\n" + "=" * 60)
    print("ALL RAW DATA VALIDATION CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    validate_all()

