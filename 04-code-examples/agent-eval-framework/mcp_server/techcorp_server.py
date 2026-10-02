"""
The TechCorp support tools as a real MCP server (Module 6.3).

Built with the official Model Context Protocol Python SDK, mcp 2.2. In mcp 2.x
the high-level server class is ``MCPServer`` (it was called ``FastMCP`` in
mcp 1.x). Each tool wraps the same simulated backend the support agent uses,
so the agent and the server share one contract.

Run it for an MCP client such as Claude Desktop or the MCP Inspector:

    uv run python -m mcp_server.techcorp_server          # stdio transport

Tests connect in-process with ``mcp.Client(server)`` (see mcp_server/contract.py).
"""

from __future__ import annotations

import json
from typing import Literal

from mcp.server.mcpserver import MCPServer

from agents import support_agent as backend

server = MCPServer(
    name="techcorp-support",
    instructions="TechCorp customer support tools: accounts, knowledge base, tickets, email, escalation.",
    version="1.0.0",
    log_level="CRITICAL",  # tool errors are returned to the client as is_error results
)


@server.tool()
def lookup_customer(identifier: str) -> dict:
    """Look up a customer's account by email or account ID (e.g. CUST-001)."""
    customer = backend.MOCK_CUSTOMERS.get(identifier.strip())
    if customer is None:
        return {"found": False, "identifier": identifier}
    return {"found": True, "customer": customer}


@server.tool()
def search_knowledge_base(query: str) -> dict:
    """Search the TechCorp knowledge base. Returns the best matching article or found=false."""
    article = backend.search_kb(query)
    if article is None:
        return {"found": False, "query": query}
    return {"found": True, "id": article["id"], "title": article["title"], "text": article["text"]}


@server.tool()
def create_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: Literal["low", "medium", "high", "critical"],
) -> dict:
    """Create a support ticket for an existing customer."""
    if customer_id not in backend.MOCK_CUSTOMERS:
        raise ValueError(f"unknown customer_id {customer_id}")
    text = backend.execute_tool("create_ticket", {"customer_id": customer_id, "subject": subject, "description": description, "priority": priority})
    return {"ticket_id": text.split()[1], "priority": priority, "status": "open"}


@server.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email to a customer address on file."""
    known = {c["email"] for c in backend.CUSTOMERS}
    if to not in known:
        raise ValueError("recipient is not a customer email on file")
    backend.execute_tool("send_email", {"to": to, "subject": subject, "body": body})
    return {"sent": True, "to": to}


@server.tool()
def escalate_to_human(reason: str, urgency: Literal["normal", "urgent"] = "normal") -> dict:
    """Hand the conversation to a human agent."""
    return {"escalated": True, "urgency": urgency, "reason": reason}


def tool_result_json(result) -> dict:
    """Pull the structured JSON out of a CallToolResult."""
    if getattr(result, "structured_content", None):
        return result.structured_content
    for block in result.content:
        if getattr(block, "text", None):
            try:
                return json.loads(block.text)
            except json.JSONDecodeError:
                return {"text": block.text}
    return {}


if __name__ == "__main__":
    server.run()
