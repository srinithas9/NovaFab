
from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")


def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


def profile_sensor_data() -> None:
    print("\n" + "=" * 60)
    print("SENSOR DATA PROFILE")
    print("=" * 60)

    df = load_csv("sensor_readings.csv")

    numeric_columns = [
        "temperature",
        "vibration",
        "pressure",
        "power_consumption",
    ]

    print(f"Rows: {len(df):,}")
    print(
        f"Unique machines: "
        f"{df['machine_code'].nunique()}"
    )

    print("\nReadings per machine:")

    readings_per_machine = (
        df.groupby("machine_code")
        .size()
        .sort_values()
    )

    print(readings_per_machine.to_string())

    print("\nSensor statistics:")

    print(
        df[numeric_columns]
        .describe()
        .round(2)
        .to_string()
    )

    print("\nMissing-value rates:")

    missing_rates = (
        df[numeric_columns]
        .isna()
        .mean()
        .sort_values(ascending=False)
        * 100
    )

    for column, rate in missing_rates.items():
        print(f"{column}: {rate:.2f}%")


def profile_production_data() -> None:
    print("\n" + "=" * 60)
    print("PRODUCTION DATA PROFILE")
    print("=" * 60)

    df = load_csv("production_runs.csv")

    df["efficiency"] = (
        df["produced_quantity"]
        / df["target_quantity"]
    )

    df["rejection_rate"] = (
        df["rejected_quantity"]
        / df["produced_quantity"]
    )

    print(f"Production runs: {len(df):,}")

    print("\nProduction statistics:")

    print(
        df[
            [
                "target_quantity",
                "produced_quantity",
                "rejected_quantity",
                "efficiency",
                "rejection_rate",
            ]
        ]
        .describe()
        .round(3)
        .to_string()
    )

    print("\nProduction by machine:")

    machine_summary = (
        df.groupby("machine_code")
        .agg(
            runs=("batch_number", "count"),
            avg_target=("target_quantity", "mean"),
            avg_produced=("produced_quantity", "mean"),
            avg_rejected=("rejected_quantity", "mean"),
            avg_efficiency=("efficiency", "mean"),
            avg_rejection_rate=("rejection_rate", "mean"),
        )
        .round(3)
    )

    print(machine_summary.to_string())


def profile_quality_data() -> None:
    print("\n" + "=" * 60)
    print("QUALITY DATA PROFILE")
    print("=" * 60)

    df = load_csv("quality_inspections.csv")

    print(f"Inspections: {len(df):,}")

    print("\nInspection results:")

    result_counts = (
        df["result"]
        .value_counts()
        .sort_index()
    )

    print(result_counts.to_string())

    print("\nInspection result percentages:")

    result_percentages = (
        df["result"]
        .value_counts(normalize=True)
        .sort_index()
        * 100
    )

    for result, percentage in result_percentages.items():
        print(
            f"{result}: "
            f"{percentage:.2f}%"
        )

    print("\nDefect-count statistics:")

    print(
        df["defect_count"]
        .describe()
        .round(2)
        .to_string()
    )


def profile_defect_data() -> None:
    print("\n" + "=" * 60)
    print("DEFECT DATA PROFILE")
    print("=" * 60)

    df = load_csv("defects.csv")

    print(f"Defect records: {len(df):,}")

    print("\nDefect types:")

    defect_types = (
        df["defect_type"]
        .value_counts()
        .sort_values(ascending=False)
    )

    print(defect_types.to_string())

    print("\nDefect severities:")

    severities = (
        df["severity"]
        .value_counts()
        .reindex(
            [
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            ],
            fill_value=0,
        )
    )

    print(severities.to_string())


def profile_maintenance_data() -> None:
    print("\n" + "=" * 60)
    print("MAINTENANCE DATA PROFILE")
    print("=" * 60)

    df = load_csv("maintenance_records.csv")

    print(f"Maintenance records: {len(df):,}")

    print("\nMaintenance types:")

    types = (
        df["maintenance_type"]
        .value_counts()
        .sort_index()
    )

    print(types.to_string())

    print("\nMaintenance statuses:")

    statuses = (
        df["status"]
        .value_counts()
        .sort_index()
    )

    print(statuses.to_string())

    print("\nMaintenance by machine:")

    machine_counts = (
        df["machine_code"]
        .value_counts()
        .sort_index()
    )

    print(machine_counts.to_string())


def profile_machine_coverage() -> None:
    print("\n" + "=" * 60)
    print("MACHINE COVERAGE")
    print("=" * 60)

    machines = load_csv("machines.csv")

    datasets = {
        "sensor_readings": load_csv(
            "sensor_readings.csv"
        ),
        "production_runs": load_csv(
            "production_runs.csv"
        ),
        "quality_inspections": load_csv(
            "quality_inspections.csv"
        ),
        "maintenance_records": load_csv(
            "maintenance_records.csv"
        ),
    }

    machine_codes = set(
        machines["machine_code"]
    )

    for dataset_name, df in datasets.items():

        covered_machines = set(
            df["machine_code"]
        )

        missing_machines = (
            machine_codes - covered_machines
        )

        print(
            f"{dataset_name}: "
            f"{len(covered_machines)}/"
            f"{len(machine_codes)} machines"
        )

        if missing_machines:
            print(
                f"  Missing: "
                f"{sorted(missing_machines)}"
            )


def profile_all() -> None:
    print("\n")
    print("#" * 60)
    print("# NovaFab Raw Data Profiling")
    print("#" * 60)

    profile_sensor_data()
    profile_production_data()
    profile_quality_data()
    profile_defect_data()
    profile_maintenance_data()
    profile_machine_coverage()

    print("\n" + "#" * 60)
    print("# PROFILE COMPLETE")
    print("#" * 60)


if __name__ == "__main__":
    profile_all()

