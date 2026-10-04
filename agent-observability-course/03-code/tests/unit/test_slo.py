import pytest

from northwind.cost import CostRecord
from northwind.slo import (
    DEFAULT_SLOS,
    SLI,
    SLO,
    burn_alert,
    burn_rate,
    compute_slis,
    error_budget,
    error_budget_remaining,
)


def test_sli_value_and_bad():
    s = SLI("x", 95, 100)
    assert s.value == 0.95 and s.bad == 5
    assert SLI("empty", 0, 0).value == 1.0


def test_slo_validation():
    with pytest.raises(ValueError):
        SLO("x", 1.5)
    assert SLO("x", 0.99).error_budget_fraction == pytest.approx(0.01)


def test_error_budget_remaining():
    slo = SLO("x", 0.95)
    assert error_budget_remaining(slo, SLI("x", 100, 100)) == 1.0
    assert error_budget_remaining(slo, SLI("x", 95, 100)) == pytest.approx(0.0)
    assert error_budget_remaining(slo, SLI("x", 90, 100)) == pytest.approx(-1.0)
    assert error_budget(slo, SLI("x", 100, 100)) == 1.0


def test_burn_rate():
    slo = SLO("x", 0.95)
    assert burn_rate(slo, SLI("x", 95, 100)) == pytest.approx(1.0)
    assert burn_rate(slo, SLI("x", 50, 100)) == pytest.approx(10.0)
    assert burn_rate(SLO("y", 1.0), SLI("y", 9, 10)) == float("inf")


@pytest.mark.parametrize(
    "rate,window,expected",
    [
        (15, "1h", "page"),
        (14, "1h", None),
        (6.5, "6h", "ticket"),
        (3.5, "1d", "ticket"),
        (0.5, "3d", None),
    ],
)
def test_burn_alert(rate, window, expected):
    assert burn_alert(rate, window) == expected


def _rec(i, outcome="resolved", lat=1000.0, cost=0.01):
    return CostRecord(
        trace_id=f"t{i}",
        tenant="ops",
        model="m",
        input_tokens=1,
        output_tokens=1,
        cost_usd=cost,
        timestamp=0,
        session_id=f"s{i}",
        latency_ms=lat,
        outcome=outcome,
    )


def test_compute_slis():
    recs = [_rec(i) for i in range(8)] + [
        _rec(8, "escalated"),
        _rec(9, "error", lat=9000, cost=0.2),
    ]
    snap = compute_slis(
        recs,
        latency_budget_ms=4000,
        cost_budget_usd=0.05,
        judge_scores=[0.9, 0.5, 0.8],
        tool_calls=10,
        tool_errors=1,
    )
    s = snap.slis
    assert s["task_success"].value == 0.9 and s["containment"].value == 0.8
    assert s["latency"].value == 0.9 and s["cost"].value == 0.9
    assert s["quality"].value == pytest.approx(2 / 3) and s["tool_success"].value == 0.9
    assert snap.p95_latency_ms > 1000 and snap.cost_per_resolved_session == pytest.approx(0.01)


def test_snapshot_report_rows():
    snap = compute_slis([_rec(i) for i in range(5)])
    rows = {r["sli"]: r for r in snap.report(DEFAULT_SLOS)}
    assert rows["task_success"]["ok"] is True and rows["task_success"]["burn_rate"] == 0.0
    assert set(DEFAULT_SLOS) == {
        "task_success",
        "containment",
        "tool_success",
        "latency",
        "cost",
        "quality",
    }
