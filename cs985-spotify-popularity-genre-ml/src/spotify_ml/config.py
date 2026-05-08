"""Project configuration constants."""

from __future__ import annotations

from pathlib import Path

RANDOM_STATE = 42
ID_COLUMN = "Id"
REGRESSION_TARGET = "pop"
CLASSIFICATION_TARGET = "top genre"

# Public-safe, neutral filenames. The original competition filenames are not used in this repo.
REGRESSION_TRAIN_FILE = "spotify_regression_train.csv"
REGRESSION_TEST_FILE = "spotify_regression_test.csv"
CLASSIFICATION_TRAIN_FILE = "spotify_classification_train.csv"
CLASSIFICATION_TEST_FILE = "spotify_classification_test.csv"

DEFAULT_DATA_DIR = Path("data/raw")
DEFAULT_OUTPUT_DIR = Path("outputs")
DEFAULT_FIGURE_DIR = Path("figures")
