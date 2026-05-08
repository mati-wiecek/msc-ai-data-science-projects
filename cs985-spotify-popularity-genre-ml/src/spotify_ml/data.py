"""Data loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import (
    CLASSIFICATION_TEST_FILE,
    CLASSIFICATION_TRAIN_FILE,
    REGRESSION_TEST_FILE,
    REGRESSION_TRAIN_FILE,
)


@dataclass(frozen=True)
class DatasetBundle:
    """Container for the four CSV files used in the project."""

    regression_train: pd.DataFrame
    regression_test: pd.DataFrame
    classification_train: pd.DataFrame
    classification_test: pd.DataFrame


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing data file: {path}. See data/README.md for the expected filenames."
        )
    return pd.read_csv(path)


def load_datasets(data_dir: str | Path) -> DatasetBundle:
    """Load all project datasets from a directory.

    Parameters
    ----------
    data_dir:
        Directory containing the four neutral CSV filenames documented in data/README.md.
    """

    data_dir = Path(data_dir)
    return DatasetBundle(
        regression_train=_read_csv(data_dir / REGRESSION_TRAIN_FILE),
        regression_test=_read_csv(data_dir / REGRESSION_TEST_FILE),
        classification_train=_read_csv(data_dir / CLASSIFICATION_TRAIN_FILE),
        classification_test=_read_csv(data_dir / CLASSIFICATION_TEST_FILE),
    )


def validate_submission(df: pd.DataFrame, expected_rows: int, expected_columns: list[str]) -> None:
    """Run lightweight checks before writing a prediction file."""

    if list(df.columns) != expected_columns:
        raise ValueError(f"Expected columns {expected_columns}, got {list(df.columns)}")
    if len(df) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, got {len(df)}")
    if df.isna().sum().sum() > 0:
        raise ValueError("Submission contains missing values.")
