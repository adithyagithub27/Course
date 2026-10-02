"""End-to-end: regression vs baseline and the CI quality gate (Modules 11, 12)."""

import json

import pytest

from regression.regression_suite import PROMPT_V2_REGRESSED, compare, evaluate_version, load_baseline, regressed_agent
from reports.quality_gate import evaluate_gate, main as gate_main, markdown_summary
from reports.run_eval import main as run_eval


@pytest.mark.regression
def test_v1_matches_baseline():
    diff = compare(load_baseline("support_v1"), evaluate_version())
    assert not diff["regression"], diff


@pytest.mark.regression
def test_prompt_regression_is_caught():
    assert "Only state prices" not in PROMPT_V2_REGRESSED
    diff = compare(load_baseline("support_v1"), evaluate_version(regressed_agent, version="v2"))
    assert diff["regression"] and set(diff["newly_failing"]) == {"GS-01", "GS-02", "GS-03"}
    assert "Faithfulness" in diff["regressed_metrics"]


@pytest.mark.smoke
def test_smoke_subset(tmp_path):
    report = run_eval(["--smoke", "--out", str(tmp_path / "smoke.json")])
    assert report["total"] == 3 and report["pass_rate"] == 1.0


def test_gate_blocks_bad_change_and_writes_pr_comment(tmp_path):
    good = run_eval(["--out", str(tmp_path / "good.json")])
    bad = run_eval(["--prompt-variant", "regressed", "--out", str(tmp_path / "bad.json")])
    assert evaluate_gate(good) == (True, [])
    ok, reasons = evaluate_gate(bad)
    assert not ok and any("pass rate 70%" in r for r in reasons)
    assert "FAILED" in markdown_summary(bad, ok, reasons)
    assert gate_main([str(tmp_path / "good.json"), "--summary", str(tmp_path / "s.md"), "--baseline", "support_v1"]) == 0
    assert gate_main([str(tmp_path / "bad.json"), "--baseline", "support_v1"]) == 1
    assert json.loads((tmp_path / "good.json").read_text())["dataset"] == "golden_support"
