"""Production layer: tracing (Langfuse v4 offline capture, OTel GenAI attributes)."""

import json

from observability.langfuse_tracing import LOCAL_SCORES, offline_spans, score_trace, traced_support_agent
from observability.otel_genai import make_tracer, run_with_otel, spans_as_rows


def test_langfuse_trace_structure():
    r = traced_support_agent("What is your refund policy?", user_id="CUST-001", session_id="s-1")
    spans = offline_spans(r["trace_id"])
    assert [s["type"] for s in spans] == ["agent", "generation", "tool", "generation"]
    assert all(s["user_id"] == "CUST-001" and s["session_id"] == "s-1" for s in spans)
    gen = spans[1]
    assert json.loads(gen["usage"])["input"] > 0 and json.loads(gen["cost"])["total"] > 0


def test_scores_recorded_offline():
    n = len(LOCAL_SCORES)
    score_trace("abc", "faithfulness", 0.9)
    assert LOCAL_SCORES[n] == {"trace_id": "abc", "name": "faithfulness", "value": 0.9, "comment": None}


def test_otel_genai_semantic_conventions():
    tracer, exporter = make_tracer()
    run_with_otel("Look up my account, alice@example.com", tracer)
    rows = spans_as_rows(exporter)
    assert [r["name"] for r in rows] == ["invoke_agent techcorp-support", "chat gpt-4.1-mini", "execute_tool lookup_customer", "chat gpt-4.1-mini"]
    chat = rows[1]["attributes"]
    assert chat["gen_ai.operation.name"] == "chat" and chat["gen_ai.provider.name"] == "openai"
    assert chat["gen_ai.request.model"] == "gpt-4.1-mini" and chat["gen_ai.usage.input_tokens"] > 0
    assert rows[2]["attributes"]["gen_ai.tool.name"] == "lookup_customer"
