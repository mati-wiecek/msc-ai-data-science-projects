from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def safe_read_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    """Read a CSV with a clear error message when local data files are missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}. Place the Kaggle/raw data in data/raw/ "
            "or update the DATA_DIR variable in the notebook."
        )
    return pd.read_csv(path, **kwargs)


def existing_columns(df: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    """Return only columns that exist in a DataFrame."""
    return [c for c in columns if c in df.columns]


def iqr_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float]:
    """Return Tukey IQR outlier bounds for a numeric series."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    q1, q3 = clean.quantile([0.25, 0.75])
    iqr = q3 - q1
    return float(q1 - k * iqr), float(q3 + k * iqr)


def cramers_v(table: pd.DataFrame | np.ndarray) -> float:
    """Cramer's V effect size for a contingency table."""
    chi2, _, _, _ = chi2_contingency(table)
    n = np.asarray(table).sum()
    if n == 0:
        return np.nan
    r, k = np.asarray(table).shape
    denom = n * max(min(k - 1, r - 1), 1)
    return float(math.sqrt(chi2 / denom))


def benjamini_hochberg(p_values: Iterable[float]) -> np.ndarray:
    """Benjamini-Hochberg false-discovery-rate adjusted p-values."""
    p_values = np.asarray(list(p_values), dtype=float)
    adjusted = np.full_like(p_values, np.nan, dtype=float)
    valid = ~np.isnan(p_values)
    p = p_values[valid]
    if len(p) == 0:
        return adjusted
    order = np.argsort(p)
    ranked = p[order]
    n = len(ranked)
    bh = ranked * n / np.arange(1, n + 1)
    bh = np.minimum.accumulate(bh[::-1])[::-1]
    out = np.empty_like(bh)
    out[order] = np.clip(bh, 0, 1)
    adjusted[valid] = out
    return adjusted


def mannwhitney_effect(x: pd.Series, y: pd.Series) -> dict[str, float]:
    """Mann-Whitney U test plus rank-biserial correlation effect size."""
    x = pd.to_numeric(x, errors="coerce").dropna()
    y = pd.to_numeric(y, errors="coerce").dropna()
    if len(x) < 2 or len(y) < 2:
        return {"u_statistic": np.nan, "p_value": np.nan, "rank_biserial": np.nan}
    u_stat, p_value = mannwhitneyu(x, y, alternative="two-sided")
    rank_biserial = (2 * u_stat / (len(x) * len(y))) - 1
    return {
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "rank_biserial": float(rank_biserial),
    }


def binary_classification_summary(y_true, y_score, threshold: float = 0.5) -> dict[str, float]:
    """Metrics designed for imbalanced binary classification."""
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    y_pred = (y_score >= threshold).astype(int)
    out = {
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "average_precision_pr_auc": average_precision_score(y_true, y_score),
    }
    if len(np.unique(y_true)) == 2:
        out["roc_auc"] = roc_auc_score(y_true, y_score)
    else:
        out["roc_auc"] = np.nan
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    out.update({"tn": tn, "fp": fp, "fn": fn, "tp": tp})
    return out


URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
HTML_RE = re.compile(r"<.*?>")
MENTION_RE = re.compile(r"@\w+")
REPEATED_SPACES_RE = re.compile(r"\s+")


def clean_tweet(text: str) -> str:
    """Small, reproducible tweet cleaner that preserves negation words."""
    text = str(text)
    text = HTML_RE.sub(" ", text)
    text = URL_RE.sub(" urltoken ", text)
    text = MENTION_RE.sub(" usertoken ", text)
    text = text.replace("#", " ")
    text = text.lower()
    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    text = REPEATED_SPACES_RE.sub(" ", text).strip()
    return text
