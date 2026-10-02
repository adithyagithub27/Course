"""Production layer: drift monitor, governance, scorecard, benchmark, capstone, dashboard."""

import pytest

from capstone.platform import QualityPlatform
from monitoring.drift_monitor import DriftMonitor, monitor_from_rows, simulate_weeks
from monitoring.governance import AuditTrail, release_allowed
from monitoring.scorecard import EXAMPLE_AGENTS, arrow, build_scorecard, light, render_markdown
from performance.benchmark import BENCHMARK_QUERIES, run_benchmark
from performance.cost import route_model
from performance.reliability import measure_reliability
from agents.support_agent import run_support_agent


@pytest.mark.performance
def test_drift_alerts_fire_after_the_decline():
    alerts = monitor_from_rows(simulate_weeks()).check()
    assert [(a.day, a.metric, a.kind) for a in alerts] == [("2026-09-24", "faithfulness", "baseline_drop"),
                                                           ("2026-09-28", "faithfulness", "threshold"),
                                                           ("2026-09-28", "task_completion", "baseline_drop")]


def test_drift_monitor_quiet_when_stable():
    mon = DriftMonitor()
    for d in range(14):
        mon.record(f"2026-09-{d + 1:02d}", "faithfulness", 0.9)
    assert mon.check() == []


def test_governance_gate_and_tamper_evidence(tmp_path):
    trail = AuditTrail(tmp_path / "audit.jsonl")
    trail.log("evaluation", "ci", "v2", {"pass_rate": 0.9, "averages": {"Faithfulness": 0.9, "Answer Relevancy": 0.9}})
    trail.log("redteam", "ci", "v2", {"findings": 0})
    assert release_allowed(trail, "v2")[1] == ["missing approval: QA lead", "missing approval: Product owner"]
    trail.log("approval", "qa", "v2", {"role": "QA lead"})
    trail.log("approval", "po", "v2", {"role": "Product owner"})
    assert release_allowed(trail, "v2") == (True, [])
    text = trail.path.read_text().replace('"pass_rate": 0.9', '"pass_rate": 0.99')
    trail.path.write_text(text)
    assert not trail.verify()


def test_scorecard():
    assert light(0.9, 0.85) == "GREEN" and light(0.82, 0.85) == "AMBER" and light(0.7, 0.85) == "RED"
    assert arrow(0.9, 0.8) == "up" and arrow(0.8, 0.8) == "flat"
    card = build_scorecard(EXAMPLE_AGENTS, week="2026-09-28")
    assert [a["overall"] for a in card["agents"]] == ["GREEN", "AMBER", "RED"]
    assert "| TechCorp Support | [G] |" in render_markdown(card)


@pytest.mark.performance
def test_benchmark_and_routing():
    full = run_benchmark(BENCHMARK_QUERIES[:5], model="gpt-4.1").summary()
    routed = run_benchmark(BENCHMARK_QUERIES[:5], router=route_model).summary()
    assert routed["avg_cost_usd"] < full["avg_cost_usd"]
    assert full["latency_p95_s"] >= full["latency_p50_s"] > 0


@pytest.mark.performance
def test_reliability_is_consistent_offline():
    rep = measure_reliability(run_support_agent, ["What are your pricing plans?", "Check my account please, CUST-002"], runs=3)
    assert rep.failure_rate == 0 and rep.consistency == 1.0 and rep.loops == 0


def test_capstone_banking_stage_ships():
    r = QualityPlatform().run("banking_v2")
    assert r["gate"]["ship"] and r["security"]["passed"] == 16
    assert "SHIP" in QualityPlatform.render_report(r)


def test_dashboard_helpers():
    from reports.quality_dashboard import category_table

    report = {"details": [{"category": "faq", "passed": True}, {"category": "faq", "passed": False}]}
    assert category_table(report) == [{"category": "faq", "cases": 2, "passed": 1, "pass_rate": 0.5}]
