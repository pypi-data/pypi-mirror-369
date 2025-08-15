"""Rules engine reflecting prototype phase-based checks, with YAML config.

We interpret rules.yaml as simple range or equality constraints per phase, plus
constant checks applied to every row. Sensitivity delta widens ranges.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import yaml
import pandas as pd


@dataclass
class RuleConfig:
    rules: Dict[str, Any]
    sensitivity_delta: float = 0.0


def load_rules(path: str) -> RuleConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    sens = 0.0
    if isinstance(data.get("sensitivity"), dict):
        sens = float(data["sensitivity"].get("delta", 0.0))
    return RuleConfig(rules=data, sensitivity_delta=sens)


def _within(val: float, low: float | None, high: float | None, delta: float) -> bool:
    if low is None and high is None:
        return True
    if low is None:
        return val <= high * (1 + delta)
    if high is None:
        return val >= low * (1 - delta)
    # Expand bounds by delta
    width = (high - low) * delta
    return (val >= low - width) and (val <= high + width)


def _check_rule(row: pd.Series, spec: Dict[str, Any], delta: float) -> int:
    # equals or min/max
    if "equals" in spec:
        try:
            return 0 if float(row) == float(spec["equals"]) else 1
        except Exception:
            return 0 if str(row) == str(spec["equals"]) else 1
    low = spec.get("min")
    high = spec.get("max")
    try:
        v = float(row)
    except Exception:
        return 1  # cannot evaluate numeric range
    return 0 if _within(v, low, high, delta) else 1


def evaluate_rules(cfg: RuleConfig, df: pd.DataFrame) -> pd.Series:
    """Return number of rule violations per row.

    Applies constant rules, then phase rules if a 'PHASE' column exists.
    """
    delta = cfg.sensitivity_delta
    const = cfg.rules.get("constant", {})
    per_phase = {k: v for k, v in cfg.rules.items() if k not in ("constant", "sensitivity")}

    violations = []
    for _, row in df.iterrows():
        v = 0
        for col, spec in const.items():
            if col in row:
                v += _check_rule(row[col], spec, delta)
        phase = str(row.get("PHASE", ""))
        if phase in per_phase:
            for col, spec in per_phase[phase].items():
                if col in row:
                    v += _check_rule(row[col], spec, delta)
        violations.append(v)
    return pd.Series(violations, index=df.index, name="rule_violations")
