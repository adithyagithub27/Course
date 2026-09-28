# Section 5: Agent Observability Patterns

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈48 min (8 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating) / openinference-instrumentation-openai 0.1.61; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 5.1 | What an agent trace must answer | SL | 6:00 | ~575 |
| 5.2 | Code-along: tracing the tool loop step by step | SC | 9:00 | ~550 |
| 5.3 | RAG spans: retrieval quality is a production metric | SC | 7:00 | ~450 |
| 5.4 | Streaming: time to first token and tokens per second | SC | 7:00 | ~500 |
| 5.5 | Logs vs traces vs metrics for agents | SL | 6:00 | ~575 |
| 5.6 | Break it: the loop you can only see in a trace | DM | 6:00 | ~575 |
| 5.7 | Lab 3: Trace a multi-step ticket escalation | LAB | 4:00 (1:30 video) | ~250 |
| 5.8 | Quiz: Agent patterns | QZ | 3:00 (1:00 video) | ~100 |

**API guardrails for this section (do not deviate on screen):** step spans use `get_client().start_as_current_observation(name=..., as_type="chain")`; events use `get_client().create_event(name=..., level=..., metadata=...)`; the escalation call is the same `_call_model` generation with a different `model`. Streaming uses `stream=True, stream_options={"include_usage": True}` on Chat Completions; `completion_start_time` is a timezone-aware `datetime`. Prometheus labels are `tenant`, `model`, `tool`, `outcome` only. Never a `user_id` or `session_id` label.

---

## Lecture 5.1 — What an agent trace must answer

| Field | Value |
|---|---|
| ID | 5.1 |
| Type | SL (slides) |
| Target duration | 6:00 (~575 spoken words, about 4:06 of talking at 140 wpm) |
| Learning objectives | 1. List the six questions an agent trace must answer: why that tool, with what, what came back, how many steps, where the tokens went, where the time went. 2. Map each question to a span, attribute or event. 3. Judge a trace as "readable" or not against that list. |
| Prerequisites | Section 4 |
| Files used | Diagram: annotated agent trace (slides 2 and 9) |

### Script

[AVATAR]
On Monday morning after the four-thousand-dollar weekend, an engineer opens a trace. She has ninety seconds before the stand-up. [PAUSE] What does she need to be able to read off that screen, without opening a single log file? That list is the design spec for everything in this section. Six questions.

[SLIDE 1: Six questions an agent trace must answer]
1. Why did it call that tool?
2. With what arguments?
3. What came back?
4. How many steps, and did it stop on its own?
5. Where did the tokens go?
6. Where did the time go?

Why did it call that tool. With what. What came back. How many steps, and did it stop by itself or was it stopped. Where did the tokens go. Where did the time go. If a trace answers all six in ninety seconds, it's a good trace. If it answers three, you're going to be reading logs.

[SLIDE 2: The trace we're aiming for]
Diagram: waterfall. `atlas` (agent) 6.1 s. Children in order: `injection_check` (guardrail, 2 ms) → `step 1` (chain) containing `search_knowledge_base` (retriever) and `chat gpt-4.1-mini` (generation, finish: tool_calls) → `step 2` (chain) containing `execute_tool lookup_ticket` (tool, ERROR) and `chat gpt-4.1-mini` → `step 3` (chain) containing `create_ticket` (tool) and `chat gpt-4.1` (generation, escalation) → event `escalated` → scores: resolved true, steps 3.

Here's the trace we're building towards. Agent at the root. A guardrail first. Then one chain observation per step, and inside each step, whatever happened: a retriever, a generation, a tool. Step two's tool failed. Step three escalated to the big model. An event marks the escalation. Scores at the end. Let's take the six questions against it.

[SLIDE 3: Q1. Why that tool? → the generation before it]
- The model's output message in the previous generation shows the tool call it chose and any reasoning text
- `gen_ai.response.finish_reasons = ["tool_calls"]`
- Read: what did the model see (input messages) → what did it decide (output)

Why did it call that tool? Look at the generation immediately before it. Its output is the model's decision, including the tool name and arguments it chose, and its input is everything the model saw when it decided. The finish reason says `tool_calls`. Cause and effect, one click apart.

[SLIDE 4: Q2 and Q3. With what, and what came back → the tool observation]
- Input: the arguments, exactly as the model produced them
- Output: the result, clipped, masked
- Status and level: OK, or ERROR with the message the model then saw
- `gen_ai.tool.call.id` matches the call in the generation's output

With what, and what came back: the tool observation. Input is the arguments as the model produced them, which is how you catch a model passing a ticket ID with a typo. Output is the result, clipped and masked. Level and status tell you it failed, and the message shows what the model read next. The call ID ties it back to the generation.

[SLIDE 5: Q4. How many steps, and did it stop itself? → chain spans and events]
- One `chain` per step: count them
- Event `step_limit_reached` or `escalated` when the loop intervened
- Score `steps` and `step_limit_hit` on the trace
- Finish reason `stop` on the last generation means the model chose to end

How many steps? Count the chain observations. Did it stop on its own? The last generation's finish reason says `stop` if the model chose to end. If the loop intervened, there's an event: step limit reached, or escalated. And the same facts land as scores, so you can filter a week of traces by "hit the step limit."

[SLIDE 6: Q5. Where did the tokens go? → usage per generation, per step]
- Each generation: input, output, cached input
- Input tokens per step should be roughly flat; a rising line is context growth
- Cached tokens should be high on step 2+ if caching works (Section 6.4)
- Trace total = sum of generations; compare to the day's median

Where did the tokens go? Every generation has usage. Read the input tokens down the steps: flat is healthy; climbing is context growth, the Friday-night signature. Cached input should be high from step two onward once caching is on. And the trace total against the day's median tells you if this conversation is an outlier.

[SLIDE 7: Q6. Where did the time go? → the waterfall]
- Generations dominate; tools should be milliseconds
- Gaps between spans are your own code
- Time to first token per generation (5.4)
- One slow tool call at the wrong moment doubles p95 (Section 7)

Where did the time go? The waterfall. Generations should dominate. Tools should be milliseconds; a tool taking two seconds is a finding. Gaps between spans are your own code. And in the next lectures, time to first token per generation.

[SLIDE 8: What breaks readability]
- Flat traces: agent and twenty children, no steps → can't tell which tool followed which call
- Missing arguments or results → can't answer Q2 or Q3
- Silent stopping → loop ended, nothing says why
- Escalation without a marker → cost jumped, no reason in the trace
- Unredacted tool results the size of a web page → nobody scrolls

What breaks readability? Flat traces, where the agent has twenty children and no steps. Missing arguments or results. Silent stopping. Escalation with no marker. And results the size of a web page, which nobody reads.

[SLIDE 9: The pattern, in one slide]
- Agent → guardrail → step (chain) → { retriever | generation | tool } per step
- Events for interventions: `step_limit_reached`, `escalated`, `tool_retry_exhausted`
- Scores for outcomes: `resolved`, `steps`, `step_limit_hit`
- Everything clipped, masked and typed

[AVATAR]
Agent, guardrail, one chain per step, the work inside each step, events for interventions, scores for outcomes. That's the pattern. Next lecture you'll build it into the loop.

**Recap:** An agent trace must answer why a tool was called, with what, what came back, how many steps and who stopped it, where the tokens went and where the time went, and the pattern that answers all six is a chain observation per step with typed children, events for interventions and scores for outcomes.

**Transition:** Next, the code-along: step spans, redacted tool results, the step limit as an event, and escalation as a child generation.

### Speaker notes: common student mistakes / Q&A

- "Isn't one chain per step too many observations?" A ten-step trace has ten more spans. Readability is worth it; storage is clipped elsewhere.
- "Should the step span carry usage?" No; usage belongs to the generation. The step is structure.
- Students ask about "reasoning" or "thought" spans. If the model emits reasoning text, it's the generation's output; reasoning tokens are usage on the generation. No separate span.

---

## Lecture 5.2 — Code-along: tracing the tool loop step by step

| Field | Value |
|---|---|
| ID | 5.2 |
| Type | SC (code-along) |
| Target duration | 9:00 (~550 spoken words, about 3:56 of talking at 140 wpm, plus typing and trace dwell) |
| Learning objectives | 1. Wrap each loop iteration in a `chain` observation named `step n`. 2. Record tool arguments and clipped, masked results on tool observations, and errors as levels rather than exceptions. 3. Emit `step_limit_reached` and `escalated` events, and make escalation a generation with the bigger model. |
| Prerequisites | 5.1 |
| Files used | You type: edits to `03-code/app/agent.py`. Reference: repo version. |

### Script

[AVATAR]
Atlas's loop is about thirty lines. You're going to add six, and the trace goes from "agent with a pile of children" to the pattern from the last lecture. Let's go through the loop top to bottom.

[SCREEN: VS Code, `app/agent.py`, the `_loop` method as it stands: a `while` loop, `_call_model`, tool dispatch, `max_steps` check.]

[CODE: step 1, one chain observation per step]
```python
from langfuse import get_client, observe

    def _loop(self, messages: list[dict]) -> AgentResult:
        lf = get_client()
        step = 0
        while True:
            step += 1
            with lf.start_as_current_observation(name=f"step {step}", as_type="chain", metadata={"step": step}):
                response = self._call_model(messages, model=self.model)
                choice = response.choices[0]
                if choice.finish_reason != "tool_calls":
                    return AgentResult.answer(choice.message.content, steps=step)
                for call in choice.message.tool_calls:
                    messages.append(self._run_tool(call))
```

Step one. Inside the `while`, wrap the whole iteration in `start_as_current_observation`, type `chain`, named `step` and the number. It's a context manager, so everything called inside, the generation and the tools, nests under it. The metadata carries the step number as a field you can filter on.

[CODE: step 2, tool errors as levels, results clipped and masked]
```python
    @observe(as_type="tool", capture_output=False)
    def _run_tool(self, call) -> dict:
        lf = get_client()
        args = json.loads(call.function.arguments)
        try:
            result = self.tools[call.function.name](**args)
            lf.update_current_span(output=clip(result))
            return tool_message(call.id, result)
        except ToolError as exc:
            lf.update_current_span(
                output={"error": str(exc)},
                level="ERROR",
                status_message=f"{call.function.name}: {exc}",
            )
            self.consecutive_tool_errors += 1
            return tool_message(call.id, {"error": str(exc), "retryable": exc.retryable})
```

Step two, the tool wrapper. Output capture is off, and I set it explicitly, clipped, so a shipment manifest doesn't become a two-hundred-kilobyte attribute. Masking happens at the client from 4.6. On a tool error, don't raise. Record the error as output, set the level to ERROR with a message, and return a structured error to the model, so the model can decide what to do. The counter of consecutive errors is for the next step.

[CODE: step 3, the step limit as an event]
```python
            if step >= self.max_steps:
                lf.create_event(
                    name="step_limit_reached",
                    level="WARNING",
                    metadata={"max_steps": self.max_steps, "last_tool": last_tool_name, "consecutive_tool_errors": self.consecutive_tool_errors},
                )
                lf.score_current_trace(name="step_limit_hit", value=True, data_type="BOOLEAN")
                return AgentResult.degraded(
                    "I couldn't complete that right now. I've recorded the request and someone will follow up.",
                    steps=step,
                )
```

Step three, the step limit. When it trips, three things. An event named `step_limit_reached`, at warning level, with the limit, the last tool and the error count in its metadata; the event appears in the trace exactly where the loop stopped. A boolean score on the trace. And an honest, degraded answer to the user. That's the difference between the Friday run and the guarded run in Lecture 1.1, in nine lines.

[CODE: step 4, escalation as a child generation with an event]
```python
            if self.consecutive_tool_errors >= 2 and self.model != self.escalation_model and not escalated:
                lf.create_event(name="escalated", metadata={"from": self.model, "to": self.escalation_model, "reason": "repeated tool errors"})
                model = self.escalation_model
                escalated = True
            response = self._call_model(messages, model=model)
```

Step four, escalation. When the trigger fires, emit an `escalated` event with from, to and reason, and call `_call_model` with the escalation model. Because `_call_model` is already a generation observation, the trace shows a generation named `chat` with model `gpt-4.1` as a child of that step, right after the event. Cost jumps five times, and the trace says why. Escalate once per conversation; without that guard you'd escalate on every step.

[CODE: step 5, `_call_model` takes the model]
```python
    @observe(name="chat", as_type="generation")
    def _call_model(self, messages: list[dict], *, model: str) -> ModelResponse:
        response = self.client.chat.completions.create(model=model, messages=messages, tools=self.tool_specs)
        get_client().update_current_generation(model=response.model, usage_details=..., cost_details=self.pricing.cost_details(response), prompt=self.prompt)
        return response
```

And `_call_model` now takes the model as an argument. The generation's model field is whatever answered, so the two generations in a conversation can differ, and cost per model separates cleanly in Section six.

[SCREEN: Terminal 1: `OFFLINE=1 make run`. Terminal 2: send "Where is my ticket INC-2231?" with `SCENARIO=ticket_flaky` so the first lookup fails once, then succeeds. Browser: the trace.]

[DEMO: Trace: `atlas` → `injection_check` → `step 1` { `search_knowledge_base`, `chat` (gpt-4.1-mini, finish tool_calls) } → `step 2` { `lookup_ticket` (ERROR, "ticketing API 503"), `chat` } → `step 3` { `lookup_ticket` (OK), `chat` (finish stop) }. Scores: resolved true, steps 3. No escalation, because only one consecutive error.]

Send a ticket question with the flaky-ticket scenario, where the first lookup fails once. Read the trace. Step one: retriever and a generation that chose a tool. Step two: the tool at error level, red, with the 503 message, and the model's next decision. Step three: the tool succeeds, the model answers, finish reason stop. Resolved true, steps three. One error, no escalation, because the counter reset on success.

[SCREEN: Send the same question with `SCENARIO=loop` and `ATLAS_MAX_STEPS=8`. Open the trace.]

[DEMO: Eight steps; every `lookup_ticket` at ERROR; an `escalated` event in step 3; generations in steps 3-8 show model gpt-4.1; a `step_limit_reached` event after step 8; scores: resolved false, step_limit_hit true, steps 8. Trace cost about $0.04.]

Now the loop scenario, with the limit at eight. Eight steps. Every tool call red. An escalation event in step three, and every generation after it says gpt-4.1. A step-limit event after step eight. Resolved false, step limit hit true. Four cents. Every one of the six questions from 5.1 is answered on this screen.

[SLIDE 1: What the six lines bought you]
| Question | Answered by |
|---|---|
| Why that tool | previous generation's output, inside the same step |
| With what / what came back | tool observation input and clipped output; ERROR level on failure |
| How many steps, who stopped it | count of `step n`; `step_limit_reached` event; `steps` and `step_limit_hit` scores |
| Where the tokens went | usage per generation, per step; model per generation |
| Where the time went | the waterfall per step |
| Why cost jumped | `escalated` event and model name on the generation |

[AVATAR]
Six lines: a chain per step, errors as levels, two events, one score, and a model argument. That's the whole pattern. Everything in Sections six, seven and eleven reads traces shaped like this.

**Recap:** A `chain` observation per step, tool errors recorded as ERROR-level output instead of exceptions, `step_limit_reached` and `escalated` events, a `step_limit_hit` score and a model argument on the generation make the loop readable step by step.

**Transition:** Next, the retriever: why "how good was the search" is a production metric, and how to record it.

### Speaker notes: common student mistakes / Q&A

- Mistake: creating the step observation but calling `_call_model` outside the `with` block. The generation lands under the agent, not the step. Check indentation.
- Mistake: `create_event` after the step's `with` block closed. The event still lands in the trace under the agent, which is acceptable, but it reads better inside the step.
- "Why not raise on tool error and let the span record the exception?" Because the model needs the error as a message to decide what to do, and an exception ends the loop. Record, return, let the loop decide.
- `SCENARIO=ticket_flaky` is a helper mode of the mock for this lecture; if the repo names it differently at recording time, match the repo.

---

## Lecture 5.3 — RAG spans: retrieval quality is a production metric

| Field | Value |
|---|---|
| ID | 5.3 |
| Type | SC (code-along) |
| Target duration | 7:00 (~450 spoken words, about 3:13 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Record query, top-k, document IDs and scores on the retriever observation. 2. Flag empty and low-confidence retrievals with a level and a boolean score. 3. Compute empty-result rate and grounded rate across a replayed day. |
| Prerequisites | 5.2 |
| Files used | You type: edits to `03-code/app/knowledge.py`, `03-code/app/agent.py`. Reference: repo versions. Data: `OFFLINE=1 make replay`. |

### Script

[AVATAR]
Here's a question nobody asks until it's a problem: how often does Atlas answer a policy question with nothing relevant in front of it? When retrieval comes back empty, the model doesn't say "I don't know." It improvises. Confidently. The only place that shows up is the retriever span, if you record the right things on it.

[SLIDE 1: What to record on a retriever observation]
- Input: the query text and `top_k`
- Output: document IDs and scores (not full chunk text; it's already in the generation's input)
- Metadata: `hits`, `top_score`, `empty`, `index_version`
- Level: WARNING when empty or below a confidence threshold
- Score on the trace: `grounded` (boolean)

Five things. The query and top-k as input. Document IDs and scores as output, not the chunk text, which already appears in the generation's input. Metadata with the hit count, top score and an empty flag. A warning level when the result is empty or weak. And a boolean `grounded` score on the trace, so a week of traces can be filtered by it.

[SCREEN: VS Code, `app/knowledge.py`.]

[CODE: the retriever, fully recorded]
```python
from langfuse import get_client, observe

MIN_SCORE = float(os.getenv("KB_MIN_SCORE", "0.35"))

@observe(as_type="retriever", capture_output=False)
def search_knowledge_base(query: str, top_k: int = 3) -> list[dict]:
    hits = _bm25.search(query, top_k=top_k)
    good = [h for h in hits if h.score >= MIN_SCORE]
    lf = get_client()
    lf.update_current_span(
        input={"query": query, "top_k": top_k},
        output=[{"doc": h.doc, "score": round(h.score, 3)} for h in hits],
        metadata={"hits": len(hits), "good_hits": len(good), "top_score": round(hits[0].score, 3) if hits else 0.0,
                  "empty": not good, "index_version": _bm25.version},
        level="WARNING" if not good else "DEFAULT",
        status_message="no relevant documents" if not good else None,
    )
    return [h.to_dict() for h in good]
```

The retriever. Search, then split hits into good ones above a threshold. Update the span: input with query and top-k; output with doc names and rounded scores; metadata with hits, good hits, top score, an empty flag and the index version. Warning level when nothing cleared the threshold. And return only the good hits, so the model never sees junk with a score of point one.

[SCREEN: `app/agent.py`, where the retriever is called in step 1.]

[CODE: the grounded score]
```python
            docs = search_knowledge_base(message)
            lf.score_current_trace(name="grounded", value=bool(docs), data_type="BOOLEAN")
```

In the agent, right after retrieval, score the trace: grounded true if we had at least one good document, false otherwise. One line, and "how often do we answer ungrounded" becomes a filter.

[SCREEN: Terminal: send "What's the policy on bringing my dog to the office?" (not in the KB). Browser: the trace. Retriever at WARNING, output shows three docs with scores 0.12, 0.09, 0.07, metadata empty true; grounded false; the generation still answered.]

[DEMO: Warning-level retriever with low scores, grounded false, and a confident-sounding answer from the model.]

Ask something the knowledge base doesn't cover. The retriever is yellow. Three hits, all under the threshold, empty true. Grounded false. And look at the answer: the model produced two polite sentences of policy that doesn't exist. Without the retriever span, this trace looks like a success.

[SLIDE 2: Two rates you'll track from here]
- Empty-result rate: retriever observations with `empty = true` ÷ all retrievals
- Grounded rate: traces with `grounded = true` ÷ all traces with a retrieval
- Baseline on the replayed day: empty 6.8%, grounded 93.2%
- A jump in empty rate after a KB or index change is Incident 2's second cause (Section 11)

Two rates. Empty-result rate, from the retriever metadata. Grounded rate, from the score. On the replayed day the baseline is six point eight percent empty, ninety-three point two grounded. Write those in your build log. In Section eleven, a change to top-k moves those numbers, and you'll be asked to notice.

[SCREEN: Terminal: `OFFLINE=1 make replay`. Ops Console → Quality page now shows "Grounded rate 93.2%" and "Empty retrievals 6.8%". Browser: Langfuse, filter traces by score `grounded = false`; about 80 traces. Open two; note the question types: pets, parking, gym.]

[DEMO: Console shows the two rates; Langfuse lists ungrounded traces.]

Replay the day, and the console's quality page has its first two real numbers. In Langfuse, filter by grounded false: about eighty traces. Open a few. Pets, parking, the gym. That list is a to-do list for whoever owns the knowledge base, produced by the agent's own telemetry.

[SLIDE 3: When top-k and thresholds change]
- Record `top_k` and `index_version` so a change is visible in traces
- Higher top-k: more tokens per step (cost), fewer empties; lower: the reverse
- Section 6.5 tunes top-k for cost; Section 11 shows what happens when someone tunes it without looking here

[AVATAR]
Record the query, the documents, the scores, the emptiness. Score the trace as grounded or not. Two rates, on a dashboard, from day one. Retrieval quality is not an offline benchmark; it's a production metric, and now you have it.

**Recap:** The retriever observation records query, top-k, document IDs, scores, hit counts and an empty flag at warning level, the agent scores the trace `grounded`, and empty-result rate and grounded rate become production metrics you can filter a day by.

**Transition:** Next, streaming: measuring time to first token and tokens per second on every generation.

### Speaker notes: common student mistakes / Q&A

- Mistake: putting full chunk text in the retriever output. It doubles storage; the text is already in the generation's input messages.
- "Why a threshold instead of just top-k?" BM25 always returns something. Without a threshold, `empty` is never true and you never see the problem.
- Threshold values depend on the scorer; `KB_MIN_SCORE=0.35` is tuned for the course's BM25-lite over seven documents. Say so.
- The exact baseline rates depend on the seed and the mock commit; check the console before recording and update the slide if they moved.

---

## Lecture 5.4 — Streaming: time to first token and tokens per second

| Field | Value |
|---|---|
| ID | 5.4 |
| Type | SC (code-along) |
| Target duration | 7:00 (~500 spoken words, about 3:34 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Stream a chat completion with usage included and assemble the response. 2. Record `completion_start_time` on the Langfuse generation and `gen_ai.response.time_to_first_chunk` on the span. 3. Compute TTFT and TPOT with `northwind.latency` and know which one users feel. |
| Prerequisites | 5.2 |
| Files used | You type: edits to `03-code/app/agent.py` (`_call_model_stream`). Reference: `03-code/src/northwind/latency.py`, repo version of `agent.py`. |

### Script

[AVATAR]
Two generations, both two point six seconds. One felt instant; one felt broken. The difference: the first showed a word after three hundred milliseconds, the second showed nothing for two seconds and then everything at once. Total latency can't tell them apart. Time to first token can. Let's measure it.

[SLIDE 1: Three latency numbers per generation]
- TTFT: time to first token. What the user feels as "did it hear me?"
- TPOT: time per output token, after the first. Reading speed.
- Total: TTFT + (output_tokens − 1) × TPOT. What p95 dashboards usually show.
- Same total, different TTFT = completely different experience

Three numbers per generation. Time to first token, which is what the user feels as responsiveness. Time per output token after the first, which is reading speed. And total, which is what most dashboards show and which hides the difference.

[SCREEN: VS Code, `src/northwind/latency.py`. Show `ttft_ms`, `tpot_ms`, `percentile`.]

The latency module has the arithmetic: `ttft_ms` from two timestamps, `tpot_ms` from first-token time, end time and output tokens, and a percentile function you'll use in Section seven. Pure Python, unit-tested.

[SCREEN: `app/agent.py`. Add `_call_model_stream`.]

[CODE: the streaming generation]
```python
from datetime import datetime, timezone
from opentelemetry import trace
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from northwind.latency import ttft_ms, tpot_ms

    @observe(name="chat", as_type="generation")
    def _call_model_stream(self, messages: list[dict], *, model: str) -> ModelResponse:
        started = datetime.now(timezone.utc)
        first_token_at: datetime | None = None
        parts: list[str] = []
        usage = None
        stream = self.client.chat.completions.create(
            model=model, messages=messages, tools=self.tool_specs,
            stream=True, stream_options={"include_usage": True},
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                if first_token_at is None:
                    first_token_at = datetime.now(timezone.utc)
                    get_client().update_current_generation(completion_start_time=first_token_at)
                    trace.get_current_span().set_attribute(
                        g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK, (first_token_at - started).total_seconds()
                    )
                parts.append(chunk.choices[0].delta.content)
            if chunk.usage:
                usage = chunk.usage
        ended = datetime.now(timezone.utc)
        ...
```

The streaming version. Note the start time. Ask for a stream, and ask for usage to be included; without that option the final chunk has no token counts and you can't price the call. Then iterate. On the first chunk with content, record the time, and do two things with it. Tell Langfuse via `completion_start_time`, which is how its UI shows time to first token on the generation. And set the standard attribute, `gen_ai.response.time_to_first_chunk`, on the underlying OpenTelemetry span, in seconds. Incubating name, may change. Collect the text, catch the usage on the last chunk, note the end time.

[CODE: finish the generation]
```python
        get_client().update_current_generation(
            model=model,
            output="".join(parts),
            usage_details={"input": usage.prompt_tokens, "output": usage.completion_tokens},
            cost_details=self.pricing.cost_details_from_usage(model, usage),
            metadata={
                "ttft_ms": ttft_ms(started, first_token_at),
                "tpot_ms": tpot_ms(first_token_at, ended, usage.completion_tokens),
            },
        )
        return assemble_response(parts, usage, model)
```

After the loop, finish the generation: output, usage, cost, and the two computed numbers in metadata, so they're filterable per generation. Then assemble a response object shaped like the non-streaming one, so the loop doesn't care which path ran.

[SLIDE 2: Where each number lives]
| Number | Where | Used by |
|---|---|---|
| `completion_start_time` | Langfuse generation | Langfuse latency views, "time to first token" column |
| `gen_ai.response.time_to_first_chunk` | span attribute (seconds) | any OTel backend; collector → metrics (Section 9) |
| `ttft_ms`, `tpot_ms` | generation metadata | Ops Console latency page, Section 7 budgets |
| Prometheus histogram `atlas_ttft_seconds` | `/metrics` | Grafana p95 (Section 9) |

The same measurement lands in four places for four audiences. Langfuse's own field for its UI. The standard attribute for any OpenTelemetry backend. Our metadata for the console. And, in Section nine, a Prometheus histogram for Grafana.

[SCREEN: Terminal: `OFFLINE=1 make run` with `ATLAS_STREAM=1`. Send a question. Browser: the generation shows "Time to first token 312 ms", total 2.6 s; metadata shows ttft_ms 312, tpot_ms 16.]

[DEMO: The mock streams offline too, with realistic TTFT and TPOT distributions.]

Run with streaming on and send a question. The generation now shows time to first token: three hundred and twelve milliseconds, against a total of two point six seconds. TPOT sixteen milliseconds, about sixty tokens a second. The mock streams offline as well, with realistic distributions, so the day's replay has TTFT for every generation.

[SLIDE 3: Reading TTFT across a day]
- p50 TTFT ≈ 350 ms, p95 ≈ 1.1 s on the replayed day
- TTFT climbs with input tokens: context bloat shows here first
- TPOT is mostly a property of the model; a jump means a provider change or a slow region
- Section 7 sets budgets: TTFT p95 under 1.5 s, total p95 under 4 s

Across the day: median TTFT about three hundred and fifty milliseconds, p95 around one point one seconds. Two patterns to remember. TTFT climbs with input size, so context bloat shows up here before it shows up in your bill. And TPOT is mostly a property of the model; if it jumps, the provider changed something. Section seven sets budgets for both.

[AVATAR]
Two timestamps and one flag on the request. Time to first token in Langfuse, the standard attribute for everyone else, and the number users actually feel, on every generation.

**Recap:** Stream with `include_usage`, record the first content chunk's time as `completion_start_time` and as `gen_ai.response.time_to_first_chunk`, compute TTFT and TPOT with `northwind.latency`, and store them in metadata so latency can be read per generation and across a day.

**Transition:** Next, a slides lecture on the three signals: when an agent should log, when it should trace, and when it should count.

### Speaker notes: common student mistakes / Q&A

- Mistake: omitting `stream_options={"include_usage": True}`. Usage is `None`; cost is zero; dashboards lie low.
- Mistake: measuring TTFT to the first chunk of any kind. The first chunk may carry only a role and no content. Wait for content (or a tool-call delta).
- Tool-call streaming: deltas carry `tool_calls` fragments; the repo's `assemble_response` reassembles them. Keep it out of the lecture; mention it exists.
- `completion_start_time` must be timezone-aware; naive datetimes are rejected or misread.
- On the Responses API, the usage fields are `input_tokens` / `output_tokens`; the repo's pricing helper handles both.

---

## Lecture 5.5 — Logs vs traces vs metrics for agents

| Field | Value |
|---|---|
| ID | 5.5 |
| Type | SL (slides) |
| Target duration | 6:00 (~575 spoken words, about 4:06 of talking at 140 wpm) |
| Learning objectives | 1. Decide, for a given fact about an agent, whether it belongs in a log, a span or a metric. 2. Correlate structured JSON logs with traces via `trace_id`. 3. Avoid cardinality traps: never a user or session label on a Prometheus metric. |
| Prerequisites | 5.1 to 5.4 |
| Files used | `03-code/telemetry/logging_setup.py`, `03-code/telemetry/metrics.py` (shown, not typed) |

### Script

[AVATAR]
"Should this be a log or a span?" I get that question in every team I work with, and the answer is a rule you can apply in five seconds. But there's a trap on the metrics side that has taken down more Prometheus servers than any bug, and agents walk straight into it. Let's do the rule, then the trap.

[SLIDE 1: Three signals, three questions]
| Signal | Answers | Shape | Cost grows with |
|---|---|---|---|
| Trace | what happened in this request, in order | tree of spans | requests × spans |
| Metric | how much, how often, right now | number series over time | label combinations |
| Log | what did the code say at this moment | line of text or JSON | lines |

Three signals. A trace answers what happened in one request. A metric answers how much and how often, right now, across all requests. A log answers what the code wanted to say at a moment. Their costs grow differently: traces with request volume, metrics with label combinations, logs with lines.

[SLIDE 2: The five-second rule]
- Is it about one request, in sequence? → span or event on the span
- Is it a number you'd graph over time or alert on? → metric
- Is it a message for a human debugging later? → log, with `trace_id`
- Is it both? → span first; derive the metric from spans or emit both

The rule. If it's about one request, in sequence, it's a span or an event on one. If it's a number you'd graph or alert on, it's a metric. If it's a message for a human, it's a log, with the trace ID attached. If it's both, span first, and emit the metric alongside.

[SLIDE 3: Agent examples]
| Fact | Signal |
|---|---|
| The model chose `lookup_ticket` with these arguments | span (tool observation) |
| Tool error rate for `lookup_ticket`, last 5 minutes | metric: `atlas_tool_calls_total{tool, outcome}` |
| Step limit reached in this conversation | event on the span + score; and metric `atlas_step_limit_total{tenant}` |
| Cost of this generation | span (generation cost_details) |
| Cost per hour by tenant | metric: `atlas_cost_usd_total{tenant, model}` |
| "Prompt fetched from fallback: Langfuse unreachable" | log, WARNING, with trace_id |
| TTFT of this generation | span (completion_start_time) |
| TTFT p95 today | metric: histogram `atlas_ttft_seconds{model}` |

Examples. The tool the model chose: a span. Tool error rate over five minutes: a metric. Step limit reached: an event on the span, a score, and a metric counter, because you'll alert on the rate. Cost of one generation: on the span. Cost per hour by tenant: a metric. "Prompt fetched from fallback": a log at warning level, with the trace ID. TTFT of this call: on the span. TTFT p95 today: a histogram.

[SLIDE 4: Logs that are worth having]
```json
{"ts": "2026-09-28T14:02:07Z", "level": "WARNING", "logger": "atlas.prompts",
 "msg": "prompt fetched from fallback", "prompt": "atlas-system",
 "trace_id": "c8e0b7a1c432fda1dd0b3d28692756c3", "span_id": "21c0b128c8a0a5b9",
 "tenant": "ops", "service": "atlas", "env": "dev"}
```
- `telemetry/logging_setup.py`: JSON formatter that reads the current span context
- Paste the `trace_id` into Langfuse: the whole request appears
- No message bodies, no PII in logs; that's what masked spans are for

A log that's worth having looks like this. JSON, one line, a level, a message, and the trace and span IDs read from the current span context by the formatter. Paste that trace ID into Langfuse and the whole request opens. Our logging setup does this for every line. Two rules for logs: no message bodies, and no personal data. Logs are usually retained longer and read by more people than traces.

[SLIDE 5: The cardinality trap]
- A metric series exists for every unique combination of label values
- `tenant` (4) × `model` (3) × `tool` (5) × `outcome` (2) = 120 series. Fine.
- Add `user_id` (2,000) → 240,000 series. Prometheus memory, query time and your dashboards all suffer.
- Add `session_id` → unbounded. This is how a metrics server dies.
- Rule: labels are for dimensions with a small, fixed set of values. Users and sessions are trace dimensions, never metric labels.

Now the trap. A Prometheus metric is one series per unique combination of label values. Tenant, model, tool, outcome: four times three times five times two, a hundred and twenty series. Fine. Add a user ID label, with two thousand employees: two hundred and forty thousand series. Add a session ID: unbounded, and your metrics server falls over at three in the morning. Labels are for dimensions with a small, fixed set of values. Users and sessions belong in traces, where they already are.

[SLIDE 6: What `telemetry/metrics.py` exposes]
```text
atlas_requests_total{tenant, outcome}
atlas_tokens_total{tenant, model, kind}          kind = input | output | cache_read | reasoning
atlas_cost_usd_total{tenant, model}
atlas_tool_calls_total{tenant, tool, outcome}
atlas_step_limit_total{tenant}
atlas_budget_hits_total{tenant, level}           level = soft | hard
atlas_ttft_seconds{model}     histogram
atlas_request_seconds{tenant} histogram
```

Here's what Atlas exposes at slash metrics, and every label set is small and fixed. Tokens by kind, so cached and reasoning tokens are visible as series. Cost by tenant and model. Tool calls by outcome. Step limits and budget hits. Two histograms. Section nine builds the dashboard and alerts on exactly these.

[SLIDE 7: Putting it together for one request]
Diagram: one request flows through Atlas. Three arrows out: "spans → Langfuse (what happened, cost, TTFT)", "metrics → Prometheus (rates, totals, histograms, by tenant/model/tool)", "logs → stdout JSON with trace_id (human notes)". A dotted line from a log line to the trace it names.

For one request: spans to Langfuse for what happened. Metrics to Prometheus for how much and how often. Logs to standard out, in JSON, with the trace ID, for the human notes. The trace ID is the thread that ties a log line back to the request it came from.

[AVATAR]
Span for the request, metric for the number, log for the human, trace ID on everything. And never, ever, a user ID on a metric label.

**Recap:** Facts about one request go on spans, numbers you graph or alert on go in metrics with small fixed label sets, human notes go in JSON logs carrying `trace_id`, and users and sessions are trace dimensions, never Prometheus labels.

**Transition:** Next, a break-it demo: the Friday loop, seen from inside the trace this time, and the code that stops it.

### Speaker notes: common student mistakes / Q&A

- "Can I derive metrics from spans instead of emitting both?" Yes, via the collector's span-metrics connector (Section 13) or Langfuse dashboards (9.4). We emit both in the app for simplicity and for the offline path.
- "Why not `logger.info` the whole prompt?" Size, PII and retention. The prompt is on the generation, masked.
- Students ask about OpenTelemetry logs and metrics APIs. Both exist; we use Prometheus client and JSON logging because they're the common enterprise default. Section 12.4 mentions the OTel versions.
- Metric names on the slide must match `telemetry/metrics.py` at recording time.

---

## Lecture 5.6 — Break it: the loop you can only see in a trace

| Field | Value |
|---|---|
| ID | 5.6 |
| Type | DM (live demo, before/after) |
| Target duration | 6:00 (~575 spoken words, about 4:06 of talking at 140 wpm, plus trace dwell) |
| Learning objectives | 1. Inject the `loop` scenario and read the runaway trace: repeated identical tool errors, climbing input tokens, escalation. 2. Explain why no log line, metric or HTTP status would have shown it. 3. Apply the two fixes, a step limit and consecutive-error surfacing, and read the after trace. |
| Prerequisites | 5.2, 1.1 |
| Files used | `03-code/simulator/scenarios.py::loop`, `03-code/app/agent.py`, `03-code/tests/integration/test_spans.py` (`test_loop_scenario_stops_at_step_limit`) |

**Recording note:** the "before" run uses `ATLAS_MAX_STEPS=0` and `ATLAS_MAX_TOOL_RETRIES=0` so both guards are off; stop the swarm after one conversation. The "after" run uses defaults (`ATLAS_MAX_STEPS=8`, `ATLAS_MAX_TOOL_RETRIES=2`). Tint before red, after green. Lecture 1.1 showed the money; this lecture shows the trace and the code.

### Script

[AVATAR]
In Lecture 1.1 you watched the Friday loop from the cost meter. Now you're going to watch it from inside the trace, because that's where an on-call engineer would actually find it. Then we fix it in the code, and read the trace again.

[SCREEN: Terminal 1: `ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 OFFLINE=1 make run`. Terminal 2: `OFFLINE=1 make swarm SCENARIO=loop`. Stop after the first conversation completes (about 60 steps, ~2 minutes at mock latency; editors: cut to the end).]

Guards off. One conversation through the loop scenario. I'll let it run to the timeout.

[SCREEN: Browser: Langfuse, newest trace. The tree is very long. Collapse to steps: `step 1` ... `step 61`. Header: 61 steps, cost $3.90, 9 min 58 s, 480k input tokens total.]

[DEMO: Scroll the collapsed tree; it goes on for two screens.]

Here it is. Sixty-one steps. Nine minutes fifty-eight seconds. Three dollars ninety. Four hundred and eighty thousand input tokens for one question.

[SCREEN: Expand `step 2`, `step 3`, `step 4`. Each has `lookup_ticket` at ERROR with the same status message "ticketing API 503" and a `chat` generation. Click the generations in turn and read usage: input 2,140 → 3,260 → 4,390.]

Expand a few steps. Every one is the same shape: `lookup_ticket`, red, "ticketing API 503", then a model call. Click the generations and read the input tokens. Twenty-one hundred. Thirty-two hundred. Forty-four hundred. About eleven hundred more each step. The error message, the arguments, the model's retry text, all appended, all re-read.

[SCREEN: Expand `step 14`. It contains an `escalated` event from the previous lecture's code? No: in this "before" build the escalation is a plain model swap with no event. Show the generation model changing from gpt-4.1-mini to gpt-4.1 with no marker.]

Step fourteen. The model on the generation changes from mini to full gpt-4.1, and nothing in the trace says why. That's the escalation rule firing, silently. From here every step costs five times more.

[SCREEN: Expand `step 61`. Its generation has no finish; the conversation ends with the HTTP timeout. No event, no score.]

Step sixty-one ends with the client timeout. No event. No score. No answer. From the outside: an HTTP 200 with an empty body, after ten minutes.

[SLIDE 1: Where else would this have shown up?]
| Signal | What it showed on Friday |
|---|---|
| HTTP status | 200 |
| Request count | 1 |
| Error logs | 60 lines "ticketing API 503", indistinguishable from 60 different users |
| Tool error metric | 100% error rate for `lookup_ticket`: a real signal, if anyone had the alert |
| Trace | 61 identical steps, climbing tokens, silent escalation, no stop |

Where else would you have seen this? The HTTP status was 200. Request count, one. The error logs had sixty lines saying 503, which look exactly like sixty different users having a bad day. The tool error metric did spike, and that's the alert we add in Section nine. But the shape of the failure, one conversation retrying itself into the ground, only exists in the trace.

[AVATAR]
Two fixes, both in the agent, both from Lecture 5.2. A step limit, with an event. And surfacing consecutive tool errors instead of feeding them back forever.

[SCREEN: VS Code, `app/agent.py`. Highlight the `max_steps` block with `create_event("step_limit_reached")` and the new consecutive-errors block.]

[CODE: the second guard, consecutive identical tool errors]
```python
            if self.consecutive_tool_errors > self.max_tool_retries:
                lf.create_event(
                    name="tool_retry_exhausted",
                    level="WARNING",
                    metadata={"tool": last_tool_name, "attempts": self.consecutive_tool_errors, "last_error": last_error},
                )
                lf.score_current_trace(name="tool_retry_exhausted", value=True, data_type="BOOLEAN")
                return AgentResult.degraded(
                    f"The {TOOL_LABELS[last_tool_name]} system isn't responding right now. "
                    "I've noted your request and you'll get an email when it's back.",
                    steps=step,
                )
```

The step limit you saw in 5.2. This is the second guard. After more than two consecutive errors from the same tool, stop. Emit a `tool_retry_exhausted` event with the tool, the attempt count and the last error. Score the trace. And tell the employee the truth, with the system's name in plain English. This fires long before the step limit would, on exactly the failure that caused Friday.

[SCREEN: Terminal 1: `OFFLINE=1 make run` (defaults). Terminal 2: `OFFLINE=1 make swarm SCENARIO=loop`, one conversation.]

[SCREEN: Browser: newest trace. `atlas` → `injection_check` → `step 1` { retriever, chat } → `step 2` { `lookup_ticket` ERROR, chat } → `step 3` { `lookup_ticket` ERROR, chat } → `step 4` { `lookup_ticket` ERROR } → event `tool_retry_exhausted` (WARNING). Scores: resolved false, tool_retry_exhausted true, steps 4. Cost $0.02, 7.1 s.]

[DEMO: Short, readable trace with a warning event and an honest answer as the trace output.]

Same scenario, guards on. Four steps. Three red tool calls. Then a yellow event, `tool_retry_exhausted`, with the tool name and "ticketing API 503" in its metadata. Resolved false, so it's honest about the outcome. Two cents. Seven seconds. And the trace output is the message the employee saw.

[SLIDE 2: Before and after, from the trace]
| | Before | After |
|---|---|---|
| Steps | 61 | 4 |
| Tool errors fed back to the model | 60 | 3 |
| Escalation | silent, step 14 | never reached |
| Stop reason in trace | none | `tool_retry_exhausted` event + score |
| Cost | $3.90 | $0.02 |
| User saw | timeout | honest message in 7 s |

Sixty-one steps to four. Three ninety to two cents. And the reason it stopped is written in the trace, as an event and a score, so a filter for `tool_retry_exhausted = true` on Monday shows every conversation the outage touched.

[SCREEN: `tests/integration/test_spans.py`, `test_loop_scenario_stops_at_step_limit`. Run `make test`.]

[CODE: the regression test]
```python
def test_loop_scenario_stops_early(atlas_offline_loop, spans):
    result = atlas_offline_loop.run("Where is my ticket INC-2231?", tenant="ops", user_id="u", session_id="s")
    steps = [s for s in spans.get_finished_spans() if s.name.startswith("step ")]
    assert len(steps) <= 4
    assert result.resolved is False
    assert any(s.name == "tool_retry_exhausted" for s in spans.get_finished_spans())
```

And the test that keeps it fixed: run the loop scenario offline, assert at most four steps, an unresolved result and the event. Green.

[AVATAR]
The loop was always visible. It just wasn't visible anywhere people were looking. Now it's a four-step trace with a yellow event, and a test that fails if anyone turns the guards off again.

**Recap:** The runaway loop appears in the trace as dozens of identical ERROR tool calls, climbing input tokens and a silent model swap, while HTTP status and logs look normal; a step limit and a consecutive-tool-error guard, each with an event and a score, turn it into a four-step trace with an honest answer.

**Transition:** Lab 3: trace the ticket escalation path yourself and write the test for it.

### Speaker notes: common student mistakes / Q&A

- "Why not just retry with backoff inside the tool?" You will, in Section 7.3, for transient errors. This guard is for when retries are exhausted: stop feeding the failure to the model.
- "Should the agent create the ticket anyway when the ticket system is down?" It can't; that's the system that's down. The degraded message promises a follow-up; Section 7.5 adds a queue for exactly this.
- The mock's loop scenario is deterministic; if the before-trace step count differs from 61 at recording time, update the narration numbers to match.
- Keep the before run's `ATLAS_MAX_STEPS=0` out of `.env`; it's an override for this demo only.

---

## Lecture 5.7 — Lab 3: Trace a multi-step ticket escalation

| Field | Value |
|---|---|
| ID | 5.7 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~250 spoken words, about 1:47 of talking at 140 wpm) |
| Learning objectives | 1. Trace the path lookup fails → create_ticket → escalation with steps, events and scores. 2. Write an integration test that asserts the shape of that trace. 3. Read TTFT and grounded on the same trace. |
| Prerequisites | 5.1 to 5.6 |
| Files used | `04-labs/lab-03-agent-trace.md`, `03-code/app/agent.py`, `03-code/tests/integration/test_spans.py` |

### Script

[AVATAR]
Lab three. The escalation path: an employee asks about a ticket, the lookup fails, Atlas creates a new ticket instead, and escalates to the bigger model to write the summary. Your job is to make that trace answer all six questions from 5.1, and to pin it with a test. Forty-five minutes.

[SCREEN: VS Code, `04-labs/lab-03-agent-trace.md`. Scroll the steps.]

Part one: run the `ticket_escalation` scenario offline and open the trace. Check off the six questions. Anything you can't answer from the trace is a gap to fix.

Part two: fix the gaps. The lab expects at least: a `chain` per step, an `escalated` event before the gpt-4.1 generation, `create_ticket` with its arguments and the new ticket ID in its output, and scores for `resolved`, `steps` and `grounded`.

[SCREEN: Scroll to the test spec.]

Part three: the test. Assert the number of step spans, that exactly one generation used the escalation model and that it comes after the `escalated` event, and that the `create_ticket` observation's output contains a ticket ID.

[SCREEN: Scroll to the stretch goal.]

Stretch: turn on streaming and assert that every generation has `completion_start_time` set.

[AVATAR]
Deliverables: the green test, and a screenshot of the trace with the escalation event and the gpt-4.1 generation visible. Add the trace's total cost to your build log next to the median from the replayed day.

**Recap:** Lab 3 makes the ticket-escalation trace answer all six questions, with steps, an escalation event, tool arguments and scores, and pins it with a test.

**Transition:** A six-question quiz on agent patterns, then Section 6, the signature section: where the money goes, and how to spend forty percent less of it.

### Speaker notes: common student mistakes / Q&A

- Students assert the escalation generation by position rather than by model name; the mock's step count can vary by one. Assert on the model attribute.
- The `escalated` event is created by the client, not attached to the OTel span as an event; tests find it as a span named `escalated` in the in-memory exporter.
- If `create_ticket`'s output is masked (ticket IDs are not PII in our regexes, but employee IDs are), check the mask before blaming the tool.

---

## Lecture 5.8 — Quiz: Agent patterns

| Field | Value |
|---|---|
| ID | 5.8 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~100 spoken words, about 0:43 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of the six questions and the step-span pattern. 2. Check recall of retriever recording, TTFT measurement, signal selection and cardinality. |
| Prerequisites | 5.1 to 5.7 |
| Files used | `06-assessments/quizzes/section-05.md` |

### Script

[AVATAR]
Six questions. Three minutes.

[SLIDE 1: Section 5 quiz: what's covered]
- The six questions and which span answers each
- Tool errors: level and output, not exceptions
- Events vs scores for the step limit
- What to record on a retriever; the grounded score
- TTFT vs total latency; `include_usage`
- Log, span or metric? Cardinality

One on mapping questions to spans. One on how tool errors should be recorded. One on events versus scores. One on retriever spans and grounding. One on time to first token. And one that gives you a fact and asks: log, span or metric?

Tip for the last one: if the fact has a user in it, it's not a metric label.

**Recap:** The quiz checks the six questions, the step pattern, retriever recording, TTFT and signal selection.

**Transition:** Next, Section 6, Cost engineering: token anatomy, a price table you can trust, and the challenge to cut Atlas's daily bill by forty percent.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which signal for cost per hour by tenant?" Metric, with `tenant` and `model` labels; cost per generation is on the span.
- Second most missed: what `stream_options={"include_usage": True}` does. Without it, streamed calls have no usage and zero cost.
