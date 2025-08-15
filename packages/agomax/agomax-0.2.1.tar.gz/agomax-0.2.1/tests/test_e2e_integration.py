from pathlib import Path
import pandas as pd

from agomax.core.detect import fit, score

BASE_DIR = Path(__file__).resolve().parents[0].parent
DATA_DIR = BASE_DIR / "agomax" / "data"
CONFIG_DIR = BASE_DIR / "agomax" / "configs"
COLUMNS_YAML = str(CONFIG_DIR / "columns.yaml")
RULES_YAML = str(CONFIG_DIR / "rules.yaml")


def test_e2e_small_synthetic_with_overrides():
    # Build a controlled tiny dataset where threshold overrides will force known behavior
    # Values chosen to be within INITIALISATION bounds in rules.yaml so rule_violations == 0
    df = pd.DataFrame([
        {"roll": -0.0005, "pitch": 0.00095, "yaw": 0.0, "rollspeed": 0.0002, "pitchspeed": 0.0002, "yawspeed": 0.0015,
         "airspeed": 0.0, "PHASE": "INITIALISATION", "throttle": 0.0, "climb": 0.0, "GPS_status": 1, "Gyro_status": 1, "Accel_status": 1, "Baro_status": 1},
        {"roll": -0.0004, "pitch": 0.00096, "yaw": 0.0, "rollspeed": 0.0003, "pitchspeed": 0.0004, "yawspeed": 0.0016,
         "airspeed": 0.0, "PHASE": "INITIALISATION", "throttle": 0.0, "climb": 0.0, "GPS_status": 1, "Gyro_status": 1, "Accel_status": 1, "Baro_status": 1},
    ])

    pack, base_full, base_feats = fit(
        df,
        COLUMNS_YAML,
        params={
            "scale_features": False,
            "threshold_mode": "percentile",
            "optics_min_samples": 2,
            "dbscan_min_samples": 2,
        },
    )

    # Force all models to flag anomalies via extreme overrides
    overrides = {
        "kmeans_distance": 1e-9,   # small => KMeans flags outliers
        "lof_score": 1e9,           # high => LOF flags anomalies (lower tail threshold)
        "ocsvm_score": 1e9,         # high => OCSVM flags anomalies
        "dbscan_eps": 1e-9,         # tiny eps => most points become noise
        "dbscan_min_samples": 5,
        "optics_min_samples": 50,
    }
    res_all = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=overrides)
    print("E2E All-anomaly case:\n", res_all[["kmeans_flag","lof_pred","ocsvm_pred","dbscan_flag","optics_flag","rule_violations","anomaly"]])

    # All models should push vote to anomaly (-1) and rules have 0 violations in this trivial case
    assert (res_all["vote"] < 0).all()
    assert (res_all["rule_violations"] == 0).all()
    assert (res_all["anomaly"] == 1).all(), "final_anomaly must be 1 when vote=anomaly"

    # Now set thresholds to the opposite extreme to get all normal
    overrides2 = {
        "kmeans_distance": 1e9,
        "lof_score": -1e9,
        "ocsvm_score": -1e9,
        "dbscan_eps": 1e9,
        "dbscan_min_samples": 2,
        "optics_min_samples": 2,
    }
    res_none = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=overrides2)
    print("E2E All-normal case:\n", res_none[["kmeans_flag","lof_pred","ocsvm_pred","dbscan_flag","optics_flag","rule_violations","anomaly"]])
    assert (res_none[["kmeans_flag", "lof_pred", "ocsvm_pred", "dbscan_flag", "optics_flag"]] == 1).all(axis=None)
    # Rules still 0, so final_anomaly must be 0
    assert (res_none["rule_violations"] == 0).all()
    assert (res_none["anomaly"] == 0).all(), "final_anomaly must be 0 when vote=normal and rules ok"

    # Mixed: make rules trip regardless of models
    df_rules = df.copy()
    df_rules.loc[0, "throttle"] = 99  # violate INITIALISATION rule (equals 0)
    res_rules = score(pack, df_rules, COLUMNS_YAML, RULES_YAML, thresholds=overrides2)
    print("E2E Rules-trigger case:\n", res_rules[["rule_violations","anomaly"]])
    assert (res_rules.loc[0, "rule_violations"] > 0) and (res_rules.loc[0, "anomaly"] == 1)
