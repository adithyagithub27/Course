"""Sampling policies: head sampling, tail sampling and judge sampling.

All decisions are **deterministic** functions of the trace id so that every
service in a request path (and every test) agrees on them.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

_MAX = 2**52


def _unit(key: str, salt: str = "") -> float:
    """Map a string to a stable float in [0, 1)."""
    h = hashlib.sha256(f"{salt}:{key}".encode()).digest()
    return int.from_bytes(h[:7], "big") % _MAX / _MAX


def head_sample(trace_id: str, rate: float, *, salt: str = "head") -> bool:
    """Keep ``rate`` of traces, decided at trace start from the id alone."""
    if not 0.0 <= rate <= 1.0:
        raise ValueError("rate must be in [0, 1]")
    if rate == 1.0:
        return True
    if rate == 0.0:
        return False
    return _unit(trace_id, salt) < rate


@dataclass(frozen=True)
class TraceSummary:
    """What a tail sampler knows at trace end."""

    trace_id: str
    error: bool = False
    duration_ms: float = 0.0
    cost_usd: float = 0.0
    steps: int = 1
    tenant: str = ""
    escalated: bool = False
    feedback_negative: bool = False


@dataclass(frozen=True)
class TailSamplingPolicy:
    """Always keep the interesting traces, sample the boring ones.

    Rules (evaluated in order, first match wins):
      errors -> keep; slow -> keep; expensive -> keep; many steps -> keep;
      escalated -> keep; negative feedback -> keep; else base_rate.
    """

    base_rate: float = 0.1
    keep_errors: bool = True
    slow_ms: float | None = 4000.0
    expensive_usd: float | None = 0.05
    max_steps: int | None = 5
    keep_escalated: bool = True
    keep_negative_feedback: bool = True
    tenant_rates: dict[str, float] = field(default_factory=dict)

    def reason(self, t: TraceSummary) -> str | None:
        """Why the trace is kept regardless of rate, or None."""
        if self.keep_errors and t.error:
            return "error"
        if self.slow_ms is not None and t.duration_ms > self.slow_ms:
            return "slow"
        if self.expensive_usd is not None and t.cost_usd > self.expensive_usd:
            return "expensive"
        if self.max_steps is not None and t.steps > self.max_steps:
            return "many_steps"
        if self.keep_escalated and t.escalated:
            return "escalated"
        if self.keep_negative_feedback and t.feedback_negative:
            return "negative_feedback"
        return None

    def should_keep(self, t: TraceSummary) -> tuple[bool, str]:
        r = self.reason(t)
        if r:
            return True, r
        rate = self.tenant_rates.get(t.tenant, self.base_rate)
        return head_sample(t.trace_id, rate, salt="tail"), "rate"


@dataclass(frozen=True)
class JudgeSamplingPolicy:
    """Which traces get an LLM judge (which costs money)."""

    rate: float = 0.1
    always_judge_escalated: bool = True
    always_judge_negative_feedback: bool = True
    tenant_rates: dict[str, float] = field(default_factory=dict)
    max_per_hour: int | None = None

    def should_judge(self, t: TraceSummary) -> bool:
        if self.always_judge_escalated and t.escalated:
            return True
        if self.always_judge_negative_feedback and t.feedback_negative:
            return True
        if t.error:
            return False  # nothing to judge
        rate = self.tenant_rates.get(t.tenant, self.rate)
        return head_sample(t.trace_id, rate, salt="judge")


#: Short name used in the lecture scripts.
JudgeSampler = JudgeSamplingPolicy


def expected_kept(n: int, rate: float) -> int:
    """Expected number of traces kept (for capacity planning and tests)."""
    return round(n * rate)
