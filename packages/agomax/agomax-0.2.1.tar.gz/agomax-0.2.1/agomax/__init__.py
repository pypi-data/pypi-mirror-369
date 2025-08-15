
"""AgomaX package (Phase 1 & 2, Dashboard and API modes)."""

import subprocess
import sys
from pathlib import Path

def dashboard(port=8501, theme=None, debug=False):
	"""Launch the AgomaX Streamlit dashboard. Optional: port, theme, debug."""
	try:
		import streamlit  # noqa: F401
	except ImportError:
		print("Streamlit is not installed. Please run: pip install streamlit", file=sys.stderr)
		return
	base = Path(__file__).resolve().parent
	app_path = base / "dashboard" / "streamlit_app.py"
	if not app_path.exists():
		print(f"Dashboard app not found at {app_path}", file=sys.stderr)
		return
	cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)]
	if theme:
		cmd += ["--theme.base", theme]
	if debug:
		cmd += ["--logger.level", "debug"]
	subprocess.run(cmd, check=True)
