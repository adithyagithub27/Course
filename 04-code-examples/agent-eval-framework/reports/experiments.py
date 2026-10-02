"""
Experiment tracking (Module 12.3): store each evaluation run, compare two.

    log_run(report, version="v1.3")                 # appends reports/results/experiments.jsonl
    compare_runs("v1.2", "v1.3") -> per-metric deltas, pass-rate delta, improved/regressed lists
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

RESULTS = Path(__file__).parent / "results"
EXPERIMENTS = RESULTS / "experiments.jsonl"


def log_run(report: dict, version: str, notes: str = "", path: Path = EXPERIMENTS) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"version": version, "ts": datetime.now(UTC).isoformat(timespec="seconds"), "notes": notes,
           "pass_rate": report["pass_rate"], "averages": report["averages"], "total": report["total"],
           "categories": _by_category(report)}
    with path.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def _by_category(report: dict) -> dict[str, float]:
    cats: dict[str, list[bool]] = {}
    for d in report.get("details", []):
        cats.setdefault(d.get("category") or "uncategorized", []).append(d["passed"])
    return {c: round(sum(v) / len(v), 3) for c, v in cats.items()}


def runs(path: Path = EXPERIMENTS) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def compare_runs(a: str, b: str, path: Path = EXPERIMENTS) -> dict:
    by_version = {r["version"]: r for r in runs(path)}
    ra, rb = by_version[a], by_version[b]
    deltas = {m: round(rb["averages"].get(m, 0) - v, 3) for m, v in ra["averages"].items() if v is not None}
    return {"a": a, "b": b, "pass_rate": (ra["pass_rate"], rb["pass_rate"]),
            "pass_rate_delta": round(rb["pass_rate"] - ra["pass_rate"], 3), "metric_deltas": deltas,
            "improved": [m for m, d in deltas.items() if d > 0.01], "regressed": [m for m, d in deltas.items() if d < -0.01]}
