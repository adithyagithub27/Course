"""Lecture 4.2 - Agent-specific metrics: Task Completion and Tool Correctness
on real agent runs (tools_called vs expected_tools).

    uv run python demos/m04_agent_metrics.py
"""
from _common import banner, table

from agents.support_agent import run_support_agent
from deepeval.test_case import LLMTestCase, ToolCall
from evaluators import metrics as M
from evaluators.deepeval_suite import to_test_case
from evaluators.golden import load

banner("Lecture 4.2 - agent metrics")
rows = []
for case in [c for c in load("golden_support") if c["id"] in ("GS-03", "GS-05", "GS-06", "GS-07")]:
    tc = to_test_case(run_support_agent(case["input"]), case)
    tool_m, task_m = M.tool_correctness(), M.task_completion()
    tool_m.measure(tc)
    task_m.measure(tc)
    rows.append({"id": case["id"], "expected tools": ",".join(case["expected_tools"]),
                 "called": ",".join(t.name for t in tc.tools_called), "tool_correct": f"{tool_m.score:.2f}", "task_complete": f"{task_m.score:.2f}"})
# A recorded bad run: ticket instead of a knowledge-base answer.
bad = LLMTestCase(input="How do I reset my password?", actual_output="I've opened a ticket for your password reset.",
                  tools_called=[ToolCall(name="create_ticket")], expected_tools=[ToolCall(name="search_knowledge_base")])
m = M.tool_correctness()
m.measure(bad)
rows.append({"id": "recorded-bad", "expected tools": "search_knowledge_base", "called": "create_ticket", "tool_correct": f"{m.score:.2f}", "task_complete": "-"})
table(rows, width=48)
print(f"\nToolCorrectness reason for the bad run: {m.reason}")
