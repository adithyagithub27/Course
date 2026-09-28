# Challenges

Three "pause, then solution" challenges that sit between the labs and the projects. Each one is short, builds a portfolio artefact, and has a reference walkthrough in the lecture that follows the pause.

| Lecture | Challenge | Type | Time | Output |
|---|---|---|---|---|
| 4.7 | [Riley for your business](#challenge-47-riley-for-your-business) | Udemy assignment | 45 to 90 min | A voice-first prompt for a real business, plus one console transcript posted in Q&A |
| 5.9 | [Add a waitlist tool](#challenge-59-add-a-waitlist-tool) | Pause-then-solution (in lecture) | 30 to 60 min | `join_waitlist` tool with read-back, `ToolError`s and tests |
| 13.7 | [Domain swap: restaurant, salon or law office](#challenge-137-domain-swap) | Udemy assignment | 6 to 12 hours | A second, distinct portfolio agent re-skinned from your capstone |

---

## Challenge 4.7: Riley for your business

**Goal:** prove you can write a voice-first prompt for a business you know, not just for Maple Street Dental.

### Brief

Pick a real business you know well: a salon, restaurant, clinic, gym, garage, law office, your employer, or a family business. Using `10-resources/business-template.md`, write the instructions a receptionist agent for that business would need, run it in console mode, and post one transcript in the Q&A thread for lecture 4.7.

### Steps

1. Fill in `business-template.md`: business name and type, who calls and why (top five reasons), opening hours, ten facts callers ask about, things the agent must never do, when to hand off to a human, and how the business wants to sound.
2. Write the prompt as `MY_BUSINESS_PROMPT` in `agents/c47_my_business.py` (copy `agents/s04_voice_prompting.py`). Use the same blocks as `maple.prompts`: identity and AI disclosure, goal, style, output rules, facts policy, safety, escalation. Put the ten facts in the prompt for now; Section 7 moves them into a lookup tool.
3. Run it: `uv run agents/c47_my_business.py console` (or `console --text`).
4. Hold one realistic three-to-six-turn conversation, copy the transcript, and run `labs/voice_lint.py` from Lab 3 over the agent's replies.
5. Post in Q&A: business type (no need to name it), your prompt's identity and style blocks, the transcript, and one thing you changed after hearing it.

### Acceptance criteria

- [ ] The agent discloses it is an AI assistant for the business in its first or second sentence.
- [ ] Replies are one or two sentences; the lint flags at most one reply.
- [ ] At least one fact is answered correctly from the prompt, and one question outside the facts gets an honest "I'm not sure" plus an offer of a person or message.
- [ ] Numbers, times and prices are spoken naturally.
- [ ] There is at least one domain-specific "never do" rule (for example "never quote a repair price" for a garage).

### Common mistakes

| Mistake | Fix |
|---|---|
| Copying Maple's prompt and changing the name | Rewrite the "never do" and escalation rules for this business: that is where domains differ most |
| Listing facts as bullet points and getting bullets back | Keep facts in the prompt as plain sentences, and keep the "no lists" output rule |
| No human hand-off | Every business has a "get me a person" moment; name it |
| Real customer data in the transcript | Invent names and numbers before posting |

---

## Challenge 5.9: Add a waitlist tool

**Goal:** add a new tool end to end, and avoid the three mistakes almost everyone makes the first time.

### Spec (shown on screen; pause the video here)

> When a caller wants a day that has no suitable openings, Riley offers the waitlist. Add a tool
> `join_waitlist(name, phone, preferred_day)` backed by `scheduler.add_to_waitlist`.
> - Only offer it after `find_available_slots` found nothing suitable.
> - Read back name, phone and day, and get a clear yes, before adding.
> - Invalid input (bad phone, closed day, past date) must produce a speakable message.
> - Store the outcome in `CallState` (`call_outcome = "waitlisted"`).
> - Add tests.

`ClinicScheduler.add_to_waitlist(patient_name, phone, preferred_day, part_of_day="any")` already exists in `src/maple/scheduler.py`. It validates the name, normalises the phone number, parses the day, rejects closed, past and out-of-window days with speakable `SchedulerError` subclasses, and returns the existing entry instead of duplicating a request for the same phone and day. `scheduler.waitlist(day=None)` lists entries.

### Hints

1. Write the docstring first. It is the only thing the model reads to decide when to call the tool.
2. The read-back rule belongs in **both** the docstring and the booking rules in the prompt.
3. Catch `SchedulerError` and raise `ToolError(str(exc))`: the scheduler's messages are already speakable.
4. Return a sentence for Riley to say, and tell the model not to read the waitlist ID aloud.
5. Test the scheduler part offline first, then add one behaviour test with `mock_tools` forcing an empty `find_available_slots`.

### Solution outline

Add a mixin next to the booking tools (or directly on your agent class):

```python
from typing import Literal

from livekit.agents import RunContext, ToolError, function_tool

from common import CallState  # agents/common.py
from maple import prompts
from maple.scheduler import ClinicScheduler, SchedulerError


class WaitlistToolsMixin:
    """Adds join_waitlist (lecture 5.9)."""

    scheduler: ClinicScheduler

    @function_tool
    async def join_waitlist(
        self,
        context: RunContext[CallState],
        patient_name: str,
        phone: str,
        preferred_day: str,
        part_of_day: Literal["morning", "afternoon", "any"] = "any",
    ) -> str:
        """Put the caller on the waitlist for a day that has no suitable openings.

        Use this ONLY after find_available_slots found nothing that works for the caller and the
        caller said they want to be called if a slot opens. Before calling, read back the name,
        phone number and day, and wait for a clear yes. Do not use this to book appointments.

        Args:
            patient_name: The patient's full name.
            phone: A ten digit callback phone number.
            preferred_day: The day they want: an ISO date such as 2026-10-08, or words such as "Thursday".
            part_of_day: "morning", "afternoon" or "any".
        """
        try:
            entry = self.scheduler.add_to_waitlist(patient_name, phone, preferred_day, part_of_day)
        except SchedulerError as exc:
            raise ToolError(str(exc)) from exc

        state = context.userdata
        state.caller_name = entry.patient_name
        state.caller_phone = entry.phone
        state.call_outcome = "waitlisted"
        return (
            f"Added to the waitlist for {prompts.speak_date(entry.preferred_day)}. Tell the caller the "
            "front desk will call if a time opens up. Never read out the waitlist ID."
        )
```

The spec's `name` argument is called `patient_name` here to match `book_appointment`; consistent argument names across tools help the model reuse details it already collected. The optional `part_of_day` lets "Thursday morning" go straight through. The reference solution in `agents/s05_booking_agent.py` (`RileyBookingAgent.join_waitlist`) is the same tool defined directly on the agent class, and also reads back the caller's waitlist position via `scheduler.waitlist_position()`.

Then:

1. Add `WaitlistToolsMixin` to your agent's bases: `class RileyBookingAgent(WaitlistToolsMixin, BookingToolsMixin, Agent)`.
2. Extend the booking rules: "If no suitable time is available, offer the waitlist. Read back name, phone number and day before calling join_waitlist."
3. Add the scheduler tests below to `tests/unit/test_waitlist.py` (verified against the course scheduler).
4. Add one behaviour test: with `mock_tools(RileyBookingAgent, {"find_available_slots": no_slots})`, where `no_slots(day, part_of_day="any")` returns "There are no openings in the next two weeks. Offer the waitlist or a transfer.", the caller asks for Thursday, and the judged reply offers the waitlist without inventing a time. A second turn ("Yes, please add me") should produce a read-back, not an immediate `join_waitlist` call.

```python
from datetime import date

import pytest

from maple.scheduler import ClinicClosedError, ClinicScheduler, InvalidPhoneError, ValidationError

TODAY = date(2026, 10, 5)  # a Monday


def test_join_waitlist_for_thursday():
    sched = ClinicScheduler(today=TODAY)
    entry = sched.add_to_waitlist("Casey Morgan", "(512) 555-0161", "thursday")
    assert entry.preferred_day == date(2026, 10, 8)
    assert entry.phone == "5125550161"
    assert sched.waitlist("thursday") == [entry]


def test_same_caller_same_day_is_not_duplicated():
    sched = ClinicScheduler(today=TODAY)
    first = sched.add_to_waitlist("Casey Morgan", "512-555-0161", "2026-10-08")
    second = sched.add_to_waitlist("Casey Morgan", "5125550161", "thursday")
    assert first == second
    assert len(sched.waitlist()) == 1


def test_closed_day_is_rejected():
    sched = ClinicScheduler(today=TODAY)
    with pytest.raises(ClinicClosedError):
        sched.add_to_waitlist("Casey Morgan", "5125550161", "sunday")


@pytest.mark.parametrize(
    "name, phone, error",
    [("", "5125550161", ValidationError), ("Casey Morgan", "555 12", InvalidPhoneError)],
)
def test_bad_input_raises_speakable_errors(name, phone, error):
    sched = ClinicScheduler(today=TODAY)
    with pytest.raises(error) as exc:
        sched.add_to_waitlist(name, phone, "thursday")
    assert "?" in str(exc.value) or "." in str(exc.value)
```

### The three mistakes most people make

| Mistake | What you hear | Fix |
|---|---|---|
| **Vague description** (`"""Waitlist."""`) | Riley never offers the waitlist, or calls it when the caller only asked a question | Say when to use it, when not to, and what each argument means |
| **No read-back** | "Done, you're on the list!" with a misheard phone number | Read back name, phone and day; call the tool only after a clear yes (rule in docstring and prompt) |
| **Forgetting `ToolError`** | Silence or "Sorry, something went wrong" for a Sunday request | Convert `SchedulerError` to `ToolError(str(exc))` so Riley says "We're closed on Sundays" |

Two more worth checking: returning the raw `WaitlistEntry` (Riley reads out "W L dash zero zero one"), and not recording `call_outcome`, which makes the waitlist invisible in your Section 10 dashboards.

---

## Challenge 13.7: Domain swap

**Goal:** re-skin your capstone for a different business, keeping the architecture and the tests. This proves the skills transfer and gives you a second, distinct portfolio project.

### What changes and what stays

| Changes | Stays |
|---|---|
| FAQ file (`data/faq.md` equivalent) | Agent server, session wiring, turn handling, fallbacks |
| Tool schema (names, arguments, docstrings) | Tool patterns: read-back before commit, `ToolError`, filler, userdata |
| Business-logic module (the scheduler equivalent) | Pure-Python-first design with unit tests |
| Prompt blocks: identity, rules, safety, escalation | Output rules, security rules, verification pattern |
| Test data and judge intents | Test pyramid, CI workflow, latency and cost reporting |

Use `10-resources/business-template.md` to collect the facts before writing code. Pick **one** of the three briefs below.

### Brief A: "Nonna's Table", a 60-seat Italian restaurant

**Callers want to:** book, change or cancel a table; ask about hours, menu, dietary options, parking and private events.

**Suggested tools:** `find_tables(date, time, party_size)`, `book_table(name, phone, date, time, party_size, notes)`, `change_booking(phone, new_date, new_time, new_party_size)`, `cancel_booking(phone)`, `lookup_restaurant_info(question)`, `transfer_to_host(reason)`.

**Business rules to implement in pure Python:** tables for 2, 4 and 6; parties over 8 go to the events team; last seating 21:30; 15-minute grace period policy.

**Domain risk:** allergies. Riley must never promise a dish is safe for an allergy; she notes it on the booking and offers the host.

**Acceptance criteria:**
- [ ] A party of 4 books Friday at 19:30 with a read-back of name, date, time and party size.
- [ ] A party of 10 is not booked; Riley offers the events team.
- [ ] "Is the tiramisu nut-free?" gets no guarantee: a note is added and the host is offered.
- [ ] Menu and hours answers are grounded in the new FAQ; unknown questions get "I'm not sure".
- [ ] At least 15 of your capstone acceptance tests are adapted and passing (for example AT-02 becomes "book a table").
- [ ] Unit tests cover table assignment and the last-seating rule.

### Brief B: "Fade & Bloom", a hair salon with four stylists

**Callers want to:** book a service with a specific stylist or "anyone", change or cancel, ask prices and how long services take.

**Suggested tools:** `find_openings(service, stylist, day)`, `book_service(name, phone, service, stylist, start)`, `reschedule_service(phone, new_start)`, `cancel_service(phone)`, `lookup_salon_info(question)`, `transfer_to_front_desk(reason)`.

**Business rules to implement in pure Python:** services have different durations (cut 45 min, colour 120 min, blow-dry 30 min); each stylist has their own hours and days off; colour needs a patch test at least 48 hours before a first appointment.

**Domain risk:** variable-length services. A 120-minute colour must not overlap a stylist's other bookings or run past closing; the fixed 30-minute slots of the dental scheduler do not fit, so generalise `find_slots` to take a duration.

**Acceptance criteria:**
- [ ] "A colour with Jess on Saturday" only offers starts where 120 minutes fit in Jess's hours.
- [ ] "Anyone" searches all stylists and says which stylist each option is with.
- [ ] A first-time colour client is told about the patch test before booking.
- [ ] Price questions are answered as ranges from the FAQ, never invented.
- [ ] At least 15 capstone acceptance tests adapted and passing.
- [ ] Unit tests cover duration fitting, stylist days off and the patch-test rule.

### Brief C: "Harbor Legal", a four-lawyer family and employment law office

**Callers want to:** book a consultation, ask about practice areas and fees, reach their lawyer, or ask a legal question.

**Suggested tools:** `find_consultation_slots(practice_area, day)`, `book_consultation(name, phone, practice_area, start, other_party_name)`, `verify_client(phone, matter_number)`, `lookup_firm_info(question)`, `take_message(for_lawyer, summary)`, `transfer_to_reception(reason)`.

**Business rules to implement in pure Python:** consultations are 30 minutes and area-specific; new matters need the other party's name for a conflict check before booking; existing clients must be verified before any message about their matter is taken.

**Domain risks:** Riley must **never give legal advice** or predict outcomes, must not ask for case details beyond what intake needs (confidentiality), and must route urgent matters (for example "I've been served and the deadline is tomorrow", or anything involving safety) to a human immediately.

**Acceptance criteria:**
- [ ] "Can my employer fire me for this?" gets no legal opinion; Riley offers a consultation.
- [ ] A new employment-law caller books a consultation after giving the other party's name for the conflict check.
- [ ] An existing client cannot leave a matter-specific message until `verify_client` succeeds (enforced in code).
- [ ] An urgent deadline or safety concern is transferred or escalated immediately.
- [ ] Fees are answered only from the FAQ ("The first consultation is ...") with no promises.
- [ ] At least 15 capstone acceptance tests adapted and passing (the injection and impersonation tests matter even more here).

### Deliverables and submission

| # | Deliverable |
|---|---|
| D1 | A separate repository (or a clearly separate folder) with the re-skinned agent, FAQ, business-logic module and adapted tests |
| D2 | A 2 to 3 minute demo call |
| D3 | A README using the capstone portfolio template, plus a "What changed from Riley" table |

Submit through the **Domain swap** assignment in lecture 13.7 (see `06-assessments/assignments.md`).

### Self-check rubric

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| Domain fit (30) | 27-30: Tools and rules reflect how this business really works, including its specific risk | 18-26: Works but feels like the dental agent with new nouns | 0-17: Rules missing or wrong for the domain |
| Safety for the domain (25) | 23-25: Domain risk handled in code and prompt, with tests | 15-22: Handled in prompt only | 0-14: Not handled |
| Tests carried over (25) | 23-25: 15+ adapted acceptance tests passing, plus new unit tests for new rules | 15-22: 10 to 14 adapted | 0-14: Fewer than 10 |
| Portfolio quality (20) | 18-20: Clear README, demo and "what changed" table | 12-17: Present but thin | 0-11: Missing |
