"""
Glue between agent results and DeepEval.

    result = run_support_agent(case["input"])
    tc = to_test_case(result, case)               # LLMTestCase with tools_called, retrieval_context
    report = run_suite(cases, run_support_agent, metrics_for)   # dict summary for reports and CI

``retrieval_context`` is what the agent actually saw: the text its tools
returned in this run (knowledge-base articles, account lookups). That is what
faithfulness should be judged against.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase, ToolCall

from evaluators.golden import load


def tools_called(result: dict) -> list[ToolCall]:
    return [
        ToolCall(name=tc["tool"], input_parameters=tc.get("arguments", {}), output=tc.get("result"))
        for tc in result.get("tool_calls", [])
    ]


def to_test_case(result: dict, case: dict) -> LLMTestCase:
    """Build an LLMTestCase from one agent run and its golden case."""
    observed = [tc["result"] for tc in result.get("tool_calls", []) if tc["tool"] in ("search_knowledge_base", "lookup_customer")]
    return LLMTestCase(
        input=case["input"],
        actual_output=result.get("response") or result.get("answer", ""),
        expected_output=case.get("expected_output"),
        context=case.get("context") or None,
        retrieval_context=observed or case.get("context") or None,
        tools_called=tools_called(result),
        expected_tools=[ToolCall(name=n) for n in case.get("expected_tools", [])],
        name=case.get("id"),
        tags=[case.get("category", "uncategorized")],
        completion_time=result.get("latency_s"),
    )


def golden_dataset(name: str = "golden_support") -> EvaluationDataset:
    """A DeepEval EvaluationDataset of Goldens (inputs + expectations, no outputs yet)."""
    goldens = [
        Golden(
            input=c["input"],
            expected_output=c.get("expected_output"),
            context=c.get("context") or None,
            expected_tools=[ToolCall(name=n) for n in c.get("expected_tools", [])],
            additional_metadata={"id": c["id"], "category": c.get("category")},
        )
        for c in load(name)
    ]
    return EvaluationDataset(goldens=goldens)


def measure(tc: LLMTestCase, metrics: list) -> dict[str, dict]:
    """Run metrics on one test case without DeepEval's console output."""
    out = {}
    for m in metrics:
        name = getattr(m, "name", None) or m.__name__
        try:
            m.measure(tc)
            out[name] = {"score": round(float(m.score), 3), "passed": bool(m.is_successful()), "reason": m.reason}
        except Exception as exc:  # missing params etc. are reported, not raised
            out[name] = {"score": None, "passed": False, "reason": f"error: {exc}"}
    return out


def run_suite(
    cases: list[dict],
    agent_fn: Callable[[str], dict],
    metrics_for: Callable[[dict], list],
) -> dict:
    """Run every case through the agent and its metrics. Returns a JSON-able report."""
    details = []
    for case in cases:
        result = agent_fn(case["input"])
        tc = to_test_case(result, case)
        scores = measure(tc, metrics_for(case))
        tools_ok = [t["tool"] for t in result["tool_calls"]] == case.get("expected_tools", []) if "expected_tools" in case else True
        passed = all(s["passed"] for s in scores.values()) and tools_ok
        details.append({
            "id": case.get("id"), "category": case.get("category"), "input": case["input"],
            "output": tc.actual_output, "tools": [t["tool"] for t in result["tool_calls"]],
            "tools_ok": tools_ok, "metrics": scores, "passed": passed,
            "tokens": result.get("total_tokens", 0), "latency_s": result.get("latency_s"),
        })
    passed = sum(d["passed"] for d in details)
    metric_names = sorted({k for d in details for k in d["metrics"]})
    averages = {}
    for name in metric_names:
        vals = [d["metrics"][name]["score"] for d in details if name in d["metrics"] and d["metrics"][name]["score"] is not None]
        averages[name] = round(sum(vals) / len(vals), 3) if vals else None
    return {"total": len(details), "passed": passed, "failed": len(details) - passed,
            "pass_rate": round(passed / len(details), 3) if details else 0.0,
            "averages": averages, "details": details}


def default_metrics_for(case: dict) -> list:
    """Project 1 metric set; faithfulness only where the case has grounding context."""
    from evaluators.metrics import answer_relevancy, correctness, faithfulness

    ms = [answer_relevancy(), correctness()]
    if case.get("context"):
        ms.insert(1, faithfulness())
    return ms


def save_report(report: dict, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2, default=str))
    return p
