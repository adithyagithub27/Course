import pytest

from northwind.latency import (
    LatencyBudget,
    LatencySample,
    RequestTiming,
    StepTiming,
    by_group,
    hourly_p95,
    percentile,
    summarize,
    violations,
)


@pytest.mark.parametrize(
    "values,p,expected",
    [
        ([1, 2, 3, 4, 5], 50, 3.0),
        ([1, 2, 3, 4, 5], 95, 4.8),
        ([1, 2, 3, 4, 5], 0, 1.0),
        ([1, 2, 3, 4, 5], 100, 5.0),
        ([7], 95, 7.0),
        ([10, 20], 50, 15.0),
    ],
)
def test_percentile_linear_interpolation(values, p, expected):
    assert percentile(values, p) == pytest.approx(expected)


def test_percentile_errors():
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1], 101)


def test_summarize_and_empty():
    s = summarize([100, 200, 300, 400, 1000])
    assert s.count == 5 and s.p50 == 300 and s.max == 1000 and s.mean == 400
    assert summarize([]).count == 0


def test_tpot_and_tokens_per_second():
    s = LatencySample(total_ms=1300, ttft_ms=300, output_tokens=101)
    assert s.tpot_ms == pytest.approx(10.0)
    assert s.tokens_per_second == pytest.approx(100.0)
    assert LatencySample(total_ms=100, output_tokens=1).tpot_ms is None


def test_violations_aggregate_and_per_sample():
    samples = [
        LatencySample(total_ms=500, ttft_ms=100, output_tokens=50, steps=1, trace_id=f"t{i}")
        for i in range(5)
    ]
    samples.append(
        LatencySample(total_ms=9000, ttft_ms=5000, output_tokens=10, steps=1, trace_id="slow")
    )
    v = violations(
        samples, LatencyBudget(total_p95_ms=4000, ttft_p95_ms=1000, per_step_ms=2500, tpot_ms=60)
    )
    metrics = {x.metric for x in v}
    assert {"total_p95_ms", "ttft_p95_ms", "per_step_ms", "tpot_ms"} <= metrics
    assert any(x.trace_id == "slow" for x in v)
    assert "budget" in str(v[0])


def test_no_violations_when_within_budget():
    samples = [LatencySample(total_ms=1000, ttft_ms=200, output_tokens=100) for _ in range(10)]
    assert violations(samples, LatencyBudget()) == []
    assert violations([], LatencyBudget()) == []


def test_request_timing_ttft_is_perceived():
    rt = RequestTiming(
        "t", (StepTiming(1, "m", 800, 300, 20, 100), StepTiming(2, "m", 1500, 400, 200))
    )
    assert rt.total_ms == 2300 and rt.ttft_ms == 1200 and rt.slowest_step.step == 2
    s = rt.to_sample()
    assert s.steps == 2 and s.output_tokens == 200 and s.ttft_ms == 1200
    assert (
        violations(
            [rt], LatencyBudget(total_p95_ms=1000, ttft_p95_ms=None, per_step_ms=None, tpot_ms=None)
        )[0].metric
        == "total_p95_ms"
    )


def test_by_group_and_hourly():
    samples = [
        LatencySample(100, tenant="a"),
        LatencySample(300, tenant="a"),
        LatencySample(50, tenant="b"),
    ]
    g = by_group(samples, "tenant")
    assert g["a"].count == 2 and g["b"].max == 50
    h = hourly_p95([(0, 100), (10, 300), (3700, 50)])
    assert set(h) == {0, 3600} and h[0] == pytest.approx(290)
