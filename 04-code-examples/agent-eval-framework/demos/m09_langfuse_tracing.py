"""Lecture 9.2 - Tracing with Langfuse v4: spans, costs, latency, scores.
Live (LANGFUSE_* keys set) the traces appear in the Langfuse UI; offline they
are captured in memory and printed.

    uv run python demos/m09_langfuse_tracing.py
"""
from _common import banner, table

import json

from config.settings import langfuse_configured
from deepeval.test_case import LLMTestCase
from evaluators.metrics import answer_relevancy
from observability.langfuse_tracing import LOCAL_SCORES, offline_spans, print_trace, score_trace, traced_support_agent

banner("Lecture 9.2 - Langfuse tracing", ["openai", "langfuse"])
sessions = [("CUST-001", "What are your pricing plans?"),
            ("CUST-001", "I've been charged twice this month for my Pro plan. My email is alice@example.com. Please create a ticket."),
            ("CUST-002", "How do I reset my password?"),
            ("CUST-003", "I want to file a legal complaint and I'm contacting my lawyer.")]
rows, trace_ids = [], []
for user, q in sessions:
    r = traced_support_agent(q, user_id=user, session_id=f"session-{user}", version="v1")
    m = answer_relevancy()
    m.measure(LLMTestCase(input=q, actual_output=r["response"]))
    score_trace(r["trace_id"], "answer_relevancy", m.score, comment="online eval")
    trace_ids.append(r["trace_id"])
    spans = offline_spans(r["trace_id"])
    cost = sum(json.loads(s["cost"]).get("total", 0) for s in spans if s["cost"])
    rows.append({"user": user, "question": q, "spans": len(spans), "llm_calls": r["llm_calls"], "tokens": r["total_tokens"],
                 "cost_usd": f"{cost:.6f}", "latency_s": r["latency_s"], "relevancy": f"{m.score:.2f}"})
table(rows, width=40)
print(f"\nTrace tree for the ticket request ({rows[1]['user']}):")
print_trace(trace_ids[1])
print(f"\nScores attached (create_score): {len(LOCAL_SCORES)} {'(sent to Langfuse)' if langfuse_configured() else '(recorded locally offline)'}")
