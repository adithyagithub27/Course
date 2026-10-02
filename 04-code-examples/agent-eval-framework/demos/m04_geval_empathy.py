"""Lecture 4.4 - Build a custom GEval metric: "Customer Empathy".

    uv run python demos/m04_geval_empathy.py
"""
from _common import banner

from deepeval.test_case import LLMTestCase
from evaluators.custom_metrics import customer_empathy

banner("Lecture 4.4 - G-Eval: Customer Empathy")
metric = customer_empathy()
print("Criteria:", metric.criteria)
print("Evaluation steps:")
for s in metric.evaluation_steps:
    print("  -", s)
complaint = "This is ridiculous! I was charged twice and nobody answers my emails!"
replies = {
    "empathetic": "I'm sorry for the frustration, and thank you for flagging it. I've opened a high-priority ticket so billing can refund the duplicate charge.",
    "flat": "A ticket has been created for the duplicate charge.",
    "rude": "Stop shouting. Read the docs yourself, you idiot.",
}
for name, reply in replies.items():
    m = customer_empathy()
    m.measure(LLMTestCase(input=complaint, actual_output=reply))
    print(f"\n{name:<11} score {m.score:.2f} {'PASS' if m.is_successful() else 'FAIL'}  {reply}")
    print(f"            reason: {m.reason}")
