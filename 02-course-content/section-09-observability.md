# Section 9: Agent Observability & Tracing

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 09 (curriculum `01-curriculum/full-curriculum.md`, Module 09)
> **Section runtime:** 24 minutes (3 lectures; Lab 9.1 follows Lecture 9.2)
> **Running example:** the TechCorp support agent, `agents/support_agent.py`, traced two ways: with Langfuse v4 (`observability/langfuse_tracing.py`) and with vendor-neutral OpenTelemetry GenAI spans (`observability/otel_genai.py`).
> **Source of truth:** `14-quality-review/course2-bible.md` and the code in `04-code-examples/agent-eval-framework/`. If this script and the code disagree, the code wins.
> **API guardrails (do not deviate on screen):** Langfuse v4 only: `from langfuse import Langfuse, get_client, observe, propagate_attributes`; trace attributes via `propagate_attributes(...)`; scores via `get_client().create_score(...)`. Never show any Langfuse v2-era decorator, context or trace-update API, even as "the old way" (bible §2.2 lists what does not exist in v4). OpenTelemetry: official `opentelemetry-semantic-conventions` names (`gen_ai.*`, imported from `opentelemetry.semconv._incubating.attributes`); never `opentelemetry.semconv.ai`.
> **Production format:** HeyGen avatar for `[AVATAR]` blocks; OBS screen recording for `[SCREEN]`, `[CODE]` and `[DEMO]`; slides built from `[SLIDE]` cues by `slide_builder.py`. Diagrams are Course 2 masters in `10-graphics/diagrams/` (D-numbers).
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "Verified: openai 2.54.0 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0 | opentelemetry-semantic-conventions 0.66b0. Offline mode: mock LLM + mock judge."
> **Numbers:** offline mode. Token counts come from the mock LLM (`len(text)//4`), latencies from a simulated clock, costs from `gpt-4.1-mini` list prices in `config/settings.py` (verify current pricing). Trace IDs change on every run; never read one aloud. Where a Langfuse UI walkthrough is scripted, it needs a live Langfuse project: re-capture live before recording.
> **Word counts** are spoken words only. Build-along lectures run below 140 words per minute to leave room for code, commands and output.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 9.1 | Why You Can't Debug an Agent Without Traces | Teach + demo | 8:00 | 956 |
| 9.2 | Tracing with Langfuse: Spans, Costs & Latency | Build-along | 8:00 | 831 |
| 9.3 | OpenTelemetry GenAI Conventions: The Enterprise Standard | Build-along | 8:00 | 768 |
| | **Total** | | **24:00** | **2,555** |

**Cue legend:** as in `section-05-rag-eval.md`. `[DEMO]` blocks are pasted from real runs; `[CODE]` blocks are copied from the named file.

**Code names used in this section (matched to `04-code-examples/agent-eval-framework/`):** `init_langfuse`, `TracedOpenAI`, `traced_tool`, `traced_support_agent`, `_traced_run`, `score_trace`, `offline_spans`, `print_trace`, `LOCAL_SCORES` in `observability/langfuse_tracing.py`; `make_tracer`, `OTelOpenAI`, `make_tool_executor`, `run_with_otel`, `spans_as_rows`, `AGENT_NAME` in `observability/otel_genai.py`; `cost_usd` in `config/settings.py`; `count_tokens` in `performance/tokens.py`; env vars `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (`.env.example`).

---

## Lecture 9.1 — Why You Can't Debug an Agent Without Traces

| Field | Value |
|---|---|
| ID | 9.1 |
| Title | Why You Can't Debug an Agent Without Traces |
| Type | Teach + demo |
| Target duration | 8:00 (about 956 spoken words, 6:50 of talking at 140 wpm) |
| Learning objectives | 1. Explain why logs of requests and responses can't explain a multi-step, non-deterministic agent. 2. Describe a trace: one agent run as a tree of spans (agent, generations, tools) with inputs, outputs, tokens, cost, latency and level. 3. Find the failing step of a broken agent run from its trace. |
| Prerequisites | Module 1 (the agent loop); Module 6 (tool calls) |
| Files used | `demos/m09_blind_vs_traced.py`; `observability/langfuse_tracing.py` (`traced_tool`, `print_trace`); diagram D13 (`10-graphics/diagrams/D13-trace-anatomy.svg`, builds 1 to 3) |
| Version banner | `Verified: openai 2.54.0 | langfuse 4.16.0` |

### Script

[AVATAR]
Friday, half past four. A deploy goes out. By five, the TechCorp support agent answers every refund question the same way: "I couldn't find that in our knowledge base." [PAUSE] Health checks are green. Every request returns 200. There are no errors in the logs. So where do you look? The prompt? The model? A rate limit? By the end of this lecture, you'll be able to find the broken step of an agent run in one look, and you'll see why that's impossible without a trace.

[SLIDE 1: What your logs say]
- 200 OK
- Latency: normal
- Errors: none
- Reply: "I couldn't find that in our knowledge base"
Footer: Verified: openai 2.54.0 | langfuse 4.16.0. Offline mode: mock LLM + mock judge.

Here's everything traditional monitoring gives you. The request succeeded. Latency is normal. No exceptions. And a reply that's polite, honest and useless. Every dashboard is green, and every customer is unhappy. What would you check first? [PAUSE] Most people open the prompt. Hold that instinct. In a few minutes, you'll see the prompt was the one part working perfectly, and that editing it would have made Friday night longer, not shorter.

[SLIDE 2: Why agents need more than logs]
- Many steps per request, not one
- A different path on every run
- The failure is often a step, not the reply

Why isn't a log line enough? Three reasons. An agent request isn't one call. It's a loop of model calls and tool calls, often four or five steps. The path can change from run to run, because the model decides what to do next. And the failure usually hides in a middle step, while the final reply looks perfectly reasonable.

[B-ROLL: Animation, labelled "illustrative": the same customer question sent three times; the first run takes the path search, reply; the second takes lookup, search, reply; the third takes search, search, reply. Paths drawn as three coloured lines through the D3 agent loop.]

And you can't simply re-run the request to watch it fail. Remember Module 2: same input, different outputs. Have you ever tried to reproduce an agent bug and watched it work perfectly? By the time you try, the agent may take a different path. So you record the path the first time, on every request.

A log tells you what went in and what came out. A trace tells you everything in between.

[SLIDE 3: Anatomy of an agent trace]
Diagram: D13, shown as builds 1 to 3: the trace, one box for the whole agent run with user, session and total cost; the spans, nested children (generation, tool, generation) with tokens, cost and latency; the root cause, one tool span highlighted amber with its empty output.

Here's a trace. The top box is one agent run, with who asked, which session, and the total cost. Inside it are spans, one per step. A generation span is a model call: the model, the messages, the tokens and the cost. A tool span is a tool call: its arguments and its result. Spans nest, so you can see which step caused which.

And each span has a level. A tool that returns nothing can be marked as a warning. That's the detail that will crack our Friday incident.

[CODE: `observability/langfuse_tracing.py`, `traced_tool`]
```python
@observe(name="tool", as_type="tool")
def traced_tool(name: str, arguments: dict) -> str:
    get_client().update_current_span(name=f"tool {name}", input=arguments)
    result = execute_tool(name, arguments)
    level = "WARNING" if result.startswith(("No relevant", "Customer not found")) else "DEFAULT"
    get_client().update_current_span(output=result, level=level)
    return result
```

Here's the instrumentation for every tool call, using Langfuse version four. One decorator turns the function into a tool span. The span records the arguments and the result. And if the result is "no relevant articles" or "customer not found", the level becomes WARNING. Six lines of code. You'll build the rest in the next lecture.

[SCREEN: Terminal. Run the blind-versus-traced demo; pause on BLIND, then on the trace tree.]

```bash
uv run python demos/m09_blind_vs_traced.py
```

[DEMO: Output (banner trimmed; the trace ID changes on every run)]
```text
BLIND: all you have is the final output
  Q: What is your refund policy?
  A: I couldn't find that in our knowledge base, so I don't want to guess. I can create a ticket so a specialist can answer.
  Is it the prompt? the model? a rate limit? You can't tell.

TRACED: Langfuse trace 7ba2c933eafa15bc6ba7134b2862d64d
agent      support-agent
  generation chat gpt-4.1-mini                usage={"input": 767, "output": 35}
  tool       tool search_knowledge_base       <-- WARNING
             output: No relevant articles found in the knowledge base.
  generation chat gpt-4.1-mini                usage={"input": 842, "output": 29}

Root cause in one look: search_knowledge_base returned nothing; the model behaved correctly.
(For comparison, the healthy tool returns: KB-102 (Refund policy): TechCorp offers a 30-day money-back ...)
```

This demo simulates the Friday deploy: the search index is broken, so every search comes back empty. What would you guess from the first half alone? First, the blind view. A question, an answer, and nothing else. Is it the prompt? The model? You can't tell.

[SCREEN: Zoom on the trace tree; highlight the WARNING line and its output.]

Now the same run, traced. Four spans. The agent at the top. A generation: the model read 767 input tokens and decided to search. A tool span, flagged WARNING, and its output: "No relevant articles found." Then a second generation, 842 tokens in, where the model wrote that polite "I couldn't find it" reply.

Read that trace again. Did the model do anything wrong? [PAUSE] No. It searched, got nothing, and refused to guess, which is exactly what the prompt asks. The root cause is the search index. The healthy tool returns the refund article, KB-102. If you'd edited the prompt on Friday night, you'd have changed working code and fixed nothing.

[SLIDE 4: What to read in every trace]
- Which step failed, and its level
- Tokens per call: is input growing?
- Latency per step: where's the wait?
- Tool success and retries
- Cost per run

Here's what to read in every trace. Which step failed, and its level. Tokens per call: notice input grew from 767 to 842, because each model call re-sends the whole conversation. Latency per step, to find the slow one. Tool success, and how many retries. And the total cost of the run. Lecture 9.3 turns those token counts into a cost breakdown. Which of those five would have cracked the Friday incident fastest? [PAUSE] The first: one WARNING on one tool span.

[SLIDE 5: Traces and evals work together]
- Failed eval: open its trace to see why
- Production trace: score it, like an eval
- Bad trace: becomes a new golden test

Traces aren't just for incidents. They connect to everything you've built so far. When an eval fails in CI, its trace shows which step broke. When a production trace looks wrong, you can attach a score to it, exactly like an eval score. And a bad production trace becomes a new golden test case, so it can never happen twice. That's layer five of the pyramid, production monitoring, feeding back into layers three and four.

[SCREEN: Terminal. Run the Lab 9.1 reference demo and show only the BEFORE FIX block.]

```bash
uv run python demos/m09_lab_trace_find_fix.py
```

[DEMO: Output (banner and AFTER FIX block trimmed)]
```text
--- BEFORE FIX ---
What are your pricing plans?                           ok
How do I reset my password?                            ok
What is your refund policy?                            ok
Can you check my account? My email is Alice@Example.   FAILING span: tool lookup_customer -> Customer not found.
What are the API rate limits for the Pro plan?         FAILING span: tool search_knowledge_base -> No relevant articles found in the knowledge b
```

You'll practise exactly this in Lab 9.1, right after the next lecture. Five traced questions, two of them failing. One is an email typed in mixed case that the lookup can't find. The other is an API question whose article is missing from the search index. Your job is to find both failing spans from the traces alone, fix them, and re-run to prove it.

[AVATAR]
Here's the rule for this module. When an agent misbehaves, read the trace before you touch the prompt. In our incident, a trace turned a two-hour guessing game into a one-line diagnosis: the tool returned nothing. And it cost six lines of instrumentation. Is there any agent you run today that you couldn't trace like this? That's the one to fix first.

[SLIDE 6: Recap]
- Final outputs hide the failing step
- Traces show every call, tool and token
- Read the trace before the prompt

### Recap

An agent request is a loop of model and tool calls, so logs and green dashboards can't show where it broke. A trace records every step as a span with inputs, outputs, tokens, cost and level, and in our Friday incident it showed in one look that the search index failed while the model behaved correctly.

### Transition

In Lecture 9.2, you'll build that tracing yourself with Langfuse version four: spans, users and sessions, costs, latency, and evaluation scores attached to every trace.

### Speaker notes: common student mistakes / Q&A

- **Offline.** Spans are captured by an in-memory OpenTelemetry exporter inside the Langfuse client, then printed. Token counts are the mock's `len(text)//4`. The trace ID changes every run; never read it aloud. If you want the Langfuse UI on screen, set `LANGFUSE_*` keys and re-capture live before recording.
- **The Friday incident** is illustrative (adapted from the curriculum's CloudOps scenario; the demo's docstring calls it "the 16:30 deploy"). Do not attach a real company or "2 hours" figure as a statistic; "a two-hour guessing game" is the story's framing.
- **"Why does input grow from 767 to 842?"** The second call carries the first call's tool request and the tool result. Lecture 9.3 measures this.
- **Logging vs tracing** (curriculum Q1): logs record events; traces record the parent-child structure between steps. Both are useful; agents need the structure.
- The A5 screen beat is the demo; the diagram D13 is shown as three builds.

---

## Lecture 9.2 — Tracing with Langfuse: Spans, Costs & Latency

| Field | Value |
|---|---|
| ID | 9.2 |
| Title | Tracing with Langfuse: Spans, Costs & Latency |
| Type | Build-along |
| Target duration | 8:00 (about 831 spoken words, 5:56 of talking at 140 wpm; the rest is code and output) |
| Learning objectives | 1. Instrument an agent with Langfuse v4: `@observe(as_type=...)` for the agent and tools, and a generation per model call with usage and cost. 2. Add user, session, tags and version to every span with `propagate_attributes`. 3. Attach evaluation scores to traces with `create_score`, and read cost and latency per trace. |
| Prerequisites | 9.1; Module 4 (AnswerRelevancyMetric) |
| Files used | `observability/langfuse_tracing.py`; `demos/m09_langfuse_tracing.py`; `tests/production/test_observability.py`; `.env.example` (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`) |
| Version banner | `Verified: openai 2.54.0 | langfuse 4.16.0` |

### Script

[AVATAR]
Four customers. Four questions. One of them cost almost twice as much as the others, made an extra model call and created a ticket. [PAUSE] Which one, and why? With Langfuse, that's a table you read, not an investigation you run. By the end of this lecture, you'll be able to trace an agent with Langfuse version four, attach users, sessions and costs to every step, and put evaluation scores right on the trace.

[SLIDE 1: Langfuse v4 in four calls]
- `@observe(as_type=...)`: a function becomes a span
- `propagate_attributes(...)`: user, session, tags, version
- `start_as_current_observation(as_type="generation")`: a model call
- `create_score(...)`: an eval result on a trace
Footer: Verified: openai 2.54.0 | langfuse 4.16.0. Offline mode: mock LLM + mock judge.

Langfuse is an open-source platform for tracing and evaluating LLM apps, and version four is built on OpenTelemetry. You need four calls. The observe decorator turns a function into a span. Propagate attributes stamps the user, session and version onto every span. A generation observation records a model call. And create score attaches an evaluation result to a trace.

[SLIDE 2: Using a tutorial? Check its version]
- This course: `langfuse` 4.16
- Everything imports from the `langfuse` package
- Trace attributes: `propagate_attributes`
- An import error usually means a v2-era tutorial

A warning, because you'll meet old code. Langfuse changed its Python API between major versions, and many tutorials online were written for version two. If an import from a tutorial fails, what should you check first? [PAUSE] The version it targets, before you debug anything else. In version four, everything you need imports straight from the `langfuse` package, and trace attributes always come from `propagate_attributes`.

[CODE: `observability/langfuse_tracing.py`, the agent span and trace attributes]
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

Here's the top of the trace. The decorator makes this function a span of type agent, named support-agent. Inside it, `propagate_attributes` sets the user ID, the session ID, two tags, the agent version and some metadata. Every span created inside this block inherits them. That's how you'll later filter "all traces for CUST-001" or "everything from version two".

Notice that we didn't rewrite the agent. We passed it a traced OpenAI client and a traced tool executor. Why does that matter? [PAUSE] Because your tracing code and your agent code stay separate, so turning tracing off can't break the agent.

[CODE: `observability/langfuse_tracing.py`, `TracedOpenAI.create`]
```python
    def create(self, **kwargs: Any) -> Any:
        model = kwargs.get("model", "")
        with get_client().start_as_current_observation(
            name=f"chat {model}", as_type="generation", model=model, input=kwargs.get("messages")
        ) as gen:
            resp = self._inner.chat.completions.create(**kwargs)
            usage = resp.usage
            msg = resp.choices[0].message
            out = msg.content or [tc.function.name for tc in (msg.tool_calls or [])]
            gen.update(
                output=out,
                usage_details={"input": usage.prompt_tokens, "output": usage.completion_tokens},
                cost_details={"total": cost_usd(model, usage.prompt_tokens, usage.completion_tokens)},
            )
            return resp
```

Every model call goes through this wrapper. Why wrap the client instead of decorating the agent's loop? Because the loop is the agent's code, and the client is the one place every model call passes through. It opens a generation observation with the model name and the messages. After the call, it records the output, the input and output tokens, and the cost. If the model asked for tools, the output is the list of tool names, so you can see the decision.

[SLIDE 3: `gpt-4.1-mini` list prices (verify current pricing)]
- Input: $0.40 per million tokens
- Cached input: $0.10 per million tokens
- Output: $1.60 per million tokens
- Source: `config/settings.py`

The cost comes from `gpt-4.1-mini` list prices in the course settings: forty cents per million input tokens and a dollar sixty per million output. Verify current pricing before you trust any number.

The tool spans are the six lines from Lecture 9.1, with the WARNING level for empty results.

[CODE: `observability/langfuse_tracing.py`, `score_trace`]
```python
def score_trace(trace_id: str, name: str, value: float, comment: str | None = None) -> None:
    """Attach an evaluation score to a trace (Langfuse create_score)."""
    if langfuse_configured():
        get_client().create_score(trace_id=trace_id, name=name, value=value, comment=comment, data_type="NUMERIC")
    else:
        LOCAL_SCORES.append({"trace_id": trace_id, "name": name, "value": value, "comment": comment})
```

Now evaluation. After each run, the demo scores the answer with DeepEval's answer relevancy metric from Module 4, then calls `create_score` with the trace ID, a name and the value. In Langfuse, that score sits right on the trace. With no Langfuse keys, the course records it locally instead, so everything still runs offline. What can you do with scores on traces? Filter for every trace with relevancy under 0.7, and you have this week's list of bad answers, each with its full trace attached.

[SCREEN: Terminal. Run the tracing demo; pause on the table, then on the trace tree.]

```bash
uv run python demos/m09_langfuse_tracing.py
```

[DEMO: Output (banner trimmed)]
```text
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

Four traces, one row each. Three of them took two model calls, about seventeen hundred tokens, and under a tenth of a cent. Which one is the outlier? [PAUSE] The double charge. Six spans, three model calls, almost three thousand tokens, and fourteen hundredths of a cent. Nearly twice the cost, and you can see why in its tree.

[SCREEN: Zoom on the trace tree.]

Look up the customer. Create the ticket, TKT-5001, high priority. Then reply. Three generations, and the input grows each time, from 787 to 949 to 1,092 tokens, because each call carries everything before it. All four traces got a relevancy score of 1.00, attached with `create_score`.

The latency column is simulated in offline mode, but the pattern holds live: more steps, more time. The ticket request took about three point three seconds against under two for the others.

[SCREEN: PRODUCTION NOTE: re-capture live before recording. With `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_BASE_URL` set, run the same demo and record the Langfuse UI: the Traces list filtered by user CUST-001, the double-charge trace's timeline, its cost and the answer_relevancy score, then the Sessions view.]

In the Langfuse UI, the same data becomes clickable. What would you click first? Filter by user and you see Alice's two requests. Open the double-charge trace and you get a timeline, every input and output, the cost and the score. Group by session, and a whole conversation lines up in order.

[SCREEN: Terminal. Run the observability tests.]

```bash
uv run pytest -q tests/production/test_observability.py
```

[DEMO: Output (trimmed)]
```text
...                                                                      [100%]
3 passed in 0.48s
```

Does tracing need tests? Yes. Three of them: the trace has the right span types in order, agent, generation, tool, generation, with the user and session on every span; scores are recorded; and the OpenTelemetry version, which is next lecture.

[SLIDE 4: Recap]
- `@observe` turns functions into typed spans
- `propagate_attributes` adds user, session, version
- `create_score` puts eval results on traces

### Recap

Langfuse version four traces an agent with four calls: observe for the agent and tool spans, a generation per model call with tokens and cost, propagate attributes for user, session and version, and create score to put evaluation results on the trace. The double-charge request stood out at three model calls and nearly twice the cost.

### Transition

Langfuse is one backend. In Lecture 9.3, you'll emit the same trace in the vendor-neutral OpenTelemetry GenAI format, which Langfuse, Jaeger, Grafana Tempo and Datadog can all read, and see where the tokens really go.

### Speaker notes: common student mistakes / Q&A

- **Offline.** Spans go to an in-memory exporter (no Langfuse server contacted); tokens are the mock's `len(text)//4`; latency is a simulated clock; costs use `gpt-4.1-mini` at $0.40 / $1.60 per million tokens from `config/settings.py` (verify current pricing). The UI walkthrough needs a live Langfuse project: re-capture live before recording. `TKT-5001` counts up per process.
- **`ModuleNotFoundError` on a Langfuse submodule**: the student is following a v2-era tutorial. v4 imports `Langfuse`, `get_client`, `observe` and `propagate_attributes` from `langfuse` itself.
- **Host variable:** v4 uses `LANGFUSE_BASE_URL`; the course code also accepts the older `LANGFUSE_HOST`.
- **"How do I set trace-level attributes?"** In v4 they come only from `propagate_attributes(...)`; span-level updates use `get_client().update_current_span(...)`.
- **Flush on exit** in short scripts: `get_client().flush()`, or the last spans may never reach Langfuse (the module's `__main__` does this).
- **Lab 9.1** (Trace, Find, Fix) follows this lecture: `demos/m09_lab_trace_find_fix.py` is the reference (two failing spans: a mixed-case email that `lookup_customer` can't find, and the API article missing from search; fixes: lowercase emails, re-index KB-104).

---

## Lecture 9.3 — OpenTelemetry GenAI Conventions: The Enterprise Standard

| Field | Value |
|---|---|
| ID | 9.3 |
| Title | OpenTelemetry GenAI Conventions: The Enterprise Standard |
| Type | Build-along |
| Target duration | 8:00 (about 768 spoken words, 5:29 of talking at 140 wpm; the rest is code and output) |
| Learning objectives | 1. Explain what the OpenTelemetry GenAI semantic conventions standardize: span names and `gen_ai.*` attributes for agents, model calls and tool calls. 2. Emit those spans with the official `opentelemetry-semantic-conventions` constants and test them like any other output. 3. Use the token attributes to find where an agent's cost goes, and name three levers to reduce it. |
| Prerequisites | 9.2 |
| Files used | `observability/otel_genai.py`; `demos/m09_otel_genai.py`; `demos/m09_cost_analysis.py`; `tests/production/test_observability.py` (`test_otel_genai_semantic_conventions`); `config/settings.py` (`cost_usd`) |
| Version banner | `Verified: openai 2.54.0 | opentelemetry-sdk 1.45.0 | opentelemetry-semantic-conventions 0.66b0 | langfuse 4.16.0` |

### Script

[AVATAR]
Your platform team runs Datadog. Your ML team lives in Langfuse. Security wants everything in Grafana. [PAUSE] Do you instrument the agent three times? No. You emit one kind of span, in one standard format, and every backend reads it. By the end of this lecture, you'll be able to trace an agent with the OpenTelemetry GenAI conventions, test that telemetry like code, and use it to find where three quarters of your tokens go.

[SLIDE 1: OpenTelemetry GenAI conventions]
- OpenTelemetry: the open standard for traces
- GenAI conventions: shared names for AI spans
- Agent, model call, tool call
- Status: still marked "incubating"
Footer: Verified: opentelemetry-sdk 1.45.0 | opentelemetry-semantic-conventions 0.66b0. Offline mode: mock LLM.

OpenTelemetry is the open standard for traces, metrics and logs, supported by almost every observability vendor. Its semantic conventions are agreed names, so a span from your code means the same thing in every tool. The GenAI conventions add names for AI work: invoking an agent, calling a model, executing a tool.

One honest caveat. These names are still marked incubating, which means they can change between releases. So pin your versions, and test your telemetry, which we'll do in a minute.

[SLIDE 2: Three span types, official names]
- `invoke_agent {agent}`: the whole agent run
- `chat {model}`: one model call
- `execute_tool {tool}`: one tool call
- Attributes: `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`

Why agree on names at all? So a dashboard built for one agent works for every agent, and a backend can show token costs without knowing your code. Three span names. `invoke_agent` plus the agent name, for the whole run. `chat` plus the model, for each model call. `execute_tool` plus the tool, for each tool call. And on each span, attributes with a `gen_ai` prefix: the operation, the provider, the model, the token counts, the tool's name, arguments and result.

[CODE: `observability/otel_genai.py`, imports and `OTelOpenAI.create`]
```python
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as GenAI

def create(self, **kwargs: Any) -> Any:
    model = kwargs.get("model", "")
    with self._tracer.start_as_current_span(f"chat {model}", kind=trace.SpanKind.CLIENT) as span:
        span.set_attribute(GenAI.GEN_AI_OPERATION_NAME, GenAI.GenAiOperationNameValues.CHAT.value)
        span.set_attribute(GenAI.GEN_AI_PROVIDER_NAME, GenAI.GenAiProviderNameValues.OPENAI.value)
        span.set_attribute(GenAI.GEN_AI_REQUEST_MODEL, model)
        if kwargs.get("temperature") is not None:
            span.set_attribute(GenAI.GEN_AI_REQUEST_TEMPERATURE, kwargs["temperature"])
        resp = self._inner.chat.completions.create(**kwargs)
        span.set_attribute(GenAI.GEN_AI_RESPONSE_MODEL, resp.model)
        span.set_attribute(GenAI.GEN_AI_RESPONSE_ID, resp.id)
        span.set_attribute(GenAI.GEN_AI_RESPONSE_FINISH_REASONS, [c.finish_reason for c in resp.choices])
        span.set_attribute(GenAI.GEN_AI_USAGE_INPUT_TOKENS, resp.usage.prompt_tokens)
        span.set_attribute(GenAI.GEN_AI_USAGE_OUTPUT_TOKENS, resp.usage.completion_tokens)
        return resp
```

Look at the import first, because it's the most common mistake. The constants come from the official `opentelemetry-semantic-conventions` package, from its incubating attributes module. If a tutorial imports `opentelemetry.semconv.ai`, that's a different, third-party package with its own names. Same idea, wrong names.

Then the wrapper, the same pattern as the Langfuse one. Open a `chat` span. Record what was requested, the operation, the provider and the model. Make the call. Record what came back: the response model, ID, finish reasons and token counts. Why record both the requested and the response model? [PAUSE] Because they can differ, and when a provider quietly serves a different model version, you'll want to know.

[SCREEN: VS Code, `observability/otel_genai.py`. Scroll to `make_tool_executor` and highlight `span.set_status(Status(StatusCode.ERROR, "empty tool result"))`.]

The tool executor does the same for `execute_tool` spans: the tool name, its arguments and its result. And an empty result sets the span's status to ERROR. That's the OpenTelemetry version of the WARNING level from 9.1, and every backend can alert on it.

[SCREEN: Terminal. Run the OTel demo.]

```bash
uv run python demos/m09_otel_genai.py
```

[DEMO: Output (banner trimmed; second chat span trimmed)]
```text
Answer: I found your account. You are Alice Johnson on the Pro plan, and your account is active with a balance of $0.00.

invoke_agent techcorp-support  [status UNSET]
    gen_ai.operation.name = invoke_agent
    gen_ai.agent.name = techcorp-support
    gen_ai.conversation.id = conv-001
chat gpt-4.1-mini  [status UNSET]
    gen_ai.operation.name = chat
    gen_ai.provider.name = openai
    gen_ai.request.model = gpt-4.1-mini
    gen_ai.response.model = gpt-4.1-mini
    gen_ai.response.id = chatcmpl-mock-a9468b9666-0
    gen_ai.response.finish_reasons = ('tool_calls',)
    gen_ai.usage.input_tokens = 770
    gen_ai.usage.output_tokens = 36
execute_tool lookup_customer  [status UNSET]
    gen_ai.operation.name = execute_tool
    gen_ai.tool.name = lookup_customer
    gen_ai.tool.type = function
    gen_ai.tool.call.arguments = {"identifier": "alice@example.com"}
    gen_ai.tool.call.result = Customer found: {"id": "CUST-001", "name": "Alice Johnson", "email": "
chat gpt-4.1-mini  [status UNSET]
    ...
    gen_ai.response.finish_reasons = ('stop',)
    gen_ai.usage.input_tokens = 932
    gen_ai.usage.output_tokens = 28

Swap InMemorySpanExporter for OTLPSpanExporter to ship these to Langfuse, Jaeger, Tempo or Datadog.
```

Does this match the Langfuse trace from 9.2? Same shape: four spans. The agent run, with its name and a conversation ID. A chat span: OpenAI, `gpt-4.1-mini`, finished with tool calls, 770 tokens in. A tool span: `lookup_customer` with Alice's email, and the result. And a final chat span that finished with "stop", 932 tokens in.

One naming detail. Older examples use `gen_ai.system` for the provider. In the current conventions, that name is deprecated and replaced by `gen_ai.provider.name`, which is what you see here.

How do you send these somewhere real? Swap the in-memory exporter for an OTLP exporter pointed at your backend. Langfuse accepts OpenTelemetry data, and so do Jaeger, Tempo and Datadog. One instrumentation, any destination.

[CODE: `tests/production/test_observability.py`, `test_otel_genai_semantic_conventions`]
```python
def test_otel_genai_semantic_conventions():
    tracer, exporter = make_tracer()
    run_with_otel("Look up my account, alice@example.com", tracer)
    rows = spans_as_rows(exporter)
    assert [r["name"] for r in rows] == ["invoke_agent techcorp-support", "chat gpt-4.1-mini", "execute_tool lookup_customer", "chat gpt-4.1-mini"]
    chat = rows[1]["attributes"]
    assert chat["gen_ai.operation.name"] == "chat" and chat["gen_ai.provider.name"] == "openai"
    assert chat["gen_ai.request.model"] == "gpt-4.1-mini" and chat["gen_ai.usage.input_tokens"] > 0
    assert rows[2]["attributes"]["gen_ai.tool.name"] == "lookup_customer"
```

And here's the step most teams skip: evaluating the agent's telemetry against the conventions. This test runs the agent and asserts the exact span names, in order, and the key attributes. If a library upgrade renames an attribute, or someone breaks the tool span, CI fails before your dashboards go quietly blank. Telemetry is an output. Test it like one.

[SCREEN: Terminal. Run the cost analysis demo.]

```bash
uv run python demos/m09_cost_analysis.py
```

[DEMO: Output (banner trimmed)]
```text
call     input  output      cost $   fixed overhead share
1          788      36    0.000373   93%
2          950      35    0.000436   77%
3         1055     101    0.000584   70%
4         1202      51    0.000562   61%

4 LLM calls, 3995 input tokens, $0.001955 (gpt-4.1-mini, verify current pricing)
System prompt + tool schemas = 736 tokens per call -> 74% of all input tokens in this trace.
Levers: fewer loop iterations, smaller tool schemas, prompt caching (cached input is 75% cheaper on gpt-4.1-mini; verify).
```

Now put the token attributes to work. This is the longest request in the golden set: cancel and refund. Four model calls, almost four thousand input tokens, about a fifth of a cent. Where do the tokens go? [PAUSE] The system prompt and the five tool schemas, 736 tokens, are re-sent on every call. That fixed overhead is 74 percent of all input tokens in this trace. On the first call, it's 93 percent.

So the levers are clear. Fewer loop iterations. Smaller tool schemas. And prompt caching, because cached input is listed at a quarter of the normal price on `gpt-4.1-mini`. Verify current pricing before you build a business case on it. That's exactly where Module 10 picks up.

[SLIDE 3: Recap]
- One `gen_ai` span format, any backend
- Use the official semantic-conventions constants
- Test telemetry; read tokens to find cost

### Recap

The OpenTelemetry GenAI conventions give agent, model and tool spans standard names and `gen_ai` attributes, imported from the official semantic-conventions package, so one instrumentation feeds Langfuse, Jaeger, Tempo or Datadog. Test those spans like any output, and read their token counts: here, fixed prompt overhead was 74 percent of input tokens.

[SLIDE 4: You can now]
- Find a failing step from one trace
- Trace agents in Langfuse v4 with scores
- Emit vendor-neutral `gen_ai` spans with OpenTelemetry

### Transition

You can now see where every token and every second goes. In Lecture 10.1, you'll measure it at scale: latency, token cost and throughput benchmarking across the whole golden set.

### Speaker notes: common student mistakes / Q&A

- **Offline.** Token counts come from the mock (`len(text)//4`); `chatcmpl-mock-...` IDs are mock response IDs. Costs use `gpt-4.1-mini` list prices from `config/settings.py` ($0.40 input, $0.10 cached input, $1.60 output per million; verify current pricing). Re-capture live before recording if you show live token counts; the 74% overhead share will move but stay large, because the system prompt and tool schemas are re-sent on every call.
- **The curriculum's cost demo** promised "one tool call accounts for 80% of the total cost". The real code shows something different and more useful: fixed prompt overhead is 74% of input tokens. Teach the real number.
- **`ImportError: opentelemetry.semconv.ai`**: that is the third-party OpenLLMetry package, not installed and not used. Use `opentelemetry.semconv._incubating.attributes.gen_ai_attributes` from `opentelemetry-semantic-conventions` (0.66b0 pinned).
- **`gen_ai.system`** is deprecated in this package in favour of `gen_ai.provider.name` (the package's own docstring says so). The curriculum still lists `gen_ai.system`; T-DOCS should update it.
- **OTLP export**: `opentelemetry-exporter-otlp-proto-http` is already installed (it comes with langfuse 4); `from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter`. The endpoint and auth headers depend on the backend; check each vendor's OTLP docs (verify).
- **"Status UNSET"** is normal for a successful span; only the empty-tool-result case sets ERROR.
