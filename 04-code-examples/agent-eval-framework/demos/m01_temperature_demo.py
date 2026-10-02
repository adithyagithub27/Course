"""Lecture 1.1 - Temperature experiment: the same question 5 times at 0.0 and at 1.0.

    uv run python demos/m01_temperature_demo.py
"""
from _common import banner

from agents.support_agent import run_support_agent

banner("Lecture 1.1 - temperature")
q = "How long do refunds take?"
for temp in (0.0, 1.0):
    answers = [run_support_agent(q, temperature=temp)["response"] for _ in range(5)]
    print(f"\ntemperature={temp}: {len(set(answers))} distinct answer(s) out of 5")
    for i, a in enumerate(answers, 1):
        print(f"  {i}. {a}")
print("\nSame facts, different words: an exact-match assertion would fail on the 1.0 runs.")
