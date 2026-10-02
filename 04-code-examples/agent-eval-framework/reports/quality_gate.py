"""
CI quality gate (Module 12.1-12.2): read an evaluation report, apply the gates
from config/eval_config.yaml, write a markdown summary for the PR comment, and
exit non-zero to block the merge.

    python -m reports.quality_gate reports/results/eval.json --summary reports/results/summary.md

Gates: pass rate >= gates.pr_pass_rate (80%) and every critical metric average
>= gates.critical_metric_min (0.7). Optional --baseline compares with a stored
baseline (regression tolerance 5 points).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config.thresholds import gates

CRITICAL = ["Faithfulness", "Answer Correctness", "Answer Relevancy"]


def evaluate_gate(report: dict, min_pass_rate: float | None = None, critical_min: float | None = None) -> tuple[bool, list[str]]:
    g = gates()
    min_pass_rate = g["pr_pass_rate"] if min_pass_rate is None else min_pass_rate
    critical_min = g["critical_metric_min"] if critical_min is None else critical_min
    reasons = []
    if report["pass_rate"] < min_pass_rate:
        reasons.append(f"pass rate {report['pass_rate']:.0%} < {min_pass_rate:.0%}")
    for m in CRITICAL:
        v = report["averages"].get(m)
        if v is not None and v < critical_min:
            reasons.append(f"{m} average {v:.2f} < {critical_min:.2f}")
    return (not reasons, reasons)


def markdown_summary(report: dict, ok: bool, reasons: list[str], regression: dict | None = None) -> str:
    lines = [f"## Agent quality gate: {'PASSED' if ok else 'FAILED'}", "",
             f"**Pass rate:** {report['passed']}/{report['total']} ({report['pass_rate']:.0%})", "",
             "| Metric | Average |", "|---|---|"]
    lines += [f"| {m} | {v:.2f} |" for m, v in sorted(report["averages"].items()) if v is not None]
    if reasons:
        lines += ["", "**Blocking issues:**"] + [f"- {r}" for r in reasons]
    failing = [d for d in report.get("details", []) if not d["passed"]]
    if failing:
        lines += ["", "<details><summary>Failing cases</summary>", ""]
        for d in failing:
            worst = min(((k, v["score"]) for k, v in d["metrics"].items() if v["score"] is not None), key=lambda x: x[1], default=("tools", 0))
            lines.append(f"- `{d['id']}` {d['input'][:70]!r}: lowest {worst[0]} = {worst[1]}" + ("" if d.get("tools_ok", True) else f", tools {d['tools']}"))
        lines += ["", "</details>"]
    if regression:
        lines += ["", f"**Regression vs baseline:** {'YES' if regression['regression'] else 'no'}"]
        for m, d in regression["deltas"].items():
            lines.append(f"- {m}: {d['baseline']:.2f} -> {d['current']:.2f} ({d['delta']:+.2f})")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--summary", default=None)
    ap.add_argument("--baseline", default=None, help="baseline name in regression/baselines")
    a = ap.parse_args(argv)
    report = json.loads(Path(a.report).read_text())
    ok, reasons = evaluate_gate(report)
    regression = None
    if a.baseline:
        from regression.regression_suite import compare, load_baseline

        regression = compare(load_baseline(a.baseline), report)
        if regression["regression"]:
            ok = False
            reasons.append("regression vs baseline: " + ", ".join(regression["regressed_metrics"] + regression["newly_failing"]))
    md = markdown_summary(report, ok, reasons, regression)
    if a.summary:
        Path(a.summary).parent.mkdir(parents=True, exist_ok=True)
        Path(a.summary).write_text(md)
    print(md)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
