"""Lecture 6.3 - MCP server testing: list the server's tools, compare their
schemas with what the agent was told, call them with good and bad input, and
validate a real agent run against the server's contract.

    uv run python demos/m06_mcp_server_validation.py
"""
from _common import banner

import asyncio

from agents.support_agent import run_support_agent
from mcp_server.contract import agent_schemas, call, compare, server_schemas, validate_call

banner("Lecture 6.3 - MCP contract tests", ["mcp", "openai"])


async def main() -> None:
    schemas = await server_schemas()
    print("Tools exposed by the techcorp-support MCP server:")
    for name, s in schemas.items():
        print(f"  {name}({', '.join(s.get('properties', {}))})  required={s.get('required', [])}")
    print(f"\nAgent vs server schema differences: {compare(agent_schemas(), schemas) or 'none'}")
    for tool, args in [("lookup_customer", {"identifier": "alice@example.com"}),
                       ("create_ticket", {"customer_id": "CUST-999", "subject": "x", "description": "y", "priority": "high"}),
                       ("create_ticket", {"customer_id": "CUST-001", "subject": "x", "description": "y", "priority": "urgent"})]:
        err, out = await call(tool, args)
        print(f"\ncall {tool}({args})\n  is_error={err}  result={str(out)[:110]}")
    run = run_support_agent("I've been charged twice this month for my Pro plan. My email is alice@example.com. Please create a ticket.")
    print("\nValidating the agent's real tool calls against the server's JSON schemas:")
    for t in run["tool_calls"]:
        print(f"  {t['tool']}: {validate_call(schemas, t['tool'], t['arguments']) or 'valid'}")
    print(f"  bad call example: {validate_call(schemas, 'create_ticket', {'customer_id': 'CUST-001', 'priority': 'urgent'})}")


asyncio.run(main())
