"""Component: the MCP server contract (Module 6.3), via the official mcp SDK in-process client."""

import asyncio

from mcp_server.contract import agent_schemas, call, check_server, compare, server_schemas, validate_call


def test_contract_holds():
    assert asyncio.run(check_server()) == []


def test_server_exposes_the_five_agent_tools():
    schemas = asyncio.run(server_schemas())
    assert set(schemas) == set(agent_schemas())
    assert schemas["create_ticket"]["properties"]["priority"]["enum"] == ["low", "medium", "high", "critical"]


def test_compare_detects_drift():
    agent = agent_schemas()
    server = {k: dict(v) for k, v in agent.items()}
    server["create_ticket"] = dict(server["create_ticket"], required=["customer_id"])
    del server["send_email"]
    problems = compare(agent, server)
    assert any("send_email: missing" in p for p in problems)
    assert any(p.startswith("create_ticket: required") for p in problems)


def test_calls_and_validation():
    err, out = asyncio.run(call("search_knowledge_base", {"query": "refund policy"}))
    assert not err and out["id"] == "KB-102"
    err, _ = asyncio.run(call("send_email", {"to": "stranger@evil.com", "subject": "x", "body": "y"}))
    assert err
    schemas = asyncio.run(server_schemas())
    assert validate_call(schemas, "lookup_customer", {"identifier": "alice@example.com"}) == []
    assert validate_call(schemas, "create_ticket", {"customer_id": "CUST-001", "priority": "urgent"})
    assert validate_call(schemas, "drop_tables", {}) == ["unknown tool drop_tables"]
