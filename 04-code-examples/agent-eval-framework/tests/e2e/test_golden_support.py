"""End-to-end: the golden dataset through DeepEval's assert_test (Modules 3 and 11).
Same file runs live with gpt-4.1 as judge: OFFLINE=0 uv run deepeval test run tests/e2e/test_golden_support.py
"""

import pytest
from deepeval import assert_test

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, golden_dataset, run_suite, to_test_case
from evaluators.golden import SUPPORT_CATEGORIES, load

CASES = load("golden_support")


def test_ten_cases_four_categories():
    assert len(CASES) == 10
    assert [sum(c["category"] == k for c in CASES) for k in SUPPORT_CATEGORIES] == [3, 3, 2, 2]
    capstone = load("golden_capstone")
    assert len(capstone) == 20 and {c["category"] for c in capstone} == set(SUPPORT_CATEGORIES)
    assert [c["id"] for c in capstone[:10]] == [c["id"] for c in CASES]


@pytest.mark.functional
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden_case(case):
    result = run_support_agent(case["input"])
    assert_test(to_test_case(result, case), default_metrics_for(case))


@pytest.mark.regression
def test_capstone_dataset_pass_rate():
    report = run_suite(load("golden_capstone"), run_support_agent, default_metrics_for)
    assert report["pass_rate"] == 1.0, [d["id"] for d in report["details"] if not d["passed"]]


def test_golden_dataset_as_deepeval_goldens():
    ds = golden_dataset("golden_support")
    assert len(ds.goldens) == 10 and ds.goldens[0].expected_tools[0].name == "search_knowledge_base"
