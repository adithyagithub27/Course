"""Retrieval: top_k, hits and result size in tokens by tenant (5.3, 11.2 evidence 5)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import retrieval_hourly  # noqa: E402

d, settings = page("Retrieval")
rows = retrieval_hourly(d)
st.subheader("atlas.retrieval.top_k by tenant")
st.line_chart(rows, x="hour", y="mean_top_k", color="tenant")
st.subheader("Retriever result size (tokens sent to the model) by tenant")
st.line_chart(rows, x="hour", y="mean_result_tokens", color="tenant")
st.subheader("Empty retrievals by tenant")
st.line_chart(rows, x="hour", y="empty_share", color="tenant")
st.dataframe(rows, hide_index=True)
