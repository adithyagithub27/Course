"""SLIs, SLOs, error budgets and burn rates for an agent.

The six SLIs leadership understands (Section 9.1):

* task_success      — sessions the agent resolved without escalation or error
* containment       — sessions that did not need a human
* tool_error_rate   — (inverted SLI: lower is better)
* latency_p95       — threshold SLI: requests under the latency budget
* cost_per_resolved — threshold SLI: resolved sessions under the cost budget
* judge_score       — threshold SLI: sampled judge scores above 0.7
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from northwind.cost import CostRecord
from northwind.latency import percentile


@dataclass(frozen=True)
class SLI:
    """A ratio of good events to total events."""

    name: str
    good: int
    total: int
    description: str = ""

    @property
    def value(self) -> float:
        return self.good / self.total if self.total else 1.0

    @property
    def bad(self) -> int:
        return self.total - self.good


@dataclass(frozen=True)
class SLO:
    """Target ratio over a window (days)."""

    name: str
    target: float
    window_days: int = 28
    description: str = ""

    def __post_init__(self) -> None:
        if not 0 < self.target <= 1:
            raise ValueError("target must be in (0, 1]")

    @property
    def error_budget_fraction(self) -> float:
        return 1.0 - self.target


def error_budget_remaining(slo: SLO, sli: SLI) -> float:
    """Fraction of the error budget still unspent (negative = overspent)."""
    allowed_bad = slo.error_budget_fraction * sli.total
    if allowed_bad == 0:
        return 1.0 if sli.bad == 0 else -1.0
    return (allowed_bad - sli.bad) / allowed_bad


def error_budget(slo: SLO, sli: SLI) -> float:
    """Alias of :func:`error_budget_remaining`."""
    return error_budget_remaining(slo, sli)


def burn_rate(slo: SLO, sli: SLI) -> float:
    """How fast the budget burns: 1.0 = exactly on budget over the window; 14.4 = alert."""
    if slo.error_budget_fraction == 0:
        return float("inf") if sli.bad else 0.0
    bad_fraction = sli.bad / sli.total if sli.total else 0.0
    return bad_fraction / slo.error_budget_fraction


#: Multi-window burn-rate alert thresholds (Google SRE workbook), with the severities used in
#: ``deploy/alerts.yml``: 14.4x over 1h pages (AtlasTaskSuccessBurnRateFast), 6x over 6h opens a
#: ticket (AtlasTaskSuccessBurnRateSlow).
BURN_RATE_ALERTS: tuple[tuple[str, float, str], ...] = (
    ("1h", 14.4, "page"),
    ("6h", 6.0, "ticket"),
    ("1d", 3.0, "ticket"),
    ("3d", 1.0, "ticket"),
)


def burn_alert(rate: float, window: str) -> str | None:
    """Return ``page``/``ticket`` if ``rate`` breaches the threshold for ``window``."""
    for w, threshold, severity in BURN_RATE_ALERTS:
        if w == window and rate >= threshold:
            return severity
    return None


#: Default SLOs for Atlas.
DEFAULT_SLOS: dict[str, SLO] = {
    "task_success": SLO("task_success", 0.95, description="sessions resolved or escalated cleanly"),
    "containment": SLO("containment", 0.80, description="sessions resolved without a human"),
    "tool_success": SLO("tool_success", 0.99, description="tool calls that did not error"),
    "latency": SLO("latency", 0.95, description="requests under the latency budget"),
    "cost": SLO("cost", 0.90, description="sessions under the per-session cost budget"),
    "quality": SLO("quality", 0.90, description="judged responses scoring >= 0.7"),
}


@dataclass
class SLISnapshot:
    """All SLIs computed for one window."""

    slis: dict[str, SLI] = field(default_factory=dict)
    p95_latency_ms: float = 0.0
    cost_per_resolved_session: float = 0.0

    def report(self, slos: dict[str, SLO] | None = None) -> list[dict[str, object]]:
        slos = slos or DEFAULT_SLOS
        rows = []
        for name, sli in self.slis.items():
            slo = slos.get(name)
            row: dict[str, object] = {
                "sli": name,
                "value": round(sli.value, 4),
                "good": sli.good,
                "total": sli.total,
            }
            if slo:
                row["target"] = slo.target
                row["error_budget_remaining"] = round(error_budget_remaining(slo, sli), 3)
                row["burn_rate"] = round(burn_rate(slo, sli), 2)
                row["ok"] = sli.value >= slo.target
            rows.append(row)
        return rows


def compute_slis(
    records: Iterable[CostRecord],
    *,
    latency_budget_ms: float = 4000.0,
    cost_budget_usd: float = 0.05,
    judge_scores: Iterable[float] = (),
    quality_threshold: float = 0.7,
    tool_calls: int = 0,
    tool_errors: int = 0,
) -> SLISnapshot:
    """Derive the six SLIs from cost records (one per request) and judge scores."""
    recs = list(records)
    total = len(recs)
    resolved = sum(1 for r in recs if r.outcome == "resolved")
    escalated = sum(1 for r in recs if r.outcome == "escalated")
    under_latency = sum(1 for r in recs if r.latency_ms <= latency_budget_ms)
    # cost per session
    by_session: dict[str, float] = {}
    for r in recs:
        by_session[r.session_id or r.trace_id] = (
            by_session.get(r.session_id or r.trace_id, 0.0) + r.cost_usd
        )
    sessions_under = sum(1 for c in by_session.values() if c <= cost_budget_usd)
    scores = list(judge_scores)
    good_scores = sum(1 for s in scores if s >= quality_threshold)
    snap = SLISnapshot()
    snap.slis = {
        "task_success": SLI("task_success", resolved + escalated, total),
        "containment": SLI("containment", resolved, total),
        "tool_success": SLI("tool_success", max(tool_calls - tool_errors, 0), tool_calls),
        "latency": SLI("latency", under_latency, total),
        "cost": SLI("cost", sessions_under, len(by_session)),
        "quality": SLI("quality", good_scores, len(scores)),
    }
    snap.p95_latency_ms = percentile([r.latency_ms for r in recs], 95) if recs else 0.0
    resolved_cost = sum(r.cost_usd for r in recs if r.outcome == "resolved")
    resolved_sessions = {r.session_id or r.trace_id for r in recs if r.outcome == "resolved"}
    snap.cost_per_resolved_session = (
        resolved_cost / len(resolved_sessions) if resolved_sessions else 0.0
    )
    return snap
