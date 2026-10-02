"""Lecture 2.1 - Why traditional assertions break: run the same question 10 times
and compare an exact-match assert with a semantic check.

    uv run python demos/m02_assertion_flakiness.py
"""
from _common import banner

from agents.support_agent import run_support_agent

banner("Lecture 2.1 - assertion flakiness")
q = "How long do refunds take?"
expected = "Refunds are processed within 5-7 business days."
exact = semantic = 0
for i in range(1, 11):
    a = run_support_agent(q)["response"]
    ok_exact = a == expected
    ok_sem = "5-7 business days" in a
    exact += ok_exact
    semantic += ok_sem
    print(f"run {i:>2}: exact={'PASS' if ok_exact else 'FAIL'}  semantic={'PASS' if ok_sem else 'FAIL'}  {a}")
print(f"\nassert response == expected : {exact}/10 passed (flaky, though every answer is correct)")
print(f"assert '5-7 business days' in : {semantic}/10 passed")
