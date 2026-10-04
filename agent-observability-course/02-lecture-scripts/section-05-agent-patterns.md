# Section 5: Agent Observability Patterns

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈48 min (8 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`; every figure comes from `01-curriculum/numbers-card.md` or from the captured command output quoted in the cue
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15+ (uv.lock 4.16.0) / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating) / openinference-instrumentation-openai 0.1.61+ (uv.lock 0.1.63); check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 5.1 | What an agent trace must answer | SL | 6:00 | ~635 |
| 5.2 | Code-along: tracing the tool loop step by step | SC | 9:00 | ~625 |
| 5.3 | RAG spans: retrieval quality is a production metric | SC | 7:00 | ~520 |
| 5.4 | Streaming: time to first token and tokens per second | SC | 7:00 | ~595 |
| 5.5 | Logs vs traces vs metrics for agents | SL | 6:00 | ~635 |
| 5.6 | Break it: the loop you can only see in a trace | DM | 6:00 | ~565 |
| 5.7 | Lab 3: Trace a multi-step ticket escalation | LAB | 4:00 (1:30 video) | ~210 |
| 5.8 | Quiz: Agent patterns | QZ | 3:00 (1:00 video) | ~105 |

**Two instrumentation paths (as in Section 4):** Atlas itself, `app/agent.py`, uses the vendor-neutral path from Section 3: `step n` spans, `ga.*` setters and OpenTelemetry span events (`ga.add_event`). Section 12 relies on that path. The code-alongs here walk the Langfuse-native layer in `app/langfuse_native.py` (`make langfuse-native`, or `python -m app.langfuse_native "<question>" --scenario <name>`), the second layer for Langfuse-first teams, and point to the matching lines in `app/agent.py` each time.

**API guardrails for this section (do not deviate on screen):** step observations use `get_client().start_as_current_observation(name="step n", as_type="chain")`; events use `get_client().create_event(name=..., level=..., metadata=...)` with the names `step_limit_reached`, `tool_retries_exhausted` and `escalation`; the escalation call is the same `call_model` generation with the escalation model. Atlas's own path records the same events as OpenTelemetry span events on the agent span, plus `request_deadline_exceeded`. Streaming uses `stream=True` with `stream_options={"include_usage": True}`; `completion_start_time` is a timezone-aware `datetime`. Prometheus labels come only from the small fixed sets in `telemetry/metrics.py` (`tenant`, `model`, `outcome`, `feature`, `kind`, `tool`, `reason`, `decision`, ...). Never a `user_id` or `session_id` label. Every code block is an exact excerpt of the named file; elided lines are shown as `...`. Commands that call `python -m app.langfuse_native` directly set `ATLAS_PROMPT_CACHE=0` so their numbers match the Makefile's baseline.

---

## Lecture 5.1 — What an agent trace must answer

| Field | Value |
|---|---|
| ID | 5.1 |
| Type | SL (slides, with one terminal beat) |
| Target duration | 6:00 (~635 spoken words, about 4:32 of talking at 140 wpm) |
| Learning objectives | 1. List the six questions an agent trace must answer: why that tool, with what, what came back, how many steps, where the tokens went, where the time went. 2. Map each question to a span, attribute or event. 3. Judge a trace as "readable" or not against that list. |
| Prerequisites | Section 4 |
| Files used | Diagram: annotated agent trace (slide 2); `03-code/app/langfuse_native.py` (one run, output only) |

### Script

[AVATAR]
On Monday morning after the weekend from Section one, an engineer opens a trace. She has ninety seconds before the stand-up. [PAUSE] What does she need to read off that screen, without opening a single log file? That list is the design spec for everything in this section. Six questions.

[SLIDE 1: Six questions an agent trace must answer]
1. Why did it call that tool?
2. With what arguments?
3. What came back?
4. How many steps, and did it stop on its own?
5. Where did the tokens go?
6. Where did the time go?

Why did it call that tool. With what. What came back. How many steps, and did it stop by itself or was it stopped. Where did the tokens go. Where did the time go. If a trace answers all six in ninety seconds, it's a good trace. If it answers three, you're going to be reading logs.

[SLIDE 2: The trace we're aiming for]
Diagram: waterfall of a flaky-ticket conversation. `atlas` (agent) at the root. Children in order: `injection_check` (guardrail) → `step 1` (chain) containing `chat` (generation, finish: tool_calls) and `lookup_ticket` (tool, ERROR "ticket_service_timeout") → `step 2` (chain), same shape, ERROR again → `step 3` (chain): `chat` and `lookup_ticket` (ERROR "not_found") → `step 4` (chain): `chat` (finish: stop). Scores: resolved 1, steps 4. A second, smaller panel: `step 1` with `chat` (gpt-4.1-mini), an `escalation` event, then `chat` (gpt-4.1).

Here's the trace we're building towards. Agent at the root. A guardrail first. Then one chain observation per step, and inside each step, whatever happened: a generation, then a tool or a retriever. In this conversation the ticket service timed out twice, then said "not found", and the model gave an honest answer in step four. The small panel shows the other shape: an escalation event, then a generation on the bigger model. Scores at the end.

[SCREEN: Terminal in `03-code/`, venv active. Run the command below.]

[CODE: the same shape, from the real code]
```bash
ATLAS_PROMPT_CACHE=0 python -m app.langfuse_native "Where is my ticket TCK-100231?" --scenario ticket_flaky
```

[DEMO: Output: `atlas [agent]`, `injection_check [guardrail]`, then `step 1 [chain]` to `step 4 [chain]`. Steps 1 and 2 hold `lookup_ticket [tool]  level=ERROR  output={"error": "ticket_service_timeout", "ticket_id": "TCK-100231", "retry": true}`; step 3 `lookup_ticket [tool]  level=ERROR  output={"error": "not_found", "ticket_id": "TCK-100231"}`; step 4 only `chat [generation]`. Generation input tokens: 3,261, 3,329, 3,397, 3,455. Last lines: `scores: injection_flagged=0 (BOOLEAN), resolved=1 (BOOLEAN), steps=4 (NUMERIC)`, `outcome=resolved  steps=4  cost=$0.005620`.]

That diagram isn't a mock-up. Here it is from the repo's Langfuse-native layer, with the flaky-ticket scenario. Four steps, two timeouts, a not-found, an honest answer. Keep this output open; we'll answer the six questions against it.

[SLIDE 3: Q1. Why that tool? → the generation before it]
- The previous generation's output shows the tool call the model chose
- `gen_ai.response.finish_reasons = ["tool_calls"]`
- Read: what did the model see (input, tokens) → what did it decide (output)

Why did it call that tool? Look at the generation immediately before it, in the same step. Its output is the model's decision, the tool it chose, and its finish reason says `tool_calls`. Its input and token count tell you what it saw when it decided. Cause and effect, one click apart.

[SLIDE 4: Q2 and Q3. With what, and what came back → the tool observation]
- Input: the arguments, exactly as the model produced them
- Output: the result, clipped and masked
- Level and status: DEFAULT, or ERROR with the message the model then saw
- `gen_ai.tool.call.id` ties it to the call in the generation's output

With what, and what came back: the tool observation. Input is the arguments as the model produced them, which is how you catch a model passing a ticket ID with a typo. Output is the result, clipped and masked. The level tells you it failed, and the output shows exactly what the model read next.

[SLIDE 5: Q4. How many steps, and who stopped it? → chains, events, scores]
- One `chain` per step: count them
- An event when the loop intervened: `step_limit_reached`, `tool_retries_exhausted`, `escalation`
- Scores on the trace: `steps`, `resolved`, `step_limit_hit`
- Finish reason `stop` on the last generation means the model chose to end

How many steps? Count the chain observations. Did it stop on its own? The last generation's finish reason says `stop` if the model chose to end. If the loop intervened, there's an event: step limit reached, tool retries exhausted, or an escalation. And the same facts land as scores, so you can filter a week of traces by "hit the step limit."

[SLIDE 6: Q5. Where did the tokens go? → usage per generation, per step]
- Each generation: input, output, cached input
- Input tokens per step should be roughly flat; a rising line is context growth
- Cached input should be high from step 2 once caching is on (Section 6.4)
- Trace total = sum of generations; compare to the day's $0.0141 per conversation

Where did the tokens go? Every generation has usage. Read the input tokens down the steps: here, three thousand two hundred and sixty-one, then about seventy more each step. That slow climb is context growth, the Friday-night signature. Cached input should be high from step two once caching is on. And compare the trace's total to the day's average of a cent and a half per conversation.

[SLIDE 7: Q6. Where did the time go? → the waterfall]
- Generations dominate; tools should be milliseconds
- Gaps between spans are your own code
- Time to first token per generation (5.4)
- One slow tool call at the wrong moment moves p95 (Section 7)

Where did the time go? The waterfall. Generations should dominate. Tools should be milliseconds; a tool taking two seconds is a finding. Gaps between spans are your own code. And in Lecture 5.4, time to first token per generation.

[SLIDE 8: What breaks readability]
- Flat traces: agent and twenty children, no steps → can't tell which tool followed which call
- Missing arguments or results → can't answer Q2 or Q3
- Silent stopping → the loop ended, nothing says why
- Escalation without a marker → cost jumped, no reason in the trace
- Unclipped tool results the size of a web page → nobody scrolls

What breaks readability? Flat traces, where the agent has twenty children and no steps. Missing arguments or results. Silent stopping. Escalation with no marker. And results the size of a web page, which nobody reads.

[SLIDE 9: The pattern, in one slide]
- Agent → guardrail → step (chain) → { generation | retriever | tool } per step
- Events for interventions: `step_limit_reached`, `tool_retries_exhausted`, `escalation`
- Scores for outcomes: `resolved`, `steps`, `step_limit_hit`
- Everything clipped, masked and typed

[AVATAR]
Agent, guardrail, one chain per step, the work inside each step, events for interventions, scores for outcomes. That's the pattern. Next lecture, you'll read the loop that produces it.

[SLIDE 10: Recap]
- Six questions define a readable trace
- One chain per step, typed children
- Events for interventions, scores for outcomes

**Recap:** An agent trace must answer why a tool was called, with what, what came back, how many steps and who stopped it, where the tokens went and where the time went, and the pattern that answers all six is a chain observation per step with typed children, events for interventions and scores for outcomes.

**Transition:** Next, the code-along: step observations, tool errors as levels, the step limit and tool-retry limit as events, and escalation as a child generation.

### Speaker notes: common student mistakes / Q&A

- "Isn't one chain per step too many observations?" A ten-step trace has ten more spans. Readability is worth it; storage is clipped elsewhere.
- "Should the step span carry usage?" No; usage belongs to the generation. The step is structure.
- Students ask about "reasoning" or "thought" spans. If the model emits reasoning text, it's the generation's output; reasoning tokens are usage on the generation. No separate span.
- The `ticket_flaky` scenario makes `lookup_ticket` time out on two of every three calls; TCK-100231 doesn't exist, so the third call says "not found". Atlas's own path produces the same shape with `step n` spans (Ops Console → Traces).

---

## Lecture 5.2 — Code-along: tracing the tool loop step by step

| Field | Value |
|---|---|
| ID | 5.2 |
| Type | SC (code-along through `_loop`) |
| Target duration | 9:00 (~625 spoken words, about 4:28 of talking at 140 wpm, plus runs and trace dwell) |
| Learning objectives | 1. Wrap each loop iteration in a `chain` observation named `step n`. 2. Record tool results as levels rather than exceptions. 3. Emit `step_limit_reached`, `tool_retries_exhausted` and `escalation` events, and make escalation a generation on the bigger model; find the same three in Atlas's own `_loop`. |
| Prerequisites | 5.1 |
| Files used | `03-code/app/langfuse_native.py` (`_loop`), `03-code/app/agent.py` (`_loop`) |

**Recording note:** the three runs below were captured on 2026-10-02. The default step limit is 6 (`ATLAS_MAX_STEPS`); `ATLAS_MAX_TOOL_RETRIES` defaults to 0, which means unlimited.

### Script

[AVATAR]
Atlas's loop is about forty lines. Inside them sit every answer to the six questions: where a step starts and ends, what happens when a tool fails, and the three moments the loop intervenes. Let's read it top to bottom, then run it three ways.

[SCREEN: VS Code, `app/langfuse_native.py`, `_loop`.]

[CODE: step 1, one chain per step (excerpt of `_loop` in `app/langfuse_native.py`)]
```python
def _loop(run: _Run, messages: list[dict[str, Any]], *, model: str) -> None:
    """Lecture 5.2: one ``chain`` per step, events where the loop intervened."""
    s, r, lf = run.settings, run.result, get_client()
    failures: dict[str, int] = {}
    last_step = s.max_steps if s.max_steps > 0 else 50  # this demo layer caps unlimited at 50
    for step in range(1, last_step + 1):
        r.steps = step
        with lf.start_as_current_observation(name=f"step {step}", as_type="chain") as chain:
            chain.update(metadata={"context_messages": len(messages)})
            assistant = call_model(run, messages, model=model)
            calls = assistant.get("tool_calls") or []
```

Step one. The loop runs up to the step limit, six by default. Each iteration opens `start_as_current_observation`, type `chain`, named `step` and the number. It's a context manager, so everything called inside, the generation and the tools, nests under it. The metadata records how many messages the model is about to read, which is the context growing in plain sight.

[CODE: step 2, escalation as a child generation (excerpt)]
```python
            if not calls:
                content = assistant.get("content") or ""
                if content.startswith(ESCALATE_MARKER):
                    lf.create_event(
                        name="escalation",
                        level="DEFAULT",
                        metadata={"to_model": s.escalation_model},
                    )
                    assistant = call_model(run, messages, model=s.escalation_model)
                    content = (assistant.get("content") or "").replace(ESCALATE_MARKER, "")
                    r.outcome = "escalated"
                r.answer = content.strip()
                return
```

What if the model asked for no tool? Then it answered, and usually that's the end. But for sensitive requests, a grievance or a legal question, the small model marks its answer for escalation. Then the loop emits an `escalation` event naming the bigger model, and calls the same generation function with `gpt-4.1`. Because `call_model` is a generation observation, the trace shows the event and then a second generation, on the bigger model, inside the same step. Cost jumps five times, and the trace says why. Escalation is for sensitive intents only; a failing tool never triggers it.

[CODE: step 3, tool failures and the retry limit (excerpt)]
```python
            messages.append(assistant)
            for tc in calls:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"] or "{}")
                content, ok = TOOLS[name](run, args)
                if s.context_diet:
                    content = truncate_tool_result(content, s.tool_result_token_budget)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": content})
                if not ok:
                    failures[name] = failures.get(name, 0) + 1
                    if 0 < s.max_tool_retries < failures[name]:
                        lf.create_event(
                            name="tool_retries_exhausted",
                            level="WARNING",
                            metadata={"tool": name, "failures": failures[name]},
                        )
                        r.outcome, r.answer = "tool_error", TOOL_ERROR_ANSWER.format(tool=name)
                        return
```

And when a tool fails? Remember from 4.2: a failed tool doesn't raise; its observation goes to ERROR level, and the error comes back as a message for the model to read. The loop counts failures per tool. If a retry limit is set and one tool has failed more times than that, stop: emit `tool_retries_exhausted` at warning level, with the tool and the count, and give the employee an honest answer. By default that limit is zero, meaning unlimited. Lecture 5.6 switches it on.

[CODE: step 4, the step limit (excerpt)]
```python
    lf.create_event(name="step_limit_reached", level="WARNING", metadata={"max_steps": last_step})
    lf.score_current_trace(name="step_limit_hit", value=1, data_type="BOOLEAN")
    r.outcome, r.answer = "step_limit", STEP_LIMIT_ANSWER
```

And if the loop runs out of steps, three things. An event, `step_limit_reached`, at warning level, with the limit. A boolean score on the trace. And an honest answer: open a ticket, or reply and Atlas will create one. That's the difference between the Friday run and the guarded run from Lecture 1.1, in three lines.

[SCREEN: VS Code, `app/agent.py`, `_loop`: the `with self.tracer.start_as_current_span(f"step {step}") as st:` line, the `ga.add_event(root, "escalation", ...)` call, `ga.add_event(root, "tool_retries_exhausted", ...)`, and `ga.add_event(root, "step_limit_reached", max_steps=last_step)`.]

Now flip to Atlas's own loop. Same shape, vendor-neutral. Each step is an OpenTelemetry span named `step` and the number. The same three interventions are span events on the agent span, through `ga.add_event`, and the agent span's level goes to warning. One more check lives only here: a request deadline, ten minutes by default, which you'll meet in 5.6. Whichever path you read, the trace answers the same questions.

[SCREEN: Terminal.]

[CODE: three runs]
```bash
make langfuse-native MSG="I have a grievance about my manager, what are my options?"
ATLAS_PROMPT_CACHE=0 python -m app.langfuse_native "Where is my ticket TCK-100231?" --scenario ticket_flaky
ATLAS_PROMPT_CACHE=0 python -m app.langfuse_native "Where is my ticket TCK-100231?" --scenario loop
```

[DEMO: Run 1: `step 1 [chain]` holding `chat [generation]  model=gpt-4.1-mini  usage={"input": 3267, "output": 18, ...}`, `escalation [event]`, `chat [generation]  model=gpt-4.1  usage={"input": 3267, "output": 110, ...}`; `outcome=escalated  steps=1  cost=$0.008750`. Run 2: four steps as in 5.1, `outcome=resolved  steps=4  cost=$0.005620`. Run 3: `step 1 [chain]` to `step 6 [chain]`, every `lookup_ticket [tool]  level=ERROR  output={"error": "ticket_service_unavailable", "ticket_id": "TCK-100231", "retry": true}`, then `step_limit_reached [event]  level=WARNING`; `scores: injection_flagged=0 (BOOLEAN), step_limit_hit=1 (BOOLEAN), resolved=0 (BOOLEAN), steps=6 (NUMERIC)`; `outcome=step_limit  steps=6  cost=$0.008586`.]

Three runs. Read the generation lines first: in the loop run the input tokens climb from three thousand two hundred and sixty-one to three thousand six hundred and six over six steps, the context growing in plain sight. Now the shapes. A grievance: one step, an escalation event, then a generation on gpt-4.1. Almost nine tenths of a cent, most of it the big model, and the trace says why. The flaky ticket: four steps, two red tool calls, then the honest not-found answer. And the loop scenario: six steps, every tool call red, then a yellow `step_limit_reached` event. Step limit hit, one. Resolved, zero. Can you answer all six questions from these screens? [PAUSE] You can, for every one of them.

[SLIDE 1: What each line bought you]
| Question | Answered by |
|---|---|
| Why that tool | the generation before it, inside the same step |
| With what / what came back | tool observation input and output; ERROR level on failure |
| How many steps, who stopped it | count of `step n`; `step_limit_reached` or `tool_retries_exhausted` event; `steps` and `step_limit_hit` scores |
| Where the tokens went | usage per generation, per step; model per generation |
| Where the time went | the waterfall per step |
| Why cost jumped | `escalation` event and the model name on the next generation |

[AVATAR]
A chain per step, errors as levels, three events, one score. That's the whole pattern, and Atlas's own loop has the same shape with span events. Everything in Sections six, seven and eleven reads traces shaped like this.

[SLIDE 2: Recap]
- A chain per step nests the work
- Failed tools are levels, not exceptions
- Events mark escalation and both limits

**Recap:** A `chain` observation per step, tool failures recorded as ERROR-level observations, `escalation`, `tool_retries_exhausted` and `step_limit_reached` events, a `step_limit_hit` score and the model name on every generation make the loop readable step by step, on both instrumentation paths.

**Transition:** Next, the retriever: why "how good was the search" is a production metric, and how to record it.

### Speaker notes: common student mistakes / Q&A

- Mistake: creating the step observation but calling the model outside the `with` block. The generation lands under the agent, not the step. Check indentation.
- Mistake: `create_event` after the step's `with` block closed. The event still lands in the trace under the agent, which is where `step_limit_reached` belongs anyway; tool events read better inside the step.
- "Why not raise on tool error and let the span record the exception?" Because the model needs the error as a message to decide what to do, and an exception ends the loop. Record, return, let the loop decide.
- `ATLAS_MAX_STEPS=0` means unlimited in Atlas (only the 600 s request deadline stops it); this teaching layer caps it at 50 steps so a demo can't run away.

---

## Lecture 5.3 — RAG spans: retrieval quality is a production metric

| Field | Value |
|---|---|
| ID | 5.3 |
| Type | SC (code-along) |
| Target duration | 7:00 (~520 spoken words, about 3:43 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Record query, top-k, document IDs, scores and an empty flag on the retriever observation. 2. Flag empty retrievals with a warning level, and know why a non-empty result can still be wrong. 3. Read the empty-retrieval rate and the grounded rate for a replayed day. |
| Prerequisites | 5.2 |
| Files used | `03-code/app/knowledge.py` (`search`, `min_score`), `03-code/app/tools.py` (`search_knowledge_base`), `03-code/telemetry/genai_attrs.py` (`set_retrieval`), `03-code/app/langfuse_native.py`, `03-code/console/pages/4_Quality.py`, `03-code/console/pages/7_Retrieval.py`. Data: `OFFLINE=1 make replay`. |

### Script

[AVATAR]
Here's a question nobody asks until it's a problem: how often does Atlas answer a policy question with nothing relevant in front of it? A live model with an empty search result doesn't always say "I don't know." Sometimes it improvises. Confidently. The only place that shows up is the retriever span, if you record the right things on it.

[SLIDE 1: What to record on a retriever observation]
- Input: the query text and `top_k`
- Output: document IDs and scores (not the article text; it's already in the next generation's input)
- Hits and an empty flag
- Level: WARNING when empty
- Later: a grounded score from the judge (Section 8)

Five things. The query and top-k as input. Document IDs and scores as output, not the article text, which already appears in the next model call's input. The hit count and an empty flag. A warning level when the result is empty. And later, a grounded score from the judge in Section eight.

[SCREEN: VS Code, `app/knowledge.py`, `search`; then `src/northwind/config.py`, `kb_min_score: float = 0.5`.]

[CODE: excerpt of `KnowledgeBase.search` in `app/knowledge.py`]
```python
    def search(self, query: str, top_k: int = 4, *, min_score: float = 0.5) -> list[SearchHit]:
        q = tokenize(query)
        if not q or not self.articles:
            return []
        scored = [(self.score(q, i), i) for i in range(len(self.articles))]
        scored.sort(key=lambda x: (-x[0], self.articles[x[1]].doc_id))
        hits = []
        for s, i in scored[: max(0, top_k)]:
            if s < min_score:
                break
            a = self.articles[i]
            hits.append(SearchHit(a.doc_id, a.title, s, self._snippet(a, q)))
        return hits
```

First, the retriever itself. A small BM25 scorer over the fourteen articles. It scores every article, keeps the top four, and drops anything under a relevance floor, `KB_MIN_SCORE`, half a point by default. Why a floor? BM25 always returns something. Without a floor, "empty" is never true, and you never see the problem.

[CODE: `set_retrieval` from `telemetry/genai_attrs.py` (Atlas's path)]
```python
def set_retrieval(
    span: Span,
    *,
    query: str,
    top_k: int,
    hits: int,
    scores: list[float] | None = None,
    doc_ids: list[str] | None = None,
    redact: bool = True,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, OP_RETRIEVAL)
    span.set_attribute(LF_OBS_TYPE, "retriever")
    span.set_attribute(LF_OBS_INPUT, _safe(query, redact))
    span.set_attribute(ATLAS_RETRIEVAL_TOP_K, int(top_k))
    span.set_attribute(ATLAS_RETRIEVAL_HITS, int(hits))
    span.set_attribute(ATLAS_RETRIEVAL_EMPTY, hits == 0)
    if scores:
        span.set_attribute(ATLAS_RETRIEVAL_SCORES, [round(float(s), 4) for s in scores])
    if doc_ids:
        span.set_attribute(LF_OBS_OUTPUT, json.dumps(doc_ids))
```

On Atlas's own path, the search tool's span becomes a retriever with `set_retrieval`. Operation `retrieval`, Langfuse type `retriever`, the masked query as input. Then our own attributes: top-k, hit count, an empty flag, and the scores. The document IDs go out as the output. The Langfuse-native layer from 4.2 records the same facts, and sets a warning level when the list is empty.

[CODE: ask something the knowledge base doesn't cover]
```bash
make langfuse-native MSG="Do we have yoga classes?"
```

[DEMO: `search_knowledge_base [retriever]  level=WARNING  output=[]` inside `step 1`; then `answer: I couldn't find a policy article for that. Next step: I can open a ticket with the service desk so a person can help.`; `cost=$0.002756`.]

Ask about yoga classes. The retriever is yellow: warning level, empty output. And the answer? Our mock is honest: it couldn't find a policy, and offers a ticket. A live model might not be. Either way, the empty flag on this span is what lets you count how often it happens.

[CODE: now something that isn't empty, but isn't right]
```bash
make langfuse-native MSG="Is there a yoga class on Fridays?"
```

[DEMO: `search_knowledge_base [retriever]  output=[{"doc": "KB-012", "score": 2.414}, {"doc": "KB-005", "score": 2.34}, {"doc": "KB-002", ...`; `cost=$0.004479`.]

Now add one word: "on Fridays". Three documents come back above the floor: the ticket article, expenses, password resets. They matched the word "Friday", not the question. Not empty, not relevant, and the model writes an answer from them. Can a retriever span catch that? [PAUSE] Only partly: the scores look fine. That's why the second signal, the judge's grounded score, exists. It asks whether the answer is supported by what was retrieved.

[SCREEN: Terminal: `OFFLINE=1 make replay` (if not already done). Ops Console → Quality page: tiles showing grounded rate 98.6 % and empty retrievals 2.6 %. Then the Retrieval page: mean `atlas.retrieval.top_k`, result tokens and empty share per hour, by tenant.]

[SLIDE 2: Two rates you'll track from here]
- Empty-retrieval rate: retriever spans with `atlas.retrieval.empty = true` ÷ all retriever spans
- Grounded rate: judged traces with grounded ≥ 0.7 ÷ judged traces
- Baseline day: empty 2.6 % (165 of 6,396 retriever calls); grounded rate 98.6 %
- A change to top-k or the floor moves both; Section 11 shows what happens when someone tunes it without looking here

On the replayed day the console's quality page has both rates. Empty retrievals: two point six percent, a hundred and sixty-five of six thousand three hundred and ninety-six searches. Grounded rate, from the judge's sample: ninety-eight point six percent. Write both in your build log. The retrieval page breaks top-k, result size and empty share down by tenant and hour. In Section eleven, someone changes top-k, and these lines move.

[SLIDE 3: When top-k and the floor change]
- Record `top_k` on every retrieval so a change is visible in traces
- Higher top-k: more tokens per step (cost), fewer empties; lower: the reverse
- Section 6.5 tunes top-k for cost; Incident 1 shows what happens when someone tunes it without looking here

[AVATAR]
Record the query, the documents, the scores, the emptiness. Warn on empty. Let the judge decide grounded. Two rates, on a dashboard, from day one. Retrieval quality isn't an offline benchmark; it's a production metric, and now you have it.

[SLIDE 4: Recap]
- Record query, top-k, IDs, scores, empty flag
- Empty is a warning; irrelevant needs the judge
- Two rates: 2.6 % empty, 98.6 % grounded

**Recap:** The retriever span records query, top-k, document IDs, scores, hit count and an empty flag, with a warning level when empty; empty-retrieval rate comes from those spans and grounded rate from the judge, and both are production metrics you can read for a day.

**Transition:** Next, streaming: measuring time to first token and tokens per second on every generation.

### Speaker notes: common student mistakes / Q&A

- Mistake: putting full article text in the retriever output. It doubles storage; the text is already in the next generation's input.
- `KB_MIN_SCORE=0.5` is tuned for this course's BM25-lite over fourteen articles; scores are BM25 points, not 0-to-1 similarities. Say so if asked.
- "Where's the grounded score in my trace?" The replay simulates the judge on a 30 % sample; Section 8 builds the real one (`make judge`). The agent doesn't set it.
- The two rates are `numbers-card.md` §4; they come from the replay, not from the two single questions above.

---

## Lecture 5.4 — Streaming: time to first token and tokens per second

| Field | Value |
|---|---|
| ID | 5.4 |
| Type | SC (code-along) |
| Target duration | 7:00 (~595 spoken words, about 4:15 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Stream a chat completion with usage included and capture the first token's time. 2. Record it as `gen_ai.response.time_to_first_chunk` and `atlas.ttft_ms` (Atlas's path) or `completion_start_time` (Langfuse-native). 3. Compute TTFT and TPOT and know which one users feel. |
| Prerequisites | 5.2 |
| Files used | `03-code/app/agent.py` (`OpenAIChatClient.chat`, `collect_stream`, `_finish`), `03-code/telemetry/genai_attrs.py` (`set_llm_usage`), `03-code/src/northwind/latency.py` (`LatencySample`, `RequestTiming`), `03-code/console/pages/3_Latency.py` |

**Recording note:** offline TTFT values are the mock's simulated timings (`ATLAS_STREAM=1` is the default). The per-generation values below are from the VPN request through Atlas's console exporter on 2026-10-02; the day-level values are `numbers-card.md` §3.

### Script

[AVATAR]
Two answers, both three seconds long. One felt instant; one felt broken. The difference: the first showed a word after half a second, the second showed nothing for three seconds and then everything at once. Total latency can't tell them apart. Time to first token can. So how do you measure it?

[SLIDE 1: Three latency numbers per generation]
- TTFT: time to first token. What the user feels as "did it hear me?"
- TPOT: time per output token, after the first. Reading speed.
- Total: TTFT + (output_tokens − 1) × TPOT. What p95 dashboards usually show.
- Same total, different TTFT = completely different experience

Three numbers per generation. Time to first token, which is what the user feels as responsiveness. Time per output token after the first, which is reading speed. And total, which is what most dashboards show and which hides the difference.

[SCREEN: VS Code, `app/agent.py`, `OpenAIChatClient.chat`.]

[CODE: excerpt of `OpenAIChatClient.chat` in `app/agent.py`]
```python
    def chat(self, **kwargs: Any) -> Any:
        kwargs.pop("scenario", None)
        if kwargs.get("stream"):
            kwargs.setdefault("stream_options", {"include_usage": True})
        return self._client.chat.completions.create(**kwargs)
```

First, ask for the right stream. When Atlas streams, it adds `include_usage`. Without that option the final chunk has no token counts, and you can't price the call: cost reads zero and every dashboard lies low.

[CODE: excerpt of `collect_stream` in `app/agent.py`]
```python
    for ch in chunks:
        last = ch
        if getattr(ch, "usage", None) is not None:
            usage = ch.usage
        if not ch.choices:
            continue
        choice = ch.choices[0]
        delta = choice.delta
        if choice.finish_reason:
            finish = choice.finish_reason
        if delta is None:
            continue
        if delta.content:
            if ttft is None:
                ttft = clock() - started
            content_parts.append(delta.content)
        for tc in delta.tool_calls or []:
            if ttft is None:
                ttft = clock() - started
```

Then consume it. For every chunk: keep the usage when it arrives on the last one, note the finish reason, and on the first chunk that carries content or a tool-call fragment, record the time since the call started. Not the first chunk of any kind: the first one often carries only a role and no text. Collect the text and the tool-call pieces, and at the end you have a normal message, the usage and the time to first token.

[CODE: excerpt of `set_llm_usage` in `telemetry/genai_attrs.py`]
```python
    if ttft_s is not None:
        span.set_attribute(g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK, float(ttft_s))
        span.set_attribute(ATLAS_TTFT_MS, float(ttft_s) * 1000.0)
```

Where does it land? On Atlas's path, two attributes on the generation span: the standard `gen_ai.response.time_to_first_chunk`, in seconds, incubating name, may change; and our own `atlas.ttft_ms`. On the Langfuse-native path, it's the `completion_start_time` argument you saw in 4.2, which Langfuse shows as time to first token on the generation.

[SCREEN: Terminal 1: `OTEL_EXPORTER=console make run`. Terminal 2: the VPN `curl` from 2.3.]

[DEMO: Console: first `chat gpt-4.1-mini` span with `"gen_ai.response.time_to_first_chunk": 0.3534`, `"atlas.ttft_ms": 353.4`, `"atlas.latency_ms": 692.9`; second with `0.5651`, `565.1`, `2700.9` and `"gen_ai.usage.output_tokens": 290`. The `invoke_agent atlas` span: `"atlas.ttft_ms": 1258.0`, `"atlas.latency_ms": 3393.8`. The curl response shows `"ttft_ms": 1258.0`.]

Send the VPN question and read the console. First model call: first token at three hundred and fifty-three milliseconds. Second call: five hundred and sixty-five, then about two point seven seconds to finish two hundred and ninety tokens. That's roughly seven milliseconds per token after the first, about a hundred and thirty-five tokens a second. Now the agent span: time to first token, one thousand two hundred and fifty-eight milliseconds. Why so much bigger? [PAUSE] Because the user sees nothing until the final answer starts, and that's after the whole first step.

[CODE: excerpt of `RequestTiming.ttft_ms` in `src/northwind/latency.py`]
```python
    @property
    def ttft_ms(self) -> float | None:
        """Time until the first token of the *final* answer (what the user perceives)."""
        if not self.steps:
            return None
        last = self.steps[-1]
        if last.ttft_ms is None:
            return None
        return sum(s.total_ms for s in self.steps[:-1]) + last.ttft_ms
```

The latency module writes that rule down: the time to the first token of the final answer is every earlier step's full duration plus the last step's first token. Six hundred and ninety-three plus five hundred and sixty-five. Its `LatencySample` also computes time per output token and tokens per second.

[SLIDE 2: Where each number lives]
| Number | Where | Used by |
|---|---|---|
| `gen_ai.response.time_to_first_chunk`, `atlas.ttft_ms` | generation span (Atlas's path) | any OTel backend, the Ops Console |
| `completion_start_time` | Langfuse generation (Langfuse-native path) | Langfuse's time-to-first-token view |
| `atlas.ttft_ms` on the agent span | final-answer TTFT | Section 7 budgets |
| `atlas_ttft_seconds{model}` | Prometheus histogram, per generation | Grafana p95 (Section 9) |

The same measurement lands in several places for several audiences. The standard attribute and our own on the generation. Langfuse's field on the native path. The final-answer number on the agent span. And a Prometheus histogram for Grafana in Section nine.

[SCREEN: Ops Console → Latency page, "Generation detail: atlas.ttft_ms p95 and duration p95" chart for the replayed day.]

[SLIDE 3: Reading TTFT across a day]
- Final-answer TTFT: p50 1,427 ms, p95 1,702 ms on the replayed day
- Per-generation TTFT (`atlas_ttft_seconds`): p50 509 ms, p95 652 ms
- TTFT climbs with input tokens: context bloat shows here first
- TPOT is mostly a property of the model; a jump means a provider change or a slow region

Across the replayed day: final-answer time to first token, median one point four seconds, p95 one point seven. Per generation, median about half a second. Two patterns to remember. TTFT climbs with input size, so context bloat shows up here before it shows up in your bill. And TPOT is mostly a property of the model; if it jumps, the provider changed something. Section seven sets budgets against these.

[AVATAR]
One option on the request, one timestamp in the stream. Time to first token on every generation, and the number users actually feel on every request.

[SLIDE 4: Recap]
- Stream with `include_usage`, or cost is zero
- Record the first content chunk's time
- Users feel final-answer TTFT, not total

**Recap:** Stream with `include_usage`, record the first content chunk's time as `gen_ai.response.time_to_first_chunk` and `atlas.ttft_ms` (or `completion_start_time` on the Langfuse-native path), and remember that the user feels the final answer's time to first token, which includes every earlier step.

**Transition:** Next, a slides lecture on the three signals: when an agent should log, when it should trace, and when it should count.

### Speaker notes: common student mistakes / Q&A

- Mistake: omitting `stream_options={"include_usage": True}`. Usage is `None`; cost is zero; dashboards lie low.
- Mistake: measuring TTFT to the first chunk of any kind. The first chunk may carry only a role. Wait for content or a tool-call delta, as `collect_stream` does.
- `completion_start_time` must be timezone-aware; naive datetimes are misread.
- The tokens-per-second figure is arithmetic on the console output: (2,700.9 − 565.1) ms ÷ 289 tokens ≈ 7.4 ms per token.
- On the Responses API, the usage fields are `input_tokens` / `output_tokens`; `usage_numbers` in `app/agent.py` handles both.

---

## Lecture 5.5 — Logs vs traces vs metrics for agents

| Field | Value |
|---|---|
| ID | 5.5 |
| Type | SL (slides, with one terminal beat) |
| Target duration | 6:00 (~635 spoken words, about 4:32 of talking at 140 wpm) |
| Learning objectives | 1. Decide, for a given fact about an agent, whether it belongs in a log, a span or a metric. 2. Correlate structured JSON logs with traces via `trace_id`. 3. Avoid cardinality traps: never a user or session label on a Prometheus metric. |
| Prerequisites | 5.1 to 5.4 |
| Files used | `03-code/telemetry/logging_setup.py`, `03-code/telemetry/metrics.py`; `curl` against a running Atlas |

**Recording note:** the terminal beat needs `make run` and two requests (the VPN and ticket questions from 2.3 and 3.4); the metric lines and the log line below were captured on 2026-10-02. `/metrics` and `/metrics/` both answer 200; the `-L` in `curl -sL` is harmless and can stay.


### Script

[AVATAR]
"Should this be a log or a span?" I get that question in every team I work with, and the answer is a rule you can apply in five seconds. But there's a trap on the metrics side that has taken down more Prometheus servers than any bug. Have you seen one fall over? Agents walk straight into it. The rule first, then the trap.

[SLIDE 1: Three signals, three questions]
| Signal | Answers | Shape | Cost grows with |
|---|---|---|---|
| Trace | what happened in this request, in order | tree of spans | requests × spans |
| Metric | how much, how often, right now | number series over time | label combinations |
| Log | what did the code say at this moment | line of JSON | lines |

Three signals. A trace answers what happened in one request. A metric answers how much and how often, right now, across all requests. A log answers what the code wanted to say at a moment. Their costs grow differently: traces with request volume, metrics with label combinations, logs with lines.

[SLIDE 2: The five-second rule]
- Is it about one request, in sequence? → span or event on the span
- Is it a number you'd graph over time or alert on? → metric
- Is it a message for a human debugging later? → log, with `trace_id`
- Is it both? → span first, and emit the metric alongside

The rule. If it's about one request, in sequence, it's a span or an event on one. If it's a number you'd graph or alert on, it's a metric. If it's a message for a human, it's a log, with the trace ID attached. If it's both, span first, and emit the metric alongside.

[SLIDE 3: Agent examples]
| Fact | Signal |
|---|---|
| The model chose `lookup_ticket` with these arguments | span (tool) |
| Tool error rate for `lookup_ticket`, last 5 minutes | metric: `atlas_tool_calls_total{tool, outcome}` |
| Step limit reached in this conversation | event on the agent span; metric `atlas_requests_total{outcome="step_limit"}` |
| Cost of this generation | span (`atlas.cost_usd`, `cost_details`) |
| Cost per hour by tenant | metric: `atlas_cost_usd_total{tenant, model, feature}` |
| "llm call failed, attempt 1/3" | log, WARNING, with trace_id |
| TTFT of this generation | span (`atlas.ttft_ms`) |
| TTFT p95 today | metric: histogram `atlas_ttft_seconds{model}` |

Examples. The tool the model chose: a span. Tool error rate over five minutes: a metric. Step limit reached: an event on the agent span, and the request counter with outcome step limit, because you'll alert on the rate. Cost of one generation: on the span. Cost per hour by tenant: a metric. A retry warning: a log line, with the trace ID. TTFT of this call: on the span. TTFT p95 today: a histogram.

[SCREEN: Terminal 2, after two requests to a running Atlas.]

[CODE: what Atlas counts]
```bash
curl -sL localhost:8000/metrics | grep -E '^atlas_(requests|tool_calls|tokens|cost_usd)_total'
```

[DEMO: Output:
`atlas_requests_total{feature="policy_question",model="gpt-4.1-mini",outcome="resolved",tenant="ops"} 1.0`
`atlas_requests_total{feature="ticket_lookup",model="gpt-4.1-mini",outcome="resolved",tenant="ops"} 1.0`
`atlas_tokens_total{kind="input",model="gpt-4.1-mini",tenant="ops"} 16530.0`
`atlas_tokens_total{kind="output",model="gpt-4.1-mini",tenant="ops"} 414.0`
`atlas_cost_usd_total{feature="policy_question",model="gpt-4.1-mini",tenant="ops"} 0.0045144`
`atlas_cost_usd_total{feature="ticket_lookup",model="gpt-4.1-mini",tenant="ops"} 0.00276`
`atlas_tool_calls_total{outcome="ok",tool="search_knowledge_base"} 1.0`
`atlas_tool_calls_total{outcome="error",tool="lookup_ticket"} 1.0`]

Here's what that looks like on a running Atlas after two questions. Two requests, by feature and outcome. Sixteen and a half thousand input tokens. Cost per feature, to the same digits as the traces. And tool calls by outcome: one search that worked, one ticket lookup that didn't. What's missing from every label? No user, no session, no trace ID.

[SLIDE 4: Logs that are worth having]
```json
{"ts": "2026-10-02T00:56:41.070889+00:00", "level": "WARNING", "logger": "atlas.agent", "service": "atlas",
 "message": "llm call failed (APITimeoutError) attempt 1/3",
 "trace_id": "a5fedb4b9da10fcd6c0b5fd88e63df97", "span_id": "52b456398abbab7c"}
```
- `telemetry/logging_setup.py`: a JSON formatter that reads the current span context and masks PII in the message
- Paste the `trace_id` into Langfuse or the console's Traces page: the whole request appears
- No message bodies, no PII in logs; that's what masked spans are for

A log worth having looks like this one, from Atlas's terminal during a retry-storm request. JSON, one line, a level, a message, and the trace and span IDs, read from the current span by the formatter. Paste that trace ID into Langfuse or the console's Traces page and the whole request opens. Two rules for logs: no message bodies, and no personal data. Logs are usually kept longer, and read by more people, than traces.

[SLIDE 5: The cardinality trap]
- A metric series exists for every unique combination of label values
- `atlas_tokens_total{tenant, model, kind}`: 5 tenants (incl. `other`) × 5 models × 4 kinds = at most 100 series. Fine.
- Add `user_id` (about 4,800 employees) → up to 480,000 series. Memory, query time and dashboards all suffer.
- Add `session_id` → unbounded. This is how a metrics server dies.
- Rule: labels only for dimensions with a small, fixed set of values. Users and sessions are trace dimensions.

Now the trap. A Prometheus metric is one series per unique combination of label values. Tokens by tenant, model and kind: five times five times four, at most a hundred series. Fine. Add a user ID label, with about four thousand eight hundred employees: up to four hundred and eighty thousand series. Add a session ID: unbounded, and your metrics server falls over at three in the morning. Labels are for dimensions with a small, fixed set of values. Users and sessions belong in traces, where they already are. Atlas even maps unknown tenants to `other`, so a typo in a header can't create a new series.

[SLIDE 6: What `telemetry/metrics.py` exposes (selection)]
```text
atlas_requests_total{tenant, model, outcome, feature}
atlas_tokens_total{tenant, model, kind}            kind = input | output | cached | reasoning
atlas_cost_usd_total{tenant, model, feature}
atlas_tool_calls_total{tool, outcome}              outcome = ok | error
atlas_llm_retries_total{model, reason}
atlas_budget_decisions_total{tenant, decision}
atlas_guardrail_events_total{tenant, kind}
atlas_ttft_seconds{model}                          histogram, per generation
atlas_request_latency_seconds{tenant, feature}     histogram, end to end
atlas_agent_steps{tenant}                          histogram
```

Here's a selection of what Atlas exposes, and every label set is small and fixed. A unit test checks the label names against an allowlist, so nobody adds a user ID by accident. Section nine builds the dashboard and alerts on exactly these.

[AVATAR]
Span for the request, metric for the number, log for the human, trace ID on everything. And never, ever, a user ID on a metric label.

[SLIDE 7: Recap]
- Span for the request, metric for the number
- Log for the human, with `trace_id`
- Never a user or session label

**Recap:** Facts about one request go on spans, numbers you graph or alert on go in metrics with small fixed label sets, human notes go in JSON logs carrying `trace_id`, and users and sessions are trace dimensions, never Prometheus labels.

**Transition:** Next, a break-it demo: the Friday loop, seen from inside the trace this time, and the setting that stops it.

### Speaker notes: common student mistakes / Q&A

- "Can I derive metrics from spans instead of emitting both?" Yes, via the collector's span-metrics connector (Section 13) or Langfuse dashboards (9.4). Atlas emits both for simplicity and for the offline path.
- "Why not `logger.info` the whole prompt?" Size, PII and retention. The newest message is on the generation, masked.
- Students ask about OpenTelemetry's logs and metrics APIs. Both exist; we use the Prometheus client and JSON logging because they're the common enterprise default. Section 12.4 mentions the OTel versions.
- The full metric list, including in-flight, queue-wait, shed, fallback, budget-spent, feedback and exporter-failure metrics, is in `telemetry/metrics.py`; Sections 6, 7 and 9 introduce them.

---

## Lecture 5.6 — Break it: the loop you can only see in a trace

| Field | Value |
|---|---|
| ID | 5.6 |
| Type | DM (live demo, before/after) |
| Target duration | 6:00 (~565 spoken words, about 4:02 of talking at 140 wpm, plus trace dwell) |
| Learning objectives | 1. Run the `loop` scenario with the guards off and read the runaway trace: identical tool errors, climbing input tokens, a deadline stop. 2. Explain why no HTTP status, log line or request count would have shown it. 3. Apply the two guards, the step limit and the tool-retry limit, and read the after traces. |
| Prerequisites | 5.2, 1.1 |
| Files used | `03-code/simulator/loop_demo.py` (`make loop-demo`), `03-code/simulator/scenarios.py` (`loop`), `03-code/app/agent.py` (`_loop`), `03-code/tests/integration/test_spans.py` (`test_loop_scenario_stops_at_step_limit`, `test_loop_scenario_stops_early`) |

**Recording note:** the three runs reproduce `numbers-card.md` §6 exactly (checked 2026-10-02). Use one store for all three, `STORE=.atlas/loop.sqlite`, and open each run's trace on the Ops Console Traces page by the `trace_id` the run prints (start `make console STORE=.atlas/loop.sqlite` after the first run; on an empty store the console would replay a whole day into it first). With Langfuse keys loaded, the same traces also land in Langfuse. Tint before red, after green. Lecture 1.1 showed the money; this lecture shows the trace and the code.

### Script

[AVATAR]
In Lecture 1.1 you watched the Friday loop from the cost meter. Now you'll watch it from inside the trace, because that's where an on-call engineer would actually find it. Then two settings, and the trace again.

[CODE: guards off]
```bash
ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 make loop-demo STORE=.atlas/loop.sqlite
```

[DEMO: The step lines scroll (`step    1  input   3,261 tok ...`, `step    2  input   3,330 tok ...`, `step    3  input   3,399 tok ...`, ... `step  500  input  37,692 tok  step $0.0151  total $4.1241`), then `outcome=timeout  steps=549  model_calls=549  tool_calls=549  input_tokens=12,169,683  cached_tokens=0  cost=$4.8995  latency=600.8s  trace_id=...`.]

Guards off: no step limit, no limit on tool failures. One question through the loop scenario. Without pacing, ten simulated minutes take a few seconds. Five hundred and forty-nine steps. Twelve million input tokens. Four dollars ninety.

[SCREEN: Ops Console → Traces, paste the printed `trace_id`. The table under the waterfall runs for hundreds of rows: `step 1`, `chat gpt-4.1-mini`, `execute_tool lookup_ticket` (status ERROR), `step 2`, ... Scroll for a while.]

Open its trace. The table goes on for screens. Every step the same shape: a model call, then `lookup_ticket`, status ERROR, "ticket service unavailable."

[SCREEN: Click into the first three generations: `gen_ai.usage.input_tokens` 3,261, 3,330, 3,399. Then the last step's generation: 41,073.]

Read the input tokens down the steps. Three thousand two hundred and sixty-one. Three thousand three hundred and thirty. Three thousand three hundred and ninety-nine. Sixty-nine more each step: the tool's arguments, its error, the model's next attempt, all appended, all re-read. By the last step, forty-one thousand. And the model never changes; no escalation, just growth.

[SCREEN: The `invoke_agent atlas` span: event `request_deadline_exceeded` (`deadline_s=600.0`, `steps=549`), `error.type=deadline_exceeded`, level WARNING, output "This request took too long and was stopped. Please try again, or open a ticket in ServiceHub."]

How did it end? The agent span has one event: `request_deadline_exceeded`, after five hundred and forty-nine steps. Atlas's last-resort deadline, ten minutes, like a gateway timeout. Without it, nothing in the loop would ever have stopped.

[SLIDE 1: Where else would this have shown up?]
| Signal | What it showed on Friday |
|---|---|
| HTTP status | 200, with a "took too long" answer after 10 minutes |
| Request count | 1 |
| Error logs | none: a failed tool is data, not an exception |
| Tool error metric | `atlas_tool_calls_total{tool="lookup_ticket", outcome="error"}` +549: a real signal, if anyone had the alert |
| Trace | 549 identical steps, climbing tokens, a deadline stop |

Where else would you have seen this? The HTTP status was 200. Request count, one. Error logs: nothing, because a failed tool is data for the model, not an exception. The tool error counter did climb, and that's the alert you add in Section nine. But the shape of the failure, one conversation retrying itself into the ground, only exists in the trace.

[AVATAR]
Two guards, both one setting. The step limit you saw in 5.2, six by default. And a limit on how often one tool may fail before Atlas stops and says so.

[CODE: the default guard: the step limit]
```bash
make loop-demo STORE=.atlas/loop.sqlite
```

[DEMO: Six step lines, then `outcome=step_limit  steps=6  model_calls=6  tool_calls=6  input_tokens=20,601  cached_tokens=0  cost=$0.0086  latency=4.3s`.]

Defaults back on. Six steps, then the step-limit answer. Less than a cent. Its trace ends with a `step_limit_reached` event. Better, but notice: six times, Atlas asked a service that was down.

[SCREEN: VS Code, `app/agent.py`, `_loop`, the tool-retry guard.]

[CODE: excerpt of `_loop` in `app/agent.py`]
```python
                    if not ok:
                        tool_failures[name] = tool_failures.get(name, 0) + 1
                        # ATLAS_MAX_TOOL_RETRIES: surface the error instead of looping (Lecture 5.6 fix)
                        if s.max_tool_retries > 0 and tool_failures[name] > s.max_tool_retries:
                            result.outcome = "tool_error"
                            result.answer = TOOL_ERROR_ANSWER.format(tool=name)
                            ga.add_event(
                                root,
                                "tool_retries_exhausted",
                                tool=name,
                                failures=tool_failures[name],
                                max_tool_retries=s.max_tool_retries,
                            )
                            root.set_attribute(ga.LF_OBS_LEVEL, "WARNING")
                            root.set_attribute("error.type", "tool_retries_exhausted")
                            messages.append({"role": "assistant", "content": result.answer})
                            return
```

The second guard. Count failures per tool. Once one tool has failed more times than `ATLAS_MAX_TOOL_RETRIES`, stop: outcome `tool_error`, an event naming the tool and the count, the agent span at warning level, and an answer that tells the employee which system is down. The setting defaults to zero, which means unlimited, so you switch it on explicitly.

[CODE: the fix: at most two retries per tool]
```bash
ATLAS_MAX_TOOL_RETRIES=2 make loop-demo STORE=.atlas/loop.sqlite
```

[DEMO: Three step lines, then `outcome=tool_error  steps=3  model_calls=3  tool_calls=3  input_tokens=9,990  cached_tokens=0  cost=$0.0042  latency=2.0s` and `answer: The lookup_ticket service is not responding right now, so I couldn't finish this. I've stopped retrying; please try again in a few minutes or reply and I'll open a ticket.` The trace's agent span carries the `tool_retries_exhausted` event (`tool=lookup_ticket`, `failures=3`, `max_tool_retries=2`).]

Three steps. Three red tool calls. Then a `tool_retries_exhausted` event with the tool name and the count, and an honest message that names the broken service. Forty-two hundredths of a cent. Two seconds. And on Monday, a filter for that event shows every conversation the outage touched.

[SLIDE 2: Before and after, from the trace]
| | Guards off | Step limit (default) | Step limit + `ATLAS_MAX_TOOL_RETRIES=2` |
|---|---|---|---|
| Steps | 549 | 6 | 3 |
| Stop reason in trace | `request_deadline_exceeded` | `step_limit_reached` | `tool_retries_exhausted` |
| Cost | $4.90 | $0.0086 | $0.0042 |
| Simulated time | 600.8 s | 4.3 s | 2.0 s |
| Employee saw | "took too long" | "please open a ticket" | "lookup_ticket is not responding" |

[SCREEN: Terminal.]

[CODE: the tests that keep it fixed]
```bash
python -m pytest -q tests/integration/test_spans.py -k loop_scenario
```

[DEMO: `2 passed, 17 deselected`.]

[CODE: `test_loop_scenario_stops_early` from `tests/integration/test_spans.py`]
```python
def test_loop_scenario_stops_early(settings, tracing):
    """5.6 fix: ATLAS_MAX_TOOL_RETRIES=2 surfaces the broken tool after three failed calls."""
    from app.agent import AtlasAgent

    agent = AtlasAgent(settings.with_overrides(max_tool_retries=2))
    result = agent.run("Where is my ticket TCK-100231?", tenant="ops", scenario="loop")
    spans = tracing.get_finished_spans()
    root = _by_name(spans, "invoke_agent atlas")[0]
    assert len(_by_name(spans, "step ")) == result.steps == 3
    assert result.resolved is False and result.outcome == "tool_error"
    assert any(e.name == "tool_retries_exhausted" for e in root.events)
```

And the tests. One asserts the defaults stop the loop at six steps with a `step_limit_reached` event. The other runs the fix: exactly three step spans, unresolved, outcome tool error, and the `tool_retries_exhausted` event on the agent span. Both green.

[AVATAR]
The loop was always visible. It just wasn't visible anywhere people were looking. Now it's a three-step trace with a yellow event, and two tests that fail if anyone turns the guards off again.

[SLIDE 3: Recap]
- The loop is invisible to status codes and logs
- Its trace: identical errors, tokens climbing
- Step limit plus tool-retry limit stop it

**Recap:** With the guards off, the runaway loop appears in the trace as hundreds of identical ERROR tool calls, input tokens climbing sixty-nine per step and a deadline stop, while HTTP status and logs look normal; the default step limit stops it at six steps, and `ATLAS_MAX_TOOL_RETRIES=2` stops it at three with a `tool_retries_exhausted` event and an honest answer.

**Transition:** Lab 3: trace the escalation path yourself and write the test for it.

### Speaker notes: common student mistakes / Q&A

- "Why not just retry with backoff inside the tool?" You will, in Section 7.3, for transient errors. This guard is for when retries are exhausted: stop feeding the failure to the model.
- "Should the agent create the ticket anyway when the ticket system is down?" It can't; that's the system that's down. Section 7.5 discusses degraded modes.
- `ATLAS_MAX_STEPS=0` means unlimited; only the request deadline (`ATLAS_REQUEST_DEADLINE_S`, default 600 s, simulated time offline) stops the loop, with `UNLIMITED_STEP_CEILING=2000` as a last resort. Keep these overrides out of `.env`; they're for this demo only.
- `make swarm SCENARIO=loop` injects the loop into a share of the swarm's traffic and rarely produces a single clean example; use `make loop-demo` for this lecture.

---

## Lecture 5.7 — Lab 3: Trace a multi-step ticket escalation

| Field | Value |
|---|---|
| ID | 5.7 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~210 spoken words, about 1:30 of talking at 140 wpm) |
| Learning objectives | 1. Trace an escalation path and check it against the six questions from 5.1. 2. Write an integration test that asserts the shape of that trace. 3. Read time to first token on the same trace. |
| Prerequisites | 5.1 to 5.6 |
| Files used | `04-labs/lab-03-agent-trace.md`, `03-code/app/agent.py`, `03-code/tests/integration/test_spans.py` (`test_escalation_child_generation` as the pattern) |

### Script

[AVATAR]
Lab three. When Atlas hands a sensitive request to the bigger model, the cost per answer jumps several times. Could you prove from a trace alone why it did? That's the lab: make the escalation path answer all six questions from 5.1, and pin its shape with a test. About an hour.

[SCREEN: VS Code, `04-labs/lab-03-agent-trace.md`. Scroll the steps.]

Part one: run a grievance question offline, like the one in 5.2, and check the trace against the six questions. Which one would you check first?

Part two: close the gaps the lab lists.

[SCREEN: Scroll to the test spec.]

Part three: the test. Exactly one generation on the escalation model, and an `escalation` event on the agent span. `test_escalation_child_generation` is a good starting pattern.

[SCREEN: Scroll to the stretch goal.]

Stretch: explain the escalated answer's time to first token.

[SLIDE 1: You can now]
- Read any agent trace against six questions
- Trace steps, tool errors, events and escalation
- Measure TTFT and choose log, span or metric

[AVATAR]
You can now read an agent trace against six questions, trace the loop step by step, and measure what users feel. Deliverables: the green test and a screenshot showing the escalation event and the gpt-4.1 generation.

**Recap:** Lab 3 makes the escalation trace answer all six questions, with steps, an escalation event, the model on every generation and tool arguments, and pins its shape with a test.

**Transition:** A six-question quiz on agent patterns, then Section 6, the signature section: where the money goes, and how to spend forty percent less of it.

### Speaker notes: common student mistakes / Q&A

- Students assert the escalation generation by position rather than by model name. Assert on `gen_ai.request.model`.
- On Atlas's path the `escalation` event is an OpenTelemetry span event on `invoke_agent atlas` (find it in `root.events`); on the Langfuse-native path it's an event observation inside the step.
- Escalation fires only for sensitive intents (grievances, legal, disciplinary); tool errors never escalate.
- The lab file is the source of truth for the exact question, file names and steps.

---

## Lecture 5.8 — Quiz: Agent patterns

| Field | Value |
|---|---|
| ID | 5.8 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~105 spoken words, about 0:45 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of the six questions and the step pattern. 2. Check recall of retriever recording, TTFT measurement, signal selection and cardinality. |
| Prerequisites | 5.1 to 5.7 |
| Files used | `06-assessments/quizzes/section-05.md` |

### Script

[AVATAR]
Six questions. Three minutes.

[SLIDE 1: Section 5 quiz: what's covered]
- The six questions and which span answers each
- Tool errors: level and output, not exceptions
- Events vs scores for the step limit
- What to record on a retriever; empty vs grounded
- TTFT vs total latency; `include_usage`
- Log, span or metric? Cardinality

One on mapping questions to spans. One on how tool errors should be recorded. One on events versus scores. One on retriever spans and grounding. One on time to first token. And one that gives you a fact and asks: log, span or metric?

Tip for the last one: if the fact has a user in it, it's not a metric label.

**Recap:** The quiz checks the six questions, the step pattern, retriever recording, TTFT and signal selection.

**Transition:** Next, Section 6, Cost engineering: token anatomy, a price table you can trust, and the challenge to cut Atlas's daily bill by forty percent.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which signal for cost per hour by tenant?" Metric, `atlas_cost_usd_total` with `tenant`, `model` and `feature` labels; cost per generation is on the span.
- Second most missed: what `stream_options={"include_usage": True}` does. Without it, streamed calls have no usage and zero cost.
