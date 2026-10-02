# Section 10: Performance & Reliability Testing

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 10 (curriculum `01-curriculum/full-curriculum.md`, Module 10, ~21 min, 3 lectures)
> **Source of truth for code, numbers and outputs:** `14-quality-review/course2-bible.md` §7 (Module 10), §8.20, §12. Every output below was captured from a real run in **offline mode** (`OFFLINE=1`: deterministic mock LLM and mock judge, no API key). Offline latencies come from a **simulated clock**; say "simulated" whenever a latency is on screen.
> **Repo:** `04-code-examples/agent-eval-framework/`. Run demos with `uv run python demos/<file>` (or `.venv/bin/python demos/<file>`).
> **Version banner for every code slide:** `Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+ | agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key`
> **Models and prices (A8):** agent `gpt-4.1-mini`, strong model and judge `gpt-4.1`. Every price on screen carries "verify current pricing".

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 10.1 | Latency, Token Cost & Throughput Benchmarking | Teach + demo | 7:00 | 895 |
| 10.2 | Reliability: Failure Rate, Retry, Timeout & Loop Detection | Build-along | 7:00 | 660 |
| 10.3 | Cost Engineering: Finding the 80/20 of Agent Spend | Build-along | 7:00 | 727 |

Cue legend (word counts below are spoken narration in `### Script`, `### Recap` and `### Transition`, excluding cue lines, slide text, tables, code and command output): `[AVATAR]` HeyGen avatar on camera (only these blocks go to HeyGen); `[SLIDE n: title]` full-screen slide, bullets are the exact slide text, `Diagram:` lines are designer instructions; `[SCREEN: ...]` OBS recording of the editor or browser; `[CODE: ...]` code revealed on screen, the fenced block is the exact text; `[DEMO: ...]` a terminal run, the fenced block is real output (trimmed); `[B-ROLL: ...]` cutaway; `[PAUSE]` one beat of silence. Word counts are spoken words only.

---

## Lecture 10.1 — Latency, Token Cost & Throughput Benchmarking

| Field | Value |
|---|---|
| ID | 10.1 |
| Title | Latency, Token Cost & Throughput Benchmarking |
| Type | Teach + demo |
| Target duration | 7:00 (895 spoken words; the rest is terminal dwell) |
| Learning objectives | 1. Measure end-to-end latency as a distribution (p50, p95, max) instead of an average. 2. Attribute token cost per call and per step (tool-call step vs answer step) with a client wrapper. 3. Turn a benchmark into throughput and cost-per-1,000-tasks numbers a manager can budget with. |
| Prerequisites | 9.3 (cost per trace, OpenTelemetry GenAI spans) |
| Files used | `performance/benchmark.py` (`UsageMeter`, `percentile`, `run_benchmark`, `BENCHMARK_QUERIES`), `config/settings.py` (prices), `demos/m10_benchmark.py` |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key

[AVATAR]
Your agent answers most questions in under two seconds. Then one customer asks to cancel and get a refund, and they wait four and a half. Same agent. Same day. If you only measured the average, you'd never see that customer. [PAUSE] So how slow is your agent, really? And what does each answer cost?

[SLIDE 2: By the end of this lecture]
- Benchmark latency as a distribution, not an average
- Attribute token cost to every LLM call and step
- Turn the numbers into throughput and cost per 1,000 tasks

By the end of this lecture, you'll run a twenty-query benchmark on the TechCorp support agent. You'll read its latency distribution, see which step spends the money, and turn it all into two numbers your manager actually wants: tasks per minute and dollars per thousand tasks.

[SLIDE 3: Where performance fits]
Diagram: the five quality dimensions as five tiles in a row (Correctness, Faithfulness, Relevance, Safety, Reliability). The Reliability tile is highlighted in Teal and expands downward into four small tags: "consistency 0.7", "failure rate ≤ 10%", "p95 ≤ 10 s", "cost ≤ $0.01/task (verify current pricing)".

Remember the five quality dimensions from Module 2? Latency and cost aren't a sixth dimension. They live under Reliability. And they already have thresholds in `config/eval_config.yaml`: p95 latency at or under ten seconds, and at most one cent per task, verify current pricing. In Module 9 you traced a single request. Now you measure hundreds, because one trace is an anecdote and a benchmark is evidence.

[SLIDE 4: Three numbers, three questions]
- Latency: how long does the user wait?
- Token cost: how much does each answer cost?
- Throughput: how many tasks per minute can one worker do?

Three numbers. Latency answers "how long does the user wait?" Token cost answers "what does each answer cost?" And throughput answers "how much traffic can one worker handle?" Each one needs a different measurement, so let's take them one at a time.

[SLIDE 5: Latency is a distribution]
Diagram: a histogram with five bars labelled 0-1 s, 1-2 s, 2-3 s, 3-4 s, 4-5 s, heights 2, 15, 1, 1, 1. A Teal vertical line at 1.75 s labelled "p50". An Amber line at 3.34 s labelled "p95". A small red marker at 4.5 s labelled "max". Footnote: "simulated latency, offline mode".

Here's why averages lie. Most of our twenty tasks finish between one and two seconds. Three take longer. The average hides those three, but those three are the customers who complain.

So you report percentiles. The p50, the median, is the typical user. The p95 is the unlucky one in twenty. And the max is your worst case. When your p95 is double your p50, you have a long tail, and the next question is always: which tasks live in the tail?

If you stream responses, also measure time to first token, because that's when the user sees something happen. Our support agent doesn't stream, so we measure end to end.

[SLIDE 6: Where agent latency comes from]
- Each loop iteration is one more LLM call
- FAQ answer: 2 LLM calls (search, then answer)
- Cancel and refund: 4 LLM calls, 3 tools
- More calls means more waiting and more tokens

For agents, latency has a simple driver. Every trip around the loop is another LLM call. A pricing question takes two calls: search the knowledge base, then answer. A cancel-and-refund request takes four calls and three tools. So the slowest task is usually the longest trajectory, not a slow network. What does that tell you about where to optimise first?

[CODE: `performance/benchmark.py`, the `UsageMeter.create` method. Highlight the two `clock.now()` calls and the `step` line.]

```python
def create(self, **kwargs: Any) -> Any:
    t0 = clock.now()
    resp = self._inner.chat.completions.create(**kwargs)
    step = "tool_call" if resp.choices[0].finish_reason == "tool_calls" else "answer"
    self.calls.append(Call(kwargs.get("model", ""), resp.usage.prompt_tokens, resp.usage.completion_tokens, clock.now() - t0, step))
    return resp
```

Here's the measuring tool. `UsageMeter` wraps the OpenAI client and records every call: the model, input tokens, output tokens, latency, and the step. If the model asked for a tool, it's a tool-call step. Otherwise it's the answer step. You pass it into the agent with `client=meter`, and the agent never knows it's being watched.

[SLIDE 7: Cost per call, per task, per 1,000 tasks]
- Cost = input tokens × input price + output tokens × output price
- gpt-4.1-mini: $0.40 in, $1.60 out per 1M tokens (verify current pricing)
- Sum per task, then multiply by 1,000 for a budget number

Cost is arithmetic on those token counts. Input and output tokens have different prices. For gpt-4.1-mini, forty cents per million input tokens and a dollar sixty per million output tokens. Verify current pricing before you quote it. Add up the calls in a task, and you have cost per task. Multiply by a thousand, and you have a number finance can put in a spreadsheet.

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`. Type the command.]

```bash
uv run python demos/m10_benchmark.py
```

[DEMO: Output after the banner (offline, simulated latency)]

```text
  model                  gpt-4.1-mini
  tasks                  20
  latency_p50_s          1.75
  latency_p95_s          3.34
  latency_max_s          4.5
  avg_tokens             1785.2
  avg_llm_calls          2
  avg_cost_usd           0.000811
  total_cost_usd         0.016227
  cost_per_1k_tasks_usd  0.81

Latency distribution (s):
  0-1s ## 2
  1-2s ############### 15
  2-3s # 1
  3-4s # 1
  4-5s # 1

Cost by step: {'tool_call': 0.007901, 'answer': 0.008326}
Throughput (sequential): 32.4 tasks/minute per worker
Slowest task: 4.497s, 4 LLM calls, tools ['lookup_customer', 'search_knowledge_base', 'create_ticket']: I want to cancel my subscription and get a full refund. I si
```

Twenty queries: pricing, refunds, account lookups, an escalation, two attacks and one off-topic question. Read it top to bottom. The p50 is one point seven five seconds. The p95 is three point three four. So the unlucky one in twenty waits almost twice as long as the typical user.

Average cost is about eight hundredths of a cent per task. That's eighty-one cents per thousand tasks on gpt-4.1-mini, verify current pricing.

[SCREEN: Same output. Zoom on the histogram, then on the "Slowest task" line.]

The histogram tells the story. Fifteen of twenty tasks finish in one to two seconds. Three stragglers sit above two seconds. And the slowest task is exactly what we predicted: cancel and refund, four LLM calls, three tools. Nobody needs to guess where the tail comes from.

[SCREEN: Same output. Zoom on "Cost by step" and "Throughput".]

Now cost by step. Tool-call steps cost seventy-nine ten-thousandths of a dollar in total. Answer steps cost eighty-three. Roughly half and half. So the money isn't hiding in one step. In Lecture 10.3, you'll find where it really goes.

And throughput: thirty-two point four tasks per minute for one worker running sequentially. That's just sixty seconds divided by the average task time, so it moves whenever latency moves. Need a thousand tasks an hour? That's about seventeen a minute, so one worker covers it on paper. In production, rate limits usually decide before your code does.

[AVATAR]
One honest note about these numbers. Offline, latency comes from a simulated clock, so it's repeatable but it's not a real API latency. Run the same command with your API key, and you'll get real times and real costs. Run it three times, too, because live latency varies from run to run, and one run is a sample, not a measurement. The shape usually holds: long trajectories form the tail. Which of your own agent's tasks do you think would land there?

[SLIDE 8: Recap]
- Report p50, p95 and max, never the average
- Meter every LLM call: tokens, latency, step
- Budget in cost per 1,000 tasks

Three things to keep. Latency is a distribution, so report p50, p95 and max. Meter every LLM call so cost and latency have an address. And translate it all into cost per thousand tasks, because that's the number that gets budgets approved.

### Recap

A benchmark turns "it feels fast" into p50 1.75 s, p95 3.34 s and $0.81 per 1,000 tasks, and shows that the slowest tasks are the longest trajectories.

### Transition

A fast agent that fails one time in ten is still broken. Next, in Lecture 10.2, you'll measure failure rate and build retries, timeouts and loop detection.

### Speaker notes: common student mistakes / Q&A

- **Offline numbers.** Every latency here is simulated (0.30 s plus per-token terms per LLM call). Costs are computed from mock token counts (`len(text)//4`). Say "offline" on screen. Re-capture live (`OFFLINE=0`) before recording if you want real API latencies on screen.
- **"Why is avg_llm_calls exactly 2?"** It is rounded to two decimals from the 20 runs; FAQ answers take 2 calls, refusals take 1, account work takes 3 or 4.
- **Throughput is per worker, sequential.** Parallel workers multiply it until the provider's rate limit stops you. Do not promise a throughput number without checking your account's rate limits (verify in the provider dashboard).
- **Time to first token** is not measured by this repo (the support agent does not stream). If a student's agent streams, measure TTFT separately from total latency.
- Prices come from `config/settings.py`, checked 2026-10-01: verify current pricing before recording.

---

## Lecture 10.2 — Reliability: Failure Rate, Retry, Timeout & Loop Detection

| Field | Value |
|---|---|
| ID | 10.2 |
| Title | Reliability: Failure Rate, Retry, Timeout & Loop Detection |
| Type | Build-along |
| Target duration | 7:00 (660 spoken words; the rest is typing and output) |
| Learning objectives | 1. Measure failure rate and tool-sequence consistency by running the same inputs several times. 2. Wrap agent calls in a retry and a timeout, and explain when a retry is dangerous. 3. Detect infinite loops at runtime with a repeat counter and a step budget. |
| Prerequisites | 10.1; 7.3 (loop detector in multi-agent systems) |
| Files used | `performance/reliability.py` (`measure_reliability`, `with_retry`, `call_with_timeout`, `LoopDetector`, `detect_tool_loop`), `agents/support_agent.py` (`max_iterations=5`), `config/eval_config.yaml` (reliability thresholds), `demos/m10_reliability.py` |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Agent gpt-4.1-mini | OFFLINE=1 runs without a key

[AVATAR]
At two in the morning, your CRM times out. Your agent tries to look up a customer, gets an error, and... what? Does it retry? Does it hang forever? Does it tell the customer something made up? [PAUSE] You don't know, because you've never tested it. Let's fix that.

[SLIDE 2: By the end of this lecture]
- Measure failure rate and consistency over repeated runs
- Add retries and timeouts, and know when retries hurt
- Catch infinite loops while they happen

You'll build four reliability checks today. Failure rate and consistency, retries, timeouts, and loop detection. All four live in one small file, `performance/reliability.py`, and all four have thresholds waiting for them in `eval_config.yaml`.

[SLIDE 3: Reliability thresholds you already own]
- consistency ≥ 0.7 (same tool sequence across runs)
- max failure rate 0.1
- max 6 LLM calls per task (loop guard)
- agent loop cap: 5 iterations, then escalate

Here are the targets. At least seventy percent of inputs should follow the same tool sequence every time. At most one run in ten may fail. No task may use more than six LLM calls. And the agent itself stops after five iterations and hands over to a human. Why run the same input more than once? Because a non-deterministic agent can pass on Monday and fail on Tuesday with the exact same question.

[CODE: `performance/reliability.py`, the signature and loop of `measure_reliability`. Highlight `runs: int = 5` and the line that builds `sequences`.]

```python
def measure_reliability(agent_fn: Callable[[str], dict], inputs: list[str], runs: int = 5,
                        is_failure: Callable[[dict], bool] | None = None) -> ReliabilityReport:
    """Run each input `runs` times; count failures, loops and tool-sequence consistency."""
    is_failure = is_failure or (lambda r: not r.get("response"))
```

Check one: failure rate and consistency. `measure_reliability` runs each input five times. An exception or an empty response counts as a failure. It also records the sequence of tools the agent called. If every run of an input used the same tools in the same order, that input counts as consistent.

[CODE: `performance/reliability.py`, `with_retry` and `call_with_timeout`.]

```python
def with_retry(fn: Callable[[], Any], attempts: int = 3, backoff_s: float = 0.0,
               retry_on: tuple[type[BaseException], ...] = (Exception,)) -> tuple[Any, int]:
    """Call fn until it succeeds. Returns (result, retries_used). Re-raises after the last attempt."""
    for i in range(attempts):
        try:
            return fn(), i
        except retry_on:
            if i == attempts - 1:
                raise
            if backoff_s:
                time.sleep(backoff_s * (2**i))

def call_with_timeout(fn: Callable[[], Any], timeout_s: float) -> Any:
    """Run fn in a worker thread; raise TimeoutError if it takes longer than timeout_s."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn)
        try:
            return future.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError as exc:
            raise TimeoutError(f"agent call exceeded {timeout_s}s") from exc
```

Checks two and three. `with_retry` calls a function up to three times, with optional exponential backoff, and tells you how many retries it used. `call_with_timeout` runs the call in a worker thread and raises a clean `TimeoutError` if it takes too long. A clean error is the point. You never want a timeout to look like a tool result the agent might act on.

[SLIDE 4: When a retry hurts]
- Retrying the whole agent repeats every LLM call (cost)
- Retrying after `create_ticket` succeeded can create a duplicate ticket
- Retry read-only tools; make write tools idempotent

Here's the trap. `with_retry` retries the whole agent run. That repeats every LLM call, so it costs money. Worse, imagine the agent already created a ticket, and then a later step fails. The retry runs everything again. Now the customer has two tickets. So retry read-only work freely, like `lookup_customer`. For write tools like `create_ticket` and `send_email`, make them idempotent first, or retry the single tool call instead of the whole agent.

[CODE: `performance/reliability.py`, `LoopDetector.record`.]

```python
def record(self, action: str, detail: str = "") -> str | None:
    self.history.append((action, detail))
    if len(self.history) > self.max_steps:
        return f"step budget exceeded ({self.max_steps} steps)"
    tail = self.history[-self.max_repeats :]
    if len(tail) == self.max_repeats and len(set(tail)) == 1:
        return f"'{action}' repeated {self.max_repeats} times in a row"
    return None
```

Check four is loop detection, the sixth failure mode from Module 1. You met `LoopDetector` in Lecture 7.3. It flags two things: the same action with the same arguments three times in a row, or more than ten steps in total. `detect_tool_loop` runs it over a finished result's tool calls, so you can use it in tests as well as at runtime.

[SCREEN: Terminal. Open `demos/m10_reliability.py` for three seconds: highlight the `flaky_tool` function that raises `ConnectionError("CRM timeout")` on its first two calls. Then run the demo.]

```bash
uv run python demos/m10_reliability.py
```

[DEMO: Output after the banner (offline)]

```text
25 runs: failure rate 0%, loops 0, tool-sequence consistency 100%

Retry: succeeded after 2 retries -> Here's your account: Bob Smith, Basic plan, status active, balance $29
Timeout: agent call exceeded 0.1s
Loop detection: 'search_knowledge_base' repeated 3 times in a row
```

Five inputs, five runs each: twenty-five runs. Zero failures, zero loops, one hundred percent consistency. Offline, the mock model is scripted, so a perfect score is expected. Live, run it with your key and see your real number. Seventy percent is the bar, not a hundred.

The retry line is the CRM outage from the hook. The demo's flaky tool throws a CRM timeout twice. The third attempt works, and Bob Smith gets his answer.

The timeout fires at a tenth of a second, and the error message says exactly what happened. And the loop detector catches five identical knowledge-base searches on the third repeat, long before the step budget. Which would you rather read at two in the morning: "repeated three times in a row", or a ten-dollar bill for a loop?

[AVATAR]
Put these four checks in your test suite and your runtime. Tests tell you before release. Runtime guards protect you after release. You'll want both, because live models drift, and tools fail on days you didn't test.

[SLIDE 5: Recap]
- Run each input several times; measure failures and consistency
- Retry reads freely; make writes idempotent first
- Stop loops with a repeat count and step budget

Run every input more than once. Retry the safe things, and protect the unsafe ones. And stop loops early, with a repeat count and a step budget.

### Recap

Reliability is measured over repeated runs, protected with retries and timeouts that fail cleanly, and enforced at runtime with a loop detector.

### Transition

Your agent is reliable now. Is it affordable? In Lecture 10.3 you'll find the 80/20 of agent spend and cut it with two measured levers.

### Speaker notes: common student mistakes / Q&A

- **100% consistency offline is by construction.** The mock is scripted per input; re-capture live before recording if you want a realistic consistency number on screen. The threshold is 0.7 in `config/eval_config.yaml`.
- **Retry scope.** The demo retries the whole agent call because the flaky tool raises out of the agent. Students often copy that into production for write paths. Push them to idempotency keys or per-tool retries.
- **Where the 5-iteration cap lives:** `run_support_agent(..., max_iterations=5)`; after five LLM calls the agent replies "I apologize, but I'm having trouble processing your request. Let me escalate this to a human agent."
- **Timeout threads.** `call_with_timeout` raises after the limit, but the worker thread can keep running in the background; in production prefer the client's own timeout setting as well.

---

## Lecture 10.3 — Cost Engineering: Finding the 80/20 of Agent Spend

| Field | Value |
|---|---|
| ID | 10.3 |
| Title | Cost Engineering: Finding the 80/20 of Agent Spend |
| Type | Build-along |
| Target duration | 7:00 (727 spoken words; the rest is typing and output) |
| Learning objectives | 1. Find the fixed prompt overhead that is re-sent on every LLM call. 2. Cut it with a "prompt diet" and measure the saving. 3. Route simple questions to a cheaper model, measure the saving, and re-check quality on the golden dataset. |
| Prerequisites | 10.1; 9.3 (cost analysis of one trace) |
| Files used | `performance/cost.py` (`route_model`, `prompt_overhead`, `savings`), `performance/benchmark.py`, `demos/m09_cost_analysis.py`, `demos/m10_cost_hotspots.py`, `demos/m10_model_routing.py` |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- gpt-4.1-mini and gpt-4.1 | prices: verify current pricing

[AVATAR]
Seventy-four percent. That's how much of the input you paid for in one TechCorp trace that the customer never typed. It was the same system prompt and the same tool schemas, sent again on every single call. [PAUSE] Where else is your agent paying for words nobody reads?

[SLIDE 2: By the end of this lecture]
- Find the fixed overhead in every call
- Cut it with a prompt diet, and measure
- Route easy questions to a cheaper model, and re-check quality

Today you'll find your agent's biggest cost hotspot, then pull two levers and measure each one: a prompt diet and model routing. And after each change, you'll prove quality didn't drop. Cost cuts without a quality check are just bugs you haven't found yet.

[SCREEN: Terminal. Run the Module 9 cost analysis again.]

```bash
uv run python demos/m09_cost_analysis.py
```

[DEMO: Output after the banner (offline)]

```text
call     input  output      cost $   fixed overhead share
1          788      36    0.000373   93%
2          950      35    0.000436   77%
3         1055     101    0.000584   70%
4         1202      51    0.000562   61%
4 LLM calls, 3995 input tokens, $0.001955 (gpt-4.1-mini, verify current pricing)
System prompt + tool schemas = 736 tokens per call -> 74% of all input tokens in this trace.
```

Here's the trace from Lecture 9.3. Four LLM calls. On the first call, ninety-three percent of the input is fixed overhead. Across the whole trace, it's seventy-four percent. That's the 80/20 of agent spend: a small, fixed block of text, multiplied by every loop iteration and every customer.

[SCREEN: Terminal. Run the hotspot demo.]

```bash
uv run python demos/m10_cost_hotspots.py
```

[DEMO: Output after the banner (offline)]

```text
Fixed overhead re-sent on every call: {'system_prompt_tokens': 255, 'tool_schema_tokens': 481}

FAQ traffic, all 5 tool schemas : 6596 input tokens, $0.003107
FAQ traffic, only the KB tool    : 3285 input tokens, $0.001776
Prompt diet saves 42.8% on FAQ traffic (verify current pricing).
```

Now split that overhead. The system prompt is two hundred fifty-five tokens. The five tool schemas are four hundred eighty-one. So sixty-five percent of the overhead isn't your instructions. It's the tool definitions. Did you expect that?

[SLIDE 3: Lever 1: the prompt diet]
- A pricing question needs one tool: `search_knowledge_base`
- Sending all 5 schemas costs 481 tokens per call
- Send only the tools a request can use

Lever one: the prompt diet. A pricing question can only ever need one tool, the knowledge-base search. So why send all five schemas? The demo runs four FAQ questions twice. Once with all five tools, once with only the search tool. Input tokens drop from six thousand five hundred ninety-six to three thousand two hundred eighty-five. Cost drops forty-three percent on FAQ traffic. Verify current pricing, but the ratio holds.

[CODE: `demos/m10_cost_hotspots.py`, the one line that builds the diet tool list.]

```python
kb_only = [t for t in TOOLS if t["function"]["name"] == "search_knowledge_base"]
```

The code is one line: filter the tool list. The hard part is deciding which requests are "FAQ only". Get it wrong, and a refund request arrives at an agent that has no ticket tool. So the diet needs a classifier you trust, and that's exactly the next lever.

[CODE: `performance/cost.py`, `route_model` and the `RISKY` pattern.]

```python
CHEAP_MODEL = "gpt-4.1-mini"
STRONG_MODEL = "gpt-4.1"

RISKY = re.compile(r"@|CUST-|ticket|charged|cancel|refund after|lawyer|legal|breach|manager|human|ignore|account", re.I)


def route_model(question: str) -> str:
    """Rule-based router: FAQ-style questions go to the cheap model."""
    return STRONG_MODEL if RISKY.search(question) else CHEAP_MODEL
```

Lever two: model routing. Start from the expensive setup, gpt-4.1 for everything. Then send simple FAQ questions to gpt-4.1-mini, which costs a fifth as much per token. Verify current pricing. Anything that smells risky stays on the strong model: an email address, a customer ID, tickets, cancellations, lawyers, breaches, "ignore" instructions. It's a plain regular expression. No extra LLM call, no extra latency. Why start with rules instead of an LLM classifier? Because rules are free, testable, and easy to explain in a review.

[SCREEN: Terminal. Run the routing demo.]

```bash
uv run python demos/m10_model_routing.py
```

[DEMO: Output after the banner (offline)]

```text
setup                         cost/task  per 1k tasks
----------------------------  ---------  ------------
all gpt-4.1                   0.004057   4.06
routed (FAQ -> gpt-4.1-mini)  0.002878   2.88

8/20 queries routed to gpt-4.1-mini; saving 29.1%
Quality check with routing: 10/10 golden cases pass, averages {'Answer Correctness': 0.97, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
Offline the mock answers the same for every model, so quality is equal by construction: re-run live to verify.
```

Eight of the twenty benchmark queries go to the cheap model. Cost per thousand tasks drops from four dollars six to two dollars eighty-eight. That's a twenty-nine percent saving. You may have read claims of fifty percent. On this traffic mix it's about thirty, because twelve of the twenty queries are account work and escalations, and they stay on the strong model. Your saving depends on your mix.

[SCREEN: Same output. Zoom on the "Quality check" line, then on the last line.]

Then the step people skip: the quality check. All ten golden cases still pass. But read the last line. Offline, the mock gives the same answer whatever the model, so equal quality is guaranteed here. Live, this is the run that matters. Re-run it with your key before you ship a router.

[SLIDE 4: Two more levers to measure next]
- Prompt caching: cached input is 75% cheaper on gpt-4.1-mini (verify)
- Semantic caching: reuse answers to near-identical questions
- Measure each lever alone, then together, on the same benchmark

Two more levers, for your own experiments. Prompt caching: the provider bills a repeated prompt prefix at a discount, seventy-five percent cheaper on gpt-4.1-mini, verify current pricing. That fixed overhead is a perfect candidate. And semantic caching: reuse an answer when a new question means the same thing. Be careful with that one. A cached answer to "my refund" must never reach a different customer.

[AVATAR]
In Lab 10.1, you'll benchmark, pick one lever, re-benchmark and re-run the golden set. Measure each lever on its own first. Savings don't simply add up. Your stretch goal is a thirty percent cut with no drop in quality. Routing alone lands at twenty-nine here, so you'll need to combine levers or tune the router.

[SLIDE 5: Recap]
- Fixed overhead was 74% of input tokens
- Prompt diet: −43% on FAQ traffic
- Routing: −29%, then re-check quality live

Fixed overhead is the 80/20 of agent spend. A prompt diet cut FAQ cost by forty-three percent. Routing cut the whole benchmark by twenty-nine. And neither counts until the golden set passes with a live model.

[SLIDE 6: You can now]
- Benchmark p50, p95 and cost per 1,000 tasks
- Measure failure rate, retries, timeouts and loops
- Cut agent cost with measured levers and a quality check

You can now benchmark an agent, prove it's reliable, and cut its cost without guessing.

### Recap

Find the fixed overhead first, cut it with a prompt diet (−42.8% on FAQ traffic) and model routing (−29.1% overall), and re-run the golden set before you ship.

### Transition

Every change you just made, a new tool list, a new model, could quietly break something. Module 11 is about catching that. Next, Lecture 11.1: why agents regress.

### Speaker notes: common student mistakes / Q&A

- **Real numbers, not the curriculum's.** The curriculum's "50% cost reduction" demo is not what the code produces. Offline routing saves 29.1% (8/20 routed) and the prompt diet 42.8% on FAQ traffic (bible §12, facts 1 and 2). Say "about 30%" and "about 40%" if you round. Re-run live before recording if you want live numbers; ratios will shift.
- **Equal quality is by construction offline** (the mock ignores the model name). Do not say "routing keeps quality" without the live re-run.
- **The 65% figure** is 481 / 736 tool-schema tokens of the fixed overhead. Token counts in our build sandbox used the `len/4` fallback; on a normal machine `tiktoken` (`o200k_base`) runs and the counts change slightly. Re-capture on the recording machine.
- **Lab 10.1 target.** The curriculum sets a ≥30% saving; routing alone (29.1%) falls just short offline. That is a teaching moment, not a bug: combine levers or widen the router, then re-measure.
- **Semantic caching** has no code in the repo; it is mentioned as a lever only. Caching answers that contain account data is a privacy bug.
