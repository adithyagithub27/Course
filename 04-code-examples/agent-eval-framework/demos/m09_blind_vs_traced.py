"""Lecture 9.1 - Blind debugging vs traced debugging. The knowledge-base index
broke after a deploy; the agent politely says it can't find anything.
Without a trace you guess; with a trace you see the empty tool result.

    uv run python demos/m09_blind_vs_traced.py
"""
from _common import banner

from agents.support_agent import execute_tool
from observability.langfuse_tracing import print_trace, traced_support_agent, traced_tool
from langfuse import observe


@observe(name="tool", as_type="tool")
def broken_index_tool(name: str, arguments: dict) -> str:
    """The 16:30 deploy broke the search index: every search comes back empty."""
    if name == "search_knowledge_base":
        from langfuse import get_client

        get_client().update_current_span(name=f"tool {name}", input=arguments, output="No relevant articles found in the knowledge base.", level="WARNING")
        return "No relevant articles found in the knowledge base."
    return traced_tool(name, arguments)


banner("Lecture 9.1 - blind vs traced debugging", ["openai", "langfuse"])
q = "What is your refund policy?"
r = traced_support_agent(q, user_id="CUST-001", session_id="incident-1", tool_executor=broken_index_tool)
print("BLIND: all you have is the final output")
print(f"  Q: {q}\n  A: {r['response']}")
print("  Is it the prompt? the model? a rate limit? You can't tell.\n")
print(f"TRACED: Langfuse trace {r['trace_id']}")
print_trace(r["trace_id"])
print("\nRoot cause in one look: search_knowledge_base returned nothing; the model behaved correctly.")
print(f"(For comparison, the healthy tool returns: {execute_tool('search_knowledge_base', {'query': 'refund policy'})[:60]}...)")
