# Lab 09: Performance Benchmarking and Cost Optimization

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 10 — Performance Testing                              |
| **Duration**       | 60 minutes                                                   |
| **Difficulty**     | Intermediate                                                 |
| **Learning Objective** | Benchmark an agent's latency, token cost, and LLM call count, identify the most expensive query type, apply one optimization to achieve a 50%+ cost reduction, and compare before vs. after results. |

---

## Prerequisites

- Completed **Lab 01** (can run the support agent)
- Understanding of OpenAI token pricing
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Review the benchmark module

```bash
cat performance/benchmark.py
```

Key functions:
- `benchmark_latency()` — measures end-to-end response time
- `benchmark_token_cost()` — estimates cost per task
- `benchmark_llm_calls()` — counts LLM invocations per task
- `run_full_benchmark()` — runs all three benchmarks

### 2. Create workspace

```bash
mkdir -p reports/results
```

---

## Step-by-Step Instructions

### Step 1 — Define 10 diverse test inputs

Create `lab09_benchmark.py`:

```python
"""
Lab 09 — Performance Benchmark
Run: python lab09_benchmark.py
"""

import json
import time
from performance.benchmark import (
    benchmark_latency,
    benchmark_token_cost,
    benchmark_llm_calls,
    BenchmarkResult,
)
from agents.support_agent import run_support_agent


# ── 10 Test Inputs Across Different Categories ───────────────────
TEST_INPUTS = [
    # Simple KB lookups (low cost expected)
    "What are your pricing plans?",
    "What is your refund policy?",
    "How do I reset my password?",

    # Account operations (tool calling = more LLM rounds)
    "Look up my account. My email is alice@example.com",
    "Look up customer CUST-001",

    # Complex multi-step tasks (highest cost expected)
    "I'm CUST-001. Create a high priority ticket for double billing.",
    "I'm CUST-001. I was charged twice. Create a ticket and email me.",

    # Escalation scenarios
    "I'm furious. Your product destroyed my data. I need a manager.",

    # Edge cases
    "Can your product integrate with SAP?",
    "Tell me everything about your enterprise features.",
]
```

### Step 2 — Run the baseline benchmark

Add the benchmarking code:

```python
def run_baseline_benchmark() -> dict:
    """Run the complete baseline benchmark."""
    print("=" * 60)
    print("BASELINE BENCHMARK — 10 Test Inputs")
    print("=" * 60)

    # Latency benchmark (1 run per input for speed)
    print("\nBenchmarking latency...")
    latency = benchmark_latency(run_support_agent, TEST_INPUTS, runs_per_input=1)

    # Token cost benchmark
    print("Benchmarking token cost...")
    cost = benchmark_token_cost(run_support_agent, TEST_INPUTS)

    # LLM calls benchmark
    print("Benchmarking LLM call count...")
    llm_calls = benchmark_llm_calls(run_support_agent, TEST_INPUTS)

    results = {
        "latency": latency.summary(),
        "cost": cost.summary(),
        "llm_calls": llm_calls.summary(),
    }

    # Print summary
    print("\n" + "-" * 60)
    print("LATENCY (seconds per task)")
    print(f"  Mean:    {results['latency']['mean']:.3f}s")
    print(f"  Median:  {results['latency']['median']:.3f}s")
    print(f"  P95:     {results['latency']['p95']:.3f}s")
    print(f"  Min:     {results['latency']['min']:.3f}s")
    print(f"  Max:     {results['latency']['max']:.3f}s")

    print("\nTOKEN COST (USD per task)")
    print(f"  Mean:    ${results['cost']['mean']:.6f}")
    print(f"  Median:  ${results['cost']['median']:.6f}")
    print(f"  Max:     ${results['cost']['max']:.6f}")
    print(f"  Total:   ${sum(cost.values):.6f}")

    print("\nLLM CALLS (per task)")
    print(f"  Mean:    {results['llm_calls']['mean']:.1f}")
    print(f"  Max:     {results['llm_calls']['max']:.0f}")

    return results
```

### Step 3 — Identify the most expensive query type

Add per-query analysis:

```python
def analyze_per_query_cost() -> list[dict]:
    """Run each query individually and rank by cost."""
    print("\n" + "=" * 60)
    print("PER-QUERY COST ANALYSIS")
    print("=" * 60)

    query_costs = []
    for i, query in enumerate(TEST_INPUTS):
        start = time.perf_counter()
        result = run_support_agent(query)
        elapsed = time.perf_counter() - start

        query_costs.append({
            "index": i + 1,
            "query": query[:50],
            "tokens": result["total_tokens"],
            "llm_calls": result["llm_calls"],
            "tools": [tc["tool"] for tc in result["tool_calls"]],
            "latency_s": round(elapsed, 3),
            "est_cost_usd": round(result["total_tokens"] * 0.4 * 0.15e-6
                                  + result["total_tokens"] * 0.6 * 0.60e-6, 6),
        })

    # Sort by cost (descending)
    query_costs.sort(key=lambda x: x["est_cost_usd"], reverse=True)

    print(f"\n{'#':>3} {'Tokens':>7} {'LLM':>4} {'Cost':>10} {'Latency':>8} Query")
    print("-" * 75)
    for qc in query_costs:
        print(f"{qc['index']:>3} {qc['tokens']:>7} {qc['llm_calls']:>4} "
              f"${qc['est_cost_usd']:>9.6f} {qc['latency_s']:>7.3f}s "
              f"{qc['query']}")

    most_expensive = query_costs[0]
    print(f"\nMOST EXPENSIVE: Query {most_expensive['index']}")
    print(f"  \"{most_expensive['query']}\"")
    print(f"  Tokens: {most_expensive['tokens']}, "
          f"LLM calls: {most_expensive['llm_calls']}, "
          f"Cost: ${most_expensive['est_cost_usd']:.6f}")

    return query_costs
```

### Step 4 — Apply an optimization

Choose one optimization strategy. Here are three options:

**Option A: Reduce system prompt length**

```python
OPTIMIZED_SYSTEM_PROMPT = """You are TechCorp's support agent.
Answer using the knowledge base. Look up accounts when asked.
Create tickets for unresolved issues. Escalate complex cases.
Never share one customer's data with another. Be concise."""
```

**Option B: Use response caching for repeated queries**

```python
from functools import lru_cache
import hashlib

_cache = {}

def run_support_agent_cached(user_message: str) -> dict:
    """Cached version — returns stored result for identical queries."""
    cache_key = hashlib.md5(user_message.encode()).hexdigest()
    if cache_key in _cache:
        return _cache[cache_key]
    result = run_support_agent(user_message)
    _cache[cache_key] = result
    return result
```

**Option C: Reduce max_tokens to limit output length**

```python
import os
from agents.support_agent import run_support_agent as _original_run

def run_support_agent_lean(user_message: str) -> dict:
    """Run with reduced max_tokens and shorter system prompt."""
    # Temporarily set a shorter system prompt
    import agents.support_agent as sa
    original_prompt = sa.SYSTEM_PROMPT
    sa.SYSTEM_PROMPT = (
        "You are TechCorp's support agent. Be concise. "
        "Use tools when needed. Never share customer data."
    )
    result = _original_run(user_message)
    sa.SYSTEM_PROMPT = original_prompt
    return result
```

### Step 5 — Re-benchmark with the optimization

```python
def run_optimized_benchmark(optimized_fn) -> dict:
    """Run the benchmark with the optimized agent."""
    print("\n" + "=" * 60)
    print("OPTIMIZED BENCHMARK")
    print("=" * 60)

    latency = benchmark_latency(optimized_fn, TEST_INPUTS, runs_per_input=1)
    cost = benchmark_token_cost(optimized_fn, TEST_INPUTS)
    llm_calls = benchmark_llm_calls(optimized_fn, TEST_INPUTS)

    return {
        "latency": latency.summary(),
        "cost": cost.summary(),
        "llm_calls": llm_calls.summary(),
    }
```

### Step 6 — Compare before vs. after

```python
def compare_results(baseline: dict, optimized: dict) -> None:
    """Print a before vs. after comparison."""
    print("\n" + "=" * 60)
    print("BEFORE vs. AFTER COMPARISON")
    print("=" * 60)

    metrics = [
        ("Latency (mean)", "latency", "mean", "s"),
        ("Latency (p95)", "latency", "p95", "s"),
        ("Cost (mean)", "cost", "mean", "USD"),
        ("Cost (max)", "cost", "max", "USD"),
        ("LLM calls (mean)", "llm_calls", "mean", ""),
    ]

    print(f"\n{'Metric':<25} {'Before':>12} {'After':>12} {'Change':>12}")
    print("-" * 65)

    for label, category, stat, unit in metrics:
        before = baseline[category][stat]
        after = optimized[category][stat]
        if before > 0:
            change_pct = ((after - before) / before) * 100
        else:
            change_pct = 0
        direction = "better" if change_pct < 0 else "worse"
        print(f"{label:<25} {before:>12.4f} {after:>12.4f} "
              f"{change_pct:>+10.1f}% ({direction})")

    # Cost reduction summary
    before_cost = baseline["cost"]["mean"]
    after_cost = optimized["cost"]["mean"]
    if before_cost > 0:
        reduction = ((before_cost - after_cost) / before_cost) * 100
        target_met = "YES" if reduction >= 50 else "NO"
        print(f"\nCost reduction: {reduction:.1f}%")
        print(f"50% target met: {target_met}")


# ── Main Execution ────────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Baseline
    baseline = run_baseline_benchmark()

    # Step 2: Per-query analysis
    query_costs = analyze_per_query_cost()

    # Step 3: Optimized run (using Option A: shorter prompt)
    import agents.support_agent as sa
    original_prompt = sa.SYSTEM_PROMPT
    sa.SYSTEM_PROMPT = (
        "You are TechCorp's support agent. Be concise. "
        "Use the knowledge base for product questions. "
        "Look up accounts when asked. Create tickets for issues. "
        "Escalate complex cases. Never share customer data."
    )
    optimized = run_optimized_benchmark(run_support_agent)
    sa.SYSTEM_PROMPT = original_prompt

    # Step 4: Compare
    compare_results(baseline, optimized)

    # Step 5: Save results
    report = {
        "baseline": baseline,
        "optimized": optimized,
        "query_costs": query_costs,
    }
    with open("reports/results/benchmark_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nResults saved to reports/results/benchmark_results.json")
```

### Step 7 — Run the complete benchmark

```bash
python lab09_benchmark.py
```

---

## Expected Output

```
============================================================
BASELINE BENCHMARK — 10 Test Inputs
============================================================

Benchmarking latency...
Benchmarking token cost...
Benchmarking LLM call count...

------------------------------------------------------------
LATENCY (seconds per task)
  Mean:    2.341s
  Median:  2.150s
  P95:     3.890s

TOKEN COST (USD per task)
  Mean:    $0.000185
  Max:     $0.000312

LLM CALLS (per task)
  Mean:    1.8
  Max:     3

============================================================
PER-QUERY COST ANALYSIS
============================================================

  # Tokens  LLM  Cost       Latency  Query
---------------------------------------------------------------------------
  7     823    3  $0.000312   3.890s  I'm CUST-001. I was charged twice...
  6     645    2  $0.000245   2.650s  I'm CUST-001. Create a high prior...
  ...

============================================================
BEFORE vs. AFTER COMPARISON
============================================================

Metric                      Before       After       Change
-----------------------------------------------------------------
Latency (mean)              2.3410       1.8520      -20.9% (better)
Cost (mean)                 0.0002       0.0001      -52.3% (better)
LLM calls (mean)            1.8000       1.6000      -11.1% (better)

Cost reduction: 52.3%
50% target met: YES
```

---

## Verification Checklist

- [ ] 10 diverse test inputs cover all query categories
- [ ] Baseline benchmark completed with latency, cost, and LLM call metrics
- [ ] Per-query cost analysis identifies the most expensive query type
- [ ] At least one optimization strategy was implemented
- [ ] Optimized benchmark shows measurable improvement
- [ ] Before vs. after comparison table is generated
- [ ] Results are saved to `reports/results/benchmark_results.json`
- [ ] You can explain **why** the most expensive query costs more (more tool calls, more LLM rounds, longer context)

---

## Common Pitfalls

1. **Benchmarking with `runs_per_input=3` takes too long** — The default benchmark runs each input 3 times for latency measurement. For this lab, use `runs_per_input=1` to save time and API costs. In production, use 3+ runs for statistical significance.

2. **Token cost estimates are approximate** — The benchmark uses a 40/60 input/output split estimate. Actual costs depend on exact prompt and completion lengths. For precise cost tracking, use the Langfuse integration from Lab 08.

3. **Optimizing the wrong thing** — If latency is dominated by network round-trips (not token generation), reducing prompt length won't help. Check the per-query breakdown to find the real bottleneck before optimizing.

---

## Extension Challenge

**Advanced:** Implement and benchmark **all three** optimization strategies (shorter prompt, caching, reduced output), then combine the best two. Create a comparison table:

| Strategy              | Cost Reduction | Latency Reduction | Quality Impact |
| --------------------- | -------------- | ----------------- | -------------- |
| Shorter prompt        | [X]%           | [X]%              | [assess]       |
| Response caching      | [X]%           | [X]%              | [assess]       |
| Reduced max_tokens    | [X]%           | [X]%              | [assess]       |
| Best two combined     | [X]%           | [X]%              | [assess]       |

For each strategy, also run the DeepEval `AnswerRelevancyMetric` to verify that quality has not regressed. A 50% cost reduction is worthless if quality drops below the threshold.
