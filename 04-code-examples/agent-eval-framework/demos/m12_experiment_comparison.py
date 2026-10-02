"""Lecture 12.3 - Experiment comparison: v1.2 vs v1.3 side by side.

    uv run python demos/m12_experiment_comparison.py
"""
from _common import banner

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite
from evaluators.golden import load
from regression.regression_suite import regressed_agent
from reports.experiments import RESULTS, compare_runs, log_run

banner("Lecture 12.3 - experiment comparison")
path = RESULTS / "experiments_demo.jsonl"
path.unlink(missing_ok=True)
cases = load("golden_support")
log_run(run_suite(cases, regressed_agent, default_metrics_for), "v1.2", "shorter prompt", path=path)
log_run(run_suite(cases, run_support_agent, default_metrics_for), "v1.3", "grounding rule restored", path=path)
c = compare_runs("v1.2", "v1.3", path=path)
print(f"Pass rate: v1.2 {c['pass_rate'][0]:.0%} -> v1.3 {c['pass_rate'][1]:.0%} ({c['pass_rate_delta']:+.0%})")
for m, d in c["metric_deltas"].items():
    print(f"  {m:<20} {d:+.3f}")
print(f"Improved: {c['improved']}  Regressed: {c['regressed']}")
