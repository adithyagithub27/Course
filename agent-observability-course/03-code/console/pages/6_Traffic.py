"""Traffic: requests per minute by tenant with last week's shadow line (11.2 evidence 2)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import shadow_traffic, traffic  # noqa: E402

d, settings = page("Traffic")
bin_s = st.sidebar.selectbox("Bin", [60, 300, 900], format_func=lambda s: f"{s // 60} min")
tenant = st.selectbox("Tenant", ["ops", "finance", "hr", "eng"])
now = {r["ts"]: r["requests"] for r in traffic(d, bin_s=bin_s) if r["tenant"] == tenant}
shadow = shadow_traffic(d, bin_s=bin_s)
prev = {r["ts"]: r["requests"] for r in shadow["rows"] if r["tenant"] == tenant}
keys = sorted(set(now) | set(prev))
st.line_chart(
    {
        "this day": [now.get(k, 0) for k in keys],
        f"shadow ({shadow['source']})": [prev.get(k, 0) for k in keys],
    }
)
st.caption(
    "Shadow = the same tenant one week earlier when the store holds it "
    "(make replay DAY=2026-09-07 KEEP=1); otherwise the replayed traffic plan of the previous seed."
)
