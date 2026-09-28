# Lecture Descriptions

> One Udemy lecture description for every item in `01-curriculum/curriculum.md` v1.1 (115 items: 89 video lectures, 7 labs, 1 challenge, 5 assignments/projects, 13 quizzes incl. the practice test). Paste into each lecture's **Description** field. Where the curriculum splits a long lecture into Part A / Part B uploads (5.3, 7.5, 8.2, 9.3, 13.2, 13.5), use the same description for both parts and add "Part A:" or "Part B:" at the start. Descriptions say what the student will do or learn. **No links, coupons or promotion** (Udemy rules; verify). The only exception is 15.3, the bonus lecture, and its links go in the lecture itself under Udemy's bonus-lecture rules.

> Type key: DM demo, SL slides, SC screencast, TH talking head/avatar, LAB lab, CE challenge (pause, then solution), QZ quiz/practice test, AS assignment/project.


## Section 1: Welcome and How Voice Agents Work

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 1.1 | Meet Riley: one call that works, one that fails, one that's fixed | DM | 5 | Hear three calls: Riley booking an appointment and transferring the caller, a naive agent talking over the caller and inventing availability, and the fixed agent passing its test suite. By Section 13, your agent handles the first call and passes the third call's tests. |
| 1.2 | What a voice agent actually is | SL | 7 | Learn what separates a voice agent from an IVR and a chatbot, and meet every component in the pipeline: transport, VAD, STT, turn detection, LLM, tools and TTS. For each one, you'll see where it tends to fail. |
| 1.3 | Cascaded vs speech-to-speech architectures | SL | 8 | Compare the cascaded STT→LLM→TTS pipeline with speech-to-speech models like OpenAI Realtime, and the half-cascade hybrid. You'll weigh control, cost, latency, voice quality and tool reliability. |
| 1.4 | The latency budget: why 800 ms is the magic number | SL | 8 | Break voice-to-voice latency into endpointing, STT, LLM time-to-first-token, TTS time-to-first-byte and network, and see why you should aim for under a second. Download the latency budget worksheet you'll fill in later in the course. |
| 1.5 | Course roadmap, repo tour and how to get help | SC | 7 | Tour the 15 sections, the voice-agents-course repo and its Makefile. You'll also learn how the labs work and how to ask questions in Q&A so you get fast, useful answers. |
| 1.6 | Quiz: Voice agent fundamentals | QZ | 4 | Eight questions that check you understand voice pipeline components, architectures and the latency budget. |

## Section 2: Setup: Accounts, Keys and Your Dev Environment

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 2.1 | Accounts you need and what they cost | SC | 8 | Set up the accounts you need (LiveKit Cloud, OpenAI, Deepgram, Cartesia and a Twilio trial) and see what the course will cost you. You'll also learn the difference between LiveKit Inference model strings and direct provider plugins. |
| 2.2 | Python project setup with uv | SC | 8 | Clone the repo, install it with uv (with a pip fallback), create your .env from .env.example and download the model files. The project is then ready for every lecture. |
| 2.3 | LiveKit CLI, projects and credentials | SC | 7 | Install the LiveKit CLI, authenticate, create a project and write your credentials to .env. Then confirm everything works with a single command. |
| 2.4 | Smoke test: unit tests and console mode | SC | 6 | Run the offline unit tests (no API keys needed), then talk to your first agent through your laptop mic in console mode. The lecture also covers common microphone and API key errors. |
| 2.5 | Lab 1: Environment verification | LAB | 3 | Work through the environment checklist to confirm your Python version, dependencies, keys, LiveKit connection and microphone before you build. |
| 2.6 | Quick win: run the finished Riley before you build it | SC | 6 | Talk to the finished capstone Riley in console mode before you write any code: book an appointment and trigger a transfer. You'll hear where the course ends up before you start building. |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | 6 | Set hard spending limits, check your free-tier minutes, and practise at zero cost with MOCK_MODE=1, which runs Riley on a scripted fake LLM with text input and output. You'll also learn to estimate a lab's cost before you run it. |

## Section 3: Your First Voice Agent with LiveKit Agents

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 3.1 | LiveKit mental model: rooms, participants, tracks, dispatch | SL | 8 | Learn LiveKit's building blocks: rooms, participants, audio tracks and dispatch. You'll see how an AgentServer registers with LiveKit and gets sent into a room when a caller joins. |
| 3.2 | AgentSession and Agent: the two core classes | SL | 7 | Understand the two core classes: Agent, which holds instructions, tools and per-agent model overrides, and AgentSession, the runtime that wires STT, LLM, TTS, VAD, turn handling and userdata together. |
| 3.3 | Code-along: hello Riley in 30 lines | SC | 10 | Code along to build hello Riley in about 30 lines: AgentServer, an rtc_session entrypoint, AgentSession with Deepgram, GPT-4.1 mini, Cartesia and Silero, and a spoken greeting. You'll run it in console mode. |
| 3.4 | Dev mode and the Agents Playground | DM | 6 | Run the agent in dev mode with hot reload, connect from the LiveKit Agents Playground and watch live transcripts as you talk to Riley. |
| 3.5 | Choosing STT, LLM and TTS providers | SL | 9 | Compare STT, LLM and TTS providers on accuracy, latency, price, voices and languages. You'll switch models through environment variables in src/maple/config.py, so a provider rename only means changing one line. |
| 3.6 | VAD, turn detection and interruptions | SL | 9 | Learn how Silero VAD, endpointing delays, the semantic turn detector, interruption settings and preemptive generation decide when Riley speaks and when it stops. |
| 3.7 | Tuning turn-taking live | DM | 5 | Change endpointing and interruption settings live and hear how Riley behaves differently. The lecture also covers the tuning mistakes that make agents interrupt or lag. |
| 3.8 | Lab 2: Customise your first agent | LAB | 4 | Swap Riley's voice, model and turn-taking settings, then write down how each change affects latency and how natural the conversation feels. |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | 7 | Hear five common failures before and after the fix: endpointing too short or too long, interruptions turned off, TTS reading markdown aloud, and the wrong STT model for accents or phone audio. Each one comes with the single setting that fixes it. |
| 3.10 | Quiz: First agent and turn-taking | QZ | 3 | Five questions on the LiveKit mental model, the core classes and turn-taking settings. |

## Section 4: Prompting for the Ear

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 4.1 | Why chat prompts fail on voice | SL | 7 | See why markdown, lists, long answers, URLs and emojis break text-to-speech, and why longer answers also increase latency. |
| 4.2 | Anatomy of a voice system prompt | SL | 8 | Take a voice system prompt apart: identity, goal, spoken style, output rules, tool policy, guardrails and escalation, as implemented in src/maple/prompts.py. |
| 4.3 | Numbers, dates, names and pronunciation | SC | 8 | Make Riley say phone numbers, dates, times and names correctly using grouping, spelled-out words, spelling confirmations and pronunciation hints. |
| 4.4 | Greetings, silence and "are you still there?" | SC | 7 | Add a natural greeting with on_enter, detect silence with user_away_timeout, and hang up gracefully when the caller stops responding. |
| 4.5 | Persona and brand voice without the cringe | TH | 5 | Design a warm, efficient persona that stays consistent and says clearly that it's an AI, without sounding cheesy. |
| 4.6 | Lab 3: Rewrite a chat prompt for voice | LAB | 5 | Rewrite a chat-style prompt for voice and score the before and after versions against a rubric. |
| 4.7 | Challenge: Riley for your business | AS | 3 | Rewrite Riley's instructions for a business you know using the business template, run it in console mode and post one transcript in Q&A. This is your first portfolio piece. |
| 4.8 | Quiz: Prompting for the ear | QZ | 2 | Five questions on writing prompts for voice: output rules, numbers and dates, greetings and silence handling. |

## Section 5: Tools: Booking, Rescheduling and Cancelling

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 5.1 | How function tools work in LiveKit | SL | 7 | Learn how @function_tool turns Agent methods into tools: docstrings become descriptions, typed arguments, RunContext, max_tool_steps, return values and ToolError. |
| 5.2 | The clinic scheduler: pure Python first | SC | 8 | Walk through the clinic scheduler and its unit tests, and see why keeping business logic in pure Python outside the agent makes it fast to test and safe to change. |
| 5.3 | Code-along: check availability and book | SC | 12 | Code along to build find_available_slots and book_appointment tools. You'll collect the caller's name, phone number, reason and preferred time before booking. |
| 5.4 | Confirmation and read-back patterns | SC | 8 | Have Riley read back the date, time and name before committing a booking, and handle corrections like "no, Thursday" smoothly. |
| 5.5 | Hiding latency while tools run | SC | 7 | Hide tool latency with context.with_filler and session.say, and block interruptions while a booking is being committed. |
| 5.6 | Reschedule, cancel and tool errors | SC | 9 | Add reschedule and cancel tools, raise ToolError with messages Riley can say out loud, and prompt the caller to retry cleanly after an error. |
| 5.7 | Session state with userdata | SC | 6 | Carry caller details across tools with a typed dataclass stored as AgentSession userdata and accessed through context.userdata. |
| 5.8 | Project 1: Booking agent | AS | 5 | Build and demo a booking agent that checks availability, books, reschedules and cancels, with read-backs. |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | 6 | Pause the video and build a join_waitlist tool from the spec on screen, then compare your version with the solution. The walkthrough covers the three mistakes most people make: a vague tool description, no read-back, and forgetting ToolError. |
| 5.10 | Quiz: Tools | QZ | 2 | Five questions on function tools, read-backs, filler speech, tool errors and session state. |

## Section 6: Speech-to-Speech with OpenAI Realtime

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 6.1 | How realtime speech models work | SL | 8 | Learn how realtime speech-to-speech models work: audio in and audio out, server VAD, voices, the transcription side channel and session limits. |
| 6.2 | Code-along: Riley on `gpt-realtime` | SC | 10 | Code along to rebuild Riley on gpt-realtime with openai.realtime.RealtimeModel, reusing the same booking tools and tuning turn detection. |
| 6.3 | Hybrid: realtime LLM with your own TTS | SC | 7 | Combine a realtime LLM in text mode with your own TTS, so you keep brand-consistent voices and control over pronunciation. |
| 6.4 | Head-to-head: cascaded vs realtime | DM | 10 | Play the same five test calls through the cascaded and realtime builds side by side so you can hear the difference, then compare latency, cost per minute, tool accuracy and interruptions. You'll finish by filling in the decision matrix. |
| 6.5 | Lab 4: Measure both architectures | LAB | 5 | Measure both architectures yourself and record the results on the comparison sheet. |
| 6.6 | Quiz: Architectures and tools | QZ | 2 | Eight questions on cascaded vs speech-to-speech trade-offs and on function tools. |

## Section 7: Knowledge and Multi-Agent Handoffs

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 7.1 | RAG for voice: short, speakable, grounded | SL | 7 | Adapt RAG for voice: retrieval as a tool vs pre-turn injection, short and speakable answers, and a reliable "I don't know". |
| 7.2 | Code-along: FAQ lookup tool | SC | 10 | Code along to connect the Maple Street FAQ retriever to a lookup_clinic_info tool, with grounding instructions that stop Riley inventing policies. |
| 7.3 | Scaling knowledge: vector stores and latency | SL | 6 | Learn when a vector database is worth its extra latency, and how caching and prefetching on turn completion keep answers fast. |
| 7.4 | Why split one agent into several | SL | 6 | Learn when to split one agent into specialists (prompt size, tool confusion, personas), and the trade-offs of handing off vs keeping a single agent. |
| 7.5 | Code-along: Greeter → Booking → Billing | SC | 12 | Code along to build Greeter → Booking → Billing handoffs with tools that return a new Agent, shared userdata, on_enter greetings and chat context that carries over. |
| 7.6 | Lab 5: Add an Insurance agent | LAB | 5 | Add an Insurance specialist to the handoff graph and route callers to it correctly. |
| 7.7 | Quiz: Knowledge and handoffs | QZ | 2 | Six questions on RAG for voice and multi-agent handoffs. |
| 7.8 | Multilingual Riley: Spanish and Hindi callers | SC | 8 | Support Spanish- and Hindi-speaking callers with STT language settings, the multilingual turn detector, a TTS voice per language and switching language mid-call. You'll also see what to test differently for each language. |

## Section 8: Telephony: Put Riley on a Phone Number

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 8.1 | PSTN, SIP and trunks in plain English | SL | 8 | Follow a phone call from the PSTN through a SIP trunk and LiveKit SIP into a room with your agent. You'll also see why 8 kHz audio affects your choice of STT model. |
| 8.2 | Inbound calls: Twilio trunk + LiveKit dispatch rule | SC | 12 | Buy a number, create a Twilio Elastic SIP trunk, and set up a LiveKit inbound trunk and dispatch rule, so Riley answers real calls. |
| 8.3 | Phone-specific tuning | SC | 7 | Tune Riley for phone lines: a telephony-suited STT model, noise handling, longer endpointing, and reading caller ID from SIP participant attributes. |
| 8.4 | Transfer to a human and ending calls | SC | 9 | Add a transfer_to_human tool using transfer_sip_participant, compare warm and cold transfers, and end calls cleanly. |
| 8.5 | Outbound calls: appointment reminders | SC | 10 | Place outbound appointment-reminder calls with explicit dispatch and a SIP participant created through the LiveKit API. You'll also plan what happens when voicemail picks up. |
| 8.6 | Compliance: disclosure, consent and recording | TH | 6 | Go through what to check before a voice agent talks to the public: AI disclosure, recording consent, TCPA, do-not-call and data retention. This is a practical checklist, not legal advice. |
| 8.7 | Project 2: Phone receptionist | AS | 3 | Put Riley on an inbound number that books appointments and transfers to a human, then submit a short demo. If you can't get a phone number in your country, there's a web client and SIP test path instead. |
| 8.8 | Quiz: Telephony | QZ | 2 | Five questions on SIP trunks, dispatch rules, phone tuning, transfers and outbound call compliance. |

## Section 9: Testing and Evaluating Voice Agents

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 9.1 | How voice agents fail in production | SL | 8 | Map how voice agents fail (mishearing, bad turn-taking, hallucinated availability, wrong tool arguments, missed escalation, latency spikes, injection) to the test that catches each one. |
| 9.2 | The voice testing pyramid | SL | 6 | Build the voice testing pyramid: unit tests, text-session behavior tests, LLM and WER evals, simulated calls and production monitoring. |
| 9.3 | Behavior tests with LiveKit's test framework | SC | 12 | Write behavior tests with LiveKit's test framework: run a text session, check the next event and grade the reply with an LLM judge, all in pytest-asyncio. |
| 9.4 | Asserting tool calls and arguments | SC | 10 | Assert that Riley calls the right tool with the right arguments, check tool outputs, skip optional messages, and check that nothing unexpected happens afterwards. |
| 9.5 | Mocking tools for deterministic tests | SC | 7 | Use mock_tools to force "no availability" and error paths, so you can test Riley's recovery without relying on luck. |
| 9.6 | LLM-as-judge with DeepEval on transcripts | SC | 9 | Score golden conversations with DeepEval conversational G-Eval for politeness, voice brevity, confirmation read-backs and correct escalation. |
| 9.7 | Measuring STT accuracy with WER | SC | 7 | Measure speech-to-text accuracy with word error rate, checking the course's pure-Python WER against jiwer and focusing on domain terms like drug names and surnames. |
| 9.8 | Latency testing against a budget | SC | 7 | Export metrics to JSONL, compute p50 and p95 for end-of-utterance delay, LLM TTFT and TTS TTFB, and fail the build when a stage goes over budget. |
| 9.9 | Simulated callers: agents testing agents | SC | 6 | Unleash LLM-driven caller personas (a confused senior, an impatient caller, an injection attacker) against Riley and let a judge grade how each call turned out. |
| 9.10 | Voice agent tests in CI | SC | 3 | Run unit tests on every push, and agent tests and evals when secrets are available, in GitHub Actions with report artifacts. |
| 9.11 | Project 3: Test suite for Riley | AS | 0 (text) | Write 15+ tests across the pyramid for Riley and submit the test report. |
| 9.12 | Quiz: Testing voice agents | QZ | 0 | Ten questions on voice failure modes, test types and the testing tools used in this section. |
| 9.13 | Audio-in tests: real caller audio through the pipeline | SC | 7 | Text tests miss speech-recognition errors. Run recorded caller audio (accents, phone noise, overlapping speech) through the STT node, check the transcripts against WER thresholds, then feed them into your behavior tests. |
| 9.14 | LiveKit Simulations: scenario-based caller testing at scale | DM | 6 | Use LiveKit's Simulation framework to run caller scenarios against the deployed agent, read the simulator's verdicts, and record your own verdict with on_simulation_end. This is a LiveKit Cloud feature, so check availability and pricing for your plan. |

## Section 10: Observability, Latency and Cost

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 10.1 | What to measure on every call | SL | 7 | Decide what to measure on every call: end-of-utterance delay, STT, LLM TTFT and tokens, TTS TTFB and characters, interruptions, tool latency and call outcome. |
| 10.2 | Collecting metrics and usage | SC | 9 | Collect metrics_collected events, log them, add up usage with UsageCollector and write a per-call summary to JSONL when the session shuts down. |
| 10.3 | Tracing with OpenTelemetry and Langfuse | SC | 10 | Send OpenTelemetry traces to Langfuse, with a span per turn and per tool, linked to transcripts. |
| 10.4 | Cost per minute: the number your boss will ask for | SC | 8 | Turn usage summaries into cost per minute with src/maple/costs.py, and compare where the money goes in the cascaded and realtime builds. |
| 10.5 | Dashboards and alerts that matter | SL | 6 | Choose the dashboard panels and alert thresholds that matter: p95 latency, cost per minute, transfer rate, containment rate and failed tool calls. |
| 10.6 | Lab 6: Build a call-quality report | LAB | 5 | Run ten calls and produce a call-quality report with latency percentiles and cost per minute. |
| 10.7 | Quiz: Observability and cost | QZ | 2 | Five questions on call metrics, tracing, cost per minute and alert thresholds. |

## Section 11: Security, Safety and Guardrails

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 11.1 | Threat model for voice agents | SL | 7 | Threat-model a phone agent: spoken prompt injection, social engineering, data exfiltration through tools, toll fraud and voice cloning. |
| 11.2 | Least-privilege tools and confirmation gates | SC | 8 | Scope tools to least privilege, verify caller identity before revealing appointments, and require a read-back before any irreversible action. |
| 11.3 | PII redaction in transcripts and logs | SC | 8 | Redact phone numbers, emails, dates of birth and card numbers from transcripts before they reach logs or traces, and set a retention policy. |
| 11.4 | Output guardrails and topic boundaries | SC | 7 | Keep Riley on topic with output checks in the llm_node and transcription_node hooks: refuse medical advice and escalate when a trigger fires. |
| 11.5 | Red-teaming Riley | DM | 5 | Attack Riley with injection personas from the simulated caller, fix what breaks and re-run the safety tests. |
| 11.6 | Quiz: Security | QZ | 3 | Eight questions on voice agent threats and defenses. |

## Section 12: Deploying to Production

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 12.1 | Agent server architecture and scaling | SL | 8 | Learn how agent servers scale: workers, job processes, idle processes, load thresholds, prewarming, draining and memory limits. |
| 12.2 | Dockerising the agent | SC | 8 | Write a multi-stage Dockerfile that downloads model files at build time, runs as a non-root user and starts the agent in production mode. |
| 12.3 | Deploy to LiveKit Cloud | SC | 10 | Deploy Riley to LiveKit Cloud with secrets, read the logs and roll back a bad release. |
| 12.4 | Self-hosting option | SL | 6 | See what self-hosting needs on any container host (Render, Fly.io, ECS or Kubernetes): outbound WebSocket, a health port and load-based autoscaling. |
| 12.5 | A web front end for Riley | SC | 8 | Connect the LiveKit React agent starter and a token server to your deployed Riley, so people can talk to it in a browser. |
| 12.6 | Production readiness checklist | SL | 6 | Go through production readiness: fallback models, timeouts, spoken error messages, graceful degradation and an on-call runbook. |
| 12.7 | Lab 7: Deploy and call your agent | LAB | 4 | Deploy your agent and confirm you can reach it from the web and by phone. |
| 12.8 | Chaos demo: kill a provider mid-call | DM | 5 | Revoke a provider key during a live call and watch the fallback provider take over with spoken error recovery. Then see what happens to the same call without fallbacks. |
| 12.9 | Quiz: Deployment | QZ | 2 | Five questions on agent server scaling, Docker, LiveKit Cloud deploys and production readiness. |

## Section 13: Capstone: Riley, Production Receptionist

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 13.1 | Capstone brief and architecture | SL | 6 | Review the capstone requirements, acceptance criteria and target architecture for production Riley. |
| 13.1a | Build it yourself first: the capstone gate | TH | 3 | Stop here and build the capstone yourself from the brief, time-boxed to one week. The lectures that follow are the reference solution, so check your work against them afterwards. |
| 13.2 | Reference solution: assembling the production agent | SC | 15 | Reference solution: combine prompts, tools, knowledge, handoffs, guardrails, telemetry and telephony into one production agent. Compare it with your own capstone build. |
| 13.3 | Hardening: fallbacks, timeouts, error speech | SC | 10 | Harden Riley with provider fallback lists, connection timeouts and spoken error recovery, so a provider outage doesn't end the call. |
| 13.4 | Full test run: unit → behavior → evals → simulated calls | SC | 12 | Run the whole suite from unit tests to simulated calls, read the report and fix a failing case live. |
| 13.5 | Deploy, call, observe | DM | 12 | Deploy production Riley, place real calls and watch the traces and cost per minute in real time. |
| 13.6 | Capstone submission and portfolio write-up | TH | 5 | Package your capstone for GitHub and LinkedIn with a README, a demo call recording and your test report. |
| 13.7 | Domain swap: ship Riley for a restaurant, salon or law office | AS | 4 | Re-skin the capstone for a restaurant, salon or law office with a new FAQ, tool schema and prompt, and adapt the existing tests. You'll finish with a second portfolio project that shows the skills transfer. |

## Section 14: Pipecat and Choosing Your Stack (optional)

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 14.1 | Pipecat's frame pipeline model | SL | 7 | Learn Pipecat's model of frames, processors, transports, Pipeline, PipelineTask, PipelineRunner and LLMContext. |
| 14.2 | Code-along: Riley booking flow in Pipecat | SC | 12 | Code along to rebuild Riley's booking flow in Pipecat with Deepgram, OpenAI, Cartesia, Silero VAD and FunctionSchema tools. |
| 14.3 | LiveKit Agents vs Pipecat vs managed platforms | SL | 8 | Compare LiveKit Agents, Pipecat and managed platforms (Vapi, Retell, ElevenLabs Agents, Bland) on control, cost, compliance and lock-in. |
| 14.4 | Quiz: Choosing a stack | QZ | 5 | Six questions on frameworks, managed platforms and choosing a stack. |

## Section 15: Wrap-up and Next Steps

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 15.1 | What you built and where to go next | TH | 5 | Recap what you built, then look at next steps: multilingual agents, avatars, outbound campaigns and the Build → Test → Operate course path. |
| 15.2 | Final practice test | QZ | 0 | A 40-question practice test across the whole course, with an explanation and a lecture reference for every answer. |
| 15.3 | Bonus lecture | TH | 5 | Bonus: where to go next, including the instructor's other courses and community, in line with Udemy's bonus lecture rules. |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | 8 | Look at the roles that hire for voice agent skills, work through 12 interview questions with model answers, and learn how freelancers scope and price a voice agent project. No salary figures. |

---

Coverage check: 115 descriptions for 115 curriculum items (script-verified: none missing, none extra; each is 1-2 sentences).
