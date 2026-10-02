"""Safety: injection, refusal and PII-in-output rates per hour (8.4)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import safety_hourly  # noqa: E402

d, settings = page("Safety")
rows = safety_hourly(d)
st.line_chart(rows, x="hour", y=["injection_rate", "refusal_rate", "pii_in_output_rate"])
st.dataframe(rows, hide_index=True)
