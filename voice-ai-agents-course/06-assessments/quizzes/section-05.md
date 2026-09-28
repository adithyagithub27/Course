# Quiz: Tools (Section 5)

| Field | Value |
|---|---|
| Udemy lecture | 5.10 Quiz: Tools |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 5.1, 5.2, 5.4, 5.5, 5.9 (Section 6's quiz covers docstrings, `ToolError`, filler speech and userdata) |

---

### Q1. In one turn, Riley calls `find_available_slots` for Monday, then Tuesday, then Wednesday, then Thursday, and the caller hears nothing for several seconds. Which setting limits how many tool rounds can run before Riley must answer?

*Related lecture: 5.1 How function tools work in LiveKit*

- **A.** `min_endpointing_delay`
  - *Explanation:* Incorrect. Endpointing controls when the caller's turn ends. It has nothing to do with tool calls.
- **B.** `user_away_timeout`
  - *Explanation:* Incorrect. That detects caller silence, not agent tool loops.
- **C.** `max_tool_steps` on the `AgentSession`
  - *Explanation:* Correct. `max_tool_steps` caps the number of consecutive tool-call rounds in a single turn, so a confused model cannot loop indefinitely. Pair it with a clearer prompt ("check one day at a time, then offer options").
- **D.** `InterruptionOptions(min_words=...)`
  - *Explanation:* Incorrect. Interruption settings decide when caller speech stops Riley's speech, not how many tools run.

**Correct answer: C**

---

### Q2. Why does the course put booking rules (opening hours, lunch break, 24-hour cancellation policy) in `src/maple/scheduler.py` instead of inside the agent's tool methods?

*Related lecture: 5.2 The clinic scheduler: pure Python first*

- **A.** LiveKit does not allow more than 20 lines of code inside a tool.
  - *Explanation:* Incorrect. There is no such limit.
- **B.** Pure-Python rules can be unit-tested offline in milliseconds and reused unchanged by the cascaded, realtime, multi-agent and Pipecat versions of Riley, while tools stay thin adapters.
  - *Explanation:* Correct. Separating business logic from the framework is what makes the testing pyramid's base possible and lets the same rules serve every architecture in the course.
- **C.** It makes the LLM more creative.
  - *Explanation:* Incorrect. Where the code lives does not change the model's behaviour.
- **D.** It lowers LLM token usage because the scheduler is not in the prompt.
  - *Explanation:* Incorrect. Tool code is never in the prompt, wherever it lives. Only the tool's name, description and arguments are.

**Correct answer: B**

---

### Q3. Riley reads back "Tuesday, October sixth at nine thirty for a cleaning. Shall I go ahead?" The caller says "No, Thursday." What should happen next?

*Related lecture: 5.4 Confirmation and read-back patterns*

- **A.** Book Tuesday anyway, then offer to reschedule.
  - *Explanation:* Incorrect. Committing against an explicit "no" creates a wrong booking and an extra step for the caller.
- **B.** Book Thursday at nine thirty without checking.
  - *Explanation:* Incorrect. Thursday at nine thirty may not be free. Riley must not assume availability.
- **C.** Apologise and restart the whole booking from the caller's name.
  - *Explanation:* Incorrect. Only the day changed. Re-asking everything wastes the caller's time.
- **D.** Call `find_available_slots` for Thursday, offer the options, read the new details back, and book only after a clear "yes".
  - *Explanation:* Correct. A correction updates one detail, triggers a fresh availability check, and restarts the confirmation loop. `BOOKING_RULES` in `maple.prompts` spells this out.

**Correct answer: D**

---

### Q4. While `book_appointment` is committing, the caller coughs and says "uh". In early tests this interrupted Riley and the booking confirmation was lost halfway through. What does the course's booking tool do to prevent this?

*Related lecture: 5.5 Hiding latency while tools run*

- **A.** Calls `context.disallow_interruptions()` at the start of commit tools, so the booking and its confirmation finish before caller speech can interrupt.
  - *Explanation:* Correct. For irreversible actions a half-finished exchange is worse than a short wait. `book_appointment`, `reschedule_appointment` and `cancel_appointment` all disallow interruptions while they commit.
- **B.** Mutes the caller's microphone for the rest of the call.
  - *Explanation:* Incorrect. That would stop the caller from correcting anything afterwards.
- **C.** Sets `max_tool_steps=1`.
  - *Explanation:* Incorrect. That limits tool rounds, not interruptions.
- **D.** Asks the caller to stay silent during bookings.
  - *Explanation:* Incorrect. You cannot rely on callers following instructions like this, and coughs are involuntary.

**Correct answer: A**

---

### Q5. You add a `join_waitlist(name, phone, preferred_day)` tool with the docstring `"""Waitlist."""`. In testing, Riley never offers the waitlist when a day is full. What is the most likely cause?

*Related lecture: 5.9 Challenge: add a waitlist tool*

- **A.** The tool's arguments need default values.
  - *Explanation:* Incorrect. Required arguments are fine; they tell the model what to collect.
- **B.** Tools added after the agent starts are ignored.
  - *Explanation:* Incorrect. The tool is defined on the class, so it is registered when the agent starts.
- **C.** The description is too vague for the model to know when to use it. Say when to call it ("when no suitable slot is available and the caller wants to be contacted if one opens"), what each argument means, and that the details must be read back first.
  - *Explanation:* Correct. A vague description is the first of the three common mistakes in the waitlist challenge (the others are skipping the read-back and not raising `ToolError` for bad input). The docstring is the model's only guide to when a tool applies.
- **D.** The waitlist needs its own agent.
  - *Explanation:* Incorrect. A single, well-described tool is enough. Splitting agents is for larger capability groups (Section 7).

**Correct answer: C**
