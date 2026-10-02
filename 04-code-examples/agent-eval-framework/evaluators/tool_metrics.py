"""
Deterministic tool-calling checks (Module 6). Fast, free, and exact: use these
first, and an LLM judge only for what rules cannot decide.

    tool_selection_accuracy(results, cases)  share of cases whose first tool is right
    check_arguments(call, expected)          missing / wrong argument names and values
    check_sequence(calls, expected_order)    expected tools appear in this order
    unauthorized_calls(calls, forbidden)     calls that must never happen
"""

from __future__ import annotations

from dataclasses import dataclass, field


def tool_names(result: dict) -> list[str]:
    return [tc["tool"] for tc in result.get("tool_calls", [])]


def first_call(result: dict, tool: str) -> dict | None:
    return next((tc for tc in result.get("tool_calls", []) if tc["tool"] == tool), None)


@dataclass
class ArgCheck:
    ok: bool
    missing: list[str] = field(default_factory=list)
    wrong: dict[str, tuple] = field(default_factory=dict)


def check_arguments(call: dict | None, expected: dict) -> ArgCheck:
    """Compare a tool call's arguments with expected key/value pairs (case-insensitive strings)."""
    if call is None:
        return ArgCheck(ok=not expected, missing=list(expected))
    args = call.get("arguments", {})
    missing = [k for k in expected if k not in args]
    wrong = {}
    for k, v in expected.items():
        if k in args:
            got = args[k]
            same = str(got).lower() == str(v).lower() if not isinstance(v, list) else sorted(map(str.lower, got)) == sorted(map(str.lower, v))
            if not same:
                wrong[k] = (v, got)
    return ArgCheck(ok=not missing and not wrong, missing=missing, wrong=wrong)


def check_sequence(calls: list[str], expected_order: list[str]) -> bool:
    """True if expected_order is a subsequence of calls."""
    it = iter(calls)
    return all(any(c == e for c in it) for e in expected_order)


def unauthorized_calls(result: dict, forbidden: set[str]) -> list[dict]:
    return [tc for tc in result.get("tool_calls", []) if tc["tool"] in forbidden]


def tool_selection_accuracy(results: list[dict], cases: list[dict]) -> float:
    """Share of cases where the agent's tool set matches expected_tools (empty means 'no tool')."""
    hits = 0
    for r, c in zip(results, cases, strict=True):
        exp = c.get("expected_tools", [])
        got = tool_names(r)
        hits += (got[: len(exp)] == exp) if exp else (got == [])
    return hits / len(cases) if cases else 0.0
