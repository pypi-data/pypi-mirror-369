"""Model training and scoring aligned with the prototype.

Prototype specifics kept:
- KMeans with k=2 (random init, n_init=10, random_state=1), distance-to-centroid threshold = mean + 3*std
- LOF with n_neighbors=14, contamination="auto", novelty=True
- One-Class SVM with nu=0.1, kernel='rbf', gamma='scale'
- DBSCAN with default eps=0.78 (tunable), min_samples default from sklearn (5) unless overridden
- OPTICS with default min_samples=50 (tunable)

All models are trained on the base feature DataFrame, then used to score another DataFrame row-wise.
Thresholds can be adjusted at scoring time without retraining for KMeans (distance),
for LOF/OCSVM we rescore using decision_function/score_samples where available
and apply a user threshold on the output sign.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, OPTICS
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler


@dataclass
class ModelPack:
    kmeans: KMeans
    lof: LocalOutlierFactor
    ocsvm: OneClassSVM
    dbscan_base: DBSCAN
    optics_base: OPTICS
    # Precomputed for kmeans thresholding
    kmeans_centroids: np.ndarray
    # Optional scaler when scale_features=True
    scaler: Optional[StandardScaler]
    # Dynamic thresholds and metadata
    thresholds: Dict


DEFAULTS = {
    "kmeans_k": 2,
    "kmeans_n_init": 10,
    "kmeans_random_state": 1,
    "lof_n_neighbors": 14,
    "lof_contamination": "auto",
    "ocsvm_nu": 0.1,
    "ocsvm_kernel": "rbf",
    "ocsvm_gamma": "scale",
    "dbscan_eps": 0.78,
    "dbscan_min_samples": 5,
    "optics_min_samples": 50,
    # New options
    "scale_features": False,
    # threshold_mode: 'percentile' or 'mad'
    "threshold_mode": "percentile",
    "mad_k": 3.0,
}


def _percentile_threshold(data: np.ndarray, pct: float, tail: str) -> float:
    if tail == "upper":
        q = pct
    else:
        q = 100.0 - pct
    return float(np.percentile(data, q))


def _mad_threshold(data: np.ndarray, k: float, tail: str) -> float:
    med = float(np.median(data))
    mad = float(np.median(np.abs(data - med)))
    if tail == "upper":
        return med + k * mad
    else:
        return med - k * mad


def train_models(base_features: pd.DataFrame, params: Dict | None = None) -> ModelPack:
    """Train models and compute dynamic thresholds on the base dataset.

    Thresholds per model (KMeans, LOF, OCSVM) are computed on training scores only,
    using either 99.7th percentile (upper tail for distances, lower tail for scores)
    or Median +/- k*MAD with k=3 by default.
    """
    p = {**DEFAULTS, **(params or {})}

    scaler: Optional[StandardScaler] = None
    X = base_features.to_numpy()
    if p["scale_features"]:
        scaler = StandardScaler().fit(X)
        X_train = scaler.transform(X)
    else:
        X_train = X

    kmeans = KMeans(init="random", n_clusters=p["kmeans_k"], n_init=p["kmeans_n_init"], random_state=p["kmeans_random_state"])
    kmeans.fit(X_train)

    lof = LocalOutlierFactor(n_neighbors=p["lof_n_neighbors"], contamination=p["lof_contamination"], novelty=True)
    lof.fit(X_train)

    ocsvm = OneClassSVM(nu=p["ocsvm_nu"], kernel=p["ocsvm_kernel"], gamma=p["ocsvm_gamma"])
    ocsvm.fit(X_train)

    # Clamp clustering params for small datasets
    n_samples = int(X_train.shape[0])
    db_min = int(p["dbscan_min_samples"]) if p.get("dbscan_min_samples") is not None else 5
    db_min_eff = max(1, min(db_min, max(1, n_samples)))
    dbscan_base = DBSCAN(eps=p["dbscan_eps"], min_samples=db_min_eff).fit(X_train)

    op_min = int(p["optics_min_samples"]) if p.get("optics_min_samples") is not None else 50
    if n_samples < 2:
        # Can't fit OPTICS; store a placeholder with sane default; scoring refits per-batch anyway
        optics_base = OPTICS(min_samples=2)
    else:
        op_min_eff = max(2, min(op_min, n_samples))
        optics_base = OPTICS(min_samples=op_min_eff).fit(X_train)

    # Compute training score distributions
    centroids = kmeans.cluster_centers_
    base_clusters = kmeans.labels_
    km_dists = np.array([np.linalg.norm(X_train[i] - centroids[int(c)]) for i, c in enumerate(base_clusters)], dtype=float)

    # LOF scores: use decision_function; lower is more anomalous
    try:
        lof_scores_train = np.asarray(lof.decision_function(X_train), dtype=float)
    except Exception:
        # Fallback
        lof_scores_train = -np.asarray(lof._score_samples(X_train), dtype=float)

    # OCSVM scores: decision_function; lower more anomalous
    oc_scores_train = np.asarray(ocsvm.decision_function(X_train), dtype=float)

    # Dynamic thresholds
    mode = p["threshold_mode"]  # 'percentile' or 'mad'
    mad_k = float(p["mad_k"])
    if mode == "percentile":
        # 99.7th percentile for upper tail (KMeans distance)
        km_thr = _percentile_threshold(km_dists, 99.7, tail="upper")
        # 0.3rd percentile for lower tail scores (LOF/OCSVM)
        lof_thr = _percentile_threshold(lof_scores_train, 99.7, tail="lower")
        oc_thr = _percentile_threshold(oc_scores_train, 99.7, tail="lower")
    else:  # 'mad'
        km_thr = _mad_threshold(km_dists, mad_k, tail="upper")
        lof_thr = _mad_threshold(lof_scores_train, mad_k, tail="lower")
        oc_thr = _mad_threshold(oc_scores_train, mad_k, tail="lower")

    thresholds = {
        "mode": mode,
        "mad_k": mad_k,
        "values": {
            "kmeans": float(km_thr),
            "lof": float(lof_thr),
            "ocsvm": float(oc_thr),
        },
        "directions": {
            "kmeans": "upper",
            "lof": "lower",
            "ocsvm": "lower",
        },
        "scale_features": bool(p["scale_features"]),
    }

    return ModelPack(
        kmeans=kmeans,
        lof=lof,
        ocsvm=ocsvm,
        dbscan_base=dbscan_base,
        optics_base=optics_base,
        kmeans_centroids=centroids,
        scaler=scaler,
        thresholds=thresholds,
    )


@dataclass
class Thresholds:
    kmeans_distance: float | None = None
    lof_score: float | None = None  # threshold on LOF negative_outlier_factor_ or decision_function
    ocsvm_score: float | None = None  # threshold on decision_function (>0 normal; <0 anomaly)
    dbscan_eps: float | None = None
    dbscan_min_samples: int | None = None
    optics_min_samples: int | None = None


@dataclass
class ScoreOutputs:
    # Raw model outputs stored for live rescoring
    kmeans_flags: List[int]
    kmeans_dists: List[float]
    lof_preds: List[int]
    lof_scores: List[float]
    ocsvm_preds: List[int]
    ocsvm_scores: List[float]
    dbscan_labels: List[int]
    optics_labels: List[int]


def score_all(
    pack: ModelPack,
    df_features: pd.DataFrame,
    thresholds: Thresholds | None = None,
) -> ScoreOutputs:
    """Score a dataset with all models. thresholds apply without retraining.

    Returns raw per-model results, keeping prototype semantics:
    - KMeans: outlier if distance > threshold -> label -1 else +1
    - LOF: use predict() for labels; for scores use decision_function if available
    - OCSVM: predict(); scores from decision_function
    - DBSCAN/OPTICS: fit_predict on df (prototype refit behavior for target df)
    """
    t = thresholds or Thresholds()

    # Prepare features (apply scaler if present)
    X = df_features.to_numpy()
    X_used = pack.scaler.transform(X) if pack.scaler is not None else X

    # KMeans
    clusters = pack.kmeans.predict(X_used)
    dists = [float(np.linalg.norm(X_used[i] - pack.kmeans_centroids[int(clusters[i])])) for i in range(len(X_used))]
    km_default = pack.thresholds["values"]["kmeans"]
    km_thresh = t.kmeans_distance if t.kmeans_distance is not None else km_default
    kmeans_flags = [-1 if d > km_thresh else 1 for d in dists]

    # LOF
    try:
        lof_scores = pack.lof.decision_function(X_used)
    except Exception:
        # Fallback: scikit sometimes has only negative_outlier_factor_
        lof_scores = -pack.lof._score_samples(X_used)
    lof_default = pack.thresholds["values"]["lof"]
    lof_thr = t.lof_score if t.lof_score is not None else lof_default
    lof_preds = np.where(lof_scores < lof_thr, -1, 1)

    # OCSVM
    oc_scores = pack.ocsvm.decision_function(X_used)
    oc_default = pack.thresholds["values"]["ocsvm"]
    oc_thr = t.ocsvm_score if t.ocsvm_score is not None else oc_default
    ocsvm_preds = np.where(oc_scores < oc_thr, -1, 1)

    # DBSCAN
    db_eps = t.dbscan_eps if t.dbscan_eps is not None else pack.dbscan_base.eps
    db_min = t.dbscan_min_samples if t.dbscan_min_samples is not None else pack.dbscan_base.min_samples
    # Clamp min_samples to avoid ValueError on tiny datasets
    n_samples = int(X_used.shape[0])
    if db_min is None:
        db_min_eff = 5
    else:
        # Ensure 1 <= min_samples <= n_samples
        db_min_eff = max(1, min(int(db_min), max(1, n_samples)))
    db = DBSCAN(eps=db_eps, min_samples=db_min_eff)
    db_labels = db.fit_predict(X_used)
    # Convert noise (=-1) to anomaly (-1) and clusters to normal (1)
    db_flags = np.where(db_labels == -1, -1, 1)

    # OPTICS
    op_min = t.optics_min_samples if t.optics_min_samples is not None else pack.optics_base.min_samples
    # OPTICS requires min_samples >= 2 and <= n_samples; for n_samples < 2, skip and mark normal
    if n_samples < 2:
        optics_flags = np.ones(n_samples, dtype=int)
    else:
        if op_min is None:
            op_min_eff = 50
        else:
            op_min_eff = int(op_min)
        # constrain to [2, n_samples]
        op_min_eff = max(2, min(op_min_eff, n_samples))
        optics = OPTICS(min_samples=op_min_eff)
        optics_labels = optics.fit_predict(X_used)
        optics_flags = np.where(optics_labels == -1, -1, 1)

    return ScoreOutputs(
        kmeans_flags=list(map(int, kmeans_flags)),
        kmeans_dists=dists,
        lof_preds=list(map(int, lof_preds)),
        lof_scores=list(map(float, lof_scores)),
        ocsvm_preds=list(map(int, ocsvm_preds)),
        ocsvm_scores=list(map(float, oc_scores)),
        dbscan_labels=list(map(int, db_flags)),
        optics_labels=list(map(int, optics_flags)),
    )
