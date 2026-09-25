# Lab 08: Langfuse Tracing and Root Cause Diagnosis

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 09 — Observability with Langfuse                      |
| **Duration**       | 75 minutes                                                   |
| **Difficulty**     | Intermediate                                                 |
| **Learning Objective** | Instrument a multi-step agent with Langfuse tracing, run five queries, navigate the dashboard to find the longest/most expensive/failing spans, and diagnose a root cause from the trace data. |

---

## Prerequisites

- Completed **Lab 01** (can run the support agent)
- A free Langfuse cloud account at [cloud.langfuse.com](https://cloud.langfuse.com)
- `.env` configured with `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Create a Langfuse account

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com)
2. Sign up for a free account
3. Create a new project called `agent-eval-lab`
4. Navigate to **Settings > API Keys** and create a new key pair

### 2. Add Langfuse credentials to `.env`

```dotenv
# .env (append these lines)
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

> **Never commit Langfuse keys to version control.**

### 3. Verify Langfuse installation

```bash
pip show langfuse
```

You should see version `2.50.x` or higher. If not:

```bash
pip install "langfuse>=2.50.0,<3.0"
```

### 4. Test the connection

```python
python -c "
from langfuse import Langfuse
from dotenv import load_dotenv
load_dotenv()
lf = Langfuse()
print('Langfuse connection OK' if lf.auth_check() else 'Connection FAILED')
"
```

---

## Step-by-Step Instructions

### Step 1 — Review the existing tracing setup

```bash
cat observability/langfuse_setup.py
```

Key components:
- `init_langfuse()` — initializes the Langfuse client from env vars
- `traced_agent_call()` — wraps the support agent with `@observe` decorator
- `log_eval_score()` — logs evaluation scores to a trace
- `get_trace_summary()` — retrieves trace data for analysis

### Step 2 — Create the instrumented lab script

Create `lab08_tracing.py`:

```python
"""
Lab 08 — Langfuse Tracing Lab
Run: python lab08_tracing.py
"""

import os
import time
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

load_dotenv()

from agents.support_agent import (
    run_support_agent,
    execute_tool,
    SYSTEM_PROMPT,
    TOOLS,
)
from openai import OpenAI

client = OpenAI()
langfuse = Langfuse()


@observe(name="tool-execution")
def traced_tool_call(tool_name: str, arguments: dict) -> str:
    """Execute a tool with tracing — each tool call becomes a span."""
    langfuse_context.update_current_observation(
        input={"tool": tool_name, "arguments": arguments},
    )
    result = execute_tool(tool_name, arguments)
    langfuse_context.update_current_observation(
        output=result,
    )
    return result


@observe(name="llm-call")
def traced_llm_call(messages: list, call_number: int) -> dict:
    """Make an LLM call with tracing — each call becomes a span."""
    langfuse_context.update_current_observation(
        input={"call_number": call_number, "message_count": len(messages)},
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    langfuse_context.update_current_observation(
        output=response.choices[0].message.content or "(tool call)",
        metadata={
            "tokens": response.usage.total_tokens if response.usage else 0,
            "finish_reason": response.choices[0].finish_reason,
        },
    )
    return response


@observe(name="support-agent-traced")
def run_agent_with_full_tracing(user_message: str) -> dict:
    """
    Run the support agent with full span-level tracing.
    Each LLM call and tool execution is a separate span.
    """
    import json

    langfuse_context.update_current_trace(
        user_id="lab-student",
        metadata={"lab": "lab-08", "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")},
        tags=["lab-08"],
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": user_message})

    tool_calls_log = []
    llm_calls = 0
    total_tokens = 0

    for iteration in range(5):
        response = traced_llm_call(messages, call_number=iteration + 1)

        llm_calls += 1
        total_tokens += response.usage.total_tokens if response.usage else 0
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = traced_tool_call(tool_call.function.name, args)

                tool_calls_log.append({
                    "tool": tool_call.function.name,
                    "arguments": args,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            final_response = choice.message.content or ""
            langfuse_context.update_current_observation(
                output=final_response,
                metadata={
                    "total_tokens": total_tokens,
                    "llm_calls": llm_calls,
                    "tool_calls_count": len(tool_calls_log),
                },
            )
            return {
                "response": final_response,
                "tool_calls": tool_calls_log,
                "total_tokens": total_tokens,
                "llm_calls": llm_calls,
            }

    return {
        "response": "Max iterations reached.",
        "tool_calls": tool_calls_log,
        "total_tokens": total_tokens,
        "llm_calls": llm_calls,
    }


# ── Run 5 Diverse Queries ─────────────────────────────────────────
QUERIES = [
    "What are your pricing plans?",
    "Can you look up my account? My email is alice@example.com",
    "I've been charged twice. My ID is CUST-001. Please create a ticket.",
    "I'm furious — your product lost all my data. I need a manager NOW.",
    "Can your product integrate with SAP and support SAML SSO?",
]


if __name__ == "__main__":
    print("=" * 60)
    print("Lab 08: Running 5 traced queries")
    print("=" * 60)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n--- Query {i}: {query[:50]}...")
        start = time.perf_counter()
        result = run_agent_with_full_tracing(query)
        elapsed = time.perf_counter() - start

        print(f"    Response: {result['response'][:80]}...")
        print(f"    Tools: {[tc['tool'] for tc in result['tool_calls']]}")
        print(f"    Tokens: {result['total_tokens']}")
        print(f"    LLM calls: {result['llm_calls']}")
        print(f"    Latency: {elapsed:.2f}s")

    # Flush traces to Langfuse
    langfuse.flush()

    print("\n" + "=" * 60)
    print("All traces sent to Langfuse.")
    print("Open your Langfuse dashboard to explore the traces.")
    print(f"Dashboard: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
    print("=" * 60)
```

### Step 3 — Run the traced queries

```bash
python lab08_tracing.py
```

Wait for the script to complete. All five queries will be traced.

### Step 4 — Navigate the Langfuse dashboard

Open your Langfuse dashboard in a browser:

1. **Traces tab** — You should see 5 traces tagged with `lab-08`
2. Click on any trace to see the **span waterfall** — each LLM call and tool execution is a separate span

### Step 5 — Find the longest span

In the Langfuse dashboard:

1. Go to the **Traces** tab
2. Sort by **Latency** (descending)
3. Click the slowest trace
4. In the span waterfall, identify which span took the longest

**Record in your notes:**

```markdown
### Longest Span
- **Trace:** [trace name / query]
- **Span:** [span name, e.g., "llm-call #2"]
- **Duration:** [X.XX seconds]
- **Reason:** [why this span was slow — model inference, network, etc.]
```

### Step 6 — Find the most expensive span

1. In the trace detail view, look at the **Tokens** column
2. Or sort traces by token count if the dashboard supports it
3. Identify which query consumed the most tokens

**Record:**

```markdown
### Most Expensive Span
- **Trace:** [trace name / query]
- **Total tokens:** [X,XXX]
- **Estimated cost:** $[X.XXXX]
- **Reason:** [multi-turn tool calling, long system prompt, etc.]
```

### Step 7 — Find and diagnose a failing span

The "SAP integration" query (Query 5) likely produces a lower-quality response because the knowledge base doesn't cover it.

1. Open the trace for Query 5
2. Look at the `search_knowledge_base` tool span — what did it return?
3. Look at the final LLM call — did the model hallucinate despite getting "No relevant articles found"?

**Root Cause Diagnosis:**

```markdown
### Failing Span Diagnosis
- **Trace:** Query 5 — SAP integration question
- **Failing span:** [which span]
- **Root cause:** The knowledge base returned no results for the query.
  The LLM then [hallucinated features / correctly admitted uncertainty].
- **Impact:** [Customer gets wrong information / appropriate response]
- **Fix:** [Add SAP integration docs to KB / improve fallback behavior]
```

---

## Expected Output

### Console output:

```
============================================================
Lab 08: Running 5 traced queries
============================================================

--- Query 1: What are your pricing plans?...
    Response: TechCorp offers three plans: Basic at $9.99...
    Tools: ['search_knowledge_base']
    Tokens: 385
    LLM calls: 2
    Latency: 2.14s

--- Query 2: Can you look up my account? My email is alic...
    Response: I found your account! You are Alice Johnson...
    Tools: ['lookup_customer']
    Tokens: 412
    LLM calls: 2
    Latency: 1.87s

...

============================================================
All traces sent to Langfuse.
Open your Langfuse dashboard to explore the traces.
Dashboard: https://cloud.langfuse.com
============================================================
```

### Langfuse dashboard:

You should see 5 traces, each containing nested spans for LLM calls and tool executions.

---

## Verification Checklist

- [ ] Langfuse cloud account is created and API keys are in `.env`
- [ ] `langfuse.auth_check()` returns `True`
- [ ] All 5 queries ran and produced traces
- [ ] Traces appear in the Langfuse dashboard with `lab-08` tag
- [ ] You can see the span waterfall for each trace
- [ ] You identified the **longest** span and recorded the duration
- [ ] You identified the **most expensive** span and recorded the token count
- [ ] You diagnosed the root cause of the failing/low-quality span
- [ ] All three findings are documented in structured notes

---

## Common Pitfalls

1. **Traces don't appear in the dashboard** — Langfuse batches trace uploads. Call `langfuse.flush()` at the end of your script (already included above) and wait 10–30 seconds before checking the dashboard.

2. **`LANGFUSE_PUBLIC_KEY` vs. `LANGFUSE_SECRET_KEY` swapped** — The public key starts with `pk-lf-` and the secret key starts with `sk-lf-`. If swapped, `auth_check()` will fail.

3. **Nested `@observe` decorators not creating child spans** — Langfuse uses Python's context variables to track the current trace. If you run traced functions in threads or async without proper context propagation, child spans may appear as separate traces.

---

## Extension Challenge

**Advanced:** Add evaluation scores to the traces using `log_eval_score()`. After running each query:

1. Evaluate the response with `AnswerRelevancyMetric` from DeepEval
2. Log the score to the Langfuse trace using `langfuse_context.score_current_trace()`
3. In the Langfuse dashboard, filter traces by score to find the lowest-quality responses

```python
from langfuse.decorators import langfuse_context

# After getting the result, score the trace
langfuse_context.score_current_trace(
    name="answer_relevancy",
    value=0.85,  # Replace with actual metric score
    comment="Evaluated by AnswerRelevancyMetric",
)
```

This connects evaluation results directly to agent traces — the foundation of production monitoring.
