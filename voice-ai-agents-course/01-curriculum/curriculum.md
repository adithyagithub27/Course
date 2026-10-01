# Curriculum: Production Voice AI Agents with Python

> **Source of truth.** Every lecture script, lab, quiz, code file and Udemy listing field must match the section numbers, lecture IDs, file names and running example defined here.
>
> **Verified stack (checked against installed packages on 2026-09-28):** Python 3.11+, `livekit-agents` 1.8.x, `pipecat-ai` 1.12.x, `deepeval`, `jiwer`, `pytest-asyncio`.

---

## 1. Course at a Glance

| Field | Value |
|---|---|
| Working title | Production Voice AI Agents with Python: Build, Test, Deploy |
| Runtime | ~11.4 hours of video (683 min in the 89 video lectures, 689 min with the 5.9 challenge) across 15 sections, 97 lectures; 763 min including lab, assignment and quiz slots (v1.1, durations synced with the scripts 2026-10-01) |
| Level | Intermediate (basic Python + basic async/await). Section 1-3 are beginner-safe. |
| Running example | **"Riley", the AI receptionist for Maple Street Dental** (fictional clinic). Riley answers questions, books/reschedules/cancels appointments, transfers to a human, and runs on a real phone number. |
| Primary framework | LiveKit Agents 1.8 (`AgentServer`, `AgentSession`, `Agent`, `@function_tool`) |
| Secondary framework | Pipecat 1.12 (Section 14 comparison build) |
| Models (default) | STT `deepgram/nova-3`, LLM `openai/gpt-4.1-mini`, TTS `cartesia/sonic-3`, VAD Silero, turn detection `inference.TurnDetector()`; speech-to-speech `openai.realtime.RealtimeModel(model="gpt-realtime")` |
| Model config | All model strings come from environment variables in `src/maple/config.py` so students can swap providers and survive model renames |
| Testing stack | LiveKit test framework (`session.run`, `result.expect`, `.judge()`), `mock_tools`, DeepEval conversational metrics, `jiwer` WER, custom latency harness, simulated callers |
| Observability | `metrics_collected` events, `session.usage` and per-turn `ChatMessage.metrics`, OpenTelemetry + Langfuse |
| Deploy | Docker, LiveKit Cloud agents, alternative self-host on any container host; GitHub Actions CI |
| Telephony | LiveKit SIP + Twilio Elastic SIP trunk: inbound, outbound, transfer to human |
| Student API cost | ~$10-20 total using free tiers (LiveKit Cloud free tier, Deepgram and Cartesia starter credits, OpenAI pay-as-you-go, Twilio trial) |
| Relationship to other courses | Sequel to *Generative AI & AI Agents: Zero to Production* (build) and *AI Agent Testing & Evaluation* (test). Standalone: no prior course required. |

### Learning outcomes (Udemy "What you'll learn")

1. Build real-time voice AI agents in Python with LiveKit Agents: STT, LLM, TTS, VAD and turn detection wired into one low-latency pipeline.
2. Choose between cascaded (STT→LLM→TTS) and speech-to-speech (OpenAI Realtime) architectures using latency, cost and quality data.
3. Write system prompts designed for the ear: brevity, pacing, read-backs, numbers, dates and pronunciation.
4. Give voice agents tools to book, reschedule and cancel appointments, with confirmation patterns and filler speech while tools run.
5. Add a spoken FAQ knowledge base (RAG for voice) and multi-agent handoffs between specialist agents.
6. Put an agent on a real phone number with SIP: inbound calls, outbound calls and warm transfer to a human.
7. Test voice agents like software: behavior tests, LLM-as-judge, tool-call assertions, WER, latency budgets and simulated callers in CI.
8. Monitor latency, token usage and cost per minute with metrics, OpenTelemetry and Langfuse.
9. Secure voice agents against prompt injection, PII leakage and unsafe tool use, with escalation to humans.
10. Deploy to production with Docker and LiveKit Cloud, and compare the build with Pipecat and managed platforms.

---

## 2. Code Repository Layout (student repo: `voice-agents-course`)

Lives in `voice-ai-agents-course/03-code/`. Lecture scripts and labs must reference these exact paths.

```
03-code/
├── README.md                     # setup, run commands, lecture→file map
├── pyproject.toml                # uv/pip project, pinned majors
├── uv.lock                       # locked dependency versions (`uv sync --locked`, lecture 12.2)
├── .env.example                  # LIVEKIT_*, OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY, model env vars
├── Makefile                      # make install | console | dev | test | test-agent | eval | lint
├── livekit.toml.example          # agent name for deploy / telephony dispatch
├── (telephony/)                  # NOT shipped: students create inbound-trunk.json and dispatch-rule.json in 8.2, outbound-trunk.json in 8.5
├── src/maple/                    # pure-Python business logic (no network, fully unit-tested)
│   ├── config.py                 # reads STT_MODEL, LLM_MODEL, TTS_MODEL, REALTIME_MODEL etc. with defaults
│   ├── prompts.py                # Riley's voice-first instructions, reusable prompt blocks
│   ├── scheduler.py              # in-memory clinic calendar: find_slots, book, reschedule, cancel
│   ├── knowledge.py              # tiny FAQ retriever over data/faq.md (keyword + BM25-lite, no deps)
│   ├── pii.py                    # redact phone, email, DOB, card numbers from transcripts
│   ├── costs.py                  # cost-per-minute calculator from usage summaries + price table
│   ├── latency.py                # latency budget, p50/p90/p95 stats, budget violations
│   ├── wer.py                    # word error rate (pure Python, cross-checked against jiwer)
│   └── data/faq.md               # Maple Street Dental FAQ (hours, insurance, parking, services, policies)
├── agents/
│   ├── common.py                 # shared session builder, CallState, tool mixins (booking, knowledge, telephony, verification)
│   ├── s03_hello_agent.py        # first cascaded agent (console + playground)
│   ├── s04_voice_prompting.py    # voice-first prompt, greeting, silence handling
│   ├── s05_booking_agent.py      # @function_tool booking/reschedule/cancel, read-backs, filler speech
│   ├── s06_realtime_agent.py     # OpenAI Realtime speech-to-speech version of Riley
│   ├── s07_knowledge_agent.py    # FAQ lookup tool (RAG for voice)
│   ├── s07_multi_agent.py        # Greeter → Booking → Billing handoffs with shared userdata
│   ├── s08_telephony_agent.py    # phone-ready agent, transfer_to_human tool, end_call
│   ├── s08_outbound_call.py      # script: dispatch agent + create outbound SIP participant (reminder calls)
│   ├── s10_observed_agent.py     # metrics_collected, session.usage, OTel/Langfuse, cost per minute
│   ├── s11_guarded_agent.py      # injection-resistant prompt, PII redaction, tool permissions, escalation
│   ├── s12_chaos_demo.py         # recording helper for 12.8: kill switch for the primary LLM
│   └── s13_capstone_receptionist.py  # full production Riley: all features combined
├── pipecat/
│   └── s14_pipecat_bot.py        # same Riley booking flow in Pipecat 1.12
├── tests/
│   ├── unit/                     # offline, no keys: scheduler, knowledge, pii, costs, latency, wer, config
│   ├── agent/                    # LiveKit behavior tests (need OPENAI_API_KEY; auto-skip otherwise)
│   │   ├── test_greeting.py
│   │   ├── test_booking_flows.py
│   │   ├── test_safety.py
│   │   ├── test_capstone.py      # capstone acceptance tests (13.4)
│   │   └── test_mock_mode.py     # offline MOCK_MODE checks
│   ├── evals/
│   │   ├── test_conversation_quality.py   # DeepEval conversational G-Eval on golden transcripts
│   │   ├── stt_wer_eval.py                 # WER report against reference transcripts
│   │   ├── latency_report.py               # summarises exported metrics JSONL vs budget
│   │   ├── audio_in_eval.py                # recorded caller WAVs through STT + WER (9.13)
│   │   └── simulated_caller.py             # LLM caller personas vs Riley over text sessions
│   └── data/
│       ├── golden_conversations.json
│       ├── stt_references.json
│       ├── sample_metrics.jsonl
│       └── audio/                          # your own caller WAVs for 9.13 (none ship, by design)
├── deploy/
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/README.md            # how to use the LiveKit React agent starter against Riley
└── .github/workflows/ci.yml      # unit tests always; agent tests + evals when secrets present
```

---

## 3. Section-by-Section Curriculum

Lecture types: **TH** talking head/avatar, **SL** slides, **SC** screencast/code-along, **DM** live demo, **LAB** guided lab (text + video walkthrough), **QZ** quiz, **AS** assignment, **CE** coding challenge (spec, pause, solution walkthrough).

The **Min** column is the lecture's slot. For TH, SL, SC, DM and CE it is the video length. For LAB, AS and QZ it is the slot in the section total; the video part is a short intro (length in each script's header) and the hands-on time is in the lab or project file header, which is the source of truth for every time estimate students hear (decision V3).

### Section 1: Welcome and How Voice Agents Work (≈38 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 1.1 | Meet Riley: one call that works, one that fails, one that's fixed | DM | 5 | Hook by contrast. Call 1: Riley books an appointment and transfers. Call 2: a naive agent talks over the caller, mishears the date and hallucinates availability. Call 3: the fixed agent passing its test suite. Promise: by Section 13 yours does call 1 and passes call 3's tests. | Capstone demo recording, failure recording |
| 1.2 | What a voice agent actually is | SL | 7 | Voice agent vs IVR vs chatbot. Components: transport (WebRTC/SIP), VAD, STT, turn detection, LLM, tools, TTS. Where each fails. | Diagram: voice pipeline |
| 1.3 | Cascaded vs speech-to-speech architectures | SL | 8 | STT→LLM→TTS pipeline vs realtime S2S (OpenAI Realtime). Trade-offs: control, cost, latency, voice quality, tool reliability. Half-cascade hybrid. | Comparison table |
| 1.4 | The latency budget: why 800 ms is the magic number | SL | 8 | Human turn gap ≈200-300 ms. Budget: endpointing, STT final, LLM TTFT, TTS TTFB, network. Target <1 s voice-to-voice. Preview of how we'll measure it in S9/S10. | `10-resources/latency-budget-worksheet.md` |
| 1.5 | Course roadmap, repo tour and how to get help | SC | 6 | Walk the 15 sections, the `voice-agents-course` repo, Makefile, Q&A etiquette, how to use labs. | `03-code/README.md` |
| 1.6 | Quiz: Voice agent fundamentals | QZ | 4 | 8 questions | `06-assessments/quizzes/section-01.md` |

### Section 2: Setup: Accounts, Keys and Your Dev Environment (≈44 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 2.1 | Accounts you need and what they cost | SC | 8 | LiveKit Cloud (free tier), OpenAI, Deepgram, Cartesia, optional ElevenLabs, Twilio trial. LiveKit Inference model strings vs direct provider plugins. Student budget ≈$10-20. | `10-resources/provider-cost-guide.md` |
| 2.2 | Python project setup with uv | SC | 8 | Clone repo, `uv sync` (pip fallback), `.env` from `.env.example`, `make install`, `python agents/s03_hello_agent.py download-files`. | `pyproject.toml`, `.env.example` |
| 2.3 | LiveKit CLI, projects and credentials | SC | 7 | Install `lk` CLI, `lk cloud auth`, create project, `lk app env` to write credentials, verify with `lk room list`. | |
| 2.4 | Smoke test: unit tests and console mode | SC | 6 | `make test` (offline unit tests pass), `uv run agents/s03_hello_agent.py console` talks through your laptop mic. Troubleshooting mic permissions and keys. | `tests/unit/` |
| 2.5 | Lab 1: Environment verification | LAB | 3 | Checklist lab. Video intro; hands-on time about 45 minutes (lab header). | `04-labs/lab-01-environment.md` |
| 2.6 | Quick win: run the finished Riley before you build it | SC | 6 | `make console AGENT=agents/s13_capstone_receptionist.py`: talk to the capstone agent, book an appointment, trigger a transfer. Students hear the destination before the journey. | `agents/s13_capstone_receptionist.py` |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | 6 | Set hard spending limits on OpenAI, Deepgram, Cartesia; LiveKit free-tier minutes; `MOCK_MODE=1` runs Riley with a scripted fake LLM and text I/O for zero-cost practice; how to estimate a lab's cost before running it. | `src/maple/config.py`, `agents/common.py`, `10-resources/provider-cost-guide.md` |

### Section 3: Your First Voice Agent with LiveKit Agents (≈66 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 3.1 | LiveKit mental model: rooms, participants, tracks, dispatch | SL | 8 | SFU, rooms, participants, audio tracks, agent server registers with LiveKit and gets dispatched into rooms. `AgentServer` + `@server.rtc_session()` entrypoint. | Diagram |
| 3.2 | AgentSession and Agent: the two core classes | SL | 7 | `Agent` = instructions + tools + per-agent model overrides. `AgentSession` = the runtime (stt, llm, tts, vad, turn_handling, userdata). `session.start(agent=..., room=ctx.room)`. | |
| 3.3 | Code-along: hello Riley in 30 lines | SC | 10 | Build `s03_hello_agent.py`: `AgentServer()`, entrypoint, `AgentSession(stt=..., llm=..., tts=..., vad=silero.VAD.load(), turn_handling=TurnHandlingOptions(turn_detection=inference.TurnDetector()))`, `session.generate_reply(instructions="Greet the caller")`, `cli.run_app(server)`. Run `console`. | `agents/s03_hello_agent.py` |
| 3.4 | Dev mode and the Agents Playground | DM | 6 | `dev` command, hot reload, connect from the LiveKit Agents Playground / web starter, watch transcripts. | |
| 3.5 | Choosing STT, LLM and TTS providers | SL | 8 | LiveKit Inference strings (`deepgram/nova-3`, `openai/gpt-4.1-mini`, `cartesia/sonic-3`) vs plugins (`openai.LLM(...)`). Accuracy, latency, price, voices, languages. Config via `src/maple/config.py`. | `src/maple/config.py` |
| 3.6 | VAD, turn detection and interruptions | SL | 8 | Silero VAD params, endpointing (`EndpointingOptions` min/max delay, fixed vs dynamic), semantic turn detector, interruption options (`min_duration`, `min_words`, false-interruption resume), preemptive generation. | Diagram: turn-taking timeline |
| 3.7 | Tuning turn-taking live | DM | 5 | Change endpointing and interruption settings, hear the difference. Common tuning mistakes. | |
| 3.8 | Lab 2: Customise your first agent | LAB | 4 | Swap voice, model and turn settings; record observations. Hands-on time about 60 minutes (lab header). | `04-labs/lab-02-first-agent.md` |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | 7 | Before/after audio for: (1) endpointing too short, caller cut off; (2) too long, awkward silence; (3) interruptions disabled, agent talks over caller; (4) TTS reading markdown symbols aloud; (5) STT model mismatch on accents and phone audio. Each paired with the one setting that fixes it. | `agents/s03_hello_agent.py` with `BROKEN=<case>` env toggles |
| 3.10 | Quiz: First agent and turn-taking | QZ | 3 | 5 questions | `06-assessments/quizzes/section-03.md` |

### Section 4: Prompting for the Ear (≈45 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 4.1 | Why chat prompts fail on voice | SL | 7 | Markdown, lists, long answers, URLs, emojis all break TTS. Latency grows with output length. | |
| 4.2 | Anatomy of a voice system prompt | SL | 8 | Identity, goal, style (1-2 sentences, one question at a time), output rules (no markdown, spell out numbers), tools policy, guardrails, escalation. | `src/maple/prompts.py` |
| 4.3 | Numbers, dates, names and pronunciation | SC | 8 | Phone numbers in groups, dates as words, confirm spellings, TTS text transforms, pronunciation hints. | `agents/s04_voice_prompting.py` |
| 4.4 | Greetings, silence and "are you still there?" | SC | 7 | `on_enter` greeting, `user_away_timeout`, user state events, graceful hang-up after repeated silence. | `agents/s04_voice_prompting.py` |
| 4.5 | Persona and brand voice without the cringe | TH | 5 | Warmth vs efficiency, disclosure that it's an AI, consistency. | |
| 4.6 | Lab 3: Rewrite a chat prompt for voice | LAB | 5 | Before/after exercise with rubric. Hands-on time about 45 minutes (lab header). | `04-labs/lab-03-voice-prompting.md` |
| 4.7 | Challenge: Riley for your business | AS | 3 | Students rewrite Riley's instructions for a business they know (salon, restaurant, clinic, law office) using `business-template.md`, run it in console, and post one transcript in Q&A. First portfolio artefact. | `10-resources/business-template.md` |
| 4.8 | Quiz: Prompting for the ear | QZ | 2 | 5 questions | `06-assessments/quizzes/section-04.md` |

### Section 5: Tools: Booking, Rescheduling and Cancelling (≈70 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 5.1 | How function tools work in LiveKit | SL | 7 | `@function_tool` on Agent methods, docstrings become descriptions, typed args, `RunContext`, `max_tool_steps`, returning strings/dicts, `ToolError`. | |
| 5.2 | The clinic scheduler: pure Python first | SC | 8 | Walk `src/maple/scheduler.py` and its unit tests. Why business logic lives outside the agent. | `src/maple/scheduler.py`, `tests/unit/test_scheduler.py` |
| 5.3 | Code-along: check availability and book | SC | 12 | `find_available_slots`, `book_appointment` tools; slot filling (name, phone, reason, time). | `agents/s05_booking_agent.py` |
| 5.4 | Confirmation and read-back patterns | SC | 8 | Read back date/time/name before committing; handling "no, Thursday". | same |
| 5.5 | Hiding latency while tools run | SC | 7 | `context.with_filler("One moment while I check the schedule.", delay=...)`, `session.say`, disallowing interruptions during commits. | same |
| 5.6 | Reschedule, cancel and tool errors | SC | 9 | `reschedule_appointment`, `cancel_appointment`, raising `ToolError` with speakable messages, retry prompts. | same |
| 5.7 | Session state with userdata | SC | 6 | Typed `@dataclass` userdata on `AgentSession`, `context.userdata`, carrying caller details across tools. | same |
| 5.8 | Project 1: Booking agent | AS | 5 | Build and demo the booking flow. | `05-projects/project-1-booking-agent.md` |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | 6 | Spec given on screen: `join_waitlist(patient_name, phone, preferred_day)` backed by `scheduler.add_to_waitlist` and `scheduler.waitlist_position`. Student pauses and builds it. Then the solution walkthrough covers the three mistakes most people make (tool description too vague, no read-back, forgetting ToolError). | `agents/s05_booking_agent.py`, `src/maple/scheduler.py` |
| 5.10 | Quiz: Tools | QZ | 2 | 5 questions | `06-assessments/quizzes/section-05.md` |

### Section 6: Speech-to-Speech with OpenAI Realtime (≈42 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 6.1 | How realtime speech models work | SL | 8 | Audio in/audio out, server VAD, voices, transcription side channel, session limits. | |
| 6.2 | Code-along: Riley on `gpt-realtime` | SC | 10 | `AgentSession(llm=openai.realtime.RealtimeModel(model=..., voice="marin"))`, same tools reused, turn detection options. | `agents/s06_realtime_agent.py` |
| 6.3 | Hybrid: realtime LLM with your own TTS | SC | 7 | `modalities=["text"]` + separate TTS for voice control and brand consistency. | same |
| 6.4 | Head-to-head: cascaded vs realtime | DM | 10 | Same 5 test calls, played side by side so students hear the difference, not just read numbers; compare latency, cost/minute, tool accuracy, interruptions. Decision matrix. | `10-resources/architecture-decision-matrix.md` |
| 6.5 | Lab 4: Measure both architectures | LAB | 5 | Fill the comparison sheet. Hands-on time about 75 minutes (lab header). | `04-labs/lab-04-realtime-vs-cascaded.md` |
| 6.6 | Quiz: Architectures and tools | QZ | 2 | 8 questions | `06-assessments/quizzes/section-06.md` |

### Section 7: Knowledge and Multi-Agent Handoffs (≈56 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 7.1 | RAG for voice: short, speakable, grounded | SL | 7 | Retrieval as a tool vs pre-turn injection (`on_user_turn_completed`), answer length, "I don't know" behavior. | |
| 7.2 | Code-along: FAQ lookup tool | SC | 10 | `src/maple/knowledge.py` retriever + `lookup_clinic_info` tool; grounding instructions. | `agents/s07_knowledge_agent.py` |
| 7.3 | Scaling knowledge: vector stores and latency | SL | 6 | When to use a vector DB, embedding latency, caching, pre-fetch on turn completion. | |
| 7.4 | Why split one agent into several | SL | 6 | Prompt size, tool confusion, specialist personas. Handoff vs single agent trade-offs. | |
| 7.5 | Code-along: Greeter → Booking → Billing | SC | 12 | Tools that return another `Agent` to hand off, shared userdata, `on_enter` per agent, chat context carry-over. | `agents/s07_multi_agent.py` |
| 7.6 | Lab 5: Add an Insurance agent | LAB | 5 | Extend the handoff graph. Hands-on time about 60 minutes (lab header). | `04-labs/lab-05-handoffs.md` |
| 7.7 | Quiz: Knowledge and handoffs | QZ | 2 | 6 questions | `06-assessments/quizzes/section-07.md` |
| 7.8 | Multilingual Riley: Spanish and Hindi callers | SC | 8 | STT language settings and multilingual models, the multilingual turn detector, per-language TTS voices, detecting and switching language mid-call, translating the FAQ answers, what to test differently. | `agents/s07_knowledge_agent.py` (`LANGUAGE` env; `follow_caller_language()` behind `FOLLOW_CALLER_LANGUAGE=1`), `src/maple/config.py` |

### Section 8: Telephony: Put Riley on a Phone Number (≈57 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 8.1 | PSTN, SIP and trunks in plain English | SL | 8 | Phone network → SIP trunk (Twilio) → LiveKit SIP → room → agent. Codecs, 8 kHz audio and why STT choice matters on phones. | Diagram |
| 8.2 | Inbound calls: Twilio trunk + LiveKit dispatch rule | SC | 12 | Buy number, create Elastic SIP trunk, LiveKit inbound trunk + dispatch rule with `lk` CLI, agent name via `livekit.toml`/`LIVEKIT_AGENT_NAME`. | `livekit.toml.example`, `agents/s08_telephony_agent.py` |
| 8.3 | Phone-specific tuning | SC | 7 | Telephony-tuned STT, noise, longer endpointing, caller ID from SIP participant attributes. | same |
| 8.4 | Transfer to a human and ending calls | SC | 9 | `transfer_to_human` tool using `get_job_context().transfer_sip_participant(...)`, warm vs cold transfer, `end_call` tool. | same |
| 8.5 | Outbound calls: appointment reminders | SC | 10 | Explicit dispatch + `CreateSIPParticipant` via the LiveKit API; answering-machine considerations. | `agents/s08_outbound_call.py` |
| 8.6 | Compliance: disclosure, consent and recording | TH | 6 | AI disclosure, call-recording consent (one/two-party), TCPA for outbound, do-not-call, data retention. Not legal advice. | `10-resources/telephony-compliance-checklist.md` |
| 8.7 | Project 2: Phone receptionist | AS | 3 | Inbound number that books and transfers. Includes a "no phone number" path (web client + SIP test) for students who cannot get a Twilio number in their country. | `05-projects/project-2-phone-receptionist.md` |
| 8.8 | Quiz: Telephony | QZ | 2 | 5 questions | `06-assessments/quizzes/section-08.md` |

### Section 9: Testing and Evaluating Voice Agents (≈88 min) — signature section

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 9.1 | How voice agents fail in production | SL | 8 | Failure taxonomy: mishearing, wrong turn-taking, talking over callers, hallucinated availability, wrong tool args, missed escalation, latency spikes, prompt injection. Map each to a test type. | `10-resources/voice-failure-taxonomy.md` |
| 9.2 | The voice testing pyramid | SL | 6 | Unit (pure logic) → behavior (text sessions) → evals (LLM judges, WER) → simulated calls → production monitoring. | Diagram |
| 9.3 | Behavior tests with LiveKit's test framework | SC | 12 | `async with AgentSession(llm=...) as session: await session.start(RileyAgent()); result = await session.run(user_input="...")`, `await result.expect.next_event().is_message(role="assistant").judge(judge_llm, intent="...")`, `pytest-asyncio`. | `tests/agent/test_greeting.py` |
| 9.4 | Asserting tool calls and arguments | SC | 10 | `result.expect.next_event().is_function_call(name="book_appointment", arguments={...})`, `is_function_call_output`, `skip_next_event_if`, `contains_function_call`, `no_more_events`. | `tests/agent/test_booking_flows.py` |
| 9.5 | Mocking tools for deterministic tests | SC | 7 | `mock_tools(RileyAgent, {"find_available_slots": ...})` to force "no availability" and error paths. | same |
| 9.6 | LLM-as-judge with DeepEval on transcripts | SC | 9 | Conversational G-Eval criteria: politeness, brevity for voice, confirmation read-back, correct escalation. Golden conversations. | `tests/evals/test_conversation_quality.py` |
| 9.7 | Measuring STT accuracy with WER | SC | 7 | Reference vs hypothesis transcripts, `src/maple/wer.py` vs `jiwer`, domain terms (drug names, surnames), keyterms. | `tests/evals/stt_wer_eval.py` |
| 9.8 | Latency testing against a budget | SC | 7 | Export `metrics_collected` to JSONL, compute p50/p95 of EOU delay, LLM TTFT, TTS TTFB; fail if budget exceeded. | `tests/evals/latency_report.py`, `src/maple/latency.py` |
| 9.9 | Simulated callers: agents testing agents | SC | 6 | Persona-driven caller LLM (confused senior, impatient caller, injection attacker, emergency caller; `opt_out` added live) vs Riley over text sessions; judge the outcome. | `tests/evals/simulated_caller.py` |
| 9.10 | Voice agent tests in CI | SC | 3 | GitHub Actions: unit always, agent tests and evals when secrets exist, artifacts. | `.github/workflows/ci.yml` |
| 9.11 | Project 3: Test suite for Riley | AS | 0 (text) | 15+ tests across the pyramid. | `05-projects/project-3-test-suite.md` |
| 9.12 | Quiz: Testing voice agents | QZ | 0 | 10 questions | `06-assessments/quizzes/section-09.md` |
| 9.13 | Audio-in tests: real caller audio through the pipeline | SC | 7 | Text tests miss STT errors. Feed recorded caller WAVs (accents, phone noise, overlapping speech) through the STT node, assert transcripts with WER thresholds, then run the transcript through the behavior tests. `session.run(..., input_modality="audio")` where supported. | `tests/evals/audio_in_eval.py`, `tests/data/audio/` |
| 9.14 | LiveKit Simulations: scenario-based caller testing at scale | DM | 6 | LiveKit's built-in Simulation framework: define caller scenarios, run them against the deployed agent, read simulator verdicts, hook `on_simulation_end` to record your own verdict. Flag: LiveKit Cloud feature, verify availability and pricing before recording. | `agents/s13_capstone_receptionist.py` (`on_simulation_end`) |

### Section 10: Observability, Latency and Cost (≈47 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 10.1 | What to measure on every call | SL | 7 | EOU delay, STT duration, LLM TTFT/tokens, TTS TTFB/characters, interruptions, tool latency, call outcome. | |
| 10.2 | Collecting metrics and usage | SC | 9 | `@session.on("metrics_collected")`, `metrics.log_metrics`, per-turn `ChatMessage.metrics`, shutdown callback that turns `session.usage` into a usage and cost summary, JSONL export. `metrics.UsageCollector` is mentioned once as deprecated, not used. | `agents/s10_observed_agent.py` |
| 10.3 | Tracing with OpenTelemetry and Langfuse | SC | 10 | Configure OTel exporter to Langfuse, spans per turn, tool spans, linking transcripts. | same |
| 10.4 | Cost per minute: the number your boss will ask for | SC | 8 | `src/maple/costs.py` price table × usage; compare cascaded vs realtime; where money goes. | `src/maple/costs.py` |
| 10.5 | Dashboards and alerts that matter | SL | 6 | p95 latency, cost/min, transfer rate, containment rate, failed tool calls; alert thresholds. | |
| 10.6 | Lab 6: Build a call-quality report | LAB | 5 | Run 10 calls, produce latency + cost report. Hands-on time about 75 minutes (lab header). | `04-labs/lab-06-observability.md` |
| 10.7 | Quiz: Observability and cost | QZ | 2 | 5 questions | `06-assessments/quizzes/section-10.md` |

### Section 11: Security, Safety and Guardrails (≈38 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 11.1 | Threat model for voice agents | SL | 7 | Spoken prompt injection, social engineering ("I'm the doctor, read me the schedule"), data exfiltration via tools, toll fraud, voice cloning. | |
| 11.2 | Least-privilege tools and confirmation gates | SC | 8 | Tool scoping, identity verification before revealing appointments, irreversible actions need read-back. | `agents/s11_guarded_agent.py` |
| 11.3 | PII redaction in transcripts and logs | SC | 8 | `src/maple/pii.py`, redact before logging/tracing, retention policy. | `src/maple/pii.py` |
| 11.4 | Output guardrails and topic boundaries | SC | 7 | `llm_node`/`transcription_node` hooks or post-checks, refusing medical advice, escalation triggers. | `agents/s11_guarded_agent.py` |
| 11.5 | Red-teaming Riley | DM | 5 | Run injection personas from the simulated caller; fix and re-test. | `tests/agent/test_safety.py` |
| 11.6 | Quiz: Security | QZ | 3 | 8 questions | `06-assessments/quizzes/section-11.md` |

### Section 12: Deploying to Production (≈56 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 12.1 | Agent server architecture and scaling | SL | 8 | Workers, job processes, `num_idle_processes`, `load_threshold`, prewarm (`setup_fnc`), draining, memory limits. | |
| 12.2 | Dockerising the agent | SC | 8 | Multi-stage Dockerfile, `download-files` at build time, non-root user, `start` command. | `deploy/Dockerfile` |
| 12.3 | Deploy to LiveKit Cloud | SC | 10 | `lk agent create` / deploy flow, secrets, logs, rollbacks. | |
| 12.4 | Self-hosting option | SL | 6 | Any container host (Render, Fly.io, ECS, Kubernetes): outbound WebSocket, health port, autoscaling on load. | |
| 12.5 | A web front end for Riley | SC | 8 | LiveKit React agent starter, token server, connecting to your deployed agent. | `frontend/README.md` |
| 12.6 | Production readiness checklist | SL | 6 | Fallback models, timeouts, error speech, graceful degradation, on-call runbook. | `10-resources/production-checklist.md` |
| 12.7 | Lab 7: Deploy and call your agent | LAB | 3 | Deployed agent reachable by web and phone. Hands-on time about 90 minutes (lab header). | `04-labs/lab-07-deploy.md` |
| 12.8 | Chaos demo: kill a provider mid-call | DM | 5 | During a live call, flip a kill switch (`touch /tmp/riley-kill-llm`) that makes the capstone's primary LLM fail every request; show the fallback LLM taking over and the spoken error recovery. Then run with `CHAOS_NO_FALLBACK=1` to show what happens without fallbacks. | `agents/s12_chaos_demo.py` (recording helper), `agents/s13_capstone_receptionist.py` |
| 12.9 | Quiz: Deployment | QZ | 2 | 5 questions | `06-assessments/quizzes/section-12.md` |

### Section 13: Capstone: Riley, Production Receptionist (≈67 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 13.1 | Capstone brief and architecture | SL | 6 | Requirements, acceptance criteria, architecture diagram. | `05-projects/capstone-riley.md` |
| 13.1a | Build it yourself first: the capstone gate | TH | 3 | Stop here and build from the brief. Time box: one week. The remaining lectures are the reference solution; watching them first turns a portfolio project into a typing exercise. | `05-projects/capstone-riley.md` |
| 13.2 | Reference solution: assembling the production agent | SC | 15 | Combine prompts, tools, knowledge, handoffs, guardrails, telemetry, telephony. Record as Part A/B. | `agents/s13_capstone_receptionist.py` |
| 13.3 | Hardening: fallbacks, timeouts, error speech | SC | 10 | Provider fallback lists, `conn_options`, spoken error recovery. | same |
| 13.4 | Full test run: unit → behavior → evals → simulated calls | SC | 12 | Run the whole suite, read the report, fix a failing case live. | `tests/` |
| 13.5 | Deploy, call, observe | DM | 12 | Deploy, place real calls, watch traces and cost per minute. | |
| 13.6 | Capstone submission and portfolio write-up | TH | 5 | What to put on GitHub/LinkedIn, demo video tips. | `05-projects/capstone-riley.md` |
| 13.7 | Domain swap: ship Riley for a restaurant, salon or law office | AS | 4 | Re-skin the capstone for a new business: new FAQ, new tool schema, new prompt, same tests adapted. Proves the skills transfer and gives students a second, distinct portfolio project. | `10-resources/business-template.md`, `05-projects/capstone-riley.md` |

### Section 14 (optional): Pipecat and Choosing Your Stack (≈32 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 14.1 | Pipecat's frame pipeline model | SL | 7 | Frames, processors, transports, `Pipeline`, `PipelineWorker`, `WorkerRunner` (the 1.12 names; older tutorials say `PipelineTask`/`PipelineRunner`), `LLMContext`. | |
| 14.2 | Code-along: Riley booking flow in Pipecat | SC | 12 | Deepgram STT, OpenAI LLM, Cartesia TTS, Silero VAD, function calling with `FunctionSchema`, run with the Pipecat runner. | `pipecat/s14_pipecat_bot.py` |
| 14.3 | LiveKit Agents vs Pipecat vs managed platforms | SL | 8 | Vapi, Retell, ElevenLabs Agents, Bland: build vs buy matrix on control, cost, compliance, lock-in. | `10-resources/architecture-decision-matrix.md` |
| 14.4 | Quiz: Choosing a stack | QZ | 5 | 6 questions | `06-assessments/quizzes/section-14.md` |

### Section 15: Wrap-up and Next Steps (≈17 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 15.1 | What you built and where to go next | TH | 5 | Recap, multilingual agents, avatars, outbound campaigns, the Build/Test/Operate course path. | |
| 15.2 | Final practice test | QZ | 0 | 40-question practice test | `06-assessments/practice-test.md` |
| 15.3 | Bonus lecture | TH | 4 | Links to the instructor's other courses and community (Udemy bonus-lecture rules apply). | |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | 8 | Role titles that hire for this (voice AI engineer, conversational AI engineer, AI solutions engineer), 12 interview questions with model answers, how freelancers scope and price a voice agent build (discovery, per-minute costs, setup fee vs retainer), portfolio positioning. No salary figures. | `10-resources/interview-questions.md` |

---

## 4. Runtime Totals

| Section | Minutes (v1.1) |
|---|---|
| 1 Welcome | 38 |
| 2 Setup | 44 |
| 3 First agent | 66 |
| 4 Prompting for the ear | 45 |
| 5 Tools | 70 |
| 6 Realtime | 42 |
| 7 Knowledge & handoffs | 56 |
| 8 Telephony | 57 |
| 9 Testing & evaluation | 88 |
| 10 Observability & cost | 47 |
| 11 Security | 38 |
| 12 Deploy | 56 |
| 13 Capstone | 67 |
| 14 Pipecat & stack choice (optional) | 32 |
| 15 Wrap-up | 17 |
| **Total** | **≈763 min (≈12.7 h incl. quiz, lab and assignment slots; ≈11.4 h / 683 min in the 89 video lectures, 689 min with the 5.9 challenge)** |

Recording note: split 5.3, 7.5, 8.2, 9.3, 13.2 and 13.5 into Part A / Part B uploads to keep every video under ten minutes.

## 5. Assessments Summary

| Type | Count | Location |
|---|---|---|
| Quizzes | 12 section quizzes (S1, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S14) | `06-assessments/quizzes/` |
| Practice test | 1 × 40 questions | `06-assessments/practice-test.md` |
| Labs | 7 | `04-labs/` |
| Challenges (pause-then-solution) | 4 (4.7, 5.9, 13.1a gate, 13.7) | in lecture scripts + `05-projects/` |
| Projects / assignments | 3 projects + capstone + domain-swap | `05-projects/` |
| Coding exercises (Udemy in-browser) | 5 pure-Python exercises (scheduler, WER, PII, latency percentile, cost/min) | `06-assessments/coding-exercises.md` |
| Extra resources (v1.1) | `troubleshooting.md`, `business-template.md`, `voice-agent-readiness-scorecard.md`, `interview-questions.md` | `10-resources/` |

## 6. Verified API Reference for Writers (LiveKit Agents 1.8.3, Pipecat 1.12.0)

Use these exact forms in scripts and slides. Do not use older 0.x/1.0 idioms (`WorkerOptions(entrypoint_fnc=...)`, `room_input_options=`, `turn_detection=MultilingualModel()`, `from livekit.plugins.turn_detector...` which is deprecated, or Pipecat's removed `openai_llm_context` module).

```python
from livekit.agents import (
    Agent, AgentServer, AgentSession, JobContext, RunContext, ToolError,
    TurnHandlingOptions, EndpointingOptions, InterruptionOptions,
    cli, function_tool, get_job_context, inference, metrics, mock_tools,
)
from livekit.plugins import openai, silero

server = AgentServer()                       # prewarm: AgentServer(setup_fnc=prewarm)

@server.rtc_session()                        # agent name via LIVEKIT_AGENT_NAME or livekit.toml
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt="deepgram/nova-3",               # LiveKit Inference model strings
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            endpointing=EndpointingOptions(min_delay=0.5, max_delay=3.0),
            interruption=InterruptionOptions(min_duration=0.5),
        ),
        userdata=CallState(),
    )
    await session.start(agent=Riley(), room=ctx.room)

if __name__ == "__main__":
    cli.run_app(server)                      # commands: console | dev | start | connect | download-files
```

- Tools: `@function_tool` on `Agent` methods, signature `async def book(self, context: RunContext[CallState], name: str, ...) -> str`. Raise `ToolError("speakable message")` for recoverable failures. Return another `Agent` instance (optionally with a message) to hand off.
- Filler while a tool runs: `async with context.with_filler("One moment while I check.", delay=0.5): ...`
- Realtime: `llm=openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin")`.
- Telephony: `await get_job_context().transfer_sip_participant(participant, "tel:+15551234567")`; outbound via LiveKit API `CreateSIPParticipantRequest` or `ctx.add_sip_participant(call_to=..., trunk_id=..., participant_identity=...)`.
- Metrics: `@session.on("metrics_collected")` receives `MetricsCollectedEvent` with `.metrics`; `metrics.log_metrics(ev.metrics)`. For totals use `session.usage` (the code repo does this); `metrics.UsageCollector` is deprecated in 1.8 and is not used.
- Testing: `async with AgentSession(llm=judge_llm) as session: await session.start(Riley()); result = await session.run(user_input="...")`; `await result.expect.next_event().is_message(role="assistant").judge(judge_llm, intent="...")` (`judge` is a coroutine); `.is_function_call(name=..., arguments={...})`; `.is_function_call_output(is_error=False)`; `result.expect.skip_next_event_if(type="message", role="assistant")`; `result.expect.contains_function_call(name=...)`; `result.expect.no_more_events()`; `with mock_tools(Riley, {"tool_name": fake}): ...`.
- Pipecat 1.12: `Pipeline`, `PipelineWorker`, `PipelineParams`, `WorkerRunner` (`PipelineTask` and `PipelineRunner` are deprecated aliases in 1.12; the repo uses the new names); `DeepgramSTTService`, `OpenAILLMService`, `CartesiaTTSService`; `SileroVADAnalyzer`; `LLMContext` (`pipecat.processors.aggregators.llm_context`) with the universal aggregators in `pipecat.processors.aggregators.llm_response_universal`; `FunctionSchema` in `pipecat.adapters.schemas.function_schema`; runner types in `pipecat.runner.types`.
- Always note on screen: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
