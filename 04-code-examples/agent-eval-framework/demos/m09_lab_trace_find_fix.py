"""Lab 9.1 - Trace, find, fix: five queries, two fail. Find the failing span in
each trace, fix the bug, re-run.

    uv run python demos/m09_lab_trace_find_fix.py
"""
from _common import banner

from langfuse import get_client, observe

from agents.support_agent import execute_tool
from observability.langfuse_tracing import offline_spans, traced_support_agent

BUGS = {"on": True}


@observe(name="tool", as_type="tool")
def buggy_tools(name: str, arguments: dict) -> str:
    args = dict(arguments)
    if BUGS["on"] and name == "lookup_customer":
        pass  # BUG 1: no normalisation, so "Alice@Example.com" is not found
    elif name == "lookup_customer":
        args["identifier"] = args["identifier"].strip().lower() if "@" in args["identifier"] else args["identifier"]
    if BUGS["on"] and name == "search_knowledge_base" and "api" in args.get("query", "").lower():
        result = "No relevant articles found in the knowledge base."  # BUG 2: API article missing from the index
    else:
        result = execute_tool(name, args)
    level = "WARNING" if result.startswith(("No relevant", "Customer not found")) else "DEFAULT"
    get_client().update_current_span(name=f"tool {name}", input=args, output=result, level=level)
    return result


banner("Lab 9.1 - trace, find, fix", ["openai", "langfuse"])
QUERIES = ["What are your pricing plans?", "How do I reset my password?", "What is your refund policy?",
           "Can you check my account? My email is Alice@Example.com", "What are the API rate limits for the Pro plan?"]
for phase in ("BEFORE FIX", "AFTER FIX"):
    BUGS["on"] = phase == "BEFORE FIX"
    print(f"\n--- {phase} ---")
    for q in QUERIES:
        r = traced_support_agent(q, user_id="lab-9", session_id=phase, tool_executor=buggy_tools)
        bad = [s for s in offline_spans(r["trace_id"]) if s["level"] == "WARNING"]
        status = f"FAILING span: {bad[0]['name']} -> {bad[0]['output'][:45]}" if bad else "ok"
        print(f"{q[:52]:<54} {status}")
print("\nFixes: lowercase emails before lookup_customer; re-index the API article (KB-104).")
