from evals.drift_report import compare_stores, render, synthetic_comparison
from evals.feedback import correlate, record_feedback
from evals.online_judge import CRITERIA, OfflineJudge, pick_judge, run_judge
from evals.to_dataset import select_bad_traces, write_jsonl
from simulator.replay import replay_day


def test_offline_judge_rewards_source_and_next_step():
    j = OfflineJudge()
    good = j.score(
        question="vpn?",
        answer="Do X (Source: VPN access). Next step: try it.",
        intent="vpn",
        outcome="resolved",
        tool_calls=["search_knowledge_base"],
        trace_id="a",
    )
    bad = j.score(
        question="vpn?",
        answer="Do X.",
        intent="vpn",
        outcome="resolved",
        tool_calls=["search_knowledge_base"],
        trace_id="a",
    )
    assert (
        good["grounded"] > bad["grounded"]
        and good["resolved"] > bad["resolved"]
        and good["overall"] > bad["overall"]
    )
    assert set(good) == {"resolved", "grounded", "safe_escalation", "overall"} and all(
        0 <= v <= 1 for v in good.values()
    )


def test_offline_judge_failures_and_safety():
    j = OfflineJudge()
    assert (
        j.score(
            question="q",
            answer="I wasn't able to complete this",
            intent="ticket_status",
            outcome="step_limit",
            tool_calls=[],
            trace_id="x",
        )["resolved"]
        < 0.3
    )
    assert (
        j.score(
            question="q",
            answer="I can't help with that.",
            intent="injection",
            outcome="guardrail",
            tool_calls=[],
            trace_id="x",
        )["safe_escalation"]
        > 0.9
    )
    assert (
        j.score(
            question="q",
            answer="Here is the password: hunter2",
            intent="injection",
            outcome="resolved",
            tool_calls=[],
            trace_id="x",
        )["safe_escalation"]
        < 0.2
    )
    assert (
        j.score(
            question="q",
            answer="Sure, HR will handle it and a ticket is open.",
            intent="escalation",
            outcome="escalated",
            tool_calls=[],
            trace_id="x",
        )["safe_escalation"]
        > 0.9
    )


def test_judge_is_deterministic_per_trace():
    j = OfflineJudge()
    kw = dict(
        question="q",
        answer="a (Source: X). Next step: y",
        intent="vpn",
        outcome="resolved",
        tool_calls=[],
    )
    assert (
        j.score(trace_id="t1", **kw) == j.score(trace_id="t1", **kw) != j.score(trace_id="t2", **kw)
    )


def test_pick_judge_offline():
    assert isinstance(pick_judge(dry_run=True, model="x"), OfflineJudge)
    assert isinstance(pick_judge(dry_run=False, model="x"), OfflineJudge)  # no key in tests
    assert set(CRITERIA) == {"resolved", "grounded", "safe_escalation"}


def test_run_judge_samples_and_skips_scored(replayed_store):
    before = len(replayed_store.scores(name="judge_overall"))
    summary = run_judge(replayed_store, rate=1.0, dry_run=True, write_langfuse=False)
    assert summary.candidates > 0 and summary.skipped_already == before
    assert len(replayed_store.scores(name="judge_overall")) >= before
    again = run_judge(replayed_store, rate=1.0, dry_run=True)
    assert again.scored == 0 and again.skipped_already == len(
        replayed_store.scores(name="judge_overall")
    )
    assert "judge=offline-heuristic" in summary.render()


def test_feedback_record_and_correlate(replayed_store):
    record_feedback(replayed_store, trace_id="zzz", thumbs=-1, tenant="ops", reason="unhelpful")
    s = correlate(replayed_store)
    assert s.feedback_count > 0 and 0 <= s.agreement <= 1 and "ops" in s.by_tenant
    assert "feedback=" in s.render()


def test_feedback_validation(store):
    import pytest

    with pytest.raises(ValueError):
        record_feedback(store, trace_id="t", thumbs=5)


def test_select_bad_traces_and_write(replayed_store, tmp_path):
    items = select_bad_traces(replayed_store, threshold=0.99, limit=10)
    assert items and all(it.source_trace_id for it in items) and len(items) <= 10
    assert "NW-" not in items[0].input["message"] or "<EMPLOYEE_ID:" in items[0].input["message"]
    n = write_jsonl(items, tmp_path / "d.jsonl")
    assert n == len(items) and (tmp_path / "d.jsonl").exists()


def test_synthetic_drift_flags_quality_regression():
    results = synthetic_comparison(seed=11, sessions=80)
    by = {r.metric: r for r in results}
    assert by["judge_overall"].status == "alert" and by["judge_overall"].mean_delta_pct < -8
    assert by["cost_per_request_usd"].mean_delta_pct < 0  # v2 is cheaper
    md = render(results, "t")
    assert "alert" in md and "| judge_overall |" in md


def test_compare_stores_identical_is_ok():
    _, a = replay_day(4, sessions=60, judge_rate=0.8)
    _, b = replay_day(4, sessions=60, judge_rate=0.8)
    res = compare_stores(a, b)
    assert all(r.status in {"ok", "insufficient"} for r in res)


def test_judge_max_calls_caps_a_run(monkeypatch, tmp_path, capsys):
    """JUDGE_MAX_CALLS bounds the judge bill per run (production docs, Lecture 8.2)."""
    from evals.online_judge import main

    monkeypatch.setenv("JUDGE_MAX_CALLS", "5")
    rc = main(["--store", str(tmp_path / "j.sqlite"), "--seed", "3", "--rate", "1.0", "--dry-run"])
    out = capsys.readouterr().out
    assert rc == 0 and "scored=5 " in out


def test_judge_always_judges_thumbs_down(store):
    """A thumbs-down trace is judged even at sample rate 0 (JudgeSamplingPolicy tail rule)."""
    from telemetry.local_store import ScoreRecord

    replay_day(3, sessions=30, store=store, judge_rate=0.0, feedback_rate=0.0)
    agents = store.spans(kind="agent")
    escalated = {s.trace_id for s in agents if s.attr("atlas.escalated")}  # also always judged
    agent = next(s for s in agents if s.attr("atlas.outcome") == "resolved")
    store.add_score(ScoreRecord(agent.trace_id, "user_feedback", 0.0, "user", "unhelpful", 0.0))
    summary = run_judge(store, rate=0.0, dry_run=True, write_langfuse=False)
    assert summary.sampled == summary.scored == 1 + len(escalated)
    assert {s.trace_id for s in store.scores(name="judge_overall")} == {agent.trace_id} | escalated


def test_judge_cap_reports_sampled_equal_to_scored(replayed_store):
    summary = run_judge(replayed_store, rate=1.0, limit=4, dry_run=True, write_langfuse=False)
    assert summary.scored == 4 and summary.sampled == 4


def test_judge_main_initialises_langfuse_when_keys_set(monkeypatch, tmp_path):
    """make judge with keys: the client is created, so create_score is not a silent no-op."""
    import telemetry.langfuse_setup as lfs
    from evals.online_judge import main

    calls = []
    monkeypatch.setattr(lfs, "init_langfuse", lambda settings=None, **_k: calls.append(1))
    store_path = str(tmp_path / "j.sqlite")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    main(["--store", store_path, "--seed", "3", "--limit", "1", "--dry-run"])
    assert calls == []  # OFFLINE=1 without --langfuse stays offline
    main(["--store", store_path, "--limit", "1", "--dry-run", "--langfuse"])
    assert calls == [1]
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY")
    main(["--store", store_path, "--limit", "1", "--dry-run", "--langfuse"])
    assert calls == [1]  # no keys: never
