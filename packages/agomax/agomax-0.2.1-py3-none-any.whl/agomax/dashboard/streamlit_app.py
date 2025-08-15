import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from agomax.core.detect import fit, score

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "configs"
DATA_DIR = BASE_DIR / "data"
COLUMNS_YAML = str(CONFIG_DIR / "columns.yaml")
RULES_YAML = str(CONFIG_DIR / "rules.yaml")

st.set_page_config(page_title="AgomaX", page_icon="🛫", layout="wide")

CUSTOM_CSS = """
<style>
:root {
  --bg: #ffffff;
  --fg: #222831;
  --muted: #6b7280;
  --card: #f7f9fb;
  --accent: #0ea5a8;
  --accent2: #0284c7;
}
html, body, [class^="css"]  { font-family: 'Open Sans', Roboto, Lato, sans-serif; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.small-muted { color: var(--muted); font-size: 0.9rem; }
.kpi-card { background: var(--card); padding: 1rem 1.25rem; border-radius: 10px; border: 1px solid #eef2f7; }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: var(--fg); }
.kpi-label { font-size: 0.9rem; color: var(--muted); }
.section-title { font-weight: 700; font-size: 1.1rem; color: var(--fg); margin-top: .5rem; }
hr { border: none; border-top: 1px solid #eee; margin: 0.5rem 0 1rem; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PAGES = {
    "Home": "homepage",
    "Model & Rules Tuning": "offline",
    "Live Monitoring": "live",
}

pg = st.sidebar.radio("Navigation", list(PAGES.keys()))

if pg == "Home":
    from agomax.dashboard.pages.homepage import render as render_home
    render_home()
elif pg == "Model & Rules Tuning":
    from agomax.dashboard.pages.offline import render as render_offline
    render_offline(COLUMNS_YAML, RULES_YAML, DATA_DIR)
else:
    from agomax.dashboard.pages.live import render as render_live
    render_live(COLUMNS_YAML, RULES_YAML, DATA_DIR)
