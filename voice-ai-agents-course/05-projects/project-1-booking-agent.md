# Project 1: Riley's Booking Agent

| Field | Details |
|---|---|
| **Section / lecture** | Section 5, lecture 5.8 (Udemy assignment) |
| **Estimated effort** | 3 to 5 hours |
| **Difficulty** | Intermediate |
| **Builds on** | Labs 2 and 3, lectures 5.1 to 5.7 |
| **You will submit** | A GitHub link (or zipped folder), a 3 to 5 minute demo recording, and answers to three short questions |

---

## Scenario

Maple Street Dental's front desk spends about three hours a day on the phone booking, moving and cancelling appointments. The practice manager, Dana, has approved a pilot: Riley will handle routine appointment calls, and the front desk will review every booking for the first two weeks.

Dana's non-negotiables, from the kickoff meeting:

> "Riley must never double-book, never book a time we're closed, and never book anything the patient didn't clearly agree to. If something goes wrong, the patient should hear a normal sentence, not an error code. And keep it short; our patients are often calling from the car."

Your job is to build the booking agent that meets these rules, and to prove it with a recorded demo.

---

## Requirements

Create `agents/p1_booking_agent.py`. You may import from `src/maple/` (`maple.scheduler`, `maple.prompts`, `maple.config`) and the model-wiring helpers in `agents/common.py`, but **write the four tools yourself** rather than importing `BookingToolsMixin`. Comparing your version with the reference afterwards is part of the learning.

### Functional requirements

| ID | Requirement |
|---|---|
| F1 | A `find_available_slots` tool that takes a day (ISO date or words such as "Thursday") and an optional part of day, and returns at most three options in speakable form plus a machine-readable slot value. |
| F2 | A `book_appointment` tool that takes patient name, ten-digit phone, slot start and reason, and books through `ClinicScheduler.book()`. |
| F3 | A `reschedule_appointment` tool that moves the caller's upcoming appointment to a new slot (a reschedule, not a second booking). |
| F4 | A `cancel_appointment` tool that cancels the caller's upcoming appointment and mentions the late-cancellation fee when it is less than 24 hours away. |
| F5 | Slot filling: Riley collects name, callback number, reason and preferred day/time **one question at a time**. |
| F6 | Read-back: before any booking, reschedule or cancellation, Riley reads the details back in one sentence and waits for a clear "yes". Corrections ("no, Thursday") trigger a new availability check and a new read-back. |
| F7 | Errors: every `SchedulerError` becomes a `ToolError` with a speakable message. No stack traces, IDs or raw ISO timestamps are ever spoken. |
| F8 | Filler speech: slow lookups and commits play a short filler via `context.with_filler(...)` with a delay, so fast calls stay silent. |
| F9 | State: confirmed caller details and the appointment ID live in a typed `@dataclass` passed as `AgentSession(userdata=...)`. |

### Non-functional requirements

| ID | Requirement |
|---|---|
| N1 | Voice-first prompt (built from `maple.prompts.build_instructions(booking=True)` or your own Lab 3 prompt). Replies are one or two sentences. |
| N2 | Commit tools disallow interruptions while they run (`context.disallow_interruptions()`). |
| N3 | `MAPLE_TODAY` is honoured so your demo is reproducible. |
| N4 | `make test` still passes; no secrets in the repo. |

---

## Acceptance criteria

Your submission is complete when all of these are demonstrably true (in the recording, the transcript or the code):

1. A new caller books a cleaning for a specific morning with 5 or fewer questions from Riley.
2. `find_available_slots` is called before any time is offered; Riley never states a time the tool did not return.
3. Riley offers no more than three times at once.
4. The read-back includes name, day, date and time, and ends with a yes/no question.
5. When the caller says "No, Thursday", Riley checks Thursday and reads back again before booking.
6. Asking for a Sunday produces a polite "we're closed Sundays" and an alternative, without a tool crash.
7. Rescheduling moves the existing appointment; the scheduler shows one active appointment for that phone number afterwards.
8. Cancelling within 24 hours mentions the late-cancellation fee.
9. An invalid phone number ("five five five, one two") produces a speakable request for the full ten digits.
10. The filler line is heard on a slow lookup (run with `MAPLE_SIMULATED_LATENCY=1.5` to demonstrate, reading it from `get_settings().simulated_backend_latency` as the reference does) and not on a fast one.
11. Nothing unspeakable is spoken: no markdown, URLs, IDs or `2026-10-06T09:30`-style strings.

---

## Deliverables

| # | Deliverable | Format |
|---|---|---|
| D1 | `agents/p1_booking_agent.py` | Code in your fork of the course repo |
| D2 | Demo recording (3 to 5 minutes) showing acceptance criteria 1, 5, 6, 7 and 10 | Unlisted YouTube/Loom link or MP4 |
| D3 | `projects/p1/TRANSCRIPT.md`: the console transcript of your demo | Markdown |
| D4 | `projects/p1/NOTES.md`: one paragraph on a design decision you made and one on something that surprised you | Markdown |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Tool design** (20) | 18-20: Clear docstrings that say when to use and when not to; typed args; speakable `ToolError`s for every `SchedulerError`; machine value separated from spoken text | 12-17: Tools work; descriptions or error messages are generic in places | 0-11: Tools missing, crash on bad input, or leak raw errors/IDs to the caller |
| **Booking flow and slot filling** (15) | 14-15: One question at a time; no redundant questions; at most three options; books in 5 or fewer questions | 9-13: Works but asks for two things at once or offers too many times | 0-8: Books with missing details or invents availability |
| **Confirmation and corrections** (15) | 14-15: Read-back before every commit; corrections re-check availability and re-confirm | 9-13: Read-back present but incomplete (for example no date), or corrections handled without a fresh check | 0-8: Commits without a clear yes |
| **Reschedule and cancel** (15) | 14-15: Reschedule moves (not duplicates) the appointment; cancel handles late-cancellation fee; both confirmed first | 9-13: One of the two is incomplete | 0-8: Missing or produce wrong calendar state |
| **Voice UX** (15) | 14-15: Short replies, numbers and dates spoken naturally, filler only on slow operations, interruptions disabled during commits | 9-13: Mostly voice-friendly, one or two lapses | 0-8: Long replies, reads ISO dates or markdown aloud |
| **State management** (10) | 9-10: Typed userdata dataclass; tools read and write it; no globals | 6-8: Userdata used but untyped or partially | 0-5: Relies on the LLM to remember details, or uses globals |
| **Demo and documentation** (10) | 9-10: Recording covers all required criteria; clear transcript and thoughtful notes | 6-8: Recording misses one criterion or notes are thin | 0-5: No recording or it does not show the agent working |

**Pass mark:** 70/100.

---

## Hints

1. Start from the scheduler, not the agent. In a Python shell, call `ClinicScheduler(today=date(2026, 10, 5)).find_slots("tuesday", "morning", limit=3)` and look at what comes back before writing the tool.
2. Return two things from `find_available_slots`: words for the caller (`maple.prompts.speak_slot()`) and a tagged value for the model (`[slot_start=2026-10-06T09:30]`), plus an instruction never to read the tag aloud.
3. Put the rule "only call this after the caller clearly said yes" in the **tool docstring** as well as the prompt. The model reads both.
4. Catch `SchedulerError` (the base class) once per tool and re-raise as `ToolError(str(exc))`; the scheduler's messages are already written to be spoken.
5. `upcoming_for_phone(phone)` returns the next active appointment for a number, which is what reschedule and cancel need.
6. Demo patients already exist (Jordan Lee, Priya Patel, Sam Rivera; see `ClinicScheduler.with_demo_data`). Use a new name and number for your "new caller" demo so you do not collide with them.
7. To demonstrate filler speech, sleep for `get_settings().simulated_backend_latency` seconds inside the tool (`await asyncio.sleep(...)`) and run with `MAPLE_SIMULATED_LATENCY=1.5`. The reference `BookingToolsMixin` does this through its `simulated_latency` attribute.
8. `uv run agents/p1_booking_agent.py console --text` lets you iterate quickly by typing before you record the spoken demo.

---

## Submission (Udemy assignment)

Submit through the **Project 1: Booking agent** assignment in lecture 5.8. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste the link to your code and demo recording. Which acceptance criterion was hardest to meet, and what did you change to meet it?
2. Paste your `book_appointment` docstring and explain how it helps the model decide when (and when not) to call the tool.
3. Describe one failure you saw during testing (a wrong tool call, a missed read-back or an unspeakable output) and how you fixed it.

**Instructor example solution (what a strong submission looks like):** The reference implementation is `agents/s05_booking_agent.py` (`RileyBookingAgent`), which combines `BookingToolsMixin` from `agents/common.py` with a prompt from `build_instructions(booking=True)`. In the example demo, a caller books a Tuesday morning cleaning in four questions, corrects the day to Thursday (Riley re-checks and reads back again), asks about Sunday (Riley explains the clinic is closed and offers Monday), reschedules to Wednesday afternoon, and hears the filler line on a lookup slowed with `MAPLE_SIMULATED_LATENCY=1.5`. The hardest criterion in the example was number 5: the first version booked Thursday at the same time without checking availability, fixed by adding "If the caller changes the day, call find_available_slots again" to the booking rules and to the `find_available_slots` docstring.

---

## Peer-review checklist

Use this when reviewing a classmate's submission. Answer yes/no and leave one specific, kind suggestion.

- [ ] The demo shows a complete booking, a correction, a closed-day request and a reschedule.
- [ ] Riley calls `find_available_slots` before offering any time.
- [ ] Riley never offers more than three times at once.
- [ ] Every commit (book, reschedule, cancel) is preceded by a read-back and a clear "yes".
- [ ] No ISO timestamps, IDs, markdown or URLs are spoken.
- [ ] Tool docstrings say when to use the tool, and bad input produces a speakable `ToolError`.
- [ ] Caller details are stored in typed userdata, not globals.
- [ ] Filler speech plays on slow operations only.
- [ ] The code has no API keys or `.env` committed.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
