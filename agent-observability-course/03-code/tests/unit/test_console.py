import json

from console.ops_console import build_summary, main, render_text
from northwind.config import TENANTS, Settings


def test_build_summary_shape(replayed_store):
    s = build_summary(replayed_store, Settings.from_env({}))
    for key in [
        "requests",
        "sessions",
        "total_cost_usd",
        "cost_by_tenant",
        "cost_by_feature",
        "cost_by_model",
        "hourly_cost",
        "latency",
        "ttft",
        "quality",
        "budgets",
        "slos",
        "tools",
        "alerts",
        "outcomes",
    ]:
        assert key in s
    assert s["requests"] > 0 and set(s["cost_by_tenant"]) <= set(TENANTS) and len(s["budgets"]) == 4
    assert s["quality"]["judge_count"] > 0 and s["latency"]["p95"] > 0
    json.dumps(s, default=str)  # serialisable


def test_render_text_sections(replayed_store):
    txt = render_text(build_summary(replayed_store, Settings.from_env({})))
    for section in [
        "ATLAS OPS CONSOLE",
        "Cost by tenant",
        "Cost by feature",
        "Latency",
        "Quality",
        "Budgets",
        "SLOs",
        "Alerts",
    ]:
        assert section in txt


def test_cli_text_mode_with_replay(tmp_path, capsys):
    rc = main(["--text", "--store", str(tmp_path / "s.sqlite"), "--seed", "3"])
    out = capsys.readouterr().out
    assert rc == 0 and "ATLAS OPS CONSOLE" in out and "requests=" in out


def test_cli_json_mode(tmp_path, capsys):
    rc = main(
        [
            "--json",
            "--store",
            str(tmp_path / "s.sqlite"),
            "--seed",
            "3",
            "--incidents",
            "latency_regression",
        ]
    )
    data = json.loads(capsys.readouterr().out)
    assert rc == 0 and data["scenarios"].get("slow_provider", 0) > 0
    assert any(a["rule"] == "latency_p95" for a in data["alerts"])
