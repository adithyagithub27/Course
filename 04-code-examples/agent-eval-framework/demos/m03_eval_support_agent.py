"""Lecture 3.3 - Running your first agent eval end to end: 10 golden cases,
three metrics, a results table.

    uv run python demos/m03_eval_support_agent.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite
from evaluators.golden import load

banner("Lecture 3.3 - evaluate the support agent", ["openai", "deepeval"])
report = run_suite(load("golden_support"), run_support_agent, default_metrics_for)
rows = []
for d in report["details"]:
    s = {k: v["score"] for k, v in d["metrics"].items()}
    rows.append({"id": d["id"], "category": d["category"], "relevancy": s.get("Answer Relevancy"),
                 "faithful": s.get("Faithfulness", "-"), "correct": s.get("Answer Correctness"),
                 "tools_ok": d["tools_ok"], "result": "PASS" if d["passed"] else "FAIL"})
table(rows)
print(f"\n{report['passed']}/{report['total']} passed ({report['pass_rate']:.0%}). Averages: {report['averages']}")
