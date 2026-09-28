# Quiz: Prompting for the Ear (Section 4)

| Field | Value |
|---|---|
| Udemy lecture | 4.8 Quiz: Prompting for the ear |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 4.1 to 4.5 |

---

### Q1. A chat-style prompt makes Riley answer "What are your hours?" with a five-sentence paragraph. Apart from being tiring to listen to, why does this hurt a voice agent specifically?

*Related lecture: 4.1 Why chat prompts fail on voice*

- **A.** Long answers cost more STT minutes.
  - *Explanation:* Incorrect. STT processes the caller's audio, not Riley's replies.
- **B.** The caller cannot skim or scroll back, and long replies generate more tokens and TTS audio, so the caller waits longer, forgets details, and is more likely to interrupt mid-answer.
  - *Explanation:* Correct. Listening is linear and memory is short. Every extra sentence adds generation and synthesis work and increases the chance of barge-in, which is why voice prompts demand one or two short sentences.
- **C.** LiveKit truncates replies longer than 50 words.
  - *Explanation:* Incorrect. There is no such truncation; the whole reply would be spoken.
- **D.** Long answers disable turn detection.
  - *Explanation:* Incorrect. Turn detection keeps working. The problem is the caller's experience and latency.

**Correct answer: B**

---

### Q2. Riley tells callers the clinic's number as "five hundred twelve, five hundred fifty-five, one hundred". What is the best fix?

*Related lecture: 4.3 Numbers, dates, names and pronunciation*

- **A.** Switch to a TTS voice with a different accent.
  - *Explanation:* Incorrect. The voice reads the text it is given. The text is the problem.
- **B.** Remove phone numbers from the FAQ so Riley never says them.
  - *Explanation:* Incorrect. Callers need the number. Hiding information is not a fix.
- **C.** Give Riley a speakable form and an explicit rule: read phone numbers digit by digit in groups ("five one two, five five five, zero one zero zero"), for example using a helper like `maple.prompts.speak_phone()` for text you control.
  - *Explanation:* Correct. Output rules with an example, plus pre-formatting text you generate yourself, make TTS read numbers the way a person would. The course keeps `CLINIC_PHONE_SPOKEN` for exactly this.
- **D.** Put the number in bold so TTS emphasises it.
  - *Explanation:* Incorrect. Markdown is either read aloud or ignored by TTS; it never changes digit grouping.

**Correct answer: C**

---

### Q3. After a lookup tool returns `2026-10-06T09:30`, Riley says "two thousand twenty-six dash ten dash zero six T nine thirty". What is the most robust fix?

*Related lecture: 4.3 Numbers, dates, names and pronunciation*

- **A.** Have the tool return a speakable description ("Tuesday, October sixth at nine thirty in the morning") alongside the machine value, and tell the model to use the machine value only in tool calls and never read it aloud.
  - *Explanation:* Correct. The course's `find_available_slots` returns `speak_slot()` text plus a tagged `slot_start` with an instruction not to read it. The model gets both what to say and what to pass back to `book_appointment`.
- **B.** Ask callers to read dates in ISO format.
  - *Explanation:* Incorrect. The caller should never have to adapt to the system's data format.
- **C.** Strip all dates from tool results.
  - *Explanation:* Incorrect. Then Riley cannot tell the caller when their appointment is, or pass the right slot to the booking tool.
- **D.** Increase the LLM temperature so it paraphrases more.
  - *Explanation:* Incorrect. Randomness does not reliably convert formats, and it makes other behaviour less predictable.

**Correct answer: A**

---

### Q4. A caller puts the phone down to find their insurance card and goes silent for 30 seconds. How should Riley behave, and which LiveKit features support it?

*Related lecture: 4.4 Greetings, silence and "are you still there?"*

- **A.** Hang up immediately after 10 seconds of silence to save money.
  - *Explanation:* Incorrect. Hanging up on a caller who is fetching information is a bad experience, and a few seconds of silence costs very little.
- **B.** Repeat the last question every 3 seconds until the caller answers.
  - *Explanation:* Incorrect. Constant repetition is annoying and can talk over a caller who is just starting to speak.
- **C.** Do nothing; silence is harmless.
  - *Explanation:* Incorrect. A caller who has walked away or whose line dropped would keep the session open indefinitely, and a caller who is back will not know Riley is still there.
- **D.** Use `user_away_timeout` on the `AgentSession` and react to the `user_state_changed` event (state `away`): check in gently once ("Take your time, I'm here"), and end the call gracefully only after repeated silence.
  - *Explanation:* Correct. This is the pattern from `s04_voice_prompting.py`, using the `SILENCE_CHECK_IN` and `SILENCE_GOODBYE` lines from `maple.prompts`.

**Correct answer: D**

---

### Q5. A caller asks, "Wait, am I talking to a real person?" What should Riley's persona guidelines produce?

*Related lecture: 4.5 Persona and brand voice without the cringe*

- **A.** "I'm Riley! I'm here to help, so let's keep going with your booking."
  - *Explanation:* Incorrect. Deflecting a direct question about AI status erodes trust and, depending on jurisdiction, may breach disclosure rules (Section 8.6).
- **B.** "No, I'm Riley, the clinic's AI assistant. I can book appointments or connect you with someone at the front desk if you'd prefer."
  - *Explanation:* Correct. A short, honest disclosure followed by what Riley can do and a path to a human keeps trust and momentum. The course's `IDENTITY` block requires exactly this.
- **C.** "Yes, I'm Riley from the front desk."
  - *Explanation:* Incorrect. Claiming to be human is deceptive and exactly what disclosure rules forbid.
- **D.** A two-minute explanation of how large language models work.
  - *Explanation:* Incorrect. Accurate but far too long for voice, and not what the caller needs.

**Correct answer: B**
