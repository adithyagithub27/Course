# Demo 38 — Benchmarking Latency and Cost

**Used in:** Lecture 10.1 (Latency, Token Cost & Throughput Benchmarking); Lab 10.1
**Lecture type:** Teach + demo
**Duration:** ~2 minutes of screen recording
**Purpose:** Benchmark 20 queries: p50/p95 latency, tokens, cost per task and per 1,000 tasks, cost by step, throughput.
**Demo file(s):** `demos/m10_benchmark.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m10_benchmark.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Summary (45 s)

p50 1.75 s, p95 3.34 s (simulated), $0.81 per 1,000 tasks on gpt-4.1-mini (verify current pricing).

### Scene 2: Distribution (30 s)

The histogram; the slowest task is the 4-call cancel-and-refund trajectory.

### Scene 3: Where cost goes (30 s)

Cost by step and throughput (32.4 tasks/minute per sequential worker).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m10_benchmark.py
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

## Verify Before Recording

- [ ] Latency is simulated offline: say so on screen
- [ ] TTFT is not measured (the agent doesn't stream)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Amber on p95, teal on p50
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
