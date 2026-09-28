# Final Practice Test: Production Voice AI Agents

| Field | Value |
|---|---|
| Udemy lecture | 15.2 Final practice test (Udemy "Practice test" item) |
| Questions | 40 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Suggested time limit | 60 minutes |
| **Passing score** | **70% (28 of 40)** |
| Knowledge areas | Enter each question's "Domain" in Udemy's "Knowledge area" field so the results page breaks scores down by domain |

None of these questions repeats a section-quiz question; they test the same skills in new scenarios.

## Domain weighting

| # | Domain (Udemy knowledge area) | Sections | Questions | Weight |
|---|---|---|---|---|
| D1 | Voice agent fundamentals and architectures | 1, 6 | 5 | 12.5% |
| D2 | LiveKit Agents core, setup and turn-taking | 2, 3 | 4 | 10% |
| D3 | Prompting for the ear | 4 | 3 | 7.5% |
| D4 | Tools, state and confirmation | 5 | 4 | 10% |
| D5 | Knowledge, handoffs and multilingual | 7 | 3 | 7.5% |
| D6 | Telephony | 8 | 4 | 10% |
| D7 | Testing and evaluation | 9 | 7 | 17.5% |
| D8 | Observability and cost | 10 | 3 | 7.5% |
| D9 | Security and safety | 11 | 3 | 7.5% |
| D10 | Deployment and production hardening | 12, 13 | 3 | 7.5% |
| D11 | Pipecat and choosing a stack | 14 | 1 | 2.5% |
| | **Total** | | **40** | **100%** |

Testing carries the largest weight because it is the course's signature skill (Section 9). Section 14 is optional in the course, so it carries one question.

## Answer key

| Q | Ans | Q | Ans | Q | Ans | Q | Ans |
|---|---|---|---|---|---|---|---|
| 1 | C | 11 | A | 21 | B | 31 | D |
| 2 | A | 12 | C | 22 | D | 32 | A |
| 3 | B | 13 | B | 23 | C | 33 | B |
| 4 | D | 14 | D | 24 | A | 34 | C |
| 5 | C | 15 | A | 25 | B | 35 | D |
| 6 | A | 16 | C | 26 | C | 36 | A |
| 7 | B | 17 | B | 27 | D | 37 | B |
| 8 | D | 18 | D | 28 | A | 38 | C |
| 9 | C | 19 | C | 29 | B | 39 | D |
| 10 | B | 20 | A | 30 | C | 40 | A |

---

## D1: Voice agent fundamentals and architectures

### Q1. The clinic's lawyer requires one exact sentence at the start of every call: "This call may be recorded for quality purposes." Which approach guarantees the words are spoken verbatim?

*Domain: D1 · Related lecture: 1.3 Cascaded vs speech-to-speech architectures*

- **A.** Put "Always say exactly: This call may be recorded..." at the top of a speech-to-speech model's instructions.
  - *Explanation:* Incorrect. The model will usually comply, but a generative model can paraphrase or skip it. "Usually" is not "guaranteed".
- **B.** Ask the caller to confirm they heard a disclaimer.
  - *Explanation:* Incorrect. That checks the caller, not what Riley said, and still needs the sentence spoken first.
- **C.** Send the fixed text straight to TTS with `session.say(...)` (available in a cascaded or half-cascade setup), so no model generates it.
  - *Explanation:* Correct. `session.say` speaks text you control through the TTS. Fixed legal or compliance lines are one of the reasons teams keep a TTS in the loop even when using a realtime model for understanding.
- **D.** Lower the LLM temperature to 0.
  - *Explanation:* Incorrect. Temperature 0 reduces variation but does not guarantee exact wording, and it affects every other reply too.

**Correct answer: C**

### Q2. Riley's LLM takes 2 seconds to generate a full three-sentence reply, yet callers hear her start speaking after about 700 ms. Why?

*Domain: D1 · Related lecture: 1.4 The latency budget*

- **A.** The pipeline streams: LLM tokens flow into TTS, which starts synthesising the first sentence while the rest is still being generated, so the caller waits for time to first token plus TTS time to first byte, not the full generation.
  - *Explanation:* Correct. Streaming between stages is why TTFT and TTFB are the numbers that matter for perceived latency, not total generation time.
- **B.** The LLM caches the whole answer from a previous call.
  - *Explanation:* Incorrect. Each reply is generated fresh. Prompt caching speeds up input processing but does not replay answers.
- **C.** TTS predicts what the LLM will say.
  - *Explanation:* Incorrect. TTS only speaks text it has received.
- **D.** The 2-second figure must be wrong, because voice agents cannot speak before the LLM finishes.
  - *Explanation:* Incorrect. They can and do: that is the point of a streaming pipeline.

**Correct answer: A**

### Q3. In a noisy reception area, a TV in the background keeps making Riley stop mid-sentence as if the caller interrupted. Which component is being triggered, and what helps?

*Domain: D1 · Related lecture: 1.2 What a voice agent actually is*

- **A.** The LLM; fix it by telling Riley to ignore the TV.
  - *Explanation:* Incorrect. The interruption happens before any text reaches the LLM.
- **B.** Voice activity detection (VAD), which flags any speech-like audio; noise cancellation, a stricter interruption threshold (minimum duration or words) and headset use all help.
  - *Explanation:* Correct. VAD detects speech presence, and speech from a TV is still speech. Filtering noise before VAD and requiring more evidence before an interruption counts are the standard fixes.
- **C.** The TTS engine, which stops when audio levels rise.
  - *Explanation:* Incorrect. TTS does not listen to the caller; the session stops playback when an interruption is detected.
- **D.** The WebRTC transport dropping packets.
  - *Explanation:* Incorrect. Packet loss causes choppy audio, not false barge-ins that correlate with the TV.

**Correct answer: B**

### Q4. On the realtime version of Riley, callers who pause to think are often answered too early. You are using OpenAI's semantic VAD for turn detection. What setting change is most appropriate?

*Domain: D1 · Related lecture: 6.2 Code-along: Riley on gpt-realtime*

- **A.** Switch the voice from "marin" to another voice.
  - *Explanation:* Incorrect. The voice affects how Riley sounds, not when she decides the caller has finished.
- **B.** Add "Wait longer before answering" to the instructions.
  - *Explanation:* Incorrect. Turn detection runs in the audio layer; the model's instructions do not control the end-of-turn decision.
- **C.** Disable turn detection so the model never responds automatically.
  - *Explanation:* Incorrect. Riley would never reply unless you trigger responses manually.
- **D.** Lower the semantic VAD eagerness (for example from "auto" to "low"), so the model waits longer when the caller sounds unfinished.
  - *Explanation:* Correct. Semantic VAD's eagerness controls how quickly it ends the turn. Lower eagerness suits callers who pause to think, at the cost of slightly slower responses.

**Correct answer: D**

### Q5. Over a long call, the realtime version's cost per minute keeps climbing, while the cascaded version stays flatter. What best explains this?

*Domain: D1 · Related lecture: 6.4 Head-to-head: cascaded vs realtime*

- **A.** Realtime models charge a flat fee per response.
  - *Explanation:* Incorrect. They are billed by tokens, not per response.
- **B.** Realtime models bill for silence while the caller is thinking.
  - *Explanation:* Incorrect. Silence is not the main driver; the conversation history is.
- **C.** Each new response processes the growing conversation, including earlier audio, as input tokens, and audio tokens are priced much higher than text tokens (caching reduces but does not remove this).
  - *Explanation:* Correct. Every turn re-sends context. In a cascaded pipeline that context is cheap text; in speech-to-speech it includes audio tokens. That is why the course's cost model prices realtime audio and cached tokens separately.
- **D.** The cascaded pipeline stops billing STT after the first minute.
  - *Explanation:* Incorrect. STT is billed for all audio sent to it.

**Correct answer: C**

---

## D2: LiveKit Agents core, setup and turn-taking

### Q6. A student's first `console` run fails with an error saying the turn detector's model files are missing. What should they run?

*Domain: D2 · Related lecture: 2.2 Python project setup with uv*

- **A.** `uv run agents/s03_hello_agent.py download-files`, which downloads the local model weights (Silero VAD and the turn detector) once.
  - *Explanation:* Correct. Local models are downloaded separately from Python packages. The production Dockerfile runs the same command at build time.
- **B.** `make test`
  - *Explanation:* Incorrect. Unit tests do not download models.
- **C.** `lk cloud auth`
  - *Explanation:* Incorrect. That authenticates the CLI; it does not fetch model files.
- **D.** `pip install --upgrade livekit-agents`
  - *Explanation:* Incorrect. The package is installed; the model weights are what is missing.

**Correct answer: A**

### Q7. You want to talk to Riley from the Agents Playground in your browser and have the agent reload automatically when you edit the code. Which command do you use?

*Domain: D2 · Related lecture: 3.4 Dev mode and the Agents Playground*

- **A.** `console`
  - *Explanation:* Incorrect. Console mode uses your local microphone and speakers and does not serve browser users.
- **B.** `dev`
  - *Explanation:* Correct. `dev` registers the agent server with LiveKit (so the Playground can dispatch it into a room) and hot-reloads on code changes.
- **C.** `start`
  - *Explanation:* Incorrect. `start` is the production mode, without hot reload.
- **D.** `download-files`
  - *Explanation:* Incorrect. It only downloads model weights and exits.

**Correct answer: B**

### Q8. You enable preemptive generation, so the LLM starts working on a reply before the end of the caller's turn is confirmed. What is the main trade-off?

*Domain: D2 · Related lecture: 3.6 VAD, turn detection and interruptions*

- **A.** Riley can no longer be interrupted.
  - *Explanation:* Incorrect. Interruption handling is independent of preemptive generation.
- **B.** Tool calls stop working.
  - *Explanation:* Incorrect. Tools work as usual once the reply is committed.
- **C.** The caller hears two replies for every turn.
  - *Explanation:* Incorrect. Only one reply is spoken; speculative work is discarded if the caller keeps talking.
- **D.** Lower latency when the guess is right, but wasted LLM tokens (cost) when the caller keeps talking and the speculative reply is thrown away.
  - *Explanation:* Correct. Preemptive generation overlaps LLM work with end-of-turn detection. The price is extra token spend on turns where the caller was not actually finished.

**Correct answer: D**

### Q9. A student practises with `MOCK_MODE=1 ... console --text` for a week at zero cost. What has this **not** tested?

*Domain: D2 · Related lecture: 2.7 Spending caps, free tiers and offline mock mode*

- **A.** Whether the agent file imports and starts correctly.
  - *Explanation:* Incorrect. Mock mode still runs the agent code, so start-up problems appear.
- **B.** Whether the conversation loop and text input work.
  - *Explanation:* Incorrect. Mock mode exercises the session loop with typed input.
- **C.** Real model behaviour and audio: how the real LLM follows the prompt and calls tools, and how STT, turn-taking and TTS behave.
  - *Explanation:* Correct. Mock mode replaces the LLM with a scripted fake and removes STT and TTS. It is for practising the mechanics at zero cost, not for judging quality.
- **D.** Whether the student can use the terminal.
  - *Explanation:* Incorrect. That was tested plenty.

**Correct answer: C**

---

## D3: Prompting for the ear

### Q10. Riley's LLM occasionally outputs `**Tuesday**`, but callers never hear "asterisk". When lecture 3.9 runs with `BROKEN=markdown`, they do. What explains the difference?

*Domain: D3 · Related lecture: 4.1 Why chat prompts fail on voice*

- **A.** The broken mode uses a different TTS provider.
  - *Explanation:* Incorrect. The provider is the same; a processing step is switched off.
- **B.** By default the session applies TTS text transforms that strip markdown and emojis before synthesis; the broken mode asks for markdown and switches that filter off. The filter is a safety net, so prompt output rules are still needed for lists, URLs and long answers.
  - *Explanation:* Correct. Text transforms clean up formatting symbols, but they cannot turn a bulleted list or a URL into good speech. That is the job of the prompt.
- **C.** The LLM only produces markdown in broken mode.
  - *Explanation:* Incorrect. The question states the LLM produces it occasionally in normal mode too.
- **D.** Callers' phones remove asterisks.
  - *Explanation:* Incorrect. Phones carry audio; there is no text to filter.

**Correct answer: B**

### Q11. The TTS keeps mispronouncing the caller's name "Siobhan" as "See-oh-ban". What is the best combination of fixes?

*Domain: D3 · Related lecture: 4.3 Numbers, dates, names and pronunciation*

- **A.** Confirm the spelling with the caller, and add a pronunciation hint for the TTS (a respelling such as "shi-VAWN" in a text transform, or the provider's custom pronunciation feature).
  - *Explanation:* Correct. The spelling gets the booking right; the pronunciation hint makes Riley say it the way the caller does. Keep the correct spelling in data and change only what is sent to TTS.
- **B.** Store the name as "Shivawn" in the booking.
  - *Explanation:* Incorrect. That corrupts the patient record to fix a speech problem.
- **C.** Avoid saying the caller's name at all.
  - *Explanation:* Incorrect. Read-backs need the name, and callers notice when it is avoided.
- **D.** Switch the LLM to a larger model.
  - *Explanation:* Incorrect. Pronunciation is produced by the TTS, not the LLM.

**Correct answer: A**

### Q12. Why does the booking agent greet callers with `self.session.say(prompts.GREETING)` in `on_enter` rather than `generate_reply(...)`?

*Domain: D3 · Related lecture: 4.4 Greetings, silence and "are you still there?"*

- **A.** `generate_reply` cannot be called from `on_enter`.
  - *Explanation:* Incorrect. The multi-agent specialists use `generate_reply` in `on_enter`.
- **B.** `say` is required for the AI disclosure to be legal.
  - *Explanation:* Incorrect. Disclosure can be generated; `say` just makes it predictable.
- **C.** A fixed greeting skips the LLM, so it starts faster and is identical on every call, which makes the disclosure dependable and tests simple.
  - *Explanation:* Correct. The greeting is the one line you know in advance. Sending it straight to TTS removes LLM latency from the first impression and guarantees the wording.
- **D.** `say` makes the greeting uninterruptible by default.
  - *Explanation:* Incorrect. Interruptibility is a separate option; it is not the reason for using `say` here.

**Correct answer: C**

---

## D4: Tools, state and confirmation

### Q13. An early version of `find_available_slots` returned a JSON list of all 40 free slots for the week. Riley started reading out long lists and sometimes picked times the caller never heard. What is the better design?

*Domain: D4 · Related lecture: 5.1 How function tools work in LiveKit*

- **A.** Return the same JSON but tell the model to summarise it.
  - *Explanation:* Incorrect. The model still has to reason over 40 items each time, and summaries vary.
- **B.** Return at most three options as speakable text plus a machine value for each (for example `[slot_start=2026-10-06T09:30]`) with an instruction never to read the machine value aloud.
  - *Explanation:* Correct. Tool results are part of the voice UX. Limiting options and separating spoken text from machine values is what the course's `find_available_slots` does.
- **C.** Return nothing and let the model propose times.
  - *Explanation:* Incorrect. That invites hallucinated availability.
- **D.** Return the slots as a markdown table.
  - *Explanation:* Incorrect. Tables are unspeakable and invite formatting symbols.

**Correct answer: B**

### Q14. After a reschedule, the front desk finds two active appointments for the same patient: the old one and the new one. What is the root cause and fix?

*Domain: D4 · Related lecture: 5.6 Reschedule, cancel and tool errors*

- **A.** The caller asked twice; add "don't book twice" to the prompt.
  - *Explanation:* Incorrect. Prompt rules do not fix a tool that creates instead of moves.
- **B.** The scheduler is too slow; add filler speech.
  - *Explanation:* Incorrect. Speed has nothing to do with duplicate records.
- **C.** Two callers booked the same slot at once.
  - *Explanation:* Incorrect. The duplicates belong to the same patient, and the scheduler prevents double-booking a slot.
- **D.** The agent used `book_appointment` for a reschedule. `reschedule_appointment` must move the existing appointment (find the upcoming one, then reschedule it), and a behaviour test should assert that the reschedule tool, not the booking tool, is called and that exactly one appointment stays active.
  - *Explanation:* Correct. Distinct tools with clear descriptions, plus a test on the resulting calendar state, prevent this class of bug.

**Correct answer: D**

### Q15. In `BookingAgent.on_enter`, you want to greet the caller by name if the Greeter already learned it. How do you read it?

*Domain: D4 · Related lecture: 5.7 Session state with userdata*

- **A.** `self.session.userdata.caller_name`
  - *Explanation:* Correct. Outside tools, the session's `userdata` holds the shared `CallState`. Inside tools the same object is `context.userdata`.
- **B.** `context.userdata.caller_name`
  - *Explanation:* Incorrect. There is no `context` in `on_enter`; `RunContext` is only passed to tools.
- **C.** Ask the LLM what the caller's name was.
  - *Explanation:* Incorrect. That is slower and less reliable than reading stored state.
- **D.** A module-level `CALLER_NAME` variable.
  - *Explanation:* Incorrect. Globals are shared between concurrent calls in the same process.

**Correct answer: A**

### Q16. You set filler speech on `find_available_slots` with `delay=0.3`. Callers now hear "One moment while I check the schedule" on almost every lookup, even fast ones, and say Riley sounds slow. What should you change?

*Domain: D4 · Related lecture: 5.5 Hiding latency while tools run*

- **A.** Remove the filler entirely.
  - *Explanation:* Incorrect. Slow lookups would then produce dead air, which is worse.
- **B.** Make the filler sentence longer.
  - *Explanation:* Incorrect. That makes every lookup feel even slower.
- **C.** Raise the delay (the course uses 0.8 s) so the filler only plays when a lookup is genuinely slow.
  - *Explanation:* Correct. The delay is the threshold for "slow enough to need a filler". Set it above your typical tool latency so most calls stay silent.
- **D.** Play the filler before every tool call via the prompt.
  - *Explanation:* Incorrect. That guarantees the filler on fast calls, the exact complaint.

**Correct answer: C**

---

## D5: Knowledge, handoffs and multilingual

### Q17. FAQ answers take noticeably longer than other turns because the model first calls `lookup_clinic_info` and then answers. Most calls to this clinic are FAQ questions. What alternative from lecture 7.1 removes the extra round trip?

*Domain: D5 · Related lecture: 7.1 RAG for voice*

- **A.** Put the entire FAQ in the system prompt.
  - *Explanation:* Incorrect. It works for tiny FAQs, but it adds tokens to every turn and scales badly. The question asks for the retrieval-based alternative.
- **B.** Retrieve in `on_user_turn_completed` and inject the top passage into the turn's context before the LLM runs, so the model answers in a single generation.
  - *Explanation:* Correct. Pre-turn injection trades a little retrieval time on every turn for no extra LLM step on FAQ turns. With a millisecond-fast local index, that is a good trade when most calls are FAQs.
- **C.** Call the tool twice to warm a cache.
  - *Explanation:* Incorrect. That adds round trips instead of removing them.
- **D.** Switch to a vector database.
  - *Explanation:* Incorrect. The delay comes from the extra LLM step, not from retrieval speed.

**Correct answer: B**

### Q18. In `s07_multi_agent.py`, `carry_over()` copies the chat context with `exclude_instructions=True` before handing it to the next agent. Why exclude instructions?

*Domain: D5 · Related lecture: 7.5 Code-along: Greeter → Booking → Billing*

- **A.** Instructions contain API keys.
  - *Explanation:* Incorrect. Instructions never contain secrets.
- **B.** It saves exactly one token.
  - *Explanation:* Incorrect. The point is behaviour, not a trivial token saving.
- **C.** LiveKit does not allow instructions to be copied.
  - *Explanation:* Incorrect. Copying them is possible; it is just undesirable.
- **D.** The specialist should see what the caller said but follow its own system prompt, not the previous agent's; carrying the old instructions over would give the model two conflicting roles.
  - *Explanation:* Correct. Conversation history carries over; the role does not. The context is also truncated to recent items to keep the prompt short.

**Correct answer: D**

### Q19. Riley starts receiving Spanish-speaking callers. Which plan follows lecture 7.8?

*Domain: D5 · Related lecture: 7.8 Multilingual Riley: Spanish and Hindi callers*

- **A.** Keep the English STT; the LLM will translate whatever it receives.
  - *Explanation:* Incorrect. English STT transcribes Spanish poorly, so the LLM receives garbage to translate.
- **B.** Translate Riley's replies only, but keep English STT and TTS.
  - *Explanation:* Incorrect. Recognition and voice must also match the language.
- **C.** Configure the STT language (or a multilingual model), use a turn detector that supports the language, pick a TTS voice for that language, serve FAQ answers in that language, and add tests with Spanish inputs.
  - *Explanation:* Correct. Every stage is language-sensitive: recognition, turn-taking, knowledge and voice. The course drives this with the `LANGUAGE` setting in `src/maple/config.py`.
- **D.** Ask Spanish speakers to call back with an interpreter.
  - *Explanation:* Incorrect. The clinic's FAQ says the team speaks Spanish, and the goal is to serve these callers.

**Correct answer: C**

---

## D6: Telephony

### Q20. Your dispatch rule uses `dispatchRuleIndividual` with `roomPrefix: "call-"`. What does that do?

*Domain: D6 · Related lecture: 8.2 Inbound calls: Twilio trunk + LiveKit dispatch rule*

- **A.** Each inbound call gets its own new room named with the `call-` prefix, and the named agent is dispatched into it.
  - *Explanation:* Correct. Individual rules isolate callers from each other. That is what a receptionist needs.
- **B.** All calls join one shared room called `call-`.
  - *Explanation:* Incorrect. That describes a direct rule to a fixed room, which would put callers in the same conversation.
- **C.** Only numbers starting with "call-" are accepted.
  - *Explanation:* Incorrect. The prefix names rooms; it does not filter callers.
- **D.** Calls are recorded to files prefixed "call-".
  - *Explanation:* Incorrect. Dispatch rules do not configure recording.

**Correct answer: A**

### Q21. The front desk complains that transferred callers arrive and have to explain everything again. Which change addresses this?

*Domain: D6 · Related lecture: 8.4 Transfer to a human and ending calls*

- **A.** Transfer faster with no heads-up.
  - *Explanation:* Incorrect. Speed does not give the receptionist context.
- **B.** A warm transfer: Riley (or a supervisor leg) briefs the receptionist with a short summary before connecting the caller, instead of a cold SIP REFER hand-off.
  - *Explanation:* Correct. A cold transfer hands the call over blind. A warm transfer shares context first. At minimum, log the `reason` passed to `transfer_to_human` where staff can see it.
- **C.** Tell callers to repeat themselves quickly.
  - *Explanation:* Incorrect. That describes the problem, not a fix.
- **D.** Disable transfers.
  - *Explanation:* Incorrect. Escalation to a human is a core requirement.

**Correct answer: B**

### Q22. `agents/s08_outbound_call.py` dispatches Riley for a reminder call, but the call fails with a trunk error. Inbound calls work fine. What is the most likely cause?

*Domain: D6 · Related lecture: 8.5 Outbound calls: appointment reminders*

- **A.** The agent name is wrong.
  - *Explanation:* Incorrect. The dispatch succeeded; the failure happens when dialling.
- **B.** Outbound calls do not work with Twilio.
  - *Explanation:* Incorrect. Twilio Elastic SIP trunks support outbound (termination) calls.
- **C.** The caller's phone is off.
  - *Explanation:* Incorrect. That produces no answer or voicemail, not a trunk error.
- **D.** `SIP_OUTBOUND_TRUNK_ID` is missing or points at the inbound trunk; outbound calls need a separate LiveKit outbound trunk configured with the Twilio termination URI and credentials.
  - *Explanation:* Correct. Inbound and outbound are separate trunks in LiveKit. Creating the SIP participant requires the outbound trunk's ID.

**Correct answer: D**

### Q23. Maple Street Dental records calls for quality review and serves patients in California. What does lecture 8.6 advise (not legal advice)?

*Domain: D6 · Related lecture: 8.6 Compliance: disclosure, consent and recording*

- **A.** Recording is fine as long as the clinic consents.
  - *Explanation:* Incorrect. That is the one-party consent model, which does not apply in all-party consent states such as California.
- **B.** Record only the agent's side of the call.
  - *Explanation:* Incorrect. The caller's voice is exactly what consent rules protect, and a one-sided recording is of little use for quality review anyway.
- **C.** Announce the recording at the start of the call (California requires the consent of all parties), offer a way to opt out, and get legal review of the wording.
  - *Explanation:* Correct. A clear, early announcement is the standard approach for all-party consent states, and it pairs naturally with the AI disclosure.
- **D.** Recording laws do not apply to AI agents.
  - *Explanation:* Incorrect. The laws apply to the recording, regardless of who is speaking.

**Correct answer: C**

---

## D7: Testing and evaluation

### Q24. A team has 40 simulated-caller tests, 5 behaviour tests and 3 unit tests. CI takes 25 minutes, costs money on every push and fails randomly. What is the best restructuring?

*Domain: D7 · Related lecture: 9.2 The voice testing pyramid*

- **A.** Invert it: move rules into pure-Python unit tests, cover tool order and arguments with behaviour tests, and keep a small set of simulated callers for end-to-end scenarios (running them on a schedule or before release).
  - *Explanation:* Correct. The pyramid puts many fast, deterministic tests at the bottom and few slow, costly ones at the top. That makes CI fast, cheap and trustworthy.
- **B.** Add retries to every simulated test.
  - *Explanation:* Incorrect. Retries hide flakiness and multiply cost.
- **C.** Delete all simulated tests.
  - *Explanation:* Incorrect. They catch conversation-level problems nothing else does; there should just be fewer of them.
- **D.** Run the whole suite only once a month.
  - *Explanation:* Incorrect. Regressions would ship for weeks before being noticed.

**Correct answer: A**

### Q25. Why can LiveKit behaviour tests run with `session.run(user_input="...")` and no audio at all?

*Domain: D7 · Related lecture: 9.3 Behavior tests with LiveKit's test framework*

- **A.** Because audio is never a source of bugs.
  - *Explanation:* Incorrect. Audio is a major source of bugs; it is just tested at a different layer.
- **B.** Behaviour tests target the agent's decisions (instructions, tool choice and arguments, replies) through a text session; audio stages are tested separately with WER, latency and audio-in tests.
  - *Explanation:* Correct. Separating decision logic from audio makes behaviour tests fast and cheap, and lets each audio problem be measured with the right metric.
- **C.** Because the test framework converts text to audio and back automatically.
  - *Explanation:* Incorrect. `user_input` text goes straight to the session as the user's turn.
- **D.** Because LiveKit requires tests to be text-only.
  - *Explanation:* Incorrect. Audio-in testing is possible where supported (lecture 9.13).

**Correct answer: B**

### Q26. A bug report shows `book_appointment` was called with `slot_start="Tuesday 10am"` instead of the `2026-10-06T10:00` value the tool offered. Which test assertion catches this in future?

*Domain: D7 · Related lecture: 9.4 Asserting tool calls and arguments*

- **A.** `result.expect.contains_function_call(name="book_appointment")`
  - *Explanation:* Incorrect. It confirms the call happened but ignores the arguments, which were the bug.
- **B.** A judge asking whether the booking "sounded correct".
  - *Explanation:* Incorrect. The spoken confirmation might sound fine while the stored slot is wrong.
- **C.** `result.expect.next_event().is_function_call(name="book_appointment", arguments={...})` with the exact `slot_start` from the mocked or pinned availability.
  - *Explanation:* Correct. Asserting arguments against deterministic availability catches wrong formats and wrong slots before they reach the calendar.
- **D.** Counting the number of assistant messages.
  - *Explanation:* Incorrect. Message counts say nothing about tool arguments.

**Correct answer: C**

### Q27. Your DeepEval judge uses the same model as Riley, and scores almost every transcript 0.9 or above, including ones the team considers poor. What should you do?

*Domain: D7 · Related lecture: 9.6 LLM-as-judge with DeepEval on transcripts*

- **A.** Lower the threshold so everything passes.
  - *Explanation:* Incorrect. The judge already passes everything; the problem is that it does not discriminate.
- **B.** Remove the judge and rely on exact string matches.
  - *Explanation:* Incorrect. Exact matching does not work for conversational behaviour.
- **C.** Ask Riley to grade herself at the end of each call.
  - *Explanation:* Incorrect. Self-grading has the same bias, in a worse place.
- **D.** Calibrate the judge: write sharper, observable criteria, compare its scores with human labels on a sample of good and bad transcripts, and consider a different or stronger judge model to reduce self-preference.
  - *Explanation:* Correct. An LLM judge is a measuring instrument; calibrate it against people before trusting its thresholds.

**Correct answer: D**

### Q28. Comparing two STT providers, provider A writes "Dr. Chen at 9:30" and provider B writes "doctor chen at nine thirty" for the same audio. Your raw WER says A is much worse. What is wrong with the comparison?

*Domain: D7 · Related lecture: 9.7 Measuring STT accuracy with WER*

- **A.** Formatting differences are being counted as recognition errors; apply the same normalisation (lowercase, punctuation, replacements such as "dr" → "doctor", number formatting) to both hypotheses and the reference before computing WER.
  - *Explanation:* Correct. Normalisation matters more than the algorithm. The course's `maple.wer.normalize()` exists for exactly this reason.
- **B.** WER cannot compare providers.
  - *Explanation:* Incorrect. It can, as long as normalisation is identical.
- **C.** Provider A is simply worse.
  - *Explanation:* Incorrect. Both transcripts say the same thing.
- **D.** Use character error rate instead, which ignores formatting.
  - *Explanation:* Incorrect. Character error rate is just as sensitive to "9:30" versus "nine thirty".

**Correct answer: A**

### Q29. All behaviour tests pass, but callers with strong accents keep getting bookings for the wrong day. Which test type from Section 9 targets this gap?

*Domain: D7 · Related lecture: 9.13 Audio-in tests: real caller audio through the pipeline*

- **A.** More text behaviour tests with accented spellings.
  - *Explanation:* Incorrect. Text tests bypass STT, which is where the error happens.
- **B.** Audio-in tests: feed recorded caller audio (accents, phone noise) through the STT stage, assert WER thresholds on the transcripts, then run those transcripts through the behaviour tests.
  - *Explanation:* Correct. Text tests assume perfect transcripts. Audio-in tests measure what the real pipeline hears and connect STT errors to booking outcomes.
- **C.** A latency budget test.
  - *Explanation:* Incorrect. Wrong days are an accuracy problem, not a timing problem.
- **D.** A higher judge threshold.
  - *Explanation:* Incorrect. Judges evaluate replies; they cannot fix what STT misheard.

**Correct answer: B**

### Q30. An open-source contributor's pull request fails CI because `OPENAI_API_KEY` is not available to workflows from forks. What should the CI design be?

*Domain: D7 · Related lecture: 9.10 Voice agent tests in CI*

- **A.** Put the API key in the repository so forks can use it.
  - *Explanation:* Incorrect. That leaks the key to anyone who can read the repo.
- **B.** Disable CI for pull requests.
  - *Explanation:* Incorrect. Unit tests can and should still run.
- **C.** Run unit tests always, make key-dependent agent tests and evals skip cleanly when the secret is absent, and run them on the main branch or trusted PRs where secrets exist.
  - *Explanation:* Correct. This is the course's `ci.yml` design: fast offline tests everywhere, paid tests where secrets are available, and no failures just because a key is missing.
- **D.** Ask contributors to email their own keys.
  - *Explanation:* Incorrect. Collecting other people's keys is unsafe and unnecessary.

**Correct answer: C**

---

## D8: Observability and cost

### Q31. How does the course's latency report compute a voice-to-voice value for each turn from the exported metrics?

*Domain: D8 · Related lecture: 10.2 Collecting metrics and usage*

- **A.** It measures the call's total duration and divides by the number of turns.
  - *Explanation:* Incorrect. That mixes speaking time and listening time with response latency.
- **B.** It uses the TTS duration only.
  - *Explanation:* Incorrect. TTS duration is how long Riley speaks, not how long the caller waits.
- **C.** It reads a `voice_to_voice` field that LiveKit writes directly.
  - *Explanation:* Incorrect. The course derives it from separate stage metrics.
- **D.** It joins EOU, LLM and TTS records that share a `speech_id`, and sums end-of-utterance delay, LLM time to first token and TTS time to first byte.
  - *Explanation:* Correct. `maple.latency.samples_from_metrics()` groups records by `speech_id` and sums the three stages for turns that have all of them.

**Correct answer: D**

### Q32. Why do voice agents benefit so much from LLM prompt caching?

*Domain: D8 · Related lecture: 10.4 Cost per minute*

- **A.** Every turn re-sends the system prompt and the whole conversation so far, so a large stable prefix is sent many times per call; cached input tokens are billed at a fraction of the normal price and processed faster.
  - *Explanation:* Correct. Keep the system prompt stable and at the start so the cache hits. The course's cost model prices cached input tokens separately for this reason.
- **B.** Caching stores audio so STT is cheaper.
  - *Explanation:* Incorrect. Prompt caching applies to LLM input tokens, not audio.
- **C.** Caching lets the LLM skip generating replies.
  - *Explanation:* Incorrect. Output tokens are always generated and billed.
- **D.** Caching removes the need for TTS.
  - *Explanation:* Incorrect. TTS is unaffected by LLM caching.

**Correct answer: A**

### Q33. After a prompt change, the containment rate (calls handled without a human) jumped from 70% to 95%, but patient complaints also rose. What should you check first?

*Domain: D8 · Related lecture: 10.5 Dashboards and alerts that matter*

- **A.** Nothing; higher containment is always better.
  - *Explanation:* Incorrect. Containment is only good when callers' problems are actually solved.
- **B.** Whether Riley is now failing to escalate when she should: transcripts where callers asked for a person, `transfer_to_human` call counts and failures, and call outcomes alongside containment.
  - *Explanation:* Correct. A sudden containment jump plus complaints often means missed escalations or a broken transfer tool. Pair containment with transfer rate, failed tool calls and outcome quality.
- **C.** TTS cost per minute.
  - *Explanation:* Incorrect. Cost does not explain complaints about service.
- **D.** Whether the LLM's temperature is too low.
  - *Explanation:* Incorrect. There is no evidence pointing at temperature.

**Correct answer: B**

---

## D9: Security and safety

### Q34. You must guarantee Riley never speaks a medication dose, even if the model is manipulated into generating one. Where does the course put that deterministic check?

*Domain: D9 · Related lecture: 11.4 Output guardrails and topic boundaries*

- **A.** Only in the system prompt.
  - *Explanation:* Incorrect. Prompts guide the model but can be overridden or ignored.
- **B.** In the STT configuration.
  - *Explanation:* Incorrect. STT processes the caller's speech, not Riley's.
- **C.** In an output guardrail that inspects the generated text before it reaches TTS (for example by overriding `llm_node` or checking in `transcription_node`), replacing unsafe content with a safe refusal and escalation.
  - *Explanation:* Correct. Output hooks run on every reply, so they enforce rules regardless of what the model was persuaded to say. Keep the prompt rule too; defence in depth.
- **D.** In the post-call report.
  - *Explanation:* Incorrect. By then the caller has already heard the dose.

**Correct answer: C**

### Q35. A vendor pitches "voice recognition: Riley can tell it's really the patient from their voice". Given lecture 11.1's threat model, how should you treat this?

*Domain: D9 · Related lecture: 11.1 Threat model for voice agents*

- **A.** Adopt it and remove `verify_caller`.
  - *Explanation:* Incorrect. Voice cloning makes voice alone an unreliable identity check.
- **B.** Use it only for callers over 65.
  - *Explanation:* Incorrect. Age does not change the attack.
- **C.** Voice is safe as long as the call is recorded.
  - *Explanation:* Incorrect. Recording does not prevent a cloned voice from passing.
- **D.** Do not rely on voice as authentication, because voice cloning is a listed threat; keep knowledge-based verification (phone on file plus date of birth), limits on attempts, and human fallback for sensitive changes.
  - *Explanation:* Correct. Cloned voices are cheap to produce. Treat voice as a convenience signal at most, never as the only factor.

**Correct answer: D**

### Q36. What retention policy fits lecture 11.3's guidance for Riley's call data?

*Domain: D9 · Related lecture: 11.3 PII redaction in transcripts and logs*

- **A.** Keep redacted transcripts and metrics for a defined period that serves quality review, do not keep raw audio unless there is a stated purpose and consent, and delete on schedule.
  - *Explanation:* Correct. Minimise what you store, redact what you keep, and set expiry. Data you do not hold cannot leak.
- **B.** Keep everything forever in case it is useful for training.
  - *Explanation:* Incorrect. Indefinite retention of patient data maximises breach impact and conflicts with privacy obligations.
- **C.** Delete everything immediately, including metrics.
  - *Explanation:* Incorrect. You would lose the observability needed to run the service.
- **D.** Keep raw audio, but only in the log files.
  - *Explanation:* Incorrect. Logs are one of the least controlled places to store sensitive data.

**Correct answer: A**

---

## D10: Deployment and production hardening

### Q37. You deploy a new version of Riley at 10:00 on a Monday while 12 calls are in progress. What should happen to those calls?

*Domain: D10 · Related lecture: 12.1 Agent server architecture and scaling*

- **A.** They are dropped and callers ring back.
  - *Explanation:* Incorrect. Dropping patients mid-booking is exactly what graceful deployment avoids.
- **B.** The old agent server drains: it stops accepting new jobs, lets active calls finish (within a drain timeout longer than a typical call), then exits while new calls go to the new version.
  - *Explanation:* Correct. Draining makes rolling deploys invisible to callers.
- **C.** The calls are moved live to the new version's processes.
  - *Explanation:* Incorrect. Active jobs stay in their process; they are not migrated mid-call.
- **D.** Deploys must wait until there are zero calls.
  - *Explanation:* Incorrect. With draining, you can deploy any time.

**Correct answer: B**

### Q38. During a provider incident, the LLM API sometimes hangs for 30 seconds before failing, leaving callers in silence. What hardening from lecture 13.3 addresses this?

*Domain: D10 · Related lecture: 13.3 Hardening: fallbacks, timeouts, error speech*

- **A.** A longer `user_away_timeout`.
  - *Explanation:* Incorrect. That concerns caller silence, not a hanging provider.
- **B.** Asking callers to be patient in the greeting.
  - *Explanation:* Incorrect. Callers will not wait 30 seconds, whatever the greeting says.
- **C.** Tight connection options (timeouts and a small retry budget via `conn_options`) plus a fallback provider list, so a hung request fails fast to the fallback model, with spoken error recovery if everything fails.
  - *Explanation:* Correct. Timeouts turn a hang into a fast failure, fallbacks turn the failure into a working reply, and error speech covers the worst case.
- **D.** Increase `max_tool_steps`.
  - *Explanation:* Incorrect. Tool steps are unrelated to provider timeouts.

**Correct answer: C**

### Q39. For Riley's web front end (lecture 12.5), a teammate suggests putting `LIVEKIT_API_SECRET` in the React app so the browser can create its own access tokens. What is the correct design?

*Domain: D10 · Related lecture: 12.5 A web front end for Riley*

- **A.** It is fine if the secret is minified.
  - *Explanation:* Incorrect. Anything shipped to the browser can be read by anyone.
- **B.** Use the same token for every visitor.
  - *Explanation:* Incorrect. Shared tokens cannot be scoped or revoked per user and would put everyone in the same room.
- **C.** Put the secret in `localStorage`.
  - *Explanation:* Incorrect. It is still in the browser.
- **D.** Keep the secret on a server: a small token endpoint mints short-lived, room-scoped tokens (optionally including the agent dispatch), and the browser only ever receives the token.
  - *Explanation:* Correct. The LiveKit agent starters use exactly this token-server pattern.

**Correct answer: D**

---

## D11: Pipecat and choosing a stack

### Q40. A team already streams phone audio over WebSockets from their telephony provider's media-stream feature and does not want to run LiveKit rooms. Which framework property makes Pipecat a natural fit?

*Domain: D11 · Related lecture: 14.3 LiveKit Agents vs Pipecat vs managed platforms*

- **A.** Pipecat's pipeline is transport-agnostic: the same processors can run behind different transports (WebRTC, WebSocket with telephony serializers, and others), so they can plug in their existing media stream.
  - *Explanation:* Correct. Pipecat separates transport from processing, which suits teams with an existing audio path. LiveKit Agents is built around LiveKit rooms and dispatch, which is a strength when you want LiveKit's SFU, SIP and scaling.
- **B.** Pipecat does not support function calling, so it is simpler.
  - *Explanation:* Incorrect. Pipecat supports function calling (lecture 14.2).
- **C.** Pipecat is a managed platform with per-minute pricing.
  - *Explanation:* Incorrect. Pipecat is an open-source framework you run yourself.
- **D.** LiveKit Agents cannot handle phone calls.
  - *Explanation:* Incorrect. Section 8 puts Riley on a phone number with LiveKit SIP.

**Correct answer: A**
