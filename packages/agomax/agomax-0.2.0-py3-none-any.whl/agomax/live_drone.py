from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, Optional

import pandas as pd
import yaml

from agomax.core.preprocessing import load_column_mapping, apply_column_mapping, compute_features
from agomax.core.detect import fit, score


@dataclass
class LiveSourceConfig:
    type: str  # csv_replay | udp_json | dronekit
    csv_path: Optional[str] = None
    rate_hz: float = 10.0
    udp_host: str = "0.0.0.0"
    udp_port: int = 14550
    dronekit_conn: str = "tcp:127.0.0.1:5760"


@dataclass
class LiveLearnConfig:
    rows: int = 500
    scale_features: bool = False
    threshold_mode: str = "percentile"
    mad_k: float = 3.0


def load_live_config(path: str | Path) -> tuple[LiveSourceConfig, LiveLearnConfig]:
    data = yaml.safe_load(Path(path).read_text()) if Path(path).exists() else {}
    src = data.get("source", {}) or {}
    learn = data.get("learn", {}) or {}
    return (
        LiveSourceConfig(
            type=str(src.get("type", "csv_replay")),
            csv_path=src.get("csv_path"),
            rate_hz=float(src.get("rate_hz", 10.0)),
            udp_host=str(src.get("udp_host", "0.0.0.0")),
            udp_port=int(src.get("udp_port", 14550)),
            dronekit_conn=str(src.get("dronekit_conn", "tcp:127.0.0.1:5760")),
        ),
        LiveLearnConfig(
            rows=int(learn.get("rows", 500)),
            scale_features=bool(learn.get("scale_features", False)),
            threshold_mode=str(learn.get("threshold_mode", "percentile")),
            mad_k=float(learn.get("mad_k", 3.0)),
        ),
    )


def csv_replay(path: str | Path, rate_hz: float = 10.0) -> Generator[Dict, None, None]:
    df = pd.read_csv(path)
    # Emit rows at a fixed rate
    delay = 1.0 / max(1e-9, rate_hz)
    for _, row in df.iterrows():
        yield row.to_dict()
        time.sleep(delay)


def udp_json_stream(host: str, port: int) -> Generator[Dict, None, None]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(1.0)
    while True:
        try:
            data, _ = sock.recvfrom(65535)
            msg = json.loads(data.decode("utf-8"))
            if isinstance(msg, dict):
                yield msg
            elif isinstance(msg, list):
                for item in msg:
                    if isinstance(item, dict):
                        yield item
        except socket.timeout:
            continue


def dronekit_stream(conn_str: str):  # pragma: no cover (optional dep)
    try:
        # Compat for Python 3.10+ where collections.MutableMapping moved to collections.abc
        import collections, collections.abc  # type: ignore
        if not hasattr(collections, "MutableMapping"):
            collections.MutableMapping = collections.abc.MutableMapping  # type: ignore[attr-defined]
        from dronekit import connect
    except Exception:
        raise ImportError("DroneKit not installed. Install dronekit to use dronekit_stream.")
    vehicle = connect(conn_str, wait_ready=True)
    while True:
        att = vehicle.attitude
        vels = vehicle.velocity  # (vx, vy, vz) m/s
        airspeed = getattr(vehicle, "airspeed", None)
        alt = getattr(vehicle.location.global_relative_frame, "alt", None)
        gps = getattr(vehicle, "location", None)
        lat = getattr(getattr(gps, "global_frame", None), "lat", None)
        lon = getattr(getattr(gps, "global_frame", None), "lon", None)
        msg = {
            "roll": getattr(att, "roll", 0.0),
            "pitch": getattr(att, "pitch", 0.0),
            "yaw": getattr(att, "yaw", 0.0),
            "rollspeed": vels[0] if vels else 0.0,
            "pitchspeed": vels[1] if vels else 0.0,
            "yawspeed": vels[2] if vels else 0.0,
            "airspeed": float(airspeed) if airspeed is not None else 0.0,
            "altitude": float(alt) if alt is not None else 0.0,
            "gps_lat": float(lat) if lat is not None else 0.0,
            "gps_lon": float(lon) if lon is not None else 0.0,
            # placeholders for rules constants; users may map from real msgs
            "PHASE": "ON MISSION",
            "throttle": 50.0,
            "climb": 0.0,
            "GPS_status": 1,
            "Gyro_status": 1,
            "Accel_status": 1,
            "Baro_status": 1,
        }
        yield msg
        time.sleep(0.1)


def standardize_row(row: Dict, columns_yaml: str) -> Dict:
    df = pd.DataFrame([row])
    mapping = load_column_mapping(columns_yaml)
    df = apply_column_mapping(df, mapping)
    # Keep existing fields; compute features as in Phase 1
    df = compute_features(df)
    # Return standardized schema: original + derived features
    return df.iloc[0].to_dict()


def live_iterator(source_cfg: LiveSourceConfig, columns_yaml: str) -> Generator[Dict, None, None]:
    if source_cfg.type == "csv_replay":
        if not source_cfg.csv_path:
            raise ValueError("csv_replay requires csv_path in live.yaml")
        for row in csv_replay(source_cfg.csv_path, source_cfg.rate_hz):
            yield standardize_row(row, columns_yaml)
    elif source_cfg.type == "udp_json":
        for row in udp_json_stream(source_cfg.udp_host, source_cfg.udp_port):
            yield standardize_row(row, columns_yaml)
    elif source_cfg.type == "dronekit":
        for row in dronekit_stream(source_cfg.dronekit_conn):
            yield standardize_row(row, columns_yaml)
    else:
        raise ValueError(f"Unknown source type: {source_cfg.type}")


def live_learn_and_detect(
    source_cfg: LiveSourceConfig,
    learn_cfg: LiveLearnConfig,
    columns_yaml: str,
    rules_yaml: str,
    out_dir: str | Path,
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect baseline
    buffer = []
    iterator = live_iterator(source_cfg, columns_yaml)
    for row in iterator:
        buffer.append(row)
        if len(buffer) >= learn_cfg.rows:
            break

    base_df = pd.DataFrame(buffer)
    base_df.to_csv(out_dir / "live_base.csv", index=False)

    # Train models equivalent to Phase 1
    pack, base_full, base_feats = fit(
        base_df,
        columns_yaml,
        params={
            "scale_features": learn_cfg.scale_features,
            "threshold_mode": learn_cfg.threshold_mode,
            "mad_k": learn_cfg.mad_k,
        },
    )

    # Save minimal bundle (thresholds + scale flag)
    (out_dir / "live_profile.json").write_text(json.dumps({
        "thresholds": pack.thresholds,
        "scale_features": bool(pack.scaler is not None),
    }, indent=2))

    # Switch to detection mode
    total = 0
    anomalies = 0
    last_update = time.time()
    for row in iterator:
        total += 1
        df = pd.DataFrame([row])
        res = score(pack, df, columns_yaml, rules_yaml)
        anomalies += int(res["anomaly"].iloc[0])
        yield {
            "row": row,
            "result": res.iloc[0].to_dict(),
            "stats": {
                "total": total,
                "anomalies": anomalies,
                "last_update": time.time(),
            },
            "pack": pack,
        }
