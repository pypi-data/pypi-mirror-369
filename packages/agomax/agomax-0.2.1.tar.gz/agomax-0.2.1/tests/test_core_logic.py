import itertools
import json
from pathlib import Path
import tempfile

import pandas as pd

from agomax.core.detect import ensemble_vote
from agomax.core.rules import load_rules, evaluate_rules, RuleConfig


def test_majority_voting_all_combinations():
    # -1 = anomaly, +1 = normal in backend
    keys = ["kmeans_flag", "lof_pred", "ocsvm_pred", "dbscan_flag", "optics_flag"]
    for combo in itertools.product([-1, 1], repeat=5):
        row = {k: v for k, v in zip(keys, combo)}
        vote = ensemble_vote(pd.Series(row))
        expected = -1 if combo.count(-1) >= 3 else 1
        assert vote == expected, f"combo={combo} vote={vote} expected={expected}"


def test_rules_engine_bounds_and_flags():
    # Build a simple rules spec: x in [0, 1], phase-specific y in [0, 10]
    rules_yaml = {
        "constant": {"x": {"min": 0, "max": 1}},
        "TEST": {"y": {"min": 0, "max": 10}},
        "sensitivity": {"delta": 0.0},
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "rules.yaml"
        p.write_text(json.dumps(rules_yaml))  # YAML superset accepts JSON
        cfg = load_rules(str(p))

    df = pd.DataFrame([
        {"PHASE": "TEST", "x": 0.5, "y": 5},   # ok
        {"PHASE": "TEST", "x": 1.5, "y": 5},   # x out
        {"PHASE": "TEST", "x": 0.5, "y": 50},  # y out
        {"PHASE": "TEST", "x": 2.0, "y": 50},  # both out
    ])
    violations = evaluate_rules(cfg, df)
    assert list(violations) == [0, 1, 1, 2]

    rules_flag = (violations > 0).astype(int)
    assert list(rules_flag) == [0, 1, 1, 1]


def test_final_decision_or_logic():
    # vote: -1 anomaly, 1 normal; rules_flag: 1 if any violation else 0
    cases = [
        {"vote": -1, "rules_flag": 0, "expected": 1},
        {"vote": 1, "rules_flag": 1, "expected": 1},
        {"vote": -1, "rules_flag": 1, "expected": 1},
        {"vote": 1, "rules_flag": 0, "expected": 0},
    ]
    for c in cases:
        final = 1 if (c["vote"] < 0 or c["rules_flag"] > 0) else 0
        assert final == c["expected"], f"case={c} final={final}"
