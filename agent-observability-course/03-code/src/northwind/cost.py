"""Cost attribution: per request, then rolled up by session, user, tenant and feature.

A :class:`CostRecord` is what a generation span becomes once priced. Rollups
are plain dictionaries so the Ops Console, the weekly report and the CI budget
gate can all consume them without a dataframe library.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Literal

from northwind.pricing import estimate_cost

Dimension = Literal["tenant", "session_id", "user_id", "feature", "model", "intent"]
DIMENSIONS: tuple[str, ...] = ("tenant", "session_id", "user_id", "feature", "model", "intent")


@dataclass(frozen=True)
class CostRecord:
    """One priced LLM generation (or a whole request when aggregated upstream)."""

    trace_id: str
    tenant: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float
    session_id: str = ""
    user_id: str = ""
    feature: str = "chat"
    intent: str = "unknown"
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    latency_ms: float = 0.0
    outcome: str = "resolved"
    steps: int = 1
    scenario: str | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @classmethod
    def from_usage(
        cls,
        *,
        trace_id: str,
        tenant: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        timestamp: float,
        cached_tokens: int = 0,
        reasoning_tokens: int = 0,
        **extra: object,
    ) -> CostRecord:
        """Price the usage with :func:`northwind.pricing.estimate_cost` and build a record."""
        cb = estimate_cost(
            model,
            input_tokens,
            output_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
        )
        return cls(
            trace_id=trace_id,
            tenant=tenant,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=float(cb.total_usd),
            timestamp=timestamp,
            **extra,  # type: ignore[arg-type]
        )

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class Rollup:
    """Aggregated cost for one key of one dimension."""

    key: str
    requests: int = 0
    cost_usd: Decimal = Decimal(0)
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    sessions: set[str] = field(default_factory=set)
    resolved: int = 0
    escalated: int = 0
    errors: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost_per_request(self) -> Decimal:
        return self.cost_usd / self.requests if self.requests else Decimal(0)

    @property
    def cost_per_session(self) -> Decimal:
        return self.cost_usd / len(self.sessions) if self.sessions else Decimal(0)

    @property
    def cost_per_resolved(self) -> Decimal | None:
        return self.cost_usd / self.resolved if self.resolved else None

    @property
    def cache_hit_ratio(self) -> float:
        return self.cached_tokens / self.input_tokens if self.input_tokens else 0.0

    def as_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "requests": self.requests,
            "cost_usd": float(self.cost_usd),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "sessions": len(self.sessions),
            "resolved": self.resolved,
            "escalated": self.escalated,
            "errors": self.errors,
            "cost_per_request": float(self.cost_per_request),
            "cost_per_session": float(self.cost_per_session),
            "cache_hit_ratio": round(self.cache_hit_ratio, 4),
        }


def rollup(records: Iterable[CostRecord], by: str = "tenant") -> dict[str, Rollup]:
    """Group records by one dimension and aggregate."""
    if by not in DIMENSIONS:
        raise ValueError(f"unknown dimension {by!r}; choose from {DIMENSIONS}")
    out: dict[str, Rollup] = {}
    for r in records:
        key = str(getattr(r, by)) or "(none)"
        agg = out.setdefault(key, Rollup(key=key))
        agg.requests += 1
        agg.cost_usd += Decimal(str(r.cost_usd))
        agg.input_tokens += r.input_tokens
        agg.output_tokens += r.output_tokens
        agg.cached_tokens += r.cached_tokens
        if r.session_id:
            agg.sessions.add(r.session_id)
        if r.outcome == "resolved":
            agg.resolved += 1
        elif r.outcome == "escalated":
            agg.escalated += 1
        elif r.outcome in {"error", "step_limit", "refused"}:
            agg.errors += 1
    return out


def rollup_nested(
    records: Iterable[CostRecord], outer: str, inner: str
) -> dict[str, dict[str, Rollup]]:
    """Two-level rollup, e.g. tenant -> feature."""
    groups: dict[str, list[CostRecord]] = defaultdict(list)
    for r in records:
        groups[str(getattr(r, outer)) or "(none)"].append(r)
    return {k: rollup(v, inner) for k, v in sorted(groups.items())}


def total_cost(records: Iterable[CostRecord]) -> Decimal:
    """Exact sum of costs."""
    return sum((Decimal(str(r.cost_usd)) for r in records), Decimal(0))


def cost_per_session(records: Iterable[CostRecord]) -> Decimal:
    """Average cost per distinct session across all records."""
    recs = list(records)
    sessions = {r.session_id for r in recs if r.session_id}
    if not sessions:
        return Decimal(0)
    return total_cost(recs) / len(sessions)


def top_n(rollups: dict[str, Rollup], n: int = 5, key: str = "cost_usd") -> list[Rollup]:
    """Largest ``n`` rollups by attribute ``key``."""
    return sorted(rollups.values(), key=lambda r: getattr(r, key), reverse=True)[:n]


def showback_table(
    records: Iterable[CostRecord],
    by: str = "tenant",
    *,
    currency: str = "USD",
    fmt: Callable[[Decimal], str] | None = None,
) -> str:
    """Markdown table finance can read: one row per key, sorted by cost."""
    money = fmt or (lambda d: f"{d:,.4f}")
    rolls = sorted(rollup(records, by).values(), key=lambda r: r.cost_usd, reverse=True)
    header = (
        f"| {by} | requests | sessions | tokens in | tokens out | cache hit | "
        f"cost ({currency}) | cost/session | share |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    grand = sum((r.cost_usd for r in rolls), Decimal(0))
    rows = []
    for r in rolls:
        share = (r.cost_usd / grand * 100) if grand else Decimal(0)
        rows.append(
            f"| {r.key} | {r.requests} | {len(r.sessions)} | {r.input_tokens:,} | "
            f"{r.output_tokens:,} | {r.cache_hit_ratio:.0%} | {money(r.cost_usd)} | "
            f"{money(r.cost_per_session)} | {share:.1f}% |"
        )
    total_row = (
        f"| **total** | {sum(r.requests for r in rolls)} | "
        f"{len({s for r in rolls for s in r.sessions})} | "
        f"{sum(r.input_tokens for r in rolls):,} | {sum(r.output_tokens for r in rolls):,} | "
        f"| {money(grand)} | | 100% |"
    )
    return header + "\n".join(rows + [total_row]) + "\n"
