import pandas as pd
from pathlib import Path

from agomax.core.detect import fit, score

BASE_DIR = Path(__file__).resolve().parents[1]
COLUMNS_YAML = BASE_DIR / "configs" / "columns.yaml"
RULES_YAML = BASE_DIR / "configs" / "rules.yaml"
DATA_DIR = BASE_DIR / "data"


def test_pipeline_runs():
    base = pd.read_csv(DATA_DIR / "base.csv")
    pack, base_full, base_feats = fit(base, str(COLUMNS_YAML))
    res = score(pack, base, str(COLUMNS_YAML), str(RULES_YAML))
    assert "anomaly" in res.columns
    assert len(res) == len(base)


def test_threshold_adjustment_changes_counts():
    base = pd.read_csv(DATA_DIR / "base.csv")
    pack, base_full, base_feats = fit(base, str(COLUMNS_YAML))
    res1 = score(pack, base, str(COLUMNS_YAML), str(RULES_YAML))
    # Use extreme thresholds to force many anomalies
    res2 = score(
        pack,
        base,
        str(COLUMNS_YAML),
        str(RULES_YAML),
        thresholds={
            "kmeans_distance": 1e-9,
            "lof_score": 1e9,
            "ocsvm_score": 1e9,
        },
    )
    assert res1["anomaly"].sum() != res2["anomaly"].sum()


def test_export_shapes():
    base = pd.read_csv(DATA_DIR / "base.csv")
    pack, base_full, base_feats = fit(base, str(COLUMNS_YAML))
    res = score(pack, base, str(COLUMNS_YAML), str(RULES_YAML))
    csv_bytes = res.to_csv(index=False).encode()
    json_str = res.to_json(orient="records")
    assert len(csv_bytes) > 0
    assert json_str.startswith("[") and json_str.endswith("]")
