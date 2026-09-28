"""Per-tenant budgets: soft cap (degrade), hard cap (refuse), rolling windows and
an EWMA anomaly detector.

The guard is deliberately in-process and dependency-free so it can sit in the
request path. Persisting the windows is left to the caller (Redis in prod).
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum


class Decision(StrEnum):
    """What the request path should do."""

    ALLOW = "allow"
    DEGRADE = "degrade"
    REFUSE = "refuse"


@dataclass(frozen=True)
class TenantBudget:
    """Caps in USD over a rolling window (default: 24 h)."""

    tenant: str
    soft_cap_usd: float
    hard_cap_usd: float
    window_s: int = 86_400

    def __post_init__(self) -> None:
        if self.soft_cap_usd < 0 or self.hard_cap_usd < 0:
            raise ValueError("caps must be non-negative")
        if self.soft_cap_usd > self.hard_cap_usd:
            raise ValueError("soft cap must not exceed hard cap")
        if self.window_s <= 0:
            raise ValueError("window must be positive")


@dataclass
class SpendWindow:
    """Rolling sum of (timestamp, usd) pairs; O(1) amortised add and evict."""

    window_s: int
    _items: deque[tuple[float, float]] = field(default_factory=deque)
    _total: float = 0.0

    def add(self, usd: float, ts: float) -> None:
        if usd < 0:
            raise ValueError("spend must be non-negative")
        self._items.append((ts, usd))
        self._total += usd
        self.evict(ts)

    def evict(self, now: float) -> None:
        cutoff = now - self.window_s
        while self._items and self._items[0][0] <= cutoff:
            _, usd = self._items.popleft()
            self._total -= usd
        if self._total < 0:
            self._total = 0.0

    def total(self, now: float | None = None) -> float:
        if now is not None:
            self.evict(now)
        return round(self._total, 10)

    def __len__(self) -> int:
        return len(self._items)


@dataclass
class EWMAAnomalyDetector:
    """Exponentially weighted moving average with a running variance.

    ``update(x)`` returns a z-score-like deviation; ``is_anomaly(x)`` is True when
    the deviation exceeds ``threshold`` after ``warmup`` observations.
    """

    alpha: float = 0.3
    threshold: float = 3.0
    warmup: int = 5
    mean: float | None = None
    var: float = 0.0
    n: int = 0

    def __post_init__(self) -> None:
        if not 0 < self.alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")

    def deviation(self, x: float) -> float:
        """z-like score of ``x`` against the current state without updating."""
        if self.mean is None or self.n < self.warmup:
            return 0.0
        std = math.sqrt(self.var) if self.var > 0 else 0.0
        if std == 0:
            return 0.0 if x == self.mean else math.inf
        return (x - self.mean) / std

    def update(self, x: float) -> float:
        """Fold ``x`` in and return its deviation *before* the update."""
        dev = self.deviation(x)
        if self.mean is None:
            self.mean = x
            self.var = 0.0
        else:
            diff = x - self.mean
            self.mean += self.alpha * diff
            self.var = (1 - self.alpha) * (self.var + self.alpha * diff * diff)
        self.n += 1
        return dev

    def is_anomaly(self, x: float) -> bool:
        return self.deviation(x) > self.threshold


@dataclass(frozen=True)
class BudgetDecision:
    """Outcome of a budget check."""

    tenant: str
    decision: Decision
    spent_usd: float
    soft_cap_usd: float
    hard_cap_usd: float
    reason: str
    anomaly: bool = False

    @property
    def utilisation(self) -> float:
        return self.spent_usd / self.hard_cap_usd if self.hard_cap_usd else 0.0

    def as_dict(self) -> dict[str, object]:
        return {
            "tenant": self.tenant,
            "decision": self.decision.value,
            "spent_usd": round(self.spent_usd, 6),
            "soft_cap_usd": self.soft_cap_usd,
            "hard_cap_usd": self.hard_cap_usd,
            "utilisation": round(self.utilisation, 4),
            "reason": self.reason,
            "anomaly": self.anomaly,
        }


class BudgetGuard:
    """Tracks spend per tenant and decides allow / degrade / refuse.

    Example::

        guard = BudgetGuard.from_caps(["hr"], soft=25, hard=40)
        guard.record("hr", 0.02, ts=now)
        guard.decide("hr", now).decision  # Decision.ALLOW
    """

    def __init__(
        self,
        budgets: dict[str, TenantBudget] | None = None,
        *,
        default_budget: TenantBudget | None = None,
        anomaly_alpha: float = 0.3,
        anomaly_threshold: float = 3.0,
    ) -> None:
        self._budgets: dict[str, TenantBudget] = dict(budgets or {})
        self._default = default_budget
        self._windows: dict[str, SpendWindow] = {}
        self._detectors: dict[str, EWMAAnomalyDetector] = {}
        self._alpha = anomaly_alpha
        self._threshold = anomaly_threshold
        self.decisions: dict[str, dict[str, int]] = {}

    @classmethod
    def from_caps(
        cls, tenants: list[str], *, soft: float, hard: float, window_s: int = 86_400
    ) -> BudgetGuard:
        return cls({t: TenantBudget(t, soft, hard, window_s) for t in tenants})

    def budget_for(self, tenant: str) -> TenantBudget:
        b = self._budgets.get(tenant) or self._default
        if b is None:
            raise KeyError(f"no budget for tenant {tenant!r}")
        return b

    def set_budget(self, budget: TenantBudget) -> None:
        self._budgets[budget.tenant] = budget

    def _window(self, tenant: str) -> SpendWindow:
        if tenant not in self._windows:
            self._windows[tenant] = SpendWindow(self.budget_for(tenant).window_s)
        return self._windows[tenant]

    def _detector(self, tenant: str) -> EWMAAnomalyDetector:
        if tenant not in self._detectors:
            self._detectors[tenant] = EWMAAnomalyDetector(self._alpha, self._threshold)
        return self._detectors[tenant]

    def record(self, tenant: str, usd: float, ts: float) -> float:
        """Add a spend and return its anomaly deviation (z-like)."""
        self._window(tenant).add(usd, ts)
        return self._detector(tenant).update(usd)

    def spent(self, tenant: str, now: float) -> float:
        return self._window(tenant).total(now)

    def estimate(self, tenant: str) -> float:
        """Expected cost of the next request: the EWMA of past requests (0 before any spend)."""
        det = self._detectors.get(tenant)
        return float(det.mean) if det is not None and det.mean is not None else 0.0

    def decide(self, tenant: str, now: float, *, next_cost_usd: float = 0.0) -> BudgetDecision:
        """Decide for the *next* request. ``next_cost_usd`` may pre-charge an estimate."""
        b = self.budget_for(tenant)
        spent = self.spent(tenant, now)
        projected = spent + max(next_cost_usd, 0.0)
        anomaly = self._detector(tenant).is_anomaly(next_cost_usd) if next_cost_usd else False
        if projected >= b.hard_cap_usd:
            d, reason = Decision.REFUSE, f"hard cap {b.hard_cap_usd:.2f} USD reached"
        elif projected >= b.soft_cap_usd:
            d, reason = Decision.DEGRADE, f"soft cap {b.soft_cap_usd:.2f} USD reached"
        else:
            d, reason = Decision.ALLOW, "within budget"
        self.decisions.setdefault(tenant, {}).setdefault(d.value, 0)
        self.decisions[tenant][d.value] += 1
        return BudgetDecision(tenant, d, spent, b.soft_cap_usd, b.hard_cap_usd, reason, anomaly)

    def status(self, now: float) -> list[BudgetDecision]:
        """Snapshot for dashboards (does not count as a decision)."""
        out = []
        for tenant in sorted(set(self._budgets) | set(self._windows)):
            b = self.budget_for(tenant)
            spent = self.spent(tenant, now)
            if spent >= b.hard_cap_usd:
                d = Decision.REFUSE
            elif spent >= b.soft_cap_usd:
                d = Decision.DEGRADE
            else:
                d = Decision.ALLOW
            out.append(
                BudgetDecision(tenant, d, spent, b.soft_cap_usd, b.hard_cap_usd, "status", False)
            )
        return out


#: Short name used in the lecture scripts.
EwmaAnomaly = EWMAAnomalyDetector


def hourly_anomalies(
    hourly_spend: list[float], *, alpha: float = 0.3, threshold: float = 3.0, warmup: int = 5
) -> list[int]:
    """Indices of hours whose spend is anomalous versus the EWMA of the previous hours."""
    det = EWMAAnomalyDetector(alpha=alpha, threshold=threshold, warmup=warmup)
    flagged = []
    for i, x in enumerate(hourly_spend):
        if det.is_anomaly(x):
            flagged.append(i)
        det.update(x)
    return flagged
