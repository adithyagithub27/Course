import json

from telemetry.local_store import LocalSpanStore, ScoreRecord, SpanRecord


def _span(i, kind="agent", status="OK", **attrs):
    a = {
        "atlas.tenant": "ops",
        "session.id": "s1",
        "atlas.cost_usd": 0.001,
        "gen_ai.request.model": "gpt-4.1-mini",
        "gen_ai.usage.input_tokens": 100,
        "gen_ai.usage.output_tokens": 10,
    }
    a.update(attrs)
    return SpanRecord(
        trace_id=f"t{i}",
        span_id=f"sp{i}",
        name="invoke_agent atlas",
        kind=kind,
        start_time=1000.0 + i,
        end_time=1001.5 + i,
        status=status,
        attributes=a,
    )


def test_insert_query_count(store: LocalSpanStore):
    assert (
        store.insert(
            [
                _span(1),
                _span(2, kind="generation"),
                _span(3, kind="tool", **{"gen_ai.tool.name": "lookup_ticket"}),
            ]
        )
        == 3
    )
    assert store.count() == 3 and store.count("agent") == 1
    assert store.spans(kind="tool")[0].attr("gen_ai.tool.name") == "lookup_ticket"
    assert store.spans(since=1002.0)[0].trace_id == "t2"
    assert store.spans(tenant="ops", limit=1)


def test_duplicate_span_id_replaces(store):
    store.insert([_span(1)])
    store.insert([_span(1, **{"atlas.cost_usd": 0.5})])
    assert store.count() == 1 and store.spans()[0].attr("atlas.cost_usd") == 0.5


def test_cost_and_latency_records(store):
    store.insert(
        [
            _span(1, **{"atlas.outcome": "resolved", "atlas.steps": 2, "atlas.ttft_ms": 400.0}),
            _span(2, kind="generation"),
        ]
    )
    recs = store.cost_records("request")
    assert len(recs) == 1 and recs[0].steps == 2 and recs[0].latency_ms == 1500.0
    gens = store.cost_records("generation")
    assert len(gens) == 1 and gens[0].model == "gpt-4.1-mini"
    lat = store.latency_samples()
    assert lat[0].ttft_ms == 400.0


def test_scores_roundtrip(store):
    store.add_score(ScoreRecord("t1", "judge_overall", 0.8, "judge", "", 5.0, "ops", "s1"))
    store.add_score(ScoreRecord("t1", "user_feedback", 1.0, "user", "", 6.0, "ops", "s1"))
    assert store.score_values("judge_overall") == [0.8]
    assert (
        len(store.scores(source="user")) == 1 and store.scores(since=5.5)[0].name == "user_feedback"
    )


def test_tool_stats(store):
    store.insert(
        [
            _span(1, kind="tool", status="ERROR", **{"gen_ai.tool.name": "lookup_ticket"}),
            _span(2, kind="tool", **{"gen_ai.tool.name": "lookup_ticket"}),
        ]
    )
    assert store.tool_stats() == {"lookup_ticket": {"calls": 2, "errors": 1}}


def test_jsonl_export_import_roundtrip(store, tmp_path):
    store.insert([_span(1), _span(2, kind="generation")])
    store.add_score(ScoreRecord("t1", "judge_overall", 0.9, "judge", "", 1.0, "ops", "s1"))
    p = tmp_path / "spans.jsonl"
    n = store.export_jsonl(p, scores_path=tmp_path / "scores.jsonl")
    assert n == 2 and len(p.read_text().splitlines()) == 2
    other = LocalSpanStore.from_jsonl(p, tmp_path / "scores.jsonl")
    assert other.count() == 2 and other.score_values("judge_overall") == [0.9]
    line = json.loads(p.read_text().splitlines()[0])
    assert list(line) == sorted(line)  # sorted keys => deterministic files


def test_time_range_and_clear(store):
    assert store.time_range() == (0.0, 0.0)
    store.insert([_span(1), _span(5)])
    assert store.time_range() == (1001.0, 1006.5)
    store.clear()
    assert store.count() == 0


def test_span_record_helpers():
    r = _span(1)
    assert r.duration_ms == 1500.0 and SpanRecord.from_json(r.to_json()) == r
