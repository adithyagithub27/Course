"""Quality: judge scores, grounded and empty-retrieval rates, feedback, disagreements (5.3, 8.x, 11.4)."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import (  # noqa: E402
    disagreements,
    feedback_by_session_length,
    feedback_hourly,
    judge_by_prompt_version,
    judge_feedback_agreement,
    judge_hourly,
    quality_summary,
    top_feedback_comments,
)

d, settings = page("Quality")
q = quality_summary(d)
if not q["judged"]:
    st.info("No scores yet: run `make judge` (or replay, which judges a sample).")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Judge overall", q["judge_means"].get("overall", "n/a"), help=f"n={q['judged']}")
c2.metric("Grounded rate", f"{q['grounded_rate']:.1%}" if q["grounded_rate"] is not None else "n/a")
c3.metric(
    "Empty retrievals",
    f"{q['empty_retrieval_rate']:.1%}" if q["empty_retrieval_rate"] is not None else "n/a",
)
pos = q["feedback_positive_share"]
c4.metric("Feedback", f"{pos:.0%} of {q['feedback_rate']:.1%}" if pos is not None else "none")

st.subheader("Judge scores per hour")
st.line_chart(judge_hourly(d), x="hour", y="mean", color="score")
st.subheader("Judge scores by prompt version")
st.dataframe(judge_by_prompt_version(d), hide_index=True)

left, right = st.columns(2)
left.subheader("Feedback rate by session length")
left.bar_chart(feedback_by_session_length(d), x="turns", y="feedback_rate")
right.subheader("Thumbs-down rate per hour")
right.line_chart(feedback_hourly(d), x="hour", y="thumbs_down_rate")

agree = judge_feedback_agreement(d)
st.subheader("Judge vs user: disagreements")
if agree["rate"] is not None:
    st.caption(f"agreement {agree['rate']:.0%} over {agree['overlap']} traces with both")
rows = disagreements(d)
for r in rows:
    r["open"] = f"./Traces?trace={r['trace_id']}"
st.dataframe(
    rows,
    hide_index=True,
    column_config={"open": st.column_config.LinkColumn("trace", display_text="open trace")},
)
st.subheader("Most common feedback comments")
st.dataframe(top_feedback_comments(d), hide_index=True)
