# Quiz: Choosing a Stack (Section 14)

| Field | Value |
|---|---|
| Udemy lecture | 14.4 Quiz: Choosing a stack |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 14.1 to 14.3 |

---

### Q1. In Pipecat, you want to redact phone numbers from the caller's words before they are added to the LLM context. Where does a custom `FrameProcessor` belong in the pipeline?

*Related lecture: 14.1 Pipecat's frame pipeline model*

- **A.** After `transport.output()`, at the end of the pipeline.
  - *Explanation:* Incorrect. By then the caller's text has already reached the LLM and the reply has been spoken.
- **B.** Between the STT service and the user context aggregator, so it can rewrite transcription frames before they reach the context.
  - *Explanation:* Correct. Frames flow in order through processors. Placing the redactor right after STT means every later processor, including the context aggregator and the LLM, only sees redacted text.
- **C.** Between the TTS service and the transport output.
  - *Explanation:* Incorrect. That position sees audio for the caller, not the caller's transcribed words.
- **D.** In a separate pipeline that runs after the call.
  - *Explanation:* Incorrect. Post-call processing cannot stop PII from entering the live LLM context.

**Correct answer: B**

---

### Q2. What are the roles of `Pipeline`, `PipelineWorker` and `WorkerRunner` in Pipecat 1.12?

*Related lecture: 14.1 Pipecat's frame pipeline model*

- **A.** They are three names for the same class, kept for backwards compatibility.
  - *Explanation:* Incorrect. They are distinct objects with different responsibilities.
- **B.** `Pipeline` is for audio, `PipelineWorker` for text, and `WorkerRunner` for tools.
  - *Explanation:* Incorrect. The split is not by modality. All frame types flow through the same pipeline.
- **C.** `Pipeline` is the ordered list of processors, `PipelineWorker` runs one conversation through it with run-time parameters (`PipelineParams`) and lets you queue frames, and `WorkerRunner` manages the worker's lifecycle such as signals and cleanup.
  - *Explanation:* Correct. You build the processor chain, wrap it in a worker with parameters, and hand the worker to a runner (`await runner.add_workers(worker)` in `pipecat/s14_pipecat_bot.py`). Older tutorials call the last two `PipelineTask` and `PipelineRunner`; those names are deprecated aliases since Pipecat 1.3 and print warnings in 1.12.
- **D.** `WorkerRunner` defines processors, and `Pipeline` executes them.
  - *Explanation:* Incorrect. The roles are the other way round.

**Correct answer: C**

---

### Q3. A blog tutorial's Pipecat code does `from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext`, and it fails with `ModuleNotFoundError` on Pipecat 1.12. What is the correct modern approach?

*Related lecture: 14.2 Code-along: Riley booking flow in Pipecat*

- **A.** Pin Pipecat to an old version so the tutorial works.
  - *Explanation:* Incorrect. You would lose years of fixes and fight other incompatibilities. Update the code instead.
- **B.** Copy the old module into your project.
  - *Explanation:* Incorrect. Vendoring removed internals creates a maintenance trap and may not work with the current services.
- **C.** Pass the messages list directly to `OpenAILLMService` without a context.
  - *Explanation:* Incorrect. The context and aggregators are what keep the conversation history consistent; skipping them breaks multi-turn conversations.
- **D.** Use `LLMContext` from `pipecat.processors.aggregators.llm_context` with the universal aggregators from `pipecat.processors.aggregators.llm_response_universal`.
  - *Explanation:* Correct. The provider-specific `openai_llm_context` module was removed. The universal `LLMContext` works across LLM services, which is what `pipecat/s14_pipecat_bot.py` uses.

**Correct answer: D**

---

### Q4. How does the Pipecat version of Riley describe the `book_appointment` tool to the LLM?

*Related lecture: 14.2 Code-along: Riley booking flow in Pipecat*

- **A.** With a `FunctionSchema` (name, description, properties, required fields) from `pipecat.adapters.schemas.function_schema`, collected into a tools schema on the context, plus a handler registered on the LLM service.
  - *Explanation:* Correct. Pipecat separates the provider-neutral schema from the handler function. The handler calls the same `maple.scheduler` code as the LiveKit version.
- **B.** With LiveKit's `@function_tool` decorator, which Pipecat also reads.
  - *Explanation:* Incorrect. `@function_tool` is a LiveKit Agents API. Pipecat has its own schema objects.
- **C.** By pasting the JSON schema into the system prompt.
  - *Explanation:* Incorrect. Tools are passed through the LLM API's function-calling interface, not as prompt text.
- **D.** Pipecat does not support function calling.
  - *Explanation:* Incorrect. Pipecat supports function calling across its LLM services.

**Correct answer: A**

---

### Q5. A two-dentist practice with no developers wants a phone receptionist running within a week, with standard booking through their existing calendar. Which option is usually the best fit?

*Related lecture: 14.3 LiveKit Agents vs Pipecat vs managed platforms*

- **A.** Build a custom LiveKit Agents stack with a full test pyramid.
  - *Explanation:* Incorrect. It is excellent for control and scale, but without developers the practice cannot build or maintain it in a week.
- **B.** A managed voice-agent platform (such as Vapi, Retell, ElevenLabs Agents or Bland) with a built-in calendar integration, after checking its compliance terms and per-minute pricing.
  - *Explanation:* Correct. Managed platforms trade control and per-minute cost for speed and no infrastructure, which fits a small team with a standard use case. Checking data handling and contract terms is still essential for a healthcare business.
- **C.** Build a Pipecat pipeline from scratch.
  - *Explanation:* Incorrect. Same problem as option A: it needs engineering capacity the practice does not have.
- **D.** Keep the press-1 IVR forever.
  - *Explanation:* Incorrect. That ignores the stated goal, and a managed option can meet it.

**Correct answer: B**

---

### Q6. A hospital group requires that call audio and transcripts stay in its own cloud account, wants to swap STT and LLM vendors as contracts change, and has a platform engineering team. Which choice fits best?

*Related lecture: 14.3 LiveKit Agents vs Pipecat vs managed platforms*

- **A.** A managed platform with default settings, because it is fastest.
  - *Explanation:* Incorrect. Speed matters less here than data residency and vendor flexibility, which default managed setups may not provide.
- **B.** Whichever option has the cheapest per-minute price this month.
  - *Explanation:* Incorrect. Price changes over time, and these requirements are about control and compliance.
- **C.** A no-code chatbot builder with a phone add-on.
  - *Explanation:* Incorrect. It gives even less control over data location and components.
- **D.** An open-source framework (LiveKit Agents or Pipecat), self-hosted or deployed into their own cloud, with providers chosen per contract.
  - *Explanation:* Correct. Open-source frameworks give full control over where data flows and which providers are used, and the group has the team to run it. Lock-in is lowest when every component is replaceable.

**Correct answer: D**
