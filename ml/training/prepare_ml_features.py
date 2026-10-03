from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data" / "processed" / "ml_dataset.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "ml_features_v1.csv"


TARGET_COLUMN = "target"


REMOVED_COLUMNS = {
    # Identifiers / temporal fields
    "machine_code",
    "date",

    # Constant features in the current dataset
    "production_runs",
    "inspection_count",

    # Redundant quality representations
    "failed_inspections",
    "review_inspections",
    "total_defects",
}


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(INPUT_PATH)


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_keep = [
        column
        for column in df.columns
        if column not in REMOVED_COLUMNS
        and column != TARGET_COLUMN
    ]

    features = df[columns_to_keep].copy()

    features[TARGET_COLUMN] = df[TARGET_COLUMN]

    return features


def validate_features(
    original: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:

    expected_removed = REMOVED_COLUMNS

    actual_removed = set(original.columns) - set(selected.columns)

    assert actual_removed == expected_removed, (
        "Feature removal mismatch.\n"
        f"Expected: {sorted(expected_removed)}\n"
        f"Actual:   {sorted(actual_removed)}"
    )

    assert TARGET_COLUMN in selected.columns

    assert len(original) == len(selected)

    assert selected[TARGET_COLUMN].isin([0, 1]).all()

    feature_columns = [
        column
        for column in selected.columns
        if column != TARGET_COLUMN
    ]

    assert not selected[feature_columns].isna().any().any()

    constant_features = [
        column
        for column in feature_columns
        if selected[column].nunique() <= 1
    ]

    assert not constant_features, (
        f"Constant features remain: {constant_features}"
    )


def print_summary(
    original: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:

    original_features = [
        column
        for column in original.columns
        if column != TARGET_COLUMN
    ]

    selected_features = [
        column
        for column in selected.columns
        if column != TARGET_COLUMN
    ]

    print("=" * 70)
    print("ML FEATURE SELECTION")
    print("=" * 70)

    print()
    print(f"Original feature count: {len(original_features)}")
    print(f"Selected feature count: {len(selected_features)}")

    print()
    print("Removed features:")
    for column in sorted(REMOVED_COLUMNS):
        print(f"  - {column}")

    print()
    print("Selected features:")

    for index, column in enumerate(selected_features, start=1):
        print(f"  {index:02d}. {column}")

    print()
    print("Dataset shape:")
    print(f"  Rows:    {len(selected):,}")
    print(f"  Columns: {len(selected.columns)}")

    print()
    print("Target distribution:")
    print(
        selected[TARGET_COLUMN]
        .value_counts()
        .sort_index()
        .to_string()
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = load_dataset()

    selected = select_features(original)

    validate_features(
        original,
        selected,
    )

    selected.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print_summary(
        original,
        selected,
    )

    print()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()