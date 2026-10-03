from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml_features_v1.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "splits"
)

TRAIN_OUTPUT = OUTPUT_DIR / "train.csv"
VALIDATION_OUTPUT = OUTPUT_DIR / "validation.csv"
TEST_OUTPUT = OUTPUT_DIR / "test.csv"


DATE_COLUMN = "date"

# Date is intentionally removed from the model features,
# so recover it from the original ML dataset for splitting.
ORIGINAL_DATASET = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml_dataset.csv"
)


# ------------------------------------------------------------
# Chronological split configuration
# ------------------------------------------------------------
#
# The target represents whether corrective maintenance
# occurs within the following 7 days.
#
# Positive target examples begin on 2026-06-24.
#
# Therefore, the training period must extend beyond
# 2026-06-24 so that the model has positive examples
# to learn from.
#
# We maintain a 7-day gap between each split to reduce
# temporal dependence between training and evaluation.
#
# TRAIN:
#     2026-01-01 -> 2026-07-14
#
# GAP:
#     2026-07-15 -> 2026-07-21
#
# VALIDATION:
#     2026-07-22 -> 2026-08-14
#
# GAP:
#     2026-08-15 -> 2026-08-21
#
# TEST:
#     2026-08-22 -> 2026-09-23
#
# The remaining dates after 2026-09-23 are not used for
# evaluation because the simulation ends on 2026-09-30 and
# the selected test period already contains sufficient
# positive examples.
#
# Expected distribution:
#
# TRAIN:
#     1,755 rows
#     21 positive
#
# VALIDATION:
#     216 rows
#     7 positive
#
# TEST:
#     297 rows
#     28 positive
# ------------------------------------------------------------

TRAIN_START = pd.Timestamp("2026-01-01")
TRAIN_END = pd.Timestamp("2026-07-14")

VALIDATION_START = pd.Timestamp("2026-07-22")
VALIDATION_END = pd.Timestamp("2026-08-14")

TEST_START = pd.Timestamp("2026-08-22")
TEST_END = pd.Timestamp("2026-09-23")


def load_data() -> pd.DataFrame:
    """Load selected features and restore date for splitting."""

    features = pd.read_csv(INPUT_PATH)

    original = pd.read_csv(
        ORIGINAL_DATASET,
        usecols=["machine_code", "date"],
    )

    # Feature selection preserves row order.
    assert len(features) == len(original), (
        "Feature dataset and original dataset "
        "have different row counts."
    )

    features["date"] = pd.to_datetime(
        original["date"]
    )

    return features


def create_splits(
    df: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Create chronological train, validation, and test splits."""

    train = df[
        (df["date"] >= TRAIN_START)
        & (df["date"] <= TRAIN_END)
    ].copy()

    validation = df[
        (df["date"] >= VALIDATION_START)
        & (df["date"] <= VALIDATION_END)
    ].copy()

    test = df[
        (df["date"] >= TEST_START)
        & (df["date"] <= TEST_END)
    ].copy()

    return (
        train,
        validation,
        test,
    )


def validate_split(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> None:
    """Validate chronological boundaries and target integrity."""

    assert len(train) > 0
    assert len(validation) > 0
    assert len(test) > 0

    # Chronological ordering.
    assert train["date"].max() < validation["date"].min()
    assert validation["date"].max() < test["date"].min()

    # Exact expected boundaries.
    assert train["date"].min() == TRAIN_START
    assert train["date"].max() == TRAIN_END

    assert (
        validation["date"].min()
        == VALIDATION_START
    )

    assert (
        validation["date"].max()
        == VALIDATION_END
    )

    assert (
        test["date"].min()
        == TEST_START
    )

    assert (
        test["date"].max()
        == TEST_END
    )

    # No overlapping rows.
    assert set(train.index).isdisjoint(
        validation.index
    )

    assert set(train.index).isdisjoint(
        test.index
    )

    assert set(validation.index).isdisjoint(
        test.index
    )

    # Target must remain binary.
    assert train["target"].isin(
        [0, 1]
    ).all()

    assert validation["target"].isin(
        [0, 1]
    ).all()

    assert test["target"].isin(
        [0, 1]
    ).all()

    # Training must contain positive examples.
    # A supervised classifier cannot learn the positive
    # class if the training set contains only class 0.
    assert train["target"].sum() > 0, (
        "Training split contains no positive examples."
    )

    # Evaluation splits must also contain positive examples.
    assert validation["target"].sum() > 0, (
        "Validation split contains no positive examples."
    )

    assert test["target"].sum() > 0, (
        "Test split contains no positive examples."
    )


def print_summary(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> None:
    """Print split sizes, date ranges, and target distributions."""

    print("=" * 70)
    print("TIME-BASED ML SPLIT")
    print("=" * 70)

    for name, dataset in [
        ("TRAIN", train),
        ("VALIDATION", validation),
        ("TEST", test),
    ]:
        print()
        print(name)
        print("-" * 70)

        print(
            f"Rows:       {len(dataset):,}"
        )

        print(
            f"Date range: "
            f"{dataset['date'].min().date()} "
            f"-> "
            f"{dataset['date'].max().date()}"
        )

        print("Target distribution:")

        print(
            dataset["target"]
            .value_counts()
            .sort_index()
            .to_string()
        )

        print(
            f"Positive rate: "
            f"{dataset['target'].mean() * 100:.2f}%"
        )

    print()
    print("=" * 70)
    print("TIME GAPS")
    print("=" * 70)

    train_validation_gap = (
        VALIDATION_START - TRAIN_END
    ).days - 1

    validation_test_gap = (
        TEST_START - VALIDATION_END
    ).days - 1

    print(
        f"Train -> Validation gap: "
        f"{train_validation_gap} days"
    )

    print(
        f"Validation -> Test gap: "
        f"{validation_test_gap} days"
    )


def main() -> None:
    """Build and save chronological ML splits."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    train, validation, test = create_splits(
        df
    )

    validate_split(
        train,
        validation,
        test,
    )

    # Date is used only to construct the chronological
    # split. It is not provided to the model.
    train.to_csv(
        TRAIN_OUTPUT,
        index=False,
    )

    validation.to_csv(
        VALIDATION_OUTPUT,
        index=False,
    )

    test.to_csv(
        TEST_OUTPUT,
        index=False,
    )

    print_summary(
        train,
        validation,
        test,
    )

    print()
    print("Saved:")
    print(f"  - {TRAIN_OUTPUT}")
    print(f"  - {VALIDATION_OUTPUT}")
    print(f"  - {TEST_OUTPUT}")


if __name__ == "__main__":
    main()