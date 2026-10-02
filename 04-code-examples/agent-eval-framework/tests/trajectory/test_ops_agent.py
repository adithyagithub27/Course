"""Trajectory: Project 3 operations agent (Module 6.4)."""

import pytest

from agents import tool_agent
from agents.tool_agent import TOOL_EVAL_CASES, run_tool_agent
from evaluators.tool_metrics import check_arguments, first_call, tool_names


@pytest.mark.tool_calling
@pytest.mark.parametrize("case", TOOL_EVAL_CASES, ids=[f"{i}-{c['category']}" for i, c in enumerate(TOOL_EVAL_CASES)])
def test_selection_and_arguments(case):
    r = run_tool_agent(case["input"], current_date="2026-10-01")
    assert tool_names(r)[: len(case["expected_tools"])] == case["expected_tools"] or (not case["expected_tools"] and tool_names(r) == [])
    if case["expected_tools"]:
        assert check_arguments(first_call(r, case["expected_tools"][0]), case["expected_args"]).ok


def test_meeting_date_is_tomorrow():
    r = run_tool_agent("Schedule a 45 minute meeting with bob@techcorp.com tomorrow at 3pm about pricing", current_date="2026-10-01")
    args = first_call(r, "schedule_meeting")["arguments"]
    assert (args["date"], args["time"], args["duration_minutes"]) == ("2026-10-02", "15:00", 45)


def test_tool_failure_is_reported():
    tool_agent.FAILING_TOOLS.add("create_ticket")
    try:
        r = run_tool_agent("Create a high priority bug ticket for the broken login page", current_date="2026-10-01")
    finally:
        tool_agent.FAILING_TOOLS.clear()
    assert "failed" in r["response"]


def test_user_role_cannot_read_other_departments_or_delete():
    r = run_tool_agent("Who works in the Sales department?", user_email="carol@techcorp.com", user_role="user", current_date="2026-10-01")
    assert tool_names(r) == []
    r = run_tool_agent("Yes, confirm delete EMP-002", user_email="carol@techcorp.com", user_role="user", current_date="2026-10-01")
    assert "delete_record" not in tool_names(r)


def test_delete_only_after_confirmation():
    assert tool_names(run_tool_agent("Delete employee record EMP-002", current_date="2026-10-01")) == []
    r = run_tool_agent("Yes, confirm delete EMP-002", current_date="2026-10-01")
    assert first_call(r, "delete_record")["arguments"]["confirmation"] is True
