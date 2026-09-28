# Quiz: Architectures and Tools (Section 6)

| Field | Value |
|---|---|
| Udemy lecture | 6.6 Quiz: Architectures and tools |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 5.1, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 6.4 |

---

### Q1. In testing, Riley sometimes calls `cancel_appointment` when a caller says "I need to move my Thursday appointment." The tool code is correct. What is the most effective first fix?

*Related lecture: 5.1 How function tools work in LiveKit*

- **A.** Increase `max_tool_steps` so Riley can try more tools.
  - *Explanation:* Incorrect. `max_tool_steps` limits how many tool rounds can run in one turn. It does not help the model choose the right tool; it only allows more wrong calls.
- **B.** Rewrite the docstrings of `reschedule_appointment` and `cancel_appointment` so each says clearly when to use it (and when not to), because the docstring becomes the tool description the LLM sees.
  - *Explanation:* Correct. With `@function_tool`, the method's docstring and typed arguments become the tool schema. Vague or overlapping descriptions are the most common cause of wrong tool selection. "Use when the caller wants to move an existing appointment to a new time; do not cancel" fixes most cases.
- **C.** Rename both tools to `tool_1` and `tool_2` so the model does not rely on names.
  - *Explanation:* Incorrect. Meaningful names are part of how the model chooses tools. Removing them makes selection worse.
- **D.** Remove `cancel_appointment` from Riley entirely.
  - *Explanation:* Incorrect. That hides the symptom and removes a feature the clinic needs. Fix the descriptions and add a behaviour test instead.

**Correct answer: B**

---

### Q2. A caller asks for Tuesday at 10:00, but that slot was taken seconds ago by another caller. Inside `book_appointment`, what should the tool do?

*Related lecture: 5.6 Reschedule, cancel and tool errors*

- **A.** Return `None` so the LLM knows something went wrong.
  - *Explanation:* Incorrect. `None` gives the model nothing to say, and it may even assume the booking succeeded.
- **B.** Raise a plain `ValueError("slot taken")` and let the framework handle it.
  - *Explanation:* Incorrect. An unexpected exception is reported to the model as a generic failure. You lose control of the message the caller hears.
- **C.** Call `session.say("Sorry, that slot is gone")` from inside the tool and then return `"OK"`.
  - *Explanation:* Incorrect. Returning "OK" tells the LLM the booking worked, so its next sentence will likely confirm an appointment that does not exist.
- **D.** Raise `ToolError("That time was just taken. The next free times are ten thirty and eleven.")`, a speakable message the LLM can relay and recover from.
  - *Explanation:* Correct. `ToolError` marks the call as a recoverable failure and passes your message to the model. Writing it as speakable text (with alternatives) lets Riley recover gracefully instead of apologising vaguely or pretending it worked.

**Correct answer: D**

---

### Q3. `find_available_slots` usually returns in 200 ms but sometimes takes 2 to 3 seconds when the practice-management API is slow. You want callers to hear something during slow lookups, but not on fast ones. What should you use?

*Related lecture: 5.5 Hiding latency while tools run*

- **A.** `async with context.with_filler("One moment while I check the schedule.", delay=0.5): ...` around the slow call.
  - *Explanation:* Correct. The filler is only spoken if the block is still running after `delay`, so fast lookups stay silent and slow ones get a natural "one moment" instead of dead air.
- **B.** Add "Always say 'one moment please' before every tool call" to the prompt.
  - *Explanation:* Incorrect. That adds a filler even when the tool returns instantly, which makes Riley sound slow and repetitive, and prompt instructions are not reliable timing controls.
- **C.** `time.sleep(0.5)` before the API call so the caller hears a natural pause.
  - *Explanation:* Incorrect. A blocking sleep freezes the event loop, which can stall audio and adds latency on every call.
- **D.** Lower TTS TTFB by switching voices.
  - *Explanation:* Incorrect. TTS speed does not change how long the tool takes. The gap is caused by the tool, not by speech synthesis.

**Correct answer: A**

---

### Q4. Riley collects the caller's name in turn 2 and phone number in turn 4, but `book_appointment` in turn 9 sometimes gets the wrong phone number because the LLM re-extracts it from a long conversation. How should you carry these details?

*Related lecture: 5.7 Session state with userdata*

- **A.** Store them in module-level global variables in the agent file.
  - *Explanation:* Incorrect. The agent server runs many calls, and globals would leak one caller's data into another's call.
- **B.** Ask the caller to repeat every detail right before booking.
  - *Explanation:* Incorrect. A read-back is good, but making the caller dictate everything twice is a poor experience and does not fix the storage problem.
- **C.** Save them in a typed `@dataclass` passed as `userdata=CallState()` to `AgentSession`, write them from the tools via `context.userdata`, and read them in `book_appointment`.
  - *Explanation:* Correct. `userdata` is per-session state available to every tool through `RunContext`. Storing confirmed details there makes the booking deterministic instead of relying on the model's memory of a long transcript.
- **D.** Put them in the system prompt with `update_instructions()` on the agent after each turn.
  - *Explanation:* Incorrect. That still relies on the LLM to copy values correctly, adds tokens to every turn, and mixes data with instructions.

**Correct answer: C**

---

### Q5. You move Riley from the cascaded pipeline to `gpt-realtime`. Which change to the session is correct?

*Related lecture: 6.2 Code-along: Riley on gpt-realtime*

- **A.** Replace `stt`, `llm` and `tts` with `llm=openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin")`, and keep the same `Agent` subclass and its `@function_tool` methods.
  - *Explanation:* Correct. The realtime model hears audio and speaks audio, so separate STT and TTS are not needed. Tools are defined on the `Agent`, so the same booking tools work unchanged.
- **B.** Keep `stt` and `tts`, and set `llm="openai/gpt-realtime"` as a LiveKit Inference string.
  - *Explanation:* Incorrect. In the course, the realtime model is used through the OpenAI plugin's `RealtimeModel` class, and keeping STT and TTS would turn it back into a cascade.
- **C.** Rewrite all tools as JSON schemas because realtime models do not support `@function_tool`.
  - *Explanation:* Incorrect. LiveKit converts `@function_tool` methods for the realtime model automatically. No rewrite is needed.
- **D.** Remove the tools, because speech-to-speech models cannot call functions.
  - *Explanation:* Incorrect. Realtime models support function calling. Riley books appointments in the realtime version too.

**Correct answer: A**

---

### Q6. With the realtime version, your transcript logs occasionally show a caller sentence that differs slightly from what Riley obviously understood. Why can this happen?

*Related lecture: 6.1 How realtime speech models work*

- **A.** The realtime model runs two different LLMs in parallel.
  - *Explanation:* Incorrect. There is one model responding. The difference comes from how the transcript is produced.
- **B.** LiveKit rewrites transcripts to remove PII.
  - *Explanation:* Incorrect. Nothing redacts transcripts unless you add it (Section 11).
- **C.** The caller's audio is compressed so heavily that the model guesses.
  - *Explanation:* Incorrect. Compression affects accuracy in general, but it does not explain why the log differs from what the model understood.
- **D.** The model reasons directly over audio, and the user transcript comes from a separate transcription side channel, so the text in your logs is not exactly what the model "heard".
  - *Explanation:* Correct. In speech-to-speech, the input transcript is a by-product produced by a separate transcription process. It can disagree with the model's own understanding, which matters for logging, auditing and text-based tests.

**Correct answer: D**

---

### Q7. Marketing wants Riley to keep the Cartesia voice, but engineering prefers the realtime model's understanding and turn-taking. What configuration achieves this?

*Related lecture: 6.3 Hybrid: realtime LLM with your own TTS*

- **A.** Set the realtime model's `voice` parameter to the Cartesia voice ID.
  - *Explanation:* Incorrect. Realtime voices are the model provider's own voices; a Cartesia ID is not valid there.
- **B.** Configure the realtime model with text-only output (`modalities=["text"]`) and add `tts=` to the `AgentSession` so your TTS speaks the replies.
  - *Explanation:* Correct. This is the half-cascade: audio in to the realtime model, text out, then your chosen TTS. You keep brand voice and pronunciation control at the cost of a little extra latency.
- **C.** Run the full cascade but name the LLM `gpt-realtime`.
  - *Explanation:* Incorrect. A text-only cascade does not get the realtime model's direct audio understanding, whatever the model is called.
- **D.** Post-process the realtime audio through a voice changer.
  - *Explanation:* Incorrect. That adds latency and artefacts and is not a supported pattern.

**Correct answer: B**

---

### Q8. Your head-to-head test of the same five calls shows: cascaded perceived latency 1.2 s, 5/5 correct bookings, about $0.05 per minute; realtime 0.8 s, 4/5 correct bookings (one booked before the caller said yes), about $0.20 per minute. Maple Street Dental cares most about accurate bookings and cost. What is the best recommendation?

*Related lecture: 6.4 Head-to-head: cascaded vs realtime*

- **A.** Realtime, because lower latency always wins in voice.
  - *Explanation:* Incorrect. Latency matters, but the clinic's stated priorities are accuracy and cost, and realtime lost on both in this data.
- **B.** Neither; voice agents are not ready for bookings.
  - *Explanation:* Incorrect. The cascaded run booked correctly in all five calls. The data supports deploying, with monitoring.
- **C.** Cascaded for now, while working on its latency, and re-test realtime (or the hybrid) as prices and tool reliability change.
  - *Explanation:* Correct. The recommendation follows the clinic's priorities and the evidence: cascaded was fully accurate at about a quarter of the cost. Latency can be tuned (endpointing, model choice), and the decision should be revisited with new measurements.
- **D.** Realtime, and fix the premature booking by telling the caller to speak more clearly.
  - *Explanation:* Incorrect. The failure was the agent committing without confirmation, which is an agent problem. Blaming the caller does not fix it.

**Correct answer: C**
