"""Latency measurement for streaming agents: TTFT, TPOT, totals, percentiles, budgets.

No numpy: percentiles use linear interpolation on the sorted list (the same
definition Prometheus and pandas use by default).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class LatencySample:
    """One request's timings in milliseconds."""

    total_ms: float
    ttft_ms: float | None = None
    output_tokens: int = 0
    steps: int = 1
    trace_id: str = ""
    tenant: str = ""
    model: str = ""

    @property
    def tpot_ms(self) -> float | None:
        """Time per output token after the first token (ms/token)."""
        if self.ttft_ms is None or self.output_tokens <= 1:
            return None
        return max(0.0, (self.total_ms - self.ttft_ms) / (self.output_tokens - 1))

    @property
    def tokens_per_second(self) -> float | None:
        tpot = self.tpot_ms
        return 1000.0 / tpot if tpot else None


@dataclass(frozen=True)
class StepTiming:
    """Timings of one agent step: the model call plus its tool calls."""

    step: int
    model: str
    total_ms: float
    ttft_ms: float | None = None
    output_tokens: int = 0
    tool_ms: float = 0.0

    @property
    def model_ms(self) -> float:
        return max(0.0, self.total_ms - self.tool_ms)


@dataclass(frozen=True)
class RequestTiming:
    """Whole request assembled from steps; ``to_sample`` gives the aggregate view."""

    trace_id: str
    steps: tuple[StepTiming, ...]
    tenant: str = ""

    @property
    def total_ms(self) -> float:
        return sum(s.total_ms for s in self.steps)

    @property
    def ttft_ms(self) -> float | None:
        """Time until the first token of the *final* answer (what the user perceives)."""
        if not self.steps:
            return None
        last = self.steps[-1]
        if last.ttft_ms is None:
            return None
        return sum(s.total_ms for s in self.steps[:-1]) + last.ttft_ms

    @property
    def slowest_step(self) -> StepTiming | None:
        return max(self.steps, key=lambda s: s.total_ms) if self.steps else None

    def to_sample(self) -> LatencySample:
        return LatencySample(
            total_ms=self.total_ms,
            ttft_ms=self.ttft_ms,
            output_tokens=self.steps[-1].output_tokens if self.steps else 0,
            steps=len(self.steps),
            trace_id=self.trace_id,
            tenant=self.tenant,
            model=self.steps[-1].model if self.steps else "",
        )


def percentile(values: Sequence[float], p: float) -> float:
    """Linear-interpolated percentile; ``p`` in [0, 100]."""
    if not values:
        raise ValueError("percentile of empty sequence")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    k = (len(xs) - 1) * p / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return float(xs[int(k)])
    return float(xs[lo] + (xs[hi] - xs[lo]) * (k - lo))


@dataclass(frozen=True)
class LatencyStats:
    count: int
    mean: float
    p50: float
    p90: float
    p95: float
    p99: float
    max: float
    min: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "count": self.count,
            "mean": round(self.mean, 2),
            "p50": round(self.p50, 2),
            "p90": round(self.p90, 2),
            "p95": round(self.p95, 2),
            "p99": round(self.p99, 2),
            "max": round(self.max, 2),
            "min": round(self.min, 2),
        }


def summarize(values: Iterable[float]) -> LatencyStats:
    """Percentile summary of a set of durations."""
    xs = [float(v) for v in values]
    if not xs:
        return LatencyStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return LatencyStats(
        count=len(xs),
        mean=sum(xs) / len(xs),
        p50=percentile(xs, 50),
        p90=percentile(xs, 90),
        p95=percentile(xs, 95),
        p99=percentile(xs, 99),
        max=max(xs),
        min=min(xs),
    )


@dataclass(frozen=True)
class LatencyBudget:
    """Targets in ms. ``None`` disables a check."""

    total_p95_ms: float = 4000.0
    ttft_p95_ms: float | None = 1200.0
    per_step_ms: float | None = 2500.0
    tpot_ms: float | None = 60.0


@dataclass(frozen=True)
class Violation:
    metric: str
    observed: float
    budget: float
    trace_id: str = ""

    def __str__(self) -> str:
        where = f" ({self.trace_id})" if self.trace_id else ""
        return f"{self.metric}: {self.observed:.0f} ms > budget {self.budget:.0f} ms{where}"


def violations(
    samples: Sequence[LatencySample | RequestTiming], budget: LatencyBudget
) -> list[Violation]:
    """Aggregate (p95) and per-sample (per-step, TPOT) budget violations."""
    out: list[Violation] = []
    samples = [s.to_sample() if isinstance(s, RequestTiming) else s for s in samples]
    if not samples:
        return out
    totals = [s.total_ms for s in samples]
    p95 = percentile(totals, 95)
    if p95 > budget.total_p95_ms:
        out.append(Violation("total_p95_ms", p95, budget.total_p95_ms))
    ttfts = [s.ttft_ms for s in samples if s.ttft_ms is not None]
    if budget.ttft_p95_ms is not None and ttfts:
        t95 = percentile(ttfts, 95)
        if t95 > budget.ttft_p95_ms:
            out.append(Violation("ttft_p95_ms", t95, budget.ttft_p95_ms))
    for s in samples:
        if budget.per_step_ms is not None and s.steps > 0:
            per_step = s.total_ms / s.steps
            if per_step > budget.per_step_ms:
                out.append(Violation("per_step_ms", per_step, budget.per_step_ms, s.trace_id))
        if budget.tpot_ms is not None and s.tpot_ms is not None and s.tpot_ms > budget.tpot_ms:
            out.append(Violation("tpot_ms", s.tpot_ms, budget.tpot_ms, s.trace_id))
    return out


def by_group(samples: Iterable[LatencySample], attr: str) -> dict[str, LatencyStats]:
    """Latency summary per tenant/model/etc."""
    groups: dict[str, list[float]] = {}
    for s in samples:
        groups.setdefault(str(getattr(s, attr)) or "(none)", []).append(s.total_ms)
    return {k: summarize(v) for k, v in sorted(groups.items())}


def hourly_p95(samples: Iterable[tuple[float, float]], bucket_s: int = 3600) -> dict[int, float]:
    """Given (timestamp, total_ms) pairs, p95 per time bucket (bucket start epoch)."""
    buckets: dict[int, list[float]] = {}
    for ts, ms in samples:
        buckets.setdefault(int(ts // bucket_s) * bucket_s, []).append(ms)
    return {k: percentile(v, 95) for k, v in sorted(buckets.items())}
