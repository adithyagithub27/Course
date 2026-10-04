# HeyGen Production Guide — AI Agent Testing & Evaluation

> **Course:** AI Agent Testing & Evaluation (Udemy) — Course 2 in this repo. The rules in this guide (7-beat structure, tone, scene types, QA bar) are shared by Courses 3 and 4.
> **Format:** 55 lectures, 400 minutes of lectures (6 h 40 min), 3–8 minutes each, avatar-presented with mixed visuals. Source of truth for IDs, titles and durations: `01-curriculum/full-curriculum.md`.
> **Scripts:** `02-course-content/section-XX-slug.md`, one file per module (decision T5).
> **Last updated:** 2026-10-04

---

## Production Stack

| Tool | Role |
|---|---|
| **HeyGen** | Avatar presenter — generates talking-head clips from the `[AVATAR]` blocks of the scripts |
| **OBS Studio** | Screen recordings — code demos, terminal sessions, dashboards (`03-demos/` specs) |
| **SVG diagrams + slide builder** | Master diagrams D1–D16 in `10-graphics/diagrams/`; slide decks generated from the `[SLIDE]` cues (see "Visual Assets" below) |
| **CapCut / DaVinci Resolve** | Assembly and editing — stitch avatar + slides + diagrams + demos |
| **Udemy** | Final publishing platform |

Shared production tools (used by all three courses) live in `voice-ai-agents-course/09-production/tools/`: `scene_extractor.py` (scripts → HeyGen scene manifest), `heygen_batch.py generate|poll` (submit and download, resumable), `slide_builder.py` (decks), `pronunciation.json` (spoken-form glossary; add terms there, never inline in scripts). Secrets come only from environment variables: `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, `OPENAI_API_KEY`.

---

## The 7-Beat Lecture Structure

Every lecture follows exactly seven beats. No exceptions.

| Beat | Duration | Visual | Purpose |
|---|---|---|---|
| **1. HOOK** | 10–15 s | Failure / problem visual | Open with pain or surprise |
| **2. PROMISE** | 5 s | Title card + outcome | "By the end you'll be able to…" |
| **3. CONTEXT** | 30–60 s | Architecture diagram | Set the scene — where does this fit? |
| **4. TEACH** | 3–5 min | Diagrams + code highlights | Core concept, 2–3 sub-points max |
| **5. SHOW** | 2–4 min | Screen recording | Live demo proving the concept |
| **6. RECAP** | 30–45 s | 3-bullet summary card | Lock it in |
| **7. BRIDGE** | 10–15 s | Next-up card | Tease the next lecture |

### Why This Works

- The **hook** earns attention before you ask for it.
- The **promise** tells the viewer exactly what they'll walk away with.
- **Context** anchors the idea inside the bigger picture so nothing feels random.
- **Teach** delivers the concept — two to three sub-points, no more.
- **Show** proves the concept with a real demo. Seeing is believing.
- **Recap** cements the key takeaways while they're fresh.
- **Bridge** creates momentum into the next lecture.

---

## Word Budget

| Metric | Value |
|---|---|
| Speaking rate | ~140 words per minute |
| 3-minute lecture | ~420 spoken words |
| 6-minute lecture | ~840 spoken words |
| 8-minute lecture | ~1,120 spoken words (less in screencasts: demo output, typing and dwell fill the rest) |

Count your words. If a script runs long, cut — don't speed up.

---

## Production Rules

1. **Avatar never talks >60 seconds (about 140 words) without a visual change (decision A3).** Cut to a diagram, code, terminal, or different angle. Talking heads lose attention fast.

2. **Every lecture opens with a hook — NEVER "Hi guys, welcome back" or "Welcome back" (decision A4).** Start with a problem, a failure, a surprising stat, or a provocative question. Earn the viewer's next 30 seconds.

3. **One idea per lecture.** If the title needs the word "and," split it into two lectures. Focused lectures get higher completion rates.

4. **Show before tell.** Demo the result or show the failure in the first 60 seconds. Then explain the mechanism. Payoff first, theory second.

5. **Visual change every 15–30 seconds.** New slide, new code highlight, new diagram element, zoom, or scene cut. The screen should never be static for more than 30 seconds.

6. **No captions/subtitles as the primary visual.** Captions are supplementary. The primary visual must be a diagram, code, demo, or avatar.

7. **Same avatar, voice, colors, and fonts across ALL lectures.** Visual consistency builds trust. Never switch mid-course.

8. **Audio: –16 LUFS loudness target.** Normalize all final exports. Viewers watch on laptops and phones — consistent loudness matters.

---

## Tone Rules

### Voice & Language
- **Second person always.** "You" — never "we shall" or "one might."
- **Short sentences.** One clause each where possible. Punch, don't meander.
- **Conversational, not academic.** Write like you're explaining to a sharp colleague over coffee, not presenting at a conference.
- **Real-world analogies.** Compare abstract concepts to things people already understand.

### Rhythm & Engagement
- **Use a number or concrete example every 45 seconds.** Use real numbers from the course repo ("pass rate dropped from 100% to 70%", "routing saved 29%"), never invented statistics. An outside statistic needs a source or an inline "(verify: source)" note (decision A6).
- **Say payoff before theory.** "One faithfulness check would have blocked this deploy" — THEN explain the mechanism. People listen harder when they know why it matters.
- **Questions to camera every 60–90 seconds.** "So what happens next?" "Think about this for a second…" "Why would that matter?"
- **Engaging hooks throughout.** "Imagine…" / "Here's where this fails…" / "Let's see this in action…" / "Watch what happens when…"

### Banned Phrases
- ~~"Basically"~~
- ~~"So yeah"~~
- ~~"As I mentioned earlier"~~
- ~~"In this video we will look at"~~
- ~~"Without further ado"~~
- ~~"Let's dive in"~~ (unless genuinely diving into a demo)
- ~~"Hi guys, welcome back"~~
- ~~"Before we get started"~~
- ~~"Welcome back"~~

If you catch yourself writing filler, delete the sentence and rewrite with a concrete fact or example.

---

## Scene Types

Each scene type has specific production requirements:

| Scene Type | Max Duration | Production Notes |
|---|---|---|
| **Avatar talking to camera** | 60 s continuous | Use for hooks, bridges, and transitions between concepts. Never exceed 60 s without a cut. |
| **Architecture diagram + voiceover** | 30–90 s | Build the diagram progressively — animate elements appearing. Don't show the full diagram at once. |
| **Code on screen + voiceover** | 60–120 s | Dark IDE theme (VS Code Dark+). Highlight the relevant 5–15 lines. Use zoom/callouts for key lines. |
| **Terminal output + voiceover** | 30–60 s | Dark terminal. Show the command, then the output. Pause briefly on key output lines. |
| **Agent trace visualization + voiceover** | 60–120 s | Show the agent's decision path step by step. Color-code: green = correct, red = failure, yellow = uncertain. |
| **Dashboard / metrics + voiceover** | 30–60 s | Clean charts. One metric per chart. Annotate the key number with a callout. |
| **Before/after comparison** | 30–60 s | Split screen or sequential. Label clearly: BEFORE (red tint) / AFTER (green tint). |
| **Failure demo** | 30–90 s | Red highlights, red border. Show the failure clearly before explaining the fix. |
| **Title card / transition** | 3–5 s | Consistent template. Course colors. Brief music sting. |
| **Recap card (3 bullets)** | 15–30 s | Three bullet points max. Large text. Read each bullet aloud. |

---

## Batch Production Workflow

Work one module (script section) at a time: extract scenes, generate, review, record screencasts, assemble, QA, then move on. Never generate the whole course in HeyGen before Module 3 has passed review (`CLAUDE.md`).

### Phase 1: Scripts
1. The module's script is `02-course-content/section-XX-slug.md` (all 55 lectures exist). Review it against this guide and `SCRIPT-TEMPLATE.md`: 7 beats, word count vs target, hook, recap card (A1), "You can now" card on the last lecture of the module (A2), no avatar run over 140 words (A3).
2. Run the code the lecture shows: `cd 04-code-examples/agent-eval-framework && make test` (204 passed, 5 skipped), then each demo in the lecture's `[SCREEN]`/`[CODE]` cues (`03-demos/README.md` maps lectures to demos). If a library upgrade breaks a test, pin the version in `pyproject.toml`; don't rewrite scripts mid-recording.

### Phase 2: Extract avatar scenes
3. `python voice-ai-agents-course/09-production/tools/scene_extractor.py 02-course-content/section-03-first-eval.md --out 09-heygen/scenes/section-03.json --polish`
   Only `[AVATAR]` blocks go to HeyGen; every other cue becomes a slide, screencast or B-roll.

### Phase 3: Generate
4. Pilot: `python voice-ai-agents-course/09-production/tools/heygen_batch.py generate 09-heygen/scenes/section-03.json --limit 3`, review lip sync and pronunciation, then the full batch.
5. `heygen_batch.py poll 09-heygen/scenes/section-03.json --download-dir 09-heygen/generated --wait`. Files are named `S{section:02}/{lecture_id}-{beat}.mp4`.

### Phase 4: Visuals and screencasts
6. Build the module's slide deck from the `[SLIDE]` cues (see Visual Assets) and check every slide against `10-graphics/slide-deck-outline.md`.
7. Record all screencasts for the module with OBS in one session from the `03-demos/demo-scripts/` specs (same layout, font size and terminal theme).

### Phase 5: Assemble
8. Assemble in CapCut or DaVinci Resolve: avatar clips + slides + diagrams + screencasts + title, recap and next-up cards.
9. Background music low (–24 LUFS under voice).

### Phase 6: QA, export, log
10. QA against the script (checklist below), export **1920×1080, H.264, 30 fps, –16 LUFS**, upload to Udemy with the module/lecture mapping.
11. Add one line per exported lecture to `BUILD_LOG.md` (ID, date, status). Commit manifests and status files; never commit MP4s.

---

## Visual Assets

- **Master diagrams:** SVG files in `10-graphics/diagrams/` (`D{n}-{slug}.svg`, build steps as `D{n}-step{k}.svg`), D1–D16, listed in `10-graphics/diagrams/index.json` and mapped to lectures in `10-graphics/slide-deck-outline.md`. Rebuild with `python 10-graphics/diagrams/_src/build_diagrams.py`. Palette, type and scene kits K1–K7: `10-graphics/design-system.md` (decision A7).
- **Slide decks:** generated from the scripts' `[SLIDE n: ...]` cues, one PPTX per module:
  `python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content`
  (add `--section 06` for one module). A cue that names a diagram (for example "D3 build 2") embeds the rendered PNG. Regenerate after any script edit rather than hand-editing decks.
- There are no separate `scene-plans/` or `visual-specs/` folders (decision T9): the `[SLIDE]`/`[SCREEN]` cues in the scripts plus `slide-deck-outline.md` are the visual spec.

---

## File Layout

```
02-course-content/
│   section-00-welcome.md … section-15-career.md     ← lecture scripts (Course 3/4 cue format)
03-demos/
│   README.md, demo-scripts/demo-NN-*.md             ← screencast specs with real output
09-heygen/
│   ├── PRODUCTION-GUIDE.md                          ← this file
│   ├── SCRIPT-TEMPLATE.md                           ← the script format
│   ├── avatar-config/PENDING.md                     ← avatar choice (IDs live in env vars)
│   ├── voice-config/PENDING.md                      ← voice choice
│   ├── scenes/section-XX.json                       ← manifests from scene_extractor.py (committed)
│   └── generated/S{section:02}/{lecture_id}-{beat}.mp4   ← HeyGen output (git-ignored)
10-graphics/
    ├── design-system.md, slide-deck-outline.md
    ├── diagrams/ (D1–D16 SVG, index.json)
    └── slides/section-XX.pptx                       ← generated decks
```

---

## Quality Bar

Before any lecture ships, it must pass this checklist:

- [ ] Opens with a hook that creates curiosity or tension
- [ ] One clear idea — a viewer could summarize it in one sentence
- [ ] Demo or concrete example within the first 90 seconds
- [ ] Visual changes at least every 30 seconds
- [ ] No filler phrases
- [ ] `[SLIDE n: Recap]` card with exactly 3 bullets (each under 10 words) before the spoken recap
- [ ] Last lecture of the module ends with a `[SLIDE n: You can now]` card
- [ ] Version banner on every code lecture; every price says "verify current pricing"
- [ ] Bridge teases the next lecture
- [ ] Audio at –16 LUFS
- [ ] 1920×1080, H.264, 30 fps

If a lecture fails any item, fix it before export.
