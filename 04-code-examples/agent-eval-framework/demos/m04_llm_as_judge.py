"""Lecture 4.3 - LLM-as-judge from scratch: rubric prompt, JSON score, reasoning,
then a calibration check against human scores.

    uv run python demos/m04_llm_as_judge.py
"""
from _common import banner, table

from evaluators.llm_as_judge import JUDGE_PROMPT, agreement, judge

banner("Lecture 4.3 - LLM as judge")
print(JUDGE_PROMPT.split("Question:")[0].replace("{{", "{").replace("}}", "}"))
ctx = "TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days."
q = "What is your refund policy?"
answers = [
    ("TechCorp has a 30-day money-back guarantee, and refunds take 5-7 business days.", 5),
    ("You can get a refund within 30 days.", 4),
    ("Refunds are possible for 14 days and take 10 business days.", 1),
    ("I can't help with refunds.", 1),
]
rows, judged = [], []
for text, human in answers:
    v = judge(q, text, ctx)
    judged.append(v["score"])
    rows.append({"answer": text, "judge": v["score"], "human": human, "reasoning": v["reasoning"]})
table(rows, width=60)
print(f"\nCalibration vs human labels: {agreement(judged, [h for _, h in answers])}")
