"""
Performance Benchmarking — Latency, cost, and throughput measurement.

Demonstrates how to benchmark AI agent performance characteristics.
Used in Module 10.
"""

import time
import statistics
from dataclasses import dataclass, field


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark run."""
    metric: str
    runs: int
    values: list[float] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.mean(self.values) if self.values else 0

    @property
    def median(self) -> float:
        return statistics.median(self.values) if self.values else 0

    @property
    def p95(self) -> float:
        if not self.values:
            return 0
        sorted_vals = sorted(self.values)
        idx = int(len(sorted_vals) * 0.95)
        return sorted_vals[min(idx, len(sorted_vals) - 1)]

    @property
    def std_dev(self) -> float:
        return statistics.stdev(self.values) if len(self.values) > 1 else 0

    def summary(self) -> dict:
        return {
            "metric": self.metric,
            "runs": self.runs,
            "mean": round(self.mean, 4),
            "median": round(self.median, 4),
            "p95": round(self.p95, 4),
            "std_dev": round(self.std_dev, 4),
            "min": round(min(self.values), 4) if self.values else 0,
            "max": round(max(self.values), 4) if self.values else 0,
        }


# Token cost rates (as of 2026 — update as needed)
TOKEN_COSTS = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
}


def benchmark_latency(agent_fn, test_inputs: list[str], runs_per_input: int = 3) -> BenchmarkResult:
    """
    Benchmark end-to-end latency of an agent.

    Args:
        agent_fn: Callable that takes a string and returns a dict
        test_inputs: List of test messages
        runs_per_input: Number of times to run each input
    """
    result = BenchmarkResult(metric="latency_seconds", runs=len(test_inputs) * runs_per_input)

    for input_text in test_inputs:
        for _ in range(runs_per_input):
            start = time.perf_counter()
            agent_fn(input_text)
            elapsed = time.perf_counter() - start
            result.values.append(elapsed)

    return result


def benchmark_token_cost(
    agent_fn,
    test_inputs: list[str],
    model: str = "gpt-4o-mini",
) -> BenchmarkResult:
    """
    Benchmark token consumption and cost per task.

    Returns cost in USD per task.
    """
    result = BenchmarkResult(metric="cost_per_task_usd", runs=len(test_inputs))
    rates = TOKEN_COSTS.get(model, TOKEN_COSTS["gpt-4o-mini"])

    for input_text in test_inputs:
        output = agent_fn(input_text)
        tokens = output.get("total_tokens", 0)
        # Approximate split: 40% input, 60% output
        est_cost = tokens * 0.4 * rates["input"] + tokens * 0.6 * rates["output"]
        result.values.append(est_cost)

    return result


def benchmark_llm_calls(agent_fn, test_inputs: list[str]) -> BenchmarkResult:
    """Benchmark number of LLM invocations per task."""
    result = BenchmarkResult(metric="llm_calls_per_task", runs=len(test_inputs))

    for input_text in test_inputs:
        output = agent_fn(input_text)
        result.values.append(output.get("llm_calls", 0))

    return result


def run_full_benchmark(
    agent_fn,
    test_inputs: list[str],
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Run the complete performance benchmark suite.

    Returns a dict with latency, cost, and LLM call benchmarks.
    """
    return {
        "latency": benchmark_latency(agent_fn, test_inputs).summary(),
        "cost": benchmark_token_cost(agent_fn, test_inputs, model).summary(),
        "llm_calls": benchmark_llm_calls(agent_fn, test_inputs).summary(),
    }


if __name__ == "__main__":
    from agents.support_agent import run_support_agent

    test_cases = [
        "What are your pricing plans?",
        "How do I reset my password?",
        "What is your refund policy?",
    ]

    print("Running performance benchmark...")
    results = run_full_benchmark(run_support_agent, test_cases)

    for category, data in results.items():
        print(f"\n{category.upper()}:")
        for k, v in data.items():
            print(f"  {k}: {v}")
