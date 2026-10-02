"""
promptfoo Python provider: lets promptfoo attack the REAL tool-calling agent.

promptfoo calls ``call_api(prompt, options, context)`` for every test and
grades what comes back. We run the actual agent (tools, mock backends and all)
and return its reply plus the tool calls it made, so assertions can check
actions, not just words.

Select the target in the YAML with ``config.agent``:
    support            TechCorp support agent (default)
    banking            SecureBank v1 (as launched, vulnerable)
    banking_hardened   SecureBank v2 (the fix)

Offline (OFFLINE=1) the agents use the deterministic mock LLM, so the static
suite in promptfooconfig.yaml runs with no API key.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def call_api(prompt: str, options: dict, context: dict) -> dict:
    from agents.banking_agent import run_banking_agent
    from agents.support_agent import run_support_agent

    agent = (options.get("config") or {}).get("agent", "support")
    if agent == "banking":
        result = run_banking_agent(prompt, hardened=False)
    elif agent == "banking_hardened":
        result = run_banking_agent(prompt, hardened=True)
    else:
        result = run_support_agent(prompt)

    return {
        "output": result["response"],
        "metadata": {
            "tool_calls": [{"tool": t["tool"], "arguments": t["arguments"]} for t in result["tool_calls"]],
            "tools": [t["tool"] for t in result["tool_calls"]],
        },
        "tokenUsage": {"total": result["total_tokens"]},
    }
