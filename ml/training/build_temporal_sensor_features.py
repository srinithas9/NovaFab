
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sensor_features.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "temporal_sensor_features.csv"
)


KEY_COLUMNS = [
    "machine_code",
    "date",
]


SENSOR_COLUMNS = [
    "temperature",
    "vibration",
    "pressure",
    "power_consumption",
]


def load_sensor_features() -> pd.DataFrame:
    """Load daily machine-level sensor features."""

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
    )

    return df


def build_temporal_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build historical sensor features for each machine-day.

    All temporal features are calculated separately for each
    machine.

    Features for each sensor:
        - previous-day value
        - one-day change
        - previous 3-day rolling mean
        - previous 7-day rolling mean
        - previous 7-day rolling standard deviation

    The current day's observation is excluded from all
    rolling-window calculations.
    """

    df = (
        df.sort_values(
            ["machine_code", "date"]
        )
        .reset_index(drop=True)
        .copy()
    )

    grouped = df.groupby(
        "machine_code",
        sort=False,
    )

    temporal_features = df[
        KEY_COLUMNS
    ].copy()

    for sensor in SENSOR_COLUMNS:

        current_values = df[
            f"{sensor}_mean"
        ]

        lag_1 = grouped[
            f"{sensor}_mean"
        ].shift(1)

        temporal_features[
            f"{sensor}_mean_lag_1"
        ] = lag_1

        # Current day minus previous day.
        #
        # Positive = sensor increased.
        # Negative = sensor decreased.
        temporal_features[
            f"{sensor}_mean_change_1d"
        ] = (
            current_values
            - lag_1
        )

        # Previous 3-day rolling mean.
        #
        # shift(1) ensures today's observation
        # is not included.
        rolling_mean_3d = (
            grouped[
                f"{sensor}_mean"
            ]
            .shift(1)
            .groupby(
                df["machine_code"],
                sort=False,
            )
            .rolling(
                window=3,
                min_periods=3,
            )
            .mean()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        temporal_features[
            f"{sensor}_mean_rolling_mean_3d"
        ] = rolling_mean_3d.to_numpy()

        # Previous 7-day rolling mean.
        rolling_mean_7d = (
            grouped[
                f"{sensor}_mean"
            ]
            .shift(1)
            .groupby(
                df["machine_code"],
                sort=False,
            )
            .rolling(
                window=7,
                min_periods=7,
            )
            .mean()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        temporal_features[
            f"{sensor}_mean_rolling_mean_7d"
        ] = rolling_mean_7d.to_numpy()

        # Previous 7-day rolling standard deviation.
        rolling_std_7d = (
            grouped[
                f"{sensor}_mean"
            ]
            .shift(1)
            .groupby(
                df["machine_code"],
                sort=False,
            )
            .rolling(
                window=7,
                min_periods=7,
            )
            .std()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        temporal_features[
            f"{sensor}_mean_rolling_std_7d"
        ] = rolling_std_7d.to_numpy()

    return temporal_features


def validate_features(
    original: pd.DataFrame,
    features: pd.DataFrame,
) -> None:
    """Validate structure and temporal feature integrity."""

    expected_rows = 9 * 273

    assert len(features) == expected_rows, (
        f"Expected {expected_rows} rows, "
        f"got {len(features)}"
    )

    assert (
        features["machine_code"].nunique()
        == 9
    )

    assert (
        features["date"].nunique()
        == 273
    )

    assert (
        features[
            KEY_COLUMNS
        ].duplicated().sum()
        == 0
    )

    expected_feature_count = (
        len(SENSOR_COLUMNS) * 5
    )

    feature_columns = [
        column
        for column in features.columns
        if column not in KEY_COLUMNS
    ]

    assert len(feature_columns) == (
        expected_feature_count
    )

    # ---------------------------------------------------------
    # Validate temporal history availability.
    # ---------------------------------------------------------

    for _, group in features.groupby(
        "machine_code"
    ):
        group = group.sort_values(
            "date"
        )

        # First day has no previous-day observation.
        assert (
            group[
                "temperature_mean_lag_1"
            ]
            .head(1)
            .isna()
            .all()
        )

        # Every subsequent day has a previous-day value.
        assert (
            group[
                "temperature_mean_lag_1"
            ]
            .iloc[1:]
            .notna()
            .all()
        )

        # First three days do not have three previous
        # observations.
        rolling_3d_columns = [
            column
            for column in feature_columns
            if "rolling_mean_3d" in column
        ]

        assert (
            group[
                rolling_3d_columns
            ]
            .head(3)
            .isna()
            .all()
            .all()
        )

        assert not (
            group[
                rolling_3d_columns
            ]
            .iloc[3:]
            .isna()
            .any()
            .any()
        )

        # First seven days do not have seven previous
        # observations.
        rolling_7d_columns = [
            column
            for column in feature_columns
            if (
                "rolling_mean_7d" in column
                or "rolling_std_7d" in column
            )
        ]

        assert (
            group[
                rolling_7d_columns
            ]
            .head(7)
            .isna()
            .all()
            .all()
        )

        assert not (
            group[
                rolling_7d_columns
            ]
            .iloc[7:]
            .isna()
            .any()
            .any()
        )

    # ---------------------------------------------------------
    # Validate machine-day keys.
    # ---------------------------------------------------------

    original_keys = set(
        original[
            KEY_COLUMNS
        ].itertuples(
            index=False,
            name=None,
        )
    )

    feature_keys = set(
        features[
            KEY_COLUMNS
        ].itertuples(
            index=False,
            name=None,
        )
    )

    assert feature_keys == original_keys, (
        "Temporal feature generation changed "
        "the machine-day keys."
    )

    # ---------------------------------------------------------
    # Validate numerical feature types.
    # ---------------------------------------------------------

    numeric_features = features[
        feature_columns
    ]

    assert all(
        pd.api.types.is_numeric_dtype(
            numeric_features[column]
        )
        for column in feature_columns
    ), (
        "Temporal feature columns must "
        "contain numeric values."
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    original = load_sensor_features()

    features = build_temporal_features(
        original
    )

    validate_features(
        original,
        features,
    )

    features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print(
        "TEMPORAL SENSOR FEATURE BUILD COMPLETE"
    )
    print("=" * 60)

    print(
        f"Input rows:       {len(original):,}"
    )

    print(
        f"Output rows:      {len(features):,}"
    )

    print(
        f"Machines:         "
        f"{features['machine_code'].nunique()}"
    )

    print(
        f"Machine-days:     "
        f"{features['date'].nunique()}"
    )

    print()
    print("Temporal feature columns:")

    for column in features.columns:
        print(f"  - {column}")

    print()
    print("First 10 rows:")

    print(
        features.head(10).to_string(
            index=False
        )
    )

    print()
    print(
        f"Output file: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()

