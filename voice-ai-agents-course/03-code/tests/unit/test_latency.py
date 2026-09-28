"""Unit tests for maple.latency (lectures 1.4, 9.8, 10.1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from maple.latency import (
    LatencyBudget,
    check_budget,
    format_report,
    load_jsonl,
    percentile,
    samples_from_metrics,
    summarize,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_metrics.jsonl"


@pytest.mark.parametrize(
    ("values", "p", "expected"),
    [
        ([1, 2, 3, 4, 5], 50, 3),
        ([1, 2, 3, 4], 50, 2.5),
        ([10], 95, 10),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 90, 9.1),
        ([5, 1, 4, 2, 3], 0, 1),
        ([5, 1, 4, 2, 3], 100, 5),
    ],
)
def test_percentile_matches_numpy_linear(values: list[float], p: float, expected: float) -> None:
    assert percentile(values, p) == pytest.approx(expected)


def test_percentile_errors() -> None:
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1, 2], 101)


def test_percentile_against_numpy_if_available() -> None:
    np = pytest.importorskip("numpy")
    values = [812, 640, 1210, 590, 980, 1500, 700, 655, 720, 2300, 610]
    for p in (50, 90, 95, 99):
        assert percentile(values, p) == pytest.approx(float(np.percentile(values, p)))


def test_summarize() -> None:
    s = summarize([100, 200, 300, 400])
    assert s.count == 4 and s.mean == 250 and s.p50 == 250 and s.max == 400


def test_check_budget_reports_only_violations() -> None:
    budget = LatencyBudget(llm_ttft=500, tts_ttfb=300, percentile=95)
    samples = {"llm_ttft": [400, 450, 900, 950], "tts_ttfb": [100, 120, 130], "unknown": [1e9]}
    violations = check_budget(samples, budget)
    assert [v.stage for v in violations] == ["llm_ttft"]
    assert violations[0].over_by_ms > 0
    assert "llm_ttft: p95=" in str(violations[0])


def test_empty_stages_are_skipped() -> None:
    assert check_budget({}) == []


def test_samples_from_metrics_converts_and_joins() -> None:
    records = [
        {"type": "eou_metrics", "end_of_utterance_delay": 0.5, "transcription_delay": 0.2, "speech_id": "s1"},
        {"type": "llm_metrics", "ttft": 0.4, "speech_id": "s1"},
        {"type": "tts_metrics", "ttfb": 0.15, "speech_id": "s1"},
        {"type": "llm_metrics", "ttft": -1, "speech_id": "s2"},  # not measured
        {"type": "vad_metrics", "idle_time": 1.0},
    ]
    samples = samples_from_metrics(records)
    assert samples["eou_delay"] == [500.0]
    assert samples["stt_final"] == [200.0]
    assert samples["llm_ttft"] == [400.0]
    assert samples["tts_ttfb"] == [150.0]
    assert samples["voice_to_voice"] == [pytest.approx(1050.0)]


def test_load_jsonl_rejects_bad_lines(tmp_path: Path) -> None:
    path = tmp_path / "m.jsonl"
    path.write_text('{"type": "llm_metrics", "ttft": 0.3}\n\nnot json\n')
    with pytest.raises(ValueError, match=r"m\.jsonl:3"):
        load_jsonl(path)


def test_sample_data_is_realistic_and_within_default_budget() -> None:
    records = load_jsonl(DATA)
    assert len(records) >= 40
    samples = samples_from_metrics(records)
    for stage in ("eou_delay", "llm_ttft", "tts_ttfb", "voice_to_voice"):
        assert len(samples[stage]) >= 8
    assert check_budget(samples) == []
    strict = LatencyBudget(voice_to_voice=800)
    assert [v.stage for v in check_budget(samples, strict)] == ["voice_to_voice"]


def test_format_report_has_all_present_stages() -> None:
    samples = samples_from_metrics(load_jsonl(DATA))
    report = format_report(samples)
    for stage in samples:
        assert stage in report
    assert "OK" in report


def test_budget_as_dict_excludes_percentile() -> None:
    d = LatencyBudget().as_dict()
    assert "percentile" not in d and set(d) == {
        "eou_delay",
        "stt_final",
        "llm_ttft",
        "tts_ttfb",
        "voice_to_voice",
    }
    json.dumps(d)
