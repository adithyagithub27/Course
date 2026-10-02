"""Trajectory: the 3-agent Reply Desk (Module 7, Lab 7.1)."""

import pytest

from agents.multi_agent import FALLBACK_REPLY, FailureInjection, Message, run_multi_agent


@pytest.mark.multi_agent
def test_healthy_run_delegates_research_then_writer():
    r = run_multi_agent("Customer asks: what are your pricing plans?")
    assert r.status == "ok" and r.delegations == ["research", "writer", "finish"]
    assert [(m.sender, m.receiver) for m in r.messages] == [("supervisor", "research"), ("research", "supervisor"),
                                                            ("supervisor", "writer"), ("writer", "supervisor")]
    assert all(m.is_valid() for m in r.messages)
    assert "$29.99" in r.final_reply


@pytest.mark.multi_agent
@pytest.mark.parametrize("flag,failure,status", [
    ("research_empty", "empty_research", "degraded"),
    ("writing_toxic", "unsafe_output", "degraded"),
    ("research_loop", "loop_detected", "degraded"),
    ("corrupt_message", "corrupted_message", "recovered"),
])
def test_injected_failures_are_detected(flag, failure, status):
    r = run_multi_agent("Customer asks: how do I reset my password?", FailureInjection(**{flag: True}))
    assert failure in r.failure_types and r.status == status
    assert r.steps <= 10
    if status == "degraded":
        assert r.final_reply == FALLBACK_REPLY
    else:
        assert "Settings > Security" in r.final_reply


def test_toxic_text_never_reaches_the_customer():
    r = run_multi_agent("Customer asks: how long do refunds take?", FailureInjection(writing_toxic=True))
    assert "idiot" not in r.final_reply


def test_message_checksum():
    m = Message("a", "b", "hello", 1)
    assert m.is_valid()
    m.content = "tampered"
    assert not m.is_valid()
