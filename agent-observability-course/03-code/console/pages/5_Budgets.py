"""Budgets: cumulative spend per tenant against the soft and hard caps, EWMA anomalies (6.7)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import budget_timeline  # noqa: E402

d, settings = page("Budgets")
rows = budget_timeline(d, settings)
tenant = st.selectbox("Tenant", sorted({r["tenant"] for r in rows}) or ["ops"])
mine = [r for r in rows if r["tenant"] == tenant]
st.line_chart(mine, x="time", y=["cumulative_usd", "soft_cap_usd", "hard_cap_usd"])
st.caption("Per-5-minute spend; red rows are flagged by the EWMA detector (BudgetGuard.record).")
st.dataframe([r for r in mine if r["anomaly"]] or [{"anomaly": "none"}], hide_index=True)
st.subheader("All tenants, end of window")
last = {}
for r in rows:
    last[r["tenant"]] = r
st.dataframe(list(last.values()), hide_index=True)
