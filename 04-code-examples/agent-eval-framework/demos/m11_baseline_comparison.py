"""Lecture 11.2 - Baseline comparison: store a baseline, compare a new version,
gate on deltas.

    uv run python demos/m11_baseline_comparison.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from regression.regression_suite import compare, evaluate_version, load_baseline, save_baseline

banner("Lecture 11.2 - baseline comparison")
baseline = evaluate_version(run_support_agent, version="v1.0")
path = save_baseline(baseline, "support_v1")
print(f"Baseline stored: {path.name}  pass rate {baseline['pass_rate']:.0%}  {baseline['averages']}")
candidate = evaluate_version(lambda q: run_support_agent(q, temperature=1.0), version="v1.1 (temperature 1.0)")
diff = compare(load_baseline("support_v1"), candidate, tolerance=0.05)
table([{"metric": m, "baseline": d["baseline"], "candidate": d["current"], "delta": f"{d['delta']:+.3f}",
        "gate": "FAIL" if m in diff["regressed_metrics"] else "ok"} for m, d in diff["deltas"].items()])
print(f"\nCandidate {'BLOCKED' if diff['regression'] else 'approved'}: regressed={diff['regressed_metrics']}, newly failing={diff['newly_failing']}")
