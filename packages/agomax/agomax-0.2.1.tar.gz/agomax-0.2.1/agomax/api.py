"""
AgomaX Programmatic API: Core training, detection, thresholds, rules, preprocessing, live, and simulator.
Reuses core logic; adds minimal persistence helpers for packs.
"""
from pathlib import Path
from typing import Dict, Generator, Optional

import pandas as pd
import joblib
import yaml

from agomax.core import detect, preprocessing, rules as rules_mod, models
from agomax.live_drone import LiveSourceConfig, live_iterator


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "configs"
COLUMNS_YAML = str(CONFIG_DIR / "columns.yaml")
RULES_YAML = str(CONFIG_DIR / "rules.yaml")


# --- Persistence helpers (joblib) ---
def _save_pack(pack, model_dir: str | Path):
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pack, model_dir / "model.pkl")
    detect.save_model_bundle(pack, model_dir / "profile.json")


def _load_pack(model_dir: str | Path):
    model_dir = Path(model_dir)
    return joblib.load(model_dir / "model.pkl")


# --- Core Training & Detection ---
def train(base_csv_path: str | Path, output_model_dir: str | Path | None = None,
          scale_features: bool = True, columns_yaml: Optional[str] = None) -> object:
    """Train models and optionally save bundle directory with model.pkl and profile.json."""
    df = pd.read_csv(base_csv_path)
    col_yaml = columns_yaml or COLUMNS_YAML
    pack, _, _ = detect.fit(df, columns_yaml=col_yaml, params={
        'scale_features': scale_features,
    })
    if output_model_dir:
        _save_pack(pack, output_model_dir)
    return pack


def detect_csv(input_csv_path: str | Path, model_dir: str | Path,
               thresholds: Optional[Dict] = None,
               columns_yaml: Optional[str] = None,
               rules_yaml: Optional[str] = None) -> pd.DataFrame:
    """Load trained pack and run detection on CSV; returns scored DataFrame."""
    df = pd.read_csv(input_csv_path)
    pack = _load_pack(model_dir)
    col_yaml = columns_yaml or COLUMNS_YAML
    r_yaml = rules_yaml or RULES_YAML
    return detect.score(pack, df, columns_yaml=col_yaml, rules_yaml=r_yaml, thresholds=thresholds)


# --- Threshold Tuning ---
def tune_thresholds(current_thresholds: Dict, adjustments: Dict) -> Dict:
    """Update thresholds dict with adjustments (supports both top-level and values-subdict)."""
    t = {**current_thresholds}
    # If nested under 'values', update there
    if isinstance(t.get('values'), dict):
        v = {**t['values'], **adjustments}
        t['values'] = v
    else:
        t.update(adjustments)
    return t


def auto_threshold(df: pd.DataFrame, method: str = "percentile", scale_features: bool = True,
                   columns_yaml: str | Path | None = None) -> Dict:
    """Calculate dynamic thresholds using Phase 1 logic.

    Accepts raw df; optionally applies columns mapping. If some feature columns are
    missing, computes thresholds on the available subset (>=2 columns required).
    """
    col_yaml = str(columns_yaml) if columns_yaml else None
    if col_yaml:
        mapping = preprocessing.load_column_mapping(col_yaml)
        df = preprocessing.apply_column_mapping(df, mapping)
    df2 = preprocessing.compute_features(df)
    # Select available features intersection
    from agomax.core.preprocessing import FEATURE_COLUMNS
    present = [c for c in FEATURE_COLUMNS if c in df2.columns]
    if len(present) < 2:
        raise ValueError(f"Insufficient feature columns present for auto_threshold (have {present})")
    feats = df2[present].astype(float)
    pack = models.train_models(feats, params={'threshold_mode': method, 'scale_features': scale_features})
    return pack.thresholds


# --- Rules & Preprocessing ---
def load_rules(yaml_path: str | Path | None = None) -> Dict:
    """Load rules.yaml and return dict."""
    path = str(yaml_path or RULES_YAML)
    return yaml.safe_load(Path(path).read_text())


def apply_rules(df: pd.DataFrame, sensitivity: float = 1.0, rules_yaml: str | Path | None = None) -> pd.DataFrame:
    """Apply rules engine and return a DataFrame with rule_violations and rule_anomaly columns."""
    path = str(rules_yaml or RULES_YAML)
    cfg = rules_mod.load_rules(path)
    cfg.sensitivity_delta = float(sensitivity - 1.0)  # sensitivity>1 widens bounds
    viol = rules_mod.evaluate_rules(cfg, df)
    out = pd.DataFrame({'rule_violations': viol})
    out['rule_anomaly'] = (out['rule_violations'] > 0).astype(int)
    return out


def preprocess(df: pd.DataFrame, columns_yaml: str | Path | None = None) -> pd.DataFrame:
    """Apply column mapping and derive features using columns.yaml or default."""
    col_yaml = str(columns_yaml or COLUMNS_YAML)
    mapping = preprocessing.load_column_mapping(col_yaml)
    df2 = preprocessing.apply_column_mapping(df, mapping)
    return preprocessing.compute_features(df2)


# --- Live Mode ---
def start_live(csv_path: str | Path, model_dir: str | Path, refresh_seconds: float = 2.0,
               buffer_size: int = 500, learn_mode: bool = False) -> Generator[Dict, None, None]:
    """Tail CSV in real-time and yield per-row detection results as dicts."""
    rate_hz = 1.0 / max(1e-9, float(refresh_seconds))
    source = LiveSourceConfig(type='csv_replay', csv_path=str(csv_path), rate_hz=rate_hz)
    pack = None
    if not learn_mode:
        pack = _load_pack(model_dir)
    else:
        # Learn baseline first from initial buffer
        buf = []
        it = live_iterator(source, COLUMNS_YAML)
        for row in it:
            buf.append(row)
            if len(buf) >= buffer_size:
                break
        base_df = pd.DataFrame(buf)
        pack, _, _ = detect.fit(base_df, COLUMNS_YAML, params={'scale_features': False})
    # Stream rows and score on the fly
    for row in live_iterator(source, COLUMNS_YAML):
        df = pd.DataFrame([row])
        res = detect.score(pack, df, COLUMNS_YAML, RULES_YAML)
        yield res.iloc[0].to_dict()


# --- Simulator Mode ---
def run_simulator_test(sim_config: LiveSourceConfig | None,
                       duration_seconds: int = 300,
                       baseline_rows: int = 1000) -> Dict:
    """Run drone simulator test and return metrics using the Phase 2 simulator."""
    from phase2_e2e_sim import run_phase2_e2e
    return run_phase2_e2e(n_baseline=baseline_rows, n_detect=baseline_rows,
                          duration_seconds=duration_seconds, source=sim_config)
