"""CI budget gate (Section 13.3).

Replays a day offline and fails the build when cost per session or p95 latency
exceed the budgets in ``northwind.config.Settings`` (env ``BUDGET_COST_PER_SESSION_USD``,
``BUDGET_P95_LATENCY_MS``). Passes by default. To watch it fail in a demo::

    BUDGET_P95_LATENCY_MS=2500 make budget-check            # tighter latency budget
    BUDGET_COST_PER_SESSION_USD=0.001 make budget-check     # tighter cost budget
    BUDGET_GATE_INCIDENTS=latency_regression make budget-check   # replay with an incident
    BUDGET_GATE_INCIDENTS=cost_spike make budget-check           # tokens test fails (context bloat)
"""

from __future__ import annotations

import os

import pytest

from northwind.config import Settings
from northwind.cost import cost_per_session, rollup
from northwind.latency import LatencyBudget, percentile, violations
from northwind.slo import DEFAULT_SLOS, compute_slis
from simulator.replay import replay_day
from telemetry.local_store import LocalSpanStore

SESSIONS = int(os.environ.get("BUDGET_GATE_SESSIONS", "300"))
INCIDENTS = os.environ.get("BUDGET_GATE_INCIDENTS", "none")
SEED = int(os.environ.get("BUDGET_GATE_SEED", "7"))
STORE_PATH = os.environ.get("BUDGET_GATE_STORE", ".atlas/budget-gate.sqlite")


@pytest.fixture(scope="module")
def gate():
    settings = Settings.from_env()
    store = LocalSpanStore(STORE_PATH)
    store.clear()
    summary, _ = replay_day(
        SEED, sessions=SESSIONS, incidents=INCIDENTS, store=store, judge_rate=0.3, settings=settings
    )
    return settings, store, summary


def test_cost_per_session_within_budget(gate):
    settings, store, summary = gate
    cps = float(cost_per_session(store.cost_records("request")))
    print(
        f"\ncost/session ${cps:.5f} (budget ${settings.budget_cost_per_session_usd}) total ${summary.cost_usd:.2f} over {summary.sessions} sessions"
    )
    assert cps <= settings.budget_cost_per_session_usd, (
        f"cost per session ${cps:.5f} exceeds budget ${settings.budget_cost_per_session_usd}"
    )


def test_p95_latency_within_budget(gate):
    settings, store, _ = gate
    samples = store.latency_samples()
    p95 = percentile([s.total_ms for s in samples], 95)
    print(
        f"\np95 {p95:.0f} ms (budget {settings.budget_p95_latency_ms:.0f} ms) over {len(samples)} requests"
    )
    assert p95 <= settings.budget_p95_latency_ms, (
        f"p95 {p95:.0f} ms exceeds budget {settings.budget_p95_latency_ms:.0f} ms"
    )
    v = violations(
        samples,
        LatencyBudget(
            total_p95_ms=settings.budget_p95_latency_ms,
            ttft_p95_ms=None,
            per_step_ms=None,
            tpot_ms=None,
        ),
    )
    assert not v, [str(x) for x in v]


def test_no_tenant_over_its_daily_soft_cap(gate):
    settings, store, _ = gate
    for tenant, r in rollup(store.cost_records("generation"), "tenant").items():
        assert float(r.cost_usd) <= settings.tenant_soft_cap_usd, (
            f"{tenant} spent ${r.cost_usd} > soft cap"
        )


def test_task_success_slo_holds(gate):
    settings, store, _ = gate
    snap = compute_slis(
        store.cost_records("request"),
        latency_budget_ms=settings.budget_p95_latency_ms,
        cost_budget_usd=settings.budget_cost_per_session_usd,
        judge_scores=store.score_values("judge_overall"),
    )
    sli = snap.slis["task_success"]
    assert sli.value >= DEFAULT_SLOS["task_success"].target, (
        f"task success {sli.value:.3f} below SLO"
    )
    quality = snap.slis["quality"]
    assert quality.total == 0 or quality.value >= 0.75, f"judge quality {quality.value:.3f} too low"


def test_max_input_tokens_per_generation(gate):
    """Lecture 13.3: no single prompt above MAX_INPUT_TOKENS_PER_GENERATION (default 24,000)."""
    settings, store, _ = gate
    gens = store.cost_records("generation")
    worst = max(gens, key=lambda g: g.input_tokens)
    print(
        f"\nmax input tokens/generation {worst.input_tokens:,} "
        f"(budget {settings.max_input_tokens_per_generation:,}) trace {worst.trace_id}"
    )
    assert worst.input_tokens <= settings.max_input_tokens_per_generation, (
        f"a generation sent {worst.input_tokens:,} input tokens "
        f"(> {settings.max_input_tokens_per_generation:,}): trace {worst.trace_id}"
    )
