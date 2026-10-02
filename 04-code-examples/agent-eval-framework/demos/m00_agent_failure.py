"""Lecture 0.1 - "Your agent just failed in production": a one-line prompt change
makes the support agent invent refund terms; an eval catches it before deploy.

    uv run python demos/m00_agent_failure.py
"""
from _common import banner

from agents.support_agent import SYSTEM_PROMPT, run_support_agent
from deepeval.test_case import LLMTestCase
from evaluators.metrics import faithfulness
from regression.regression_suite import PROMPT_V2_REGRESSED

banner("Lecture 0.1 - the agent that failed in production")
q = "What is your refund policy?"
kb = ["TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated."]
removed = [line for line in SYSTEM_PROMPT.splitlines() if line not in PROMPT_V2_REGRESSED.splitlines()]
print("The 'harmless' prompt edit deleted this line:\n   " + removed[0])
for label, prompt in (("BEFORE (v1)", SYSTEM_PROMPT), ("AFTER  (v2)", PROMPT_V2_REGRESSED)):
    r = run_support_agent(q, system_prompt=prompt, temperature=0)
    m = faithfulness()
    m.measure(LLMTestCase(input=q, actual_output=r["response"], retrieval_context=kb))
    print(f"\n{label} tools={[t['tool'] for t in r['tool_calls']]}")
    print(f"  answer: {r['response']}")
    print(f"  Faithfulness vs the refund policy: {m.score:.2f} -> {'PASS' if m.is_successful() else 'FAIL: block this deploy'}")
