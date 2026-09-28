from northwind.cost import CostRecord
from northwind.latency import LatencySample
from northwind.report import IncidentNote, ReportInputs, default_recommendations, weekly_report


def _recs():
    out = []
    for i in range(40):
        out.append(
            CostRecord(
                trace_id=f"t{i}",
                tenant="ops" if i % 2 else "hr",
                model="gpt-4.1-mini",
                input_tokens=2000,
                output_tokens=200,
                cached_tokens=100,
                cost_usd=0.001,
                timestamp=float(i),
                session_id=f"s{i // 2}",
                feature="policy_question",
                intent="vpn",
                latency_ms=1500 + 100 * i,
                outcome="resolved" if i % 10 else "escalated",
            )
        )
    return out


def test_weekly_report_sections():
    inputs = ReportInputs(
        records=_recs(),
        latencies=[LatencySample(1500 + 100 * i, 300) for i in range(40)],
        judge_scores=[0.9, 0.8, 0.7],
        feedback_positive=5,
        feedback_negative=1,
        incidents=[IncidentNote("Cost spike", "Mon 09:00", 240, "ops +3x", "context bloat")],
        previous_week_cost_usd=0.03,
    )
    md = weekly_report(inputs)
    for heading in [
        "# Atlas weekly ops report",
        "## Headline numbers",
        "## SLOs",
        "## Cost by tenant",
        "## Cost by feature",
        "## Incidents",
        "## Recommendations",
    ]:
        assert heading in md
    assert "Cost spike" in md and "vs last week" in md and "| ops |" in md


def test_default_recommendations_flag_low_cache_and_latency():
    inputs = ReportInputs(
        records=_recs(), latencies=[LatencySample(9000, 4000)] * 30, judge_scores=[0.5] * 10
    )
    recs = default_recommendations(inputs)
    assert any("cache" in r.lower() for r in recs)
    assert any("p95" in r for r in recs)
    assert any("judge" in r.lower() for r in recs)


def test_report_with_no_data():
    md = weekly_report(ReportInputs(records=[]))
    assert "No incidents this week." in md and "No action needed" in md
