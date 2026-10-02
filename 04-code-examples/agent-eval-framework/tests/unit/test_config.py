"""Unit: model names, offline switch, prices, thresholds (decisions A8, T3)."""

import pytest

from config import settings
from config.thresholds import DIMENSIONS, check_threshold, gates, load_thresholds, metric_dimension


def test_default_models_follow_decision_a8(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_JUDGE_MODEL", raising=False)
    assert settings.agent_model() == "gpt-4.1-mini"
    assert settings.judge_model() == "gpt-4.1"


def test_models_can_be_overridden(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-nano")
    assert settings.agent_model() == "gpt-4.1-nano"


@pytest.mark.parametrize("flag,key,expected", [("1", "sk-x", True), ("0", "sk-x", False), ("", "", True), ("", "sk-x", False)])
def test_offline_switch(monkeypatch, flag, key, expected):
    monkeypatch.setenv("OFFLINE", flag)
    monkeypatch.setenv("OPENAI_API_KEY", key)
    assert settings.is_offline() is expected


def test_prices_and_dated_snapshots():
    assert settings.price_for("gpt-4.1-mini-2025-04-14") == settings.PRICES_PER_1M["gpt-4.1-mini"]
    assert settings.cost_usd("gpt-4.1-mini", 1_000_000, 0) == pytest.approx(0.40)
    assert settings.cost_usd("gpt-4.1", 0, 1_000_000) == pytest.approx(8.00)


def test_five_dimensions_in_config():
    assert DIMENSIONS == ["correctness", "faithfulness", "relevance", "safety", "reliability"]
    assert metric_dimension("faithfulness") == "faithfulness"
    assert metric_dimension("answer_relevancy") == "relevance"


def test_thresholds_and_lower_is_better():
    t = load_thresholds()
    assert t["faithfulness"] == 0.8 and t["hallucination"] == 0.7
    assert check_threshold("faithfulness", 0.85)["passed"]
    assert not check_threshold("max_cost_per_task_usd", 0.5)["passed"]
    assert check_threshold("unknown_metric", 0.1)["passed"]


def test_env_threshold_override(monkeypatch):
    monkeypatch.setenv("EVAL_THRESHOLD_FAITHFULNESS", "0.95")
    assert load_thresholds()["faithfulness"] == 0.95


def test_gates():
    g = gates()
    assert g["pr_pass_rate"] == 0.8 and g["critical_metric_min"] == 0.7 and g["regression_tolerance"] == 0.05
