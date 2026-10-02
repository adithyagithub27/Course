"""
Run the golden-dataset evaluation and write a JSON report (used by CI and `make eval`).

    python -m reports.run_eval --dataset golden_support --out reports/results/eval.json
    python -m reports.run_eval --smoke            # 3-case smoke subset (every push)
    python -m reports.run_eval --prompt-variant regressed   # the Module 11/12 "bad change"
"""

from __future__ import annotations

import argparse

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite, save_report
from evaluators.golden import load
from regression.regression_suite import regressed_agent

SMOKE_IDS = ["GS-01", "GS-05", "GS-10"]  # one FAQ, one account action, one security case


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="golden_support")
    ap.add_argument("--out", default="reports/results/eval.json")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--prompt-variant", choices=["v1", "regressed"], default="v1")
    a = ap.parse_args(argv)
    cases = load(a.dataset)
    if a.smoke:
        cases = [c for c in cases if c["id"] in SMOKE_IDS]
    agent = regressed_agent if a.prompt_variant == "regressed" else run_support_agent
    report = run_suite(cases, agent, default_metrics_for)
    report["dataset"] = a.dataset
    report["prompt_variant"] = a.prompt_variant
    path = save_report(report, a.out)
    print(f"{report['passed']}/{report['total']} passed ({report['pass_rate']:.0%}); averages {report['averages']}; wrote {path}")
    return report


if __name__ == "__main__":
    main()
