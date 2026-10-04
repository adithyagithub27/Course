# Demo 27 — MCP Server Contract Tests

**Used in:** Lecture 6.3 (MCP Server Testing)
**Lecture type:** Build-along
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Contract-test a real MCP server built with the official Python SDK (mcp 2.2): list schemas, diff against the agent, call good and bad inputs, validate the agent's real calls.
**Demo file(s):** `demos/m06_mcp_server_validation.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m06_mcp_server_validation.py`; `make mcp   # the same server over stdio`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | mcp 2.2.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The server (45 s)

`mcp_server/techcorp_server.py`: `MCPServer(...)`, `@server.tool()` on `lookup_customer` and `create_ticket` with `Literal["low", "medium", "high", "critical"]` (bible §8.12).

### Scene 2: The contract (45 s)

Run the demo: five tools with required fields; "Agent vs server schema differences: none"; two `is_error=True` calls.

### Scene 3: Validating the agent (30 s)

Last block: the agent's real calls validate; the bad call fails with three JSON-schema errors. Show `validate_call()` (bible §8.13).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m06_mcp_server_validation.py
Tools exposed by the techcorp-support MCP server:
  lookup_customer(identifier)  required=['identifier']
  search_knowledge_base(query)  required=['query']
  create_ticket(customer_id, subject, description, priority)  required=['customer_id', 'subject', 'description', 'priority']
  send_email(to, subject, body)  required=['to', 'subject', 'body']
  escalate_to_human(reason, urgency)  required=['reason']
Agent vs server schema differences: none
call lookup_customer({'identifier': 'alice@example.com'})
  is_error=False  result={'found': True, 'customer': {'id': 'CUST-001', 'name': 'Alice Johnson', 'email': 'alice@example.com', 'plan': 
call create_ticket({'customer_id': 'CUST-999', 'subject': 'x', 'description': 'y', 'priority': 'high'})
  is_error=True  result={'text': 'Error executing tool create_ticket'}
call create_ticket({'customer_id': 'CUST-001', 'subject': 'x', 'description': 'y', 'priority': 'urgent'})
  is_error=True  result={'text': "Error executing tool create_ticket: 1 validation error for create_ticketArguments\npriority\n  Input
Validating the agent's real tool calls against the server's JSON schemas:
  lookup_customer: valid
  create_ticket: valid
  bad call example: ["'urgent' is not one of ['low', 'medium', 'high', 'critical']", "'subject' is a required property", "'description' is a required property"]
```

## Verify Before Recording

- [ ] mcp 2.x names: `MCPServer` (was `FastMCP` in 1.x), `mcp.Client`, `tool.input_schema`, `result.is_error`
- [ ] The long validation error line is truncated in the demo; zoom rather than read it
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Diagram: Agent ↔ MCP Client ↔ MCP Server ↔ backend, contract boundary highlighted
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
