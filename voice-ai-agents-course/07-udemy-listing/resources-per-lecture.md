# Resources per Lecture

> Curriculum v1.1. What to attach to each lecture in Udemy's **Resources** panel (downloadable file or external resource link). Paths are relative to `voice-ai-agents-course/`. Code paths in `03-code/` are published in the student repo `voice-agents-course`.

## How to attach

- **Downloadable files:** export each `10-resources/*.md` to **PDF** (keep the .md too if you like). Students expect PDFs, and PDFs are accessible offline. Name them `S{section}-{slug}.pdf`, e.g., `S01-latency-budget-worksheet.pdf`.
- **Code:** attach a **link to the exact repo folder or file** (external resource link) where Udemy allows it for required learning materials (verify current external-link rules). Where a link isn't allowed, attach a ZIP of the relevant `03-code/` folder at the tagged version.
- **Repo version:** tag the repo per section (`s03`, `s05`...) so links point at code that matches the video. After a framework update, update the tag and send an educational announcement.
- **Quizzes, assignments, practice test and coding exercises** are Udemy-native items built from the listed source files. They aren't downloads.
- **No promotional links** in any resource except the bonus lecture 15.3 (see `publish-checklist.md` §9).
- **Part A / Part B uploads** (5.3, 7.5, 8.2, 9.3, 13.2, 13.5): attach the resources to **Part A** and add "Resources are attached to Part A" to the Part B description.

## Lecture → resource map


### Section 1

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 1.1 | Meet Riley: one call that works, one that fails, one that's fixed | DM | Capstone demo recording, failure recording | none | None (video only) |
| 1.2 | What a voice agent actually is | SL | Diagram: voice pipeline | `10-resources/glossary.md` | Diagram PNG/PDF from slide deck |
| 1.3 | Cascaded vs speech-to-speech architectures | SL | Comparison table | `10-resources/architecture-decision-matrix.md` (preview) | Diagram PNG/PDF from slide deck |
| 1.4 | The latency budget: why 800 ms is the magic number | SL | `10-resources/latency-budget-worksheet.md` | none | PDF download |
| 1.5 | Course roadmap, repo tour and how to get help | SC | `03-code/README.md` | `10-resources/glossary.md`, Course repo link (see note on external links) | Repo link to file/folder (or ZIP) + PDF download |
| 1.6 | Quiz: Voice agent fundamentals | QZ | `06-assessments/quizzes/section-01.md` | none | Udemy quiz |

### Section 2

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 2.1 | Accounts you need and what they cost | SC | `10-resources/provider-cost-guide.md` | none | PDF download |
| 2.2 | Python project setup with uv | SC | `pyproject.toml`, `.env.example` | Course repo link, `10-resources/troubleshooting.md` (uv, download-files) | Repo link to file/folder (or ZIP) + PDF download |
| 2.3 | LiveKit CLI, projects and credentials | SC | none | `10-resources/troubleshooting.md` (keys, CLI) | PDF download |
| 2.4 | Smoke test: unit tests and console mode | SC | `tests/unit/` | `10-resources/troubleshooting.md` (mic permissions, console mode) | Repo link to file/folder (or ZIP) + PDF download |
| 2.5 | Lab 1: Environment verification | LAB | `04-labs/lab-01-environment.md` | `10-resources/troubleshooting.md` | Lab doc (download) + walkthrough video |
| 2.6 | Quick win: run the finished Riley before you build it | SC | `agents/s13_capstone_receptionist.py` | `10-resources/troubleshooting.md` | Repo link to file/folder (or ZIP) + PDF download |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | `src/maple/config.py`, `agents/common.py`, `10-resources/provider-cost-guide.md` | none | Repo link to file/folder (or ZIP) + PDF download |

### Section 3

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 3.1 | LiveKit mental model: rooms, participants, tracks, dispatch | SL | Diagram | none | Diagram PNG/PDF from slide deck |
| 3.2 | AgentSession and Agent: the two core classes | SL | none | `10-resources/livekit-agents-cheatsheet.md` | PDF download |
| 3.3 | Code-along: hello Riley in 30 lines | SC | `agents/s03_hello_agent.py` | `10-resources/livekit-agents-cheatsheet.md` | Repo link to file/folder (or ZIP) + PDF download |
| 3.4 | Dev mode and the Agents Playground | DM | none | none | none |
| 3.5 | Choosing STT, LLM and TTS providers | SL | `src/maple/config.py` | none | Repo link to file/folder (or ZIP) |
| 3.6 | VAD, turn detection and interruptions | SL | Diagram: turn-taking timeline | `10-resources/livekit-agents-cheatsheet.md` (turn-handling block) | Diagram PNG/PDF from slide deck |
| 3.7 | Tuning turn-taking live | DM | none | none | none |
| 3.8 | Lab 2: Customise your first agent | LAB | `04-labs/lab-02-first-agent.md` | none | Lab doc (download) + walkthrough video |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | `agents/s03_hello_agent.py` with `--broken` env toggles | `10-resources/latency-budget-worksheet.md`, `10-resources/voice-failure-taxonomy.md` | Repo link to file/folder (or ZIP) + PDF download |
| 3.10 | Quiz: First agent and turn-taking | QZ | `06-assessments/quizzes/section-03.md` | none | Udemy quiz |

### Section 4

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 4.1 | Why chat prompts fail on voice | SL | none | none | none |
| 4.2 | Anatomy of a voice system prompt | SL | `src/maple/prompts.py` | `10-resources/voice-prompting-cheatsheet.md` | Repo link to file/folder (or ZIP) + PDF download |
| 4.3 | Numbers, dates, names and pronunciation | SC | `agents/s04_voice_prompting.py` | `10-resources/voice-prompting-cheatsheet.md` | Repo link to file/folder (or ZIP) + PDF download |
| 4.4 | Greetings, silence and "are you still there?" | SC | `agents/s04_voice_prompting.py` | none | Repo link to file/folder (or ZIP) |
| 4.5 | Persona and brand voice without the cringe | TH | none | none | none |
| 4.6 | Lab 3: Rewrite a chat prompt for voice | LAB | `04-labs/lab-03-voice-prompting.md` | `10-resources/voice-prompting-cheatsheet.md` | Lab doc (download) + walkthrough video |
| 4.7 | Challenge: Riley for your business | AS | `10-resources/business-template.md` | `10-resources/voice-prompting-cheatsheet.md` | Udemy assignment (+ PDF of any 10-resources template) |
| 4.8 | Quiz: Prompting for the ear | QZ | `06-assessments/quizzes/section-04.md` | none | Udemy quiz |

### Section 5

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 5.1 | How function tools work in LiveKit | SL | none | `10-resources/livekit-agents-cheatsheet.md` (tools block) | PDF download |
| 5.2 | The clinic scheduler: pure Python first | SC | `src/maple/scheduler.py`, `tests/unit/test_scheduler.py` | none | Repo link to file/folder (or ZIP) |
| 5.3 | Code-along: check availability and book | SC | `agents/s05_booking_agent.py` | none | Repo link to file/folder (or ZIP) |
| 5.4 | Confirmation and read-back patterns | SC | `agents/s05_booking_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 5.5 | Hiding latency while tools run | SC | `agents/s05_booking_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 5.6 | Reschedule, cancel and tool errors | SC | `agents/s05_booking_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 5.7 | Session state with userdata | SC | `agents/s05_booking_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 5.8 | Project 1: Booking agent | AS | `05-projects/project-1-booking-agent.md` | none | Udemy assignment (+ PDF of any 10-resources template) |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | `agents/s05_booking_agent.py`, `src/maple/scheduler.py` | none | Video with pause point + repo link to starter/solution |
| 5.10 | Quiz: Tools | QZ | `06-assessments/quizzes/section-05.md` | none | Udemy quiz |

### Section 6

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 6.1 | How realtime speech models work | SL | none | `10-resources/provider-cost-guide.md` | PDF download |
| 6.2 | Code-along: Riley on `gpt-realtime` | SC | `agents/s06_realtime_agent.py` | `10-resources/livekit-agents-cheatsheet.md` (realtime block) | Repo link to file/folder (or ZIP) + PDF download |
| 6.3 | Hybrid: realtime LLM with your own TTS | SC | `agents/s06_realtime_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 6.4 | Head-to-head: cascaded vs realtime | DM | `10-resources/architecture-decision-matrix.md` | none | PDF download |
| 6.5 | Lab 4: Measure both architectures | LAB | `04-labs/lab-04-realtime-vs-cascaded.md` | none | Lab doc (download) + walkthrough video |
| 6.6 | Quiz: Architectures and tools | QZ | `06-assessments/quizzes/section-06.md` | none | Udemy quiz |

### Section 7

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 7.1 | RAG for voice: short, speakable, grounded | SL | none | none | none |
| 7.2 | Code-along: FAQ lookup tool | SC | `agents/s07_knowledge_agent.py` | none | Repo link to file/folder (or ZIP) |
| 7.3 | Scaling knowledge: vector stores and latency | SL | none | none | none |
| 7.4 | Why split one agent into several | SL | none | none | none |
| 7.5 | Code-along: Greeter → Booking → Billing | SC | `agents/s07_multi_agent.py` | none | Repo link to file/folder (or ZIP) |
| 7.6 | Lab 5: Add an Insurance agent | LAB | `04-labs/lab-05-handoffs.md` | none | Lab doc (download) + walkthrough video |
| 7.7 | Quiz: Knowledge and handoffs | QZ | `06-assessments/quizzes/section-07.md` | none | Udemy quiz |
| 7.8 | Multilingual Riley: Spanish and Hindi callers | SC | `agents/s07_knowledge_agent.py` (`LANGUAGE` env), `src/maple/config.py` | `10-resources/voice-prompting-cheatsheet.md` (multilingual notes) | Repo link to file/folder (or ZIP) + PDF download |

### Section 8

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 8.1 | PSTN, SIP and trunks in plain English | SL | Diagram | none | Diagram PNG/PDF from slide deck |
| 8.2 | Inbound calls: Twilio trunk + LiveKit dispatch rule | SC | `livekit.toml.example`, `agents/s08_telephony_agent.py` | `10-resources/telephony-compliance-checklist.md` (read before going live), `10-resources/troubleshooting.md` (Twilio/SIP) | Repo link to file/folder (or ZIP) + PDF download |
| 8.3 | Phone-specific tuning | SC | `livekit.toml.example`, `agents/s08_telephony_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 8.4 | Transfer to a human and ending calls | SC | `livekit.toml.example`, `agents/s08_telephony_agent.py` (same file) | `10-resources/livekit-agents-cheatsheet.md` (telephony block) | Repo link to file/folder (or ZIP) + PDF download |
| 8.5 | Outbound calls: appointment reminders | SC | `agents/s08_outbound_call.py` | `10-resources/telephony-compliance-checklist.md` (outbound section) | Repo link to file/folder (or ZIP) + PDF download |
| 8.6 | Compliance: disclosure, consent and recording | TH | `10-resources/telephony-compliance-checklist.md` | none | PDF download |
| 8.7 | Project 2: Phone receptionist | AS | `05-projects/project-2-phone-receptionist.md` | `10-resources/troubleshooting.md` (Twilio number availability by country, no-phone path) | Udemy assignment (+ PDF of any 10-resources template) |
| 8.8 | Quiz: Telephony | QZ | `06-assessments/quizzes/section-08.md` | none | Udemy quiz |

### Section 9

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 9.1 | How voice agents fail in production | SL | `10-resources/voice-failure-taxonomy.md` | none | PDF download |
| 9.2 | The voice testing pyramid | SL | Diagram | `10-resources/voice-failure-taxonomy.md` | Diagram PNG/PDF from slide deck |
| 9.3 | Behavior tests with LiveKit's test framework | SC | `tests/agent/test_greeting.py` | `10-resources/livekit-agents-cheatsheet.md` (testing block) | Repo link to file/folder (or ZIP) + PDF download |
| 9.4 | Asserting tool calls and arguments | SC | `tests/agent/test_booking_flows.py` | none | Repo link to file/folder (or ZIP) |
| 9.5 | Mocking tools for deterministic tests | SC | `tests/agent/test_booking_flows.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 9.6 | LLM-as-judge with DeepEval on transcripts | SC | `tests/evals/test_conversation_quality.py` | none | Repo link to file/folder (or ZIP) |
| 9.7 | Measuring STT accuracy with WER | SC | `tests/evals/stt_wer_eval.py` | none | Repo link to file/folder (or ZIP) |
| 9.8 | Latency testing against a budget | SC | `tests/evals/latency_report.py`, `src/maple/latency.py` | `10-resources/latency-budget-worksheet.md` | Repo link to file/folder (or ZIP) + PDF download |
| 9.9 | Simulated callers: agents testing agents | SC | `tests/evals/simulated_caller.py` | none | Repo link to file/folder (or ZIP) |
| 9.10 | Voice agent tests in CI | SC | `.github/workflows/ci.yml` | none | Repo link to file/folder (or ZIP) |
| 9.11 | Project 3: Test suite for Riley | AS | `05-projects/project-3-test-suite.md` | none | Udemy assignment (+ PDF of any 10-resources template) |
| 9.12 | Quiz: Testing voice agents | QZ | `06-assessments/quizzes/section-09.md` | none | Udemy quiz |
| 9.13 | Audio-in tests: real caller audio through the pipeline | SC | `tests/evals/audio_in_eval.py`, `tests/data/audio/` | `10-resources/voice-failure-taxonomy.md` | Repo link to file/folder (or ZIP) + PDF download |
| 9.14 | LiveKit Simulations: scenario-based caller testing at scale | DM | `agents/s13_capstone_receptionist.py` (`on_simulation_end`) | `10-resources/voice-failure-taxonomy.md` | Repo link to file/folder (or ZIP) + PDF download |

### Section 10

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 10.1 | What to measure on every call | SL | none | `10-resources/latency-budget-worksheet.md` | PDF download |
| 10.2 | Collecting metrics and usage | SC | `agents/s10_observed_agent.py` | `10-resources/livekit-agents-cheatsheet.md` (metrics block) | Repo link to file/folder (or ZIP) + PDF download |
| 10.3 | Tracing with OpenTelemetry and Langfuse | SC | `agents/s10_observed_agent.py` (same file) | none | Repo link to file/folder (or ZIP) |
| 10.4 | Cost per minute: the number your boss will ask for | SC | `src/maple/costs.py` | `10-resources/provider-cost-guide.md` | Repo link to file/folder (or ZIP) + PDF download |
| 10.5 | Dashboards and alerts that matter | SL | none | none | none |
| 10.6 | Lab 6: Build a call-quality report | LAB | `04-labs/lab-06-observability.md` | none | Lab doc (download) + walkthrough video |
| 10.7 | Quiz: Observability and cost | QZ | `06-assessments/quizzes/section-10.md` | none | Udemy quiz |

### Section 11

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 11.1 | Threat model for voice agents | SL | none | `10-resources/voice-failure-taxonomy.md` (security rows) | PDF download |
| 11.2 | Least-privilege tools and confirmation gates | SC | `agents/s11_guarded_agent.py` | none | Repo link to file/folder (or ZIP) |
| 11.3 | PII redaction in transcripts and logs | SC | `src/maple/pii.py` | `10-resources/telephony-compliance-checklist.md` (data retention, HIPAA) | Repo link to file/folder (or ZIP) + PDF download |
| 11.4 | Output guardrails and topic boundaries | SC | `agents/s11_guarded_agent.py` | none | Repo link to file/folder (or ZIP) |
| 11.5 | Red-teaming Riley | DM | `tests/agent/test_safety.py` | none | Repo link to file/folder (or ZIP) |
| 11.6 | Quiz: Security | QZ | `06-assessments/quizzes/section-11.md` | none | Udemy quiz |

### Section 12

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 12.1 | Agent server architecture and scaling | SL | none | `10-resources/production-checklist.md` | PDF download |
| 12.2 | Dockerising the agent | SC | `deploy/Dockerfile` | none | Repo link to file/folder (or ZIP) |
| 12.3 | Deploy to LiveKit Cloud | SC | none | none | none |
| 12.4 | Self-hosting option | SL | none | none | none |
| 12.5 | A web front end for Riley | SC | `frontend/README.md` | none | Repo link to file/folder (or ZIP) |
| 12.6 | Production readiness checklist | SL | `10-resources/production-checklist.md` | `10-resources/voice-agent-readiness-scorecard.md` | PDF download |
| 12.7 | Lab 7: Deploy and call your agent | LAB | `04-labs/lab-07-deploy.md` | none | Lab doc (download) + walkthrough video |
| 12.8 | Chaos demo: kill a provider mid-call | DM | `agents/s12_chaos_demo.py`, `agents/s13_capstone_receptionist.py` | `10-resources/production-checklist.md`, `10-resources/voice-agent-readiness-scorecard.md` | Repo link to file/folder (or ZIP) + PDF download |
| 12.9 | Quiz: Deployment | QZ | `06-assessments/quizzes/section-12.md` | none | Udemy quiz |

### Section 13

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 13.1 | Capstone brief and architecture | SL | `05-projects/capstone-riley.md` | `10-resources/production-checklist.md`, `10-resources/voice-agent-readiness-scorecard.md` (acceptance gate) | PDF download |
| 13.1a | Build it yourself first: the capstone gate | TH | `05-projects/capstone-riley.md` | `10-resources/voice-agent-readiness-scorecard.md` | PDF download |
| 13.2 | Reference solution: assembling the production agent | SC | `agents/s13_capstone_receptionist.py` | none | Repo link to file/folder (or ZIP) |
| 13.3 | Hardening: fallbacks, timeouts, error speech | SC | `agents/s13_capstone_receptionist.py` (same file) | `10-resources/production-checklist.md` | Repo link to file/folder (or ZIP) + PDF download |
| 13.4 | Full test run: unit → behavior → evals → simulated calls | SC | `tests/` | none | Repo link to file/folder (or ZIP) |
| 13.5 | Deploy, call, observe | DM | none | none | none |
| 13.6 | Capstone submission and portfolio write-up | TH | `05-projects/capstone-riley.md` | none | none |
| 13.7 | Domain swap: ship Riley for a restaurant, salon or law office | AS | `10-resources/business-template.md`, `05-projects/capstone-riley.md` | `10-resources/voice-agent-readiness-scorecard.md` | Udemy assignment (+ PDF of any 10-resources template) |

### Section 14

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 14.1 | Pipecat's frame pipeline model | SL | none | none | none |
| 14.2 | Code-along: Riley booking flow in Pipecat | SC | `pipecat/s14_pipecat_bot.py` | none | Repo link to file/folder (or ZIP) |
| 14.3 | LiveKit Agents vs Pipecat vs managed platforms | SL | `10-resources/architecture-decision-matrix.md` | `10-resources/provider-cost-guide.md` | PDF download |
| 14.4 | Quiz: Choosing a stack | QZ | `06-assessments/quizzes/section-14.md` | none | Udemy quiz |

### Section 15

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 15.1 | What you built and where to go next | TH | none | All `10-resources/` files as one ZIP ("Voice Agent Toolkit") | PDF download |
| 15.2 | Final practice test | QZ | `06-assessments/practice-test.md` | none | Udemy quiz |
| 15.3 | Bonus lecture | TH | none | none | Bonus lecture: links allowed here only, per Udemy bonus rules (verify) |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | `10-resources/interview-questions.md` | `10-resources/voice-agent-readiness-scorecard.md` (portfolio talking points) | PDF download |

## Downloadable resource index (`10-resources/`)

| File | Primary lecture | Also attached to |
|---|---|---|
| `10-resources/troubleshooting.md` | 2.4 | 2.2, 2.3, 2.5, 2.6, 8.2, 8.7 |
| `10-resources/business-template.md` | 4.7 | 13.7 |
| `10-resources/voice-agent-readiness-scorecard.md` | 12.6 | 12.8, 13.1, 13.1a, 13.7, 15.4 |
| `10-resources/interview-questions.md` | 15.4 | none |
| `10-resources/latency-budget-worksheet.md` | 1.4 | 3.9, 9.8, 10.1 |
| `10-resources/provider-cost-guide.md` | 2.1 | 6.1, 10.4, 14.3 |
| `10-resources/architecture-decision-matrix.md` | 6.4 | 1.3, 14.3 |
| `10-resources/telephony-compliance-checklist.md` | 8.6 | 8.2, 8.5, 11.3 |
| `10-resources/voice-failure-taxonomy.md` | 9.1 | 3.9, 9.2, 9.13, 9.14, 11.1 |
| `10-resources/production-checklist.md` | 12.6 | 12.1, 12.8, 13.1, 13.3 |
| `10-resources/voice-prompting-cheatsheet.md` | 4.2 | 4.3, 4.6, 4.7, 7.8 |
| `10-resources/livekit-agents-cheatsheet.md` | 3.3 | 3.2, 3.6, 5.1, 6.2, 8.4, 9.3, 10.2 |
| `10-resources/glossary.md` | 1.2 | 1.5 |

## Diagram exports (from `09-production/slide-deck-outline.md`)

| Diagram | Lecture | Export |
|---|---|---|
| Voice pipeline | 1.2 | PNG (1920×1080) + PDF handout |
| Cascaded vs S2S vs hybrid comparison table | 1.3 | PNG (1920×1080) + PDF handout |
| Latency budget waterfall | 1.4, 9.8 | PNG (1920×1080) + PDF handout |
| LiveKit rooms/participants/dispatch | 3.1 | PNG (1920×1080) + PDF handout |
| Turn-taking timeline | 3.6 | PNG (1920×1080) + PDF handout |
| SIP call flow | 8.1 | PNG (1920×1080) + PDF handout |
| Voice testing pyramid | 9.2 | PNG (1920×1080) + PDF handout |
| Observability dashboard | 10.5 | PNG (1920×1080) + PDF handout |
| Capstone architecture | 13.1 | PNG (1920×1080) + PDF handout |
