from simulator.replay import ReplayEngine, replay_day
from simulator.scenarios import generate_day
from telemetry.local_store import LocalSpanStore


def test_replay_small_day_is_deterministic():
    s1, st1 = replay_day(5, sessions=30, judge_rate=0.5)
    s2, st2 = replay_day(5, sessions=30, judge_rate=0.5)
    assert s1.cost_usd == s2.cost_usd and s1.spans == s2.spans and s1.scores == s2.scores
    a = [r.to_json() for r in st1.spans()]
    b = [r.to_json() for r in st2.spans()]
    assert a == b


def test_replay_builds_full_traces():
    _, store = replay_day(5, sessions=20, judge_rate=1.0)
    agents = store.spans(kind="agent")
    assert agents and store.count("generation") >= len(agents)
    trace = store.trace(agents[0].trace_id)
    kinds = {t.kind for t in trace}
    assert "agent" in kinds and "generation" in kinds and "guardrail" in kinds
    root = agents[0]
    assert (
        root.attr("atlas.tenant")
        and root.attr("atlas.cost_usd") >= 0
        and root.attr("gen_ai.operation.name") == "invoke_agent"
    )
    children = [t for t in trace if t.parent_span_id == root.span_id]
    assert children and all(
        c.start_time >= root.start_time and c.end_time <= root.end_time + 1e-6 for c in children
    )


def test_replay_scores_and_feedback_written():
    _, store = replay_day(5, sessions=40, judge_rate=1.0, feedback_rate=0.5)
    names = {s.name for s in store.scores()}
    assert {
        "judge_overall",
        "judge_grounded",
        "judge_resolved",
        "judge_safe_escalation",
        "user_feedback",
    } <= names


def test_incident_preset_changes_outcome():
    base, _ = replay_day(5, sessions=120, incidents="none", judge_rate=0.0)
    slow, _ = replay_day(5, sessions=120, incidents="latency_regression", judge_rate=0.0)
    assert slow.p95_latency_ms > base.p95_latency_ms * 1.3
    assert "slow_provider" in slow.by_scenario


def test_engine_reuses_agents_per_params():
    eng = ReplayEngine(1)
    a1 = eng._agent({"top_k": 4})
    a2 = eng._agent({"top_k": 4})
    a3 = eng._agent({"top_k": 20})
    assert a1 is a2 and a1 is not a3


def test_replay_into_existing_store_appends():
    store = LocalSpanStore(":memory:")
    replay_day(1, sessions=10, store=store, judge_rate=0.0)
    n = store.count()
    replay_day(2, sessions=10, store=store, judge_rate=0.0)
    assert store.count() > n


def test_plan_hours_cover_day():
    plan = generate_day(9, sessions=200)
    hours = {int(r.hour) for r in plan}
    assert len(hours) >= 18
