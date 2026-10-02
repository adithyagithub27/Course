"""Lecture 1.2 - Agent vs chatbot: the same question to a bare LLM call and to
the TechCorp agent with tools, showing the agent's step-by-step trace.

    uv run python demos/m01_agent_vs_chatbot.py
"""
from _common import banner

from agents.llm import get_client
from agents.support_agent import run_support_agent
from config.settings import agent_model

banner("Lecture 1.2 - agent vs chatbot")
q = "I've been charged twice this month for my Pro plan. My email is alice@example.com. Please create a ticket."
chat = get_client().chat.completions.create(model=agent_model(), messages=[{"role": "user", "content": q}])
print("CHATBOT (one LLM call, no tools):")
print(f"  {chat.choices[0].message.content}\n")
r = run_support_agent(q)
print("AGENT (LLM + tools in a loop):")
for i, t in enumerate(r["tool_calls"], 1):
    print(f"  step {i}: {t['tool']}({t['arguments'] if t['tool'] != 'create_ticket' else {k: t['arguments'][k] for k in ('customer_id', 'priority')}})")
    print(f"          -> {t['result'][:80]}")
print(f"  final : {r['response']}")
print(f"\n{r['llm_calls']} LLM calls, {len(r['tool_calls'])} tool calls, {r['total_tokens']} tokens")
