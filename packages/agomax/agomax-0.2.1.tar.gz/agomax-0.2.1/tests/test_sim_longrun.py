import time
from pathlib import Path
import numpy as np
import pandas as pd

from phase2_e2e_sim import run_phase2_e2e


def gen_rows(n=3000, rate_hz=10.0):
    # Deterministic synthetic telemetry with phases cycling
    phases = ["INITIALISATION", "TAKEOFF", "ON MISSION", "RETURN TO ORIGIN", "LANDING"]
    for i in range(n):
        ph = phases[(i // 600) % len(phases)]
        row = {
            "roll": np.sin(i/50.0) * 0.05,
            "pitch": np.cos(i/60.0) * 0.05,
            "yaw": np.sin(i/70.0) * 0.1,
            "rollspeed": np.sin(i/10.0) * 0.5,
            "pitchspeed": np.cos(i/10.0) * 0.5,
            "yawspeed": np.sin(i/12.0) * 0.4,
            "airspeed": max(0, 5 + np.sin(i/30.0)),
            "PHASE": ph,
            "throttle": 40 + 10*np.sin(i/100.0),
            "climb": 0.1*np.sin(i/40.0),
        }
        # inject occasional anomaly blips post-baseline
        if i > 1200 and i % 250 == 0:
            row["roll"] += 1.0
            row["pitch"] -= 1.0
        yield row
        # simulate timing without sleeping to keep tests fast


def test_longrun_mock_stream(tmp_path):
    # 1000 baseline + 1500 detect
    report = run_phase2_e2e(
        n_baseline=1000,
        n_detect=1500,
        rate_hz=10.0,
        duration_seconds=None,
        warmup_rows=200,
        rows_iter=gen_rows(3000),
    )
    # Ensure no crash and metrics present
    assert report["rows_baseline"] >= 900
    assert report["rows_live_detection"] >= 1000
    # Explainability non-trivial when anomalies present
    if report["anomalies_live"] > 0:
        feats = dict(report.get("top_features", []))
        assert len(feats) > 0
        s = sum(feats.values())
        assert 0.9 <= s <= 1.1
    # Consistency should be high
    assert report["consistency_rate"] >= 95.0
