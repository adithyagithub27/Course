# Lab 06: Multi-Agent Failure Injection and Detection

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 07 — Multi-Agent System Testing                       |
| **Duration**       | 90 minutes                                                   |
| **Difficulty**     | Advanced                                                     |
| **Learning Objective** | Build a minimal 2-agent system (router + specialist), inject communication failures and delegation loops, verify the system detects and handles each failure, and log the failure chain for debugging. |

---

## Prerequisites

- Completed **Labs 01–05** (comfortable with agent testing patterns)
- Understanding of multi-agent architectures (router/dispatcher pattern)
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Verify dependencies

```bash
pip show openai python-dotenv
```

### 2. Create the lab workspace

```bash
mkdir -p tests/multi_agent
touch tests/multi_agent/__init__.py
```

---

## Step-by-Step Instructions

### Step 1 — Build a minimal 2-agent system

Create `agents/multi_agent_system.py`. This system has:

- A **Router Agent** that receives the query and decides which specialist to delegate to
- A **Billing Specialist** that handles billing questions
- A **Technical Specialist** that handles technical questions

```python
"""
Lab 06 — Multi-Agent System with Router + Specialists
A minimal multi-agent system for testing failure modes.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Failure Injection Flags ───────────────────────────────────────
# Set these to True to inject specific failures for testing
INJECT_COMMUNICATION_FAILURE = False
INJECT_INFINITE_LOOP = False
MAX_DELEGATION_DEPTH = 5


class AgentMessage:
    """Structured message passed between agents."""
    def __init__(self, sender: str, receiver: str, content: str,
                 message_type: str = "request"):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type  # request, response, error

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.message_type,
        }


class FailureLog:
    """Tracks failures in the multi-agent system."""
    def __init__(self):
        self.entries: list[dict] = []

    def log(self, failure_type: str, agent: str, details: str):
        self.entries.append({
            "failure_type": failure_type,
            "agent": agent,
            "details": details,
        })

    def has_failures(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> list[dict]:
        return self.entries


# ── Specialist Agents ─────────────────────────────────────────────
def billing_specialist(query: str) -> str:
    """Handle billing-related queries."""
    if INJECT_COMMUNICATION_FAILURE:
        raise ConnectionError("Billing service is unavailable")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a billing specialist for TechCorp. "
                "Answer billing questions concisely. "
                "Plans: Basic ($9.99/mo), Pro ($29.99/mo), Enterprise (custom). "
                "Refund policy: 30-day money-back guarantee."
            )},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content


def technical_specialist(query: str) -> str:
    """Handle technical-related queries."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a technical support specialist for TechCorp. "
                "Answer technical questions concisely. "
                "API rate limits: Basic (100/hr), Pro (1000/hr), Enterprise (unlimited). "
                "Password reset: Settings > Security > Reset Password."
            )},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content


# ── Router Agent ──────────────────────────────────────────────────
def router_agent(query: str, depth: int = 0) -> dict:
    """
    Route queries to the appropriate specialist.

    Returns:
        dict with keys: response, delegation_chain, failure_log
    """
    failure_log = FailureLog()
    delegation_chain = []

    # Guard: detect infinite loops
    if depth >= MAX_DELEGATION_DEPTH:
        failure_log.log(
            "infinite_loop",
            "router",
            f"Delegation depth {depth} exceeded max {MAX_DELEGATION_DEPTH}",
        )
        return {
            "response": "I apologize, but I'm experiencing a routing issue. "
                        "Let me connect you with a human agent.",
            "delegation_chain": delegation_chain,
            "failure_log": failure_log.summary(),
        }

    # Step 1: Decide which specialist to route to
    routing_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a routing agent. Classify the query and respond "
                "with ONLY one word: 'billing' or 'technical'. "
                "Billing: pricing, refunds, charges, plans, subscriptions. "
                "Technical: passwords, API, integrations, errors, features."
            )},
            {"role": "user", "content": query},
        ],
    )

    route = routing_response.choices[0].message.content.strip().lower()
    delegation_chain.append(AgentMessage("user", "router", query).to_dict())
    delegation_chain.append(
        AgentMessage("router", route, f"Routing to {route}").to_dict()
    )

    # Inject infinite loop: router always re-delegates to itself
    if INJECT_INFINITE_LOOP:
        result = router_agent(query, depth=depth + 1)
        delegation_chain.extend(result["delegation_chain"])
        if result["failure_log"]:
            failure_log.entries.extend(result["failure_log"])
        return {
            "response": result["response"],
            "delegation_chain": delegation_chain,
            "failure_log": failure_log.summary(),
        }

    # Step 2: Delegate to the appropriate specialist
    try:
        if "billing" in route:
            specialist_response = billing_specialist(query)
        elif "technical" in route:
            specialist_response = technical_specialist(query)
        else:
            specialist_response = (
                "I'm not sure which department can help with this. "
                "Let me escalate to a human agent."
            )
            failure_log.log(
                "routing_failure",
                "router",
                f"Unknown route: '{route}'",
            )
    except ConnectionError as e:
        failure_log.log(
            "communication_failure",
            route,
            str(e),
        )
        specialist_response = (
            f"I apologize, but the {route} team is temporarily unavailable. "
            "Your request has been logged and we'll follow up shortly."
        )
    except Exception as e:
        failure_log.log(
            "unexpected_error",
            route,
            str(e),
        )
        specialist_response = (
            "An unexpected error occurred. Let me escalate this "
            "to a human agent."
        )

    delegation_chain.append(
        AgentMessage(route, "user", specialist_response, "response").to_dict()
    )

    return {
        "response": specialist_response,
        "delegation_chain": delegation_chain,
        "failure_log": failure_log.summary(),
    }


if __name__ == "__main__":
    result = router_agent("What are your pricing plans?")
    print(f"Response: {result['response']}")
    print(f"Delegation chain: {json.dumps(result['delegation_chain'], indent=2)}")
    print(f"Failures: {result['failure_log']}")
```

### Step 2 — Run the system in normal mode

```bash
python agents/multi_agent_system.py
```

Verify you see a response routed through the billing specialist.

### Step 3 — Write tests for normal operation

Create `tests/multi_agent/test_multi_agent.py`:

```python
"""
Lab 06 — Multi-Agent System Tests
Run: pytest tests/multi_agent/test_multi_agent.py -v
"""

import pytest
from unittest.mock import patch
import agents.multi_agent_system as mas


class TestNormalOperation:
    """Verify the multi-agent system works correctly under normal conditions."""

    def test_billing_query_routes_correctly(self):
        """Billing questions should route to the billing specialist."""
        result = mas.router_agent("What are your pricing plans?")

        assert result["response"] is not None
        assert len(result["response"]) > 10
        assert len(result["failure_log"]) == 0, (
            f"Unexpected failures: {result['failure_log']}"
        )

        # Check delegation chain includes routing
        senders = [m["sender"] for m in result["delegation_chain"]]
        assert "router" in senders

    def test_technical_query_routes_correctly(self):
        """Technical questions should route to the technical specialist."""
        result = mas.router_agent("How do I reset my password?")

        assert result["response"] is not None
        assert len(result["failure_log"]) == 0

    def test_delegation_chain_is_logged(self):
        """Every delegation step should appear in the chain."""
        result = mas.router_agent("What is your refund policy?")

        chain = result["delegation_chain"]
        assert len(chain) >= 2, (
            f"Expected at least 2 delegation steps, got {len(chain)}"
        )
        # First message should be from user to router
        assert chain[0]["sender"] == "user"
        assert chain[0]["receiver"] == "router"
```

### Step 4 — Inject a communication failure and test detection

```python
class TestCommunicationFailure:
    """Test behavior when a specialist agent is unreachable."""

    def test_communication_failure_is_detected(self):
        """System should detect and log communication failures."""
        with patch.object(mas, "INJECT_COMMUNICATION_FAILURE", True):
            result = mas.router_agent("What are your pricing plans?")

        # The failure should be logged
        assert len(result["failure_log"]) > 0, (
            "Communication failure was not logged"
        )
        failure_types = [f["failure_type"] for f in result["failure_log"]]
        assert "communication_failure" in failure_types, (
            f"Expected 'communication_failure', got: {failure_types}"
        )

    def test_graceful_degradation_on_failure(self):
        """System should still provide a response when a specialist fails."""
        with patch.object(mas, "INJECT_COMMUNICATION_FAILURE", True):
            result = mas.router_agent("What are your pricing plans?")

        # Should still get a response (not crash)
        assert result["response"] is not None
        assert len(result["response"]) > 10

        # Response should acknowledge the problem
        response_lower = result["response"].lower()
        assert any(phrase in response_lower for phrase in [
            "unavailable", "apologize", "temporarily", "follow up",
            "error", "issue",
        ]), f"Response did not acknowledge the failure: {result['response']}"

    def test_failure_log_contains_details(self):
        """Failure log should include agent name and error details."""
        with patch.object(mas, "INJECT_COMMUNICATION_FAILURE", True):
            result = mas.router_agent("What are your pricing plans?")

        assert len(result["failure_log"]) > 0
        failure = result["failure_log"][0]
        assert "agent" in failure
        assert "details" in failure
        assert len(failure["details"]) > 0
```

### Step 5 — Inject an infinite delegation loop and test detection

```python
class TestInfiniteLoopDetection:
    """Test behavior when agents enter an infinite delegation loop."""

    def test_infinite_loop_is_detected(self):
        """System should detect and stop infinite delegation loops."""
        with patch.object(mas, "INJECT_INFINITE_LOOP", True):
            result = mas.router_agent("What are your pricing plans?")

        # The loop should be detected
        failure_types = [f["failure_type"] for f in result["failure_log"]]
        assert "infinite_loop" in failure_types, (
            f"Infinite loop was not detected. Failures: {failure_types}"
        )

    def test_loop_stops_at_max_depth(self):
        """Delegation chain should not exceed MAX_DELEGATION_DEPTH."""
        with patch.object(mas, "INJECT_INFINITE_LOOP", True):
            with patch.object(mas, "MAX_DELEGATION_DEPTH", 3):
                result = mas.router_agent("What are your pricing plans?")

        # Chain should be bounded
        chain_length = len(result["delegation_chain"])
        # Each level adds ~2 messages, so 3 levels = ~6 messages max
        assert chain_length <= 20, (
            f"Delegation chain too long ({chain_length}). "
            f"Loop may not be bounded."
        )

    def test_loop_produces_fallback_response(self):
        """System should provide a fallback response when loop is detected."""
        with patch.object(mas, "INJECT_INFINITE_LOOP", True):
            result = mas.router_agent("What are your pricing plans?")

        assert result["response"] is not None
        response_lower = result["response"].lower()
        assert any(phrase in response_lower for phrase in [
            "human agent", "apologize", "routing issue", "escalat",
        ]), f"No fallback response provided: {result['response']}"
```

### Step 6 — Log and inspect the failure chain

Add a test that prints the complete failure chain for analysis:

```python
class TestFailureChainLogging:
    """Verify failure chains are fully traceable."""

    def test_full_failure_chain_output(self):
        """Print the full delegation chain and failure log for inspection."""
        with patch.object(mas, "INJECT_COMMUNICATION_FAILURE", True):
            result = mas.router_agent("What are your pricing plans?")

        print("\n" + "=" * 60)
        print("FAILURE CHAIN ANALYSIS")
        print("=" * 60)

        print("\nDelegation Chain:")
        for i, msg in enumerate(result["delegation_chain"]):
            print(f"  [{i}] {msg['sender']} -> {msg['receiver']}: "
                  f"{msg['content'][:60]}...")

        print("\nFailure Log:")
        for i, failure in enumerate(result["failure_log"]):
            print(f"  [{i}] Type: {failure['failure_type']}")
            print(f"       Agent: {failure['agent']}")
            print(f"       Details: {failure['details']}")

        print("\nFinal Response:")
        print(f"  {result['response']}")

        # This test always passes — it's for visual inspection
        assert True
```

Run all tests with visible output:

```bash
pytest tests/multi_agent/test_multi_agent.py -v -s
```

---

## Expected Output

```
tests/multi_agent/test_multi_agent.py::TestNormalOperation::test_billing_query_routes_correctly PASSED
tests/multi_agent/test_multi_agent.py::TestNormalOperation::test_technical_query_routes_correctly PASSED
tests/multi_agent/test_multi_agent.py::TestNormalOperation::test_delegation_chain_is_logged PASSED
tests/multi_agent/test_multi_agent.py::TestCommunicationFailure::test_communication_failure_is_detected PASSED
tests/multi_agent/test_multi_agent.py::TestCommunicationFailure::test_graceful_degradation_on_failure PASSED
tests/multi_agent/test_multi_agent.py::TestCommunicationFailure::test_failure_log_contains_details PASSED
tests/multi_agent/test_multi_agent.py::TestInfiniteLoopDetection::test_infinite_loop_is_detected PASSED
tests/multi_agent/test_multi_agent.py::TestInfiniteLoopDetection::test_loop_stops_at_max_depth PASSED
tests/multi_agent/test_multi_agent.py::TestInfiniteLoopDetection::test_loop_produces_fallback_response PASSED
tests/multi_agent/test_multi_agent.py::TestFailureChainLogging::test_full_failure_chain_output PASSED

========================= 10 passed in ~30s =========================
```

---

## Verification Checklist

- [ ] Multi-agent system (`multi_agent_system.py`) runs without errors in normal mode
- [ ] Router correctly delegates billing queries to the billing specialist
- [ ] Router correctly delegates technical queries to the technical specialist
- [ ] Communication failure is detected and logged in `failure_log`
- [ ] System provides a graceful fallback response on communication failure
- [ ] Infinite delegation loop is detected before exceeding `MAX_DELEGATION_DEPTH`
- [ ] Loop detection produces a human-escalation fallback
- [ ] Delegation chain is fully traceable in the output
- [ ] All 10 tests pass

---

## Common Pitfalls

1. **Forgetting to reset injection flags** — The `INJECT_COMMUNICATION_FAILURE` and `INJECT_INFINITE_LOOP` flags are module-level. Always use `patch.object` in tests so they reset automatically. Never set them manually and forget to unset.

2. **Infinite loop test actually causing an infinite loop** — If `MAX_DELEGATION_DEPTH` is set too high or the guard is buggy, the test will hang. Always use `patch.object(mas, "MAX_DELEGATION_DEPTH", 3)` in tests to keep the depth small.

3. **Testing the router's classification, not the failure handling** — The router uses an LLM to classify queries, which can be non-deterministic. Focus tests on failure detection and recovery, not on exact routing decisions.

---

## Extension Challenge

**Advanced:** Add a third failure mode: **stale data**. The billing specialist returns outdated pricing (e.g., $4.99 instead of $9.99 for Basic). Write a test that:

1. Mocks the billing specialist to return stale pricing information
2. Uses a G-Eval metric to detect the factual inaccuracy
3. Logs the stale data as a `data_staleness` failure type
4. Verifies the failure chain shows exactly where the stale data originated

This simulates a real production scenario where one agent in the chain has an outdated knowledge base.
