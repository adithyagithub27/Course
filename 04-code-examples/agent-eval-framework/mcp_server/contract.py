"""
MCP contract checks (Module 6.3): does the server expose the tools the agent
expects, with compatible schemas, and does it behave on good and bad input?

    asyncio.run(check_server())  -> list of violations ([] = contract holds)
    validate_call(tool_schemas, "create_ticket", args) -> list of schema errors
"""

from __future__ import annotations

import asyncio

import jsonschema
from mcp import Client

from agents.support_agent import TOOLS as AGENT_TOOLS
from mcp_server.techcorp_server import server, tool_result_json


async def server_schemas() -> dict[str, dict]:
    async with Client(server) as client:
        listed = await client.list_tools()
    return {t.name: t.input_schema for t in listed.tools}


def agent_schemas() -> dict[str, dict]:
    return {t["function"]["name"]: t["function"]["parameters"] for t in AGENT_TOOLS}


def compare(agent: dict[str, dict], mcp: dict[str, dict]) -> list[str]:
    """Differences between what the agent was told and what the server accepts."""
    problems = []
    for name, a in agent.items():
        m = mcp.get(name)
        if m is None:
            problems.append(f"{name}: missing on the MCP server")
            continue
        if set(a.get("required", [])) != set(m.get("required", [])):
            problems.append(f"{name}: required {sorted(a.get('required', []))} vs server {sorted(m.get('required', []))}")
        for prop, spec in a.get("properties", {}).items():
            mspec = m.get("properties", {}).get(prop)
            if mspec is None:
                problems.append(f"{name}.{prop}: not accepted by the server")
                continue
            if spec.get("type") != mspec.get("type"):
                problems.append(f"{name}.{prop}: type {spec.get('type')} vs server {mspec.get('type')}")
            if "enum" in spec and set(spec["enum"]) != set(mspec.get("enum", [])):
                problems.append(f"{name}.{prop}: enum {spec['enum']} vs server {mspec.get('enum')}")
    for name in mcp:
        if name not in agent:
            problems.append(f"{name}: on the server but unknown to the agent")
    return problems


def validate_call(schemas: dict[str, dict], tool: str, args: dict) -> list[str]:
    """Validate one tool call's arguments against the server's JSON schema."""
    if tool not in schemas:
        return [f"unknown tool {tool}"]
    v = jsonschema.Draft202012Validator(schemas[tool])
    return [e.message for e in v.iter_errors(args)]


async def call(tool: str, args: dict) -> tuple[bool, dict]:
    """Call a tool in-process. Returns (is_error, json_result)."""
    async with Client(server) as client:
        result = await client.call_tool(tool, args)
    return bool(result.is_error), tool_result_json(result)


async def check_server() -> list[str]:
    problems = compare(agent_schemas(), await server_schemas())
    err, out = await call("lookup_customer", {"identifier": "alice@example.com"})
    if err or not out.get("found"):
        problems.append("lookup_customer: known customer not found")
    err, out = await call("create_ticket", {"customer_id": "CUST-999", "subject": "x", "description": "y", "priority": "high"})
    if not err:
        problems.append("create_ticket: accepted an unknown customer_id")
    return problems


if __name__ == "__main__":
    print(asyncio.run(check_server()) or "MCP contract holds")
