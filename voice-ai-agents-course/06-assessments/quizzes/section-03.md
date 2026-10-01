# Quiz: First Agent and Turn-Taking (Section 3)

| Field | Value |
|---|---|
| Udemy lecture | 3.10 Quiz: First agent and turn-taking |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 3.1, 3.2, 3.5, 3.6, 3.9 |

---

### Q1. You run `uv run agents/s03_hello_agent.py dev` and then join a room from the Agents Playground. Riley appears in the room a moment later. What actually made Riley join?

*Related lecture: 3.1 LiveKit mental model: rooms, participants, tracks, dispatch*

- **A.** The Playground downloaded the agent code and ran it in your browser.
  - *Explanation:* Incorrect. The agent always runs in your Python process (or your deployed container), never in the browser.
- **B.** Your agent server registered with LiveKit when it started; when the room was created, LiveKit dispatched a job to it, and the server ran your `@server.rtc_session()` entrypoint for that room.
  - *Explanation:* Correct. The agent server holds a connection to LiveKit and waits for jobs. Dispatch assigns a room to it, and the entrypoint joins that room as a participant. That is why no inbound port is needed on your laptop.
- **C.** The Playground called your laptop's IP address on port 8081.
  - *Explanation:* Incorrect. LiveKit never connects in to your machine. Your agent server connects out to LiveKit.
- **D.** Every agent on your LiveKit project joins every room automatically, regardless of dispatch settings.
  - *Explanation:* Incorrect. Automatic dispatch only applies to agents without an agent name. Named agents (such as the telephony agent in Section 8) are dispatched explicitly or by a dispatch rule.

**Correct answer: B**

---

### Q2. You want to give Riley a new tool and a stricter system prompt, and separately switch the whole call to a faster STT model. Where does each change belong?

*Related lecture: 3.2 AgentSession and Agent: the two core classes*

- **A.** Both belong on the `Agent`.
  - *Explanation:* Incorrect. The `Agent` holds instructions and tools (and optional per-agent overrides), but the call's default STT, LLM, TTS, VAD and turn handling live on the `AgentSession`.
- **B.** Both belong on the `AgentSession`.
  - *Explanation:* Incorrect. Instructions and tools are defined on the `Agent`, so that each agent in a handoff (Section 7) can have its own.
- **C.** Tool and prompt on the `Agent`; STT on the `AgentSession`.
  - *Explanation:* Correct. `Agent` = who Riley is and what it can do (instructions, `@function_tool` methods). `AgentSession` = the runtime for the call (`stt`, `llm`, `tts`, `vad`, `turn_handling`, `userdata`).
- **D.** Tool and prompt in `.env`; STT on the `Agent`.
  - *Explanation:* Incorrect. `.env` holds configuration such as model names, not tools or prompts, and STT is a session-level setting.

**Correct answer: C**

---

### Q3. Your `.env` has `STT_MODEL=deepgram/nova-3` and `MAPLE_PROVIDER_MODE=inference`, but no `DEEPGRAM_API_KEY`. Speech recognition works anyway. Why?

*Related lecture: 3.5 Choosing STT, LLM and TTS providers*

- **A.** Deepgram offers anonymous access for low volumes.
  - *Explanation:* Incorrect. Direct Deepgram API calls require an API key.
- **B.** The agent silently fell back to Whisper running locally.
  - *Explanation:* Incorrect. Nothing in the course code falls back to a local model; you would see an error instead.
- **C.** Console mode uses your operating system's dictation feature.
  - *Explanation:* Incorrect. Console mode only uses your local microphone and speakers; recognition still goes through the configured STT.
- **D.** Provider/model strings such as `deepgram/nova-3` are served by LiveKit Inference and billed to your LiveKit Cloud project, so only your LiveKit credentials are needed. Direct plugins (`MAPLE_PROVIDER_MODE=plugins`) need the provider's own key.
  - *Explanation:* Correct. LiveKit Inference proxies the model for you. Switching to plugins gives you direct provider features and billing, and then `DEEPGRAM_API_KEY` is required.

**Correct answer: D**

---

### Q4. On test calls, Riley stops mid-sentence whenever the caller says "mm-hmm" or coughs, then sounds confused. Which change targets this problem most directly?

*Related lecture: 3.6 VAD, turn detection and interruptions*

- **A.** Require more evidence before treating speech as an interruption, for example `InterruptionOptions(min_duration=0.5, min_words=2)`, and keep false-interruption resume enabled so Riley continues if the "interruption" turns out to be noise.
  - *Explanation:* Correct. Backchannels and coughs are short. Requiring a minimum duration or number of recognised words filters them out, and resuming after a false interruption recovers gracefully when one slips through. The course's `build_turn_handling()` enables resume with a short timeout.
- **B.** Lower `MIN_ENDPOINTING_DELAY` to 0.2 seconds.
  - *Explanation:* Incorrect. Endpointing controls when the caller's turn ends, not whether Riley's speech gets interrupted. A shorter delay would make Riley cut callers off more often.
- **C.** Disable interruptions entirely.
  - *Explanation:* Incorrect. Then Riley talks over callers who genuinely want to interject ("no, Thursday!"), which is one of the "break it" failures from lecture 3.9.
- **D.** Switch to a faster LLM.
  - *Explanation:* Incorrect. The LLM is not involved in deciding whether audio counts as an interruption.

**Correct answer: A**

---

### Q5. After a tuning session, Riley waits two to three seconds after every caller sentence, even short, obviously finished ones like "Yes, that works." What is the most likely misconfiguration?

*Related lecture: 3.9 Break it: five ways your first agent fails*

- **A.** The TTS voice is too slow.
  - *Explanation:* Incorrect. A slow speaking rate makes Riley's speech longer, not the silence before it starts.
- **B.** The minimum endpointing delay was set far too high (for example `MIN_ENDPOINTING_DELAY=2.5`), so Riley waits that long even when the turn detector is confident the caller is done.
  - *Explanation:* Correct. The minimum delay is a floor applied to every turn. Setting it high removes cut-offs but produces the "awkward silence" failure. Keep it near 0.5 s and let the semantic turn detector extend the wait (up to the maximum) only when a sentence sounds unfinished.
- **C.** Silero VAD is not loaded.
  - *Explanation:* Incorrect. Without VAD the pipeline would fail to detect speech properly or error at start-up; it would not produce a consistent two-second pause.
- **D.** Interruptions are disabled.
  - *Explanation:* Incorrect. That makes Riley talk over callers, not wait longer before speaking.

**Correct answer: B**
