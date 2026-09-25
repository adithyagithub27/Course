"""
Tool Calling Tests — Module 06, Project 3

Tests the agent's tool-calling behavior:
- Correct tool selection
- Correct argument passing
- Error handling
- Unauthorized action prevention
"""

import pytest
from agents.support_agent import run_support_agent


@pytest.mark.tool_calling
class TestToolSelection:
    """Test that the agent selects the correct tools for each task."""

    def test_uses_knowledge_base_for_product_questions(self):
        """Product questions should trigger knowledge base search."""
        result = run_support_agent("What are your pricing plans?")
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        assert "search_knowledge_base" in tool_names, (
            f"Expected knowledge base search for product question. "
            f"Tools used: {tool_names}"
        )

    def test_uses_lookup_for_account_questions(self):
        """Account-specific questions should trigger customer lookup."""
        result = run_support_agent(
            "Can you check my account? My email is alice@example.com"
        )
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        assert "lookup_customer" in tool_names, (
            f"Expected customer lookup for account question. "
            f"Tools used: {tool_names}"
        )

    def test_uses_create_ticket_for_issues(self):
        """Unresolved issues should trigger ticket creation."""
        result = run_support_agent(
            "I've been charged twice this month for my Pro plan. "
            "My account is alice@example.com. Please create a ticket."
        )
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        assert "create_ticket" in tool_names, (
            f"Expected ticket creation for billing issue. "
            f"Tools used: {tool_names}"
        )

    def test_escalates_sensitive_requests(self):
        """Sensitive/complex requests should trigger escalation."""
        result = run_support_agent(
            "I want to speak to your CEO about a data breach "
            "that exposed my personal information."
        )
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        assert "escalate_to_human" in tool_names, (
            f"Expected escalation for sensitive data breach request. "
            f"Tools used: {tool_names}"
        )


@pytest.mark.tool_calling
class TestToolArguments:
    """Test that tool arguments are correct."""

    def test_lookup_uses_correct_email(self):
        """Customer lookup should use the email provided by the user."""
        result = run_support_agent(
            "Look up the account for alice@example.com"
        )
        lookup_calls = [
            tc for tc in result["tool_calls"]
            if tc["tool"] == "lookup_customer"
        ]
        assert len(lookup_calls) > 0, "Expected at least one lookup call"
        identifier = lookup_calls[0]["arguments"].get("identifier", "")
        assert "alice@example.com" in identifier or "CUST-001" in identifier, (
            f"Lookup should use the provided email. Got: {identifier}"
        )

    def test_ticket_has_required_fields(self):
        """Created tickets should have all required fields populated."""
        result = run_support_agent(
            "I need a ticket for a billing issue. "
            "My account is alice@example.com and I was charged twice."
        )
        ticket_calls = [
            tc for tc in result["tool_calls"]
            if tc["tool"] == "create_ticket"
        ]
        if ticket_calls:
            args = ticket_calls[0]["arguments"]
            assert "subject" in args, "Ticket missing subject"
            assert "description" in args, "Ticket missing description"
            assert "priority" in args, "Ticket missing priority"
            assert args["priority"] in ("low", "medium", "high", "critical"), (
                f"Invalid priority: {args['priority']}"
            )


@pytest.mark.tool_calling
class TestToolErrorHandling:
    """Test agent behavior when tools return errors or unexpected results."""

    def test_handles_customer_not_found(self):
        """Agent should handle gracefully when a customer is not found."""
        result = run_support_agent(
            "Look up my account. My email is unknown@notreal.com"
        )
        # Agent should inform the user rather than crash or hallucinate
        assert result["response"], "Agent should return a response"
        response_lower = result["response"].lower()
        assert any(
            phrase in response_lower
            for phrase in ["not found", "couldn't find", "unable to locate",
                          "no account", "don't have", "cannot find"]
        ), f"Agent should communicate that the account was not found. Got: {result['response'][:100]}"

    def test_no_excessive_tool_calls(self):
        """Agent should not make excessive tool calls for simple questions."""
        result = run_support_agent("What are your pricing plans?")
        assert len(result["tool_calls"]) <= 3, (
            f"Simple question triggered {len(result['tool_calls'])} tool calls. "
            f"Expected at most 3."
        )
        assert result["llm_calls"] <= 3, (
            f"Simple question triggered {result['llm_calls']} LLM calls. "
            f"Expected at most 3."
        )
