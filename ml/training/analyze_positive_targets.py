from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
SPLIT_DIR = BASE_DIR / "data" / "processed" / "splits"


for split_name in ["train", "validation", "test"]:
    path = SPLIT_DIR / f"{split_name}.csv"
    df = pd.read_csv(path)

    positives = df[df["target"] == 1].copy()

    print()
    print("=" * 70)
    print(f"{split_name.upper()} POSITIVE TARGET ANALYSIS")
    print("=" * 70)

    print(f"Rows: {len(df):,}")
    print(f"Positive rows: {len(positives):,}")

    if positives.empty:
        continue

    positives["date"] = pd.to_datetime(positives["date"])

    print(
        f"Positive date range: "
        f"{positives['date'].min().date()} "
        f"-> "
        f"{positives['date'].max().date()}"
    )

    print()
    print("Positive rows by date:")

    print(
        positives.groupby("date")
        .size()
        .to_string()
    )
