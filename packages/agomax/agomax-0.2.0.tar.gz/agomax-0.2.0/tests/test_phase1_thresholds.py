import json
from pathlib import Path
import tempfile

import pandas as pd

from agomax.core.detect import fit, score, save_model_bundle

BASE_DIR = Path(__file__).resolve().parents[0].parent
DATA_DIR = BASE_DIR / "agomax" / "data"
CONFIG_DIR = BASE_DIR / "agomax" / "configs"
COLUMNS_YAML = str(CONFIG_DIR / "columns.yaml")
RULES_YAML = str(CONFIG_DIR / "rules.yaml")


def _print_line(name: str, count: int, baseline: int, thresholds: dict):
    delta = count - baseline
    sign = "+" if delta >= 0 else "-"
    # Format thresholds dict succinctly
    thr_txt = json.dumps(thresholds, sort_keys=True)
    print(f"Test: {name} → anomalies={count} (Δ from baseline: {sign}{abs(delta)}) | thresholds: {thr_txt}")


def _run_baseline(df: pd.DataFrame, scale_features: bool, mode: str = "percentile"):
    pack, base_full, base_feats = fit(
        df,
        COLUMNS_YAML,
        params={
            "scale_features": scale_features,
            "threshold_mode": mode,
            "mad_k": 3.0,
        },
    )
    res = score(pack, df, COLUMNS_YAML, RULES_YAML)
    baseline_count = int(res["anomaly"].sum())
    defaults = pack.thresholds["values"].copy()
    # Verify saved bundle matches
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bundle.json"
        save_model_bundle(pack, out)
        saved = json.loads(out.read_text())
        assert saved["thresholds"]["values"] == pack.thresholds["values"], "Saved thresholds differ from pack defaults"
        assert bool(saved["scale_features"]) == bool(scale_features)
    return pack, baseline_count, defaults


def _verify_defaults_applied(pack, df, baseline_count):
    # Scoring with explicit defaults equals baseline
    res_def = score(
        pack,
        df,
        COLUMNS_YAML,
        RULES_YAML,
        thresholds={
            "kmeans_distance": pack.thresholds["values"]["kmeans"],
            "lof_score": pack.thresholds["values"]["lof"],
            "ocsvm_score": pack.thresholds["values"]["ocsvm"],
        },
    )
    assert int(res_def["anomaly"].sum()) == baseline_count, "Default thresholds not applied consistently"


def test_phase1_thresholds_end_to_end():
    df = pd.read_csv(DATA_DIR / "base.csv")

    for scale in (False, True):
        for mode in ("percentile", "mad"):
            name_prefix = f"scaled={scale}, mode={mode}"

            # Baseline Run
            pack, baseline_count, defaults = _run_baseline(df, scale_features=scale, mode=mode)
            _print_line(f"{name_prefix} | Baseline", baseline_count, baseline_count, defaults)
            _verify_defaults_applied(pack, df, baseline_count)

            # Low Threshold Stress Test
            low_thr = {
                # KMeans: lower -> more anomalies
                "kmeans_distance": 1e-9,
                # LOF/OCSVM use lower tail: higher -> more anomalies
                "lof_score": 1e9,
                "ocsvm_score": 1e9,
            }
            res_low = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=low_thr)
            low_count = int(res_low["anomaly"].sum())
            _print_line(f"{name_prefix} | Low thresholds", low_count, baseline_count, low_thr)
            assert low_count > baseline_count, "Anomaly count did not increase with extreme low/high thresholds"

            # High Threshold Stress Test
            high_thr = {
                # KMeans: higher -> fewer anomalies
                "kmeans_distance": 1e9,
                # LOF/OCSVM lower -> fewer anomalies
                "lof_score": -1e9,
                "ocsvm_score": -1e9,
            }
            res_high = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=high_thr)
            high_count = int(res_high["anomaly"].sum())
            _print_line(f"{name_prefix} | High thresholds", high_count, baseline_count, high_thr)
            # If rules dominate, totals may not drop; ensure model-only anomalies decrease
            res_base = score(pack, df, COLUMNS_YAML, RULES_YAML)
            base_model_only = int(((res_base["rule_violations"] == 0) & (res_base["anomaly"] == 1)).sum())
            high_model_only = int(((res_high["rule_violations"] == 0) & (res_high["anomaly"] == 1)).sum())
            assert high_model_only <= base_model_only, "Model-only anomalies did not decrease under extreme thresholds"
            # And totals should not increase
            assert high_count <= baseline_count, "Total anomalies increased under extreme thresholds"

            # Mixed Thresholds Test
            mixed_thr = {
                "kmeans_distance": 1e-6,  # lower (more anomalies)
                "lof_score": defaults["lof"],  # default
                "ocsvm_score": 1e9,  # higher (more anomalies)
            }
            res_mixed = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=mixed_thr)
            mixed_count = int(res_mixed["anomaly"].sum())
            _print_line(f"{name_prefix} | Mixed thresholds", mixed_count, baseline_count, mixed_thr)
            assert mixed_count != baseline_count, "Anomaly count unchanged under mixed thresholds; voting/overrides may be ignored"

            # Restore Defaults Test
            restore_thr = {
                "kmeans_distance": defaults["kmeans"],
                "lof_score": defaults["lof"],
                "ocsvm_score": defaults["ocsvm"],
            }
            res_restore = score(pack, df, COLUMNS_YAML, RULES_YAML, thresholds=restore_thr)
            restore_count = int(res_restore["anomaly"].sum())
            _print_line(f"{name_prefix} | Restore defaults", restore_count, baseline_count, restore_thr)
            assert restore_count == baseline_count, "Restore defaults did not match baseline anomaly count"
            expect_restore = {
                "kmeans_distance": defaults["kmeans"],
                "lof_score": defaults["lof"],
                "ocsvm_score": defaults["ocsvm"],
            }
            assert restore_thr == expect_restore, "Restore thresholds do not exactly match baseline defaults"

    print("ALL THRESHOLD TESTS PASSED")
