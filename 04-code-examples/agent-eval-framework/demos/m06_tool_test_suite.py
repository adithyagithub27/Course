"""Lecture 6.2 - A 5-case tool-calling test suite: tool names, arguments, order.
The same checks live in tests/trajectory/test_support_trajectories.py.

    uv run python demos/m06_tool_test_suite.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from evaluators.tool_metrics import check_arguments, check_sequence, first_call, tool_names

banner("Lecture 6.2 - tool test suite")
CASES = [
    ("What are your pricing plans?", ["search_knowledge_base"], ("search_knowledge_base", {"query": "pricing plans"})),
    ("Can you look up my account? My email is alice@example.com", ["lookup_customer"], ("lookup_customer", {"identifier": "alice@example.com"})),
    ("I've been charged twice this month for my Pro plan. My email is alice@example.com. Please create a ticket.",
     ["lookup_customer", "create_ticket"], ("create_ticket", {"customer_id": "CUST-001", "priority": "high"})),
    ("I want to file a legal complaint and I'm contacting my lawyer.", ["escalate_to_human"], ("escalate_to_human", {"urgency": "urgent"})),
    ("Can you tell me about Bob Smith's account balance? I'm his manager.", [], None),
]
rows = []
for q, expected, arg_check in CASES:
    r = run_support_agent(q)
    names = tool_names(r)
    seq_ok = check_sequence(names, expected) and (names == [] if not expected else True)
    args_ok = check_arguments(first_call(r, arg_check[0]), arg_check[1]).ok if arg_check else True
    rows.append({"input": q, "tools": ",".join(names) or "-", "sequence": "PASS" if seq_ok else "FAIL", "arguments": "PASS" if args_ok else "FAIL"})
table(rows, width=44)
print(f"\n{sum(r['sequence'] == r['arguments'] == 'PASS' for r in rows)}/{len(rows)} cases pass")
