"""Lecture 10.2 - Reliability: failure rate, consistency, retries, timeouts,
loop detection.

    uv run python demos/m10_reliability.py
"""
from _common import banner

import time

from agents.support_agent import execute_tool, run_support_agent
from performance.reliability import call_with_timeout, detect_tool_loop, measure_reliability, with_retry

banner("Lecture 10.2 - reliability", ["openai"])
inputs = ["What are your pricing plans?", "How long do refunds take?", "Check my account please, CUST-002",
          "I'd like to speak to a human, please.", "What is the meaning of life?"]
rep = measure_reliability(run_support_agent, inputs, runs=5)
print(f"{rep.runs} runs: failure rate {rep.failure_rate:.0%}, loops {rep.loops}, tool-sequence consistency {rep.consistency:.0%}")

calls = {"n": 0}


def flaky_tool(name, args):
    calls["n"] += 1
    if name == "lookup_customer" and calls["n"] < 3:
        raise ConnectionError("CRM timeout")
    return execute_tool(name, args)


result, retries = with_retry(lambda: run_support_agent("Check my account please, CUST-002", tool_executor=flaky_tool), attempts=3)
print(f"\nRetry: succeeded after {retries} retries -> {result['response'][:70]}")
try:
    call_with_timeout(lambda: time.sleep(0.5), timeout_s=0.1)
except TimeoutError as e:
    print(f"Timeout: {e}")
looping = [{"tool": "search_knowledge_base", "arguments": {"query": "reseller refund"}}] * 5
print(f"Loop detection: {detect_tool_loop(looping)}")
