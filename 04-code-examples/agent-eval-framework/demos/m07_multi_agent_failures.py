"""Lecture 7.1 - Multi-agent failure montage: an infinite delegation loop, state
corruption in a message, and a failure cascade from an empty research step.

    uv run python demos/m07_multi_agent_failures.py
"""
from _common import banner

from agents.multi_agent import FailureInjection, run_multi_agent

banner("Lecture 7.1 - what can go wrong with three agents")
req = "Customer asks: how long do refunds take?"
for label, inj in (("healthy", FailureInjection()),
                   ("1 infinite delegation loop", FailureInjection(research_loop=True)),
                   ("2 state corruption (message altered in transit)", FailureInjection(corrupt_message=True)),
                   ("3 failure cascade (research returns nothing)", FailureInjection(research_empty=True))):
    r = run_multi_agent(req, inj)
    print(f"\n[{label}] status={r.status} steps={r.steps}")
    print(f"  delegations: {r.delegations}")
    print(f"  failures   : {r.failures or 'none'}")
    print(f"  reply      : {r.final_reply[:110]}")
