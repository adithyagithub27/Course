"""Lecture 7.3 / 10.2 - A runtime loop detector: halt after 3 identical
consecutive actions or a 10-step budget.

    uv run python demos/m07_loop_detector.py
"""
from _common import banner

from performance.reliability import LoopDetector, detect_tool_loop

banner("Lecture 7.3 - loop detector")
det = LoopDetector(max_repeats=3, max_steps=10)
actions = [("research", "find refund facts"), ("research", "find refund facts"), ("writer", "draft"),
           ("research", "which plan?"), ("research", "which plan?"), ("research", "which plan?")]
for i, (a, d) in enumerate(actions, 1):
    reason = det.record(a, d)
    print(f"step {i}: {a:<9} {d:<20} -> {'HALT: ' + reason if reason else 'ok'}")
    if reason:
        break
calls = [{"tool": "search_knowledge_base", "arguments": {"query": "reseller refund"}}] * 4
print(f"\nOn a single agent's tool calls: {detect_tool_loop(calls)}")
