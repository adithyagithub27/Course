"""Lecture 10.3 - Cost hotspots: the fixed prompt overhead, and a 'prompt diet'
(send only the tools a question needs).

    uv run python demos/m10_cost_hotspots.py
"""
from _common import banner

from agents.support_agent import TOOLS, run_support_agent
from config.settings import cost_usd
from performance.benchmark import UsageMeter
from performance.cost import prompt_overhead, savings

banner("Lecture 10.3 - cost hotspots", ["openai"])
print(f"Fixed overhead re-sent on every call: {prompt_overhead()}")
faq = ["What are your pricing plans?", "What is your refund policy?", "How do I reset my password?", "What are the API rate limits for the Pro plan?"]
kb_only = [t for t in TOOLS if t["function"]["name"] == "search_knowledge_base"]


def run(tools):
    meter = UsageMeter()
    for q in faq:
        run_support_agent(q, client=meter, tools=tools)
    ins = sum(c.input_tokens for c in meter.calls)
    cost = sum(cost_usd("gpt-4.1-mini", c.input_tokens, c.output_tokens) for c in meter.calls)
    return ins, cost


a_in, a_cost = run(TOOLS)
b_in, b_cost = run(kb_only)
print(f"\nFAQ traffic, all 5 tool schemas : {a_in} input tokens, ${a_cost:.6f}")
print(f"FAQ traffic, only the KB tool    : {b_in} input tokens, ${b_cost:.6f}")
print(f"Prompt diet saves {savings(a_cost, b_cost)}% on FAQ traffic (verify current pricing).")
