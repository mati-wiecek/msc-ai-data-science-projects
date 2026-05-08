"""Feature engineering utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def clean_year_and_add_decade(df: pd.DataFrame, year_col: str = "year") -> pd.DataFrame:
    """Extract a clean year and add a decade feature.

    The function is intentionally defensive: if a year contains extra text or a missing value,
    it extracts the first four-digit year and falls back to the median year in that dataframe.
    """

    out = df.copy()
    if year_col not in out.columns:
        out["year_clean"] = np.nan
        out["decade"] = "unknown"
        return out

    extracted = out[year_col].astype(str).str.extract(r"(\d{4})")[0]
    out["year_clean"] = pd.to_numeric(extracted, errors="coerce")
    median_year = out["year_clean"].median()
    if pd.isna(median_year):
        median_year = 2000
    out["year_clean"] = out["year_clean"].fillna(median_year)
    out["decade"] = (np.floor(out["year_clean"] / 10) * 10).astype(int).astype(str)
    return out


def add_artist_title_text(df: pd.DataFrame) -> pd.DataFrame:
    """Create a single lowercase text field from artist and title."""

    out = df.copy()
    artist = out["artist"].fillna("") if "artist" in out.columns else ""
    title = out["title"].fillna("") if "title" in out.columns else ""
    out["artist_title_text"] = (artist.astype(str) + " " + title.astype(str)).str.lower().str.strip()
    return out


def split_feature_types(df: pd.DataFrame, categorical_candidates: list[str]) -> tuple[list[str], list[str]]:
    """Return categorical and numeric columns after filtering unavailable candidates."""

    categorical = [col for col in categorical_candidates if col in df.columns]
    numeric = [col for col in df.columns if col not in categorical]
    return categorical, numeric
