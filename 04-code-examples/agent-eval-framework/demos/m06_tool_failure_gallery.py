"""Lecture 6.1 - Tool-call failure gallery: four recorded failures of the
TechCorp agent and the deterministic check that catches each.

    uv run python demos/m06_tool_failure_gallery.py
"""
from _common import banner

from evaluators.golden import load
from evaluators.tool_metrics import check_arguments, check_sequence, first_call, unauthorized_calls

banner("Lecture 6.1 - tool call failure gallery")
SUCCESS_WORDS = ("done", "created", "processed", "sent")
for case in load("tool_failures"):
    run = {"tool_calls": case["tool_calls"], "response": case["response"]}
    chk = case["check"]
    if chk["type"] == "arguments":
        res = check_arguments(first_call(run, chk["tool"]), chk["expected"])
        verdict = f"FAIL wrong arguments {res.wrong}"
    elif chk["type"] == "forbidden":
        bad = unauthorized_calls(run, set(chk["tools"]))
        verdict = f"FAIL action tool called for a question: {[b['tool'] for b in bad]}"
    elif chk["type"] == "error_honesty":
        errored = [t["tool"] for t in case["tool_calls"] if t.get("result", "").lower().startswith("error")]
        claims = any(w in case["response"].lower() for w in SUCCESS_WORDS)
        verdict = f"FAIL {errored} returned an error but the reply claims success" if errored and claims else "PASS"
    else:
        ok = check_sequence([t["tool"] for t in case["tool_calls"]], chk["order"])
        verdict = "PASS" if ok else f"FAIL expected order {chk['order']}"
    print(f"\n{case['id']} {case['failure']}")
    print(f"  user : {case['input']}")
    print(f"  tools: {[t['tool'] + str(t['arguments']) for t in case['tool_calls']]}")
    print(f"  reply: {case['response']}")
    print(f"  check: {verdict}")
