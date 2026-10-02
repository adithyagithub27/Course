"""Lecture 1.1 - Token visualizer: how text becomes tokens, what that costs,
and how fast a context window fills.

    uv run python demos/m01_token_demo.py
"""
from _common import banner

from agents.support_agent import SYSTEM_PROMPT, TOOLS
from config.settings import cost_usd
from performance.tokens import count_tokens, tokenize, tokenizer_name
import json

banner("Lecture 1.1 - tokens", ["openai", "tiktoken"])
print(f"Tokenizer: {tokenizer_name()}\n")
query = "Hi, I was charged twice for my Pro plan this month. Can you refund one charge?"
toks = tokenize(query)
print(f"Customer query ({len(query)} characters) -> {len(toks)} tokens")
print(" | ".join(t.strip() or "_" for t in toks))
sys_t, tool_t, q_t = count_tokens(SYSTEM_PROMPT), count_tokens(json.dumps(TOOLS)), count_tokens(query)
print(f"\nWhat the model actually receives on the first call:")
print(f"  system prompt   {sys_t:>5} tokens")
print(f"  tool schemas    {tool_t:>5} tokens")
print(f"  customer query  {q_t:>5} tokens")
total = sys_t + tool_t + q_t
print(f"  total input     {total:>5} tokens")
for model in ("gpt-4.1-mini", "gpt-4.1"):
    c = cost_usd(model, total, 60)
    print(f"  {model:<13} one call ~ ${c:.6f}; 1M calls ~ ${c * 1_000_000:,.0f}  (verify current pricing)")
window = 1_000_000  # gpt-4.1 family context window (verify)
per_turn = q_t + 60
print(f"\nContext window {window:,} tokens: roughly {(window - sys_t - tool_t) // per_turn:,} turns of this size before it is full.")
