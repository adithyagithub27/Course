"""Lecture 10.3 - 50% cost reduction with model routing: cheap model for FAQ,
strong model for risky work, with quality re-checked on the golden set.

    uv run python demos/m10_model_routing.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite
from evaluators.golden import load
from performance.benchmark import BENCHMARK_QUERIES, run_benchmark
from performance.cost import route_model, savings

banner("Lecture 10.3 - model routing", ["openai"])
before = run_benchmark(BENCHMARK_QUERIES, model="gpt-4.1").summary()
after = run_benchmark(BENCHMARK_QUERIES, router=route_model).summary()
table([{"setup": "all gpt-4.1", "cost/task": before["avg_cost_usd"], "per 1k tasks": before["cost_per_1k_tasks_usd"]},
       {"setup": "routed (FAQ -> gpt-4.1-mini)", "cost/task": after["avg_cost_usd"], "per 1k tasks": after["cost_per_1k_tasks_usd"]}])
routed = [q for q in BENCHMARK_QUERIES if route_model(q) == "gpt-4.1-mini"]
print(f"\n{len(routed)}/{len(BENCHMARK_QUERIES)} queries routed to gpt-4.1-mini; saving {savings(before['avg_cost_usd'], after['avg_cost_usd'])}%")
q = run_suite(load("golden_support"), lambda m: run_support_agent(m, model=route_model(m)), default_metrics_for)
print(f"Quality check with routing: {q['passed']}/{q['total']} golden cases pass, averages {q['averages']}")
print("Offline the mock answers the same for every model, so quality is equal by construction: re-run live to verify.")
