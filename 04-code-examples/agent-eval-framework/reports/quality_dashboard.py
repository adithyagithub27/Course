"""
Agent quality dashboard (Module 12.3, capstone "dashboard reveal").

    make dashboard        # streamlit run reports/quality_dashboard.py
    python reports/quality_dashboard.py --text    # same numbers in the terminal

Reads what the pipeline writes to reports/results/:
    eval.json            latest golden-dataset report (python -m reports.run_eval)
    experiments.jsonl    run history (reports/experiments.py)
    redteam.json         latest red-team report (capstone)
If nothing is there yet it runs the offline evaluation once to create eval.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from reports.experiments import RESULTS, runs  # noqa: E402


def load_latest() -> dict:
    p = RESULTS / "eval.json"
    if not p.exists():
        from reports.run_eval import main as run_eval

        run_eval(["--out", str(p)])
    return json.loads(p.read_text())


def category_table(report: dict) -> list[dict]:
    cats: dict[str, list[dict]] = {}
    for d in report["details"]:
        cats.setdefault(d.get("category") or "uncategorized", []).append(d)
    return [{"category": c, "cases": len(v), "passed": sum(x["passed"] for x in v),
             "pass_rate": round(sum(x["passed"] for x in v) / len(v), 2)} for c, v in cats.items()]


def gate_status(report: dict) -> str:
    from reports.quality_gate import evaluate_gate

    ok, _ = evaluate_gate(report)
    return "PASS" if ok else "BLOCKED"


def render_text() -> None:
    r = load_latest()
    print(f"Quality gate: {gate_status(r)}   pass rate {r['pass_rate']:.0%} ({r['passed']}/{r['total']})")
    for m, v in r["averages"].items():
        print(f"  {m:<20} {v:.2f}")
    for row in category_table(r):
        print(f"  {row['category']:<12} {row['passed']}/{row['cases']}")
    hist = runs()
    if hist:
        print("History:", ", ".join(f"{h['version']}={h['pass_rate']:.0%}" for h in hist))


def render_streamlit() -> None:
    import pandas as pd
    import streamlit as st

    st.set_page_config(page_title="Agent Quality Dashboard", layout="wide")
    st.title("TechCorp Agent Quality Dashboard")
    r = load_latest()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quality gate", gate_status(r))
    c2.metric("Pass rate", f"{r['pass_rate']:.0%}", help=f"{r['passed']}/{r['total']} golden cases")
    c3.metric("Faithfulness", f"{r['averages'].get('Faithfulness', 0):.2f}")
    c4.metric("Answer relevancy", f"{r['averages'].get('Answer Relevancy', 0):.2f}")

    st.subheader("By category")
    st.dataframe(pd.DataFrame(category_table(r)), use_container_width=True)

    hist = runs()
    if hist:
        st.subheader("Trend across versions")
        df = pd.DataFrame([{"version": h["version"], "pass_rate": h["pass_rate"], **h["averages"]} for h in hist]).set_index("version")
        st.line_chart(df)

    rt = RESULTS / "redteam.json"
    if rt.exists():
        st.subheader("Security (red team)")
        red = json.loads(rt.read_text())
        st.write(f"{red['passed']}/{red['total']} attacks blocked; open findings by severity: {red['by_severity']}")

    st.subheader("Case details")
    st.dataframe(pd.DataFrame([{"id": d["id"], "category": d["category"], "passed": d["passed"], "tools": ", ".join(d["tools"]),
                                **{k: v["score"] for k, v in d["metrics"].items()}} for d in r["details"]]), use_container_width=True)
    st.caption("Offline runs use the mock LLM and mock judge; live runs use gpt-4.1-mini (agent) and gpt-4.1 (judge).")


if __name__ == "__main__":
    if "--text" in sys.argv:
        render_text()
    else:
        render_streamlit()
