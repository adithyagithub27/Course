"""Lecture 15.1 - Your portfolio in numbers: what you built, ready for a CV or interview.

    uv run python demos/m15_portfolio_summary.py
"""
from _common import ROOT, banner

banner("Lecture 15.1 - portfolio summary", ["openai", "deepeval", "ragas", "langfuse", "mcp"])
tests = len(list((ROOT / "tests").rglob("test_*.py")))
demos = len(list((ROOT / "demos").glob("m*.py")))
print(f"- Agents tested: TechCorp support (5 tools), policy RAG agent, operations agent (6 tools), SecureBank, 3-agent Reply Desk")
print(f"- {tests} test files across a five-layer eval pyramid; {demos} runnable demos")
print("- Metrics: DeepEval (relevancy, faithfulness, hallucination, GEval, tool correctness), RAGAS 0.4, custom judges")
print("- Security: promptfoo suite on the real agent, Garak and PyRIT configs, PII scanner, red-team report")
print("- Ops: Langfuse v4 + OpenTelemetry GenAI traces, benchmarks, model routing, drift monitor, CI quality gate")
print("\nSTAR example: 'Situation: a prompt edit made our agent invent refund terms. Task: stop it reaching")
print("production. Action: golden-dataset regression gate in CI. Result: faithfulness drop from 1.00 to 0.25 blocked the PR.'")
