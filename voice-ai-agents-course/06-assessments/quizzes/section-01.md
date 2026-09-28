# Quiz: Voice Agent Fundamentals (Section 1)

| Field | Value |
|---|---|
| Udemy lecture | 1.6 Quiz: Voice agent fundamentals |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 1.2, 1.3, 1.4, 1.5 |

---

### Q1. Maple Street Dental's current phone system says "Press 1 for appointments, press 2 for billing." The owner asks what would actually change if Riley replaced it. Which answer best describes the difference?

*Related lecture: 1.2 What a voice agent actually is*

- **A.** Riley would play the same menu but with a more natural-sounding recorded voice.
  - *Explanation:* Incorrect. A nicer recording is still an IVR. The voice is not what makes something an agent; the decision-making is.
- **B.** Riley would understand free-form speech, decide what to do next with an LLM, call tools such as the booking system, and generate a spoken reply.
  - *Explanation:* Correct. A voice agent turns open-ended speech into text, reasons about it with an LLM, takes actions through tools, and speaks a response it generated for this caller. An IVR follows a fixed tree.
- **C.** Riley would record voicemails and email transcripts to the front desk.
  - *Explanation:* Incorrect. That is voicemail transcription. It takes no actions and holds no conversation.
- **D.** Riley would be a text chatbot on the clinic website that also reads its answers aloud.
  - *Explanation:* Incorrect. Reading chatbot output aloud skips everything that makes voice hard: turn-taking, interruptions, latency and speech recognition on phone audio.

**Correct answer: B**

---

### Q2. During testing, callers who pause mid-sentence ("My insurance ID is... hang on... X-Y-Z") keep getting cut off by Riley. Which component should you look at first?

*Related lecture: 1.2 What a voice agent actually is*

- **A.** The TTS engine, because it is starting playback too early.
  - *Explanation:* Incorrect. TTS only speaks once the pipeline has decided to reply. The problem is the decision that the caller had finished.
- **B.** The LLM, because it answers before reading the full transcript.
  - *Explanation:* Incorrect. The LLM only receives the transcript after the turn has been declared complete, so it cannot be the cause of the premature cut-off.
- **C.** The WebRTC transport, because packets arrive out of order.
  - *Explanation:* Incorrect. Transport problems cause choppy or missing audio, not a consistent pattern of replying during natural pauses.
- **D.** Turn detection (endpointing), which decides when the caller has finished speaking.
  - *Explanation:* Correct. VAD only detects whether someone is speaking right now. Turn detection decides whether a pause is the end of the turn. Silence-only endpointing with a short delay cuts people off mid-thought, and a semantic turn detector or a longer minimum delay fixes it.

**Correct answer: D**

---

### Q3. A clinic group wants Riley to use one specific cloned brand voice from their TTS provider, log exactly what text was spoken on every call, and swap the STT vendor later without rewriting the agent. Which architecture fits these requirements best?

*Related lecture: 1.3 Cascaded vs speech-to-speech architectures*

- **A.** A cascaded STT → LLM → TTS pipeline.
  - *Explanation:* Correct. Each stage is a separate component, so you choose any TTS voice, you always have the exact text sent to TTS, and you can replace STT, LLM or TTS independently. That control is the main strength of cascaded pipelines.
- **B.** A speech-to-speech realtime model with its built-in voices.
  - *Explanation:* Incorrect. A speech-to-speech model generates audio directly with its own voices, so you cannot use the clinic's cloned voice, and the text transcript of the model's speech comes from a side channel rather than being the exact input to a TTS engine.
- **C.** An IVR with pre-recorded prompts in the brand voice.
  - *Explanation:* Incorrect. This keeps the voice but loses open-ended conversation and tool use, which is the reason to build an agent at all.
- **D.** Any architecture works; these requirements do not affect the choice.
  - *Explanation:* Incorrect. Voice choice, transcript fidelity and component swapping are exactly the trade-offs that separate cascaded from speech-to-speech designs.

**Correct answer: A**

---

### Q4. Your team likes how natural OpenAI's realtime model sounds when it listens, but marketing insists Riley must keep the Cartesia brand voice. What is the name of the design that gives you both?

*Related lecture: 1.3 Cascaded vs speech-to-speech architectures*

- **A.** Full cascade: separate STT, LLM and TTS.
  - *Explanation:* Incorrect. A full cascade uses a text LLM, so you lose the realtime model's direct audio understanding.
- **B.** Pure speech-to-speech with a system prompt that asks the model to "sound like the Cartesia voice".
  - *Explanation:* Incorrect. Prompting cannot change the realtime model's output voice into another provider's voice.
- **C.** Half-cascade (hybrid): the realtime model takes audio in and returns text, and your own TTS speaks it.
  - *Explanation:* Correct. The realtime model handles listening and reasoning, and its text output goes to the TTS you choose. You trade a little latency for brand-voice control. You will build this in lecture 6.3 with `modalities=["text"]`.
- **D.** Running two agents in the same room, one realtime and one cascaded, and picking the better answer.
  - *Explanation:* Incorrect. That doubles cost and latency and creates talk-over problems; it is not a recognised architecture.

**Correct answer: C**

---

### Q5. You measure one turn of a cascaded agent: endpointing delay 500 ms, final transcript 100 ms after that (overlapping nothing), LLM time to first token 450 ms, TTS time to first byte 200 ms, network 100 ms. Roughly how long does the caller wait, and how does it compare with the course's target?

*Related lecture: 1.4 The latency budget: why 800 ms is the magic number*

- **A.** About 450 ms, because only the LLM step matters.
  - *Explanation:* Incorrect. The caller waits for every sequential stage, not just the slowest one.
- **B.** About 800 ms, exactly on target.
  - *Explanation:* Incorrect. Adding the stages gives 500 + 100 + 450 + 200 + 100 = 1,350 ms, not 800 ms.
- **C.** About 1,350 ms, over the course's under-one-second goal, with endpointing and LLM TTFT as the biggest items.
  - *Explanation:* Correct. The stages run one after another, so they add up to about 1.35 s. The course targets under one second voice-to-voice (with about 800 ms as the "feels natural" mark), and the two largest line items, endpointing and LLM TTFT, are where to start optimising.
- **D.** About 2,700 ms, because every stage runs twice (once for the caller and once for the agent).
  - *Explanation:* Incorrect. Each stage runs once per turn; nothing is doubled.

**Correct answer: C**

---

### Q6. In a pilot, several callers say "Hello? Are you there?" right before Riley starts answering, and the two voices collide. What is the most likely explanation?

*Related lecture: 1.4 The latency budget: why 800 ms is the magic number*

- **A.** The response gap is well over a second, longer than the 200 to 300 ms gap people expect in conversation, so callers assume the line went dead.
  - *Explanation:* Correct. Humans take turns with very short gaps. When silence stretches past about a second, callers start speaking again, which then collides with the agent's late reply. Reducing voice-to-voice latency is the fix.
- **B.** The callers are testing whether Riley is a human.
  - *Explanation:* Incorrect. Some might be, but a consistent "Hello?" right before the reply points to a timing problem, not curiosity.
- **C.** The TTS voice is too quiet.
  - *Explanation:* Incorrect. A quiet voice would produce "Sorry, can you speak up?", not "Hello?" before the agent has spoken at all.
- **D.** The LLM prompt is too short.
  - *Explanation:* Incorrect. A short prompt tends to make responses faster, not slower. Prompt length is not what makes callers fill a silence.

**Correct answer: A**

---

### Q7. Riley recognises speech almost perfectly when you test in the browser, but on real phone calls she keeps mishearing names and numbers. What is the most likely technical reason?

*Related lecture: 1.2 What a voice agent actually is (preview of 8.1)*

- **A.** Phone callers speak faster than browser users.
  - *Explanation:* Incorrect. Speaking rate varies by person, not by channel. The channel itself changes the audio.
- **B.** The LLM treats phone calls differently from browser sessions.
  - *Explanation:* Incorrect. The LLM only sees text. If the text is wrong, the error happened earlier, in speech recognition.
- **C.** The TTS engine cannot play audio over SIP.
  - *Explanation:* Incorrect. TTS affects what the caller hears, not what Riley hears. This question is about recognition errors.
- **D.** Phone audio is narrowband (typically 8 kHz, compressed), so STT gets less acoustic detail than from a browser's wideband audio, and needs a telephony-suited model and testing on phone audio.
  - *Explanation:* Correct. The PSTN carries narrowband, compressed audio plus line noise. Recognition accuracy drops, especially for names and digits, which is why Section 8 tunes STT for telephony and Section 9 measures WER on phone-quality recordings.

**Correct answer: D**

---

### Q8. You have just cloned the course repo, have no API keys yet, and want to confirm the business logic works. Which command should you run?

*Related lecture: 1.5 Course roadmap, repo tour and how to get help*

- **A.** `make console`
  - *Explanation:* Incorrect. Console mode starts a live voice agent, which needs LiveKit credentials and model access.
- **B.** `make test`
  - *Explanation:* Correct. `make test` runs the offline unit tests in `tests/unit/` for the pure-Python modules in `src/maple/` (scheduler, knowledge, PII, costs, latency, WER, config). They need no network and no keys.
- **C.** `make test-agent`
  - *Explanation:* Incorrect. Agent behaviour tests run real LLM sessions and need `OPENAI_API_KEY`. They auto-skip without it, so they would not tell you much.
- **D.** `make eval`
  - *Explanation:* Incorrect. Evals use LLM judges and simulated callers, which need API keys and cost money.

**Correct answer: B**
