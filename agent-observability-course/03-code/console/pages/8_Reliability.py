"""Reliability: tool error share per tool and LLM retries by reason (11.2 evidence 4, 11.3)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import retries_hourly, tool_error_share_hourly  # noqa: E402

d, settings = page("Reliability")
st.subheader("Tool error share per hour")
st.line_chart(tool_error_share_hourly(d), x="hour", y="error_share", color="tool")
st.subheader("LLM retries (failed attempts) per generation, by reason")
retries = retries_hourly(d)
if retries:
    st.line_chart(retries, x="hour", y="retries_per_generation", color="reason")
    st.dataframe(retries, hide_index=True)
else:
    st.success("No failed LLM attempts in this store.")
st.caption(
    "Fallbacks and circuit-breaker state are process metrics, not span data: "
    "see atlas_model_fallbacks_total in Grafana (make stack)."
)
