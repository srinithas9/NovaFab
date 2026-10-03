from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "ml_dataset.csv"
MAINTENANCE_PATH = BASE_DIR / "data" / "raw" / "maintenance_records.csv"


df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

maintenance = pd.read_csv(MAINTENANCE_PATH)
maintenance["scheduled_date"] = pd.to_datetime(
    maintenance["scheduled_date"]
)

corrective = maintenance[
    maintenance["maintenance_type"] == "CORRECTIVE"
].copy()

# Features we expect to change as a machine degrades.
features = [
    "temperature_mean",
    "temperature_max",
    "vibration_mean",
    "vibration_max",
    "pressure_mean",
    "pressure_max",
    "power_consumption_mean",
    "power_consumption_max",
    "production_efficiency",
    "rejection_rate",
    "average_defects",
    "failure_rate",
    "days_since_last_maintenance",
]

print("=" * 90)
print("PRE-CORRECTIVE-MAINTENANCE DEGRADATION ANALYSIS")
print("=" * 90)

for _, event in corrective.iterrows():

    machine = event["machine_code"]
    event_date = event["scheduled_date"]

    machine_data = df[
        (df["machine_code"] == machine)
        & (df["date"] >= event_date - pd.Timedelta(days=7))
        & (df["date"] < event_date)
    ].copy()

    if machine_data.empty:
        continue

    machine_data["days_before_event"] = (
        event_date - machine_data["date"]
    ).dt.days

    print()
    print("-" * 90)
    print(
        f"{machine} | corrective maintenance scheduled: "
        f"{event_date.date()}"
    )
    print("-" * 90)

    print(
        machine_data[
            ["date", "days_before_event"] + features
        ]
        .sort_values("date")
        .round(3)
        .to_string(index=False)
    )

print()
print("=" * 90)
print("AVERAGE FEATURE VALUES BY DAYS BEFORE CORRECTIVE EVENT")
print("=" * 90)

event_rows = []

for _, event in corrective.iterrows():

    machine = event["machine_code"]
    event_date = event["scheduled_date"]

    machine_data = df[
        (df["machine_code"] == machine)
        & (df["date"] >= event_date - pd.Timedelta(days=7))
        & (df["date"] < event_date)
    ].copy()

    if machine_data.empty:
        continue

    machine_data["days_before_event"] = (
        event_date - machine_data["date"]
    ).dt.days

    event_rows.append(machine_data)

event_window = pd.concat(event_rows, ignore_index=True)

summary = (
    event_window
    .groupby("days_before_event")[features]
    .mean()
    .sort_index()
)

print(summary.round(3).to_string())

print()
print("=" * 90)
print("NUMBER OF OBSERVATIONS")
print("=" * 90)

print(
    event_window["days_before_event"]
    .value_counts()
    .sort_index()
    .to_string()
)
