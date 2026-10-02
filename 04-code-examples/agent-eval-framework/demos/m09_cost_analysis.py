"""Lecture 9.3 / 10.3 - Cost analysis from a trace: where do the tokens go?
Most input tokens are the same system prompt and tool schemas re-sent on every
LLM call of the loop.

    uv run python demos/m09_cost_analysis.py
"""
from _common import banner

import json

from agents.support_agent import SYSTEM_PROMPT, TOOLS
from config.settings import cost_usd
from observability.langfuse_tracing import offline_spans, traced_support_agent
from performance.tokens import count_tokens

banner("Lecture 9.3 - cost analysis", ["openai", "langfuse"])
q = "I want to cancel my subscription and get a full refund. I signed up 3 weeks ago. My email is alice@example.com."
r = traced_support_agent(q, user_id="CUST-001", session_id="cost-demo")
gens = [s for s in offline_spans(r["trace_id"]) if s["type"] == "generation"]
overhead = count_tokens(SYSTEM_PROMPT) + count_tokens(json.dumps(TOOLS))
total_in = total_cost = fixed_in = 0
print(f"{'call':<6}{'input':>8}{'output':>8}{'cost $':>12}   fixed overhead share")
for i, g in enumerate(gens, 1):
    u = json.loads(g["usage"])
    c = cost_usd("gpt-4.1-mini", u["input"], u["output"])
    total_in += u["input"]
    total_cost += c
    fixed_in += min(overhead, u["input"])
    print(f"{i:<6}{u['input']:>8}{u['output']:>8}{c:>12.6f}   {min(overhead, u['input']) / u['input']:.0%}")
print(f"\n{len(gens)} LLM calls, {total_in} input tokens, ${total_cost:.6f} (gpt-4.1-mini, verify current pricing)")
print(f"System prompt + tool schemas = {overhead} tokens per call -> {fixed_in / total_in:.0%} of all input tokens in this trace.")
print("Levers: fewer loop iterations, smaller tool schemas, prompt caching (cached input is 75% cheaper on gpt-4.1-mini; verify).")
