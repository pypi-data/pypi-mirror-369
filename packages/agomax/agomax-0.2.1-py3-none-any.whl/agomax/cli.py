from __future__ import annotations

import argparse
import json
from pathlib import Path

from agomax.live_drone import (
    load_live_config,
    LiveSourceConfig,
    LiveLearnConfig,
    live_learn_and_detect,
)


def _parse_source(args) -> LiveSourceConfig:
    return LiveSourceConfig(
        type=args.source,
        csv_path=args.csv,
        rate_hz=args.rate,
        udp_host=args.udp_host,
        udp_port=args.udp_port,
        dronekit_conn=args.dronekit,
    )


def main():
    p = argparse.ArgumentParser(prog="agomax")
    sub = p.add_subparsers(dest="cmd")

    # live-drone
    lp = sub.add_parser("live-drone", help="Start live monitoring from drone or replay")
    lp.add_argument("--connect", dest="source", choices=["csv_replay", "udp_json", "dronekit"], default="csv_replay")
    lp.add_argument("--csv", type=str, default=None)
    lp.add_argument("--rate", type=float, default=10.0)
    lp.add_argument("--udp-host", dest="udp_host", type=str, default="0.0.0.0")
    lp.add_argument("--udp-port", dest="udp_port", type=int, default=14550)
    lp.add_argument("--dronekit", type=str, default="tcp:127.0.0.1:5760")
    lp.add_argument("--columns", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "columns.yaml"))
    lp.add_argument("--rules", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "rules.yaml"))
    lp.add_argument("--live-config", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "live.yaml"))

    # baseline
    bp = sub.add_parser("baseline", help="Create/update live baseline from drone or replay")
    bp.add_argument("--connect", dest="source", choices=["csv_replay", "udp_json", "dronekit"], default="csv_replay")
    bp.add_argument("--csv", type=str, default=None)
    bp.add_argument("--rate", type=float, default=10.0)
    bp.add_argument("--udp-host", dest="udp_host", type=str, default="0.0.0.0")
    bp.add_argument("--udp-port", dest="udp_port", type=int, default=14550)
    bp.add_argument("--dronekit", type=str, default="tcp:127.0.0.1:5760")
    bp.add_argument("--columns", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "columns.yaml"))
    bp.add_argument("--rules", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "rules.yaml"))
    bp.add_argument("--live-config", type=str, default=str(Path(__file__).resolve().parents[1] / "configs" / "live.yaml"))
    bp.add_argument("--out", type=str, default=str(Path(__file__).resolve().parents[1] / "data"))

    args = p.parse_args()
    if args.cmd is None:
        p.print_help()
        return 0

    _, learn_cfg = load_live_config(args.live_config)
    src = _parse_source(args)

    if args.cmd == "baseline":
        out_dir = Path(args.out)
        # Run learn only until it returns the first detection packet (after learn)
        it = live_learn_and_detect(src, learn_cfg, args.columns, args.rules, out_dir)
        # consume one message to trigger training and first detection
        try:
            next(it)
        except StopIteration:
            pass
        print(f"Live baseline created in {out_dir}")
        return 0

    if args.cmd == "live-drone":
        # Stream basic stats to stdout
        out_dir = Path(__file__).resolve().parents[1] / "data"
        it = live_learn_and_detect(src, learn_cfg, args.columns, args.rules, out_dir)
        for pkt in it:
            stats = pkt.get("stats", {})
            res = pkt.get("result", {})
            print(json.dumps({"total": stats.get("total"), "anomaly": res.get("anomaly"), "vote": res.get("vote")}))


if __name__ == "__main__":
    main()
