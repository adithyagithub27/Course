"""Lecture 11.1/11.2 - Regression simulation: delete one rule from the system
prompt, re-run the golden suite, watch the scores drop and the gate fire.

    uv run python demos/m11_regression_simulation.py
"""
from _common import banner, table

from regression.regression_suite import compare, evaluate_version, load_baseline, regressed_agent

banner("Lecture 11.1 - regression simulation")
current = evaluate_version(regressed_agent, version="v2 (grounding rule deleted)")
diff = compare(load_baseline("support_v1"), current)
table([{"metric": m, **{k: f"{v:+.2f}" if k == "delta" else f"{v:.2f}" for k, v in d.items()}} for m, d in diff["deltas"].items()])
print(f"\nPass rate: {diff['pass_rate']['baseline']:.0%} -> {diff['pass_rate']['current']:.0%}")
print(f"Regressed metrics (> 5 points): {diff['regressed_metrics']}")
print(f"Cases that passed before and fail now: {diff['newly_failing']}")
for d in current["details"]:
    if d["id"] in diff["newly_failing"]:
        print(f"  {d['id']}: {d['output'][:90]}")
print(f"\nREGRESSION DETECTED: {diff['regression']}")
