"""Lecture 7.2 - Testing agent communication: every hand-off between the
supervisor and its two workers is checked (route, order, integrity, content).

    uv run python demos/m07_communication_tests.py
"""
from _common import banner, table

from agents.multi_agent import run_multi_agent

banner("Lecture 7.2 - communication test suite")
r = run_multi_agent("Customer asks: what are your pricing plans?")
table([m.to_dict() | {"content": m.content[:60]} for m in r.messages], width=60)
checks = {
    "research is called before the writer": r.delegations[:2] == ["research", "writer"],
    "every message passes its checksum": all(m.is_valid() for m in r.messages),
    "workers only talk to the supervisor": all("supervisor" in (m.sender, m.receiver) for m in r.messages),
    "writer used the research findings": "$29.99" in r.final_reply,
    "finished within the step budget": r.steps <= 10,
}
print()
for name, ok in checks.items():
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
print(f"\nFinal reply: {r.final_reply}")
