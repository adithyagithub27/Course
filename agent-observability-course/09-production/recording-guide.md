# Recording Guide

> Extends `../../09-heygen/PRODUCTION-GUIDE.md` (7-beat structure, 140 wpm word budget, -16 LUFS, 1920×1080 H.264 30 fps) and `../../10-graphics/design-system.md` for the observability course. This course brings two new challenges: **recording dense third-party UIs (Langfuse, Grafana) so they are readable and redacted**, and **keeping every number on screen consistent with the narration** across 15 sections recorded over 12 weeks.

---

## 1. Workflow overview

```
Script (02-lecture-scripts/) ──► Scene plan (per lecture) ──► numbers checked against 01-curriculum/numbers-card.md
        │
        ├─► Avatar scenes ──► HeyGen batch render (per section; Course 3 tools by reference)
        ├─► Slides/diagrams ──► slide_builder.py decks (10-graphics/slides) + D1-D12 masters (10-graphics/diagrams)
        ├─► Screencasts ──► OBS (one session per section, same layout)
        └─► Dashboard/trace captures (Langfuse, Grafana, Ops Console) ──► OBS at fixed zoom + redaction masks
                     │
                     ▼
        Assemble (DaVinci Resolve / CapCut) ──► Numbers overlays ──► Loudness normalize ──► Captions ──► QA ──► Upload
```

Lecture types from the curriculum map to recording methods:

| Type | Count | Recording method |
|---|---|---|
| SL (slides) | 20 | HeyGen avatar (picture-in-picture or cut-ins) + slide/diagram scenes |
| SC (screencast/code-along) | 44 | OBS screen + avatar intro/outro (beats 1-3, 6-7); switch to a capture scene when the result appears in Langfuse, Grafana or the Ops Console |
| DM (live demo) | 6 | Capture scene throughout (1.1 cost meter, 3.6 broken traces, 5.6 the loop, 7.6 slow provider, 9.4 Langfuse dashboards, 13.5 backend down) |
| TH (talking head) | 6 | HeyGen avatar, or real camera for 14.1a gate / 14.5 portfolio / 15.2 careers / 15.4 bonus if possible |
| CH challenge | 5 | Spec card → **pause card** → capture-scene solution or reveal (11.2-11.4 as Part A investigation / Part B reveal) |
| LAB walkthrough | 7 | Short OBS walkthrough of the lab doc and expected result |
| AS intro | 3 | Avatar + brief slide |
| QZ intro | 14 | 13 section quizzes plus the 15.3 practice test: a short avatar intro over the quiz-topics slide (1:00 or less), no screen capture |

**Split 6.3, 6.6, 11.2, 11.3, 11.4, 14.2 and 14.3 into Part A / Part B** at record time (same script, two uploads, each under ten minutes). Give Part B a 10-second recap hook instead of a cold hook.

## 2. HeyGen avatar

- Use the **same avatar and voice** as Courses 1-3 (see `../../09-heygen/avatar-config/` and `voice-config/`) for series consistency.
- **Pronunciation dictionary.** Use the course glossary described in `video-generation-plan.md` §4.1 (`pronunciation.observability.json`): Langfuse, OpenTelemetry/OTel, OTLP, OpenInference, LiteLLM, DeepEval, Prometheus, Grafana, TTFT, TPOT, p95, SLI/SLO, EWMA, PSI, semconv, `gen_ai.*`, Northwind, Atlas, uv, GPT-4.1 mini.
- **Attribute names in narration:** say the full dotted name once per lecture, then the plain name ("the input-tokens attribute"). Code identifiers stay in backticks in the script so the TTS polish leaves them alone.
- Keep avatar segments ≤ 60 s without a visual change (PRODUCTION-GUIDE rule 1).
- **Disclosure:** see `../07-udemy-listing/publish-checklist.md` §9 (verify Udemy's AI content policy).

## 3. OBS setup

| Setting | Value |
|---|---|
| Canvas / output | 1920×1080, 30 fps |
| Encoder | x264 or hardware H.264; CRF ~18 / high-quality preset for the master recording |
| Recording format | MKV (crash-safe), remux to MP4 after |
| Scenes | `Code` (editor full screen), `Code+Terminal` (70/30 split), `Langfuse` (browser window capture, address bar cropped, masks on project switcher and user menu), `Grafana` (browser in kiosk mode, 125% zoom), `Ops Console` (browser, 100% zoom, fixed window size), `CI` (browser on GitHub Actions, org avatar mask) |
| Audio tracks | Track 1: narration mic. Track 2: system audio (rarely used; Streamlit has no sound). Keep two tracks anyway so a notification chime can be removed |
| Cursor | OS large-cursor setting on; OBS cursor highlight off (it obscures span names) |

### Editor and terminal theme

| Item | Setting |
|---|---|
| Editor | VS Code with a dark theme matched to the design system (background `#0A1628`; strings teal `#00D4AA`; functions amber `#FFB020`; comments `#94A3B8`) |
| Font | JetBrains Mono |
| **Editor font size** | **20-22 px** at 1920×1080 (so it reads on a 13" laptop and at 720p playback). Zoom (`Ctrl/Cmd +`) rather than scaling in post |
| **Terminal font size** | **20-22 px**. Prompt in teal; a short prompt such as `atlas $` (hide user, host and path) |
| Visible lines | ≤ 15 lines of code per screen (design system); collapse the rest with `# ...`. YAML files: fold all but the discussed block |
| Minimap, breadcrumbs, extensions UI | Off |
| Notifications | Do Not Disturb on the OS; close Slack/email; hide the dock and taskbar |
| File label | Filename visible top-left (matches `03-code/` paths) |
| Version banner | Corner note on every code lecture: "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (incubating) / litellm 1.103" (curriculum §1) |
| Logs | Atlas always logs JSON (`telemetry/logging_setup.py`); there is no pretty mode. Use `LOG_LEVEL=WARNING` when log lines would distract from the screen beat, and `LOG_LEVEL=INFO` in 5.5, where the JSON log with `trace_id` is the lesson |

## 4. Audio chain (narration)

```
Dynamic or small-diaphragm condenser mic
  → audio interface (48 kHz / 24-bit)
  → OBS/DAW track: high-pass 80 Hz → noise gate/expander (light) → compressor (3:1, ~-18 dB threshold)
  → limiter (-1 dBTP) → loudness normalize in post to -16 LUFS integrated
```

- Treat the room (soft furnishings, no bare walls behind the mic); record a 10 s room-tone sample per session.
- Wear closed-back headphones so you can hear notification chimes you need to cut.
- This course has no agent audio, so there is no echo problem, but there is a **keyboard problem**: code-alongs involve a lot of typing. Use a quiet keyboard, position the mic away from it, and lean on the noise gate lightly; some keyboard sound is authentic.

## 5. Demos: rehearsal rules

- Run every demo **3 times before recording**. Demos in this course are deterministic when run in `OFFLINE=1` with the Makefile defaults (seed 7, Monday 2026-09-14, 4,000 sessions, `CACHE=0 DIET=0 ROUTER=0`), so a demo that differs between rehearsals means a lever, the seed or the store changed: stop and find out why. Remember the Makefile's `CACHE`/`DIET`/`ROUTER` override `ATLAS_*` variables in your shell; pass levers on the `make` line.
- **Shell set-up for every session:** Atlas loads `.env` itself (variables exported in the shell win), so check no stale `ATLAS_*` exports linger in the recording terminal. `curl -s localhost:8000/metrics` works directly. For live Ops Console demos next to a running server, start it with `STREAMLIT_SERVER_HEADLESS=true make console STORE=...` and open the page URL directly (on an empty store the home page would replay a whole day into it). For trace waterfalls that look like a real model's, run Atlas with `ATLAS_MOCK_LATENCY_SCALE=1`.
- **Live-LLM demos** (2.3, part of 6.6, 8.2, 13.5) are not deterministic. Record them as live, say "live request" on screen, and accept small differences from the script's numbers; the narration for these lectures must quote ranges, not exact figures.
- **Keep genuine surprises when they teach something** (a cached-token share lower than expected in 6.4, a fallback that fires earlier than planned in 7.6). Cut surprises that are noise (a network blip).
- Say the lecture ID and the take number out loud at the start of each take ("6.3A, take 2") to make editing easier.
- Pre-warm everything (compose stack up, Langfuse project open, Streamlit running, browser zoom set) so viewers don't watch loading spinners, unless the wait is the lesson (13.5's exporter timeout).

## 6. Dashboard and trace capture track: readable, redacted, consistent

> This replaces Course 3's phone-call capture protocol. One exposed secret key or OTLP header can run up a bill; one unreadable trace makes the lecture useless.

### 6.1 Readable

- [ ] **Langfuse at 125-150% browser zoom.** Window sized to 1920×1080 (or a 1600×900 region scaled to canvas). The observation tree and the detail panel both visible.
- [ ] **Grafana at 125% zoom in kiosk mode** (`?kiosk` URL parameter or the kiosk toggle; verify in your Grafana version). One panel row at a time; use the panel "View" mode for a single panel when discussing it.
- [ ] **Ops Console at 100% zoom**, fixed window, app CSS font-size ≥ 18 px, sidebar width fixed.
- [ ] **The 25% test:** pause the recording, scale the preview to 25% (≈480×270). The span name, the attribute name and the number under discussion must still be legible. If not, zoom in and scroll; never crop in post.
- [ ] **Zoom-and-hold in the edit:** 1.5× on the element being discussed, hold 3 s, zoom out. Never zoom on a moving cursor.
- [ ] **Large cursor** and slow, deliberate movement. Park the cursor off the content when not pointing.
- [ ] **Waterfall reading order:** collapse all, then expand top-down as you narrate, so the tree builds in the order the agent executed.

### 6.2 Redacted

Before recording:

- [ ] **Dedicated recording organisation and project** in Langfuse (`atlas-course`), separate from any personal or client project. Same for LangSmith and Phoenix in Section 12.
- [ ] **Dedicated OpenAI project** with a hard spending cap, keys created only for recording.
- [ ] `.env` is **never opened on screen**. Show `.env.example`, which has placeholders only.
- [ ] Clear shell history, or use a fresh shell with `HISTFILE=/dev/null`. Don't `echo $LANGFUSE_SECRET_KEY` or `printenv`. `make` targets must not print env vars.
- [ ] Terminal prompt shows no username, hostname or home path.
- [ ] Browser: separate profile with no saved passwords, no bookmarks bar, no autofill, no extensions; close other tabs.
- [ ] **Address bar cropped** out of the Langfuse and Grafana OBS scenes (it shows project ids, regions and query strings).
- [ ] **OBS colour-source masks** (Deep Navy rectangles) saved in each scene over: the Langfuse project/organisation switcher, the user avatar/menu, the API keys settings page, Grafana's user menu, the GitHub organisation avatar. Check that a mask still covers the field after scrolling or resizing.
- [ ] Langfuse **public** keys may appear briefly (they're rotated afterwards); **secret keys never**. The OTel Collector config's `Authorization` header value is `${env:LANGFUSE_AUTH}` on screen, never a literal.
- [ ] Prometheus `/targets`: only the course's local targets appear; no real hostnames.

During recording:

- [ ] Run demos with `pii.py` masking on, so the course demonstrates its own advice and no persona "employee id" appears unmasked.
- [ ] Tenant names are the fixture names (`ops`, `finance`, `hr`, `eng`); persona names are fictional and obviously so; employee IDs follow `NW-` plus five digits (`NW-10433`).
- [ ] If a real value leaks into a frame (a key, an email from a browser autofill), stop the take. Don't plan to fix it in post.

After recording:

- [ ] **Scrub pass in the edit:** step through every frame that shows a terminal, a browser, a settings page or a YAML file, looking for keys, headers, project ids, emails and hostnames.
- [ ] **Rotate every key used in recording** (Langfuse, OpenAI, LangSmith, Phoenix, Grafana admin), even if you believe none was shown.
- [ ] Delete the recording projects' traces you don't need (data retention: practise what Section 10 preaches).

### 6.3 Consistent (the Ops Console rule)

- [ ] **One fixture day for the whole course:** plain `OFFLINE=1 make replay` (seed 7, Monday 2026-09-14; `DAY=` is only for adding a second day to a two-day store, as in Lab 5). Lever comparisons go into their own stores (`make replay CACHE=1 STORE=.atlas/cache.sqlite`) and side by side on the Compare replays page. Langfuse (`make replay LANGFUSE=1`) and the Ops Console show the same day; Grafana shows live swarm traffic, not the replay.
- [ ] `.streamlit/config.toml` pins the theme (design-system colours); Streamlit version pinned in `pyproject.toml`.
- [ ] Pages are the ones in `03-code/console/pages/`, in sidebar order: Live cost, Cost, Latency, Quality, Budgets, Traffic, Retrieval, Reliability, Safety, Alerts, Traces, Compare replays (Lab 5 adds My quality). Sidebar width fixed. Incident lectures open the incident store (`make console STORE=.atlas/incident-0N.sqlite`).
- [ ] The browser window for the console is the same size in every lecture (save the OBS window-capture geometry; don't drag it between sessions).
- [ ] **Numbers come from `01-curriculum/numbers-card.md`** (regenerated with `make replay`, `make report` and the console; the scripts quote it). If the code or the price table changes, regenerate the card, fix the scripts, and re-record every capture in the affected sections.
- [ ] Every dollar figure on screen carries the K5 footer `Simulated traffic · verify current pricing`; every offline latency figure carries `mock LLM latencies`.
- [ ] Between sections, re-open the console and compare the Cost page against the Section 2 capture frame by frame. Any drift (a changed column, a different colour) gets fixed before recording continues.

## 7. Screen content rules for observability lectures

- Show the **trace, metric or table** whenever a number is spoken, so viewers can follow on mute and captions can sync.
- Label what is on screen: `Langfuse · trace view`, `Grafana · Atlas Ops`, `Ops Console · Cost`, `Terminal · console exporter`. Students use several UIs and lose track.
- For before/after comparisons (6.4, 6.5, 6.6, 6.8, 7.6), use the design-system `BEFORE` (red) / `AFTER` (teal) labels and put the two figures side by side on one K5 card.
- Use Alert Red only for failures and SLO breaches; Amber for thresholds and budget lines.
- Never show a cost figure without its "simulated" footer.

## 8. Special recordings

| Lecture | What's special | How to record |
|---|---|---|
| 1.1 | The $4,000 weekend: cost meter climbing, then the guarded run | `make loop-demo` with the guards off (`ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0`, `PACE=0.1`) into `STORE=.atlas/live.sqlite`, with the Live cost page open (`STREAMLIT_SERVER_HEADLESS=true make console STORE=.atlas/live.sqlite`, then `http://localhost:8501/Live_cost`). It ends at 549 steps and $4.90; then the default guard stops it at 6 steps and $0.0086. Record at real speed (about 50 s). Label `Simulated traffic` for the whole shot |
| 2.3 | First live trace | Live request; say "live" on screen; keep the Langfuse trace open and collapsed before expanding. This trace is reused in the promo, so record a clean take |
| 2.4 | Offline replay fills the store | `OFFLINE=1 make replay` (about 20 s; $56.28, 10,184 requests), then `make console`. This is the first appearance of the console: this frame is the reference for rule 6.3 |
| 3.2, 3.4 | Console exporter output | `OTEL_EXPORTER=console make run`; the exporter prints indented JSON per span, children first. Highlight the attribute keys with a zoom-and-hold |
| 3.6 | Three broken traces | Each break is code on a slide plus a real test: `test_broken_orphan_span_is_detectable` builds the orphan on purpose; the other two breaks are caught by `test_tool_spans_are_children_of_agent`, `test_one_generation_per_model_call` and `test_double_instrumentation_is_idempotent` in `tests/integration/test_spans.py`. Record the test run once, red slides then green tests |
| 5.6 | The loop you can only see in a trace | `make loop-demo` three ways into one store (guards off, default 6 steps, `ATLAS_MAX_TOOL_RETRIES=2`); open each `trace_id` on the Traces page; the red repeated tool span is the visual |
| 6.4-6.8 | Before/after cost | One store per configuration (`make replay CACHE=1 STORE=.atlas/cache.sqlite`, and so on), then the Compare replays page: baseline $56.28, cache $37.00, diet $41.99, router $47.07, all three $19.07 |
| 7.6 | Slow provider chaos | `make replay SCENARIO=slow_provider STORE=...`, then the console Latency page: p95 leaves the budget while retries, fallbacks and cost stay flat with the 20 s default timeout (the lesson); then the Lab 4 config (`.env.chaos.example`) in a second store brings p95 to 3,859 ms on Compare replays |
| 8.2 | Live judge | Cap with `JUDGE_MAX_CALLS`; show the judge's own cost line item on screen |
| 9.6 | An alert fires | `make stack`, `ATLAS_SCENARIO=loop` in `.env` for the stack's Atlas container, `make swarm`; Prometheus Alerts (port 9091) shows the rule pending then firing (Lab 6). Time-lapse the wait |
| 11.2-11.4 | Incident investigations (Part A) and reveals (Part B) | `make incident N=<n>`, then `make console STORE=.atlas/incident-0N.sqlite`; each `[SCREEN: Exhibit n. …]` cue is one console page or trace. Don't open `solution.md` on screen; full-screen pause card with a static timer graphic; Part B opens with a 10-second recap |
| 12.2, 12.3 | Same trace in LangSmith and Phoenix | Dedicated free-tier accounts; same redaction masks; show the exporter line that changed |
| 13.1 | Self-hosted Langfuse compose up | Show the compose file with a `verify against current Langfuse compose` note; the services starting; the first project created. Mask any generated secret in the compose `.env` |
| 13.3 | CI budget gate | A prepared failing PR, then the fix; GitHub org avatar masked |
| 13.5 | Kill the observability backend | Stop the collector container mid-swarm (`make stack`, `make swarm`); show Atlas still answering, `/healthz` `exporter_health` counting failures, and the `telemetry exporter … dropping spans` warning in the log |
| 14.1a | Capstone gate | Full-screen pause card: "Stop here. Build it from the brief. Time box: one week." |
| 15.2 | Careers | No salary figures on screen or in narration |

## 9. Engagement mechanics

Build these into production. They aren't lecture content, but they affect ratings and completion.

1. **Section-end "You can now..." card.** A 10-second K6-style slide at the end of the **last lecture of every section**, listing three concrete abilities (e.g., Section 6: "You can now: price every token · roll up cost by tenant · prove a 40% saving"). Screenshot-friendly: large text, the course name in small type, no URLs.
2. **Build log.** In 1.5 and 2.4, ask students to keep a `BUILD_LOG.md` in their repo and post one line per section in Q&A. Repeat the prompt on each section-end card.
3. **Read-it moments.** Every time a change alters a number (caching, diet, routing, a fallback, a mask), show **before and after** on one card, same replay, `BEFORE` red / `AFTER` teal.
4. **Failure-first demos.** Start each build section (3, 5, 6, 7, 8, 13) with about 30 seconds of the broken version (an orphan span, a runaway loop, a bill by tenant that doesn't add up, a p95 doubling, a green dashboard over unhappy users, a dead backend) before building the fix.
5. **Investigate first.** In 11.2-11.4, the pause card comes before any hint. Q&A pinned post explains how to post hypotheses with a spoiler tag.
6. **Q&A seeding.** On launch day, post the five most likely questions per section with answers (draw them from `../10-resources/troubleshooting.md` and the beta feedback). Pin the setup, versions, Docker and incident-lab threads.
7. **Announce version pins.** Put "Verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (incubating) / litellm 1.103" on the **first slide of every code lecture**, and keep a pinned Q&A thread for breaking changes and attribute renames.

Checklist for each lecture: see `qa-checklist.md` §1 (engagement mechanics item).

## 10. Export and delivery

- Master: 1920×1080, H.264, 30 fps, AAC 48 kHz stereo, -16 LUFS integrated, -1 dBTP true peak.
- File naming: `S{section}-L{lecture}-{slug}.mp4`, e.g., `S06-L6.3A-cost-rollups.mp4`, `S11-L11.2B-incident-1-reveal.mp4`.
- Keep the project files, raw OBS tracks and the frozen fixture snapshot until 6 months after publishing, for re-cuts after SDK or semconv updates.
