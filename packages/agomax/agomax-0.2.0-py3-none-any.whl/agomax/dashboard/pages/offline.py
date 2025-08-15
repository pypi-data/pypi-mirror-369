import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from io import StringIO
import json
import altair as alt

from agomax.core.detect import fit, score


def _init_session():
    if "pack" not in st.session_state:
        st.session_state.pack = None
    if "base_df" not in st.session_state:
        st.session_state.base_df = None
    if "results" not in st.session_state:
        st.session_state.results = None
    if "data_df" not in st.session_state:
        st.session_state.data_df = None
    if "default_thresholds" not in st.session_state:
        st.session_state.default_thresholds = None
    if "baseline_results" not in st.session_state:
        st.session_state.baseline_results = None
    if "last_anomaly_count" not in st.session_state:
        st.session_state.last_anomaly_count = None
    if "current_anomaly_count" not in st.session_state:
        st.session_state.current_anomaly_count = None
    if "anomaly_rate_history" not in st.session_state:
        st.session_state.anomaly_rate_history = []


def _kpi_cards(df: pd.DataFrame, results: pd.DataFrame):
    total = len(df)
    anomalies = int(results["anomaly"].sum()) if results is not None else 0
    rate = (anomalies / total * 100.0) if total > 0 else 0.0
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='kpi-card'><div class='kpi-value'>%d</div><div class='kpi-label'>Total rows</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{anomalies}</div><div class='kpi-label'>Anomalies</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{rate:.2f}%</div><div class='kpi-label'>Anomaly rate</div></div>", unsafe_allow_html=True)


def _timeline(df: pd.DataFrame, results: pd.DataFrame):
    if results is None or df is None or len(df) == 0:
        return
    chart_df = pd.DataFrame({
        "index": np.arange(len(df)),
        "status": results["anomaly"].map({0: "Normal", 1: "Anomaly"}),
        "value": 1,
    })
    color_scale = alt.Scale(domain=["Normal", "Anomaly"], range=["#10b981", "#ef4444"])  # green/red
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("index:Q", title="Index"),
            y=alt.Y("value:Q", axis=None),
            color=alt.Color("status:N", scale=color_scale, title="Status"),
            tooltip=["index", "status"],
        )
        .properties(height=120)
    )
    st.altair_chart(chart, use_container_width=True)


def _results_table(df: pd.DataFrame, results: pd.DataFrame):
    if results is None:
        return
    display = df.copy()
    display["anomaly"] = results["anomaly"].astype(int)
    display["vote"] = results["vote"].astype(int)
    display["rule_violations"] = results["rule_violations"].astype(int)
    st.dataframe(display, use_container_width=True)


def render(columns_yaml: str, rules_yaml: str, data_dir: Path):
    _init_session()
    st.header("Model & Rules Tuning")

    st.sidebar.subheader("Thresholds")
    # Optional thresholds: empty -> auto
    def _parse_optional_float(label: str, help: str | None = None):
        txt = st.sidebar.text_input(label, value="", placeholder="auto", help=help)
        try:
            return float(txt) if txt.strip() != "" else None
        except ValueError:
            st.sidebar.warning(f"Invalid number for {label}; using auto")
            return None

    kmeans_distance = _parse_optional_float("KMeans distance", "Override dynamic default")
    lof_score = _parse_optional_float("LOF score threshold")
    ocsvm_score = _parse_optional_float("OCSVM score threshold")
    dbscan_eps = st.sidebar.number_input("DBSCAN eps", value=0.78, step=0.01)
    dbscan_min = st.sidebar.number_input("DBSCAN min_samples", value=5, step=1)
    optics_min = st.sidebar.number_input("OPTICS min_samples", value=50, step=1)
    rules_sens = st.sidebar.slider("Rules sensitivity", min_value=0.0, max_value=0.5, value=0.0, step=0.01)

    st.write("Upload a base CSV or use the sample to initialize models.")
    c1, c2 = st.columns(2)
    with c1:
        base_file = st.file_uploader("Base CSV (model initialization)", type=["csv"], key="base")
        if st.button("Use sample base.csv"):
            sample = data_dir / "base.csv"
            if sample.exists():
                st.session_state.base_df = pd.read_csv(sample)
            else:
                st.warning("Sample not found.")
        if base_file is not None:
            st.session_state.base_df = pd.read_csv(base_file)

    with c2:
        data_file = st.file_uploader("Data CSV (to score)", type=["csv"], key="data")
        if st.button("Load sample as data"):
            sample = data_dir / "base.csv"
            if sample.exists():
                st.session_state.data_df = pd.read_csv(sample)
            else:
                st.warning("Sample not found.")
        if data_file is not None:
            st.session_state.data_df = pd.read_csv(data_file)

    # Training options
    with st.expander("Training options"):
        scale_features = st.checkbox("Scale features (StandardScaler)", value=False)
        mode = st.selectbox("Threshold mode", ["percentile", "mad"], index=0, help="99.7th percentile or median ± k*MAD")
        mad_k = st.number_input("MAD k", value=3.0, step=0.5)

    if st.button("Run detection"):
        if st.session_state.base_df is None or st.session_state.data_df is None:
            st.error("Please provide both base and data CSVs (or use samples).")
        else:
            pack, base_full, base_feats = fit(
                st.session_state.base_df,
                columns_yaml,
                params={
                    "scale_features": scale_features,
                    "threshold_mode": mode,
                    "mad_k": mad_k,
                },
            )
            st.session_state.pack = pack
            st.session_state.default_thresholds = pack.thresholds["values"].copy()
            res = score(
                pack,
                st.session_state.data_df,
                columns_yaml,
                rules_yaml,
                thresholds={
                    "kmeans_distance": kmeans_distance,
                    "lof_score": lof_score,
                    "ocsvm_score": ocsvm_score,
                    "dbscan_eps": dbscan_eps,
                    "dbscan_min_samples": dbscan_min,
                    "optics_min_samples": optics_min,
                },
                rules_sensitivity=rules_sens,
            )
            st.session_state.results = res
            st.session_state.baseline_results = res.copy()
            st.session_state.last_anomaly_count = int(res["anomaly"].sum())
            st.session_state.current_anomaly_count = st.session_state.last_anomaly_count

    # Restore defaults button
    if st.session_state.default_thresholds is not None:
        if st.sidebar.button("Restore defaults"):
            kmeans_distance = st.session_state.default_thresholds.get("kmeans")
            lof_score = st.session_state.default_thresholds.get("lof")
            ocsvm_score = st.session_state.default_thresholds.get("ocsvm")

    # Instant auto-rescore on every rerun when pack and data are available
    if st.session_state.pack is not None and st.session_state.data_df is not None:
        res_new = score(
            st.session_state.pack,
            st.session_state.data_df,
            columns_yaml,
            rules_yaml,
            thresholds={
                "kmeans_distance": kmeans_distance,
                "lof_score": lof_score,
                "ocsvm_score": ocsvm_score,
                "dbscan_eps": dbscan_eps,
                "dbscan_min_samples": dbscan_min,
                "optics_min_samples": optics_min,
            },
            rules_sensitivity=rules_sens,
        )
        last = st.session_state.current_anomaly_count
        cur = int(res_new["anomaly"].sum())
        st.session_state.results = res_new
        st.session_state.last_anomaly_count = last
        st.session_state.current_anomaly_count = cur
        # Update trend history (cap to last 20)
        total = len(st.session_state.data_df) or 1
        rate = (cur / total) * 100.0
        st.session_state.anomaly_rate_history.append(rate)
        st.session_state.anomaly_rate_history = st.session_state.anomaly_rate_history[-20:]

    if st.session_state.results is not None:
        st.subheader("KPIs")
        _kpi_cards(st.session_state.data_df, st.session_state.results)
        # Delta message
        if st.session_state.last_anomaly_count is not None and st.session_state.current_anomaly_count is not None:
            la = st.session_state.last_anomaly_count
            ca = st.session_state.current_anomaly_count
            diff = ca - la
            if diff > 0:
                st.markdown(f"<span style='color:#ef4444'>Anomalies changed: {la} → {ca} (+{diff})</span>", unsafe_allow_html=True)
            elif diff < 0:
                st.markdown(f"<span style='color:#10b981'>Anomalies changed: {la} → {ca} ({diff})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#6b7280'>Anomalies changed: {la} → {ca} (0)</span>", unsafe_allow_html=True)

        # Sparkline trend next to KPIs
        hist = st.session_state.anomaly_rate_history
        if hist:
            hist_df = pd.DataFrame({"step": list(range(max(0, len(hist)-20), len(hist))), "rate": hist})
            spark = alt.Chart(hist_df).mark_line(point=False).encode(
                x=alt.X("step:Q", axis=None),
                y=alt.Y("rate:Q", axis=None),
                color=alt.value("#0284c7"),
            ).properties(height=40)
            st.altair_chart(spark, use_container_width=True)
        # Before/After toggle
        show_compare = st.toggle("Show Before/After View", value=False)
        st.subheader("Timeline")
        if show_compare and st.session_state.baseline_results is not None:
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Before (defaults)")
                _timeline(st.session_state.data_df, st.session_state.baseline_results)
            with c2:
                st.caption("After (current)")
                _timeline(st.session_state.data_df, st.session_state.results)
        else:
            _timeline(st.session_state.data_df, st.session_state.results)

        # Rule violations charts
        st.subheader("Rule violations")
        rv = st.session_state.results["rule_violations"].astype(int)
        dist_df = rv.value_counts().sort_index().reset_index()
        dist_df.columns = ["violations", "count"]
        bar = alt.Chart(dist_df).mark_bar().encode(
            x=alt.X("violations:O", title="Violations per row"),
            y=alt.Y("count:Q", title="Count"),
            color=alt.value("#6b7280"),
            tooltip=["violations", "count"],
        ).properties(height=150)
        st.altair_chart(bar, use_container_width=True)

        heat_df = pd.DataFrame({
            "index": np.arange(len(rv)),
            "violations": rv,
        })
        heat = alt.Chart(heat_df).mark_rect().encode(
            x=alt.X("index:Q", title="Index"),
            y=alt.Y("violations:Q", title="Violations", bin=alt.Bin(maxbins=20)),
            color=alt.Color("count():Q", scale=alt.Scale(scheme="blues"), title="Density"),
            tooltip=["index", "violations"],
        ).properties(height=180)
        st.altair_chart(heat, use_container_width=True)

        st.subheader("Results")
        _results_table(st.session_state.data_df, st.session_state.results)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="Download results.csv",
                data=st.session_state.results.to_csv(index=False),
                file_name="results.csv",
                mime="text/csv",
            )
        with c2:
            st.download_button(
                label="Download results.json",
                data=st.session_state.results.to_json(orient="records"),
                file_name="results.json",
                mime="application/json",
            )
