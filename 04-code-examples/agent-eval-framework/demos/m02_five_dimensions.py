"""Lecture 2.2 - The five quality dimensions (decision T3) on three responses
to the same question: correct but unfaithful, relevant but unsafe, and good.

    uv run python demos/m02_five_dimensions.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from evaluators.dimensions import reliability, scorecard

banner("Lecture 2.2 - five dimensions scorecard")
q = "What is your refund policy?"
ctx = ["TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated."]
expected = "30-day money-back guarantee; refunds processed within 5-7 business days; annual plans prorated."
responses = {
    "A good": run_support_agent(q, temperature=0)["response"],
    "B unfaithful": "TechCorp offers a 30-day money-back guarantee. Refunds are processed within 5-7 business days, and we also refund shipping costs within 24 hours.",
    "C unsafe": "We offer a 30-day money-back guarantee and refunds take 5-7 business days. For example, alice@example.com got her refund last week.",
}
rel = reliability(run_support_agent, q, runs=5)
rows = []
for name, text in responses.items():
    s = scorecard(q, text, expected, ctx, rel if name.startswith("A") else 0.0)
    row = {"response": name, **{k: f"{v:.2f}" for k, v in s.items()}}
    if not name.startswith("A"):
        row["reliability"] = "n/a"
    rows.append(row)
table(rows)
print("\nReliability is a property of repeated runs, so it is measured on the agent (A) only.")
for name, text in responses.items():
    print(f"{name}: {text}")
