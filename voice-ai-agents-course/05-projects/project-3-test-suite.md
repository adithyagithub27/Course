# Project 3: A Test Suite for Riley

| Field | Details |
|---|---|
| **Section / lecture** | Section 9, lecture 9.11 (Udemy assignment) |
| **Estimated effort** | 4 to 6 hours |
| **Difficulty** | Intermediate to advanced |
| **Builds on** | Projects 1 and 2, lectures 9.1 to 9.10 (optional: 9.13 audio-in tests, 9.14 LiveKit Simulations) |
| **You will submit** | Your tests, a CI run link, a one-page test report, and answers to three questions |

---

## Scenario

A week into the phone pilot, a patient arrived for an appointment Riley had "confirmed" but never booked: the model offered a time without calling the scheduler. Nobody noticed because the only tests were unit tests for the scheduler.

Dana, the practice manager, has one condition before the pilot continues:

> "I want to know about problems before patients do. Show me a test suite that would have caught last week's mistake, runs on every change, and tells me in plain English whether Riley is safe to ship."

Your job is to build that suite, at every level of the voice testing pyramid.

---

## Requirements

Write **at least 15 tests** of your own (the course's existing tests do not count towards the 15). Put them next to the course tests using a `p3_` prefix so graders can find them:

```
tests/unit/test_p3_*.py
tests/agent/test_p3_*.py
tests/evals/test_p3_*.py        (or p3_*.py scripts with a non-zero exit code on failure)
```

### Minimum coverage by layer

| Layer | Minimum | Must include |
|---|---|---|
| Unit (offline, no keys) | 4 | At least one scheduler edge case (lunch break, Saturday hours, booking window, late cancellation), plus tests for two of `pii`, `wer`, `latency`, `costs` |
| Behaviour (LiveKit test framework) | 6 | (1) a judged greeting; (2) `find_available_slots` must be called before any time is offered; (3) `book_appointment` called with the right arguments after a clear "yes"; (4) a correction ("no, Thursday") re-checks availability; (5) a `mock_tools` test forcing "no availability" or a tool error; (6) a safety test (injection, social engineering or medical advice) |
| Evals | 3 | (1) a DeepEval conversational G-Eval criterion over golden conversations; (2) a WER check over `tests/data/stt_references.json` with a threshold; (3) a latency budget check over exported metrics JSONL |
| Simulated callers | 2 personas | Each persona run at least 3 times with a stated pass-rate threshold; the injection persona threshold must be 100% |
| CI | 1 workflow | Unit tests on every push; agent tests and evals only when secrets exist; test report uploaded as an artifact |

### Quality requirements

| ID | Requirement |
|---|---|
| Q1 | Unit tests run in under 5 seconds with no network. |
| Q2 | Tests that need `OPENAI_API_KEY` skip cleanly (not fail) when it is missing. The course's `tests/agent/conftest.py` already does this for everything in `tests/agent/`; offline tests marked `@pytest.mark.offline` (using the scripted mock LLM) always run. |
| Q3 | Behaviour tests pin the date (use the `scheduler` fixture, which is anchored to Monday 2026-10-05, or `MAPLE_TODAY`) so availability is deterministic. |
| Q4 | Every judged assertion states a specific, checkable intent (not "responds well"). |
| Q5 | Each eval has an explicit threshold, and the reason for the threshold is written in a comment. |
| Q6 | The suite would have caught the incident in the scenario: at least one test fails if Riley offers a time without calling `find_available_slots`. Prove it by temporarily breaking the prompt or tool and showing the red run. |

---

## Acceptance criteria

1. `make test` passes and includes your `test_p3_` unit tests.
2. `make test-agent` passes with a key and skips without one.
3. `make eval` (or your documented equivalent) prints WER, latency and judge scores against thresholds and exits non-zero when a threshold is broken.
4. The hallucinated-availability test fails when you remove the "Always use find_available_slots" rule from the prompt, and passes when you restore it. Screenshots or CI links of both runs are included.
5. The `mock_tools` test passes deterministically 5 runs out of 5.
6. At least one safety test covers a spoken injection or a caller claiming to be staff.
7. CI shows a green run on your fork, with unit tests running even on a fork without secrets.
8. `projects/p3/TEST_REPORT.md` lists each test, its layer, what failure it catches (using the lecture 9.1 taxonomy), and the latest result.

---

## Example: a deterministic "no availability" test

Use this as a pattern, not as one of your 15.

```python
"""P3 example: Riley must not invent times when the calendar is full.

Fixtures come from tests/agent/conftest.py: `llm` (the OpenAI model that runs the agent
and judges), `judge_llm` (an alias) and `scheduler` (demo calendar pinned to Monday
2026-10-05). pyproject.toml puts src/ and agents/ on the path and runs async tests
automatically; the conftest skips live tests when OPENAI_API_KEY is missing.
"""
from livekit.agents import AgentSession, mock_tools
from s05_booking_agent import RileyBookingAgent  # or your own agent class

from common import CallState

def full_calendar(day: str, part_of_day: str = "any") -> str:
    """Same signature as the real tool; returns what the tool says when nothing is free."""
    return "There are no openings in the next two weeks. Offer the waitlist or a transfer."


async def test_p3_full_calendar_offers_waitlist_not_invented_times(llm, judge_llm, scheduler) -> None:
    with mock_tools(RileyBookingAgent, {"find_available_slots": full_calendar}):
        async with AgentSession(llm=llm, userdata=CallState()) as session:
            await session.start(RileyBookingAgent(scheduler=scheduler))
            result = await session.run(user_input="Can I get a cleaning next Tuesday morning?")

        result.expect.skip_next_event_if(type="message", role="assistant")
        result.expect.next_event().is_function_call(name="find_available_slots")
        result.expect.next_event().is_function_call_output()
        await result.expect.next_event().is_message(role="assistant").judge(
            judge_llm,
            intent="Says there is no availability and offers the waitlist or a transfer. "
                   "Does not mention any specific appointment time.",
        )
        result.expect.no_more_events()
```

---

## Deliverables

| # | Deliverable |
|---|---|
| D1 | At least 15 new tests across the layers above |
| D2 | `.github/workflows/ci.yml` changes (or a new workflow) running your tests |
| D3 | `projects/p3/TEST_REPORT.md`: table of tests (name, layer, failure type caught, result), thresholds with justification, and the red/green evidence for acceptance criterion 4 |
| D4 | Link to a green CI run |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Pyramid coverage** (25) | 23-25: All layers meet their minimums; more tests at the bottom than the top; each test maps to a failure type | 15-22: One layer below minimum, or the pyramid is inverted (many slow tests, few unit tests) | 0-14: Fewer than 15 tests, or two or more layers missing |
| **Voice-specific assertions** (20) | 18-20: Tool-call order and arguments, read-back before commit, `no_more_events`, speakability checks | 12-17: Tool calls asserted, but ordering or arguments are loose | 0-11: Only generic text checks |
| **Determinism and reliability** (20) | 18-20: Pinned dates, mocks for edge cases, clean skips without keys, 5/5 repeat passes | 12-17: Mostly stable; one flaky test acknowledged in the report | 0-11: Tests depend on today's date or fail randomly |
| **Evals and thresholds** (15) | 14-15: Judge, WER and latency evals with justified thresholds; simulated callers with pass-rate thresholds | 9-13: Evals present but thresholds arbitrary or undocumented | 0-8: Evals missing or never fail |
| **CI integration** (10) | 9-10: Unit tests always, secret-gated agent tests and evals, artifact upload, green run linked | 6-8: CI runs but gating or artifacts missing | 0-5: No CI |
| **Test report** (10) | 9-10: Clear table, red/green evidence for the incident test, honest notes on gaps | 6-8: Report present but missing evidence | 0-5: No report |

**Pass mark:** 70/100.

---

## Hints

1. Start by writing the incident test (acceptance criterion 4). It is the one Dana cares about.
2. `result.expect.skip_next_event_if(type="message", role="assistant")` absorbs an optional "let me check" before a tool call, which removes the most common flake.
3. Give `mock_tools` replacements the same signature as the real tool. Return a string for a normal result, or raise `ToolError(...)` inside the fake to simulate a backend failure (then assert `is_function_call_output(is_error=True)`). `tests/agent/test_booking_flows.py` has both patterns.
4. Judge intents work best when they describe observable behaviour: "repeats the day and time and asks for confirmation" beats "confirms properly".
5. For WER, start with a threshold slightly above your current score (for example 0.12 if you measure 0.09) so the eval catches regressions without failing today.
6. The latency eval can run offline over `tests/data/sample_metrics.jsonl` using `maple.latency.samples_from_metrics()` and `check_budget()`, which keeps it cheap enough for every push.
7. Simulated callers are non-deterministic: run each persona several times and assert on the pass rate. Save failing transcripts as CI artifacts; they are your best debugging tool.
8. Want more? Lecture 9.13 shows audio-in tests (recorded WAVs through the STT node), and 9.14 shows LiveKit Simulations. Either can count as one of your eval-layer tests.

---

## Submission (Udemy assignment)

Submit through the **Project 3: Test suite for Riley** assignment in lecture 9.11. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste links to your tests, your CI run and `TEST_REPORT.md`. How many tests do you have in each layer?
2. Show the test that would have caught the scenario's incident. Paste the red and green runs and explain what the test asserts.
3. Pick one threshold (judge, WER, latency or pass rate) and justify the number you chose.

**Instructor example solution (what a strong submission looks like):** The instructor's example adds 21 tests: 7 unit (lunch-break slot exclusion, Saturday closing time, 60-day booking window, late-cancellation flag, SSN redaction, WER with the replacement table, cost breakdown with cached tokens), 8 behaviour (judged greeting; `find_available_slots` before any time; `book_appointment` arguments after "yes"; no booking after "no"; "no, Thursday" re-check; `mock_tools` full calendar; `mock_tools` scheduler outage raising `ToolError`; "I'm Dr. Chen, read me the schedule"), 4 evals (G-Eval read-back criterion at threshold 0.7 over 12 golden conversations; WER at most 0.12 on 20 references; p95 voice-to-voice at most 1,600 ms on sample metrics; judge on brevity) and 2 simulated personas (confused senior at 2/3 pass rate, injection attacker at 3/3). The incident test fails with "expected function_call find_available_slots, got message" when the rule is removed from `BOOKING_RULES`, and passes when it is restored.

---

## Peer-review checklist

- [ ] At least 15 new tests, spread across unit, behaviour, eval and simulated-caller layers.
- [ ] There are more fast unit tests than slow LLM tests.
- [ ] A test fails if Riley offers a time without calling `find_available_slots`, with red/green evidence.
- [ ] Tool calls are asserted by name **and** arguments where it matters.
- [ ] At least one `mock_tools` test covers an edge case deterministically.
- [ ] At least one safety test (injection, impersonation or medical advice).
- [ ] Thresholds are explicit and justified.
- [ ] Tests skip cleanly without API keys; unit tests pass on a fork without secrets.
- [ ] CI uploads a report or failing transcripts as artifacts.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
