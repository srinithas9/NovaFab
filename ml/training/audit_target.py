from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

RAW_MAINTENANCE_PATH = (
    BASE_DIR / "data" / "raw" / "maintenance_records.csv"
)

ML_DATASET_PATH = (
    BASE_DIR / "data" / "processed" / "ml_dataset.csv"
)


def build_expected_target(
    dataset: pd.DataFrame,
    corrective: pd.DataFrame,
) -> pd.DataFrame:
    """
    Independently calculate the expected 7-day corrective-maintenance
    target from the current raw maintenance records.

    This is used for auditing the processed ML dataset.
    """

    expected = dataset[
        ["machine_code", "date"]
    ].copy()

    expected["expected_target"] = 0

    corrective_events = {}

    for _, event in corrective.iterrows():
        machine = event["machine_code"]
        event_date = event["scheduled_date"].date()

        corrective_events.setdefault(
            machine,
            [],
        ).append(event_date)

    for index, row in expected.iterrows():
        machine = row["machine_code"]
        current_date = row["date"].date()

        future_dates = corrective_events.get(
            machine,
            [],
        )

        for event_date in future_dates:
            if (
                event_date > current_date
                and event_date
                <= current_date + pd.Timedelta(days=7)
            ):
                expected.at[index, "expected_target"] = 1
                break

    return expected


def main():
    maintenance = pd.read_csv(
        RAW_MAINTENANCE_PATH
    )

    dataset = pd.read_csv(
        ML_DATASET_PATH
    )

    maintenance["scheduled_date"] = pd.to_datetime(
        maintenance["scheduled_date"]
    )

    maintenance["completed_date"] = pd.to_datetime(
        maintenance["completed_date"]
    )

    dataset["date"] = pd.to_datetime(
        dataset["date"]
    )

    corrective = maintenance[
        maintenance["maintenance_type"] == "CORRECTIVE"
    ].copy()

    print("=" * 70)
    print("PREDICTIVE MAINTENANCE TARGET AUDIT")
    print("=" * 70)

    print()
    print(f"Total maintenance records: {len(maintenance):,}")
    print(f"Corrective records:        {len(corrective):,}")

    print()
    print("=" * 70)
    print("CORRECTIVE EVENTS BY MACHINE")
    print("=" * 70)
    print()

    machine_counts = (
        corrective["machine_code"]
        .value_counts()
        .sort_index()
    )

    print(
        machine_counts.to_string()
    )

    print()
    print("=" * 70)
    print("CORRECTIVE EVENT DATES")
    print("=" * 70)
    print()

    print(
        corrective[
            [
                "machine_code",
                "scheduled_date",
                "completed_date",
                "maintenance_type",
                "status",
            ]
        ]
        .sort_values(
            ["scheduled_date", "machine_code"]
        )
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Independently calculate expected targets
    # --------------------------------------------------------

    expected = build_expected_target(
        dataset,
        corrective,
    )

    dataset["expected_target"] = (
        expected["expected_target"].values
    )

    # --------------------------------------------------------
    # Compare processed target with independently calculated
    # target.
    # --------------------------------------------------------

    mismatches = (
        dataset["target"]
        != dataset["expected_target"]
    )

    mismatch_count = int(
        mismatches.sum()
    )

    print()
    print("=" * 70)
    print("TARGET CONSISTENCY CHECK")
    print("=" * 70)
    print()

    print(
        f"Processed positive targets: "
        f"{dataset['target'].sum():,}"
    )

    print(
        f"Expected positive targets:  "
        f"{dataset['expected_target'].sum():,}"
    )

    print(
        f"Target mismatches:           "
        f"{mismatch_count:,}"
    )

    if mismatch_count == 0:
        print()
        print("PASS: Processed target matches raw maintenance events.")
    else:
        print()
        print(
            "WARNING: Processed target does not match "
            "the current raw maintenance data."
        )

    # --------------------------------------------------------
    # Expected target distribution
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EXPECTED TARGET DISTRIBUTION")
    print("=" * 70)
    print()

    print(
        dataset["expected_target"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()

    positive_count = int(
        dataset["expected_target"].sum()
    )

    total_count = len(dataset)

    print(
        f"Positive machine-days: "
        f"{positive_count:,}"
    )

    print(
        f"Positive rate: "
        f"{positive_count / total_count:.4%}"
    )

    # --------------------------------------------------------
    # Positive targets by machine
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EXPECTED POSITIVE TARGETS BY MACHINE")
    print("=" * 70)
    print()

    positive_by_machine = (
        dataset[
            dataset["expected_target"] == 1
        ]["machine_code"]
        .value_counts()
        .sort_index()
    )

    if len(positive_by_machine) > 0:
        print(
            positive_by_machine.to_string()
        )
    else:
        print("No positive target examples found.")

    # --------------------------------------------------------
    # Positive targets by month
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EXPECTED POSITIVE TARGETS BY MONTH")
    print("=" * 70)
    print()

    positive_by_month = (
        dataset[
            dataset["expected_target"] == 1
        ]
        .assign(
            month=lambda df:
            df["date"].dt.to_period("M")
        )
        .groupby("month")
        .size()
    )

    if len(positive_by_month) > 0:
        print(
            positive_by_month.to_string()
        )
    else:
        print("No positive target examples found.")

    # --------------------------------------------------------
    # Targets generated by each corrective event
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TARGETS PER CORRECTIVE EVENT")
    print("=" * 70)
    print()

    for _, event in corrective.sort_values(
        ["machine_code", "scheduled_date"]
    ).iterrows():

        machine = event["machine_code"]
        event_date = event["scheduled_date"]

        start_date = (
            event_date
            - pd.Timedelta(days=7)
        )

        end_date = (
            event_date
            - pd.Timedelta(days=1)
        )

        matching_days = dataset[
            (dataset["machine_code"] == machine)
            & (dataset["date"] >= start_date)
            & (dataset["date"] <= end_date)
            & (dataset["expected_target"] == 1)
        ]

        print(
            f"{machine} | "
            f"corrective event: "
            f"{event_date.date()} | "
            f"positive days: "
            f"{len(matching_days)}"
        )


if __name__ == "__main__":
    main()