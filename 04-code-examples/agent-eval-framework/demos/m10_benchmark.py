"""Lecture 10.1 / Lab 10.1 - Benchmark: 20 queries, latency distribution,
cost by step, throughput. Offline latencies are SIMULATED by the mock clock.

    uv run python demos/m10_benchmark.py
"""
from _common import banner

from performance.benchmark import BENCHMARK_QUERIES, run_benchmark

banner("Lecture 10.1 - benchmark suite", ["openai"])
rep = run_benchmark(BENCHMARK_QUERIES, model="gpt-4.1-mini")
s = rep.summary()
for k, v in s.items():
    print(f"  {k:<22} {v}")
print("\nLatency distribution (s):")
lat = sorted(rep.latencies())
for lo in (0, 1, 2, 3, 4):
    n = sum(lo <= x < lo + 1 for x in lat)
    print(f"  {lo}-{lo + 1}s {'#' * n} {n}")
print(f"\nCost by step: {rep.cost_by_step()}")
print(f"Throughput (sequential): {60 / (sum(lat) / len(lat)):.1f} tasks/minute per worker")
slow = max(rep.runs, key=lambda r: r["latency_s"])
print(f"Slowest task: {slow['latency_s']}s, {slow['llm_calls']} LLM calls, tools {slow['tools']}: {slow['question'][:60]}")
