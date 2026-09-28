# Udemy Course Description

## Production Voice AI Agents with Python: Build, Test, Deploy

> Course 3 of the Build → Test → Operate series. Every field matches `01-curriculum/curriculum.md`. Paste each block into the matching field in Udemy's course landing page (description) and intended learners (objectives, requirements, audience) editors. Udemy's rich-text editor accepts **bold**, *italic*, bullet lists and numbered lists. It does not render markdown headings, so section headers below are bold lines. Paste as plain text and re-apply bold in the editor if the formatting doesn't carry over.

---

## Course description (copy-paste ready, 969 words)

<!-- BEGIN DESCRIPTION -->

**Your voice agent sounded great in the demo. Then a real caller phoned in.**

The caller talked over it. The agent booked Thursday when they said Tuesday. It took two seconds to answer, read out a URL character by character, and never offered to transfer to a human. Nobody caught any of this, because nobody had tested it.

Voice is where AI agents are heading next: receptionists, support lines, booking lines, reminder calls. Voice is also much less forgiving than chat. A caller notices a one-second pause straight away. You can't speak markdown. When a transcription error lands in a tool call, the result is a wrong appointment in a real calendar.

**Production Voice AI Agents with Python** teaches you to build voice agents that hold up on real phone calls. You'll build one, then test it, monitor it and deploy it.

**What you'll build: Riley, the AI receptionist for Maple Street Dental**

The whole course uses one running project. Riley is a voice agent for a fictional dental clinic. By the end, Riley:

- answers questions from the clinic's FAQ in short, speakable, grounded answers, including for Spanish- and Hindi-speaking callers
- books, reschedules and cancels appointments through function tools, with read-back confirmations
- hands off between Greeter, Booking and Billing specialist agents
- answers a **real phone number** over SIP, makes outbound reminder calls and transfers to a human
- has a test suite: behavior tests, tool-call assertions, LLM-as-judge evals, WER, latency budgets and simulated callers, all running in GitHub Actions
- reports latency, token usage and **cost per minute** through OpenTelemetry and Langfuse
- resists spoken prompt injection and social engineering, and redacts PII from logs
- runs in Docker on LiveKit Cloud, with a web front end

**What makes this course different**

- **Code-first and production-first.** You write every line in Python with open-source frameworks. There are no drag-and-drop builders.
- **A full section on testing voice agents.** Most voice content stops at "it works on my laptop". Section 9 treats Riley like software: a testing pyramid from pure-Python unit tests up to simulated callers, with CI.
- **Latency and cost are measured, not guessed.** You set a latency budget in Section 1, measure it in Sections 9 and 10, and report cost per minute for cascaded and speech-to-speech builds.
- **Both architectures, one agent.** You build Riley as a cascaded STT → LLM → TTS pipeline and again on OpenAI Realtime, then compare them on the same test calls.
- **You hear the failures, not just read about them.** "Break it" demos let you hear an agent cut callers off, talk over them and read markdown aloud, and then hear the one setting that fixes each. A chaos demo kills a provider mid-call to show fallbacks taking over.
- **You build before you watch.** Challenge lectures ask you to build first and check the solution after, and the capstone starts with a "build it yourself" gate. A domain-swap project re-skins Riley for a restaurant, salon or law office, so you finish with two portfolio projects.
- **An informed stack choice.** You rebuild the booking flow in Pipecat and compare LiveKit Agents, Pipecat and managed platforms (Vapi, Retell, ElevenLabs Agents, Bland) on control, cost, compliance and lock-in.

**Tools and technologies**

- **LiveKit Agents 1.8**: AgentServer, AgentSession, Agent, function tools, test framework, metrics
- **OpenAI**: GPT-4.1 mini for the cascaded pipeline and `gpt-realtime` for speech-to-speech
- **Deepgram** (STT), **Cartesia** (TTS), **Silero** VAD and LiveKit's semantic turn detector
- **Twilio Elastic SIP Trunking + LiveKit SIP**: inbound, outbound and transfer
- **Pipecat 1.12**: the same agent built as a frame pipeline
- **pytest, pytest-asyncio, DeepEval, jiwer**: behavior tests, LLM-as-judge and WER
- **OpenTelemetry + Langfuse**: traces, metrics and cost per minute
- **Docker, LiveKit Cloud, GitHub Actions**: deployment and CI

All model names come from environment variables, so when a provider renames a model you change one line.

**How the course is organized**

- **Foundations (Sections 1-3):** how voice agents work, the latency budget, setup (including spending caps and a free offline mock mode), talking to the finished Riley before you build it, and your first agent in about 30 lines
- **Make it useful (Sections 4-7):** prompting for the ear, booking tools, OpenAI Realtime, a knowledge base, multi-agent handoffs and multilingual callers
- **Make it real (Section 8):** a real phone number, inbound and outbound calls, human transfer, and compliance basics
- **Make it reliable (Sections 9-11):** testing and evaluation (including audio-in tests and scenario-based simulated calls), observability and cost, security and guardrails
- **Ship it (Sections 12-15):** Docker and LiveKit Cloud deployment, the production capstone, an optional Pipecat section with a build-vs-buy comparison, and a careers lecture on voice AI roles, interview questions and scoping and pricing a client project

**What you get:** about 11.3 hours of video in 97 lectures, a complete GitHub code repository, 7 guided labs, 4 build-it-yourself challenges, 3 projects plus a capstone and a domain-swap project, 12 section quizzes, a 40-question practice test, 5 in-browser coding exercises, and downloadable cheat sheets, templates and checklists: latency budget, provider costs, architecture decision matrix, telephony compliance, voice failure taxonomy, production readiness scorecard, troubleshooting guide, business re-skin template and interview questions.

**Part of a series.** This is Course 3 in a Build → Test → Operate series with *Generative AI & AI Agents: Zero to Production* and *AI Agent Testing & Evaluation*. It stands on its own, and you don't need the other courses.

The code targets livekit-agents 1.8 and pipecat-ai 1.12. Voice frameworks move quickly, and the repository README tracks version updates.

Plan on spending about $10-20 in API usage for the whole course, using free tiers and starter credits (prices change; check each provider). An offline mock mode lets you practise without spending anything, and every telephony lab has a path for students who can't get a phone number in their country.

If you can build a chatbot, this course teaches you to build a voice agent that works on real phone calls, with tests to prove it.

<!-- END DESCRIPTION -->

**Description checks**

- Word count: **969** (Udemy asks for at least 200 words; our target was 300+). Verify the current minimum in the editor.
- Primary keywords appear in the first two paragraphs: *voice agent*, *AI*, *production*, *Python*, *phone*. Tool keywords appear early in the body: *LiveKit*, *OpenAI Realtime*, *Pipecat*, *Twilio SIP*.
- The description has no external links, no coupon codes and no off-platform contact details. Udemy's promotional rules don't allow them in the landing page (verify current policy).
- The description makes no market or salary claims. The careers lecture (15.4) also has no salary figures.
- Counts match curriculum v1.1: ~11.3 h video, 97 lectures, 12 section quizzes, 7 labs, 4 challenges, 3 projects + capstone + domain swap, 5 coding exercises.

---

## What you'll learn (Udemy limit: 160 characters each, 4 minimum; verify)

| # | Objective | Chars |
|---|---|---|
| 1 | Build real-time voice AI agents in Python with LiveKit Agents: STT, LLM, TTS, VAD and turn detection in one low-latency pipeline | 128 |
| 2 | Choose between cascaded (STT→LLM→TTS) and speech-to-speech (OpenAI Realtime) architectures using latency, cost and quality data | 127 |
| 3 | Write system prompts designed for the ear: brevity, pacing, read-backs, numbers, dates and pronunciation | 104 |
| 4 | Give voice agents tools to book, reschedule and cancel appointments, with confirmation read-backs and filler speech while tools run | 131 |
| 5 | Add a spoken FAQ knowledge base (RAG for voice) and multi-agent handoffs between specialist agents | 98 |
| 6 | Put an agent on a real phone number with SIP: inbound calls, outbound calls and transfer to a human | 99 |
| 7 | Test voice agents like software: behavior tests, LLM-as-judge, tool-call assertions, WER, latency budgets and simulated callers in CI | 133 |
| 8 | Monitor latency, token usage and cost per minute with LiveKit metrics, OpenTelemetry and Langfuse | 97 |
| 9 | Secure voice agents against prompt injection, PII leakage and unsafe tool use, with escalation to humans | 104 |
| 10 | Deploy to production with Docker and LiveKit Cloud, and compare the build with Pipecat and managed voice platforms | 114 |

These are the curriculum's 10 learning outcomes, lightly edited to fit the limit. Paste one per field, without trailing periods.

## Requirements

- Basic Python: functions, classes, pip or uv, and running scripts from a terminal
- Basic async/await in Python (Sections 1-3 are beginner-safe)
- A computer (Windows, macOS or Linux) with a microphone and headphones
- Free accounts with LiveKit Cloud, OpenAI, Deepgram and Cartesia; a Twilio trial for the phone sections (Section 2 walks through each)
- About $10-20 of API usage for the whole course using free tiers and starter credits (prices change; check each provider)
- No prior voice, audio or telephony experience needed

## Who this course is for

- Python developers who have built a chatbot or LLM app and now want it to talk, listen and answer the phone
- AI engineers asked to ship a voice agent (receptionist, support line, booking line, reminders) into production
- Students of the instructor's courses "Generative AI & AI Agents: Zero to Production" or "AI Agent Testing & Evaluation" who want the voice sequel (neither is required)
- No-code voice builders (Vapi, Retell, n8n) who have hit the limits of the platform and want full control in code
- QA and SDET engineers who need a way to test voice agents: tool-call assertions, WER, latency budgets and simulated callers
- Tech leads and founders deciding between building on LiveKit or Pipecat and buying a managed voice platform

## Who this course is NOT for

> Udemy has no separate "not for" field. Use these as the last lines of the description or in the FAQ-style closing paragraph if you want them public, or keep them for the promo and marketing copy.

- Complete beginners to programming. You need to be comfortable reading and running Python
- People looking for a no-code or drag-and-drop voice agent builder. Every section is Python code
- Anyone wanting to train speech models from scratch. We use hosted STT, LLM and TTS models and focus on building agents
- Anyone looking for legal advice on call recording or telemarketing. The compliance lecture is a practical checklist, not legal counsel

## Verification output

```text
Objective  1: 128/160 OK
Objective  2: 127/160 OK
Objective  3: 104/160 OK
Objective  4: 131/160 OK
Objective  5:  98/160 OK
Objective  6:  99/160 OK
Objective  7: 133/160 OK
Objective  8:  97/160 OK
Objective  9: 104/160 OK
Objective 10: 114/160 OK
Description words: 969 (target >= 300) OK
```

Re-check after edits with: `python3 -c "import sys; [print(len(l.rstrip()), l.rstrip()) for l in open(sys.argv[1])]" objectives.txt`
