# Lab 05: Tool-Calling Tests

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 06 — Testing Tool Use and Agent Actions               |
| **Duration**       | 60 minutes                                                   |
| **Difficulty**     | Intermediate                                                 |
| **Learning Objective** | Write structured tests that verify an agent selects the correct tool, passes correct parameters, and handles tool errors and unavailability gracefully. |

---

## Prerequisites

- Completed **Lab 01** and **Lab 02**
- Understanding of the support agent's five tools: `lookup_customer`, `search_knowledge_base`, `create_ticket`, `send_email`, `escalate_to_human`
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Review the agent's tool definitions

```bash
cat agents/support_agent.py
```

Pay attention to the `TOOLS` list (lines 40–152) and the `execute_tool` function (lines 191–216).

### 2. Create the test directory

```bash
mkdir -p tests/tool_calling
touch tests/tool_calling/__init__.py
```

---

## Step-by-Step Instructions

### Step 1 — Write tool selection tests

The most basic tool-calling test: given an input, did the agent call the **right** tool?

Create `tests/tool_calling/test_tool_selection.py`:

```python
"""
Lab 05 — Tool Selection Tests
Run: pytest tests/tool_calling/test_tool_selection.py -v
"""

import pytest
from agents.support_agent import run_support_agent


# ── Test Data: input → expected tool(s) ───────────────────────────
TOOL_SELECTION_CASES = [
    {
        "id": "product_question",
        "input": "What are your pricing plans?",
        "expected_tools": ["search_knowledge_base"],
        "description": "Product questions should trigger KB search",
    },
    {
        "id": "account_lookup",
        "input": "Can you look up my account? My email is alice@example.com",
        "expected_tools": ["lookup_customer"],
        "description": "Account requests should trigger customer lookup",
    },
    {
        "id": "create_ticket",
        "input": (
            "I've been charged twice this month. My customer ID is "
            "CUST-001. Can you create a support ticket?"
        ),
        "expected_tools": ["create_ticket"],
        "description": "Issue reports should trigger ticket creation",
    },
    {
        "id": "escalation",
        "input": (
            "I'm furious. Your product lost all my data and I need "
            "to speak to a manager immediately."
        ),
        "expected_tools": ["escalate_to_human"],
        "description": "Angry/complex issues should trigger escalation",
    },
    {
        "id": "no_tool_needed",
        "input": "Thank you for your help!",
        "expected_tools": [],
        "description": "Simple acknowledgments should not call any tool",
    },
]


@pytest.mark.parametrize(
    "case",
    TOOL_SELECTION_CASES,
    ids=[c["id"] for c in TOOL_SELECTION_CASES],
)
def test_correct_tool_selected(case):
    """Verify the agent selects the expected tool(s)."""
    result = run_support_agent(case["input"])
    actual_tools = [tc["tool"] for tc in result["tool_calls"]]

    if case["expected_tools"]:
        # Check that every expected tool was called
        for expected in case["expected_tools"]:
            assert expected in actual_tools, (
                f"Expected tool '{expected}' was not called.\n"
                f"Input: {case['input']}\n"
                f"Actual tools: {actual_tools}\n"
                f"Reason: {case['description']}"
            )
    else:
        # No tools should have been called
        assert len(actual_tools) == 0, (
            f"Expected no tool calls, but got: {actual_tools}\n"
            f"Input: {case['input']}"
        )
```

Run it:

```bash
pytest tests/tool_calling/test_tool_selection.py -v
```

### Step 2 — Write parameter correctness tests

Calling the right tool is not enough — the **arguments** must be correct too.

Create `tests/tool_calling/test_tool_params.py`:

```python
"""
Lab 05 — Tool Parameter Correctness Tests
Run: pytest tests/tool_calling/test_tool_params.py -v
"""

import pytest
from agents.support_agent import run_support_agent


def get_tool_call(result: dict, tool_name: str) -> dict | None:
    """Extract the first call to a specific tool from the result."""
    for tc in result["tool_calls"]:
        if tc["tool"] == tool_name:
            return tc
    return None


class TestToolParameters:
    """Verify tools are called with correct arguments."""

    def test_lookup_customer_passes_email(self):
        """lookup_customer should receive the customer's email."""
        result = run_support_agent(
            "Look up my account. My email is alice@example.com"
        )
        call = get_tool_call(result, "lookup_customer")

        assert call is not None, "lookup_customer was not called"
        assert call["arguments"]["identifier"] == "alice@example.com", (
            f"Expected identifier 'alice@example.com', "
            f"got '{call['arguments'].get('identifier')}'"
        )

    def test_lookup_customer_passes_id(self):
        """lookup_customer should accept a customer ID."""
        result = run_support_agent(
            "Look up customer CUST-001 please."
        )
        call = get_tool_call(result, "lookup_customer")

        assert call is not None, "lookup_customer was not called"
        assert call["arguments"]["identifier"] == "CUST-001", (
            f"Expected identifier 'CUST-001', "
            f"got '{call['arguments'].get('identifier')}'"
        )

    def test_create_ticket_has_required_fields(self):
        """create_ticket should include all required parameters."""
        result = run_support_agent(
            "I'm customer CUST-001. I've been charged twice. "
            "Please create a high priority ticket for this."
        )
        call = get_tool_call(result, "create_ticket")

        assert call is not None, "create_ticket was not called"

        args = call["arguments"]
        required_fields = ["customer_id", "subject", "description", "priority"]
        for field in required_fields:
            assert field in args, (
                f"Missing required field '{field}' in create_ticket args. "
                f"Got: {list(args.keys())}"
            )

        # Priority should match the user's request
        assert args["priority"] in ["high", "critical"], (
            f"User asked for high priority, got '{args['priority']}'"
        )

    def test_send_email_has_valid_recipient(self):
        """send_email should use a valid email format."""
        result = run_support_agent(
            "My email is alice@example.com. Can you send me a "
            "confirmation of my Pro plan subscription?"
        )
        call = get_tool_call(result, "send_email")

        if call is not None:
            assert "@" in call["arguments"].get("to", ""), (
                f"Email 'to' field is not a valid email: "
                f"'{call['arguments'].get('to')}'"
            )
```

Run:

```bash
pytest tests/tool_calling/test_tool_params.py -v
```

### Step 3 — Write tool error handling tests

What happens when a tool **returns an error**? The agent should handle it gracefully.

Create `tests/tool_calling/test_tool_errors.py`:

```python
"""
Lab 05 — Tool Error Handling Tests
Run: pytest tests/tool_calling/test_tool_errors.py -v
"""

import pytest
from unittest.mock import patch
from agents.support_agent import run_support_agent


class TestToolErrorHandling:
    """Verify the agent handles tool errors gracefully."""

    def test_customer_not_found(self):
        """Agent should handle 'customer not found' gracefully."""
        result = run_support_agent(
            "Look up my account. My email is unknown@nowhere.com"
        )

        # The agent should acknowledge the customer was not found
        response_lower = result["response"].lower()
        assert any(phrase in response_lower for phrase in [
            "not found", "couldn't find", "could not find",
            "no account", "unable to find", "don't have",
        ]), (
            f"Agent did not acknowledge missing customer.\n"
            f"Response: {result['response']}"
        )

    def test_knowledge_base_no_results(self):
        """Agent should handle KB returning no results."""
        result = run_support_agent(
            "What is your policy on interdimensional travel insurance?"
        )

        response_lower = result["response"].lower()
        # Should NOT hallucinate a policy
        assert "interdimensional" not in response_lower or any(
            phrase in response_lower for phrase in [
                "don't have", "not sure", "no information",
                "unable to find", "not available", "escalate",
            ]
        ), (
            f"Agent may have hallucinated a response.\n"
            f"Response: {result['response']}"
        )

    @patch("agents.support_agent.execute_tool")
    def test_tool_raises_exception(self, mock_execute):
        """Agent should handle a tool that throws an exception."""
        mock_execute.side_effect = Exception("Database connection timeout")

        # The agent loop should catch this or the max_iterations
        # limit will produce a fallback response
        try:
            result = run_support_agent(
                "Look up my account: alice@example.com"
            )
            # Should still get some response (not crash)
            assert result["response"] is not None
            assert len(result["response"]) > 0
        except Exception as e:
            # If the agent crashes, that's a failure
            pytest.fail(
                f"Agent crashed when tool raised an exception: {e}"
            )
```

### Step 4 — Write tool unavailability tests

What if a tool is **removed** from the available tools?

```python
    @patch("agents.support_agent.TOOLS", [
        # Only include search_knowledge_base — remove all others
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "Search the product knowledge base for answers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        }
                    },
                    "required": ["query"],
                },
            },
        },
    ])
    def test_agent_with_limited_tools(self):
        """Agent should cope when some tools are unavailable."""
        result = run_support_agent(
            "Look up my account: alice@example.com"
        )

        # Agent should NOT call lookup_customer (it's not available)
        actual_tools = [tc["tool"] for tc in result["tool_calls"]]
        assert "lookup_customer" not in actual_tools, (
            "Agent called a tool that was not available"
        )

        # Agent should provide a helpful response or escalate
        assert len(result["response"]) > 10, (
            "Agent gave an empty or too-short response"
        )
```

Add this test method inside the `TestToolErrorHandling` class, then run all tool tests:

```bash
pytest tests/tool_calling/ -v
```

---

## Expected Output

```
tests/tool_calling/test_tool_selection.py::test_correct_tool_selected[product_question] PASSED
tests/tool_calling/test_tool_selection.py::test_correct_tool_selected[account_lookup] PASSED
tests/tool_calling/test_tool_selection.py::test_correct_tool_selected[create_ticket] PASSED
tests/tool_calling/test_tool_selection.py::test_correct_tool_selected[escalation] PASSED
tests/tool_calling/test_tool_selection.py::test_correct_tool_selected[no_tool_needed] PASSED
tests/tool_calling/test_tool_params.py::TestToolParameters::test_lookup_customer_passes_email PASSED
tests/tool_calling/test_tool_params.py::TestToolParameters::test_lookup_customer_passes_id PASSED
tests/tool_calling/test_tool_params.py::TestToolParameters::test_create_ticket_has_required_fields PASSED
tests/tool_calling/test_tool_params.py::TestToolParameters::test_send_email_has_valid_recipient PASSED
tests/tool_calling/test_tool_errors.py::TestToolErrorHandling::test_customer_not_found PASSED
tests/tool_calling/test_tool_errors.py::TestToolErrorHandling::test_knowledge_base_no_results PASSED
tests/tool_calling/test_tool_errors.py::TestToolErrorHandling::test_tool_raises_exception PASSED
tests/tool_calling/test_tool_errors.py::TestToolErrorHandling::test_agent_with_limited_tools PASSED

========================= 13 passed in ~45s =========================
```

---

## Verification Checklist

- [ ] Five tool selection tests cover all five tools plus the "no tool" case
- [ ] Parameter correctness tests verify exact argument values
- [ ] Error handling tests cover: customer not found, no KB results, tool exception
- [ ] Unavailability test removes tools and verifies the agent adapts
- [ ] All tests pass with `pytest -v`
- [ ] No hardcoded API keys in any test file

---

## Common Pitfalls

1. **Non-deterministic tool selection** — LLMs don't always pick the same tool for the same input. If a test is flaky, run it 3 times. If it fails >1 time, the test expectation might be too strict or the agent's prompt needs improvement.

2. **Forgetting to mock at the right level** — When using `@patch`, make sure you're patching the function in the module where it's **imported**, not where it's **defined**. For `execute_tool`, patch `agents.support_agent.execute_tool`.

3. **Testing tool output instead of tool selection** — Tool calling tests should verify which tool was called and with what arguments. Testing the final response is a different concern (covered by evaluation metrics in Labs 02–03).

---

## Extension Challenge

**Advanced:** Write a "multi-tool workflow" test that verifies the agent chains multiple tools correctly. For example:

> "I'm customer CUST-001. I need to create a ticket about my billing issue and send me an email confirmation."

Verify that the agent:
1. Calls `lookup_customer` with `CUST-001` (to verify identity)
2. Calls `create_ticket` with the correct customer ID and subject
3. Calls `send_email` to confirm the ticket creation
4. The tools are called in a logical order (lookup before create, create before email)

```python
def test_multi_tool_workflow():
    result = run_support_agent(
        "I'm customer CUST-001. Create a ticket about my billing "
        "issue and send me an email confirmation at alice@example.com."
    )
    tools_called = [tc["tool"] for tc in result["tool_calls"]]

    # Verify all expected tools were called
    assert "create_ticket" in tools_called
    # Verify logical ordering if both lookup and create were called
    if "lookup_customer" in tools_called:
        lookup_idx = tools_called.index("lookup_customer")
        create_idx = tools_called.index("create_ticket")
        assert lookup_idx < create_idx, "Lookup should happen before ticket creation"
```
