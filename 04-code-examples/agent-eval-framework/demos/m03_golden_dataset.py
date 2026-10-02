"""Lecture 3.2 - Building a golden dataset: pick diverse, representative cases
across the four categories and save them as DeepEval Goldens.

    uv run python demos/m03_golden_dataset.py
"""
from _common import banner, table

from collections import Counter

from deepeval.dataset import EvaluationDataset, Golden
from evaluators.golden import SUPPORT_CATEGORIES, load

banner("Lecture 3.2 - golden dataset")
cases = load("golden_support")
print(f"golden_support.json: {len(cases)} cases, categories {dict(Counter(c['category'] for c in cases))}\n")
table([{"id": c["id"], "category": c["category"], "difficulty": c["difficulty"], "tools": ",".join(c["expected_tools"]) or "-", "input": c["input"]} for c in cases],
      width=40)
# A 5-case starter set: at least one per category, hardest first.
starter = []
for cat in SUPPORT_CATEGORIES:
    starter.append(next(c for c in cases if c["category"] == cat))
starter.append(next(c for c in cases if c["category"] == "account" and c not in starter))
ds = EvaluationDataset(goldens=[Golden(input=c["input"], expected_output=c["expected_output"], context=c["context"] or None,
                                       additional_metadata={"id": c["id"], "category": c["category"]}) for c in starter])
print(f"\n5-case starter dataset: {[g.additional_metadata['id'] for g in ds.goldens]}")
print("Rule of thumb: every category, at least one hard case, expected output written by a domain expert.")
