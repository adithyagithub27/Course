import dataclasses

import pytest

from northwind.config import SCENARIOS, TENANTS, Settings, normalise_tenant_id, reload_settings


def test_defaults_are_offline_and_sane():
    s = Settings.from_env({})
    assert s.offline is True
    assert (
        s.model == "gpt-4.1-mini"
        and s.escalation_model == "gpt-4.1"
        and s.routing_model == "gpt-5-mini"
    )
    assert s.max_steps == 6 and s.retrieval_top_k == 4
    assert s.otel_exporter == "console"


@pytest.mark.parametrize(
    "value,expected",
    [("1", True), ("true", True), ("YES", True), ("0", False), ("false", False), ("", True)],
)
def test_offline_parsing(value, expected):
    assert Settings.from_env({"OFFLINE": value}).offline is expected


def test_env_overrides():
    s = Settings.from_env(
        {
            "ATLAS_MODEL": "gpt-4o-mini",
            "ATLAS_MAX_STEPS": "3",
            "BUDGET_P95_LATENCY_MS": "2500",
            "TENANT_SOFT_CAP_USD": "1.5",
            "OTEL_EXPORTER": "OTLP",
            "ATLAS_MAX_TOOL_RETRIES": "2",
            "ATLAS_PROMPT_LABEL": "staging",
            "ATLAS_STREAM": "0",
            "KB_MIN_SCORE": "0.9",
        }
    )
    assert (
        s.model == "gpt-4o-mini"
        and s.max_steps == 3
        and s.budget_p95_latency_ms == 2500
        and s.tenant_soft_cap_usd == 1.5
    )
    assert (
        s.otel_exporter == "otlp"
        and s.max_tool_retries == 2
        and s.prompt_label == "staging"
        and s.stream is False
        and s.kb_min_score == 0.9
    )


def test_bad_exporter_rejected():
    with pytest.raises(ValueError):
        Settings.from_env({"OTEL_EXPORTER": "jaeger-legacy"})


def test_bad_scenario_rejected():
    with pytest.raises(ValueError):
        Settings.from_env({"ATLAS_SCENARIO": "meteor"})


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_all_scenarios_accepted(scenario):
    assert Settings.from_env({"ATLAS_SCENARIO": scenario}).scenario == scenario


def test_with_overrides_validates_names():
    s = Settings.from_env({})
    assert s.with_overrides(max_steps=2).max_steps == 2
    with pytest.raises(TypeError):
        s.with_overrides(nonexistent=1)


def test_langfuse_enabled_requires_both_keys():
    assert not Settings.from_env({"LANGFUSE_PUBLIC_KEY": "pk"}).langfuse_enabled
    assert Settings.from_env(
        {"LANGFUSE_PUBLIC_KEY": "pk", "LANGFUSE_SECRET_KEY": "sk"}
    ).langfuse_enabled


def test_frozen():
    s = Settings.from_env({})
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.model = "x"  # type: ignore[misc]


def test_tenants_and_aliases():
    assert TENANTS == ("ops", "finance", "hr", "eng")
    assert normalise_tenant_id("logistics-ops") == "ops"
    assert normalise_tenant_id("ENG") == "eng"
    assert normalise_tenant_id("marketing") is None
    assert normalise_tenant_id(None) is None


def test_reload_settings_reads_env():
    s = reload_settings({"ATLAS_MODEL": "gpt-4.1-nano"})
    assert s.model == "gpt-4.1-nano"
    reload_settings({})


def test_dotenv_loaded_without_overriding_real_env(monkeypatch, tmp_path):
    """.env is read at startup; variables already in the environment win (make flags, prefixes)."""
    import northwind.config as cfg

    (tmp_path / ".env").write_text("ATLAS_TOP_K=9\nATLAS_PROMPT_VERSION=v2\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cfg, "_DOTENV_LOADED", False)
    monkeypatch.delenv("ATLAS_TOP_K", raising=False)
    monkeypatch.setenv("ATLAS_PROMPT_VERSION", "v1")
    monkeypatch.setenv("ATLAS_DOTENV", "1")
    try:
        s = Settings.from_env()
        assert s.retrieval_top_k == 9 and s.prompt_version == "v1"
    finally:
        import os

        os.environ.pop("ATLAS_TOP_K", None)
    monkeypatch.setattr(cfg, "_DOTENV_LOADED", False)
    monkeypatch.setenv("ATLAS_DOTENV", "0")  # the test suite's setting
    assert Settings.from_env().retrieval_top_k == Settings.retrieval_top_k
