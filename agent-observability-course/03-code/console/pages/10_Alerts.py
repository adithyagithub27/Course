"""Alerts: the console's batch rules over the whole store, plus SLOs and budgets."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.ops_console import build_summary  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402

d, settings = page("Alerts")
store = LocalSpanStore(d.path)
s = build_summary(store, settings)
store.close()
if s["alerts"]:
    st.dataframe(s["alerts"], hide_index=True)
else:
    st.success("No alerts")
st.subheader("SLOs")
st.dataframe(s["slos"], hide_index=True)
st.subheader("Budgets")
st.dataframe(s["budgets"], hide_index=True)
