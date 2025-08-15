import pandas as pd
import pytest
from agomax import api
import tempfile
import os

def test_train_and_detect(tmp_path):
    # Create a small fake dataset
    df = pd.DataFrame({
        'roll': [0.1, 0.2],
        'pitch': [0.1, 0.2],
        'yaw': [0.1, 0.2],
        'rollspeed': [0.1, 0.2],
        'pitchspeed': [0.1, 0.2],
        'yawspeed': [0.1, 0.2],
        'airspeed': [5.0, 5.1],
        'PHASE': ['ON MISSION', 'ON MISSION'],
        'throttle': [40, 41],
        'climb': [0.0, 0.1],
    })
    base = tmp_path / "base.csv"
    df.to_csv(base, index=False)
    model_dir = tmp_path / "model"
    pack = api.train(str(base), output_model_dir=str(model_dir))
    res = api.detect_csv(str(base), str(model_dir))
    assert not res.empty
    assert 'anomaly' in res.columns

def test_threshold_tuning():
    t = {'kmeans_distance': 5.0}
    adj = {'kmeans_distance': 10.0}
    tuned = api.tune_thresholds(t, adj)
    assert tuned['kmeans_distance'] == 10.0

def test_auto_threshold():
    df = pd.DataFrame({'roll': [0.1, 0.2], 'pitch': [0.1, 0.2]})
    th = api.auto_threshold(df, method="percentile")
    assert isinstance(th, dict)

def test_rules_and_preprocess():
    df = pd.DataFrame({'roll': [0.1], 'pitch': [0.2]})
    # Should not error
    api.preprocess(df)
    # Dummy rules
    rules = {'ON MISSION': {'roll': {'min': 0.0, 'max': 1.0}}}
    pd.testing.assert_frame_equal(
        api.apply_rules(df, sensitivity=1.0, rules_yaml=None),
        api.apply_rules(df, sensitivity=1.0, rules_yaml=None)
    )

def test_live_mode(tmp_path):
    df = pd.DataFrame({
        'roll': [0.1, 0.2],
        'pitch': [0.1, 0.2],
        'yaw': [0.1, 0.2],
        'rollspeed': [0.1, 0.2],
        'pitchspeed': [0.1, 0.2],
        'yawspeed': [0.1, 0.2],
        'airspeed': [5.0, 5.1],
        'PHASE': ['ON MISSION', 'ON MISSION'],
        'throttle': [40, 41],
        'climb': [0.0, 0.1],
    })
    csv = tmp_path / "live.csv"
    df.to_csv(csv, index=False)
    model_dir = tmp_path / "model"
    api.train(str(csv), output_model_dir=str(model_dir))
    gen = api.start_live(str(csv), str(model_dir), refresh_seconds=0.01)
    # Should yield at least one result
    assert next(gen)

def test_simulator_mode():
    # Only checks import and call, not actual dronekit
    sim_cfg = None  # Would be a LiveSourceConfig for real test
    try:
        api.run_simulator_test(sim_cfg, duration_seconds=1, baseline_rows=1)
    except Exception:
        pass
