"""Lab 7.1 - Failure injection in the 3-agent system: inject each of the four
failures and verify detection plus graceful degradation.

    uv run python demos/m07_lab_failure_injection.py
"""
from _common import banner, table

from agents.multi_agent import FALLBACK_REPLY, FailureInjection, run_multi_agent

banner("Lab 7.1 - failure injection")
EXPECT = {"research_empty": "empty_research", "writing_toxic": "unsafe_output",
          "research_loop": "loop_detected", "corrupt_message": "corrupted_message"}
rows = []
for flag, expected in EXPECT.items():
    r = run_multi_agent("Customer asks: how do I reset my password?", FailureInjection(**{flag: True}))
    rows.append({"injected": flag, "detected": ",".join(r.failure_types), "expected": expected,
                 "status": r.status, "steps": r.steps,
                 "result": "PASS" if expected in r.failure_types and r.status in ("degraded", "recovered") else "FAIL"})
table(rows)
print("\ndegraded = the customer gets the safe fallback; recovered = failure caught and the retry succeeded.")
print(f"Fallback reply: {FALLBACK_REPLY}")
