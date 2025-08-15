"""Preprocessing utilities for AgomaX Offline Mode.

Keeps prototype logic intact:
- Compute airspeedchange = airspeed - airspeed.shift(1), fillna(0)
- Select features: ['roll','pitch','yaw','rollspeed','pitchspeed','yawspeed','airspeedchange']
- Column names controlled by YAML mapping
"""
from __future__ import annotations

from typing import Dict, Tuple
import yaml
import pandas as pd

FEATURE_COLUMNS = [
    "roll",
    "pitch",
    "yaw",
    "rollspeed",
    "pitchspeed",
    "yawspeed",
    "airspeedchange",
]


def load_column_mapping(path: str) -> Dict[str, str]:
    """Load expected->dataset column mapping from YAML."""
    with open(path, "r") as f:
        mapping = yaml.safe_load(f) or {}
    # The YAML is expected-name: dataset-column
    return {str(k): str(v) for k, v in mapping.items()}


def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Rename dataset columns to expected names using mapping (expected -> dataset).

    If a mapped dataset column is missing, keep the original df unchanged for that key.
    """
    inverse = {v: k for k, v in mapping.items()}  # dataset -> expected
    cols_present = {c: inverse[c] for c in df.columns if c in inverse}
    if cols_present:
        df = df.rename(columns=cols_present)
    return df


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived features as in prototype."""
    if "airspeed" in df.columns:
        df = df.copy()
        df["airspeedchange"] = df["airspeed"].astype(float).diff().fillna(0.0)
    else:
        # Ensure the column exists even if not found
        df = df.copy()
        df["airspeedchange"] = 0.0
    return df


def select_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return the exact feature set used by the prototype for clustering/scoring."""
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required feature columns: {missing}")
    return df[FEATURE_COLUMNS].astype(float)


def prepare_offline_dataset(
    base_df: pd.DataFrame, mapping: Dict[str, str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare base dataset for training and scoring (offline single-file workflow).

    Returns (base_full_df, base_features_df)
    """
    base_df = apply_column_mapping(base_df, mapping)
    base_df = compute_features(base_df)
    base_feats = select_feature_frame(base_df)
    return base_df, base_feats
