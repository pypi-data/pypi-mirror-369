import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import threading
import queue
from pathlib import Path

from agomax.live_drone import load_live_config, live_learn_and_detect, LiveSourceConfig


def _init_state():
    if "live_running" not in st.session_state:
        st.session_state.live_running = False
    if "live_stats" not in st.session_state:
        st.session_state.live_stats = {"total": 0, "anomalies": 0, "last_update": None}
    if "live_rows" not in st.session_state:
        st.session_state.live_rows = []
    if "live_results" not in st.session_state:
        st.session_state.live_results = []
    if "live_thread" not in st.session_state:
        st.session_state.live_thread = None
    if "live_q" not in st.session_state:
        st.session_state.live_q = queue.Queue(maxsize=1000)


def _kpis():
    s = st.session_state.live_stats
    total = s.get("total", 0)
    anomalies = s.get("anomalies", 0)
    rate = (anomalies / total * 100.0) if total > 0 else 0.0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total points", total)
    c2.metric("Detected anomalies", anomalies)
    c3.metric("Anomaly rate", f"{rate:.2f}%")


def _timeline():
    res = st.session_state.live_results
    if not res:
        return
    df = pd.DataFrame({
        "index": np.arange(len(res)),
        "status": ["Anomaly" if int(r.get("anomaly", 0)) == 1 else "Normal" for r in res],
        "value": 1,
    })
    color_scale = alt.Scale(domain=["Normal", "Anomaly"], range=["#10b981", "#ef4444"])  # green/red
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("index:Q", title="Index"),
        y=alt.Y("value:Q", axis=None),
        color=alt.Color("status:N", scale=color_scale, title="Status"),
        tooltip=["index", "status"],
    ).properties(height=120)
    st.altair_chart(chart, use_container_width=True)


def _recent_table(n: int = 50):
    rows = st.session_state.live_rows[-n:]
    res = st.session_state.live_results[-n:]
    if not rows:
        return
    df = pd.DataFrame(rows)
    r = pd.DataFrame(res)
    df = df.reset_index(drop=True)
    r = r.reset_index(drop=True)
    out = pd.concat([df, r[["anomaly", "vote", "rule_violations"]]], axis=1)
    st.dataframe(out, use_container_width=True)


def _run_bg(source: LiveSourceConfig, columns_yaml: str, rules_yaml: str, data_dir: Path):
    # Load learn config
    live_yaml = str(Path(__file__).resolve().parents[2] / "configs" / "live.yaml")
    _, learn = load_live_config(live_yaml)
    it = live_learn_and_detect(source, learn, columns_yaml, rules_yaml, data_dir)
    for pkt in it:
        # push into queue for UI thread
        try:
            st.session_state.live_q.put(pkt, timeout=1.0)
        except queue.Full:
            continue


def render(columns_yaml: str, rules_yaml: str, data_dir: Path):
    _init_state()
    st.header("Live Monitoring")

    # Source selection
    st.sidebar.subheader("Source")
    src_type = st.sidebar.selectbox("Connect via", ["csv_replay", "udp_json", "dronekit"], index=0)
    csv_path = st.sidebar.text_input("CSV path (replay)", value=str(data_dir / "base.csv"))
    rate = st.sidebar.number_input("Replay rate (Hz)", value=10.0)
    udp_host = st.sidebar.text_input("UDP host", value="0.0.0.0")
    udp_port = st.sidebar.number_input("UDP port", value=14550, step=1)
    dk = st.sidebar.text_input("DroneKit conn", value="tcp:127.0.0.1:5760")

    source = LiveSourceConfig(type=src_type, csv_path=csv_path, rate_hz=rate, udp_host=udp_host, udp_port=int(udp_port), dronekit_conn=dk)

    colA, colB = st.columns([1, 2])
    with colA:
        if not st.session_state.live_running:
            if st.button("Start"):
                st.session_state.live_running = True
                t = threading.Thread(target=_run_bg, args=(source, columns_yaml, rules_yaml, data_dir), daemon=True)
                st.session_state.live_thread = t
                t.start()
        else:
            if st.button("Stop"):
                st.session_state.live_running = False
                # thread will stop when iterator exhausts; for UDP/dronekit it runs forever; rely on user stop
    with colB:
        st.write("Connection:", "Connected" if st.session_state.live_running else "Disconnected")

    # Drain queue and update state
    drained = 0
    while not st.session_state.live_q.empty():
        pkt = st.session_state.live_q.get()
        st.session_state.live_rows.append(pkt.get("row", {}))
        st.session_state.live_results.append(pkt.get("result", {}))
        st.session_state.live_stats.update(pkt.get("stats", {}))
        drained += 1
        # cap history
    st.session_state.live_rows = st.session_state.live_rows[-2000:]
    st.session_state.live_results = st.session_state.live_results[-2000:]

    # KPIs, timeline, anomalies table
    _kpis()
    _timeline()
    st.subheader("Recent anomalies")
    _recent_table(100)
