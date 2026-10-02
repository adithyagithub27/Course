"""Weekly drift report: compare the current window with a baseline (Section 8.5).

Offline usage (no store needed)::

    python evals/drift_report.py                      # synthetic: v1 baseline vs v2 (quality_drift) current
    python evals/drift_report.py --store .atlas/spans.sqlite --split-hour 12
    python -m evals.drift_report --prev 2026-W38 --curr 2026-W39     # two weeks in one store
    python -m evals.drift_report --prev .atlas/week1.sqlite --curr .atlas/week2.sqlite

Two replayed weeks in one store (each ``make replay`` day is one Monday)::

    make replay                                               # 2026-09-14, ISO week 2026-W38
    make replay DAY=2026-09-21 SCENARIO=quality_drift KEEP=1  # 2026-09-21, ISO week 2026-W39
    python -m evals.drift_report --prev 2026-W38 --curr 2026-W39

Metrics compared: judge scores (overall / grounded / resolved), cost per request,
latency, steps, cache hit ratio.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, date, datetime, timedelta
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


_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")


def resolve_window(spec: str) -> tuple[float, float] | None:
    """``2026-W38`` -> that ISO week, ``2026-09-14`` -> that UTC day; None for anything else."""
    m = _WEEK_RE.match(spec)
    if m:
        monday = date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
        start = datetime(monday.year, monday.month, monday.day, tzinfo=UTC)
        return start.timestamp(), (start + timedelta(days=7)).timestamp()
    try:
        d = date.fromisoformat(spec)
    except ValueError:
        return None
    start = datetime(d.year, d.month, d.day, tzinfo=UTC)
    return start.timestamp(), (start + timedelta(days=1)).timestamp()


def compare_specs(
    prev: str,
    curr: str,
    *,
    store_path: str | None = None,
    thresholds: DriftThresholds = DriftThresholds(),
) -> list[DriftResult]:
    """Compare two windows given as ISO weeks / days (within ``store_path``) or store paths."""

    def load(spec: str) -> tuple[LocalSpanStore, float | None, float | None]:
        window = resolve_window(spec)
        if window is not None:
            path = store_path or Settings.from_env().local_store_path
            return LocalSpanStore(path), window[0], window[1]
        if not Path(spec).exists():
            raise SystemExit(
                f"--prev/--curr {spec!r} is neither a week (2026-W38), a day nor a store"
            )
        return LocalSpanStore(spec), None, None

    bstore, bs, bu = load(prev)
    cstore, cs, cu = load(curr)
    b = _metrics(bstore, bs, bu)
    c = _metrics(cstore, cs, cu)
    for label, metrics in ((prev, b), (curr, c)):
        if not metrics["latency_ms"][0]:
            raise SystemExit(
                f"no requests in {label}; replay it first, e.g. make replay DAY=2026-09-21 KEEP=1"
            )
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
    ap.add_argument("--prev", default=None, help="baseline: ISO week (2026-W38), day or store path")
    ap.add_argument("--curr", default=None, help="current: ISO week (2026-W39), day or store path")
    ap.add_argument("--out", default=None, help="also write the markdown report to this file")
    args = ap.parse_args(argv)
    if bool(args.prev) != bool(args.curr):
        ap.error("--prev and --curr go together")
    if args.prev and args.curr:
        results = compare_specs(args.prev, args.curr, store_path=args.store)
        text = render(results, f"{args.prev} -> {args.curr}")
        print(text)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text, encoding="utf-8")
        return 1 if any(r.alert for r in results) else 0
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
    text = render(results, title)
    print(text)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    return 1 if any(r.alert for r in results) and args.store else 0


if __name__ == "__main__":
    raise SystemExit(main())
