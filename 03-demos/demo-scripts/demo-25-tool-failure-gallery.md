# Demo 25 — Four Tool-Call Failures

**Used in:** Lecture 6.1 (Why Tool Calling Is the Highest-Risk Part)
**Lecture type:** Teach + failure demo
**Duration:** ~2 minutes of screen recording
**Purpose:** Show four recorded tool-call failures and the deterministic check that catches each.
**Demo file(s):** `demos/m06_tool_failure_gallery.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m06_tool_failure_gallery.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: TF-1, TF-2 (50 s)

Wrong argument (`identifier` = "Alice Johnson <alice@example.com>"); an action (`create_ticket`) for a question.

### Scene 2: TF-3, TF-4 (50 s)

Tool error reported as success; `send_email` before `create_ticket` (expected order lookup → ticket → email).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m06_tool_failure_gallery.py
TF-1 argument in the wrong field
  user : Look up order history for alice@example.com
  tools: ["lookup_customer{'identifier': 'Alice Johnson <alice@example.com>'}"]
  reply: I couldn't find that account.
  check: FAIL wrong arguments {'identifier': ('alice@example.com', 'Alice Johnson <alice@example.com>')}
TF-2 action when the user only asked a question
  user : What is your refund policy?
  tools: ["create_ticket{'customer_id': 'CUST-001', 'subject': 'Refund', 'description': 'Refund request', 'priority': 'medium'}"]
  reply: I've started a refund for you.
  check: FAIL action tool called for a question: ['create_ticket']
TF-3 tool error reported as success
  user : Please open a ticket for my double charge. alice@example.com
  tools: ["lookup_customer{'identifier': 'alice@example.com'}", "create_ticket{'customer_id': 'CUST-001', 'subject': 'Double charge', 'description': 'Charged twice', 'priority': 'high'}"]
  reply: Done! Ticket created; billing will contact you.
  check: FAIL ['create_ticket'] returned an error but the reply claims success
TF-4 tools called in the wrong order
  user : Email me a confirmation of my new ticket. alice@example.com, charged twice.
  tools: ["send_email{'to': 'alice@example.com', 'subject': 'Your ticket', 'body': 'Ticket TKT-???'}", "create_ticket{'customer_id': 'CUST-001', 'subject': 'Double charge', 'description': 'Charged twice', 'priority': 'high'}"]
  reply: I've emailed you and opened a ticket.
  check: FAIL expected order ['lookup_customer', 'create_ticket', 'send_email']
```

## Verify Before Recording

- [ ] Recorded runs from `datasets/tool_failures.json`: say "recorded"
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D10
- `check: FAIL` lines in red
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
