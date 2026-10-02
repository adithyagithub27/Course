# Lab 7.1: Failure Injection in Multi-Agent Systems

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 7.1 (file `lab-06-multi-agent-failure.md`) |
| **Module** | Module 07 — Multi-Agent System Testing |
| **Lectures** | 7.1–7.3 |
| **Duration** | 90 minutes |
| **Difficulty** | Advanced |
| **Learning Objective** | Inject four failures into the 3-agent TechCorp Reply Desk (Supervisor + Research Agent + Writing Agent) — empty research, toxic writing, an infinite loop and a corrupted hand-off — and prove each is detected and either degrades to a safe fallback or recovers. |
| **Reference solution** | `demos/m07_lab_failure_injection.py`, `tests/trajectory/test_multi_agent.py` |
| **Verified on** | openai 2.54.0 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Labs 1.1, 3.1 and 6.1**
- Lectures 7.1–7.3: delegation, hand-off validation, loop detection, failure propagation

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python -m agents.multi_agent "Customer asks: how long do refunds take?"
```

Open `agents/multi_agent.py`. The **TechCorp Reply Desk** drafts customer replies:

| Agent | Job | Talks to |
|---|---|---|
| **Supervisor** | Decides the next step: JSON `{"next": "research" \| "writer" \| "finish", "instruction": ...}`; validates every hand-off | both workers |
| **Research Agent** | Tool-calling LLM over the support knowledge base; replies `FINDINGS: ...` | Supervisor only |
| **Writing Agent** | Drafts the customer reply from the findings | Supervisor only |

Safety nets already built in:

- Every hand-off is a `Message(sender, receiver, content, msg_id, checksum)`; `is_valid()` re-computes the SHA-256 checksum (12 hex characters).
- `LoopDetector(max_repeats=3, max_steps=10)` (`performance/reliability.py`) halts three identical actions in a row or more than ten steps.
- A degraded run sends `FALLBACK_REPLY`: "Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will follow up with you within one business day."
- `RunResult.status` is `ok`, `recovered` (a failure was caught and a retry worked) or `degraded` (the customer got the fallback).

`FailureInjection(research_empty, writing_toxic, research_loop, corrupt_message)` switches on one fault at a time.

---

## Step-by-Step Instructions

### Step 1 — Record the healthy run

Create `my_work/lab06_inject.py`:

```python
"""Lab 7.1 - inject four failures into the 3-agent Reply Desk and check each is caught."""
from agents.multi_agent import FALLBACK_REPLY, FailureInjection, run_multi_agent

REQUEST = "Customer asks: how long do refunds take?"
healthy = run_multi_agent(REQUEST)
print(f"healthy: status={healthy.status} steps={healthy.steps} delegations={healthy.delegations}")
```

A healthy run takes 3 steps: research → writer → finish. That is your baseline trajectory.

### Step 2 — Write the expectations before injecting

For each injection, decide what the system **should** detect and how it **should** end. Write it as data, then append the loop:

```python
INJECTIONS = {
    "research_empty": ("empty_research", "degraded"),
    "writing_toxic": ("unsafe_output", "degraded"),
    "research_loop": ("loop_detected", "degraded"),
    "corrupt_message": ("corrupted_message", "recovered"),
}
for flag, (expected_failure, expected_status) in INJECTIONS.items():
    run = run_multi_agent(REQUEST, inject=FailureInjection(**{flag: True}))
    ok = expected_failure in run.failure_types and run.status == expected_status
    if run.status == "degraded":
        ok = ok and run.final_reply == FALLBACK_REPLY
    print(f"{flag:<16} detected={run.failure_types} status={run.status:<9} steps={run.steps} -> {'PASS' if ok else 'FAIL'}")
```

```bash
uv run python -m my_work.lab06_inject
```

### Step 3 — Explain each outcome

In `my_work/lab06_notes.md`, answer for each injection:

1. **research_empty** — Why is "degrade after 1 step" better than letting the writer draft from nothing? (Which of the six failure modes would the writer commit?)
2. **writing_toxic** — Which check caught it, and where in the pipeline does it run?
3. **research_loop** — The research agent keeps asking "which plan is the customer on?". Which detector halts it and after how many steps?
4. **corrupt_message** — A message was altered in transit. Why is the result `recovered`, not `degraded`?

### Step 4 — Make it a regression test

Turn the loop into a parametrised pytest file (`my_work/test_lab06.py`) so CI fails if anyone weakens a safety net. Compare yours with `tests/trajectory/test_multi_agent.py`.

### Step 5 — Validate the hand-offs

```bash
uv run python demos/m07_communication_tests.py
```

Five communication checks: research before writer, every checksum valid, workers only talk to the supervisor, writer used the findings, finished within the step budget. Pick one and explain which failure pattern from Lecture 7.1 it guards against.

---

## Expected Output

```
healthy: status=ok steps=3 delegations=['research', 'writer', 'finish']
research_empty   detected=['empty_research'] status=degraded  steps=1 -> PASS
writing_toxic    detected=['unsafe_output'] status=degraded  steps=2 -> PASS
research_loop    detected=['loop_detected'] status=degraded  steps=3 -> PASS
corrupt_message  detected=['corrupted_message'] status=recovered steps=4 -> PASS
```

The reference demo prints the same result as a table:

```
$ uv run python demos/m07_lab_failure_injection.py
injected         detected           expected           status     steps  result
---------------  -----------------  -----------------  ---------  -----  ------
research_empty   empty_research     empty_research     degraded   1      PASS  
writing_toxic    unsafe_output      unsafe_output      degraded   2      PASS  
research_loop    loop_detected      loop_detected      degraded   3      PASS  
corrupt_message  corrupted_message  corrupted_message  recovered  4      PASS  
```

---

## Verification Checklist

- [ ] The healthy run is recorded (3 steps, status `ok`)
- [ ] Expectations were written before running the injections
- [ ] All four injections are detected with the expected failure type and status
- [ ] Every `degraded` run sends exactly `FALLBACK_REPLY` (no half-written draft reaches the customer)
- [ ] The notes explain each outcome; the pytest version runs in CI

---

## Common Pitfalls

1. **Testing only the final reply.** A degraded run and a healthy run can both produce polite text. Assert on `status`, `failure_types` and `steps`.
2. **Treating "no error raised" as success.** Failure propagation is silent: the Supervisor must notice empty findings, not just the absence of an exception.
3. **Loops without a budget.** A detector for identical actions misses A→B→A→B cycles; the 10-step budget is the safety net for those.
4. **Live runs vary.** With a real model, the step count of the healthy run can change. Test the invariants (failure detected, fallback sent), not exact step numbers.

---

## Extension Challenge

1. Combine two injections (`FailureInjection(research_empty=True, writing_toxic=True)`). Which one is reported, and is that what you want?
2. Add a fifth injection to your copy of `multi_agent.py`: the Writing Agent ignores the findings and invents a price. Which check catches it? (Hint: Module 4 faithfulness against the findings.)
3. Draw the failure cascade (diagram D11) for `research_empty` without the Supervisor's check: what would the customer have received?
