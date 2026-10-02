"""Lecture 0.2 - Environment verification: libraries, keys, mode, one agent call, one metric.

    uv run python demos/m00_verify_setup.py
"""
from _common import banner, version, PACKAGES  # noqa: I001

import os

banner("Lecture 0.2 - verify_setup", PACKAGES)
checks = []
for pkg in PACKAGES + ["opentelemetry-semantic-conventions", "streamlit", "pytest"]:
    v = version(pkg)
    checks.append((pkg, v != "not installed", v))
checks.append(("OPENAI_API_KEY set", bool(os.getenv("OPENAI_API_KEY")), "optional offline"))
checks.append(("LANGFUSE keys set", bool(os.getenv("LANGFUSE_PUBLIC_KEY")), "optional until Module 9"))

from agents.support_agent import run_support_agent  # noqa: E402
from deepeval.test_case import LLMTestCase  # noqa: E402
from evaluators.metrics import answer_relevancy  # noqa: E402

r = run_support_agent("What is your refund policy?")
checks.append(("support agent answers", bool(r["response"]), f"{r['llm_calls']} LLM calls, tools {[t['tool'] for t in r['tool_calls']]}"))
m = answer_relevancy()
m.measure(LLMTestCase(input="What is your refund policy?", actual_output=r["response"]))
checks.append(("DeepEval metric runs", m.score is not None, f"AnswerRelevancy = {m.score:.2f}"))

for name, ok, detail in checks:
    print(f"[{'OK' if ok else '--'}] {name:<38} {detail}")
required_ok = all(ok for name, ok, _ in checks if "set" not in name)
print("\nSetup complete. You're ready for Module 1." if required_ok else "\nFix the items marked -- and run again.")
