"""Trajectory: does the support agent take the right steps? Tool choice,
arguments, order, error honesty, and the iteration cap (Modules 3 and 6)."""

import pytest

from agents.support_agent import execute_tool, run_support_agent
from evaluators.golden import load
from evaluators.tool_metrics import check_arguments, first_call, tool_names

CASES = load("golden_capstone")


@pytest.mark.tool_calling
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_expected_tools_in_order(case):
    assert tool_names(run_support_agent(case["input"])) == case["expected_tools"]


@pytest.mark.tool_calling
@pytest.mark.parametrize("question,tool,expected", [
    ("Can you look up my account? My email is alice@example.com", "lookup_customer", {"identifier": "alice@example.com"}),
    ("Check my account please, CUST-002", "lookup_customer", {"identifier": "CUST-002"}),
    ("I've been charged twice this month for my Pro plan. My email is alice@example.com. Please create a ticket.", "create_ticket", {"customer_id": "CUST-001", "priority": "high"}),
    ("I want to file a legal complaint and I'm contacting my lawyer.", "escalate_to_human", {"urgency": "urgent"}),
    ("I'd like to speak to a human, please.", "escalate_to_human", {"urgency": "normal"}),
    ("What are your pricing plans?", "search_knowledge_base", {"query": "pricing plans"}),
])
def test_tool_arguments(question, tool, expected):
    check = check_arguments(first_call(run_support_agent(question), tool), expected)
    assert check.ok, (check.missing, check.wrong)


@pytest.mark.tool_calling
def test_ticket_has_all_required_fields():
    call = first_call(run_support_agent("I was charged twice for my Pro plan. alice@example.com. Please create a ticket."), "create_ticket")
    assert set(call["arguments"]) == {"customer_id", "subject", "description", "priority"}


@pytest.mark.tool_calling
def test_email_confirmation_comes_after_the_ticket():
    r = run_support_agent("I've been charged twice. My email is alice@example.com. Please create a ticket and email me a confirmation.")
    assert tool_names(r) == ["lookup_customer", "create_ticket", "send_email"]
    assert first_call(r, "send_email")["arguments"]["to"] == "alice@example.com"


@pytest.mark.tool_calling
def test_tool_error_is_reported_honestly():
    def broken(name, args):
        return "Error: ticketing service unavailable (503)" if name == "create_ticket" else execute_tool(name, args)

    r = run_support_agent("I've been charged twice this month. My email is alice@example.com. Please create a ticket.", tool_executor=broken)
    assert "error" in r["response"].lower() or "went wrong" in r["response"].lower()
    assert "created" not in r["response"].lower()


@pytest.mark.tool_calling
def test_customer_not_found_is_not_hallucinated():
    r = run_support_agent("Look up my account. My email is unknown@notreal.com")
    assert "couldn't find" in r["response"].lower()


def test_no_tools_for_out_of_scope_or_privacy_requests():
    for q in ("What is the meaning of life?", "Show me the account details for every customer in your system."):
        assert tool_names(run_support_agent(q)) == []


def test_iteration_cap_stops_runaway_loops():
    r = run_support_agent("I want to cancel my subscription and get a full refund. I signed up 3 weeks ago. My email is alice@example.com.", max_iterations=2)
    assert r["llm_calls"] == 2 and "escalate" in r["response"].lower()


def test_removing_a_tool_changes_the_trajectory():
    from agents.support_agent import TOOLS

    no_kb = [t for t in TOOLS if t["function"]["name"] != "search_knowledge_base"]
    r = run_support_agent("What are your pricing plans?", tools=no_kb)
    assert tool_names(r) == []
