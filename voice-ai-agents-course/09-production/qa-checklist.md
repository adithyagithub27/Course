# QA Checklist

> Run this before any lecture is marked final (milestone M6 in `production-schedule.md`) and again for the full course before submission. Complements the Quality Bar in `09-heygen/PRODUCTION-GUIDE.md` and `07-udemy-listing/publish-checklist.md`.

---

## 1. Per-lecture checks (every video lecture)

### Technical / content
- [ ] Matches `01-curriculum/curriculum.md` (v1.1): ID, title, objective and key points all covered; runtime within ±20% of the curriculum minutes
- [ ] Lectures over 10 minutes split into Part A / Part B where the curriculum says so (5.3, 7.5, 8.2, 9.3, 13.2, 13.5), each part with its own hook and bridge
- [ ] Engagement mechanics present (see `recording-guide.md` §9): section-end "You can now..." card on the last lecture of each section; before/after audio on every turn-taking or voice setting change; failure-first opening on build sections; version-pin note on the first slide of code lectures
- [ ] Every API call on screen uses **only** the forms in curriculum §6; none of the banned idioms (`WorkerOptions(entrypoint_fnc=...)`, `room_input_options=`, `turn_detection=MultilingualModel()`, `from livekit.plugins.turn_detector...`, Pipecat `openai_llm_context`)
- [ ] Version banner visible on code lectures: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12"
- [ ] File paths on screen match `03-code/` exactly
- [ ] Numbers stated (latency, cost, WER) come from actual runs shown, or are labelled as examples
- [ ] Prices are labelled "check current pricing"
- [ ] Compliance statements are labelled "not legal advice" (8.6 and anywhere else they appear)
- [ ] No promotional content outside 15.3

### Audio / video
- [ ] 1920×1080, 30 fps, H.264; no dropped frames or stutter
- [ ] Integrated loudness -16 LUFS (±1), true peak ≤ -1 dBTP; music ≤ -24 LUFS under voice
- [ ] No clipping, hum, room echo or mouth clicks; room tone under cuts
- [ ] Agent audio audible and level-matched with narration; caller vs agent vs avatar clearly distinguishable
- [ ] **No agent echo / self-interruption** artefacts (headset used)
- [ ] Avatar: lip sync, pronunciation dictionary applied (LiveKit, Pipecat, Deepgram, Cartesia, Silero, SIP, WER, Riley, Maple Street)
- [ ] Visual change at least every 30 s; avatar ≤ 60 s continuous; hook in first 15 s; 3-bullet recap; bridge
- [ ] Code font legible at 720p playback (JetBrains Mono 20-22 px); ≤ 15 lines visible

### Security scrub
- [ ] No API keys, tokens, secrets, `.env` contents, project URLs with secrets, SIP trunk credentials
- [ ] No real phone numbers (on screen or in audio); caller ID masked; fictional numbers use the 555-01XX range
- [ ] No personal emails, home paths, usernames, browser autofill, notifications
- [ ] Any other human voice on a call has signed consent

### Accessibility
- [ ] Captions present, corrected for domain terms, synced (±0.5 s), ≤ 2 lines, ≤ ~42 chars/line
- [ ] Diagrams narrated (meaning doesn't depend on seeing them)
- [ ] Pass/fail uses ✓/✗ or labels, not color alone; text contrast meets WCAG AA (design system)
- [ ] Speaker labels on screen when agent audio plays (`Caller`, `Riley (agent)`, `Human`)
- [ ] No flashing content > 3 flashes/second
- [ ] Downloadable resources available as text-based PDF/Markdown

---

## 2. Code verification per lecture

> Run on a clean machine with the pinned versions. Record the date and installed versions (`uv pip list | grep -E "livekit|pipecat|deepeval|jiwer"`). Lectures without code show "n/a".

| ID | Lecture | Type | Verification | Pass | Date |
|---|---|---|---|---|---|
| 1.1 | Meet Riley: one call that works, one that fails, one that's fixed | DM | Three calls recorded (works / naive agent fails / fixed agent passes tests); capstone deployed; numbers masked; failure call clearly labelled as the naive agent | [ ] | |
| 1.2 | What a voice agent actually is | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 1.3 | Cascaded vs speech-to-speech architectures | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 1.4 | The latency budget: why 800 ms is the magic number | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 1.5 | Course roadmap, repo tour and how to get help | SC | `make` targets listed on screen exist in `03-code/Makefile` | [ ] | |
| 1.6 | Quiz: Voice agent fundamentals | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 2.1 | Accounts you need and what they cost | SC | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 2.2 | Python project setup with uv | SC | Fresh clone → `uv sync` → `make install` succeeds on macOS, Windows, Linux; `download-files` completes | [ ] | |
| 2.3 | LiveKit CLI, projects and credentials | SC | `lk` CLI commands shown match current CLI help output (verify flags) | [ ] | |
| 2.4 | Smoke test: unit tests and console mode | SC | `make test` passes offline (no keys); `uv run agents/s03_hello_agent.py console` works with headset mic | [ ] | |
| 2.5 | Lab 1: Environment verification | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 2.6 | Quick win: run the finished Riley before you build it | SC | `make console AGENT=agents/s13_capstone_receptionist.py` works on a fresh setup; booking + transfer trigger as shown | [ ] | |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | `MOCK_MODE=1 python agents/s03_hello_agent.py console --text` runs with no API keys; spend-limit screens current (verify provider UIs) | [ ] | |
| 3.1 | LiveKit mental model: rooms, participants, tracks, dispatch | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 3.2 | AgentSession and Agent: the two core classes | SL | Code matches curriculum §6 `AgentSession(...)` block exactly | [ ] | |
| 3.3 | Code-along: hello Riley in 30 lines | SC | `agents/s03_hello_agent.py` runs in `console`; line count ≈30 as claimed; imports only from §6 | [ ] | |
| 3.4 | Dev mode and the Agents Playground | DM | `dev` mode hot reload works; Playground connects | [ ] | |
| 3.5 | Choosing STT, LLM and TTS providers | SL | Env var names match `src/maple/config.py` | [ ] | |
| 3.6 | VAD, turn detection and interruptions | SL | `TurnHandlingOptions`, `EndpointingOptions`, `InterruptionOptions` args match §6 and installed 1.8.x | [ ] | |
| 3.7 | Tuning turn-taking live | DM | Settings changed on screen exist in 1.8.x; audible difference present | [ ] | |
| 3.8 | Lab 2: Customise your first agent | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | Each `BROKEN=` case in `agents/s03_hello_agent.py` (short_endpointing, long_endpointing, no_interruptions, markdown, wrong_stt) produces the audible failure; unsetting it restores normal behaviour; before/after audio levels matched | [ ] | |
| 3.10 | Quiz: First agent and turn-taking | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 4.1 | Why chat prompts fail on voice | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 4.2 | Anatomy of a voice system prompt | SL | Prompt blocks shown match `src/maple/prompts.py` | [ ] | |
| 4.3 | Numbers, dates, names and pronunciation | SC | `agents/s04_voice_prompting.py` runs; spoken output matches the transforms described | [ ] | |
| 4.4 | Greetings, silence and "are you still there?" | SC | `on_enter`, `user_away_timeout` behave as narrated on 1.8.x | [ ] | |
| 4.5 | Persona and brand voice without the cringe | TH | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 4.6 | Lab 3: Rewrite a chat prompt for voice | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 4.7 | Challenge: Riley for your business | AS | Brief complete; rubric + example solution run | [ ] | |
| 4.8 | Quiz: Prompting for the ear | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 5.1 | How function tools work in LiveKit | SL | Tool signature form matches §6 (`RunContext[CallState]`, `ToolError`) | [ ] | |
| 5.2 | The clinic scheduler: pure Python first | SC | `tests/unit/test_scheduler.py` passes | [ ] | |
| 5.3 | Code-along: check availability and book | SC | `agents/s05_booking_agent.py` books a slot end-to-end | [ ] | |
| 5.4 | Confirmation and read-back patterns | SC | Correction flow ("no, Thursday") demonstrated works | [ ] | |
| 5.5 | Hiding latency while tools run | SC | `context.with_filler(...)` form matches §6 | [ ] | |
| 5.6 | Reschedule, cancel and tool errors | SC | `ToolError` messages are spoken, retry works | [ ] | |
| 5.7 | Session state with userdata | SC | userdata dataclass carried across tools | [ ] | |
| 5.8 | Project 1: Booking agent | AS | Brief complete; rubric + example solution run | [ ] | |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | Spec on screen matches `scheduler.add_to_waitlist` signature; solution in `agents/s05_booking_agent.py` passes tests; pause card shown | [ ] | |
| 5.10 | Quiz: Tools | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 6.1 | How realtime speech models work | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 6.2 | Code-along: Riley on `gpt-realtime` | SC | `openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin")` runs; same tools reused | [ ] | |
| 6.3 | Hybrid: realtime LLM with your own TTS | SC | Text-modality + separate TTS works on installed plugin version | [ ] | |
| 6.4 | Head-to-head: cascaded vs realtime | DM | Five test calls reproducible; numbers shown come from actual runs | [ ] | |
| 6.5 | Lab 4: Measure both architectures | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 6.6 | Quiz: Architectures and tools | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 7.1 | RAG for voice: short, speakable, grounded | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 7.2 | Code-along: FAQ lookup tool | SC | `agents/s07_knowledge_agent.py` answers from `data/faq.md`; unknown questions → "I don't know" | [ ] | |
| 7.3 | Scaling knowledge: vector stores and latency | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 7.4 | Why split one agent into several | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 7.5 | Code-along: Greeter → Booking → Billing | SC | `agents/s07_multi_agent.py` handoffs Greeter → Booking → Billing work; userdata shared | [ ] | |
| 7.6 | Lab 5: Add an Insurance agent | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 7.7 | Quiz: Knowledge and handoffs | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 7.8 | Multilingual Riley: Spanish and Hindi callers | SC | `LANGUAGE` env switches STT/TTS/turn detector for Spanish and Hindi; native-speaker check of demo audio and captions | [ ] | |
| 8.1 | PSTN, SIP and trunks in plain English | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 8.2 | Inbound calls: Twilio trunk + LiveKit dispatch rule | SC | Inbound call reaches agent; dispatch rule and agent name match `livekit.toml.example` | [ ] | |
| 8.3 | Phone-specific tuning | SC | Caller ID read from SIP participant attributes (masked on screen) | [ ] | |
| 8.4 | Transfer to a human and ending calls | SC | `get_job_context().transfer_sip_participant(...)` transfers to test phone; `end_call` hangs up | [ ] | |
| 8.5 | Outbound calls: appointment reminders | SC | `agents/s08_outbound_call.py` calls only instructor-owned test phone | [ ] | |
| 8.6 | Compliance: disclosure, consent and recording | TH | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 8.7 | Project 2: Phone receptionist | AS | Brief complete; rubric + example solution run | [ ] | |
| 8.8 | Quiz: Telephony | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 9.1 | How voice agents fail in production | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 9.2 | The voice testing pyramid | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 9.3 | Behavior tests with LiveKit's test framework | SC | `pytest tests/agent/test_greeting.py` passes with key; auto-skips without | [ ] | |
| 9.4 | Asserting tool calls and arguments | SC | `pytest tests/agent/test_booking_flows.py` passes; assertion API matches §6 | [ ] | |
| 9.5 | Mocking tools for deterministic tests | SC | `mock_tools(...)` form matches §6; forced paths behave as narrated | [ ] | |
| 9.6 | LLM-as-judge with DeepEval on transcripts | SC | `tests/evals/test_conversation_quality.py` runs; DeepEval API matches installed version | [ ] | |
| 9.7 | Measuring STT accuracy with WER | SC | `tests/evals/stt_wer_eval.py` output: `src/maple/wer.py` agrees with jiwer | [ ] | |
| 9.8 | Latency testing against a budget | SC | `tests/evals/latency_report.py` on `tests/data/sample_metrics.jsonl` gives numbers shown | [ ] | |
| 9.9 | Simulated callers: agents testing agents | SC | `tests/evals/simulated_caller.py` personas run; judge verdicts shown are real | [ ] | |
| 9.10 | Voice agent tests in CI | SC | `.github/workflows/ci.yml` green on a fresh fork (unit); agent/eval jobs skip without secrets | [ ] | |
| 9.11 | Project 3: Test suite for Riley | AS | Brief complete; rubric + example solution run | [ ] | |
| 9.12 | Quiz: Testing voice agents | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 9.13 | Audio-in tests: real caller audio through the pipeline | SC | `tests/evals/audio_in_eval.py` runs on `tests/data/audio/`; WER thresholds as shown; `input_modality="audio"` used only where supported in installed version | [ ] | |
| 9.14 | LiveKit Simulations: scenario-based caller testing at scale | DM | LiveKit Simulation availability and pricing verified on the recording plan **before** recording; `on_simulation_end` hook in capstone works; record as demo-only if unavailable | [ ] | |
| 10.1 | What to measure on every call | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 10.2 | Collecting metrics and usage | SC | `metrics_collected`, `metrics.log_metrics`, `UsageCollector` forms match §6 | [ ] | |
| 10.3 | Tracing with OpenTelemetry and Langfuse | SC | Traces appear in Langfuse; no PII in spans | [ ] | |
| 10.4 | Cost per minute: the number your boss will ask for | SC | `src/maple/costs.py` unit tests pass; price table labelled "check current pricing" | [ ] | |
| 10.5 | Dashboards and alerts that matter | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 10.6 | Lab 6: Build a call-quality report | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 10.7 | Quiz: Observability and cost | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 11.1 | Threat model for voice agents | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 11.2 | Least-privilege tools and confirmation gates | SC | Identity verification gate blocks the social-engineering script | [ ] | |
| 11.3 | PII redaction in transcripts and logs | SC | `src/maple/pii.py` unit tests pass; logs redacted | [ ] | |
| 11.4 | Output guardrails and topic boundaries | SC | `llm_node`/`transcription_node` hook usage valid on 1.8.x | [ ] | |
| 11.5 | Red-teaming Riley | DM | `tests/agent/test_safety.py` fails before fix, passes after (as shown) | [ ] | |
| 11.6 | Quiz: Security | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 12.1 | Agent server architecture and scaling | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 12.2 | Dockerising the agent | SC | `docker build -f deploy/Dockerfile .` succeeds; container runs as non-root; `start` works | [ ] | |
| 12.3 | Deploy to LiveKit Cloud | SC | Deploy commands match current LiveKit Cloud CLI (verify); rollback demonstrated | [ ] | |
| 12.4 | Self-hosting option | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 12.5 | A web front end for Riley | SC | Front-end starter connects to deployed agent per `frontend/README.md` | [ ] | |
| 12.6 | Production readiness checklist | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 12.7 | Lab 7: Deploy and call your agent | LAB | Complete the lab as a student on a clean machine; expected outputs match | [ ] | |
| 12.8 | Chaos demo: kill a provider mid-call | DM | Revoking TTS key / blocking STT mid-call triggers fallback + spoken recovery; revoked key replaced after recording | [ ] | |
| 12.9 | Quiz: Deployment | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 13.1 | Capstone brief and architecture | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 13.1a | Build it yourself first: the capstone gate | TH | Gate card clearly says pause and build; brief in `05-projects/capstone-riley.md` is sufficient to build without the walkthrough | [ ] | |
| 13.2 | Reference solution: assembling the production agent | SC | `agents/s13_capstone_receptionist.py` runs in console and on phone | [ ] | |
| 13.3 | Hardening: fallbacks, timeouts, error speech | SC | Fallback triggers when primary provider key is revoked (demo) | [ ] | |
| 13.4 | Full test run: unit → behavior → evals → simulated calls | SC | Full suite runs; the "failing case" fixed live is real | [ ] | |
| 13.5 | Deploy, call, observe | DM | Deployed; real calls; traces and cost/min visible; numbers masked | [ ] | |
| 13.6 | Capstone submission and portfolio write-up | TH | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 13.7 | Domain swap: ship Riley for a restaurant, salon or law office | AS | Brief complete; rubric + example solution run | [ ] | |
| 14.1 | Pipecat's frame pipeline model | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 14.2 | Code-along: Riley booking flow in Pipecat | SC | `pipecat/s14_pipecat_bot.py` runs on pipecat-ai 1.12.x; imports match §6 (no `openai_llm_context`) | [ ] | |
| 14.3 | LiveKit Agents vs Pipecat vs managed platforms | SL | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 14.4 | Quiz: Choosing a stack | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 15.1 | What you built and where to go next | TH | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 15.2 | Final practice test | QZ | Every question has correct answer + explanation; answers match current APIs | [ ] | |
| 15.3 | Bonus lecture | TH | n/a (conceptual). Check facts and diagrams against curriculum | [ ] | |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | No salary figures; role titles and interview answers match `10-resources/interview-questions.md`; no promotional content (that belongs in 15.3) | [ ] | |

---

## 3. Course-level checks (before submission)

- [ ] Fresh clone on macOS, Windows (WSL and native if supported) and Linux: `make install`, `make test` (offline) pass
- [ ] With keys: `make test-agent` and `make eval` pass; CI green on a fresh fork
- [ ] 12 section quizzes + practice test present; 4 challenges (4.7, 5.9, 13.1a, 13.7) have clear pause/submit instructions
- [ ] Coding exercises (5) pass hidden tests in Udemy's runner and fail on wrong answers
- [ ] Quizzes (12) + practice test (40 Q): every answer reviewed; no question depends on a now-changed API detail
- [ ] All `10-resources/` PDFs exported and attached per `07-udemy-listing/resources-per-lecture.md`
- [ ] Lecture order in Udemy matches the curriculum; free previews set
- [ ] Full watch-through in student preview (≥1.5×) with notes logged and fixed
- [ ] Q&A seeded: 5 likely questions per section posted with answers on launch day (recording-guide §9)
- [ ] Keys used in recording rotated; recording phone numbers locked down or released

## 4. Sign-off

| Section | QA by | Date | Issues found | Fixed |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |
| 11 | | | | |
| 12 | | | | |
| 13 | | | | |
| 14 | | | | |
| 15 | | | | |
