"""Drift detection: compare a current window of scores/costs/latencies to a baseline.

PSI (population stability index) is computed on equal-width bins of the
baseline range; values above 0.1 are "watch", above 0.25 "alert". A
Jensen-Shannon-lite divergence is provided as a second opinion.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from northwind.latency import percentile


@dataclass(frozen=True)
class WindowStats:
    n: int
    mean: float
    std: float
    p50: float
    p95: float
    min: float
    max: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "n": self.n,
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "p50": round(self.p50, 4),
            "p95": round(self.p95, 4),
            "min": round(self.min, 4),
            "max": round(self.max, 4),
        }


def window_stats(values: Sequence[float]) -> WindowStats:
    xs = [float(v) for v in values]
    if not xs:
        return WindowStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / len(xs)
    return WindowStats(
        n=len(xs),
        mean=mean,
        std=math.sqrt(var),
        p50=percentile(xs, 50),
        p95=percentile(xs, 95),
        min=min(xs),
        max=max(xs),
    )


def _histogram(values: Sequence[float], edges: Sequence[float]) -> list[float]:
    counts = [0] * (len(edges) - 1)
    for v in values:
        # find bin; clamp to the outer bins
        idx = len(edges) - 2
        for i in range(len(edges) - 1):
            if v < edges[i + 1]:
                idx = i
                break
        counts[idx] += 1
    n = max(len(values), 1)
    return [c / n for c in counts]


def _edges(baseline: Sequence[float], bins: int) -> list[float]:
    lo, hi = min(baseline), max(baseline)
    if hi == lo:
        hi = lo + 1e-9
    step = (hi - lo) / bins
    return [lo + i * step for i in range(bins)] + [hi + 1e-12]


def psi(
    baseline: Sequence[float], current: Sequence[float], bins: int = 10, eps: float = 1e-4
) -> float:
    """Population stability index between two samples (0 = identical)."""
    if not baseline or not current:
        return 0.0
    edges = _edges(baseline, bins)
    b = _histogram(baseline, edges)
    c = _histogram(current, edges)
    total = 0.0
    for pb, pc in zip(b, c):
        pb = max(pb, eps)
        pc = max(pc, eps)
        total += (pc - pb) * math.log(pc / pb)
    return total


def js_divergence(baseline: Sequence[float], current: Sequence[float], bins: int = 10) -> float:
    """Jensen-Shannon divergence (base 2, in [0, 1]) on shared bins."""
    if not baseline or not current:
        return 0.0
    edges = _edges(list(baseline) + list(current), bins)
    p = _histogram(baseline, edges)
    q = _histogram(current, edges)
    m = [(a + b) / 2 for a, b in zip(p, q)]

    def kl(x: list[float], y: list[float]) -> float:
        return sum(xi * math.log2(xi / yi) for xi, yi in zip(x, y) if xi > 0 and yi > 0)

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


@dataclass(frozen=True)
class DriftThresholds:
    psi_watch: float = 0.10
    psi_alert: float = 0.25
    mean_shift_pct: float = 15.0  # relative change in mean that alerts
    p95_shift_pct: float = 25.0
    min_samples: int = 20


@dataclass(frozen=True)
class DriftResult:
    metric: str
    baseline: WindowStats
    current: WindowStats
    psi: float
    js: float
    mean_delta_pct: float
    p95_delta_pct: float
    status: str  # ok | watch | alert | insufficient
    reasons: tuple[str, ...]
    higher_is_better: bool

    @property
    def alert(self) -> bool:
        return self.status == "alert"

    def as_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "status": self.status,
            "psi": round(self.psi, 4),
            "js": round(self.js, 4),
            "mean_delta_pct": round(self.mean_delta_pct, 2),
            "p95_delta_pct": round(self.p95_delta_pct, 2),
            "reasons": list(self.reasons),
            "baseline": self.baseline.as_dict(),
            "current": self.current.as_dict(),
        }


def _pct(new: float, old: float) -> float:
    if old == 0:
        return 0.0 if new == 0 else math.copysign(100.0, new)
    return (new - old) / abs(old) * 100.0


def compare_windows(
    metric: str,
    baseline: Sequence[float],
    current: Sequence[float],
    *,
    thresholds: DriftThresholds = DriftThresholds(),
    higher_is_better: bool = True,
) -> DriftResult:
    """Compare two windows and classify drift as ok / watch / alert."""
    b, c = window_stats(baseline), window_stats(current)
    if b.n < thresholds.min_samples or c.n < thresholds.min_samples:
        return DriftResult(
            metric, b, c, 0.0, 0.0, 0.0, 0.0, "insufficient", ("too few samples",), higher_is_better
        )
    p = psi(baseline, current)
    j = js_divergence(baseline, current)
    mean_d = _pct(c.mean, b.mean)
    p95_d = _pct(c.p95, b.p95)
    reasons: list[str] = []
    status = "ok"
    # a shift in the "bad" direction counts; improvements are reported but not alerted
    bad_mean = (-mean_d if higher_is_better else mean_d) >= thresholds.mean_shift_pct
    bad_p95 = (-p95_d if higher_is_better else p95_d) >= thresholds.p95_shift_pct
    improved = (mean_d > 0) if higher_is_better else (mean_d < 0)
    if p >= thresholds.psi_alert:
        note = " (distribution moved, mean improved)" if improved else ""
        reasons.append(f"psi {p:.3f} >= {thresholds.psi_alert}{note}")
        status = (
            "watch" if improved else "alert"
        )  # a shift towards *better* is worth a look, not a page
    elif p >= thresholds.psi_watch:
        reasons.append(f"psi {p:.3f} >= {thresholds.psi_watch}")
        status = "watch"
    if bad_mean:
        reasons.append(f"mean moved {mean_d:+.1f}%")
        status = "alert"
    if bad_p95:
        reasons.append(f"p95 moved {p95_d:+.1f}%")
        status = "alert"
    return DriftResult(metric, b, c, p, j, mean_d, p95_d, status, tuple(reasons), higher_is_better)


def drift_report_markdown(results: Sequence[DriftResult]) -> str:
    """Render drift results as a markdown table."""
    lines = [
        "| metric | status | baseline mean | current mean | Δ mean | Δ p95 | PSI | reasons |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.metric} | {r.status} | {r.baseline.mean:.3f} | {r.current.mean:.3f} | "
            f"{r.mean_delta_pct:+.1f}% | {r.p95_delta_pct:+.1f}% | {r.psi:.3f} | "
            f"{'; '.join(r.reasons) or '-'} |"
        )
    return "\n".join(lines) + "\n"
