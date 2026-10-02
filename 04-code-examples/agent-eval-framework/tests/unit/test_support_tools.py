"""Unit: the TechCorp support agent's five tool backends (no LLM)."""

import json

import pytest

from agents.support_agent import CUSTOMERS, KNOWLEDGE_BASE, TOOL_NAMES, TOOLS, execute_tool, search_kb


def test_exactly_five_tools():
    assert TOOL_NAMES == ["lookup_customer", "search_knowledge_base", "create_ticket", "send_email", "escalate_to_human"]
    for t in TOOLS:
        assert t["type"] == "function" and "parameters" in t["function"]


@pytest.mark.parametrize("ident", ["alice@example.com", "CUST-001"])
def test_lookup_by_email_or_id(ident):
    out = execute_tool("lookup_customer", {"identifier": ident})
    assert out.startswith("Customer found: ")
    assert json.loads(out.removeprefix("Customer found: "))["name"] == "Alice Johnson"


def test_lookup_not_found():
    assert execute_tool("lookup_customer", {"identifier": "nobody@example.com"}) == "Customer not found."


@pytest.mark.parametrize("query,article", [("pricing plans", "KB-101"), ("refund policy", "KB-102"), ("password reset", "KB-103"),
                                           ("API rate limits", "KB-104"), ("cancel subscription", "KB-105")])
def test_knowledge_base_search(query, article):
    assert search_kb(query)["id"] == article
    assert execute_tool("search_knowledge_base", {"query": query}).startswith(article)


def test_knowledge_base_miss():
    assert execute_tool("search_knowledge_base", {"query": "office dog policy"}).startswith("No relevant")


def test_ticket_email_escalation():
    t = execute_tool("create_ticket", {"customer_id": "CUST-001", "subject": "S", "description": "D", "priority": "high"})
    assert t.startswith("Ticket TKT-") and "Priority: high" in t
    assert execute_tool("send_email", {"to": "alice@example.com", "subject": "Hi", "body": "B"}).startswith("Email sent to alice@example.com")
    assert "urgency: urgent" in execute_tool("escalate_to_human", {"reason": "legal", "urgency": "urgent"})
    assert execute_tool("nope", {}) == "Unknown tool: nope"


def test_sample_data_shape():
    assert [c["id"] for c in CUSTOMERS] == ["CUST-001", "CUST-002", "CUST-003"]
    assert len(KNOWLEDGE_BASE) == 5
    alice = CUSTOMERS[0]
    assert [i["amount"] for i in alice["invoices"]] == [29.99, 29.99]  # the double charge
