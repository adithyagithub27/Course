"""
Langfuse Observability Setup — Agent tracing and monitoring.

Demonstrates how to instrument AI agents for full observability
using Langfuse. Used in Module 09.

Langfuse provides:
- Trace visualization (span waterfall)
- Token cost tracking
- Latency monitoring
- Evaluation score logging
- Production monitoring dashboards
"""

import os
from functools import wraps
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from dotenv import load_dotenv

load_dotenv()


def init_langfuse() -> Langfuse:
    """Initialize the Langfuse client."""
    return Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )


@observe(name="support-agent")
def traced_agent_call(user_message: str) -> dict:
    """
    Run the support agent with Langfuse tracing enabled.

    Every LLM call, tool execution, and decision point is recorded
    as a span in the trace. This enables:
    - Debugging failed agent runs
    - Identifying slow steps
    - Tracking token costs per component
    - Comparing agent versions
    """
    from agents.support_agent import run_support_agent

    # Tag the trace with metadata for filtering
    langfuse_context.update_current_trace(
        metadata={
            "agent_type": "customer_support",
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        }
    )

    result = run_support_agent(user_message)

    # Log evaluation scores to the trace
    langfuse_context.update_current_observation(
        output=result["response"],
        metadata={
            "tool_calls": len(result["tool_calls"]),
            "total_tokens": result["total_tokens"],
            "llm_calls": result["llm_calls"],
        },
    )

    return result


def log_eval_score(
    trace_id: str,
    metric_name: str,
    score: float,
    comment: str | None = None,
) -> None:
    """
    Log an evaluation score to an existing Langfuse trace.

    This connects evaluation results back to the agent run,
    enabling drill-down from a failing eval to the exact trace.
    """
    langfuse = init_langfuse()
    langfuse.score(
        trace_id=trace_id,
        name=metric_name,
        value=score,
        comment=comment,
    )


def get_trace_summary(trace_id: str) -> dict:
    """
    Retrieve a trace summary for analysis.

    Returns span count, total latency, token cost breakdown,
    and any logged evaluation scores.
    """
    langfuse = init_langfuse()
    trace = langfuse.get_trace(trace_id)

    return {
        "id": trace.id,
        "name": trace.name,
        "latency_ms": trace.latency if hasattr(trace, "latency") else None,
        "total_tokens": trace.metadata.get("total_tokens") if trace.metadata else None,
        "scores": {s.name: s.value for s in trace.scores} if trace.scores else {},
    }


if __name__ == "__main__":
    # Quick test: run a traced agent call
    result = traced_agent_call("What are your pricing plans?")
    print(f"Response: {result['response'][:100]}...")
    print(f"Tokens: {result['total_tokens']}")
    print("Check Langfuse dashboard for the trace.")
