# Demo 04 — Langfuse v4 Agent Trace

**Used in:** Lecture 9.2 (Tracing with Langfuse: Spans, Costs & Latency); also Lab 9.1
**Duration:** ~3 minutes of screen recording
**Purpose:** Trace the TechCorp agent with the Langfuse v4 SDK, read a trace (agent → generation → tool), compare users and costs, and attach scores.
**Demo files:** `observability/langfuse_tracing.py`, `demos/m09_langfuse_tracing.py`
**Commands:** `uv run python demos/m09_langfuse_tracing.py`; `make trace`
**Verified:** langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02)

## Setup

```bash
cd 04-code-examples/agent-eval-framework
# Optional, for the UI: a Langfuse Cloud (or self-hosted) project
# .env: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Without keys the demo captures the same spans in memory and prints the tree. For the UI shots, record with keys set and a throwaway project; blur keys in post. Langfuse's UI changes: verify the screens before recording.

## Recording Script

### Scene 1: The v4 API (45 s)

`observability/langfuse_tracing.py`, exact code:

```python
@observe(name="support-agent", as_type="agent")
def _traced_run(question: str, *, user_id: str, session_id: str | None, version: str, tool_executor: Any) -> dict:
    with propagate_attributes(user_id=user_id, session_id=session_id, tags=["techcorp", "support"],
                              version=version, metadata={"agent": "support"}):
        result = run_support_agent(question, client=TracedOpenAI(get_llm_client()),
                                   tool_executor=tool_executor or traced_tool)
        result["trace_id"] = get_client().get_current_trace_id()
    return result
```

Highlight `@observe(..., as_type="agent")`, `propagate_attributes(user_id=..., session_id=...)`, `get_client()`. Corner note: "Langfuse v4. No `langfuse.decorators`, no `langfuse_context`."

### Scene 2: Four traced conversations (45 s)

```bash
uv run python demos/m09_langfuse_tracing.py
```

Real offline output:

```
user      question                                  spans  llm_calls  tokens  cost_usd  latency_s  relevancy
--------  ----------------------------------------  -----  ---------  ------  --------  ---------  ---------
CUST-001  What are your pricing plans?              4      2          1731    0.000791  1.872      1.00     
CUST-001  I've been charged twice this month for m  6      3          2994    0.001397  3.283      1.00     
CUST-002  How do I reset my password?               4      2          1719    0.000778  1.783      1.00     
CUST-003  I want to file a legal complaint and I'm  4      2          1722    0.000781  1.734      1.00     
Trace tree for the ticket request (CUST-001):
agent      support-agent                   
  generation chat gpt-4.1-mini                usage={"input": 787, "output": 36}
  tool       tool lookup_customer            
             output: Customer found: {"id": "CUST-001", "name": "Alice Johnson", "email": "alice@exam
  generation chat gpt-4.1-mini                usage={"input": 949, "output": 98}
  tool       tool create_ticket              
             output: Ticket TKT-5001 created: Duplicate charge on Pro plan (Priority: high)
  generation chat gpt-4.1-mini                usage={"input": 1092, "output": 32}
Scores attached (create_score): 4 (recorded locally offline)
```

Callouts: the ticket request costs about twice the FAQ (3 LLM calls, 6 spans); costs on gpt-4.1-mini (verify current pricing); latency is simulated offline.

### Scene 3: The same trace in the UI (60 s, live keys)

Langfuse UI → Traces → filter `user_id = CUST-001` → open the ticket trace. Expand top-down: agent → generation (model, tokens, cost) → tool `lookup_customer` (input/output) → generation → tool `create_ticket` → generation. Show the Scores tab with `relevancy`. Then Sessions view.

Trace IDs and timestamps change on every run: never read one aloud.

## Verify Before Recording

- [ ] No v2 code on screen (`langfuse.decorators`, `langfuse_context`, `langfuse.trace()`, `langfuse.score()`)
- [ ] Keys blurred; throwaway Langfuse project
- [ ] UI steps re-checked against the current Langfuse release

## Post-Production Notes

- Use the printed tree as the animated build for the D13 trace-anatomy diagram
- Amber callout on latency ("simulated" offline), teal on the agent span
