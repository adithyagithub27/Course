# Slide Deck Outline

> Slide-by-slide outline for every section. Uses the scene kits K1-K7 from `10-graphics/design-system.md` (K1 Hook, K2 Title card, K3 Teaching slide, K4 Architecture diagram, K5 Code/demo, K6 Recap card, K7 Bridge). Design rules: ≤ 12 words per slide, one concept per slide, ≤ 15 visible code lines, Deep Navy background, Teal accent, Red only for failures, Amber only for warnings/latency markers.
>
> Curriculum v1.1. Every lecture opens with K1 → K2 and closes with K6 (3 bullets) → K7. The **last lecture of each section** also ends with a 10-second **"You can now..." card** (three abilities; see `recording-guide.md` §9). Examples are given for the main build sections below. These are listed once per section as "Standard open/close" and not repeated per lecture.
>
> Code slides use **only** the API forms in curriculum §6 and carry the corner note "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12".

---

## Master diagram list

| ID | Diagram | Used in | Type | Spec |
|---|---|---|---|---|
| D1 | **Voice pipeline** | 1.2, 3.1, promo, 13.1 | K4 | Left→right: Caller (person icon) → Transport (WebRTC / SIP) → **VAD** → **STT** → **Turn detection** → **LLM** (brain, teal) ⇄ **Tools** (wrench) → **TTS** → Transport → Caller. A failure badge (red dot) on each node appears in a second build step ("where each fails"). Arrows animate in sequence |
| D2 | **Cascaded vs speech-to-speech vs hybrid** | 1.3, 6.1, 6.3, 6.4 | K4 (3 rows) | Row 1: STT → LLM → TTS (three boxes). Row 2: one box "Realtime model (audio in/out)". Row 3: realtime model (text out) → your TTS. Right column: a comparison table (control, cost, latency, voice, tool reliability) with qualitative ticks, no numbers |
| D3 | **Latency budget waterfall** | 1.4, 9.8, 10.1, 13.5 | K4 / chart | A horizontal stacked waterfall from "caller stops speaking" (t=0) to "first agent audio": segments for endpointing/EOU, STT final, LLM TTFT, TTS TTFB, network. An amber vertical line at the target (student-set, e.g., 800 ms, labelled "example target"). Second build: a p95 bar overshooting in red |
| D4 | **Turn-taking timeline** | 3.6, 3.7, 4.4 | K4 | Two horizontal tracks (Caller, Agent) over time. Shows: caller speech → silence → VAD end → endpointing delay (min/max bracket) → turn detector decision → agent speech; then a caller interruption during agent speech → `min_duration` check → agent stops, or resumes on a false interruption. Preemptive generation is shown as a dashed early LLM start |
| D5 | **LiveKit mental model** | 3.1, 12.1 | K4 | LiveKit Cloud (SFU) with a room; participants (caller, agent); audio tracks; `AgentServer` registering and a dispatch arrow into the room; `@server.rtc_session()` entrypoint |
| D6 | **SIP call flow** | 8.1, 8.2, 8.4, 8.5 | K4 | Phone → PSTN → Twilio Elastic SIP trunk → LiveKit SIP (inbound trunk + dispatch rule) → Room → Riley (agent). Second build: transfer path (Riley → `transfer_sip_participant` → human's phone). Third build: outbound path (script → LiveKit API create SIP participant → trunk → PSTN → phone). Numbers shown only as `+1 555 01XX` |
| D7 | **Handoff graph** | 7.4, 7.5, 7.6 | K4 | Greeter → Booking, Greeter → Billing, with shared `userdata` as a cylinder underneath. Lab 5 adds an Insurance node (dashed, teal) |
| D8 | **Voice testing pyramid** | 9.2, 13.4, promo | K4 | Bottom→top: Unit (pure logic) → Behavior (text sessions) → Evals (LLM judges, WER) → Simulated calls → Production monitoring. Side annotations: speed, cost, needs keys?, runs in CI? |
| D9 | **Failure taxonomy map** | 9.1, 11.1 | K3 table | Failure → symptom → test type (from `10-resources/voice-failure-taxonomy.md`), in red/teal |
| D10 | **Observability dashboard** | 10.5, 10.6, 13.5 | K4 / mock-up | Six panels: p95 voice-to-voice latency (line + amber threshold), cost per minute (by stage), containment rate, transfer rate, failed tool calls, interruptions per call. Alert thresholds as amber lines; breaches in red |
| D11 | **Trace anatomy** | 10.3 | K4 | One call → turns → spans (STT, LLM, tool, TTS) as a Langfuse-style waterfall, with amber callouts on the slowest span |
| D12 | **Threat model** | 11.1 | K4 | Attacker (caller) → spoken injection / social engineering → Riley → tools/data. A shield at the tool boundary, identity verification gate, PII redaction before logs |
| D13 | **Agent server scaling** | 12.1, 12.4 | K4 | Agent server → job processes (idle pool, active), load threshold gauge, draining on deploy |
| D14 | **Capstone architecture** | 13.1, 13.2 | K4 | D1 + D6 + D7 + D10 combined: phone/web → LiveKit → Riley (handoffs, tools, knowledge, guardrails) → telemetry → Langfuse; CI box with the test pyramid |
| D15 | **Pipecat frame pipeline** | 14.1, 14.2 | K4 | transport.input → STT → user aggregator → LLM → TTS → transport.output → assistant aggregator, with frames flowing as small chips |
| D16 | **Build vs buy matrix** | 14.3 | K3 table | LiveKit Agents / Pipecat / Vapi / Retell / ElevenLabs Agents / Bland × control, cost model, compliance, lock-in (qualitative) |

---

## Section 1: Welcome and How Voice Agents Work

Standard open/close for each lecture.

**1.1 Meet Riley: works / fails / fixed (DM):** K1 cold open on call 1 (Riley books and transfers; waveform plus a transcript panel; number blurred) → K5 call 2, **naive agent** with a red overlay (talks over the caller, mishears the date, invents availability) → K5 call 3, fixed agent + test suite passing (pyramid results) → K3 "By Section 13, yours does call 1 and passes call 3's tests" → K7.
**1.2 What a voice agent actually is (SL):**
1. K1 "Is this a chatbot with a voice?"
2. K3 IVR vs chatbot vs voice agent (three columns, 3 words each)
3. K4 **D1** build step 1: the components
4. K4 **D1** build step 2: where each fails
5. K3 "Transport: WebRTC for apps, SIP for phones"
6. K6 recap
**1.3 Cascaded vs S2S (SL):** K4 **D2** row 1 → row 2 → row 3 → K3 trade-off table (qualitative) → K3 "We build both" → K6.
**1.4 Latency budget (SL):** K1 a 2-second silence with a timer → K3 "Humans take turns fast" → K4 **D3** stage by stage → K3 "Set a budget per stage" → K3 "Measure p95, not averages" → K5 worksheet preview → K6.
**1.5 Roadmap and repo tour (SC):** K3 the 15 sections as 5 arcs (Foundations / Useful / Real / Reliable / Ship) → K5 repo tree → K5 Makefile targets → K3 Q&A etiquette (lecture ID, OS, full error) → K6.

## Section 2: Setup

**2.1 Accounts and costs:** K3 account list (six logos **not** used; text labels only) → K3 "Inference strings vs plugins" → K3 budget "≈$10-20 total (check current pricing)" → K5 dashboards.
**2.2-2.4:** mostly K5; K3 "Never commit .env"; K3 troubleshooting table (mic permissions, missing key, wrong Python) from `10-resources/troubleshooting.md`.
**2.5 Lab 1:** K3 checklist slide.
**2.6 Quick win (SC):** K5 console with the capstone; K3 "This is where you're headed"; K3 build-log prompt (`BUILD_LOG.md`).
**2.7 Spending caps and mock mode (SC):** K3 "Three ways to never get a surprise bill" (caps, free tiers, `MOCK_MODE=1`); K5 masked provider limit screens; K3 cost estimate formula (minutes × cost/min).
**Section-end card:** "You can now: run Riley · run the tests offline · practise for free".

## Section 3: Your First Voice Agent

**3.1 LiveKit mental model (SL):** K4 **D5** in 4 builds (SFU → room → participants/tracks → dispatch) → K3 "Your code = an AgentServer" → K6.
**3.2 AgentSession and Agent (SL):** K3 Agent = instructions + tools + overrides → K3 AgentSession = the runtime → K5 code: the `AgentSession(...)` block from curriculum §6 (≤ 15 lines) → K3 `session.start(agent=..., room=ctx.room)` → K6.
**3.3 Hello Riley (SC):** K5 throughout; K3 "30 lines" count-up at the end.
**3.5 Choosing providers (SL):** K3 STT criteria → K3 LLM criteria → K3 TTS criteria → K5 `config.py` env vars → K3 "Swap providers in one line" → K6.
**3.6 VAD, turn detection, interruptions (SL):** K4 **D4** in builds: VAD → endpointing min/max → semantic turn detector → interruption → false-interruption resume → preemptive generation → K5 the `TurnHandlingOptions(...)` block → K6.
**3.7 Tuning live (DM):** K5 with a before/after split (design system 4.6).
**3.9 Break it (DM):** five pairs of K1 (failure, red, audio) → K5 (the one setting) → K3 AFTER (teal, audio): endpointing too short / too long / interruptions off / TTS reads markdown / wrong STT for accents and phone audio. **D4** callouts reused.
**Section-end card:** "You can now: run a voice agent · tune turn-taking · hear what's wrong".

## Section 4: Prompting for the Ear

**4.1 (SL):** K1 TTS reading a URL aloud (audio clip) → K3 "Markdown, lists, URLs, emojis" (red) → K3 "Longer output = more latency" → K6.
**4.2 (SL):** K3 seven blocks, revealed one per slide: identity, goal, style, output rules, tools policy, guardrails, escalation → K5 `prompts.py` → K6.
**4.3-4.4 (SC):** K5 + K3 before/after cards ("03/14" → "March fourteenth").
**4.5 (TH):** avatar + K3 "Warm, brief, honest: 'I'm an AI assistant'".

**4.7 Challenge (AS):** K3 "Riley for your business" brief; K3 `business-template.md` fields; K3 "Post one transcript in Q&A".
**Section-end card:** "You can now: write prompts for the ear · handle numbers and dates · handle silence".

## Section 5: Tools

**5.1 (SL):** K3 `@function_tool` anatomy (docstring → description; type hints → schema) → K5 signature `async def book(self, context: RunContext[CallState], ...)` → K3 `ToolError("speakable message")` → K3 return an `Agent` = handoff (preview) → K6.
**5.2-5.7 (SC):** K5; K4 slot-filling mini-diagram (name → phone → reason → time → read-back → commit) in 5.3/5.4; K4 a filler speech timeline in 5.5 (`with_filler` delay).

**5.9 Challenge (CE):** K3 spec card `join_waitlist(name, phone, preferred_day)` → full-screen **pause card** → K5 solution → K3 "Three common mistakes" (vague description, no read-back, no ToolError).
**Section-end card:** "You can now: give an agent tools · confirm before committing · recover from tool errors".

## Section 6: Speech-to-Speech with OpenAI Realtime

**6.1 (SL):** K4 **D2** row 2 zoom: audio in → model → audio out, transcription side channel → K3 session limits and voices → K6.
**6.2-6.3 (SC):** K5 `RealtimeModel(model="gpt-realtime", voice="marin")`; K4 **D2** row 3 for the hybrid.
**6.4 (DM):** K3 the five test calls → K5 results → K3 decision matrix summary → K6.

## Section 7: Knowledge and Multi-Agent Handoffs

**7.1 (SL):** K3 retrieval as a tool vs pre-turn injection (two columns) → K3 "Short, speakable, grounded" → K3 "'I don't know' is a feature" → K6.
**7.3 (SL):** K3 "When a vector DB is worth it" → K4 a latency mini-waterfall with the embedding call → K3 cache + prefetch → K6.
**7.4 (SL):** K3 prompt size / tool confusion / personas → K4 **D7** → K6.
**7.5 (SC):** K4 **D7** + K5.
**7.8 Multilingual Riley (SC):** K3 per-language settings table (STT language, turn detector, TTS voice); K5 `LANGUAGE` env; hear-it: the same FAQ answer in English, Spanish and Hindi; K3 "What to test differently".
**Section-end card:** "You can now: ground answers in a FAQ · hand off between agents · serve callers in more languages".

## Section 8: Telephony

**8.1 (SL):** K4 **D6** in builds → K3 "8 kHz audio: choose STT accordingly" → K3 codecs (one line) → K6.
**8.2-8.5 (SC):** K5 with OBS masks on all numbers/IDs; K4 **D6** transfer and outbound builds in 8.4 and 8.5.
**8.6 Compliance (TH):** avatar + K3 cards: AI disclosure / recording consent (one-party vs all-party) / TCPA outbound / DNC / retention / "Not legal advice" footer on every card.

## Section 9: Testing and Evaluating Voice Agents (signature)

**9.1 (SL):** K1 montage of failure clips → K3 **D9** failure-by-failure (8 slides, one failure each: mishearing, turn-taking, talking over, hallucinated availability, wrong tool args, missed escalation, latency spikes, injection) → K3 "Each failure → a test type" → K6.
**9.2 (SL):** K4 **D8** built bottom-up → K3 "What runs in CI" → K6.
**9.3-9.10 (SC):** K5; highlight the key 3-5 lines of each assertion; K3 green/red result cards with ✓/✗ glyphs (never color alone).
**9.8:** K4 **D3** overlaid with measured p50/p95.
**9.13 Audio-in tests (SC):** K4 audio file → STT node → transcript (WER check) → behavior test; K3 "Text tests miss STT errors".
**9.14 LiveKit Simulations (DM):** K3 scenario definition → K5 simulator verdicts → K5 `on_simulation_end` hook; corner flag "LiveKit Cloud feature: check availability".
**Section-end card:** "You can now: assert tool calls · measure WER and latency · run simulated callers in CI".

## Section 10: Observability, Latency and Cost

**10.1 (SL):** K3 the metrics list in three groups (speed / usage / outcome) → K4 **D3** mapped to metric names → K6.
**10.2-10.4 (SC):** K5; K4 **D11** in 10.3; K3 cost per minute formula in 10.4: Σ(stage usage × unit price) ÷ call minutes.
**10.5 (SL):** K4 **D10** panel by panel → K3 alert thresholds (amber) → K6.

## Section 11: Security

**11.1 (SL):** K4 **D12** → K3 five threats, one per slide (spoken injection, social engineering, exfiltration via tools, toll fraud, voice cloning) → K6.
**11.2-11.4 (SC):** K5; K3 "Verify identity before revealing appointments"; K3 "Irreversible = read-back".
**11.5 (DM):** K5 with red failure overlays → teal after the fix.

## Section 12: Deploying to Production

**12.1 (SL):** K4 **D13** → K3 prewarm with `AgentServer(setup_fnc=prewarm)` → K3 draining → K6.
**12.4 (SL):** K3 host options (Render, Fly.io, ECS, Kubernetes) → K3 requirements (outbound WebSocket, health port, load-based autoscaling) → K6.
**12.6 (SL):** K3 checklist slides grouped: fallbacks / timeouts / error speech / degradation / runbook → K3 `voice-agent-readiness-scorecard.md` preview → K6.
**12.8 Chaos demo (DM):** K1 the live call → K5 key revoked (key ID masked) → hear the fallback take over (teal) → the same call without fallbacks (red).
**Section-end card:** "You can now: containerise an agent · deploy to LiveKit Cloud · survive a provider outage".

## Section 13: Capstone

**13.1 (SL):** K3 requirements → K3 acceptance criteria → K4 **D14** → K6.
**13.1a Capstone gate (TH):** full-screen pause card: "Stop. Build it from the brief. Time box: one week." + scorecard as the acceptance check.
**13.2-13.5:** K5; K4 **D8** progress overlay in 13.4; K4 **D10** live in 13.5.
**13.6 (TH):** K3 portfolio checklist (README, demo recording with numbers masked, test report, architecture diagram).
**13.7 Domain swap (AS):** K3 three example businesses (restaurant, salon, law office) → K3 what changes (FAQ, tool schema, prompt) vs what stays (the tests) → `business-template.md`.
**Section-end card:** "You can now: ship a production voice agent · prove it with tests · adapt it to any business".

## Section 14: Pipecat and Choosing Your Stack

**14.1 (SL):** K4 **D15** → K3 `Pipeline`, `PipelineTask`, `PipelineRunner`, `LLMContext` (one per slide) → K6.
**14.3 (SL):** K3 **D16** row by row → K3 "Build when… / Buy when…" → K6.

## Section 15: Wrap-up

**15.1 (TH):** K3 "What you built" montage → K3 next steps (multilingual, avatars, outbound campaigns) → K3 Build → Test → Operate path (course names only; promotional detail only in 15.3).
**15.3 Bonus (TH):** only lecture with course links/coupons (Udemy bonus rules; verify).
**15.4 Careers (TH):** K3 role titles → K3 interview question examples (from `interview-questions.md`) → K3 scoping a client build (discovery, per-minute cost, setup fee vs retainer) → no salary figures.

---

## Slide count estimate

| Section | SL lectures | Est. slides (incl. open/close) |
|---|---|---|
| 1 | 3 (+DM/SC framing) | 45 |
| 2 | 0 | 15 |
| 3 | 4 | 50 |
| 4 | 2 (+TH) | 30 |
| 5 | 1 | 35 |
| 6 | 1 | 25 |
| 7 | 3 | 35 |
| 8 | 1 (+TH) | 35 |
| 9 | 2 | 60 |
| 10 | 2 | 35 |
| 11 | 1 | 25 |
| 12 | 3 | 35 |
| 13 | 1 (+TH) | 25 |
| 14 | 2 | 20 |
| 15 | 0 (+TH) | 10 |
| **Total** | 26 | **≈ 480** (v1.0 planning estimate; add ≈ 60 for the v1.1 lectures and 14 section-end cards, ≈ 540) |
