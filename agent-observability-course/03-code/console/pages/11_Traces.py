"""Traces: one conversation's waterfall (2.4, 11.2 evidence 6). Open with ?trace=<id> or
pick a session."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import session_traces, top_sessions, waterfall  # noqa: E402

d, settings = page("Traces")
trace_id = st.query_params.get("trace", "")
session = st.text_input("Session id (e.g. s07-01843)", "")
if session:
    traces = session_traces(d, session)
    st.dataframe(traces, hide_index=True)
    if traces and not trace_id:
        trace_id = traces[0]["trace_id"]
if not trace_id:
    top = top_sessions(d, 10)
    choice = st.selectbox(
        "Or one of the ten most expensive conversations",
        [f"{r['session_id']}  ${r['cost_usd']:.4f}  {r['first_trace_id']}" for r in top],
    )
    trace_id = choice.split()[-1] if choice else ""
trace_id = st.text_input("Trace id", trace_id)
rows = waterfall(d, trace_id)
if not rows:
    st.warning("No spans for that trace id in this store.")
else:
    import altair as alt

    for r in rows:
        r["end_ms"] = r["start_ms"] + max(r["duration_ms"], 1.0)
    chart = (
        alt.Chart(alt.Data(values=rows))
        .mark_bar()
        .encode(
            x=alt.X("start_ms:Q", title="ms since trace start"),
            x2="end_ms:Q",
            y=alt.Y("name:N", sort=None, title=None),
            color=alt.Color("kind:N"),
            tooltip=["name:N", "kind:N", "duration_ms:Q", "status:N"],
        )
        .properties(height=max(160, 22 * len(rows)))
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(rows, hide_index=True)
