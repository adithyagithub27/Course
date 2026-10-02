# Lab 10.1: Benchmark, Analyze, Optimize

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 10.1 (file `lab-09-performance-benchmark.md`) |
| **Module** | Module 10 — Performance & Reliability Testing |
| **Lectures** | 10.1–10.3 |
| **Duration** | 60 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Benchmark the TechCorp support agent on 20 queries (latency percentiles, tokens, cost per task), find the cost hotspot, apply one optimization (model routing or a prompt diet), measure the saving, and re-check quality on the golden dataset before claiming success. |
| **Reference solution** | `performance/benchmark.py`, `performance/cost.py`, `demos/m10_benchmark.py`, `demos/m10_cost_hotspots.py`, `demos/m10_model_routing.py` |
| **Verified on** | openai 2.54.0, deepeval 4.2.7 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 1.1** and **Lab 3.1**
- Lectures 10.1 and 10.3: percentiles, cost per task, the 80/20 of agent spend, model routing

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python demos/m10_benchmark.py
```

Read `performance/benchmark.py`:

- `UsageMeter` wraps the OpenAI client and records model, input and output tokens, latency and step type (`tool_call` or `answer`) for every call.
- `run_benchmark(questions, model=None, router=None)` runs each question once and returns a `BenchmarkReport` with `summary()` (p50, p95, max latency; average tokens and LLM calls; cost per task and per 1,000 tasks) and `cost_by_step()`.
- `BENCHMARK_QUERIES`: 20 realistic queries (FAQ, account work, escalation, refusals).

Prices live in `config/settings.py` (per 1M tokens, checked 2026-10-01): gpt-4.1 $2.00 input / $8.00 output; gpt-4.1-mini $0.40 / $1.60. **Verify current pricing** before you quote a dollar figure.

> **Offline latencies are simulated** (0.30 s plus per-token terms per LLM call) so the numbers are repeatable. Live latencies depend on the network and the provider's load: re-run live before you quote them.

---

## Step-by-Step Instructions

### Step 1 — Baseline on the strong model

Create `my_work/lab09_bench.py`:

```python
"""Lab 10.1 - benchmark, find the hotspot, optimise, re-check quality."""
from agents.support_agent import run_support_agent
from performance.benchmark import BENCHMARK_QUERIES, run_benchmark
from performance.cost import STRONG_MODEL, prompt_overhead, route_model, savings
from regression.regression_suite import evaluate_version

base = run_benchmark(BENCHMARK_QUERIES, model=STRONG_MODEL)
print("baseline (all gpt-4.1):", base.summary())
print("cost by step:", base.cost_by_step())
print("fixed overhead per call:", prompt_overhead())
```

```bash
uv run python -m my_work.lab09_bench
```

Record p50, p95, average LLM calls and cost per 1,000 tasks.

### Step 2 — Find the hotspot

`prompt_overhead()` shows what is re-sent on **every** LLM call before the customer says anything: the system prompt (255 tokens) and the five tool schemas (481 tokens). With about two LLM calls per task, that fixed overhead dominates input cost. Confirm with the trace-level view from Module 9:

```bash
uv run python demos/m09_cost_analysis.py     # fixed overhead = 74% of input tokens in one trace
```

### Step 3 — Optimize: route FAQ traffic to the mini model

`performance/cost.py` has a rule-based router: questions that touch accounts, tickets, billing, legal threats or injections go to `gpt-4.1`; FAQ-style questions go to `gpt-4.1-mini`. Add to your script:

```python
routed = run_benchmark(BENCHMARK_QUERIES, router=route_model)
b, a = base.summary()["avg_cost_usd"], routed.summary()["avg_cost_usd"]
print(f"routed: ${a:.6f}/task vs ${b:.6f}/task -> saving {savings(b, a)}%")
```

### Step 4 — Re-check quality before claiming the saving

A cheaper agent that answers worse is not an optimization. Run the golden dataset with the router in place:

```python
quality = evaluate_version(lambda q: run_support_agent(q, model=route_model(q)), version="routed")
print(f"quality re-check: {quality['passed']}/{quality['total']} pass, averages {quality['averages']}")
```

**Important:** offline, the mock LLM answers the same way whatever the model name, so quality is equal by construction. The re-check is only meaningful **live** (`OFFLINE=0` with a key; a few cents, verify current pricing). Write that caveat into your results.

### Step 5 — Try the second lever: a prompt diet

```bash
uv run python demos/m10_cost_hotspots.py
```

Sending only the knowledge-base tool schema to FAQ traffic cuts its input tokens by about 40%. Which requests can never use a diet like this, and how would you route them?

### Step 6 — Reliability check

```bash
uv run python demos/m10_reliability.py
```

Failure rate, tool-sequence consistency over 25 runs, a retry, a timeout and a loop detection. Which of the five quality dimensions do these numbers belong to? (Reliability: latency and cost sit there too.)

---

## Expected Output

Step 1–4 (offline):

```
baseline (all gpt-4.1): {'model': 'gpt-4.1', 'tasks': 20, 'latency_p50_s': 1.75, 'latency_p95_s': 3.34, 'latency_max_s': 4.5, 'avg_tokens': 1785.2, 'avg_llm_calls': 2, 'avg_cost_usd': 0.004057, 'total_cost_usd': 0.081134, 'cost_per_1k_tasks_usd': 4.06}
cost by step: {'tool_call': 0.039504, 'answer': 0.04163}
fixed overhead per call: {'system_prompt_tokens': 255, 'tool_schema_tokens': 481}
routed: $0.002878/task vs $0.004057/task -> saving 29.1%
quality re-check: 10/10 pass, averages {'Answer Correctness': 0.97, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
```

Step 5:

```
Fixed overhead re-sent on every call: {'system_prompt_tokens': 255, 'tool_schema_tokens': 481}
FAQ traffic, all 5 tool schemas : 6596 input tokens, $0.003107
FAQ traffic, only the KB tool    : 3285 input tokens, $0.001776
Prompt diet saves 42.8% on FAQ traffic (verify current pricing).
```

Token counts depend on the tokenizer: on a machine where tiktoken's `o200k_base` file is available they come from the real tokenizer; otherwise the course falls back to `len(text) / 4` and says so. Re-run on your machine and use your numbers.

---

## Verification Checklist

- [ ] Baseline recorded: p50, p95, LLM calls per task, cost per 1,000 tasks
- [ ] Hotspot identified with a number (fixed overhead tokens per call)
- [ ] One optimization applied and the saving measured with the same benchmark
- [ ] Quality re-checked on the golden dataset, with the offline caveat written down
- [ ] Every dollar figure in your notes says "verify current pricing"

---

## Common Pitfalls

1. **Comparing different query sets.** Before and after must run the same 20 queries, or the saving is meaningless.
2. **Averages hide tails.** Report p95, not just the mean. One 4-call trajectory is the slowest task in this benchmark.
3. **Claiming quality is unchanged from offline runs.** The mock ignores the model name. Only a live re-check proves the mini model is good enough for the routed traffic.
4. **Hard-coding prices.** Read them from `config/settings.py` and update them in one place.

---

## Extension Challenge

1. Write a performance gate: fail if p95 > 10 s or cost per task > $0.01 (the Reliability limits in `config/eval_config.yaml`). The capstone gate (`capstone/platform.py`) does exactly this.
2. Improve the router: send "What is the API rate limit on Basic?" to the mini model but keep "Check my account please, CUST-002" on the strong one. Measure the new saving.
3. Live only: enable prompt caching for the fixed prefix and compare `cached_tokens` in the usage data (cached input is cheaper; verify current pricing).
