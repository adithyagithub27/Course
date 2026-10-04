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


def test_replay_tags_real_features_for_showback():
    """6.3 / Project 1: generation and agent spans carry the feature, not a constant 'chat'."""
    from northwind.cost import rollup

    _, store = replay_day(5, sessions=80, judge_rate=0.0)
    features = set(rollup(store.cost_records("request"), "feature"))
    assert "chat" not in features and {"policy_question", "create_ticket"} <= features
    gen_features = {r.feature for r in store.cost_records("generation")}
    assert gen_features == features
    root = store.spans(kind="agent")[0]
    assert f"feature:{root.attr('atlas.feature')}" in root.attr("langfuse.trace.tags")


def test_second_day_gets_distinct_ids_and_timestamps():
    from datetime import date

    store = LocalSpanStore(":memory:")
    replay_day(5, sessions=10, store=store, judge_rate=0.0)
    n = store.count()
    replay_day(5, sessions=10, store=store, judge_rate=0.0, day=date(2026, 9, 21))
    assert store.count() == 2 * n  # nothing replaced
    start, end = store.time_range()
    assert end - start > 6 * 86_400


def test_replay_cli_incidents_default_from_atlas_scenario(monkeypatch, tmp_path, capsys):
    from simulator.replay import main

    monkeypatch.setenv("ATLAS_SCENARIO", "slow_provider")
    rc = main(["--seed", "5", "--sessions", "60", "--store", str(tmp_path / "s.sqlite"), "--clear"])
    out = capsys.readouterr().out
    assert rc == 0 and "slow_provider" in out and "Incidents: slow_provider" in out


def test_replay_masks_span_content_like_the_live_path():
    """Agent input/output and tool I/O are masked (hashed placeholders), as genai_attrs._safe does."""
    import re

    _, store = replay_day(5, sessions=60, judge_rate=0.0)
    raw = re.compile(r"\bNW-\d{5}\b")
    keys = (
        "langfuse.observation.input",
        "langfuse.observation.output",
        "gen_ai.tool.call.arguments",
        "gen_ai.tool.call.result",
    )
    seen_placeholder = False
    for span in store.spans():
        for k in keys:
            v = str(span.attr(k) or "")
            assert not raw.search(v), (k, v)
            seen_placeholder |= "<EMPLOYEE_ID:" in v
    assert seen_placeholder


def test_langfuse_mirror_reuses_trace_id_and_tags():
    """Judge/feedback scores (create_score(trace_id=...)) attach to the mirrored trace."""
    from app.langfuse_native import setup_langfuse_native
    from simulator.replay import _hex, _push_langfuse

    lf, capture = setup_langfuse_native(offline=True)
    engine = ReplayEngine(7)
    req = generate_day(7, sessions=3)[0]
    r = engine._agent(req.params).run(
        req.message, tenant=req.tenant, user_id=req.persona.user_id, session_id=req.session_id
    )
    trace_id = _hex(7, req.session_id, req.turn, n=32)
    _push_langfuse(lf, req, r, trace_id)
    lf.flush()
    spans = capture.spans(trace_id)
    root = next(s for s in spans if s.name == "invoke_agent atlas")
    tags = set(root.attributes["langfuse.trace.tags"])
    assert {f"feature:{r.feature}", f"prompt:{r.prompt_version}", f"tenant:{req.tenant}"} <= tags
    assert len(spans) == 1 + len(r.generations) + len(r.tools)


def test_replay_breaker_runs_on_replayed_time():
    """The breaker's cooldown is measured on the replayed clock, so replays are deterministic."""
    engine = ReplayEngine(7)
    engine._now = 1000.0
    engine.breaker.record_failure("m")
    engine.breaker.record_failure("m")
    engine.breaker.record_failure("m")
    assert engine.breaker.is_open("m")
    engine._now = 1000.0 + engine.breaker.cooldown_s
    assert not engine.breaker.is_open("m")
    assert engine._agent({}).breaker is engine.breaker
