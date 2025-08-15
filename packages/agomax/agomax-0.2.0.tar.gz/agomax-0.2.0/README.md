# AgomaX

Drone anomaly detection with ensemble models and YAML rules. Phase 1 (offline) and Phase 2 (live ingestion + live learn) are implemented.

## Usage

### Dashboard

Python entrypoint:

```python
import agomax
agomax.dashboard()  # optional: port=8501, theme="dark", debug=True
```

### Programmatic API

```python
from agomax import api

# Train and save a model
pack = api.train("agomax/data/base.csv", output_model_dir="models/default")

# Detect on a CSV with a saved model
results = api.detect_csv("agomax/data/live.csv", model_dir="models/default")

# Adjust thresholds programmatically
current = pack.thresholds
tuned = api.tune_thresholds(current, {"kmeans": current["values"]["kmeans"] + 1.0})

# Live mode (CSV tail)
for out in api.start_live("agomax/data/live.csv", "models/default", refresh_seconds=0.5):
	print(out)

# Simulator test (requires DroneKit/SITL or a provided source config)
from agomax.live_drone import LiveSourceConfig
rep = api.run_simulator_test(None, duration_seconds=60, baseline_rows=200)
print(rep)
```

## Phase 2 E2E Simulator (SITL)

Automates an end-to-end validation using ArduPilot SITL via DroneKit, with a realistic long-run protocol:
- Warmup 200 rows (ignored)
- Baseline 1000 rows (train live baseline)
- Detection for remaining rows, target ~12 minutes @ 10Hz (~7200 rows)
- Robust live iterator with reconnects, exponential backoff, and heartbeat
- Schema/NaN guards before scoring
- Explainability: KMeans per-feature contributions combined with Rules violations
- Sanity warnings when anomaly rate is very high

File: `phase2_e2e_sim.py`

Prerequisites (install in your virtualenv):
- Python 3.9+
- Packages from `requirements.txt`
- Optional (for this simulator): `dronekit`, `dronekit-sitl`

Notes:
- No project config changes are required; the script writes outputs under `agomax/data` and `agomax/output`.
- You can adjust baseline length, detection length, and rate (Hz) by editing the call in the `__main__` block.
- If you have your own telemetry source (CSV/UDP/real drone), use the CLI instead of SITL (see below).

Expected outputs:
- `agomax/data/live_base.csv` — baseline window captured from live feed
- `agomax/data/live_profile.json` — thresholds and scaling info learned from baseline
- `agomax/data/live.csv` — baseline + detection portion combined
- `agomax/output/live_anomalies.csv` — indices and flags for the detection portion
- Console PASS/FAIL report with top contributing features

Troubleshooting:
- If you see `No module named pytest` during local testing, install dev deps or run without tests.
- If SITL fails to start, ensure `dronekit-sitl` is installed and accessible in your environment.

Run (default long-run ~12 minutes):

```bash
/Users/shaguntembhurne/AgomaX/.venv/bin/python /Users/shaguntembhurne/AgomaX/phase2_e2e_sim.py
```

Tune parameters by editing the `__main__` call or importing `run_phase2_e2e(...)`.

## Live CLI

A minimal CLI is available:
- `agomax baseline` — captures a baseline from a chosen source and saves it to `agomax/data`
- `agomax live-drone` — learns from baseline then streams detections, printing basic stats

Sources supported: `csv_replay`, `udp_json`, `dronekit`. See `agomax/configs/live.yaml` for defaults.

## Streamlit Dashboard

Two pages are included:
- Offline Analysis — tune thresholds and rules, instant rescoring and visuals
- Live Monitoring — select source, start/stop, and view KPIs, timeline, and recent anomalies

## Development

- Python package metadata in `pyproject.toml`
- Tests under `tests/` and `agomax/tests/`
- Core modules in `agomax/core/`
- Live ingestion and pipeline in `agomax/live_drone.py`
- Config YAMLs in `agomax/configs/`

