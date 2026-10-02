"""Lab 4.1 - Regulatory Compliance GEval for a financial-services agent,
calibrated against 10 pre-scored examples.

    uv run python demos/m04_lab_regulatory_geval.py
"""
from _common import banner, table

from deepeval.test_case import LLMTestCase
from evaluators.custom_metrics import regulatory_compliance
from evaluators.golden import load
from evaluators.llm_as_judge import agreement

banner("Lab 4.1 - regulatory compliance metric")
rows, preds, humans = [], [], []
for ex in load("regulatory_calibration"):
    m = regulatory_compliance()
    m.measure(LLMTestCase(input="Is this a good investment?", actual_output=ex["output"]))
    pred = int(m.is_successful())
    preds.append(pred)
    humans.append(ex["human"])
    rows.append({"output": ex["output"], "score": f"{m.score:.2f}", "metric": "pass" if pred else "fail", "human": "pass" if ex["human"] else "fail",
                 "agree": "yes" if pred == ex["human"] else "NO"})
table(rows, width=70)
print(f"\nAgreement with human labels: {agreement(preds, humans, tolerance=0)}")
print("Target: >= 0.9 agreement before the metric gates anything.")
