"""console/data.py: the numbers behind every Ops Console page."""

from __future__ import annotations

import pytest

from console import data as cd
from northwind.config import TENANTS, Settings
from simulator.replay import replay_day
from telemetry.local_store import LocalSpanStore


@pytest.fixture(scope="module")
def d():
    _, store = replay_day(
        3, sessions=120, judge_rate=0.6, feedback_rate=0.4, incidents="cost_spike"
    )
    yield cd.StoreData.load(store)
    store.close()


def test_headline_matches_store(d):
    h = cd.headline(d)
    assert h["requests"] == len(d.requests) and h["sessions"] > 0
    assert h["total_cost_usd"] > 0 and 0 < h["p50_ms"] <= h["p95_ms"]
    assert h["judge_overall_mean"] is not None and h["start"].startswith("2026-09-14")


def test_cost_showback_by_feature_has_real_features(d):
    features = {r["key"] for r in cd.cost_by(d, "feature")}
    assert "chat" not in features and "policy_question" in features
    tenants = cd.cost_by(d, "tenant")
    assert {r["key"] for r in tenants} <= set(TENANTS)
    assert tenants[0]["cost_usd"] >= tenants[-1]["cost_usd"]
    t = cd.cost_tiles(d)
    assert t["cost_per_resolved_session_usd"] > 0 and 0 <= t["cache_hit_ratio"] <= 1


def test_top_sessions_link_to_traces(d):
    rows = cd.top_sessions(d, 10)
    assert len(rows) == 10 and rows[0]["cost_usd"] >= rows[-1]["cost_usd"]
    assert all(r["first_trace_id"] in d.by_trace for r in rows)


def test_waterfall_is_parent_first_with_offsets(d):
    trace_id = cd.top_sessions(d, 1)[0]["first_trace_id"]
    rows = cd.waterfall(d, trace_id)
    assert rows[0]["kind"] == "agent" and rows[0]["depth"] == 0 and rows[0]["start_ms"] == 0
    assert any(r["kind"] == "generation" and r["depth"] == 2 for r in rows)
    assert cd.waterfall(d, "nope") == []
    session = d.by_trace[trace_id][0].attr("session.id")
    assert cd.session_traces(d, session)[0]["trace_id"]


def test_cost_spike_shows_in_hourly_unit_costs_and_retrieval(d):
    unit = {r["ts"]: r for r in cd.hourly_unit_costs(d, "ops")}
    before = [r for r in unit.values() if r["hour"] < "09:00" and r["requests"]]
    during = [r for r in unit.values() if "10:00" <= r["hour"] < "12:00" and r["requests"]]
    assert max(r["mean_input_tokens_per_generation"] for r in during) > 1.5 * max(
        r["mean_input_tokens_per_generation"] for r in before
    )
    retr = cd.retrieval_hourly(d)
    ops_k = [
        r["mean_top_k"] for r in retr if r["tenant"] == "ops" and "09:00" <= r["hour"] < "13:00"
    ]
    hr_k = [r["mean_top_k"] for r in retr if r["tenant"] == "hr"]
    assert max(ops_k) > 4 and max(hr_k) == 4
    assert all(r["mean_result_tokens"] > 0 for r in retr)


def test_reliability_shows_the_retry_storm(d):
    retries = cd.retries_hourly(d)
    assert retries and {r["reason"] for r in retries} == {"APITimeoutError"}
    assert all("10:00" <= r["hour"] <= "12:00" for r in retries)
    tools = cd.tool_error_share_hourly(d)
    assert {r["tool"] for r in tools} >= {"search_knowledge_base"}


def test_latency_views(d):
    s = cd.latency_summary(d)
    assert s["total"]["p95"] >= s["total"]["p50"] > 0 and s["ttft"]["count"] > 0
    assert cd.hourly_latency(d)[0]["p95_ms"] > 0
    types = {r["type"] for r in cd.span_p95_by_type_hourly(d)}
    assert {"agent", "generation", "retriever"} <= types
    assert any(r["ttft_p95_ms"] for r in cd.generation_timing_hourly(d))


def test_quality_views(d):
    q = cd.quality_summary(d)
    assert q["judged"] > 0 and 0 <= q["grounded_rate"] <= 1
    assert q["empty_retrieval_rate"] is not None and q["feedback_count"] > 0
    assert {r["score"] for r in cd.judge_hourly(d)} == {
        "judge_grounded",
        "judge_resolved",
        "judge_overall",
    }
    assert {r["prompt_version"] for r in cd.judge_by_prompt_version(d)} == {"v1"}
    lengths = cd.feedback_by_session_length(d)
    assert {r["turns"] for r in lengths} <= {"1", "2", "3", "4+"}
    agree = cd.judge_feedback_agreement(d)
    assert agree["overlap"] >= agree["agree"]
    for row in cd.disagreements(d):
        assert (row["feedback"] >= 0.75) != (row["judge_resolved"] >= 0.7)
    assert cd.feedback_hourly(d) and isinstance(cd.top_feedback_comments(d), list)


def test_budget_timeline_flags_the_ops_spike(d):
    rows = cd.budget_timeline(d, Settings.from_env({}))
    ops = [r for r in rows if r["tenant"] == "ops"]
    assert ops[-1]["cumulative_usd"] == pytest.approx(
        sum(r.cost_usd for r in d.generations if r.tenant == "ops"), rel=1e-6
    )
    assert any(r["anomaly"] for r in ops)
    assert all(r["soft_cap_usd"] == 25.0 for r in rows)


def test_traffic_and_shadow(d):
    rows = cd.traffic(d, bin_s=300)
    assert sum(r["requests"] for r in rows) == len(d.requests)
    shadow = cd.shadow_traffic(d, bin_s=300)
    assert shadow["source"] == "replayed plan, seed 2" and shadow["rows"]


def test_shadow_uses_previous_week_when_present():
    from datetime import date

    store = LocalSpanStore(":memory:")
    replay_day(3, sessions=30, store=store, judge_rate=0.0, day=date(2026, 9, 7))
    replay_day(3, sessions=30, store=store, judge_rate=0.0)
    d = cd.StoreData.load(store)
    shadow = cd.shadow_traffic(d, bin_s=3600)
    assert shadow["source"] == "previous week"
    assert min(r["ts"] for r in shadow["rows"]) >= max(r.timestamp for r in d.requests) - 86_400


def test_safety_rates(d):
    rows = cd.safety_hourly(d)
    assert sum(r["requests"] for r in rows) == len(d.requests)
    assert all(0 <= r["injection_rate"] <= 1 for r in rows)


def test_live_page_follows_the_newest_conversation(settings):
    """1.1: a loop conversation written by the live exporter drives the meter and the alerts."""
    from app.agent import AtlasAgent
    from telemetry.otel_setup import configure_tracing, force_flush

    store = LocalSpanStore(":memory:")
    configure_tracing(settings, exporter_kind="none", store=store, batch=False)
    r = AtlasAgent(settings).run("Where is my ticket TCK-100231?", tenant="ops", scenario="loop")
    force_flush()
    v = cd.live(cd.StoreData.load(store), window_s=600)
    assert v["steps"] == settings.max_steps == r.steps
    assert len(v["context_tokens"]) == settings.max_steps
    assert v["context_tokens"] == sorted(v["context_tokens"])
    assert v["trace_cost_usd"] == pytest.approx(r.cost_usd, rel=1e-6)
    assert v["cost_by_tenant"]["ops"] > 0 and set(v["cost_by_tenant"]) >= set(TENANTS)
    rules = {a["rule"]: a["detail"] for a in v["alerts"]}
    assert rules["tool_error_rate"] == "lookup_ticket 100% over 60 s (ops)"
    assert "step_limit_reached" in rules


def test_compare_two_stores(tmp_path):
    a, b = tmp_path / "base.sqlite", tmp_path / "cache.sqlite"
    replay_day(
        3,
        sessions=40,
        store=LocalSpanStore(a),
        judge_rate=0.5,
        settings=Settings.from_env({"ATLAS_PROMPT_CACHE": "0", "ATLAS_CONTEXT_DIET": "0"}),
    )
    replay_day(
        3,
        sessions=40,
        store=LocalSpanStore(b),
        judge_rate=0.5,
        settings=Settings.from_env({"ATLAS_PROMPT_CACHE": "1", "ATLAS_CONTEXT_DIET": "0"}),
    )
    rows = cd.compare([a, b])
    assert rows[0]["cost_change_pct"] == 0.0 and rows[1]["cost_change_pct"] < 0
    assert rows[1]["cache_hit_ratio"] > rows[0]["cache_hit_ratio"]
