from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


HIGH_TIER_RARITIES = {"gold", "platinum"}


def parse_last_number(value: object) -> float:
    """Extract the final numeric token from a value such as "8400" or "[1, 8400]"."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    numbers = re.findall(r"[-+]?\d*\.?\d+", str(value))
    return float(numbers[-1]) if numbers else np.nan


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lower-case, single-spaced column names."""
    out = df.copy()
    out.columns = out.columns.str.strip().str.replace(r"\s+", " ", regex=True).str.lower()
    return out


def add_modelling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-safe numeric features and a high-tier target label."""
    out = normalise_columns(df)

    out["hp_max_raw"] = out["hp"].apply(parse_last_number) if "hp" in out else np.nan
    out["attack_max_raw"] = out["attack"].apply(parse_last_number) if "attack" in out else np.nan

    hp_fallback = pd.to_numeric(out.get("hp_max"), errors="coerce") if "hp_max" in out else np.nan
    attack_fallback = pd.to_numeric(out.get("attack_max"), errors="coerce") if "attack_max" in out else np.nan

    out["hp_for_model"] = out["hp_max_raw"].where(out["hp_max_raw"].notna(), hp_fallback)
    out["attack_for_model"] = out["attack_max_raw"].where(out["attack_max_raw"].notna(), attack_fallback)
    out["rarity"] = out["rarity"].astype(str).str.strip().str.lower()
    out["is_high"] = out["rarity"].isin(HIGH_TIER_RARITIES).astype(int)

    return out


def load_pettan_dataset(path: str | Path) -> pd.DataFrame:
    """Load the cleaned Pettan card CSV and ensure modelling features exist."""
    df = pd.read_csv(path)
    return add_modelling_features(df)
