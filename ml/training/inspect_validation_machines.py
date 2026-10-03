from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "ml_dataset.csv"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

validation_start = pd.Timestamp("2026-07-01")
validation_end = pd.Timestamp("2026-08-31")

validation = df[
    (df["date"] >= validation_start)
    & (df["date"] <= validation_end)
].copy()

positive = validation[validation["target"] == 1]

print("=" * 80)
print("VALIDATION POSITIVES BY MACHINE")
print("=" * 80)

print()
print(
    positive[
        [
            "machine_code",
            "date",
            "target",
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
            "days_since_last_maintenance",
            "previous_corrective_count",
        ]
    ]
    .sort_values(["machine_code", "date"])
    .to_string(index=False)
)

print()
print("=" * 80)
print("VALIDATION TARGET COUNTS BY MACHINE")
print("=" * 80)

print(
    validation.groupby("machine_code")["target"]
    .agg(
        rows="count",
        positives="sum",
        positive_rate="mean",
    )
    .sort_values("positives", ascending=False)
    .round(4)
    .to_string()
)

print()
print("=" * 80)
print("MACHINE-LEVEL SENSOR BASELINES")
print("=" * 80)

machine_summary = validation.groupby("machine_code").agg(
    temperature_mean=("temperature_mean", "mean"),
    vibration_mean=("vibration_mean", "mean"),
    pressure_mean=("pressure_mean", "mean"),
    power_mean=("power_consumption_mean", "mean"),
)

print(machine_summary.round(2).to_string())
