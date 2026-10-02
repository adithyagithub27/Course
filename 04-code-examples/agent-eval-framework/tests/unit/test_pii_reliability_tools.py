"""Unit: PII scanner, loop detector, retries/timeouts, tool-call checks, token/cost helpers."""

import time

import pytest

from evaluators.tool_metrics import check_arguments, check_sequence, tool_selection_accuracy, unauthorized_calls
from performance.cost import CHEAP_MODEL, STRONG_MODEL, prompt_overhead, route_model, savings
from performance.reliability import LoopDetector, call_with_timeout, detect_tool_loop, with_retry
from performance.tokens import count_tokens
from security.pii_scanner import scan, scan_responses


def test_pii_scanner_kinds_and_allow_list():
    found = scan("Bob is bob@example.com, SSN 987-65-4321, acct ACC-2002-CHK, CUST-002", allowed={"bob@example.com"})
    assert {f.kind for f in found} == {"ssn", "bank_account", "customer_id"}
    assert scan("Report it to security@techcorp.com") == []
    rep = scan_responses(["clean", "leak alice@example.com"])
    assert rep["leaking"] == 1 and rep["by_kind"] == {"email": 1}


def test_loop_detector():
    d = LoopDetector(max_repeats=3, max_steps=4)
    assert d.record("a") is None and d.record("a") is None
    assert "repeated 3 times" in d.record("a")
    d2 = LoopDetector(max_repeats=9, max_steps=2)
    d2.record("a"); d2.record("b")
    assert "budget" in d2.record("c")
    assert detect_tool_loop([{"tool": "t", "arguments": {"q": 1}}] * 3)
    assert detect_tool_loop([{"tool": "t", "arguments": {"q": i}} for i in range(3)]) is None


def test_retry_and_timeout():
    n = {"i": 0}

    def flaky():
        n["i"] += 1
        if n["i"] < 2:
            raise ConnectionError
        return "ok"

    assert with_retry(flaky, attempts=3) == ("ok", 1)
    with pytest.raises(ConnectionError):
        with_retry(lambda: (_ for _ in ()).throw(ConnectionError()), attempts=2)
    with pytest.raises(TimeoutError):
        call_with_timeout(lambda: time.sleep(0.3), timeout_s=0.05)


def test_tool_checks():
    call = {"tool": "lookup_customer", "arguments": {"identifier": "Alice"}}
    assert check_arguments(call, {"identifier": "alice@example.com"}).wrong
    assert check_arguments({"tool": "x", "arguments": {"r": ["B@x", "a@x"]}}, {"r": ["a@x", "b@x"]}).ok
    assert check_arguments(None, {"a": 1}).missing == ["a"]
    assert check_sequence(["lookup_customer", "search_knowledge_base", "create_ticket"], ["lookup_customer", "create_ticket"])
    assert not check_sequence(["create_ticket", "lookup_customer"], ["lookup_customer", "create_ticket"])
    assert unauthorized_calls({"tool_calls": [call]}, {"lookup_customer"}) == [call]
    assert tool_selection_accuracy([{"tool_calls": []}, {"tool_calls": [call]}],
                                   [{"expected_tools": []}, {"expected_tools": ["lookup_customer"]}]) == 1.0


def test_tokens_and_routing():
    assert count_tokens("hello world") >= 1
    assert prompt_overhead()["tool_schema_tokens"] > prompt_overhead()["system_prompt_tokens"] > 0
    assert route_model("What are your pricing plans?") == CHEAP_MODEL
    assert route_model("Check my account alice@example.com") == STRONG_MODEL
    assert savings(1.0, 0.5) == 50.0
