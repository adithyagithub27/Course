"""A day of Northwind traffic with injectable incidents.

``generate_day`` returns a deterministic list of :class:`PlannedRequest` spread
over 24 hours following :data:`HOURLY_LOAD` (two peaks, quiet nights). Incidents
are time windows that stamp a scenario and parameter overrides on the requests
they hit. Scenario names: ``loop``, ``context_bloat``, ``retry_storm``,
``slow_provider``, ``prompt_regression`` (see ``northwind.config.SCENARIOS``).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from northwind.config import SCENARIOS, TENANTS
from simulator.personas import (
    Persona,
    follow_up_for,
    generate_personas,
    pick_intent,
    question_for,
    session_slots,
)

#: Relative load per hour of day (index = hour, UTC-ish office day).
HOURLY_LOAD: tuple[float, ...] = (
    0.2,
    0.1,
    0.1,
    0.1,
    0.2,
    0.5,
    1.5,
    3.5,
    6.5,
    8.5,
    8.0,
    7.0,
    5.0,
    6.5,
    7.5,
    7.0,
    5.5,
    3.5,
    2.0,
    1.2,
    0.8,
    0.6,
    0.4,
    0.3,
)
DEFAULT_DATE = date(2026, 9, 14)  # a Monday


@dataclass(frozen=True)
class Incident:
    """Inject ``scenario`` between ``start_hour`` and ``end_hour`` for ``tenant`` (None = all)."""

    scenario: str
    start_hour: float
    end_hour: float
    tenant: str | None = None
    fraction: float = 1.0
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.scenario not in SCENARIOS:
            raise ValueError(f"unknown scenario {self.scenario!r}; choose from {SCENARIOS}")
        if not 0 <= self.start_hour < self.end_hour <= 24:
            raise ValueError("hours must satisfy 0 <= start < end <= 24")
        if not 0 < self.fraction <= 1:
            raise ValueError("fraction must be in (0, 1]")

    def hits(self, hour: float, tenant: str, rng: random.Random) -> bool:
        if not (self.start_hour <= hour < self.end_hour):
            return False
        if self.tenant is not None and tenant != self.tenant:
            return False
        return rng.random() < self.fraction


#: Named incident presets used by the incident labs and the CI/demo commands.
INCIDENT_PRESETS: dict[str, list[Incident]] = {
    "none": [],
    # one preset per scenario name, so ``make replay SCENARIO=loop`` works
    "loop": [Incident("loop", 14.0, 15.0, "ops", 0.5)],
    "ticket_flaky": [Incident("ticket_flaky", 10.0, 12.0, None, 0.8)],
    "context_bloat": [
        Incident("context_bloat", 9.0, 13.0, "ops", 0.85, {"context_diet": False, "top_k": 12})
    ],
    "retry_storm": [Incident("retry_storm", 10.0, 12.0, "ops", 0.7)],
    "slow_provider": [Incident("slow_provider", 13.0, 17.0, None, 0.75)],
    "prompt_regression": [
        Incident("prompt_regression", 11.0, 24.0, None, 1.0, {"prompt_version": "v2"})
    ],
    # composite presets used by the incident labs
    "cost_spike": [
        Incident("context_bloat", 9.0, 13.0, "ops", 0.85, {"context_diet": False, "top_k": 12}),
        Incident("retry_storm", 10.0, 12.0, "ops", 0.7),
    ],
    "latency_regression": [Incident("slow_provider", 13.0, 17.0, None, 0.75, {"top_k": 20})],
    "quality_drift": [
        Incident("prompt_regression", 11.0, 24.0, None, 1.0, {"prompt_version": "v2"})
    ],
    "mixed": [
        Incident("ticket_flaky", 10.0, 12.0, None, 0.9),
        Incident("slow_provider", 15.0, 16.0, None, 0.6),
    ],
}


@dataclass(frozen=True)
class PlannedRequest:
    ts: float  # epoch seconds
    session_id: str
    turn: int
    persona: Persona
    intent: str
    message: str
    scenario: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def tenant(self) -> str:
        return self.persona.tenant

    @property
    def hour(self) -> float:
        dt = datetime.fromtimestamp(self.ts, tz=UTC)
        return dt.hour + dt.minute / 60 + dt.second / 3600


def day_start(d: date = DEFAULT_DATE) -> float:
    return datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()


def sessions_per_hour(total: int, rng: random.Random) -> list[int]:
    """Distribute ``total`` sessions over 24 hours following HOURLY_LOAD (with jitter)."""
    weights = [w * (0.9 + 0.2 * rng.random()) for w in HOURLY_LOAD]
    s = sum(weights)
    raw = [total * w / s for w in weights]
    counts = [int(x) for x in raw]
    # distribute the remainder to the largest fractional parts
    remainder = total - sum(counts)
    order = sorted(range(24), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[:remainder]:
        counts[i] += 1
    return counts


def generate_day(
    seed: int = 7,
    *,
    sessions: int = 400,
    incidents: list[Incident] | None = None,
    day: date = DEFAULT_DATE,
    personas: list[Persona] | None = None,
    max_turns: int = 4,
) -> list[PlannedRequest]:
    """Deterministic plan for one day. ``incidents`` default to none."""
    rng = random.Random(seed)
    personas = personas or generate_personas(seed)
    incidents = incidents or []
    base = day_start(day)
    plan: list[PlannedRequest] = []
    counts = sessions_per_hour(sessions, rng)
    n = 0
    tenant_weights = {"ops": 0.42, "finance": 0.18, "hr": 0.18, "eng": 0.22}
    by_tenant = {t: [p for p in personas if p.tenant == t] for t in TENANTS}
    for hour, count in enumerate(counts):
        for _ in range(count):
            n += 1
            tenant = rng.choices(list(tenant_weights), weights=list(tenant_weights.values()))[0]
            persona = rng.choice(by_tenant[tenant])
            intent = pick_intent(persona, rng)
            # a second replayed day (``--day``) gets its own session ids so stores can hold both
            session_id = (
                f"s{seed:02d}-{n:05d}" if day == DEFAULT_DATE else f"s{seed:02d}-{day:%m%d}-{n:05d}"
            )
            slots = session_slots(rng)
            ts = base + hour * 3600 + rng.random() * 3600
            turns = (
                1
                if intent in {"injection", "smalltalk", "escalation"}
                else rng.choices([1, 2, 3, 4], weights=[0.12, 0.30, 0.40, 0.18])[0]
            )
            turns = min(turns, max_turns)
            for turn in range(1, turns + 1):
                msg = (
                    question_for(intent, persona, rng, slots)
                    if turn == 1
                    else follow_up_for(intent, persona, rng, slots)
                )
                if turn > 1:
                    ts += 20 + rng.random() * 90
                hour_f = (ts - base) / 3600
                scenario, params = None, {}
                matched = [inc for inc in incidents if inc.hits(hour_f, tenant, rng)]
                if matched:
                    # overlapping incidents compound: params merge, the scenario is drawn at random
                    chosen = rng.choice(matched)
                    scenario = chosen.scenario
                    for inc in matched:
                        params.update(inc.params)
                    if len(matched) > 1:
                        params["also"] = sorted(i.scenario for i in matched if i is not chosen)
                plan.append(
                    PlannedRequest(ts, session_id, turn, persona, intent, msg, scenario, params)
                )
    plan.sort(key=lambda r: (r.ts, r.session_id))
    return plan


def summarize_plan(plan: list[PlannedRequest]) -> dict[str, Any]:
    by_hour = [0] * 24
    by_tenant: dict[str, int] = {}
    by_scenario: dict[str, int] = {}
    for r in plan:
        by_hour[int(r.hour)] += 1
        by_tenant[r.tenant] = by_tenant.get(r.tenant, 0) + 1
        by_scenario[r.scenario or "none"] = by_scenario.get(r.scenario or "none", 0) + 1
    return {
        "requests": len(plan),
        "sessions": len({r.session_id for r in plan}),
        "by_hour": by_hour,
        "by_tenant": dict(sorted(by_tenant.items())),
        "by_scenario": dict(sorted(by_scenario.items())),
    }
