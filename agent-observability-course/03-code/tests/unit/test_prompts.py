import pytest

from app.prompts import PROMPT_NAME, PROMPTS, V2_MARKER, get_system_prompt, prompt_cache_key


def test_versions_and_marker():
    assert set(PROMPTS) == {"v1", "v2"} and PROMPT_NAME == "atlas-system"
    assert V2_MARKER in PROMPTS["v2"] and V2_MARKER not in PROMPTS["v1"]
    assert "Source:" in PROMPTS["v1"] and "Next step" in PROMPTS["v1"]


def test_get_system_prompt_local_and_unknown():
    text, version = get_system_prompt("v1")
    assert text == PROMPTS["v1"] and version == "v1"
    with pytest.raises(KeyError):
        get_system_prompt("v9")


def test_get_system_prompt_langfuse_falls_back_when_disabled():
    text, version = get_system_prompt("v2", use_langfuse=True, label="staging")
    assert text == PROMPTS["v2"] and version == "v2"


def test_cache_key_stable_per_tenant():
    assert prompt_cache_key("v1", "ops") == "atlas-v1-ops" != prompt_cache_key("v1", "hr")
