# Slide Deck Outline

> Slide-by-slide map for every lecture. Uses the scene kits K1-K7 from `10-graphics/design-system.md` at the repo root (K1 Hook, K2 Title card, K3 Teaching slide, K4 Architecture diagram, K5 Code/demo, K6 Recap card, K7 Bridge). Design rules: ≤ 12 words per slide, one concept per slide, ≤ 15 visible code lines, Deep Navy background, Teal accent, Red only for failures, Amber only for warnings/latency markers.
>
> **The scripts are the slide text.** Every `[SLIDE n: title]` cue in `02-lecture-scripts/` carries the exact title and bullets (or table, or diagram layout). `tools/slide_builder.py` turns those cues into the section decks (see `video-generation-plan.md` §4.4). This outline does not repeat the bullets; it says which scene kit each cue uses, where the master diagrams D1-D16 appear, and what the editor adds around the cues. If this outline and a script disagree, the script wins.
>
> Code slides use **only** the API forms in curriculum §6 and carry the corner note "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12".

---

## Standard open and close (every lecture)

Every video lecture opens with K1 → K2 and closes with K6 → K7. These are listed once here and not repeated per lecture.

| Card | Source | Rule |
|---|---|---|
| K1 Hook | The lecture's first `[AVATAR]` line, or the first `[DEMO]`/`[B-ROLL]` cue when the lecture opens on a failure | 1 bold sentence, max 8 words |
| K2 Title card | Lecture title and the first learning objective from the lecture's field table | Section badge top right |
| **K6 Recap card** | **The three bullets of the lecture's `[SLIDE n: Recap]` cue**, which sits immediately before the spoken recap (decision A1 in `14-quality-review/2026-10-01-fix-plan.md`) | Exactly three bullets, each under 10 words; read aloud. Do not write recap bullets in the edit: if a lecture has no `[SLIDE n: Recap]` cue, send it back to the script owner. Quiz, lab and assignment intros are exempt |
| **Section-end "You can now" card** | **The three abilities in the `[SLIDE n: You can now]` cue** in the last video lecture of each section, placed before the bridge (decision A2) | 10 seconds, K6 style, screenshot-friendly: large text, course name in small type, no URLs. Pair with the spoken build-log prompt (`recording-guide.md` §9) |
| K7 Bridge | The lecture's `Transition` line | "Next up:" + next lecture title + one-line teaser |

The section-end wording suggested per section below is only a fallback for review; the script's `[SLIDE n: You can now]` cue is the text that ships.

---

## Master diagram list

Every master diagram is one SVG file in `voice-ai-agents-course/10-graphics/diagrams/`, named `D{n}-{slug}.svg` (decision A7). Lectures that cue a diagram either use the whole file or one of its build steps.

### Drawing rules for all 16 diagrams

| Property | Value (from `10-graphics/design-system.md`) |
|---|---|
| Canvas | `viewBox="0 0 1920 1080"`, background Deep Navy `#0A1628`, 5% padding on all sides; title top left in Inter Bold 40 px, White |
| Nodes | Rounded rectangles, 8 px radius, fill Navy Light `#1A2742`, 2 px stroke. Stroke colour by role: Teal `#00D4AA` for the agent, LLM and active path; White `#FFFFFF` for people and tools; Cool Gray `#94A3B8` for infrastructure, data stores (cylinders) and inactive paths |
| Labels | Node name Inter SemiBold 24 px White; one-line description Inter Regular 18 px Cool Gray `#94A3B8` under the name; code identifiers in JetBrains Mono 18 px |
| Arrows | 2 px, White at 60% opacity for data flow; 3 px Teal for the highlighted path; chevron heads; dashed (8 4) for optional or "added later" paths |
| Status colours | Red `#FF4B4B` only for failures (badges, failing bars, attacker); Amber `#FFB020` only for latency, thresholds and warnings; never decorative |
| Text limit | ≤ 12 words of prose per diagram outside node labels; no numbers that are not in the spec below |
| Builds | Each build step is a separate top-level group `<g id="build-1">`, `<g id="build-2">`, ... in the same file. A static export shows every group; the editor reveals them in order |
| Accessibility | Never colour alone: failures also get a ✗ glyph, passes a ✓ glyph |

### The 16 diagrams

| ID | File | Diagram | Used in | Kit | Complete spec (nodes, labels, arrows, colours, builds) |
|---|---|---|---|---|---|
| D1 | `D1-voice-pipeline.svg` | **Voice pipeline** | 1.2, 3.1, promo, 13.1 | K4 | Title "The voice pipeline". One horizontal row, left to right, nine nodes: **Caller** (person icon, White stroke) → **Transport** "WebRTC / SIP" (Gray) → **VAD** "Is someone speaking?" → **STT** "Speech to text" → **Turn detection** "Are they done?" → **LLM** "Decide what to say" (brain icon, Teal stroke) → **TTS** "Text to speech" → **Transport** (Gray) → **Caller**. **Tools** (wrench, White stroke) sits directly under LLM with a two-way arrow LLM ⇄ Tools labelled "act on the world". Pipeline nodes VAD/STT/Turn/TTS have Gray stroke. Arrows White 60%. build-1: the row and Tools. build-2: a small Red dot with ✗ on each of VAD, STT, Turn detection, LLM, Tools, TTS, each with a short Cool Gray caption underneath: "misses quiet speech", "mishears names", "cuts caller off", "invents availability", "wrong arguments", "reads symbols aloud" |
| D2 | `D2-cascaded-vs-s2s-vs-hybrid.svg` | **Cascaded vs speech-to-speech vs hybrid** | 1.3, 6.1, 6.3, 6.4 | K4 (3 rows) | Title "Three architectures". Three stacked rows, each starting with "Audio in" (White) and ending with "Audio out" (White). Row 1 label "Cascaded": STT → LLM (Teal) → TTS, with the text "text" on the two inner arrows. Row 2 label "Speech-to-speech": one wide Teal node "Realtime model: hears, thinks, speaks". Row 3 label "Half-cascade (hybrid)": "Realtime model (text out)" (Teal) → "Your TTS" (White stroke). Right column (30% width): a 5×3 table, columns Cascaded / S2S / Hybrid, rows Control, Cost, Latency, Voice choice, Tool reliability, filled with qualitative glyphs only (●●●, ●●, ●) in Teal; no numbers. build-1 row 1, build-2 row 2, build-3 row 3, build-4 the table. 6.1 uses build-2 alone, zoomed, with a dashed Gray side arrow "transcription side channel" from Audio in to a small "Transcript" node |
| D3 | `D3-latency-budget-waterfall.svg` | **Latency budget waterfall** | 1.4, 9.8, 10.1, 13.5 | K4 / chart | Title "Where the time goes". Horizontal axis 0 to 1,200 ms, Gray ticks every 200 ms, origin labelled "caller stops speaking", end labelled "caller hears first audio". One stacked bar, six segments left to right with labels above and ms below (lecture 1.4 slide 9 example values): Network in 40, Endpointing 250, STT final 80, LLM TTFT 280, TTS TTFB 110, Network out 40 (total 800). Segment fills alternate Teal and Teal Dim `#00A885`. Amber vertical line at 800 ms labelled "example target". Footer in Cool Gray: "Example numbers for illustration". build-1 the axis, build-2 the segments one by one, build-3 the Amber target line, build-4 a second thin bar underneath labelled "slow turn (p95)" that runs past the target line, with the part past 800 ms in Red and a ✗ (no ms value printed; it illustrates "measure p95, not averages") |
| D4 | `D4-turn-taking-timeline.svg` | **Turn-taking timeline** | 3.6, 3.7, 4.4 | K4 | Title "One turn, on a timeline". Two horizontal tracks over a time axis: **Caller** (top) and **Riley** (bottom). build-1: caller speech block "I'd like to book for…", a 400 ms gap, then "…Thursday morning." Under the track a VAD row: speech / silence / speech / silence (White blocks vs Gray). build-2: at the first gap a Gray bubble "Turn detector: unlikely finished → keep waiting"; at the final silence a Teal bubble "likely finished → wait min_delay"; an Amber bracket from end of speech to end of turn labelled "end-of-utterance delay", with a `min_delay`/`max_delay` bracket pair above it. build-3: Riley speech block starts after the bracket. build-4: a caller block overlaps Riley's speech ("no, wait"), a small `min_duration` bracket, then Riley's block ends early (Teal ✓ "agent stops"); a dashed alternative shows Riley resuming, labelled "false interruption → resume". build-5: a dashed Teal block on the Riley track starting before the end of turn, labelled "preemptive generation" |
| D5 | `D5-livekit-mental-model.svg` | **LiveKit mental model** | 3.1, 12.1 | K4 | Title "Rooms, participants, tracks, dispatch". Centre: large Gray node "LiveKit server (SFU)" containing a dashed rectangle "Room". build-1: three participants around it: "Caller's browser" (White), "Phone via SIP" (White), "Riley (agent)" (Teal); each has one up arrow (publish) and one down arrow (subscribe) to the SFU. build-2: small track chips on the arrows: "mic track", "Riley's audio track", "transcript (text)". build-3: left side, "Agent server (`AgentServer`)" (Teal) with an outbound arrow labelled "WebSocket: I'm available" to the SFU; numbered Teal circles 1-5 for the dispatch steps (server connects out, caller joins room, LiveKit dispatches job, job process runs `@server.rtc_session()` entrypoint with `JobContext`, `AgentSession` starts and Riley speaks). build-4: the job process node is linked to "Riley (agent)" in the room |
| D6 | `D6-sip-call-flow.svg` | **SIP call flow** | 8.1, 8.2, 8.4, 8.5 | K4 | Title "The call path". build-1 (inbound), left to right: "Caller's phone" (White) → "PSTN" (Gray) → "Twilio Elastic SIP trunk" (Gray) → "LiveKit SIP (inbound trunk + dispatch rule)" (Gray) → "Room call-…" (dashed) → "Riley (riley-receptionist)" (Teal). Under the trunk node, Cool Gray caption "8 kHz narrowband audio". Numbers appear only as `+1 555 01XX`. build-2 (transfer): from Riley a Teal arrow labelled `transfer_sip_participant` back through LiveKit SIP and Twilio to "Front desk phone" (White). build-3 (outbound): a new left node "s08_outbound_call.py" (White) → "LiveKit API: create SIP participant" → "outbound trunk" → PSTN → "Patient's phone", dashed Teal |
| D7 | `D7-handoff-graph.svg` | **Handoff graph** | 7.4, 7.5, 7.6 | K4 | Title "Riley's team". build-1: centre node "GreeterAgent" (Teal) with caption "greets, answers FAQ, routes"; right-up "BookingAgent" caption "book, reschedule, cancel"; right-down "BillingAgent" caption "insurance, payments, prices". Solid arrows Greeter → Booking and Greeter → Billing; thin return arrows back to Greeter. build-2: a Gray cylinder underneath all three labelled "`CallState` (userdata): name, phone, appointment, handoff history", with dotted lines to each agent. build-3 (Lab 5): a dashed Teal node "InsuranceAgent" with a dashed arrow from Greeter, labelled "Lab 5" |
| D8 | `D8-voice-testing-pyramid.svg` | **Voice testing pyramid** | 9.2, 13.4, promo | K4 | Title "The voice testing pyramid". Five horizontal layers, widest at the bottom, built bottom-up (build-1 to build-5): 1 "Unit tests: pure Python, no network" `tests/unit/`; 2 "Behavior tests: text sessions, real LLM" `tests/agent/`; 3 "Evals: LLM judges, WER, latency budgets" `tests/evals/`; 4 "Simulated calls: LLM caller vs Riley; LiveKit Simulations"; 5 "Production monitoring: metrics, traces, alerts". Layer fills Navy Light with Teal stroke; folder names in JetBrains Mono. Right of each layer a badge row in Cool Gray: speed (fast → slow), cost ($ → $$$), "needs keys?" (no for layer 1, yes above), "runs in CI?" (always / when secrets exist / scheduled). 13.4 overlay: a ✓ glyph appears on each layer as its run passes |
| D9 | `D9-failure-test-map.svg` | **Failure → test map** | 9.1, 11.1 | K3 table | Title "Failure → test map". Three columns: Failure (Red ✗ glyph + text), Primary test (Teal ✓ glyph + text), Lecture (Cool Gray). Eight rows, exactly as 9.1 slide 5: Mishearing / WER eval, audio-in tests / 9.7, 9.13; Wrong turn-taking / EOU delay budget, audio simulations / 9.8, 9.14; Talking over callers / interruption tests (audio), monitoring / 9.14, 10.5; Hallucinated availability / tool-order assertion + mocks / 9.4, 9.5; Wrong tool arguments / argument assertions + state checks / 9.4; Missed escalation / behavior test + judge + simulated caller / 9.4, 9.6, 9.9; Latency spikes / p95 budget in CI / 9.8; Prompt injection / simulated attacker, safety tests / 9.9, 11.5. One build per row |
| D10 | `D10-observability-dashboard.svg` | **Observability dashboard** | 10.5, 10.6, 13.5 | K4 / mock-up | Title "The five numbers". Five tiles in one row (10.5 slide 1 and its B-ROLL), each with a big value, a label and a Teal sparkline: "p95 latency 1.47 s" (per hour; Amber threshold line at 1.6 s on the sparkline), "Cost/min 7.7¢" (per day), "Transfers 14%" (per day), "Contained 71%" (per day), "Tool failures 0.4%" (per hour). Footer in Cool Gray: "Illustrative values". build-1 to build-5 one tile each; build-6 the latency tile turns Red with ✗ and an "ALERT: > 1.6 s for 30 min" Amber label |
| D11 | `D11-trace-anatomy.svg` | **Trace anatomy** | 10.3 | K4 | Title "One call, as a trace". A Langfuse-style waterfall: top bar `agent_session` (full width, Gray). Under it alternating `user_turn` and `agent_turn` bars. One `agent_turn` expanded into child bars: `eou_detection`, `llm_node` → `llm_request`, `function_tool` (e.g. `find_available_slots`), `tts_node` → `tts_request`. Bars Teal; the slowest child (`function_tool`) in Amber with a callout "slowest span". Left margin shows span names in JetBrains Mono; right margin durations in Cool Gray. A small key at the bottom: "room name `call-…` links trace, logs and metrics". build-1 session + turns, build-2 expanded children, build-3 Amber callout |
| D12 | `D12-threat-model.svg` | **Threat model** | 11.1 | K4 | Title "Five threats, layered defences". Left: "Caller (anyone with the number)" in Red stroke. Arrow into "STT" (Gray) → "Riley (LLM)" (Teal) → a vertical shield line (Red shield icon) → "Tools" (White) → "Scheduler / patient data" (Gray cylinder). Threat labels as Red chips on the arrows: 1 "spoken injection" (into STT), 2 "social engineering" (into Riley), 3 "exfiltration via tools" (Riley → Tools), 4 "toll fraud" (Tools → "Transfer / dial" node), 5 "voice cloning" (on the caller). Defence labels as Teal chips at the shield: "identity check in code", "least-privilege tools", "allow-listed transfer target". A Gray node "Logs and traces" fed from Riley through a Teal gate "PII redaction". One build per threat, then the defences |
| D13 | `D13-agent-server-scaling.svg` | **Agent server scaling** | 12.1, 12.4 | K4 | Title "The agent server". Left: "LiveKit (Cloud or self-hosted)" (Gray). Two-way arrow labelled "WebSocket (outbound)" to "Agent server, main process" (Teal). build-1: under the main process, three Teal "job process (one call)" boxes and two Gray "idle warm process" boxes labelled `num_idle_processes`, with `setup_fnc` (prewarm) noted on the idle boxes. build-2: a gauge "load" with an Amber mark at 0.7 labelled `load_threshold`; past it a Gray label "stops accepting new jobs". build-3: a memory chip on one job process "`job_memory_warn_mb` 1000 MB" (Amber). build-4: "SIGTERM → draining" banner: job boxes stay Teal, new-job arrow crossed out in Gray, caption "`drain_timeout` 3600 s". 12.4 reuses build-1 with "any container host" replacing the LiveKit Cloud label |
| D14 | `D14-capstone-architecture.svg` | **Capstone architecture** | 13.1, 13.2 | K4 | Title "Riley in production". Left column callers: "Phone" → "Twilio SIP trunk" → "LiveKit SIP + dispatch rule (`riley-receptionist`)" → "Room"; "Web user" → "WebRTC" → same Room. Centre: "Agent server (Docker, `start`)" (Teal) containing "`AgentSession`: VAD + turn detector + STT → LLM → TTS, fallbacks + `conn_options`". Inside the session, "Riley (front desk + booking, guardrails)" ⇄ "Billing specialist", both over a "`CallState`" cylinder. Right: "Tools" → "`src/maple`: scheduler, knowledge, pii, costs" (Gray cylinder); "Transfer → front desk (config number only)" (White). Bottom right: "Telemetry: metrics JSONL, usage and cost, OpenTelemetry → Langfuse (redacted)" (Amber trace icon). Bottom band: "CI: unit → behavior → evals → simulated callers, gating deploys" with a small D8 pyramid icon. Builds: callers, agent server, agents and tools, telemetry, CI |
| D15 | `D15-pipecat-frame-pipeline.svg` | **Pipecat frame pipeline** | 14.1, 14.2 | K4 | Title "Frames through a pipeline". One row: `transport.input()` → `stt` (DeepgramSTTService) → `user aggregator` → `llm` (OpenAILLMService, Teal) → `tts` (CartesiaTTSService) → `transport.output()` → `assistant aggregator`. Small chips travel on the arrows: "AudioRawFrame", "TranscriptionFrame", "LLM context", "TextFrame", "TTSAudioRawFrame". Under the row, a dashed rectangle around all processors labelled `Pipeline`, an outer rectangle labelled `PipelineWorker` (`PipelineParams`), and an outermost one labelled `WorkerRunner`. Cool Gray footnote: "1.12 names; older tutorials: PipelineTask, PipelineRunner". A Gray cylinder `LLMContext` feeds both aggregators. Builds: row, chips, the three containers |
| D16 | `D16-build-vs-buy-matrix.svg` | **Build vs buy matrix** | 14.3 | K3 table | Title "Build vs buy". The 14.3 slide 6 table: columns "Framework, self-hosted" / "Framework, managed hosting" / "Managed platform"; rows Time to first call (Slowest / Medium / Fastest), Pipeline control (Full / Full / Limited to exposed options), Cost at low volume (Engineering time dominates / Engineering time dominates / Usually lowest total), Cost at high volume (Usually lowest per minute / Low to medium / Platform fee adds up), Compliance control (You own it all / Shared with the host / Depends on the vendor), Lock-in (Lowest / Low / Highest), Testing depth (Anything you build / Anything you build / Limited to what the platform exposes). Header row Teal text; cells White; one build per row. A Cool Gray caption under the first two columns "LiveKit Agents, Pipecat" and under the third "Vapi, Retell, ElevenLabs Agents, Bland" |

---

## Generic intro template: labs, assignments, challenges and quizzes

Lab, assignment and quiz intros (2.5, 3.8, 4.6, 4.7, 5.8, 6.5, 7.6, 8.7, 9.11, 10.6, 12.7, 13.7 and every quiz intro) use one short template instead of a per-lecture outline. A1 exempts them from the recap card; the section-end "You can now" card still applies when the intro is the last video of its section.

| Step | Lab / assignment / challenge intro | Quiz intro |
|---|---|---|
| 1 | K1 hook: one line from the script's opening (a failure, a number or a question) | K1 hook: the script's one-line hook |
| 2 | K2 title card: lab or project name + **time estimate from the lab or project file header** (V3) | K2 title card: quiz name + number of questions |
| 3 | K3 "What you'll produce": the "You will produce" / deliverables row of the lab or project file | K3 topics covered (from the quiz file's "Covers" row) |
| 4 | K3 the step names (3-5 words each), taken from the file's `## Step n` headings | (none) |
| 5 | K3 checkpoint or submission: where to post, what counts as done | K3 "Retake until 100%; explanations link to lectures" |
| 6 | K7 bridge | K7 bridge |

Time estimates shown on step 2 (source of truth: the file headers):

| Lecture | File | Time on the card |
|---|---|---|
| 2.5 | `04-labs/lab-01-environment.md` | 45 minutes |
| 3.8 | `04-labs/lab-02-first-agent.md` | 60 minutes |
| 4.6 | `04-labs/lab-03-voice-prompting.md` | 45 minutes |
| 4.7 | `05-projects/challenges.md` (4.7) | 45 to 90 minutes |
| 5.8 | `05-projects/project-1-booking-agent.md` | 3 to 5 hours |
| 6.5 | `04-labs/lab-04-realtime-vs-cascaded.md` | 75 minutes |
| 7.6 | `04-labs/lab-05-handoffs.md` | 60 minutes |
| 8.7 | `05-projects/project-2-phone-receptionist.md` | 3 to 6 hours |
| 9.11 | `05-projects/project-3-test-suite.md` | 4 to 6 hours |
| 10.6 | `04-labs/lab-06-observability.md` | 75 minutes |
| 12.7 | `04-labs/lab-07-deploy.md` | 90 minutes |
| 13.7 | `05-projects/challenges.md` (13.7) | 6 to 12 hours |

The 5.9 challenge (CE) is a full lecture with its own entry below.

---

## Section 1: Welcome and How Voice Agents Work

**1.1 Meet Riley: works / fails / fixed (DM):** K1 cold open on call 1 (Riley books and transfers; waveform plus a transcript panel; number blurred) → K5 call 2, **naive agent** with a red overlay (talks over the caller, mishears the date, invents availability) → K5 call 3, fixed agent + test suite passing (**D8** results overlay) → K3 "By Section 13, yours does call 1 and passes call 3's tests" → K6 → K7.
**1.2 What a voice agent actually is (SL):**
1. K1 "Is this a chatbot with a voice?"
2. K3 IVR vs chatbot vs voice agent (three columns, 3 words each)
3. K4 **D1** build-1: the components
4. K4 **D1** build-2: where each fails
5. K3 "Transport: WebRTC for apps, SIP for phones"
6. K6 recap
**1.3 Cascaded vs S2S (SL):** K4 **D2** build-1 → build-2 → build-3 → K3 trade-off table (D2 build-4, qualitative) → K3 "We build both" → K6.
**1.4 Latency budget (SL):** K1 a 2-second silence with a timer → K3 "Humans take turns fast" → K4 **D3** stage by stage → K3 "Set a budget per stage" → K3 "Measure p95, not averages" → K5 worksheet preview → K6.
**1.5 Roadmap and repo tour (SC):** K3 the 15 sections as 5 arcs (Foundations / Useful / Real / Reliable / Ship) → K5 repo tree → K5 Makefile targets → K3 Q&A etiquette (lecture ID, OS, full error) → K6.
**1.6 Quiz intro:** generic template.

## Section 2: Setup

**2.1 Accounts and costs (SC):** K3 account list (six logos **not** used; text labels only) → K3 "Inference strings vs plugins" → K3 budget "≈$10-20 total (check current pricing)" → K5 dashboards.
**2.2-2.4 (SC):** mostly K5; K3 "Never commit .env"; K3 troubleshooting table (mic permissions, missing key, wrong Python) from `10-resources/troubleshooting.md`.
**2.5 Lab 1:** generic template.
**2.6 Quick win (SC):** K5 console with the capstone; K3 "This is where you're headed"; K3 build-log prompt (`BUILD_LOG.md`).
**2.7 Spending caps and mock mode (SC):** K3 "Three ways to never get a surprise bill" (caps, free tiers, `MOCK_MODE=1`); K5 masked provider limit screens; K3 cost estimate formula (minutes × cost/min).
**Section-end card (fallback wording):** "You can now: run Riley · run the tests offline · practise for free".

## Section 3: Your First Voice Agent

**3.1 LiveKit mental model (SL):** K4 **D5** in 4 builds (SFU → tracks → dispatch → job process) → K3 "Your code = an AgentServer" → K6.
**3.2 AgentSession and Agent (SL):** K3 Agent = instructions + tools + overrides → K3 AgentSession = the runtime → K5 code: the `AgentSession(...)` block from curriculum §6 (≤ 15 lines) → K3 `session.start(agent=..., room=ctx.room)` → K6.
**3.3 Hello Riley (SC):** K5 throughout; K3 "30 lines" count-up at the end.
**3.4 Dev mode and the Agents Playground (DM):** K3 slide 1 "console vs dev vs start" (three rows) → K5 terminal: `dev` running, "registered" log line highlighted → K5 browser: Agents Playground connect, mic permission, Riley greets, transcript panel highlighted → K5 `lk room list` showing one room with two participants → K5 split editor/terminal: greeting edited, server reload line highlighted → K5 reconnect, new Saturday greeting heard → K3 slide 2 "Your development loop" (five numbered steps) → K6.
**3.5 Choosing providers (SL):** K3 STT criteria → K3 LLM criteria → K3 TTS criteria → K5 `config.py` env vars → K3 "Swap providers in one line" → K6.
**3.6 VAD, turn detection, interruptions (SL):** K4 **D4** in builds: VAD → endpointing min/max → semantic turn detector → interruption → false-interruption resume → preemptive generation → K5 the `TurnHandlingOptions(...)` block → K6.
**3.7 Tuning live (DM):** K5 with a before/after split (design system 4.6); **D4** callouts reused.
**3.8 Lab 2:** generic template.
**3.9 Break it (DM):** five pairs of K1 (failure, red, audio) → K5 (the one setting) → K3 AFTER (teal, audio): endpointing too short / too long / interruptions off / TTS reads markdown / wrong STT for accents and phone audio. **D4** callouts reused.
**3.10 Quiz intro:** generic template.
**Section-end card (fallback wording):** "You can now: run a voice agent · tune turn-taking · hear what's wrong".

## Section 4: Prompting for the Ear

**4.1 (SL):** K1 TTS reading a URL aloud (audio clip) → K3 "Markdown, lists, URLs, emojis" (red) → K3 "Longer output = more latency" → K6.
**4.2 (SL):** K3 seven blocks, revealed one per slide: identity, goal, style, output rules, tools policy, guardrails, escalation → K5 `prompts.py` → K6.
**4.3-4.4 (SC):** K5 + K3 before/after cards ("03/14" → "March fourteenth"); 4.4 reuses **D4** for the silence timer.
**4.5 (TH):** avatar + K3 "Warm, brief, honest: 'I'm an AI assistant'".
**4.6 Lab 3, 4.7 Challenge (AS), 4.8 Quiz intro:** generic template. 4.7 step 3 card: "Riley for your business" brief, `business-template.md` fields, "Post one transcript in Q&A".
**Section-end card (fallback wording):** "You can now: write prompts for the ear · handle numbers and dates · handle silence".

## Section 5: Tools

**5.1 (SL):** K3 `@function_tool` anatomy (docstring → description; type hints → schema) → K5 signature `async def book(self, context: RunContext[CallState], ...)` → K3 `ToolError("speakable message")` → K3 return an `Agent` = handoff (preview) → K6.
**5.2-5.7 (SC):** K5; K4 slot-filling mini-diagram (name → phone → reason → time → read-back → commit) in 5.3/5.4; K4 a filler speech timeline in 5.5 (`with_filler` delay).
**5.8 Project 1:** generic template.
**5.9 Challenge (CE):** K3 spec card `join_waitlist(patient_name, phone, preferred_day)`, backed by `add_to_waitlist` and `waitlist_position` (the signature in `agents/s05_booking_agent.py`) → K5 `scheduler.py` `add_to_waitlist` docstring → full-screen **pause card** with countdown → K5 solution from `agents/s05_booking_agent.py` → K3 "Three common mistakes" (vague description, no read-back, no ToolError) → K6.
**5.10 Quiz intro:** generic template.
**Section-end card (fallback wording):** "You can now: give an agent tools · confirm before committing · recover from tool errors".

## Section 6: Speech-to-Speech with OpenAI Realtime

**6.1 (SL):** K4 **D2** build-2 zoom: audio in → model → audio out, transcription side channel → K3 session limits and voices (limits from the script's slide; values flagged "verify") → K6.
**6.2-6.3 (SC):** K5 `RealtimeModel(model="gpt-realtime", voice="marin")`; K4 **D2** build-3 for the hybrid.
**6.4 (DM):** K3 the five test calls → K5 results (side-by-side waveforms) → K3 decision matrix summary → K6.
**6.5 Lab 4, 6.6 Quiz intro:** generic template.

## Section 7: Knowledge and Multi-Agent Handoffs

**7.1 (SL):** K3 retrieval as a tool vs pre-turn injection (two columns) → K3 "Short, speakable, grounded" → K3 "'I don't know' is a feature" → K6.
**7.2 Code-along: FAQ lookup tool (SC):** K5 `src/maple/knowledge.py` public surface (lower third with the API-verified note) → K5 terminal: `tests/unit/test_knowledge.py` green in about 0.1 s → K5 `agents/common.py`, `get_faq` and `KnowledgeToolsMixin` → K5 `agents/s07_knowledge_agent.py` agent and entrypoint → K5 demo: "Where do I park?" and "Do you take Delta Dental?" with the `lookup_clinic_info` call highlighted in the log → K5 demo: "What time do you close on Friday?" answered with no tool call (callout: faster) → K5 demo: "Do you do Botox?" no match, "I'm not sure" + offer → K6.
**7.3 (SL):** K3 "When a vector DB is worth it" → K4 a latency mini-waterfall (**D3** style) with the embedding call → K3 cache + prefetch → K6.
**7.4 (SL):** K3 prompt size / tool confusion / personas → K4 **D7** build-1 and build-2 → K6.
**7.5 (SC):** K4 **D7** + K5.
**7.6 Lab 5:** generic template; step 3 card shows **D7** build-3.
**7.7 Quiz intro:** generic template.
**7.8 Multilingual Riley (SC):** K3 per-language settings table (STT language, turn detector, TTS voice); K5 `LANGUAGE` env and `follow_caller_language()` behind `FOLLOW_CALLER_LANGUAGE=1` in `agents/s07_knowledge_agent.py`; hear-it: the same FAQ answer in English, Spanish and Hindi; K3 "What to test differently".
**Section-end card (fallback wording):** "You can now: ground answers in a FAQ · hand off between agents · serve callers in more languages".

## Section 8: Telephony

**8.1 (SL):** K4 **D6** build-1 → K3 "8 kHz audio: choose STT accordingly" → K3 codecs (one line) → K6.
**8.2-8.5 (SC):** K5 with OBS masks on all numbers/IDs; the `telephony/*.json` files are created on screen in 8.2 and 8.5 (not shipped in `03-code/`); K4 **D6** build-2 in 8.4 and build-3 in 8.5.
**8.6 Compliance (TH):** avatar + K3 cards: AI disclosure / recording consent (one-party vs all-party) / TCPA outbound / DNC / retention / "Not legal advice" footer on every card.
**8.7 Project 2, 8.8 Quiz intro:** generic template.

## Section 9: Testing and Evaluating Voice Agents (signature)

**9.1 (SL):** K1 montage of failure clips → K3 eight failures, one per slide (mishearing, turn-taking, talking over, hallucinated availability, wrong tool args, missed escalation, latency spikes, injection) → K3 **D9** row by row → K6.
**9.2 (SL):** K4 **D8** built bottom-up → K3 "What runs in CI" → K6.
**9.3-9.10 (SC):** K5; highlight the key 3-5 lines of each assertion; K3 green/red result cards with ✓/✗ glyphs (never color alone).
**9.8:** K4 **D3** overlaid with measured p50/p95.
**9.11 Project 3, 9.12 Quiz intro:** generic template.
**9.13 Audio-in tests (SC):** K4 audio file → STT node → transcript (WER check) → behavior test; K3 "Text tests miss STT errors".
**9.14 LiveKit Simulations (DM):** K3 scenario definition → K5 simulator verdicts → K5 `on_simulation_end` hook; corner flag "LiveKit Cloud feature: check availability".
**Section-end card (fallback wording):** "You can now: assert tool calls · measure WER and latency · run simulated callers in CI".

## Section 10: Observability, Latency and Cost

**10.1 (SL):** K3 the metrics list in three groups (speed / usage / outcome) → K4 **D3** mapped to metric names → K6.
**10.2-10.4 (SC):** K5; 10.2 version note on screen (`metrics_collected` still works with a deprecation notice; totals from `session.usage`; `UsageCollector` named once as deprecated); K4 **D11** in 10.3; K3 cost per minute formula in 10.4: Σ(stage usage × unit price) ÷ call minutes.
**10.5 (SL):** K4 **D10** tile by tile → K3 alert thresholds (amber) → K6.
**10.6 Lab 6, 10.7 Quiz intro:** generic template.

## Section 11: Security

**11.1 (SL):** K4 **D12** → K3 five threats, one per slide (spoken injection, social engineering, exfiltration via tools, toll fraud, voice cloning) → K6.
**11.2-11.4 (SC):** K5; K3 "Verify identity before revealing appointments"; K3 "Irreversible = read-back".
**11.5 (DM):** K5 with red failure overlays → teal after the fix.
**11.6 Quiz intro:** generic template.

## Section 12: Deploying to Production

**12.1 (SL):** K4 **D13** → K3 prewarm with `AgentServer(setup_fnc=prewarm)` → K3 draining → K6.
**12.2 Dockerising the agent (SC):** K5 `deploy/.dockerignore` with the API-verified footer → K5 `deploy/Dockerfile` builder stage (dependencies first, then the project) → K5 runtime stage, highlight `useradd`/`USER riley`, `download-files` and the `start` command → K5 build output, highlight the `download-files` step and the final image size → K5 container logs: production mode, registered with LiveKit → K5 health endpoint `OK` and the JSON blob (`agent_name`, `active_jobs`, `worker_load`) → K5 SIGTERM: draining, call continues, clean exit → K6.
**12.3 Deploy to LiveKit Cloud (SC):** K3 slide 1 "What LiveKit Cloud does for you" → K5 `livekit.toml` and `.env.production` (values masked; corner flag "lk agent commands: verify in current docs") → K5 deploy output streaming, then `id` line in `livekit.toml` → K5 `lk agent status` → K5 Playground call to `riley-receptionist` → K5 runtime logs with redacted transcript lines → K5 a demo prompt change, rollout and new version active → K5 version list and rollback → K3 slide 2 "The deploy loop" (five steps) → K6.
**12.4 (SL):** K3 host options (Render, Fly.io, ECS, Kubernetes) → K3 requirements (outbound WebSocket, health port, load-based autoscaling) → K4 **D13** build-1 with "any container host" → K6.
**12.5 A web front end for Riley (SC):** K3 slide 1 "Three pieces" (Browser → Token server → LiveKit room ← Riley, drawn in the D-style palette) → K5 terminal (flag "front-end starter commands: verify in current docs") → K5 `.env.local` (secret masked) → K5 `app-config.ts` with `agentName: "riley-receptionist"` and the clinic branding → K5 Python token-minting illustration (labelled "illustration; not a repo file") → K5 browser at `localhost:3000`, Start call, live captions → K5 `lk agent logs` showing the new job → K3 slide 2 "Before you put this on a real website" → K6.
**12.6 (SL):** K3 checklist slides grouped: fallbacks / timeouts / error speech / degradation / runbook → K3 `voice-agent-readiness-scorecard.md` preview → K6.
**12.7 Lab 7:** generic template.
**12.8 Chaos demo (DM):** K1 the live call → K5 `agents/s12_chaos_demo.py` (the `ChaosLLM` kill switch) → K5 split screen: Playground call + agent terminal + kill-switch terminal; `touch /tmp/riley-kill-llm` → hear the fallback LLM answer (teal), log line "switching to next LLM" highlighted → `rm /tmp/riley-kill-llm` → the same call with `CHAOS_NO_FALLBACK=1`: spoken error line, then transfer or goodbye (red) → K3 slide "What the chaos demo proves" → K6.
**12.9 Quiz intro:** generic template.
**Section-end card (fallback wording):** "You can now: containerise an agent · deploy to LiveKit Cloud · survive a provider outage".

## Section 13: Capstone

**13.1 (SL):** K3 requirements → K3 acceptance criteria → K4 **D14** → K6.
**13.1a Capstone gate (TH):** full-screen pause card: "Stop. Build it from the brief. Time box: one week." + scorecard as the acceptance check.
**13.2-13.5:** K5; K4 **D14** builds in 13.2; K4 **D8** progress overlay in 13.4; K4 **D10** live in 13.5. 13.3 shows `recover_after_error` (error line, then transfer or goodbye and hang-up).
**13.6 (TH):** K3 portfolio checklist (README, demo recording with numbers masked, test report, architecture diagram).
**13.7 Domain swap (AS):** generic template; step 3 cards: three example businesses (restaurant, salon, law office) → what changes (FAQ, tool schema, prompt) vs what stays (the tests) → `business-template.md`.
**Section-end card (fallback wording):** "You can now: ship a production voice agent · prove it with tests · adapt it to any business".

## Section 14: Pipecat and Choosing Your Stack

**14.1 (SL):** K4 **D15** → K3 `Pipeline`, `PipelineWorker`, `WorkerRunner`, `LLMContext` (one per slide; footnote "formerly `PipelineTask` / `PipelineRunner`, deprecated since 1.3") → K3 LiveKit → Pipecat translation table → K6.
**14.2 Code-along: Riley booking flow in Pipecat (SC):** K5 terminal with the API-verified footer → K5 `pipecat/s14_pipecat_bot.py` docstring comparison table → K5 code in eight steps, ≤ 15 lines each: imports and setup; tool schemas (`FunctionSchema`, `ToolsSchema`); tool logic (two of the four functions); `register_tools`; transport params; `run_bot` part 1 (calendar, services, tools); `run_bot` part 2 (`LLMContext`, universal aggregators, `Pipeline`, `PipelineWorker(PipelineParams(enable_metrics=True, ...))`, `WorkerRunner`); `run_bot` part 3 (`on_client_connected` queues `LLMRunFrame`) and the entry point → K4 **D15** as a recap of the `Pipeline` list → K5 runner on `localhost:7860/client`, browser call with `MAPLE_TODAY=2026-10-05` → K5 log: `find_available_slots`/`book_appointment` lines and a TTFB metrics line highlighted → K6.
**14.3 (SL):** K3 **D16** row by row → K3 "Questions to ask any vendor" → K3 "Build when… / Buy when…" → K6.
**14.4 Quiz intro:** generic template.

## Section 15: Wrap-up

**15.1 (TH):** K3 "What you built" montage → K3 next steps (multilingual, avatars, outbound campaigns) → K3 Build → Test → Operate path (course names only; promotional detail only in 15.3).
**15.2 Practice test intro:** generic template.
**15.3 Bonus (TH):** only lecture with course links/coupons (Udemy bonus rules; verify).
**15.4 Careers (TH):** K3 role titles → K3 interview question examples (from `interview-questions.md`) → K3 scoping a client build (discovery, per-minute cost, setup fee vs retainer) → no salary figures.

---

## Slide counts

Do not plan from estimates. Every `[SLIDE]` cue in the scripts is one slide, so the real count comes from the decks: run `python voice-ai-agents-course/09-production/tools/slide_builder.py --course voice-ai-agents-course` and count the slides in each `10-graphics/slides/section-XX.pptx`. Add the K1/K2/K7 cards the editor builds from templates. The 16 diagrams above are reused across sections and drawn once.
