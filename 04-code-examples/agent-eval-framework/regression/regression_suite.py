"""
Regression testing with golden datasets and stored baselines (Module 11.2).

    report = evaluate_version(run_support_agent, "golden_support")        # run + score
    save_baseline(report, "support_v1")                                   # regression/baselines/support_v1.json
    diff = compare(load_baseline("support_v1"), report, tolerance=0.05)   # deltas + verdict

A regression is: a metric average dropping more than ``tolerance`` below the
baseline, or a golden case that passed in the baseline and fails now.
The Module 11 demo simulates one by removing the grounding rule from the
system prompt (PROMPT_V2_REGRESSED).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from agents.support_agent import SYSTEM_PROMPT, run_support_agent
from config.thresholds import gates
from evaluators.deepeval_suite import default_metrics_for, run_suite
from evaluators.golden import load

BASELINE_DIR = Path(__file__).parent / "baselines"

# The "subtle prompt change": someone deletes the grounding rule.
PROMPT_V2_REGRESSED = SYSTEM_PROMPT.replace(
    "- Only state prices, limits and policies that appear in a knowledge base result\n", ""
)


def evaluate_version(agent_fn: Callable[[str], dict] = run_support_agent, dataset: str = "golden_support",
                     version: str = "v1") -> dict:
    report = run_suite(load(dataset), agent_fn, default_metrics_for)
    report["version"] = version
    report["dataset"] = dataset
    report["created_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    return report


def save_baseline(report: dict, name: str) -> Path:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    slim = {k: report.get(k) for k in ("version", "dataset", "created_at", "total", "passed", "pass_rate", "averages")}
    slim["cases"] = {d["id"]: d["passed"] for d in report["details"]}
    path = BASELINE_DIR / f"{name}.json"
    path.write_text(json.dumps(slim, indent=2))
    return path


def load_baseline(name: str) -> dict:
    return json.loads((BASELINE_DIR / f"{name}.json").read_text())


def compare(baseline: dict, current: dict, tolerance: float | None = None) -> dict:
    tolerance = gates()["regression_tolerance"] if tolerance is None else tolerance
    deltas = {}
    regressed_metrics = []
    for metric, base in baseline["averages"].items():
        now = current["averages"].get(metric)
        if base is None or now is None:
            continue
        delta = round(now - base, 3)
        deltas[metric] = {"baseline": base, "current": now, "delta": delta}
        if delta < -tolerance:
            regressed_metrics.append(metric)
    now_cases = {d["id"]: d["passed"] for d in current["details"]} if "details" in current else current.get("cases", {})
    newly_failing = [cid for cid, ok in baseline["cases"].items() if ok and not now_cases.get(cid, False)]
    return {
        "baseline_version": baseline.get("version"), "current_version": current.get("version"),
        "pass_rate": {"baseline": baseline["pass_rate"], "current": current["pass_rate"]},
        "deltas": deltas, "regressed_metrics": regressed_metrics, "newly_failing": newly_failing,
        "regression": bool(regressed_metrics or newly_failing),
    }


def regressed_agent(question: str) -> dict:
    return run_support_agent(question, system_prompt=PROMPT_V2_REGRESSED)


if __name__ == "__main__":
    base = evaluate_version(version="v1")
    print("baseline saved to", save_baseline(base, "support_v1"))
    print(json.dumps(compare(load_baseline("support_v1"), evaluate_version(regressed_agent, version="v2-regressed")), indent=2))
