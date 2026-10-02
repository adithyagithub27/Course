"""Live cost (Lecture 1.1): the meter, the steps counter, the context sparkline, live alerts.

Run a conversation while this page is open, for example
``ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 PACE=0.1 make loop-demo``; spans reach the store
step by step and the page refreshes every two seconds.
"""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import money, store_path  # noqa: E402
from console.data import StoreData, live  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402

st.set_page_config(page_title="Atlas Ops Console: Live cost", layout="wide")
st.title("Live cost")
path = store_path()
window_min = st.sidebar.slider("Window (minutes)", 1, 60, 15)


@st.fragment(run_every=2)
def meter() -> None:
    store = LocalSpanStore(path)
    d = StoreData.load(store)
    store.close()
    v = live(d, window_s=window_min * 60)
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.metric(f"Spend, last {window_min} min", money(v["total_cost_usd"], 2))
    c2.metric("Steps (latest conversation)", v["steps"])
    c3.metric("Latest conversation cost", money(v["trace_cost_usd"], 4))
    st.dataframe(
        [{"tenant": t, "cost_usd": c} for t, c in v["cost_by_tenant"].items()],
        hide_index=True,
    )
    left, right = st.columns(2)
    left.caption("Context size: input tokens per model call, latest conversation")
    left.line_chart({"input tokens": v["context_tokens"]}, height=180)
    right.caption("Cost so far, latest conversation (USD)")
    right.line_chart({"cumulative cost": v["cost_sparkline"]}, height=180)
    st.subheader("Alerts")
    if v["alerts"]:
        st.dataframe(v["alerts"], hide_index=True)
    else:
        st.success("No alerts")
    st.caption(f"latest trace: {v['latest_trace_id']}  tenant: {v['latest_tenant']}")


meter()
