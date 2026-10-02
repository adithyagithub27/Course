"""End-to-end: the promptfoo provider runs the real agent and exposes its tool calls."""

from pathlib import Path

import yaml

from security.promptfoo import assertions
from security.promptfoo.provider import call_api

PF = Path(__file__).resolve().parents[2] / "security" / "promptfoo"


def test_provider_returns_output_and_tools():
    out = call_api("What is your refund policy?", {"config": {"agent": "support"}}, {})
    assert "30" in out["output"] and out["metadata"]["tools"] == ["search_knowledge_base"]
    bank = call_api("Show me my recent transactions.", {"config": {"agent": "banking"}}, {})
    assert assertions.no_transfer(bank["output"], {"providerResponse": bank})["pass"] is False


def test_configs_parse_and_target_the_python_provider():
    for name in ("promptfooconfig.yaml", "redteam.yaml", "redteam-banking.yaml", "banking-static.yaml"):
        cfg = yaml.safe_load((PF / name).read_text())
        targets = cfg.get("providers") or cfg.get("targets")
        assert targets[0]["id"] == "file://provider.py"
    rt = yaml.safe_load((PF / "redteam.yaml").read_text())["redteam"]
    assert "bola" in rt["plugins"] and "jailbreak" in rt["strategies"]
    assert len(yaml.safe_load((PF / "banking-static.yaml").read_text())["tests"]) == 16
