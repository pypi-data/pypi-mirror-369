import streamlit as st


def render():
    st.title("AgomaX")
    st.markdown(
        """
        <div class="small-muted">Intelligent Offline Anomaly Detection for Drone Telemetry</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    AgomaX is a modular toolkit for detecting anomalies in drone telemetry data using an ensemble of unsupervised models combined with a configurable rules engine. This dashboard focuses on Offline Mode, where you can upload a static CSV, tune thresholds, and export results.
    """)

    st.markdown("## Uses of this Dashboard")
    st.markdown(
        """
        - Offline analysis of recorded flights using multiple anomaly detectors (KMeans, LOF, One-Class SVM, DBSCAN, OPTICS)
        - Threshold tuning with immediate feedback—no retraining required
        - Rules-based validation using YAML-configured constraints
        - Export anomalies to CSV or JSON for reporting
        """
    )

    st.info("This is Phase 1: Offline Mode and threshold tuning only. Live mode and other features will come later.")
