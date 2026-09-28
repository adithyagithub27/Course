import pytest

from northwind.config import SCENARIOS, TENANTS
from simulator.personas import (
    INTENT_MIX,
    TEMPLATES,
    follow_up_for,
    generate_personas,
    pick_intent,
    question_for,
)
from simulator.scenarios import (
    HOURLY_LOAD,
    INCIDENT_PRESETS,
    Incident,
    generate_day,
    sessions_per_hour,
    summarize_plan,
)


def test_personas_cover_tenants_and_are_deterministic():
    a, b = generate_personas(7), generate_personas(7)
    assert [p.employee_id for p in a] == [p.employee_id for p in b]
    assert {p.tenant for p in a} == set(TENANTS) and len({p.employee_id for p in a}) == len(a)
    assert all(p.employee_id.startswith("NW-") for p in a)


def test_intent_mix_sums_to_one_and_has_templates():
    for tenant, mix in INTENT_MIX.items():
        assert tenant in TENANTS and abs(sum(mix.values()) - 1.0) < 1e-6
        assert set(mix) <= set(TEMPLATES)


def test_question_and_follow_up_fill_slots():
    import random

    rng = random.Random(1)
    p = generate_personas(1)[0]
    q = question_for("password_reset", p, rng)
    assert p.employee_id in q
    f = follow_up_for("vpn", p, rng)
    assert isinstance(f, str) and f
    assert pick_intent(p, rng) in p.intents


def test_hourly_load_shape():
    assert len(HOURLY_LOAD) == 24 and max(HOURLY_LOAD) == HOURLY_LOAD[9] and HOURLY_LOAD[3] < 0.5
    counts = sessions_per_hour(400, __import__("random").Random(0))
    assert sum(counts) == 400 and counts[9] > counts[3]


def test_generate_day_deterministic_and_sorted():
    a = generate_day(7, sessions=50)
    b = generate_day(7, sessions=50)
    assert [(r.ts, r.message) for r in a] == [(r.ts, r.message) for r in b]
    assert all(a[i].ts <= a[i + 1].ts for i in range(len(a) - 1))
    s = summarize_plan(a)
    assert s["sessions"] == 50 and s["requests"] >= 50 and set(s["by_tenant"]) <= set(TENANTS)


def test_generate_day_requests_per_session_about_2_5():
    plan = generate_day(7, sessions=800)
    ratio = len(plan) / 800
    assert 2.2 <= ratio <= 2.8


def test_incident_validation():
    with pytest.raises(ValueError):
        Incident("meteor", 1, 2)
    with pytest.raises(ValueError):
        Incident("loop", 5, 3)
    with pytest.raises(ValueError):
        Incident("loop", 1, 2, fraction=0)


def test_incident_injection_window_and_tenant():
    plan = generate_day(7, sessions=300, incidents=INCIDENT_PRESETS["cost_spike"])
    hit = [r for r in plan if r.scenario]
    assert hit and all(r.tenant == "ops" and 9 <= r.hour < 13 for r in hit)
    assert {r.scenario for r in hit} <= {"context_bloat", "retry_storm"}
    assert any(r.params.get("top_k") == 12 for r in hit)


@pytest.mark.parametrize("name", sorted(INCIDENT_PRESETS))
def test_all_presets_valid(name):
    for inc in INCIDENT_PRESETS[name]:
        assert inc.scenario in SCENARIOS


def test_every_scenario_has_a_preset():
    assert set(SCENARIOS) <= set(INCIDENT_PRESETS)
