"""Latency: p50/p95/p99, hourly percentiles with the 4 s budget, span and TTFT detail (7.x, 11.3)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import (  # noqa: E402
    generation_timing_hourly,
    hourly_latency,
    latency_summary,
    span_p95_by_type_hourly,
)

d, settings = page("Latency")
s = latency_summary(d)
c1, c2, c3, c4 = st.columns(4)
c1.metric("p50", f"{s['total']['p50']:.0f} ms")
c2.metric(
    "p95", f"{s['total']['p95']:.0f} ms", help=f"budget {settings.budget_p95_latency_ms:.0f} ms"
)
c3.metric("p99", f"{s['total']['p99']:.0f} ms")
c4.metric("TTFT p95 (final answer)", f"{s['ttft']['p95']:.0f} ms")

st.subheader("End-to-end p50 / p95 per hour")
rows = hourly_latency(d)
for r in rows:
    r["budget_ms"] = settings.budget_p95_latency_ms
st.line_chart(rows, x="hour", y=["p50_ms", "p95_ms", "budget_ms"])

st.subheader("Span duration p95 by observation type")
st.line_chart(span_p95_by_type_hourly(d), x="hour", y="p95_ms", color="type")

st.subheader("Generation detail: atlas.ttft_ms p95 and duration p95")
st.line_chart(generation_timing_hourly(d), x="hour", y=["ttft_p95_ms", "generation_p95_ms"])
