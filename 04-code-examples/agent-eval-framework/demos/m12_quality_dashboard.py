"""Lecture 12.3 - Quality dashboard: write fresh results, then launch Streamlit.

    uv run python demos/m12_quality_dashboard.py      # text summary
    make dashboard                                    # the Streamlit app
"""
from _common import banner

from reports.quality_dashboard import render_text
from reports.run_eval import main as run_eval

banner("Lecture 12.3 - quality dashboard", ["openai", "deepeval", "streamlit"])
run_eval(["--out", "reports/results/eval.json"])
render_text()
print("\nLaunch the app: uv run streamlit run reports/quality_dashboard.py  (or: make dashboard)")
