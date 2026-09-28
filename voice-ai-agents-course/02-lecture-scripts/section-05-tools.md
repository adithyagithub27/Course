# Section 5: Tools: Booking, Rescheduling and Cancelling

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈70 min (10 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only; where talking time is shorter than the target duration, the rest is demo audio, typing, command output and on-screen dwell. Code-along lectures are paced below 140 words per minute to leave room for typing and running commands.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 5.1 | How function tools work in LiveKit | SL | 7:00 | ~825 |
| 5.2 | The clinic scheduler: pure Python first | SC | 8:00 | ~625 |
| 5.3 | Code-along: check availability and book | SC | 12:00 | ~950 |
| 5.4 | Confirmation and read-back patterns | SC | 8:00 | ~625 |
| 5.5 | Hiding latency while tools run | SC | 7:00 | ~475 |
| 5.6 | Reschedule, cancel and tool errors | SC | 9:00 | ~575 |
| 5.7 | Session state with userdata | SC | 6:00 | ~500 |
| 5.8 | Project 1: Booking agent | AS | 5:00 (2:00 video) | ~300 |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | 6:00 | ~525 |
| 5.10 | Quiz: Tools | QZ | 2:00 (0:45 video) | ~75 |

**Tool names used everywhere in this course (match the code exactly):** `find_available_slots`, `book_appointment`, `reschedule_appointment`, `cancel_appointment`, `join_waitlist` (this section); `lookup_clinic_info` (Section 7); `transfer_to_human`, `end_call` (Section 8). Agent class in this section: `RileyBookingAgent` (tools shared via `BookingToolsMixin` in `agents/common.py`). Userdata dataclass: `CallState`.

**Code-along convention:** students type into `agents/my_booking_agent.py`; the reference is `agents/s05_booking_agent.py` plus `BookingToolsMixin` in `agents/common.py`. Set `MAPLE_TODAY=2026-10-05` in `.env` (Lecture 2.6) so the demo calendar matches the video.

---

## Lecture 5.1 — How function tools work in LiveKit

| Field | Value |
|---|---|
| ID | 5.1 |
| Type | SL (slides with code) |
| Target duration | 7:00 (~825 spoken words, about 5:54 of talking at 140 wpm) |
| Learning objectives | 1. Explain the tool-calling loop: the LLM requests a tool, the framework runs it, the result goes back to the LLM, and the LLM speaks. 2. Write a `@function_tool` method whose docstring and type hints produce a clear schema. 3. Use `RunContext`, return values, `ToolError` and `max_tool_steps` correctly. |
| Prerequisites | Sections 3 and 4 |
| Files used | None (slides only; code appears in 5.3) |

### Script

[AVATAR]
So far, Riley can talk. It can't do anything. Ask it for an appointment and the best it can do is make one up, which is the worst thing it could do. Tools fix that. A tool is a Python function the LLM is allowed to call. And in LiveKit, turning a method into a tool takes one decorator.

[SLIDE 1: The tool-calling loop]
Diagram, circular:
1. Caller: "Do you have anything Thursday morning?"
2. LLM decides: call `find_available_slots(day="Thursday", part_of_day="morning")`
3. Framework runs your Python method
4. Result goes back to the LLM: "Open times: Thursday, October eighth at eight o'clock in the morning; ..."
5. LLM writes the reply: "I have eight, eight thirty or nine on Thursday. Which works?"
6. TTS speaks it

Here's the loop. The caller asks about Thursday morning. The LLM doesn't answer yet. It says, "I want to call find available slots, with day equals Thursday and part of day equals morning."

LiveKit sees that request and runs your Python method. The result goes back into the conversation. Then the LLM is called again, now with real data, and it writes the reply that Riley speaks.

Notice the LLM never touches your calendar. It only asks. Your code decides what actually happens. That's an important safety property, and we'll lean on it in Section eleven.

[SLIDE 2: A tool is a decorated method]
```python
from livekit.agents import Agent, RunContext, function_tool

class RileyBookingAgent(Agent):
    @function_tool
    async def find_available_slots(
        self,
        context: RunContext[CallState],
        day: str,
        part_of_day: Literal["morning", "afternoon", "any"] = "any",
    ) -> str:
        """Look up free appointment times. Always call this before offering times.

        Args:
            day: The day the caller wants: an ISO date such as 2026-10-06, or words such as
                "tomorrow" or "Thursday".
            part_of_day: "morning", "afternoon" or "any".
        """
        ...
```

Here's what a tool looks like. It's an async method on your agent class, with the function tool decorator on top.

Three parts of this method become the tool's description for the LLM. Let's look at each one.

[SLIDE 3: What the LLM actually sees]
```json
{
  "name": "find_available_slots",
  "description": "Look up free appointment times. Always call this before offering times.",
  "parameters": {
    "day": {"type": "string",
            "description": "The day the caller wants: an ISO date such as 2026-10-06, or words such as \"tomorrow\" or \"Thursday\"."},
    "part_of_day": {"type": "string",
                    "enum": ["morning", "afternoon", "any"], "default": "any"}
  },
  "required": ["day"]
}
```
- Method name → tool name
- Docstring first line → tool description
- `Args:` section → parameter descriptions
- Type hints → types; `Literal` → allowed values; defaults → optional

This is the schema LiveKit generates and sends to the LLM. I produced this one by introspecting the real framework, so it's exactly what the model receives.

The method name becomes the tool name. So name tools like verbs a receptionist would use. The first line of the docstring becomes the description. The Args section becomes a description for each parameter. And the type hints become types.

Look at part of day. Because I typed it as a Literal with three values, the LLM gets an enum. It can only choose morning, afternoon or any. That's a free guardrail. Every value you can restrict with a type is one less thing the LLM can get wrong.

And look at the examples in the day description. An ISO date, "tomorrow," or "Thursday." Examples in parameter descriptions work just like examples in prompts. The model copies them.

[SLIDE 4: RunContext: the tool's view of the call]
- `context.userdata`: your per-call state (`CallState`, lecture 5.7)
- `context.session`: the `AgentSession` (for `say`, etc.)
- `context.speech_handle`: the reply this tool call belongs to
- `context.with_filler(...)`: speak while slow work runs (lecture 5.5)
- `context.disallow_interruptions()`: protect critical moments (lecture 5.5)
- Not shown to the LLM: it's injected by the framework

The first parameter after self is special. RunContext. The LLM never sees it. LiveKit fills it in when it calls your tool.

It gives your tool a view of the live call. Context dot userdata is your own per-call state, like the caller's name. Context dot session is the session. And there are two helpers you'll use this section. With filler, which speaks a short line while slow work runs. And disallow interruptions, which protects the moment you commit a booking.

The square brackets, RunContext of CallState, are a type hint. They tell your editor what userdata holds, so you get autocomplete.

[SLIDE 5: What tools return]
- Return a short string or a small dict: it goes back to the LLM
- Write results for the LLM to *speak from*: "Open times: Thursday at 8:00, 8:30"
- Keep them small: every result is added to the prompt for the rest of the call
- Never return secrets or other patients' data

What should a tool return? Something the LLM can speak from. Usually a short string, sometimes a small dictionary.

Two tips. First, keep it small. Tool results become part of the conversation history, so a giant JSON blob makes every later turn slower and more expensive. Second, pre-format for speech when you can. We have helpers that turn a datetime into "Tuesday, October sixth at nine thirty in the morning." If the tool returns that, the LLM tends to repeat it exactly.

[SLIDE 6: When things go wrong: ToolError]
```python
from livekit.agents import ToolError

raise ToolError("Sorry, that time was just taken. Would you like the next available times?")
```
- Tells the LLM the call failed, with a message it can relay
- Write the message so it's safe to say out loud
- Other exceptions: logged, and the LLM gets a generic failure

Tools fail. The slot got taken. The date was a Sunday. The phone number was nine digits. For expected failures like these, raise ToolError with a message.

The LLM sees that the call failed, reads your message, and usually relays it naturally. So write the message to be spoken. "Sorry, that time was just taken. Would you like the next available times?" Our scheduler already writes its error messages this way, which you'll see next lecture.

Any other exception is treated as an unexpected crash. It's logged, and the LLM only learns that something went wrong. That's deliberate, so stack traces never get read to a caller.

[SLIDE 7: max_tool_steps]
```python
session = AgentSession(..., max_tool_steps=5)   # default is 3; Riley's booking agent uses 5
```
- How many rounds of tool calls the LLM may chain in one turn
- Example: find slots → (error, retry) → book = 3 steps
- Protects against loops that burn time and money

Last setting. Max tool steps. It limits how many rounds of tool calls the LLM can chain before it must speak. The default is three.

Riley's booking agent raises it to five, because one turn can chain a lookup, a retry after an error, and a booking. But it's still a hard ceiling. If the model gets stuck calling the same tool again and again, this limit stops it. In voice, a loop isn't just expensive. It's silence on the phone.

[AVATAR]
So a tool is a method, a docstring and good type hints. The docstring is a prompt. The types are guardrails. And the return value is something the LLM will say out loud. Keep all three in mind and your tools will be called correctly far more often.

**Recap:** A LiveKit tool is an `@function_tool` method whose name, docstring and type hints become the schema the LLM sees, with `RunContext` for call state, short speakable returns, and `ToolError` for expected failures.

**Transition:** Before we write any tools, let's look at the Python they'll call: the clinic scheduler, built and tested with no LLM at all.

### Speaker notes: common student mistakes / Q&A

- Mistake: forgetting the `Args:` section in the docstring. The tool still works, but parameters have no descriptions, and the LLM guesses formats.
- Mistake: making the tool synchronous and blocking (for example, a slow `requests.get`). Tools should be `async` and use async clients, or the whole call freezes.
- Mistake: returning a huge object (the whole calendar). It bloats every later turn. Return two or three options.
- "Can tools live outside the class?" Yes, you can pass standalone `@function_tool` functions via `tools=[...]`. Methods are simpler when tools share agent state, so the course uses methods.

---

## Lecture 5.2 — The clinic scheduler: pure Python first

| Field | Value |
|---|---|
| ID | 5.2 |
| Type | SC (screencast) |
| Target duration | 8:00 (~625 spoken words, about 4:28 of talking at 140 wpm) |
| Learning objectives | 1. Explain why business logic lives in `src/maple/scheduler.py`, outside the agent. 2. Use `ClinicScheduler` to find, book, reschedule and cancel appointments from a Python shell. 3. Read and run the scheduler unit tests. |
| Prerequisites | 5.1 |
| Files used | `03-code/src/maple/scheduler.py`, `03-code/tests/unit/test_scheduler.py` |

### Script

[AVATAR]
Here's a rule that will save you weeks. Your tools should be thin. The real logic, like opening hours, double-booking checks and cancellation policy, belongs in plain Python that knows nothing about LLMs. [PAUSE] Why? Because you can test plain Python in milliseconds, for free, a thousand times a day. You can't do that with a phone call.

[SLIDE 1: Two layers]
Diagram: top box "Riley's tools (`BookingToolsMixin` in agents/common.py, used by agents/s05_booking_agent.py)": thin wrappers, speak results, convert errors. Arrow down to bottom box "ClinicScheduler (src/maple/scheduler.py)": hours, slots, booking rules, errors. Right side: "Unit tests: offline, milliseconds" pointing at the bottom box.

Two layers. On top, Riley's tools. They translate between the conversation and the calendar. Underneath, the clinic scheduler. That's where every rule lives, and that's where most of the tests live.

[SCREEN: VS Code, open `src/maple/scheduler.py`. Scroll to `DEFAULT_HOURS`.]

Let's open the scheduler. It starts with the clinic's hours. Monday to Thursday, eight to five, with a lunch break from twelve to one. Friday, eight to two. Saturday, nine to one. Sunday, closed. Appointments are thirty-minute slots.

[SCREEN: Scroll to the exception classes.]

Next, the exceptions. There's a base class called SchedulerError, and one subclass for each problem. Clinic closed. Slot unavailable. Invalid phone. Past date. And so on.

Now look at the messages. "We're closed on Sundays. Would another day work?" Every message is a sentence you could say to a caller. That's deliberate. In the tools, we'll turn these into ToolErrors, and the LLM can relay them almost word for word.

[SCREEN: Scroll to `class ClinicScheduler`, `__init__`.]

Here's the scheduler class. The constructor takes `today`. Why pass in today instead of reading the clock? Because tests need a fixed date. If a test says "book tomorrow morning," tomorrow has to be the same day every time you run it.

[SCREEN: Terminal. Start a Python shell in the project environment.]

Let's try it in a Python shell.

[CODE: start a shell with the project installed]
```bash
uv run python
```

[CODE: type into the Python shell, one line at a time]
```python
>>> from datetime import date
>>> from maple.scheduler import ClinicScheduler
>>> sched = ClinicScheduler.with_demo_data(today=date(2026, 10, 5))
>>> [a.patient_name for a in sched.all_appointments()]
['Jordan Lee', 'Priya Patel', 'Sam Rivera']
```

`with_demo_data` gives us a scheduler with three fictional patients already booked. Today is Monday, October fifth, twenty twenty-six.

[CODE: find slots]
```python
>>> slots = sched.find_slots("tomorrow", part_of_day="morning", limit=3)
>>> [s.iso for s in slots]
['2026-10-06T08:00', '2026-10-06T08:30', '2026-10-06T09:00']
```

Find slots understands "tomorrow," weekday names and ISO dates. Part of day filters to morning or afternoon. And limit keeps it to three, because Riley should never read out a whole day of times.

[CODE: make it speakable]
```python
>>> from maple.prompts import speak_slot
>>> speak_slot(slots[0].start)
"Tuesday, October sixth at eight o'clock in the morning"
```

And here's the speech helper from Section four. The ISO string is for tools. The spoken version is for callers.

[CODE: book, then try to double-book]
```python
>>> appt = sched.book("Sam Ortiz", "(512) 555-0148", slots[0].start, reason="chipped tooth")
>>> appt.id, appt.phone
('APT-1004', '5125550148')
>>> sched.book("Ana Gomez", "512-555-0188", slots[0].start)
Traceback (most recent call last):
  ...
maple.scheduler.SlotUnavailableError: Sorry, that time was just taken. Would you like to hear the next available times?
```

Booking returns an appointment with an ID, and the phone number normalized to ten digits. Now watch. I try to book the same slot for someone else. Slot unavailable, with a sentence Riley can say.

[CODE: closed day]
```python
>>> sched.find_slots("sunday")
Traceback (most recent call last):
  ...
maple.scheduler.ClinicClosedError: We're closed on Sundays. Would another day work?
```

And asking for Sunday raises clinic closed. Every rule, visible and testable, with no LLM involved.

[SCREEN: Scroll through `reschedule`, `cancel`, `find_by_phone`, `upcoming_for_phone` in the editor.]

The rest of the class follows the same pattern. Reschedule moves an appointment and checks the new slot. Cancel frees the slot. Find by phone and upcoming for phone let Riley look up a caller's existing appointment, which we need for rescheduling.

[SCREEN: Open `tests/unit/test_scheduler.py`. Scroll to the `sched` fixture, then to `test_double_booking_raises`.]

Now the tests. At the top of the file, a fixture builds a fresh scheduler with today fixed to Monday, October fifth. Every test gets its own empty calendar.

[CODE: from `tests/unit/test_scheduler.py` (shown, not typed)]
```python
MONDAY = date(2026, 10, 5)  # a Monday


@pytest.fixture
def sched() -> ClinicScheduler:
    return ClinicScheduler(today=MONDAY)


def test_double_booking_raises(sched: ClinicScheduler) -> None:
    sched.book("Ana Gomez", "512-555-0188", "2026-10-06T09:30", "cleaning")
    with pytest.raises(SlotUnavailableError):
        sched.book("Ben Ortiz", "512-555-0199", "2026-10-06T09:30", "checkup")


def test_all_errors_are_scheduler_errors_with_speakable_text(sched: ClinicScheduler) -> None:
    with pytest.raises(SchedulerError) as info:
        sched.find_slots("sunday")
    message = str(info.value)
    assert message.endswith("?") or message.endswith(".")
    assert "Error" not in message
```

Here's the double-booking test. Book a slot. Try to book it again. Expect the error. No network, no keys, no randomness.

And look at the second one. It checks that error messages are speakable: they end like a sentence, and they don't contain the word "Error." That's a voice-specific unit test. It protects the messages Riley will read to callers.

[CODE: run just the scheduler tests]
```bash
uv run pytest tests/unit/test_scheduler.py -q
```

[DEMO: All scheduler tests pass in well under a second.]

All green in a fraction of a second.

[AVATAR]
Here's why this matters so much for voice. When a booking goes wrong on a call, there are two suspects. The LLM misunderstood, or the calendar logic is wrong. With the logic pinned down by unit tests, you can rule out the second suspect instantly. And in Section nine, you'll test the first suspect with behavior tests.

**Recap:** The scheduler holds every booking rule in plain, deterministic Python with speakable errors, so the agent's tools can stay thin and the rules can be tested in milliseconds.

**Transition:** Now let's give Riley its first two tools, find available slots and book appointment, and wire them to this scheduler.

### Speaker notes: common student mistakes / Q&A

- Mistake: calling `datetime.now()` inside business logic. Tests become flaky around midnight and on weekends. Inject `today`, as the scheduler does.
- Mistake: letting the LLM compute dates ("what's next Thursday?"). Let the scheduler parse "Thursday" relative to an injected date.
- "Why an in-memory calendar instead of a database?" To keep the course self-contained. Swapping in a real calendar API later only changes this layer, not the tools or tests above it.
- `ModuleNotFoundError: maple` in the shell means you ran plain `python`. Use `uv run python` so the project package is installed.

---

## Lecture 5.3 — Code-along: check availability and book

| Field | Value |
|---|---|
| ID | 5.3 |
| Type | SC (code-along) |
| Target duration | 12:00 (~950 spoken words, about 6:47 of talking at 140 wpm) |
| Learning objectives | 1. Write the `find_available_slots` and `book_appointment` tools as thin wrappers around `ClinicScheduler`. 2. Design tool results that are speakable and carry machine values (`slot_start`) the LLM must not read aloud. 3. Explain slot filling: how required tool arguments make the LLM collect name, phone, reason and time. |
| Prerequisites | 5.1, 5.2 |
| Files used | You type: `03-code/agents/my_booking_agent.py`. Reference: `03-code/agents/s05_booking_agent.py` and `BookingToolsMixin` in `03-code/agents/common.py`. Also `03-code/src/maple/scheduler.py`, `03-code/src/maple/prompts.py`. |

### Script

[AVATAR]
This is the lecture where Riley stops talking about appointments and starts booking them. Two tools. One to check the calendar, one to book. By the end, you'll book a real slot, in a real in-memory calendar, by voice.

[SCREEN: VS Code. Open `.env`, confirm `MAPLE_TODAY=2026-10-05` is still set from Lecture 2.6. Then create `agents/my_booking_agent.py`.]

Quick check first. Make sure MAPLE_TODAY is still set in your dot env, so your calendar matches mine. Then create a new file, `my_booking_agent.py`.

A note on where this code ends up. We're writing the tools as methods on our agent class, in this file, so you can see everything in one place. In the reference repo, these exact methods live in a shared class in `common.py`, so later sections can reuse them. I'll show you that refactor at the end of Lecture 5.7.

[CODE: step 1, imports and the agent shell]
```python
"""My booking agent: the code-along for Lectures 5.3 to 5.7."""

from __future__ import annotations

from typing import Literal

from common import (
    CallState,
    create_session,
    describe_appointment,
    get_scheduler,
    get_settings,
    prewarm,
)
from livekit.agents import Agent, AgentServer, JobContext, RunContext, cli, function_tool

from maple import prompts
from maple.scheduler import parse_day


class RileyBookingAgent(Agent):
    def __init__(self) -> None:
        self.scheduler = get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(today=self.scheduler.today, booking=True),
        )

    async def on_enter(self) -> None:
        self.session.say(prompts.GREETING)
```

The imports should look familiar. From common: call state, create session, a helper that describes an appointment in words, the shared scheduler and settings. From LiveKit: the function tool decorator and RunContext, which we met in Lecture 5.1.

In the constructor, we grab the scheduler first. `get_scheduler` returns one in-memory calendar per process, loaded with our three demo patients. Then the instructions, with two changes from Section four. Today's date comes from the scheduler, so the prompt and the calendar always agree. And booking equals true switches on the booking rules block.

And `on_enter` greets with the fixed line, like last section.

[SCREEN: Split view: `src/maple/prompts.py` `BOOKING_RULES` on the right.]

Let's glance at those booking rules, because they drive how Riley collects information. Collect, one at a time, the caller's full name, a phone number, the reason and a preferred day and time. Always use the find available slots tool before offering times. Never invent availability. And offer at most three options.

[CODE: step 2, the availability tool]
```python
    @function_tool
    async def find_available_slots(
        self,
        context: RunContext[CallState],
        day: str,
        part_of_day: Literal["morning", "afternoon", "any"] = "any",
    ) -> str:
        """Look up free appointment times. Always call this before offering times.

        Args:
            day: The day the caller wants: an ISO date such as 2026-10-06, or words such as
                "tomorrow" or "Thursday".
            part_of_day: "morning", "afternoon" or "any".
        """
        target = parse_day(day, self.scheduler.today)
        slots = self.scheduler.find_slots(target, part_of_day, limit=3)
        if not slots:
            return f"Nothing is free on {prompts.speak_date(target)}. Offer to check another day."

        options = "; ".join(f"{prompts.speak_slot(s.start)} [slot_start={s.iso}]" for s in slots)
        return (
            f"Open times: {options}. Offer these to the caller in words. "
            "Use the slot_start value when booking; never read it aloud."
        )
```

Now the first tool. The decorator, the RunContext, a day as a string, and part of day as a Literal, so the model can only pick morning, afternoon or any.

The docstring repeats the most important rule: always call this before offering times. Yes, it's also in the prompt. Tool descriptions are read at the exact moment the model decides what to do, so repeating critical rules here works.

The body is three lines of real work. Parse the day relative to the clinic's today. Ask the scheduler for up to three slots. If there are none, say so in words.

Now look closely at the return value, because this is the most important design decision in the lecture. Each option has two parts. The spoken version, "Tuesday, October sixth at nine o'clock in the morning." And a machine value in square brackets, slot start equals an ISO timestamp.

Why both? The LLM needs the spoken version to talk to the caller. And it needs the exact ISO value to pass back into the booking tool. If we only gave it words, it would have to convert "Tuesday at nine" back into a timestamp, and that's where mistakes creep in. Then the last sentence tells it how to use each part: offer the words, book with the slot start, and never read the brackets aloud.

[CODE: step 3, the booking tool]
```python
    @function_tool
    async def book_appointment(
        self,
        context: RunContext[CallState],
        patient_name: str,
        phone: str,
        slot_start: str,
        reason: str,
    ) -> str:
        """Book a new appointment. Only call this AFTER reading the details back and the caller
        clearly said yes.

        Args:
            patient_name: The patient's full name.
            phone: A ten digit callback phone number.
            slot_start: The exact slot_start returned by find_available_slots, e.g. 2026-10-06T09:30.
            reason: Short reason for the visit, e.g. "cleaning" or "tooth pain".
        """
        appt = self.scheduler.book(patient_name, phone, slot_start, reason)
        return (
            f"Booked: {describe_appointment(appt)}. Confirm the day and time once and mention "
            "the 24 hour cancellation policy."
        )
```

The second tool, book appointment. Four arguments, and none of them have defaults. That's deliberate, and it's how slot filling works.

[SLIDE 1: Slot filling, for free]
- Required arguments: `patient_name`, `phone`, `slot_start`, `reason`
- The LLM can't call the tool until it has all four
- The prompt says: ask for them one at a time
- Result: a natural, one-question-at-a-time conversation

Because every argument is required, the model can't call this tool until it has a name, a phone number, a slot and a reason. So it asks for them. And because the prompt says "one at a time," it asks for them one question per turn. You don't write a state machine. The schema and the prompt create the conversation flow.

Notice the slot start description: the exact slot start returned by find available slots. That links the two tools together.

The body is one line: book it in the scheduler. The return tells Riley what to say next: confirm the day and time once, and mention the twenty-four hour cancellation policy.

[CODE: step 4, the server and entrypoint]
```python
server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    session = create_session(get_settings(), proc=ctx.proc, max_tool_steps=5)
    await session.start(agent=RileyBookingAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
```

And the entrypoint, the same pattern as Section four. One new argument: max tool steps equals five. The default is three, and a single turn can chain a lookup, a retry and a booking, so we give it some room.

[SCREEN: Terminal.]

[CODE: run it]
```bash
uv run python agents/my_booking_agent.py console
```

[DEMO: Full booking by voice.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**You:** I'd like to book a cleaning. Do you have anything Thursday afternoon?

**Riley:** I have Thursday, October eighth at one, one thirty or two in the afternoon. Which works best?

**You:** Two o'clock.

**Riley:** Great. Can I get your full name?

**You:** Alex Kim.

**Riley:** Thanks. What's the best phone number to reach you?

**You:** Five one two, five five five, zero one six six.

**Riley:** Just to confirm: Alex Kim, Thursday, October eighth at two in the afternoon, for a cleaning. Shall I go ahead?

**You:** Yes.

**Riley:** You're booked for Thursday at two. Please give us twenty-four hours' notice if you need to cancel.

[SCREEN: Scroll up in the terminal log. Highlight the function call lines.]

Now the logs. Here's the first tool call: find available slots, with day equals Thursday and part of day equals afternoon. Here's the result, with the slot start values in brackets. And Riley never read them out loud.

And here's book appointment, with the name, the phone number, slot start equals October eighth at fourteen hundred, and reason equals cleaning. The model copied the exact slot start from the first tool. That's the design working.

[AVATAR]
Here's what you just built. The model decides what to do. The tools do it, with real rules and real data. And the prompt shapes the conversation around them. Notice Riley also read everything back before booking. That's not luck, and it's not quite guaranteed yet either. That's next lecture.

**Recap:** Two thin tools wrap the scheduler, return speakable options plus exact `slot_start` values, and use required arguments so the LLM naturally collects name, phone, reason and time.

**Transition:** Next, we'll make read-backs reliable and handle the caller who says "no, Thursday" at the last second.

### Speaker notes: common student mistakes / Q&A

- Mistake: returning a list of `datetime` objects or a big dict. The LLM then formats dates itself, inconsistently. Return speakable text plus exact machine values.
- Mistake: giving `book_appointment` optional arguments with defaults. The LLM will happily book with the defaults instead of asking.
- Mistake: forgetting `MAPLE_TODAY`. Your slots won't match the video, and "Thursday" may be fully booked in your calendar.
- "Riley read out 'slot start equals...'" Check the tool return still ends with "never read it aloud", and that the output rules block is in the prompt (`build_instructions` always includes it).

---

## Lecture 5.4 — Confirmation and read-back patterns

| Field | Value |
|---|---|
| ID | 5.4 |
| Type | SC (code-along and demo) |
| Target duration | 8:00 (~625 spoken words, about 4:28 of talking at 140 wpm) |
| Learning objectives | 1. Explain why irreversible actions need an explicit read-back and a clear "yes" before the tool runs. 2. Implement read-backs with prompt rules, tool descriptions and speakable data. 3. Handle corrections like "no, Thursday" without double-booking. |
| Prerequisites | 5.3 |
| Files used | Your `agents/my_booking_agent.py`; `03-code/src/maple/prompts.py` (`BOOKING_RULES`); reference `03-code/agents/s05_booking_agent.py` |

### Script

[AVATAR]
On a website, you get a confirmation page. Name, date, time, and a big "Confirm" button. [PAUSE] On the phone, there's no page. So the agent has to be the confirmation page. That's what a read-back is: one sentence that repeats every important detail, followed by a question, before anything irreversible happens.

[SLIDE 1: Why read-backs matter on voice]
- STT mishears: "fifteen" vs "fifty", "Tuesday" vs "Thursday"
- Callers change their minds mid-flow
- A wrong booking costs a real person a wasted trip
- Rule: read back, ask, wait for a clear yes, then act

Three reasons. Speech-to-text mishears exactly the things that matter. "Fifteen" and "fifty." "Tuesday" and "Thursday." Callers change their minds halfway through. And a wrong booking costs a real person a wasted trip. So the rule is: read back, ask, wait for a clear yes, then act.

[SLIDE 2: A good read-back]
"Just to confirm: Alex Kim, Thursday, October eighth at two in the afternoon, for a cleaning. Shall I go ahead?"
- One sentence, every critical field
- Weekday plus date (catches "Tuesday vs Thursday")
- Ends with a yes-or-no question

Here's a good read-back. One sentence. Every critical field. The weekday and the date, which catches the "Tuesday versus Thursday" mistake, because the caller hears both. And it ends with a yes-or-no question, so the next turn is simple.

[SCREEN: VS Code, `src/maple/prompts.py`, `BOOKING_RULES`. Highlight the read-back and correction lines.]

[CODE: the read-back rules in `BOOKING_RULES` (shown, not typed)]
```python
- Before calling book_appointment, reschedule_appointment or cancel_appointment, read the details
  back in one sentence (name, day, date and time) and ask "Shall I go ahead?". Only call the tool
  after the caller clearly says yes.
- If the caller corrects you, for example "no, Thursday", update the detail and read it back again.
```

Riley's read-back is built from three layers, and you already have all of them. Layer one, the prompt. These two rules in the booking block. Read back in one sentence, ask "Shall I go ahead?", and only call the tool after a clear yes. And if the caller corrects you, update the detail and read it back again.

[CODE: layer two, the tool description (already in your file)]
```python
        """Book a new appointment. Only call this AFTER reading the details back and the caller
        clearly said yes.
```

Layer two, the tool description. The word "after" is in capitals on purpose. This text is in front of the model at the exact moment it considers calling the tool.

Layer three is the data. Because find available slots returns "Thursday, October eighth at two in the afternoon," the read-back uses the exact same words. The caller hears a consistent date every time.

[SCREEN: Terminal. Run `uv run python agents/my_booking_agent.py console`.]

Now let's test the hard case. A caller who changes their mind right at the end.

[DEMO: Correction flow.]

**You:** I need a checkup on Tuesday morning.

**Riley:** I have Tuesday, October sixth at eight, eight thirty or nine in the morning. Which works?

**You:** Eight thirty.

*(name and phone collected, as in 5.3)*

**Riley:** Just to confirm: Maria Santos, Tuesday, October sixth at eight thirty in the morning, for a checkup. Shall I go ahead?

**You:** Oh, no, sorry. Thursday. Can we do Thursday instead?

**Riley:** No problem. Let me check Thursday. I have Thursday, October eighth at eight, eight thirty or nine in the morning. Which works?

**You:** Eight thirty again.

**Riley:** Just to confirm: Maria Santos, Thursday, October eighth at eight thirty in the morning, for a checkup. Shall I go ahead?

**You:** Yes.

**Riley:** You're booked for Thursday at eight thirty.

[SCREEN: Terminal log. Highlight: two `find_available_slots` calls (Tuesday, then Thursday), and exactly one `book_appointment` call with the Thursday `slot_start`.]

Let's check the log, because the log is the truth. Two calls to find available slots. Tuesday, then Thursday. And exactly one call to book appointment, with the Thursday slot. Nothing was booked for Tuesday. The correction happened before the commit, which is exactly why the read-back comes before the tool call.

[SLIDE 3: What to read back, per action]
| Action | Read back |
|---|---|
| Book | Name, weekday + date, time, reason |
| Reschedule | Old time → new time |
| Cancel | Which appointment, plus any late-cancellation fee |
| Phone number | Digits in three groups |
| Last name | Spelled letter by letter (Section 4) |

Here's the read-back checklist for every action. Booking: name, weekday and date, time and reason. Rescheduling: the old time and the new time, so there's no confusion about which one is moving. Cancelling: which appointment, and any fee. Phone numbers: in three groups. Last names: spelled out.

[SLIDE 4: Prompts are not guarantees]
- The model follows the read-back rule most of the time, not always
- Section 9: a test fails if `book_appointment` runs before a "yes"
- Section 11: code-level confirmation gates for irreversible actions

[AVATAR]
Now, an honest warning. Everything we did here is instructions. The model follows them most of the time. Most of the time isn't good enough for a calendar. So we'll add two more safety nets later. In Section nine, you'll write a test that fails if book appointment ever runs before the caller says yes. And in Section eleven, you'll add confirmation gates in code for irreversible actions. Prompt first, then tests, then code.

**Recap:** Read back every critical detail in one sentence, ask a yes-or-no question, act only on a clear yes, and re-read after any correction, using the prompt, the tool description and speakable tool data together.

**Transition:** You may have noticed a pause while Riley checks the calendar, so next we'll hide that latency with filler speech.

### Speaker notes: common student mistakes / Q&A

- Mistake: accepting "sure, I guess" or "hmm" as a yes. Tighten the rule: "a clear yes such as yes, yeah, correct, or go ahead."
- Mistake: reading back the date without the weekday. Weekday plus date catches the most common STT confusion.
- Mistake: a read-back that's three sentences long. One sentence, then the question.
- "Can I make the model call a separate `confirm` tool?" You can, but it adds a round trip. Tests and code gates (Sections 9 and 11) are a better use of latency.

---

## Lecture 5.5 — Hiding latency while tools run

| Field | Value |
|---|---|
| ID | 5.5 |
| Type | SC (code-along) |
| Target duration | 7:00 (~475 spoken words, about 3:24 of talking at 140 wpm) |
| Learning objectives | 1. Use `context.with_filler(..., delay=...)` so Riley speaks only when a tool is actually slow. 2. Compare filler with a manual `session.say`. 3. Protect commits with `context.disallow_interruptions()`. |
| Prerequisites | 5.3, 1.4 |
| Files used | Your `agents/my_booking_agent.py`; `03-code/.env` (`MAPLE_SIMULATED_LATENCY`); reference `BookingToolsMixin` in `03-code/agents/common.py` |

### Script

[AVATAR]
Remember the latency budget? Tool calls were the item that blew it: anywhere from three hundred milliseconds to a second and a half. [PAUSE] Our in-memory calendar is instant, but a real practice-management system isn't. So first, let's make our calendar slow on purpose. Then let's make Riley handle it gracefully.

[CODE: step 1, add to `.env`]
```bash
MAPLE_SIMULATED_LATENCY=2
```

In dot env, set MAPLE_SIMULATED_LATENCY to two. Every booking tool will now wait two seconds, like a slow API.

[CODE: step 2, a slow backend call in `RileyBookingAgent`]
```python
import asyncio

class RileyBookingAgent(Agent):
    def __init__(self) -> None:
        self.scheduler = get_scheduler()
        self.simulated_latency = get_settings().simulated_backend_latency
        super().__init__(
            instructions=prompts.build_instructions(today=self.scheduler.today, booking=True),
        )

    async def _backend_call(self) -> None:
        """Mimic a slow practice-management API so filler speech is audible."""
        if self.simulated_latency > 0:
            await asyncio.sleep(self.simulated_latency)
```

In the agent, read the simulated latency from settings, and add a small helper that sleeps for that long. Note `asyncio.sleep`, not `time.sleep`. A blocking sleep would freeze the whole call, including audio.

[CODE: step 3, call it from `find_available_slots`, then run]
```python
        await self._backend_call()
        target = parse_day(day, self.scheduler.today)
```

Call it at the start of find available slots, and run the agent.

[DEMO: Ask for Thursday afternoon. Two seconds of dead air before Riley answers.]

Listen. [PAUSE] [PAUSE] Two seconds of silence. On a phone, that's long enough for a caller to say "hello?" and step on Riley's answer.

[CODE: step 4, wrap slow work in a filler]
```python
        async with context.with_filler("One moment while I check the schedule.", delay=0.8):
            await self._backend_call()
            target = parse_day(day, self.scheduler.today)
            slots = self.scheduler.find_slots(target, part_of_day, limit=3)
```

Now the fix. `context.with_filler`. It's an async context manager. Put the slow work inside it. If the work is still running after the delay, Riley says the filler line. Here, "One moment while I check the schedule," after eight tenths of a second.

[DEMO: Same request. After a short beat, "One moment while I check the schedule." Then the options.]

Much better. The caller hears a human-sounding acknowledgement, and the silence has a reason.

[SLIDE 1: Why the delay matters]
- Tool finishes in 300 ms: no filler, answer arrives fast
- Tool takes 2 s: filler at 0.8 s, answer after
- A filler on every fast call sounds robotic and wastes time
- Fillers speak only when the session is idle

Here's why the delay is the clever part. If the tool finishes quickly, the filler never plays, and the answer just arrives. The filler only plays when you actually need it. If Riley said "one moment" before every single answer, even the instant ones, it would sound robotic, and it would add time to every turn.

[SLIDE 2: Filler vs `session.say`]
```python
# Manual: always speaks, even if the tool is fast
context.session.say("Let me check that for you.")

# with_filler: speaks only if the work is still running after `delay`
async with context.with_filler("One moment while I check the schedule.", delay=0.8):
    ...
```

You could do this manually, by calling `session.say` at the top of the tool. That always speaks, fast or slow. Use `session.say` for lines that must always be said, and `with_filler` for lines that cover latency.

[CODE: step 5, protect the commit]
```python
    @function_tool
    async def book_appointment(self, context: RunContext[CallState], patient_name: str,
                               phone: str, slot_start: str, reason: str) -> str:
        """..."""
        context.disallow_interruptions()  # a half-finished booking is worse than a short wait
        async with context.with_filler("Booking that for you now.", delay=0.8):
            await self._backend_call()
            appt = self.scheduler.book(patient_name, phone, slot_start, reason)
```

Now booking. Two changes. A filler, "Booking that for you now." And one important line at the top: `context.disallow_interruptions`.

Why? If the caller says something while the booking is being written, the default behavior is to interrupt the current reply. For a lookup, that's fine. For a booking, an interruption mid-commit leaves everyone unsure whether the appointment exists. So for commits, we finish the action and confirm it, then listen. A half-finished booking is worse than a short wait.

[DEMO: Book, and talk over Riley during "Booking that for you now." Riley finishes and confirms.]

[SLIDE 3: Filler lines that work]
- Short: under about two seconds of speech
- Specific: "check the schedule", not "processing"
- Varied per tool: lookup, booking, moving, cancelling
- Never promise a result: "Let me check", not "I've found you a slot"

[AVATAR]
A few rules for good filler lines. Keep them short. Make them specific to the tool. Use a different line per tool, so it doesn't sound like a loop. And never promise a result you don't have yet.

When you're done experimenting, set the simulated latency back to zero, or leave it at one to keep hearing the fillers.

**Recap:** `context.with_filler` speaks a short line only when a tool is actually slow, `session.say` is for lines that must always be said, and `disallow_interruptions` protects commits like bookings.

**Transition:** Next, Riley learns to reschedule and cancel, and to turn scheduling errors into speakable `ToolError` messages.

### Speaker notes: common student mistakes / Q&A

- Mistake: `time.sleep()` or a blocking HTTP client inside a tool. It freezes audio for everyone in that process. Use async clients.
- Mistake: `delay=0`. The filler plays on every call, even instant ones.
- Mistake: calling `disallow_interruptions()` in the lookup tool. Callers should be able to redirect a search.
- "Can the filler repeat for very slow tools?" Yes: `with_filler` accepts `interval=` and `max_steps=` to repeat, for example every four seconds, at most twice.

---

## Lecture 5.6 — Reschedule, cancel and tool errors

| Field | Value |
|---|---|
| ID | 5.6 |
| Type | SC (code-along) |
| Target duration | 9:00 (~575 spoken words, about 4:06 of talking at 140 wpm) |
| Learning objectives | 1. Implement `reschedule_appointment` and `cancel_appointment` as thin wrappers with read-backs. 2. Convert `SchedulerError` into speakable `ToolError` messages. 3. Write error messages that tell the LLM how to recover (retry prompts). |
| Prerequisites | 5.3 to 5.5 |
| Files used | Your `agents/my_booking_agent.py`; `03-code/src/maple/scheduler.py`; reference `BookingToolsMixin` in `03-code/agents/common.py` |

### Script

[AVATAR]
Let's try something. Ask your current Riley for an appointment on Sunday. [PAUSE]

[DEMO: Caller: "Do you have anything on Sunday?" Riley: "Sorry, something went wrong on my end. Could you try again?" Terminal shows a `ClinicClosedError` traceback logged as an unexpected tool error.]

"Sorry, something went wrong." The scheduler raised clinic closed, with a perfectly good message. But the tool didn't catch it, so LiveKit treated it as a crash and told the model only that the tool failed. The helpful sentence never reached the caller.

[CODE: step 1, import `ToolError` and `SchedulerError`]
```python
from livekit.agents import Agent, AgentServer, JobContext, RunContext, ToolError, cli, function_tool

from maple.scheduler import SchedulerError, parse_day
```

The fix is to catch scheduler errors and re-raise them as ToolErrors. Import both.

[CODE: step 2, wrap the scheduler calls in `find_available_slots`]
```python
        async with context.with_filler("One moment while I check the schedule.", delay=0.8):
            await self._backend_call()
            try:
                target = parse_day(day, self.scheduler.today)
                slots = self.scheduler.find_slots(target, part_of_day, limit=3)
            except SchedulerError as exc:
                raise ToolError(str(exc)) from exc
```

In find available slots, wrap the scheduler calls in try. Catch SchedulerError, and raise a ToolError with the same message. Do the same in book appointment. Remember, every scheduler message is already written to be spoken.

[DEMO: Ask for Sunday again. Riley: "We're closed on Sundays. Would another day work?"]

"We're closed on Sundays. Would another day work?" That sentence came straight from `scheduler.py`, through the ToolError, and the model relayed it. Same for a taken slot, a nine-digit phone number or a date in the past.

[SLIDE 1: Two kinds of failure]
| | Expected (`ToolError`) | Unexpected (any other exception) |
|---|---|---|
| Examples | Closed day, slot taken, bad phone | Bug, network outage |
| LLM sees | Your message | A generic failure |
| Caller hears | A specific, helpful sentence | A vague apology |
| You should | Write the message for the ear | Log it, alert, fix it |

This is the pattern. Expected failures become ToolErrors with a message for the ear. Unexpected ones stay as crashes: logged, generic to the caller, and something you fix. Don't catch every exception and turn it into a ToolError. That hides real bugs.

[CODE: step 3, the reschedule tool]
```python
    @function_tool
    async def reschedule_appointment(
        self,
        context: RunContext[CallState],
        phone: str,
        new_slot_start: str,
    ) -> str:
        """Move the caller's next upcoming appointment to a new time. Call find_available_slots
        first, read the new time back, and only call this after the caller says yes.

        Args:
            phone: The phone number the appointment was booked under.
            new_slot_start: The slot_start of the new time, e.g. 2026-10-07T14:00.
        """
        context.disallow_interruptions()
        async with context.with_filler("Let me move that for you.", delay=0.8):
            await self._backend_call()
            try:
                current = self.scheduler.upcoming_for_phone(phone)
                if current is None:
                    raise ToolError(
                        "I couldn't find an upcoming appointment under that number. "
                        "Ask the caller to confirm the phone number."
                    )
                moved = self.scheduler.reschedule(current.id, new_slot_start)
            except SchedulerError as exc:
                raise ToolError(str(exc)) from exc

        return f"Rescheduled: {describe_appointment(moved)}. Confirm the new day and time once."
```

Now rescheduling. The tool takes the phone number the appointment was booked under, and the new slot start. The docstring spells out the flow: find slots first, read back the new time, and only then call this.

Inside, we look up the caller's next upcoming appointment by phone. If there isn't one, we raise a ToolError ourselves. And look at the second sentence of that message: "Ask the caller to confirm the phone number." That's a retry prompt. It tells the model how to recover, not just what went wrong. Without it, the model often apologizes and gives up.

Then we move the appointment, and return a speakable confirmation. Disallow interruptions and a filler, same as booking, because this is also a commit.

[CODE: step 4, the cancel tool]
```python
    @function_tool
    async def cancel_appointment(self, context: RunContext[CallState], phone: str) -> str:
        """Cancel the caller's next upcoming appointment. Read the appointment back and only call
        this after the caller confirms they want to cancel.

        Args:
            phone: The phone number the appointment was booked under.
        """
        context.disallow_interruptions()
        async with context.with_filler("Okay, cancelling that now.", delay=0.8):
            await self._backend_call()
            try:
                current = self.scheduler.upcoming_for_phone(phone)
                if current is None:
                    raise ToolError(
                        "I couldn't find an upcoming appointment under that number. "
                        "Ask the caller to confirm the phone number."
                    )
                late = self.scheduler.is_late_cancellation(current)
                cancelled = self.scheduler.cancel(current.id)
            except SchedulerError as exc:
                raise ToolError(str(exc)) from exc

        fee_note = (
            " This is less than 24 hours ahead, so mention the late cancellation fee may apply."
            if late
            else ""
        )
        return f"Cancelled: {describe_appointment(cancelled)}.{fee_note} Offer to book a new time."
```

Cancel follows the same shape. One extra piece of business logic: is this a late cancellation, less than twenty-four hours ahead? The scheduler answers that, not the LLM. If it's late, the result tells Riley to mention the fee. And every cancellation ends with an offer to book a new time. That's good for the clinic, and it's in the tool result, so it happens consistently.

[SCREEN: Terminal. Run the agent.]

[DEMO: Reschedule, using the demo patient Jordan Lee, (512) 555-0142, booked Tuesday, October sixth at ten.]

**You:** Hi, I need to move my appointment. My number is five one two, five five five, zero one four two.

**Riley:** Sure. What day would you like to move it to?

**You:** Wednesday afternoon.

**Riley:** One moment while I check the schedule. I have Wednesday, October seventh at one, one thirty or two in the afternoon. Which works?

**You:** One thirty.

**Riley:** Just to confirm: I'll move your appointment from Tuesday, October sixth at ten in the morning to Wednesday, October seventh at one thirty in the afternoon. Shall I go ahead?

**You:** Yes.

**Riley:** Done. You're now booked for Wednesday at one thirty.

[DEMO: Error path. Caller gives a number with no appointment: "five one two, five five five, zero one nine one". Riley: "I couldn't find an upcoming appointment under that number. Could you double-check the number for me?"]

And the error path. A number with no appointment. Riley doesn't crash and doesn't invent one. It asks the caller to check the number, which is exactly what the retry prompt told it to do.

[AVATAR]
Three rules for tool errors. Catch the errors you expect, and let the rest crash loudly. Write every message for the ear. And add a next step, so the model knows how to recover.

**Recap:** Reschedule and cancel are thin wrappers with read-backs and fillers, and expected scheduler failures become `ToolError` messages that are speakable and tell the model how to recover.

**Transition:** Our tools each work alone, so next we'll give them shared memory for the call with typed userdata.

### Speaker notes: common student mistakes / Q&A

- Mistake: `except Exception: raise ToolError(...)` everywhere. Real bugs become polite apologies and never get fixed. Catch `SchedulerError` only.
- Mistake: error messages written for developers ("KeyError: APT-1009"). The caller will hear them, relayed or paraphrased.
- Mistake: rescheduling without a read-back of old and new times. Callers with two appointments get the wrong one moved.
- "Why look up by phone instead of appointment ID?" Callers don't know IDs. In Section 11, we add identity verification before changing existing appointments.

---

## Lecture 5.7 — Session state with userdata

| Field | Value |
|---|---|
| ID | 5.7 |
| Type | SC (code-along) |
| Target duration | 6:00 (~500 spoken words, about 3:34 of talking at 140 wpm) |
| Learning objectives | 1. Define typed per-call state with a `@dataclass` and attach it with `userdata=`. 2. Read and write it from tools with `context.userdata` (`RunContext[CallState]`). 3. Explain why userdata lives on the session and how the repo shares tools through `BookingToolsMixin`. |
| Prerequisites | 5.3 to 5.6 |
| Files used | Your `agents/my_booking_agent.py`; `03-code/agents/common.py` (`CallState`, `BookingToolsMixin`); reference `03-code/agents/s05_booking_agent.py` |

### Script

[AVATAR]
Right now, each tool call is on its own. The booking tool doesn't know what the lookup tool offered. After the call, you can't ask "what happened on this call?" without reading the transcript. [PAUSE] Userdata fixes both. It's a small, typed notebook that travels with the call.

[SCREEN: VS Code, `agents/common.py`, scroll to `class CallState`.]

[CODE: `CallState` in `agents/common.py` (shown, not typed)]
```python
@dataclass
class CallState:
    """Typed userdata carried across tools and agents for one call."""

    caller_name: str | None = None
    caller_phone: str | None = None
    caller_id_number: str | None = None
    visit_reason: str | None = None
    last_offered_slots: list[str] = field(default_factory=list)
    appointment_id: str | None = None
    identity_verified: bool = False
    verified_phone: str | None = None
    failed_verifications: int = 0
    transfer_requested: bool = False
    silence_prompts: int = 0
    call_outcome: str = "in_progress"
    notes: list[str] = field(default_factory=list)
```

Here's Riley's notebook. A plain Python dataclass called CallState. Caller name, phone and reason. The slots we last offered. The appointment ID. A few fields for later sections: caller ID from the phone network in Section eight, identity verification in Section eleven. You already used silence prompts in Section four. And call outcome, which starts as "in progress."

Two details. Every field has a default, so `CallState()` works with no arguments. And lists use `field(default_factory=list)`, so each call gets its own list instead of sharing one. That's a classic Python gotcha, and here it would mix up callers.

[CODE: step 1, attach it to the session]
```python
@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    session = create_session(
        get_settings(),
        proc=ctx.proc,
        userdata=CallState(),
        max_tool_steps=5,
    )
    await session.start(agent=RileyBookingAgent(), room=ctx.room)
```

In the entrypoint, pass a fresh CallState as userdata. One per call. `create_session` would make one for you anyway, but being explicit makes the code easier to read.

[CODE: step 2, write to it from `find_available_slots`]
```python
        context.userdata.last_offered_slots = [s.iso for s in slots]
```

Now use it. In find available slots, after we have slots, remember what we offered. Because we typed the context as RunContext of CallState, your editor autocompletes `last_offered_slots`. That's the payoff of typed userdata. Typos become red squiggles instead of silent bugs.

[CODE: step 3, write to it from `book_appointment`]
```python
        state = context.userdata
        state.caller_name = appt.patient_name
        state.caller_phone = appt.phone
        state.visit_reason = appt.reason
        state.appointment_id = appt.id
        state.call_outcome = "booked"
```

In book appointment, after a successful booking, record who, why, the appointment ID and the outcome: booked. Add similar lines to reschedule and cancel, with outcomes "rescheduled" and "cancelled".

[CODE: step 4, read it when the call ends]
```python
import logging

logger = logging.getLogger("my-booking-agent")

# inside entrypoint, after creating the session:
    async def log_outcome() -> None:
        state = session.userdata
        logger.info("call ended: outcome=%s appointment=%s", state.call_outcome, state.appointment_id)

    ctx.add_shutdown_callback(log_outcome)
```

And here's where it pays off. A shutdown callback runs when the call ends. It reads the session's userdata and logs the outcome. In Section ten, this becomes a metric: how many calls end in a booking, a transfer or a hang-up. That's containment rate, and it's the number the clinic manager cares about.

[DEMO: Run the agent, book an appointment, press Ctrl+C. The last log line shows "call ended: outcome=booked appointment=APT-1004".]

Book an appointment, end the call, and there's the outcome in the log.

[SLIDE 1: Why userdata lives on the session]
- One `CallState` per call, not per agent
- Survives handoffs between agents (Section 7)
- Readable by tools (`context.userdata`) and by your code (`session.userdata`)
- Not shown to the LLM unless a tool returns it

Why on the session and not the agent? Because in Section seven, the call moves from a greeter agent to a booking specialist. The agent changes. The notebook must not. And note that userdata is invisible to the LLM. It only knows what tools return. That's a feature: you can store things the model shouldn't see.

[SCREEN: VS Code, `agents/s05_booking_agent.py`. Then `agents/common.py`, scroll to `class BookingToolsMixin`.]

Now the refactor I promised. Open the reference file, `s05_booking_agent.py`. The agent class looks like this.

[CODE: the reference agent (shown, not typed)]
```python
class RileyBookingAgent(BookingToolsMixin, Agent):
    def __init__(self, *, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        self.simulated_latency = get_settings().simulated_backend_latency
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today, booking=True, extra=WAITLIST_RULES
            ),
        )
```

It inherits from BookingToolsMixin and Agent. And BookingToolsMixin, in `common.py`, contains the same four tools you just wrote, line for line. Moving them into a mixin means the realtime agent in Section six, the booking specialist in Section seven and the capstone can all reuse them without copying. The constructor also accepts a scheduler, so tests in Section nine can pass in a calendar with a fixed date.

Diff your file against the mixin. The only differences should be names and comments.

**Recap:** A typed `CallState` dataclass passed as `userdata` gives every tool shared, autocompleted per-call memory that survives handoffs and tells you how each call ended.

**Transition:** You now have a complete booking agent, so next is Project 1, where you'll extend it and prove it works.

### Speaker notes: common student mistakes / Q&A

- Mistake: `last_offered_slots: list[str] = []` in the dataclass. Python raises an error for mutable defaults in dataclasses; use `field(default_factory=list)`.
- Mistake: creating one `CallState()` at module level and reusing it. Every call then shares the same notebook. Create it inside the entrypoint.
- Mistake: accessing `context.userdata` when the session was created without `userdata`. You get an error; always pass one (or use `create_session`, which does).
- "Should I put the whole conversation in userdata?" No. The session already keeps chat history. Store decisions and facts, not transcripts.

---

## Lecture 5.8 — Project 1: Booking agent

| Field | Value |
|---|---|
| ID | 5.8 |
| Type | AS (assignment with short video brief) |
| Target duration | 5:00 total (2:00 video, ~300 spoken words, about 2:09 of talking at 140 wpm) |
| Learning objectives | 1. Extend and demo a complete booking flow: find, book, reschedule and cancel with read-backs. 2. Record a short demo that proves the agent handles a correction and an error. |
| Prerequisites | 5.1 to 5.7 |
| Files used | `05-projects/project-1-booking-agent.md`, `03-code/agents/s05_booking_agent.py` |

### Script

[AVATAR]
You've built every piece of a booking agent. Now make it yours, and prove it works.

[SCREEN: Open `05-projects/project-1-booking-agent.md`. Scroll through the requirements.]

Project one has four requirements. One: Riley books a new appointment, collecting name, phone, reason and a time, with a read-back before committing. Two: Riley reschedules an existing appointment, found by phone number. Three: Riley cancels an appointment and mentions the twenty-four hour policy when it applies. Four: Riley handles at least one error gracefully, like a closed day or a taken slot, without making anything up.

[SCREEN: Scroll to "Stretch goals".]

Then pick one stretch goal. Add a "what's my next appointment?" tool. Offer the waitlist from Lecture 5.9 automatically when a whole day is full. Or add a new field to CallState, like insurance provider, and use it across tools.

[SCREEN: Scroll to "Deliverables" and the rubric table.]

The deliverable is a short screen recording, two to three minutes, of a console-mode call. Your call must include at least one correction, like "no, Thursday," and at least one error path. Share your code and the recording, and in a few sentences, describe one thing that didn't work at first and how you fixed it.

The rubric scores five things. Correct tool calls. Read-back before every commit. Short, speakable replies. Graceful errors. And code quality, meaning logic stays in the scheduler and tools stay thin.

[AVATAR]
Here's a tip. Before recording, run the scheduler unit tests, then do three practice calls in text mode. It's much cheaper to find a bug by typing than by talking. And save your transcript. In Section nine, you'll turn this exact conversation into an automated test.

**Recap:** Project 1 asks for a recorded booking, reschedule and cancel flow with read-backs, a correction and a graceful error, plus one stretch goal.

**Transition:** Next, a challenge: design a waitlist tool from a spec, then compare with the solution.

### Speaker notes: common student mistakes / Q&A

- Most common rubric miss: committing a booking before the caller says yes. Check that your read-back rule is in the prompt and that the tool is only called after confirmation.
- Recordings over five minutes usually mean Riley's replies are too long. Revisit Section 4.
- Students forget that the scheduler is in memory: restarting the agent resets the demo data. That's expected.

---

## Lecture 5.9 — Challenge: add a waitlist tool (pause, then solution)

| Field | Value |
|---|---|
| ID | 5.9 |
| Type | CE (coding challenge: spec, pause, solution walkthrough) |
| Target duration | 6:00 (~525 spoken words, about 3:45 of talking at 140 wpm, plus pause time) |
| Learning objectives | 1. Design and implement a new tool, `join_waitlist`, from a spec, backed by `scheduler.add_to_waitlist`. 2. Avoid the three most common tool mistakes: a vague description, no read-back, and forgetting `ToolError`. |
| Prerequisites | 5.3 to 5.7 |
| Files used | Your `agents/my_booking_agent.py`; `03-code/src/maple/scheduler.py` (`add_to_waitlist`, `waitlist_position`); solution in `03-code/agents/s05_booking_agent.py` (`join_waitlist`, `WAITLIST_RULES`) |

### Script

[AVATAR]
Your turn to design a tool from scratch. Here's the situation. A caller wants Thursday morning. Thursday morning is full. Right now, Riley offers another day, and if that doesn't work, the call ends with nothing. The clinic wants a waitlist instead.

[SLIDE 1: The spec]
```text
Tool:     join_waitlist(patient_name, phone, preferred_day, part_of_day="any")
Backed by: self.scheduler.add_to_waitlist(patient_name, phone, preferred_day, part_of_day)
           self.scheduler.waitlist_position(entry.id)   -> 1-based position for that day
Behavior:
  - Offer the waitlist only when no offered time works for the caller
  - Read back name, phone number and day, and wait for a clear yes
  - Speakable errors for bad phone numbers, closed days, past dates
  - Result tells Riley the day (in words) and the caller's position
  - Record the outcome in CallState
```

Here's the spec. A tool called join waitlist, taking the patient name, phone, preferred day and an optional part of day. The scheduler already has `add_to_waitlist`, and `waitlist_position`, which tells you where the caller is in line for that day. You write the tool, and the prompt rule that tells Riley when to offer it.

Requirements: offer it only when nothing works. Read back before calling it. Speakable errors. A result that says the day in words and the position. And record the outcome in call state.

[SCREEN: VS Code, `src/maple/scheduler.py`, scroll to `add_to_waitlist` so students can read its docstring and exceptions.]

Before you pause, have a look at `add_to_waitlist` in the scheduler. Read which errors it can raise. You'll need that.

[AVATAR]
Pause the video now. Give yourself about fifteen minutes. Build it in your `my_booking_agent.py`, run it in text mode, and try to make Thursday morning full so you can test it. Come back when you've got something working, or when you're stuck.

[PAUSE]

[SLIDE 2: "Pause the video and build it" (hold on screen for 5 seconds with a countdown graphic)]

[AVATAR]
Welcome back. Let's walk through a solution, and I'll point out the three mistakes I see most often.

[SCREEN: VS Code, `agents/s05_booking_agent.py`, scroll to `join_waitlist`.]

[CODE: the solution tool, from `agents/s05_booking_agent.py`]
```python
    @function_tool
    async def join_waitlist(
        self,
        context: RunContext[CallState],
        patient_name: str,
        phone: str,
        preferred_day: str,
        part_of_day: Literal["morning", "afternoon", "any"] = "any",
    ) -> str:
        """Put the caller on the waitlist for a day with no suitable openings. Only call this
        after reading back the name, phone number and day and the caller said yes.

        Args:
            patient_name: The patient's full name.
            phone: A ten digit callback phone number.
            preferred_day: The day they want, as an ISO date such as 2026-10-06 or a weekday name.
            part_of_day: "morning", "afternoon" or "any".
        """
        try:
            entry = self.scheduler.add_to_waitlist(patient_name, phone, preferred_day, part_of_day)
            position = self.scheduler.waitlist_position(entry.id)
        except SchedulerError as exc:
            raise ToolError(str(exc)) from exc
        context.userdata.caller_name = entry.patient_name
        context.userdata.caller_phone = entry.phone
        context.userdata.call_outcome = "waitlisted"
        return (
            f"Added to the waitlist for {prompts.speak_date(entry.preferred_day)}, "
            f"position {position}. Tell the caller we will text them if a slot opens."
        )
```

Mistake one: a vague description. The most common first attempt is a docstring like "Adds to waitlist." The model never calls it, because it doesn't know when. Look at this one. "Put the caller on the waitlist for a day with no suitable openings." That tells the model the situation it's for. And the args have examples, like an ISO date or a weekday name.

Mistake two: no read-back. The docstring says "only call this after reading back the name, phone number and day and the caller said yes." Without that, Riley adds someone to the waitlist with a misheard phone number, and the clinic texts a stranger. Same rule as booking. Anything that stores the caller's details gets a read-back.

Mistake three: forgetting ToolError. Try a Sunday, or a nine-digit phone number, without the try block. The scheduler raises, the tool crashes, and the caller hears a vague apology. With it, they hear "We're closed on Sundays. Would another day work?"

The rest should look familiar. Record the outcome in call state. Return the day in words and the position. And tell Riley what to say next.

[CODE: the prompt rule, `WAITLIST_RULES`, passed with `extra=`]
```python
WAITLIST_RULES = """\
Waitlist:
- If no time works for the caller, offer the waitlist for their preferred day.
- Read back the name, phone number and day before calling join_waitlist."""

# in __init__:
            instructions=prompts.build_instructions(
                today=self.scheduler.today, booking=True, extra=WAITLIST_RULES
            ),
```

And the prompt side. A small waitlist block, passed in with `extra`. When to offer it, and the read-back rule again. Notice that the rule lives in both places, the prompt and the tool description, like we did for booking.

[DEMO: Console text mode. Book out Thursday morning first (or pick a fully booked day), then: "Can I get Thursday morning?" Riley offers other options; caller declines. Riley offers the waitlist, reads back, caller says yes. Riley: "You're on the waitlist for Thursday, October eighth, number one in line. We'll text you if a slot opens."]

Here it is working. Nothing suits the caller, Riley offers the waitlist, reads back the details, and confirms the position.

[AVATAR]
If your version differs, that's fine. Compare the three things that matter: a description that says when, a read-back before storing details, and ToolError for expected failures. If you got all three, you've got the pattern for every tool you'll ever write.

**Recap:** A good tool has a description that says when to use it, a read-back before storing caller details, and `ToolError` for expected failures, as in `join_waitlist`.

**Transition:** Let's finish Section 5 with a short quiz on tools.

### Speaker notes: common student mistakes / Q&A

- To test a full morning quickly, book three morning slots in text mode first, or write a unit test that fills the day with `scheduler.book(...)` calls.
- The scheduler de-duplicates: the same phone number on the same day returns the existing entry. Students sometimes think it's a bug when the position doesn't change.
- Mistake: naming the argument `name` in the tool but `patient_name` in the prompt. Keep names identical across prompt, tool and scheduler to reduce model confusion.
- `ToolError` must be imported from `livekit.agents`; students sometimes define their own exception class, which LiveKit treats as an unexpected crash.

---

## Lecture 5.10 — Quiz: Tools

| Field | Value |
|---|---|
| ID | 5.10 |
| Type | QZ (quiz with short video intro) |
| Target duration | 2:00 total (0:45 video, ~75 spoken words, about 0:32 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of tool schemas, read-backs, filler speech, `ToolError` and userdata. |
| Prerequisites | 5.1 to 5.9 |
| Files used | `06-assessments/quizzes/section-05.md` |

### Script

[AVATAR]
Five questions on tools, and then Riley goes speech-to-speech.

[SLIDE 1: Section 5 quiz: what's covered]
- What the LLM sees: names, docstrings, type hints
- Read-back before irreversible actions
- `with_filler` and its delay
- `ToolError` vs unexpected exceptions
- Why userdata lives on the session

You'll see questions on tool schemas, read-backs, filler speech, tool errors and userdata. One tip: for the error question, ask yourself who the message is written for. If it's the caller, it's a ToolError.

**Recap:** The quiz checks tool schemas, read-backs, fillers, errors and userdata.

**Transition:** Next, Section 6 swaps the cascaded pipeline for OpenAI's speech-to-speech model, and you'll see how much of Riley carries over unchanged.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: thinking `with_filler` always speaks. It speaks only if the work is still running after `delay`.
- Second most missed: thinking the LLM can see `userdata`. It only sees what tools return.
