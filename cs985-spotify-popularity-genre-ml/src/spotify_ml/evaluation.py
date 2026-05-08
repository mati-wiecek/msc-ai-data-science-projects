"""Evaluation helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error


def rmse(y_true, y_pred) -> float:
    """Root mean squared error as a float."""

    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def metrics_frame(rows: list[dict]) -> pd.DataFrame:
    """Create a consistently ordered metrics table."""

    columns = ["task", "model", "metric", "train_metric", "validation_metric"]
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=columns)
    return df[columns]
