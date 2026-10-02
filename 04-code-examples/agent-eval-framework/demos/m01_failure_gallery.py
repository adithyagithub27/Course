"""Lecture 1.4 - The six failure modes (decision T2), each with a recorded agent
run and the check that catches it.

    uv run python demos/m01_failure_gallery.py
"""
from _common import banner

from deepeval.test_case import LLMTestCase
from evaluators import metrics as M
from evaluators.golden import load
from evaluators.tool_metrics import check_arguments
from performance.reliability import detect_tool_loop

banner("Lecture 1.4 - failure mode gallery")
for case in load("failure_gallery"):
    mode, tools = case["mode"], [t["tool"] for t in case["tool_calls"]]
    if mode == "hallucination":
        m = M.faithfulness(); m.measure(LLMTestCase(input=case["input"], actual_output=case["response"], retrieval_context=case["context"]))
        caught = f"Faithfulness {m.score:.2f} (threshold {m.threshold})"
    elif mode == "wrong_tool_selection":
        caught = f"expected {case['expected_tools']}, got {tools}"
    elif mode == "incorrect_tool_arguments":
        chk = check_arguments(case["tool_calls"][0], case["expected_args"])
        caught = f"argument check: wrong={chk.wrong}"
    elif mode == "reasoning_error":
        m = M.correctness(); m.measure(LLMTestCase(input=case["input"], actual_output=case["response"], expected_output=case["expected_output"]))
        caught = f"GEval correctness {m.score:.2f}"
    elif mode == "goal_drift":
        m = M.answer_relevancy(); m.measure(LLMTestCase(input=case["input"], actual_output=case["response"]))
        caught = f"Answer relevancy {m.score:.2f}"
    else:
        caught = f"loop detector: {detect_tool_loop(case['tool_calls'])}"
    print(f"\n[{mode}] {case['input']}")
    print(f"  tools : {tools}")
    print(f"  reply : {case['response'][:100]}")
    print(f"  why   : {case['note']}")
    print(f"  caught: {caught}")
