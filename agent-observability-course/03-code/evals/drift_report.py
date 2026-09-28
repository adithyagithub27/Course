"""Weekly drift report: compare the current window with a baseline (Section 8.5).

Offline usage (no store needed)::

    python evals/drift_report.py                      # synthetic: v1 baseline vs v2 (quality_drift) current
    python evals/drift_report.py --store .atlas/spans.sqlite --split-hour 12

Metrics compared: judge scores (overall / grounded / resolved), cost per request,
latency, steps, cache hit ratio.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from northwind.config import Settings  # noqa: E402
from northwind.drift import (  # noqa: E402
    DriftResult,
    DriftThresholds,
    compare_windows,
    drift_report_markdown,
)
from telemetry.local_store import LocalSpanStore  # noqa: E402


def _metrics(
    store: LocalSpanStore, since: float | None, until: float | None
) -> dict[str, tuple[list[float], bool]]:
    """metric -> (values, higher_is_better)"""
    agents = store.spans(kind="agent", since=since, until=until)
    out: dict[str, tuple[list[float], bool]] = {
        "judge_overall": (store.score_values("judge_overall", since=since, until=until), True),
        "judge_grounded": (store.score_values("judge_grounded", since=since, until=until), True),
        "judge_resolved": (store.score_values("judge_resolved", since=since, until=until), True),
        "cost_per_request_usd": (
            [float(s.attr("atlas.cost_usd", 0.0) or 0.0) for s in agents],
            False,
        ),
        "latency_ms": ([s.duration_ms for s in agents], False),
        "steps": ([float(s.attr("atlas.steps", 1) or 1) for s in agents], False),
    }
    fb = store.score_values("user_feedback", since=since, until=until)
    if fb:
        out["user_feedback"] = (fb, True)
    return out


def compare_stores(
    baseline: LocalSpanStore,
    current: LocalSpanStore,
    *,
    thresholds: DriftThresholds = DriftThresholds(),
) -> list[DriftResult]:
    b = _metrics(baseline, None, None)
    c = _metrics(current, None, None)
    results = []
    for metric, (bvals, hib) in b.items():
        cvals = c.get(metric, ([], hib))[0]
        results.append(
            compare_windows(metric, bvals, cvals, thresholds=thresholds, higher_is_better=hib)
        )
    return results


def compare_split(
    store: LocalSpanStore, split_ts: float, *, thresholds: DriftThresholds = DriftThresholds()
) -> list[DriftResult]:
    b = _metrics(store, None, split_ts)
    c = _metrics(store, split_ts, None)
    return [
        compare_windows(m, bv, c.get(m, ([], hib))[0], thresholds=thresholds, higher_is_better=hib)
        for m, (bv, hib) in b.items()
    ]


def synthetic_comparison(seed: int = 7, sessions: int = 150) -> list[DriftResult]:
    """Baseline: a normal day. Current: the same day with the prompt v2 regression."""
    from simulator.replay import replay_day

    _, base = replay_day(seed, sessions=sessions, incidents="none", judge_rate=0.6)
    _, cur = replay_day(seed + 1, sessions=sessions, incidents="quality_drift", judge_rate=0.6)
    return compare_stores(base, cur)


def render(results: list[DriftResult], title: str) -> str:
    alerts = [r for r in results if r.alert]
    head = (
        f"# Drift report: {title}\n\n**{len(alerts)} alert(s)**"
        + (": " + ", ".join(r.metric for r in alerts) if alerts else "")
        + "\n\n"
    )
    return head + drift_report_markdown(results)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compare two windows of Atlas telemetry for drift.")
    ap.add_argument(
        "--store",
        default=None,
        help="SQLite store; if omitted or empty, a synthetic comparison is run",
    )
    ap.add_argument("--baseline-store", default=None)
    ap.add_argument(
        "--split-hour",
        type=float,
        default=12.0,
        help="hour of day that splits baseline/current within one store",
    )
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--sessions", type=int, default=150)
    args = ap.parse_args(argv)
    if args.baseline_store and args.store:
        results = compare_stores(LocalSpanStore(args.baseline_store), LocalSpanStore(args.store))
        title = f"{args.baseline_store} -> {args.store}"
    else:
        path = args.store or Settings.from_env().local_store_path
        store = LocalSpanStore(path) if Path(path).exists() else None
        if store is not None and store.count("agent") >= 40:
            start, _ = store.time_range()
            day0 = start - (start % 86_400)
            results = compare_split(store, day0 + args.split_hour * 3600)
            title = f"{path} split at {args.split_hour:g}h"
        else:
            results = synthetic_comparison(args.seed, args.sessions)
            title = f"synthetic seed={args.seed}: v1 baseline vs v2 prompt regression"
    print(render(results, title))
    return 1 if any(r.alert for r in results) and args.store else 0


if __name__ == "__main__":
    raise SystemExit(main())
