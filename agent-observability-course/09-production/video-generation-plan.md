# Video Generation Plan: AI Agent Observability & Cost Control

> **Stack:** HeyGen (avatar + narration voice), OpenAI API (runs Atlas and the online judge in demos, polishes scripts for TTS, optional voiceover TTS and caption transcripts), OBS Studio (screencasts and dashboard capture), CapCut or DaVinci Resolve (assembly), Udemy (publish).
> **Inherits:** the 7-beat lecture structure, tone rules, scene types and QA bar from `../../09-heygen/PRODUCTION-GUIDE.md`. This document covers only what is different or additional for a course whose subject is dashboards, traces and numbers.
> **Reuses:** the HeyGen tools from Course 3 by reference: `../../voice-ai-agents-course/09-production/tools/` (`scene_extractor.py`, `heygen_batch.py`, `pronunciation.json`, `requirements.txt`). Don't copy them into this folder; run them from there with this course's script paths, and maintain a **course-specific pronunciation glossary** (section 4.1 below) that you pass in place of Course 3's. `transcript_to_srt.py` is not needed here (no call demos).
> **Curriculum:** `../01-curriculum/curriculum.md`, 105 items, 627 min of non-quiz video by table minutes (≈10.5 h; 671 min including quizzes).

---

## 1. The one thing that makes this course different to produce

Course 3 had to let students **hear** an agent. This course has to let students **read** one: a trace waterfall, a `gen_ai.usage.input_tokens` attribute, a Grafana p95 line crossing an SLO threshold, a cost rollup by tenant. Roughly a third of the runtime is spent looking at a third-party UI (Langfuse, Grafana) or the course's own Streamlit Ops Console. If those captures are too small to read, show a key in a URL bar, or show numbers that don't match the narration, the course fails regardless of how good the avatar looks.

So the plan has three production tracks:

| Track | What it produces | Tool | Share of runtime |
|---|---|---|---|
| A. Avatar | Hooks, promises, context, teach beats on TH and SL lectures, recaps, bridges, pause cards for challenges | HeyGen | ≈28% (≈176 min, derivation in §4.3) |
| B. Screencast | Code-alongs, terminal, tests, Makefile targets, YAML, CI runs | OBS + narration voice | ≈40% (≈250 min) |
| C. Dashboard and trace capture | Langfuse trace and dashboard views, Grafana panels, the Ops Console, Prometheus targets, the cost meter, incident investigations | OBS at fixed browser zoom, with redaction layers and a frozen local dataset | ≈32% (≈200 min) |

Track C replaces Course 3's call-capture track. Section 5 below is dedicated to it.

---

## 2. Lecture inventory by production type

Derived from the curriculum tables (see `07-udemy-listing/publish-checklist.md` §0). Quizzes have no video beyond a 1-minute intro on some quiz lectures. Labs, assignments and challenges get a 1-3 minute intro video; challenges also get a pause card and a solution walkthrough.

| Type | Count | Table minutes | Video needed | Tracks |
|---|---|---|---|---|
| TH talking head | 6 | 31 | Full avatar | A |
| SL slides | 20 | 128 | Avatar for hook/context/recap/bridge, slides + voice for teach | A |
| SC screencast / code-along | 44 | 347 | Avatar hook and recap, OBS body; Track C whenever the result is shown in Langfuse, Grafana or the Ops Console | A + B (+ C) |
| DM live demo | 6 | 34 | Avatar hook, dashboard/trace capture body | A + C |
| CH challenge (pause, then solution) | 5 | 49 | Avatar spec + pause card, capture body for the reveal | A + C |
| LAB / AS intros | 10 | 38 | Short avatar or voice + slide, OBS walkthrough of the lab doc | A (+ B) |
| QZ quizzes and practice test | 14 | 44 | None (Udemy quiz) | none |
| **Total videos to produce** | **91** (of 105 items) | **627** | | |

Seven lectures record as Part A/B (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3), so the upload count is **98 videos**.

---

## 3. Narration: two options, pick one before recording anything

Consistency rule from the production guide: one voice, one avatar, one look across the whole course. That forces a decision now.

| | Option A: fully synthetic | Option B: hybrid (recommended) |
|---|---|---|
| Avatar beats | HeyGen avatar, HeyGen voice | HeyGen avatar with **your cloned voice** |
| Screencast and capture voiceover | Same HeyGen voice, audio-only export | **You narrate live while recording in OBS** |
| Voice consistency | Consistent (no live demos force your voice in, unlike Course 3) | Consistent: it is your voice everywhere |
| Authenticity for investigations | Lower: TTS pacing can't follow a cursor hovering over a span, and incident investigations (11.2-11.4) need "let me check that tenant… no, look at this" pacing | Higher: you react to what's on screen, which is the whole point of Track C |
| Production time | Lowest | Medium (narrating ≈450 min of screencasts and captures) |
| HeyGen credits | Highest (avatar + all voiceover) | Lowest (avatar beats only) |
| Risk | Udemy learners are sensitive to fully synthetic technical courses; the incident labs in particular would feel canned | Voice clone quality must pass a listening test |
| Series consistency | Course 3 recommended Option B; if it shipped that way, Option A here would break the series voice | Matches Course 3 |

**Recommendation: Option B.** The incident investigations need a human reading the screen in real time. Clone your voice in HeyGen so the avatar sounds like you, then narrate Tracks B and C live. It also makes re-records cheaper when a semconv attribute is renamed: re-record the changed capture, regenerate only the affected avatar beat.

If you choose Option A, at minimum narrate 11.2-11.4 Part A (the investigations) yourself and add a one-line note in lecture 1.5 that the presenter is an AI avatar. Check Udemy's current policy on AI-generated content before publishing either way.

---

## 4. Track A: HeyGen avatar pipeline

### 4.1 One-time setup

1. **Reuse the Course 3 avatar, look, voice and background** (premium look: white or slate-blue shirt, charcoal blazer, `09-heygen/backgrounds/studio-navy.png`; `HEYGEN_BACKGROUND_IMAGE` set). Read the IDs from `../../09-heygen/avatar-config/` and `voice-config/`. Do not create a new avatar for this course; the series must look like one instructor.
2. Generate a 30-second test with a paragraph from lecture 3.3 (contains "gen_ai.usage.input_tokens", "OpenTelemetry", "Langfuse", "semantic conventions", "p95"). Check pronunciation, pacing at ~140 wpm, and lip sync.
3. **Course-specific pronunciation glossary.** Create `pronunciation.observability.json` in this course's `09-production/` (same format as Course 3's `tools/pronunciation.json`) and pass it to `scene_extractor.py --polish` in place of the default. Entries: Langfuse ("LANG-fuse"), OpenTelemetry (spoken in full; "OTel" as "OH-tel"), OTLP (spell out), OpenInference (spoken in full), LiteLLM ("light L-L-M"), DeepEval ("deep eval"), Prometheus, Grafana ("gra-FAH-na"), TTFT ("time to first token" on first use, then "T-T-F-T"), TPOT ("time per output token", then "T-P-O-T"), p95 ("p ninety-five"), SLI/SLO (spell out), EWMA ("E-W-M-A"), PSI ("P-S-I"), semconv ("semantic conventions"), `gen_ai.usage.input_tokens` ("gen underscore A-I dot usage dot input tokens" on first use, "the input-tokens attribute" afterwards), Northwind, Atlas, uv ("U-V"), GPT-4.1 mini ("G-P-T four point one mini"), Docker Compose.
4. Attribute names in narration: the scripts should say the attribute once in full and then use the plain-English name. The polish step must **not** "expand" or reword code identifiers; keep them inside backticks in the script so `scene_extractor.py` leaves them alone (check its handling of inline code before the first batch).
5. Confirm the HeyGen API key from Courses 1-3 still has API access on the current plan (HeyGen API access is plan-dependent; verify).

### 4.2 Batch generation flow

```
02-lecture-scripts/section-XX.md
        │  ../../voice-ai-agents-course/09-production/tools/scene_extractor.py
        │     --out 09-production/scenes/section-XX.json --polish
        │     (splits [AVATAR] blocks, polishes for TTS with OpenAI, chunks ≤1,400 chars)
        ▼
09-production/scenes/section-XX.json   (manifest: lecture_id, scene_id, text, est_seconds)
        │  ../../voice-ai-agents-course/09-production/tools/heygen_batch.py generate
        │     (POST /v2/video/generate per scene, records video_id)
        ▼
09-production/scenes/section-XX.status.json
        │  heygen_batch.py poll  (GET /v1/video_status.get until completed, downloads MP4)
        ▼
09-production/generated/S03/3.3-hook.mp4 ...
```

Rules:
- One HeyGen video per **scene**, never per lecture. Scenes are 15-60 seconds. This keeps regenerations cheap and matches the "avatar never talks more than 60 s" rule.
- Chunk at 1,400 characters per API call (HeyGen enforces a per-scene text limit; verify the current value).
- Generate a whole section in one batch, review, then move on. Never generate the entire course before reviewing Section 3.
- Keep `speed` at 1.0 and fix pacing in the script, not the voice setting.
- File names: `S{section:02}/{lecture_id}-{beat}.mp4`, beats: `hook`, `promise`, `context`, `teach1`, `teach2`, `recap`, `bridge`, `intro`, `pause` (challenge pause cards), `reveal-intro` (incident labs).
- The tools read `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, `OPENAI_API_KEY` from the environment. Export them from the production `.env`, never from the student-facing one.

### 4.3 Credit estimate (derived from the curriculum's avatar share)

| Lecture type | Count | Table min | Avatar share assumed | Avatar min |
|---|---|---|---|---|
| TH | 6 | 31 | 100% (full avatar) | 31 |
| SL | 20 | 128 | ≈40% (hook, context, recap, bridge; teach beats are slides + voice) | 51 |
| SC | 44 | 347 | ≈1.5 min per lecture (hook + recap + bridge) | 66 |
| DM | 6 | 34 | ≈1 min per lecture (hook + recap) | 6 |
| CH | 5 | 49 | ≈1.5 min per lecture (spec card + pause card + reveal intro) | 8 |
| LAB / AS intros | 10 | 38 | ≈1.5 min per item | 15 |
| **Avatar runtime in final videos** | | | | **≈177 (≈28% of 627)** |
| Retakes and pronunciation fixes (30%) | | | | ≈53 |
| Promo video and Udemy landing clips | | | | ≈5 |
| **Total HeyGen generation** | | | | **≈235 min** |

HeyGen sells credits by generated minute and API access by plan tier. Look up your tier's price per minute and multiply by 235. Budget a 20% buffer. Prices change; do not carry a number from this document into a budget without checking the pricing page. This is lower than Course 3's ≈265 min because this course has fewer TH/SL minutes and no avatar in the demo bodies.

---

## 5. Track C: dashboard and trace capture (the part most instructors get wrong)

### 5.1 Why default screen recording fails

Langfuse and Grafana are dense UIs designed for a 27" monitor. Recorded at 100% zoom on a 1920×1080 canvas, a span name is 11 px tall and unreadable on a phone or at 720p. The address bar shows your project id and region. The Langfuse project switcher shows your organisation name. A Grafana panel legend shows a tenant label you meant to redact. And the numbers on screen change every time you re-run the swarm, so take two never matches the narration from take one.

### 5.2 Four capture rules

| Rule | How |
|---|---|
| **1. Readable zoom** | Browser at **125-150% zoom** (Langfuse) or **125%** (Grafana), window sized to exactly 1920×1080 or a 1600×900 region scaled up in OBS. Test: pause the recording, scale to 25% (≈480×270) and check that the span name and the token count are still readable. If not, zoom in more and scroll. Never fix legibility in post by cropping; you lose context |
| **2. Redact before you record** | Use a **dedicated recording Langfuse project** named `atlas-course` in an organisation named for the course, so nothing sensitive can appear. Crop the address bar out with an OBS window capture region, or use a browser kiosk mode. Add an OBS colour-source mask over the project switcher and user avatar. In Grafana, hide the top bar with kiosk mode (`?kiosk`) and use the tenant variable names from the fixture (`ops`, `finance`, `hr`, `eng`), never real names. Public keys are fine to show if they're rotated afterwards; secret keys, OTLP headers and `.env` are never shown (see `recording-guide.md` §6) |
| **3. Freeze the data** | Every offline capture uses **one fixture day**: plain `OFFLINE=1 make replay` (Makefile defaults: seed 7, Monday 2026-09-14, 4,000 sessions, `CACHE=0 DIET=0 ROUTER=0`; $56.28). It is deterministic, so no snapshot is needed: anyone who runs it gets the numbers in `../01-curriculum/numbers-card.md`. Lever and scenario comparisons go into their own stores (`STORE=.atlas/<name>.sqlite`), incidents into `.atlas/incident-0N.sqlite` (`make incident N=`). Langfuse gets the same day with `make replay LANGFUSE=1`. Grafana shows live swarm traffic against `make stack`, so its numbers are recorded as they come and narrated as ranges. When a lecture needs live model calls (`OFFLINE=0`), record it live and say so on screen |
| **4. Keep the Ops Console consistent** | The Streamlit Ops Console is the one UI the course owns, so it must look identical in every lecture: same theme (design-system dark: Deep Navy background, Teal accents, Red only for breaches), the same sidebar (the twelve pages in `03-code/console/pages/`: Live cost, Cost, Latency, Quality, Budgets, Traffic, Retrieval, Reliability, Safety, Alerts, Traces, Compare replays), same sidebar width, same store for a given lecture. For live demos next to a running server, start it with `STREAMLIT_SERVER_HEADLESS=true make console STORE=...` and open the page URL directly (on an empty store the home page replays a whole day into it). Pin the Streamlit version in `pyproject.toml`, set `theme` in `.streamlit/config.toml`, and never resize the window between lectures. The console is recorded at 100% browser zoom because its fonts are already sized for video (set `font-size` in the app's CSS to ≥ 18 px) |

### 5.3 What to capture per UI

| UI | Lectures | Capture notes |
|---|---|---|
| **Langfuse trace view** | 2.3, 3.4 (via console exporter first, then Langfuse), 4.2-4.7, 5.2-5.4, 6.3, 8.2, 11.2-11.4, 12.1 | Open the trace, collapse everything, then expand top-down as you narrate, so the waterfall builds. Hover to show usage and cost on the generation. Cursor size: large (OS accessibility setting) so students can follow it. Keep the observation tree and the detail panel both visible; don't full-screen the JSON |
| **Langfuse sessions / users / dashboards** | 4.3, 9.4 | Filter by tag on screen (type it, don't paste) so students see where the filter lives |
| **Langfuse prompts and datasets** | 4.4, 4.5, 8.6, 11.4 | Show the label switch (production → staging) as the visual for the rollback in 11.4 |
| **Grafana** | 9.2, 9.3, 9.6, 11.3, 14.3 | Kiosk mode, 125% zoom, one panel row at a time. Time range fixed to the fixture day. Annotations for releases visible. Alert state visible when an alert fires (9.6) |
| **Prometheus** | 9.2 | `/targets` page and one query only; it's not the teaching UI |
| **Ops Console (Streamlit)** | 1.1, 2.4, 3.1, 5.6, 6.3-6.8, 7.2, 7.6, 8.3, 8.7, 11.2-11.4, 14.2-14.4 | Same theme and window every time (rule 4). 1.1 uses the Live cost page, which refreshes every two seconds; record it at real speed (`PACE=0.1`, about 50 s) |
| **Terminal (console exporter, `make` targets, pytest, CI logs)** | 3.2, 3.4, 3.6, 13.3, 13.5 | Track B rules; the console exporter (`OTEL_EXPORTER=console make run`) already prints indented JSON per span. `.env` is loaded automatically; clear stale `ATLAS_*` exports from the recording shell, since they override it |
| **GitHub Actions** | 13.3 | The failing then passing budget gate. Blur any organisation avatar; the repo is the public course repo so its name is fine |

### 5.4 Incident investigations need scripting

Lectures 11.2-11.4 Part A are recorded as **real-time investigations** of the frozen incident datasets. To make them teachable:

- The investigation path is in the script as six `[SCREEN: Exhibit n. …]` cues, each one console page or trace in the incident store (`make incident N=<n>`, then `make console STORE=.atlas/incident-0N.sqlite`). Narrate as if discovering. Rehearse three times so the mouse doesn't wander.
- Each incident keeps at least one **wrong hypothesis** in its hypothesis table (top-k in Incident 2, a failing tool in Incident 1) and shows the exhibit that rules it out. Students learn more from the elimination than from the answer.
- The pause card ("Pause now. You have the spans and the brief. Eight minutes.") is a full-screen K3 slide with a visible timer graphic, not a countdown that actually runs for eight minutes.
- Part B (the reveal) opens with a 10-second recap of the brief, then the walkthrough, then the fix applied and re-run against the same spans.
- `solution.md` must not be visible in any file tree shown during Part A (incidents 1-3 ship one; incident 4's is stripped by `make student-repo`).

### 5.5 Numbers on screen must match the narration

- The script's numbers (cost per session, p95, cached-token share, the 40% saving) come from `../01-curriculum/numbers-card.md`, which is regenerated from `make replay`, `make report` and the console, never typed by hand.
- If you must re-run the replay (e.g., after a pricing-table update), regenerate the numbers and re-record every capture in that section. Don't patch one lecture.
- Every dollar figure on screen carries a small corner label `Simulated traffic · verify current pricing` (design-system K5 footer). Every latency figure carries `mock LLM latencies` when in offline mode.

### 5.6 Privacy and safety on camera

- Never show real API keys, Langfuse secret keys, OTLP auth headers, project ids or organisation names. Use the dedicated recording project and the redaction layers in 5.2.
- The knowledge base and personas are fictional; still, run demos with `pii.py` masking on, so the course demonstrates its own advice.
- Rotate every key used during recording after the section is done, even if you believe none was shown.

---

## 6. Track B: screencast standards for this course

Follow the production guide, plus:

- **Terminal:** dark theme, 20 pt font, 100×30 columns, cwd shown as `atlas $`, no shell prompt noise. Atlas always logs JSON; set `LOG_LEVEL=WARNING` when log lines would distract, and `INFO` in 5.5, where log correlation is the lesson.
- **Two windows max:** editor left, terminal right. Browser (Langfuse/Grafana/Ops Console) in a third OBS scene switched to when the result is shown.
- **Type, don't paste,** for the first occurrence of every new API (`TracerProvider`, `@observe(as_type=...)`, `update_current_generation(...)`, `litellm.cost_per_token(...)`, `Router(...)`, `GEval(...)`). Paste for repetition.
- **Version banner:** first slide of every code lecture shows "verified on langfuse 4 / opentelemetry-sdk 1.45 / semconv 0.66 (incubating)".
- **Tests on screen:** always show the pytest summary line; students trust green. `make test` runs offline with no keys; say so on screen in 2.2.
- **YAML lectures** (13.1, 13.2, 9.2's compose file): fold everything except the block being discussed; ≤ 15 visible lines.

---

## 7. Where the OpenAI API is used in production

| Use | Model | Purpose | Estimated cost (estimate; verify current pricing) |
|---|---|---|---|
| Running Atlas live in demos | `gpt-4.1-mini` (default), `gpt-4.1` (escalation), `gpt-5-mini` (routing demos 6.6) | Live requests in 2.3, the live swarm run in 1.4 and 13.5, routing comparisons in 6.6, rehearsals ×3. Most lectures use `OFFLINE=1`, so live usage is small | Low tens of dollars for the whole course, assuming most captures use the offline replay. Set a hard cap at ~$50 on the production project and raise it deliberately if needed |
| **Online judge in demos (8.2, 8.7, 11.4, 14.3)** | DeepEval G-Eval on `gpt-4.1-mini` (or `gpt-4.1` for the "judge quality" comparison in 8.2) | Judging sampled traces from the frozen day. The judge cost is itself a teaching point: the lecture shows it as a line item. Sample rate 10% of ~2,000 fixture sessions ≈ 200 judge calls per full run; rehearsals ×3 plus the drift comparison week | Low tens of dollars. Cap the judge with `JUDGE_MAX_CALLS` in `evals/online_judge.py` during recording so a runaway sampler can't repeat the $4,000 weekend for real |
| Script polish for TTS | `gpt-4.1-mini` via `scene_extractor.py --polish` | Spell out numbers, remove markdown, expand acronyms on first use, apply the course glossary; leave backticked identifiers alone | <$5 for the whole course |
| Optional voiceover TTS (Option A only) | `gpt-4o-mini-tts` | Alternative to HeyGen audio-only export | ≈450 min of narration ≈ 650k characters; check per-character pricing |
| Caption transcripts | `gpt-4o-transcribe` (or Whisper) | Only for live-narrated captures if Udemy auto-captions mangle attribute names; script-based captions cover avatar lectures | <$10 |
| Quiz and lecture-description drafting | `gpt-4.1` | Already drafted in `06-assessments/` and `07-udemy-listing/`; use only for revisions | negligible |

Set a hard monthly spending cap on the OpenAI project used for production, separate from the project used for student-facing examples. The offline mock LLM exists so that production usage stays small; use it.

---

## 8. Assembly template (per lecture)

1. Import: avatar MP4s for the lecture, OBS screencast (narration track + system track), dashboard/trace captures, the section's slide deck (`../10-graphics/slides/section-NN.pptx`, exported to PNG), recap card, and the numbers card for on-screen labels.
2. Timeline order follows the 7 beats: hook (avatar or the cost meter / a red span), promise card, context (avatar or slide), teach (slides with voice), show (screencast or capture), recap (card + voice), bridge (avatar).
3. **Numbers overlay:** wherever the narration quotes a figure, the figure appears as a K5 callout on the capture within 1 s, with the `Simulated traffic · price table dated …` footer.
4. **Zoom-and-hold:** for trace captures, add a 1.5× zoom-in on the attribute or span being discussed, hold 3 s, zoom out. Never zoom on a moving cursor.
5. Music sting on promise card only. No music under investigations (11.2-11.4); the silence while the student thinks is the content.
6. Loudness: normalise the whole lecture to -16 LUFS.
7. Export 1920×1080, H.264, 30 fps, AAC 192 kbps. Name `S06-L6.3A-cost-rollups.mp4`.

---

## 9. Production schedule (12 weeks, batched by section)

| Week | Work | Output |
|---|---|---|
| 1 | Decisions (Section 11 below), avatar and voice check, course pronunciation glossary test, capture-rig test (Langfuse at 150%, Grafana kiosk, Ops Console theme), check the numbers card against a fresh `make replay` and `make report`, record one full pilot lecture (2.3) end to end | Pilot approved |
| 2 | Freeze code repo v1 (`make test` green, `make replay` deterministic), record all Section 2-3 screencasts and captures | S2-S3 raw |
| 3 | Generate S1-S3 avatar scenes, assemble S1-S3, QA, upload as unpublished; record 1.1 with the cost meter | S1-S3 done |
| 4 | Record S4-S5 screencasts + Langfuse captures; generate avatars | S4-S5 raw + avatars |
| 5 | Assemble S4-S5; record S6 (signature section: the most captures and numbers) | S4-S5 done, S6 raw |
| 6 | Record S7 (chaos demo needs the most retakes) and S8 (judge runs live; cap them); generate S6-S8 avatars | S6-S8 raw + avatars |
| 7 | Assemble S6-S8; record S9 (Grafana week: compose stack, dashboard, alert firing) | S6-S8 done, S9 raw |
| 8 | Record S10 and **S11 incident labs** (three rehearsed investigations from the solution-free checkout), generate S9-S11 avatars, assemble S9 | S9 done, S10-S11 raw |
| 9 | Assemble S10-S11; record S12 (four backends, one trace) and S13 (Docker, collector, CI gate, chaos) | S10-S11 done, S12-S13 raw |
| 10 | Record S14 capstone (two sessions), S15; generate avatars; re-record 1.1 if the capstone console changed | S12-S15 raw |
| 11 | Assemble S12-S15, promo video, course image | All videos done |
| 12 | Full QA pass, captions review (attribute names!), quizzes and coding exercises entered in Udemy, landing page, publish | Live |

Buffer: none is built in. If any week slips, move Section 12 (portability: LangSmith, Phoenix) to a free update in month 2 and keep 12.5 (the decision matrix) at launch.

---

## 10. QA additions for this course

On top of the production-guide checklist, every lecture with a Track C capture must pass:

- [ ] Span names, attribute names and numbers readable at 25% scale (≈480×270).
- [ ] No address bar, project id, organisation name, secret key or OTLP header visible in any frame.
- [ ] Every number narrated matches the number on screen and `../01-curriculum/numbers-card.md`.
- [ ] Every dollar figure carries the `Simulated traffic · price table dated …` label; every offline latency carries `mock LLM latencies`.
- [ ] Ops Console theme, page order and date range identical to the previous capture.
- [ ] Incident Part A recorded from a checkout with no `solution.md`; the red herring is present and resolved.
- [ ] Version banner present on code lectures; "incubating, names may change" said or shown wherever a `gen_ai.*` attribute is introduced.

---

## 11. Decisions and inputs required from the course owner

Blocking (needed before Week 1 ends):

| # | Item | Why |
|---|---|---|
| 1 | Narration option: A (fully synthetic) or B (hybrid, recommended) | Determines HeyGen credits, recording time and whether the incident investigations sound live |
| 2 | Confirm the Course 1-3 HeyGen avatar ID and voice ID are reused (or provide new ones and accept the series inconsistency) | Batch generation cannot start without them |
| 3 | HeyGen plan with API access and a credit budget for ≈235 generated minutes | Confirms the pipeline in Course 3's `tools/heygen_batch.py` can run |
| 4 | OpenAI project for production with a spending cap (suggest ~$50), separate from student examples; decision on the judge model (`gpt-4.1-mini` vs `gpt-4.1`) for 8.2 | Cost control; the judge model affects the numbers narrated in Sections 8 and 14 |
| 5 | Dedicated Langfuse recording organisation and project (`atlas-course`), Cloud region choice | Track C redaction rule 2 |
| 6 | Fixture day (decided: seed 7, Monday 2026-09-14, Decision O1) and the pricing-table date pinned in `pricing.py`; re-verify prices before recording | Every number in Sections 6-9, 11 and 14 derives from it |
| 7 | Brand: confirm the design system applies unchanged; Ops Console theme file signed off | Consistency and Track C rule 4 |
| 8 | Whether to disclose the AI avatar in lecture 1.5 and the description | Udemy policy (verify) |

Non-blocking (needed by Week 6):

| # | Item |
|---|---|
| 9 | LangSmith and Arize Phoenix accounts (free tiers) for Section 12 captures |
| 10 | GitHub public repository name for the student code (README links must be final before recording S2); a deliberately failing PR prepared for 13.3 |
| 11 | A machine with Docker Desktop that can run Langfuse + OTel Collector + Prometheus + Grafana together for Sections 9 and 13 (check RAM; Langfuse self-host has several services) |
| 12 | A second machine or VM (Windows if you record on macOS, or vice versa) to record the setup lecture's OS differences |
| 13 | Udemy instructor profile, payout method, and premium instructor application if not already done |

Hardware and software (Option B):

- Dynamic or condenser USB microphone with pop filter, closed-back headphones, quiet room.
- OBS Studio with scenes for `Code`, `Code+Terminal`, `Browser (Langfuse)`, `Browser (Grafana kiosk)`, `Ops Console`, each with its redaction mask sources saved; CapCut or DaVinci Resolve; slides from `slide_builder.py` (python-pptx) with the D1-D12 masters in `../10-graphics/diagrams/`.
- Docker Desktop with enough memory for the self-hosted stack.
- A large-cursor OS setting for Track C.

---

## 12. Tools used (by reference)

| File (in `../../voice-ai-agents-course/09-production/tools/`) | Purpose | Use here |
|---|---|---|
| `scene_extractor.py` | Parses lecture scripts, extracts `[AVATAR]` blocks, optionally polishes text for TTS with OpenAI, writes scene manifests | Run with this course's `02-lecture-scripts/` paths and `--out 09-production/scenes/`; pass the course glossary (check the script's glossary path option; if it hard-codes `pronunciation.json`, add a `--glossary` flag rather than copying the file) |
| `heygen_batch.py` | Generates one HeyGen video per scene from a manifest, polls status, downloads MP4s, resumes safely | Unchanged; `--download-dir 09-production/generated/SXX` |
| `pronunciation.json` | Course 3's term → spoken form glossary | Superseded by `09-production/pronunciation.observability.json` for this course (§4.1) |
| `transcript_to_srt.py` | Converts agent conversation events to SRT | Not used (no call demos) |
| `requirements.txt` | Python dependencies for the tools | Install once in a tools venv shared across courses |

All tools read secrets from environment variables (`HEYGEN_API_KEY`, `OPENAI_API_KEY`). HeyGen endpoint paths and limits are the ones documented at the time Course 3's tools were written; the scripts print the URL they call so a mismatch is obvious. Verify against the HeyGen API reference before the first batch.
