# Script Template — AI Agent Testing & Evaluation

> The format for every Course 2 lecture script (decision T5). It is the same cue format Courses 3 and 4 use, so `voice-ai-agents-course/09-production/tools/scene_extractor.py` and `slide_builder.py` parse it.
> Scripts live in `02-course-content/section-XX-slug.md`, **one file per module**, lectures in curriculum order. Rules for tone, beats and QA: `PRODUCTION-GUIDE.md`. Facts (files, commands, outputs, versions): `14-quality-review/course2-bible.md` and the student repo; if a script and the code disagree, the code wins.

---

## Section File Header

```markdown
# Section N: <Module title from the curriculum>

> **Course:** AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python (Course 2)
> **Section runtime:** ≈NN min (K lectures)
> **Source of truth:** `01-curriculum/full-curriculum.md` (Module NN); `14-quality-review/course2-bible.md` for code facts.
> **On-screen footer for every code or API slide:** "Verified: openai 2.54.0 | deepeval 4.2.7 | … (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1."
> **Cue legend:** see below. Commands run from `04-code-examples/agent-eval-framework/`. Outputs are offline runs (`OFFLINE=1`) unless a note says otherwise.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| N.1 | <title> | SL / SC / DM / BA / LAB | 7:00 | ~900 |
```

Types: SL slide/teach, SC screencast, DM demo, BA build-along, LAB lab intro, QZ quiz intro.

## Cue Legend

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. **Only these blocks go to HeyGen.** Keep each run under ~140 spoken words (about 60 s) before the next cue (A3). |
| `[SLIDE n: title]` | Full-screen slide. Bullets under the cue are the exact slide text (≤ 12 words per slide, 3–5 bullets). A line `Diagram: D4 build 3` embeds that master diagram build. |
| `[SCREEN: ...]` | OBS screen recording; the voice-over continues. Name the real file, command and what to highlight. |
| `[CODE: ...]` | Code revealed line by line; the fenced block under it is the exact text (≤ 15 lines). |
| `[DEMO: ...]` | Live run of a demo; paste the real output from `03-demos/` or the bible. |
| `[B-ROLL: ...]` | Cutaway or motion graphic, described concretely. |
| `[PAUSE]` | One beat of silence (about one second). |

Narration after a non-avatar cue is voice-over on that visual.

---

## Blank Lecture Template

````markdown
## Lecture N.M — <exact title from the curriculum>

| Field | Value |
|---|---|
| ID | N.M |
| Title | <exact title> |
| Type | <SL / SC / DM / BA> (<one-line description>) |
| Target duration | M:00 (<target words at 140 wpm>; <counted> spoken) |
| Learning objectives | 1. … 2. … 3. … |
| Prerequisites | <previous lecture or module> |
| Files used | `demos/mNN_slug.py`; `<module files>`; Diagram D<n> |

### Script

[AVATAR]
<HOOK, 10–15 s: a real failure, a real number from the repo, or a question. No greeting, no "Welcome back".>

[SLIDE 1: <Lecture title>]
- <outcome 1>
- <outcome 2>
- <outcome 3>

By the end of this lecture, you'll be able to <concrete outcome>.

[SLIDE 2: Verified for this lecture]
- `<package version>` and `<package version>`
- <what runs offline / what needs a key>

<CONTEXT, 30–60 s: where this fits in the course; which failure modes (T2) or dimensions (T3) it serves.>

[SLIDE 3: <teaching point 1, 5–8 word title>]
Diagram: D<n> build <k>

<TEACH point 1. A number or concrete example every ~45 s. A question to camera every 60–90 s.>

[CODE: `<file path>`, <what to highlight>]
```python
<exact excerpt from the repo, ≤ 15 lines>
```

<voice-over on the code>

[SCREEN: Terminal, `uv run python demos/mNN_slug.py`. Highlight <line>.]

<SHOW: narrate the real output.>

```
<real output pasted from the bible / 03-demos spec>
```

[SLIDE n: Recap]
- <bullet under 10 words>
- <bullet under 10 words>
- <bullet under 10 words>

<spoken recap that repeats the three bullets>

[SLIDE n+1: You can now]          ← last video lecture of the module only (A2)
- <ability 1>
- <ability 2>
- <ability 3>

### Recap

<one sentence with the lecture's key numbers>

### Transition

<one or two sentences naming the next lecture by number and title>

### Speaker notes: common student mistakes / Q&A

- <offline vs live caveat for any number shown>
- <items to re-check before recording: prices ("verify current pricing"), UI steps ("verify"), counts that change>
- <likely student questions with short answers>

---
````

---

## Checklist Before Submitting a Script

- [ ] Header, field table, `### Script`, `### Recap`, `### Transition` present (the parsers need them)
- [ ] Title, ID and target duration match the curriculum exactly
- [ ] Hook in the first 15 s: a failure, a real number or a question; no greeting, no banned phrase
- [ ] Version slide or banner on every code lecture, with versions from `uv.lock`
- [ ] Every file, function, command and output exists in the student repo (paste outputs; never invent them)
- [ ] Taxonomies exactly as frozen: six failure modes (T2) — hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops; five dimensions (T3) — correctness, faithfulness, relevance, safety, reliability; the five-layer eval pyramid (T4) — unit, component, trajectory, end-to-end evals, production monitoring
- [ ] Running example is TechCorp (`agents/support_agent.py`, five tools); models `gpt-4.1-mini` (agent) / `gpt-4.1` (judge)
- [ ] No `[AVATAR]` run over ~140 words without a cue change (A3); a visual change every 15–30 s
- [ ] Slide-only lecture? Add one short `[SCREEN]` or `[DEMO]` beat backed by a real demo file (A5)
- [ ] `[SLIDE n: Recap]` with exactly 3 bullets under 10 words before the spoken recap (A1); "You can now" card on the module's last lecture (A2)
- [ ] Spoken words within ±10% of 140 × target minutes (screencasts may run shorter: demo output and typing fill the time); if long, cut, don't speed up
- [ ] Every price carries "verify current pricing"; every outside statistic has a source or "(verify: source)", or is removed (A6); offline numbers are labelled offline
- [ ] New terms with tricky pronunciation added to `voice-ai-agents-course/09-production/tools/pronunciation.json`, not spelled out inline

---

## Gold Standard

Lecture 1.4 in `02-course-content/section-01-agents.md` ("The 6 Ways AI Agents Fail") is the reference: a hook from a real recorded failure, D1 built one failure mode at a time, the real `m01_failure_gallery.py` output, the check that catches each mode, recap card and transition. Match its specificity and pacing.
