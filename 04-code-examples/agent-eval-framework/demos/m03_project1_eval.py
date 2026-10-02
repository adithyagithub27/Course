"""Project 1 / Lecture 3.4 - Evaluate the customer support agent: 10 cases,
Answer Relevancy + Faithfulness + custom correctness, pass/fail report.

    uv run python demos/m03_project1_eval.py        # writes reports/results/project1_report.md
"""
from _common import banner

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite, save_report
from evaluators.golden import SUPPORT_CATEGORIES, load
from reports.experiments import RESULTS

banner("Project 1 - customer support agent evaluation", ["openai", "deepeval"])
report = run_suite(load("golden_support"), run_support_agent, default_metrics_for)
lines = ["# Project 1 - TechCorp support agent evaluation", "",
         f"**Result:** {report['passed']}/{report['total']} cases passed ({report['pass_rate']:.0%})", "",
         "| Category | Passed |", "|---|---|"]
for cat in SUPPORT_CATEGORIES:
    ds = [d for d in report["details"] if d["category"] == cat]
    lines.append(f"| {cat} | {sum(d['passed'] for d in ds)}/{len(ds)} |")
lines += ["", "| Metric | Average | Threshold |", "|---|---|---|"]
thr = {"Answer Relevancy": 0.7, "Faithfulness": 0.8, "Answer Correctness": 0.7}
lines += [f"| {m} | {v:.2f} | {thr[m]} |" for m, v in sorted(report["averages"].items())]
failing = [d for d in report["details"] if not d["passed"]]
lines += ["", "## Failing cases", *(f"- {d['id']}: {d['input']}" for d in failing)] if failing else ["", "No failing cases."]
md = "\n".join(lines) + "\n"
save_report(report, RESULTS / "project1_results.json")
(RESULTS / "project1_report.md").write_text(md)
print(md)
