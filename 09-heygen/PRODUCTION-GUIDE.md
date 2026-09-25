# HeyGen Production Guide — AI Agent Testing & Evaluation

> **Course:** AI Agent Testing & Evaluation (Udemy)
> **Format:** ~60 lectures, 6–10 minutes each, avatar-presented with mixed visuals
> **Last updated:** 2025-01-XX

---

## Production Stack

| Tool | Role |
|---|---|
| **HeyGen** | Avatar presenter — generates talking-head clips from scripts |
| **OBS Studio** | Screen recordings — code demos, terminal sessions, dashboards |
| **Figma / Canva** | Diagrams, architecture visuals, slide graphics, recap cards |
| **CapCut / DaVinci Resolve** | Assembly and editing — stitch avatar + diagrams + demos |
| **Udemy** | Final publishing platform |

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
| 6-minute lecture | ~840 spoken words |
| 8-minute lecture | ~1,000–1,100 spoken words |
| 10-minute lecture | ~1,400 spoken words |

Count your words. If a script runs long, cut — don't speed up.

---

## Production Rules

1. **Avatar never talks >60 seconds without a visual change.** Cut to a diagram, code, terminal, or different angle. Talking heads lose attention fast.

2. **Every lecture opens with a hook — NEVER "Hi guys, welcome back."** Start with a problem, a failure, a surprising stat, or a provocative question. Earn the viewer's next 30 seconds.

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
- **Use a number or concrete example every 45 seconds.** "This cuts false positives by 60%." "Three out of five agents fail here."
- **Say payoff before theory.** "This saves 40% of debugging time" — THEN explain the mechanism. People listen harder when they know why it matters.
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

Produce in batches — never one lecture at a time.

### Phase 1: Script All
1. Write **ALL scripts** for a module before generating any video.
2. Review every script against this guide's tone rules and the 7-beat structure.
3. Confirm word counts are within budget.

### Phase 2: Group Scenes by Type
4. Extract all avatar scenes across the module → batch-generate in HeyGen.
5. Extract all diagram scenes → batch-create in Figma/Canva.
6. Extract all code/terminal demos → list them for OBS recording.

### Phase 3: Record
7. Record **all screen demos with OBS in one session per module.** Consistent screen layout, font size, and terminal theme.
8. Generate all avatar clips in HeyGen. Group by similar length for efficient batching.

### Phase 4: Assemble
9. Assemble in CapCut or DaVinci Resolve: avatar scenes + diagrams + demos + transitions.
10. Add background music (low, –24 LUFS under voice).
11. Add title cards and recap cards from templates.

### Phase 5: QA
12. QA each assembled video against the original scene plan:
    - [ ] Every beat present?
    - [ ] No avatar segment >60 s without visual change?
    - [ ] Visual change every 15–30 s?
    - [ ] Hook in first 15 s?
    - [ ] Word count matches target duration?
    - [ ] Audio normalized to –16 LUFS?

### Phase 6: Export & Publish
13. Export: **1920×1080, H.264, 30 fps, –16 LUFS audio.**
14. Upload to Udemy with correct section/lecture mapping.

---

## File Naming Convention

```
09-heygen/
├── scripts/
│   ├── M01-L01-what-is-agent-testing.md
│   ├── M01-L02-why-agents-are-different.md
│   └── ...
├── scene-plans/
│   ├── M01-L01-scene-plan.md
│   └── ...
├── visual-specs/
│   ├── M01-L01-diagrams.md
│   └── ...
├── generated/
│   ├── M01-L01-avatar-hook.mp4
│   └── ...
├── review/
│   └── ...
├── final/
│   └── ...
├── avatar-config/
│   └── PENDING.md
├── voice-config/
│   └── PENDING.md
├── PRODUCTION-GUIDE.md       ← this file
└── SCRIPT-TEMPLATE.md
```

---

## Quality Bar

Before any lecture ships, it must pass this checklist:

- [ ] Opens with a hook that creates curiosity or tension
- [ ] One clear idea — a viewer could summarize it in one sentence
- [ ] Demo or concrete example within the first 90 seconds
- [ ] Visual changes at least every 30 seconds
- [ ] No filler phrases
- [ ] Recap with exactly 3 bullet points
- [ ] Bridge teases the next lecture
- [ ] Audio at –16 LUFS
- [ ] 1920×1080, H.264, 30 fps

If a lecture fails any item, fix it before export.
