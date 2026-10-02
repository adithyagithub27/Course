"""Cost: showback by tenant and feature, unit costs, top-10 conversations (2.4, 6.x, 11.2)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import money, page  # noqa: E402
from console.data import (  # noqa: E402
    cost_by,
    cost_tiles,
    hourly_cost_by_tenant,
    hourly_unit_costs,
    top_sessions,
)

d, settings = page("Cost")
t = cost_tiles(d)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total cost", money(t["total_cost_usd"]))
c2.metric("Cost / session", money(t["cost_per_session_usd"], 4))
c3.metric("Cost / resolved session", money(t["cost_per_resolved_session_usd"], 4))
c4.metric("Cache hit ratio", f"{t['cache_hit_ratio']:.0%}")

left, right = st.columns(2)
left.subheader("By tenant")
by_tenant = cost_by(d, "tenant")
left.bar_chart(by_tenant, x="key", y="cost_usd", horizontal=True)
right.subheader("By feature")
by_feature = cost_by(d, "feature")
right.bar_chart(by_feature, x="key", y="cost_usd", horizontal=True)
st.dataframe(by_feature, hide_index=True)

st.subheader("Cost per hour by tenant")
st.bar_chart(hourly_cost_by_tenant(d), x="hour", y="cost_usd", color="tenant")

st.subheader("Unit costs per hour")
tenant = st.selectbox("Tenant", ["all", "ops", "finance", "hr", "eng"])
unit = hourly_unit_costs(d, tenant)
a, b = st.columns(2)
a.line_chart(unit, x="hour", y=["cost_per_session_usd"])
b.line_chart(
    unit, x="hour", y=["mean_input_tokens_per_generation", "mean_output_tokens_per_generation"]
)

st.subheader("Ten most expensive conversations")
rows = top_sessions(d, 10)
for r in rows:
    r["open"] = f"./Traces?trace={r['first_trace_id']}"
st.dataframe(
    rows,
    hide_index=True,
    column_order=[
        "session_id",
        "tenant",
        "feature",
        "turns",
        "steps",
        "cost_usd",
        "outcomes",
        "open",
    ],
    column_config={"open": st.column_config.LinkColumn("trace", display_text="open trace")},
)
