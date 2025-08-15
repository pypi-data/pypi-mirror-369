"""Offline Mode detection pipeline with ensemble voting + rules.

Prototype ensemble rule: majority vote of [KMeans, LOF, OCSVM, DBSCAN, OPTICS]
combined with rules: if vote indicates anomaly OR rule violations > 0 -> anomaly.

This module exposes a small contract:
- fit(base_df, columns_yaml) -> ModelPack, base_features
- score(pack, df, thresholds, rules_yaml, rules_sensitivity) -> result_df with columns
  ['anomaly', 'vote', 'rule_violations', per-model cols...]
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Tuple
import pandas as pd
import json
from pathlib import Path

from .preprocessing import load_column_mapping, prepare_offline_dataset
from .models import train_models, score_all, Thresholds
from .rules import load_rules, evaluate_rules


MODEL_COLS = [
    "kmeans_flag",
    "lof_pred",
    "ocsvm_pred",
    "dbscan_flag",
    "optics_flag",
]


def fit(base_df: pd.DataFrame, columns_yaml: str, params: Dict | None = None):
    """Train models using the base dataset (prototype parity)."""
    mapping = load_column_mapping(columns_yaml)
    base_full, base_feats = prepare_offline_dataset(base_df, mapping)
    pack = train_models(base_feats, params=params)
    return pack, base_full, base_feats


def save_model_bundle(pack, path: str | Path):
    """Save dynamic thresholds and scaler flag to JSON; models can be pickled later if needed."""
    data = {
        "thresholds": pack.thresholds,
        "scale_features": bool(pack.scaler is not None),
    }
    path = Path(path)
    path.write_text(json.dumps(data, indent=2))


def load_model_bundle(path: str | Path) -> Dict:
    return json.loads(Path(path).read_text())


def ensemble_vote(score_df: pd.DataFrame) -> int:
    """Return majority vote over model flags/preds; -1 anomaly, +1 normal."""
    preds = [
        int(score_df["kmeans_flag"]),
        int(score_df["lof_pred"]),
        int(score_df["ocsvm_pred"]),
        int(score_df["dbscan_flag"]),
        int(score_df["optics_flag"]),
    ]
    # Prototype uses max count; ties fall to the value with highest count
    from collections import Counter

    c = Counter(preds)
    return -1 if c[-1] >= c[1] else 1


def score(
    pack,
    df: pd.DataFrame,
    columns_yaml: str,
    rules_yaml: str,
    thresholds: Dict | None = None,
    rules_sensitivity: float | None = None,
) -> pd.DataFrame:
    """Score a dataset and return results with model outputs and final anomaly label."""
    mapping = load_column_mapping(columns_yaml)
    df_full, df_feats = prepare_offline_dataset(df, mapping)

    t = thresholds or {}
    t_obj = Thresholds(
        kmeans_distance=t.get("kmeans_distance"),
        lof_score=t.get("lof_score"),
        ocsvm_score=t.get("ocsvm_score"),
        dbscan_eps=t.get("dbscan_eps"),
        dbscan_min_samples=t.get("dbscan_min_samples"),
        optics_min_samples=t.get("optics_min_samples"),
    )

    scores = score_all(pack, df_feats, thresholds=t_obj)

    # Rules
    rcfg = load_rules(rules_yaml)
    if rules_sensitivity is not None:
        rcfg.sensitivity_delta = float(rules_sensitivity)
    rule_viol = evaluate_rules(rcfg, df_full)

    out = pd.DataFrame({
        "kmeans_distance": scores.kmeans_dists,
        "kmeans_flag": scores.kmeans_flags,
        "lof_score": scores.lof_scores,
        "lof_pred": scores.lof_preds,
        "ocsvm_score": scores.ocsvm_scores,
        "ocsvm_pred": scores.ocsvm_preds,
        "dbscan_flag": scores.dbscan_labels,
        "optics_flag": scores.optics_labels,
        "rule_violations": rule_viol,
    })

    out["vote"] = out.apply(ensemble_vote, axis=1)
    out["anomaly"] = ((out["vote"] < 0) | (out["rule_violations"] > 0)).astype(int)
    return out
