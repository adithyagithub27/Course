"""Lecture 12.1/12.2 - The quality gate in action: a good change passes, a bad
prompt change is blocked, and the PR comment explains why. CI runs the same
commands (.github/workflows/agent-eval.yml).

    uv run python demos/m12_quality_gate.py
"""
from _common import banner

from reports.quality_gate import evaluate_gate, markdown_summary
from reports.run_eval import main as run_eval
from regression.regression_suite import compare, load_baseline

banner("Lecture 12.2 - quality gate")
for label, variant in (("PR #41: copy edits (good change)", "v1"), ("PR #42: 'simplify' the system prompt (bad change)", "regressed")):
    report = run_eval(["--prompt-variant", variant, "--out", f"reports/results/eval_{variant}.json"])
    ok, reasons = evaluate_gate(report)
    reg = compare(load_baseline("support_v1"), report)
    if reg["regression"]:
        ok = False
        reasons.append("regression vs baseline: " + ", ".join(reg["regressed_metrics"] + reg["newly_failing"]))
    print(f"\n===== {label}: {'MERGE ALLOWED' if ok else 'MERGE BLOCKED'} =====")
    print(markdown_summary(report, ok, reasons, reg))
