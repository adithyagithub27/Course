# Demo 04 — Langfuse Agent Trace

**Used in:** Lecture 9.2 (Tracing with Langfuse)
**Duration:** ~3 minutes of screen recording
**Purpose:** Show agent observability — trace a multi-step agent execution and identify the root cause of a failure

## Setup

```bash
# Student should have Langfuse account (free cloud tier)
# .env should have LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY set
cd agent-eval-framework
```

## Recording Script

### Scene 1: Instrument the Agent (45s)

Show the code with Langfuse decorator:
```python
from langfuse.decorators import observe

@observe(name="support-agent")
def traced_agent_call(user_message: str):
    result = run_support_agent(user_message)
    return result
```

Narration: "One decorator. That's all it takes. Every LLM call, every tool execution, every decision point — captured automatically."

### Scene 2: Run Traced Queries (30s)

```bash
python -c "
from observability.langfuse_setup import traced_agent_call

# Run several queries
queries = [
    'What are your pricing plans?',
    'Look up alice@example.com',
    'I want to cancel and get a refund. I signed up yesterday.',
]

for q in queries:
    print(f'Query: {q}')
    result = traced_agent_call(q)
    print(f'Response: {result[\"response\"][:80]}...')
    print(f'Tools: {[tc[\"tool\"] for tc in result[\"tool_calls\"]]}')
    print()
"
```

### Scene 3: Navigate Langfuse Dashboard (90s)

Switch to browser — Langfuse Cloud dashboard:

1. **Traces list** — Show 3 traces from the queries just run
2. **Click into the refund trace** — Show the span waterfall:
   - Root span: support-agent (total: 4.2s)
     - LLM call 1: initial reasoning (1.1s, 340 tokens)
     - Tool call: search_knowledge_base("refund") (0.02s)
     - LLM call 2: generate response (1.8s, 520 tokens)

3. **Highlight key data points:**
   - Total latency per span
   - Token count and cost per LLM call
   - Tool call inputs and outputs
   - The complete reasoning chain

4. **Find the most expensive query** — Sort by tokens/cost

Narration: "This is what production monitoring looks like. Every step the agent took, every token it consumed, every tool it called — all visible in one waterfall. When something goes wrong in production, this is how you find out why."

### Scene 4: Cost Analysis (15s)

Show Langfuse's cost breakdown:
```
Query 1 (pricing):   $0.0004  (simple KB lookup)
Query 2 (account):   $0.0008  (KB lookup + customer lookup)
Query 3 (refund):    $0.0012  (KB lookup + reasoning + response)
```

Narration: "Each trace has a dollar cost. Multiply by your daily volume and you know your exact agent cost."

## Post-Production Notes
- Record Langfuse dashboard at 1920x1080
- Zoom into span details when showing waterfall
- Use callout arrows to highlight important metrics
- Show the real Langfuse UI — don't mock it
- If Langfuse UI changes, this demo may need re-recording
