# Full Course Review: Flow, Demos, Slides and Engagement

> **Date:** 2026-10-01
> **Scope:** every lecture script, curriculum, lab, project, production plan and student code repo for the three courses in this repository.
> **Method:** each script was read in full and checked against its curriculum and against `03-code/`. Spoken-word counts, cue density, avatar-run lengths and banned phrases were measured with a script, not estimated. Both student repos' offline test suites were run. Every claim below carries a file reference in the per-course reports:
> - `2026-10-01-course2-agent-testing-review.md`
> - `2026-10-01-course3-voice-review.md`
> - `2026-10-01-course4-observability-review.md`

---

## 1. Verdict in one table

| Course | Status claimed in `CLAUDE.md` | Status found | Flow | Demos | Slides / images | Engagement | Ready to record? |
|---|---|---|---|---|---|---|---|
| **Course 3: Voice AI Agents** (`voice-ai-agents-course/`) | Complete, ready to record | Scripts complete (97/97 lectures). Tests green (211 passed). All quoted WER, latency and cost numbers reproduce. Seven scripts contradict the code. | Good | Good (9 of 13 Section 9 lectures show red before green) | Specified in text only; no built assets | Good | **After a 2 to 3 day prose-to-code reconciliation pass.** |
| **Course 4: Observability** (`agent-observability-course/`) | Complete, ready to record | Scripts complete (105/105). **`make test` is red** (1 of 329 fails). Running-example numbers change mid-course. Sections 4 to 5 teach an instrumentation path the shipped code does not use. The Ops Console the scripts narrate is not built. | Broken at the Section 5 to 6 seam | Specified, but 30+ cited symbols, tests and flags do not exist | Specified in text only; production docs describe a different fixture | Good on paper | **No. Roughly 2 to 3 weeks of code and script reconciliation first.** |
| **Course 2: Agent Testing & Evaluation** (root folders) | Content written; positioning refresh pending | **24% scripted** (13 of 54 lectures). Modules 4 to 15 have no script. Two running examples, three versions of the core taxonomies. Student repo on Langfuse v2, pre-1.0 RAGAS API. Scripts are in a format the HeyGen pipeline cannot parse. | Broken after Module 3 | 6 demo specs for 54 lectures | Design system exists; no scene plans or visual specs | Good in the 13 scripts that exist | **No. About 27 working days of writing before HeyGen.** |

**No course has any built slide, diagram or image.** The repository contains zero PNG, SVG, PPTX, Figma or draw.io files outside `.venv`. "Engaging slides and images" exist today only as `[SLIDE n: ...]` text cues and the diagram list in each `slide-deck-outline.md`. The cues are specific enough to build from in Courses 3 and 4, but building them is unstarted work: roughly 16 master diagrams and 400+ slides per course.

---

## 2. Cross-course measurements

Spoken words were counted from narration lines only (cues, slide bullets, tables and code excluded), at the 140 wpm rate from `PRODUCTION-GUIDE.md`.

| Measure | Course 3 Voice | Course 4 Observability | Course 2 Testing |
|---|---|---|---|
| Lectures in curriculum / scripted | 97 / 97 (115 script blocks incl. Part A/B) | 105 / 105 | 54 / 13 |
| Spoken words | ~85,500 | ~68,900 | ~13,000 |
| Lectures with no `[SCREEN]`, `[CODE]` or `[DEMO]` cue (quizzes excluded) | 33 of 115 (29%) | 34 of 105 (32%) | 0 of 13 |
| Narration runs over ~70 s with no visual change | 31 lectures | 25 lectures | 35 of 107 scenes on a single slide |
| Lectures more than 15% over the word budget | 2 (12.8, 14.2) | 1 (5.7) | 0 |
| Slide-only lectures running 25 to 35% short | 3.1, 3.5, 3.6, 1.5, 15.3, 12.7 | 3.4, 4.2, 14.3 leave over 5 min unscripted | none |
| Banned phrases (`PRODUCTION-GUIDE.md`) | "Welcome back" x3 (5.9, 13.2) | "Welcome back" x2 (4.7, 14.2) | 0 |
| Three-bullet recap card cued in the script | never (recap is a sentence) | never (recap is a sentence) | always |
| Offline test suite | 211 passed | 328 passed, **1 failed** | not runnable offline; every test skips without an API key |

The slide-only share (about 30% of lectures in Courses 3 and 4) is by design: `SL` lectures pair with a following `DM` or `SC` lecture. It is still the largest engagement risk. The production guide's own quality bar asks for a demo or concrete example inside the first 90 seconds of every lecture, and a 7 to 9 minute slide lecture with no screen cue (for example voice 3.6 on turn detection, which is an audio topic) will read as a lecture, not a course.

---

## 3. The ten things to fix first, across all courses

Ranked by how many learners each would hurt and how early.

1. **Course 4: pick one replayed day and regenerate every number.** Sections 1 to 5 narrate a $6.42 / 1,184-conversation day; Sections 6 onward and the labs use the $56.70 / 10,184-request day, which is the one `make replay` produces ($56.28 measured). Lecture 2.4 promises "your answer should be $6.42", which no student will get. Quiz 2 invents a third day. Judge scores, TTFT and SLO figures also disagree between sections and with the store.
2. **Course 4: make `make test` green and fix the two demos that cannot be recorded.** `tests/integration/test_spans.py::test_chat_produces_agent_generation_tool_and_guardrail_spans` fails deterministically. The headline "guards off" demo in 1.1 and 5.6 sets `ATLAS_MAX_STEPS=0` as "unlimited", but `app/agent.py:783` loops `range(1, max_steps + 1)`, so 0 means zero steps. `make replay SCENARIO=cost_spike` (the Makefile's own example, used in 11.2 and 14.3) raises a validation error.
3. **Course 4: rewrite Sections 4 to 5 around the shipped instrumentation, or extend the code.** The code-alongs type `@observe`, `propagate_attributes`, `update_current_generation` and `score_current_trace`; `app/agent.py` uses `tracer.start_as_current_span` with helper setters, which Sections 6, 7 and 14 then show. `CLAUDE.md` says the code wins, so about ten lectures need rewriting.
4. **Course 4: build the Ops Console pages the scripts narrate, or re-cue to Langfuse and Grafana.** The scripts call for a live cost meter, a trace waterfall, a top-10 sessions list, a traffic page with a "last Monday" shadow line and a compare-replays view. The shipped console is five tabs of static tables. About a third of recorded runtime depends on this decision.
5. **Course 3: reconcile the seven scripts that contradict the code.** 7.8 says the mid-call language switch "isn't in the repo" (it is, behind `FOLLOW_CALLER_LANGUAGE=1`), 13.3 and 12.8 say the capstone error handler "only speaks the line" (it already transfers or hangs up), 5.9 uses a `join_waitlist` signature the tool does not have, 4.3 references a `SPELLING_RULES` block that does not exist, 12.2 narrates a `uv.lock` copy the Dockerfile does not do. Full list in the Course 3 report, fix 1.
6. **Course 3: fix the one flow break and the pronoun drift.** Lecture 2.5 ends "See you in Section three" but 2.6 (the quick win) and 2.7 follow. Riley is "it" in Sections 1 to 5 and 11 to 15 and "she" in Sections 6 to 9 (34 occurrences), while 4.5 teaches "one Riley everywhere".
7. **Course 2: decide whether to finish it or cut it to what exists.** 41 lectures (305 minutes), including everything the title promises (RAGAS, promptfoo, Langfuse, CI/CD, capstone), have no script. The marketed 8.5 to 9.5 hours and ~60 lectures do not match the curriculum's 6 h 32 m and 54 lectures. The 13 existing scripts use a `[SCENE n]` format that `scene_extractor.py` does not parse, use the TechGear agent while the code, labs and projects use TechCorp, and teach three different versions of the six failure modes and five quality dimensions.
8. **Course 2: modernise the student repo before writing more scripts.** `requirements.txt` pins `langfuse<3.0`, `deepeval<4.0`, `langchain<0.4`, `openai<2.0`; `lab-04` and `ragas_suite.py` use the pre-0.2 RAGAS API; no test runs offline. Course 4's code is the pattern to copy for Langfuse 4.
9. **All courses: split the long avatar runs and add the recap card.** 31 voice lectures and 25 observability lectures have narration runs over about 70 seconds with no visual change; the production guide's limit is 60 seconds. No script in Courses 3 or 4 cues the three-bullet recap card or the section-end "You can now..." card that the slide outline and QA checklist require.
10. **All courses: make the production documents agree with the scripts.** Course 4's video plan, recording guide and slide outline use tenants, a fixture date and flags that the code does not have, and tell the editor to show `update_current_trace`, which the curriculum bans. Course 3's recording guide and video plan give different lecture-type counts, and the slide outline has no entry for six screencast lectures. Course 2's `COURSE_STATUS.md` shows 0 of 176 items done with module titles that match nothing in the curriculum. There is no `BUILD_LOG.md`, which `CLAUDE.md` requires.

---

## 4. What is working

- **Course 3's structure is the model.** The v1.1 curriculum review was applied: first win in Section 2, failure-first demos ("Break it" lectures), pause-then-solution challenges, a quiz in every technical section, a capstone gate, a domain-swap project and a careers lecture. Every quoted number in 2.7, 9.7, 9.8 and 10.4 reproduces from the code. All five `BROKEN=` failure cases match `s03_hello_agent.py`.
- **Course 4's Section 6 (cost engineering) and Section 11 (incident labs) are the best-designed teaching sequences in the repo:** a single numbers card every lecture reconciles to, evidence exhibits, hypothesis and verdict tables, a one-sentence root cause. The problem is that the code and console do not yet deliver what they describe.
- **Engagement writing is consistently strong where scripts exist:** hooks are failures, stats or questions; promises are measurable; questions to camera and concrete numbers are dense; banned phrases are almost absent. Course 2's 13 scripts are, scene for scene, the most disciplined (hook, promise, 3-bullet recap, bridge every time).
- **Slide cues are buildable.** Courses 3 and 4 specify slide titles, bullets, diagram content and progressive builds; the 16-diagram master list in each `slide-deck-outline.md` plus the scene kits in `10-graphics/design-system.md` are enough for a designer to start.

---

## 5. Recommended order of work

1. Course 4 code fixes (test, step limit, scenario flag) and the single-day number regeneration. Then the Sections 4 to 5 rewrite and the Ops Console decision.
2. Course 3 prose-to-code pass (fix list 1 in its report), the 2.5 bridge, the pronoun, the long avatar runs, the recap cards.
3. Both: regenerate the production docs from the scripts, add `BUILD_LOG.md`, start Section 3 of Course 3 as the pilot per `PRODUCTION-HANDOFF.md`.
4. Course 2: a go/no-go decision on finishing 41 lectures versus relaunching as a shorter course. Either way, freeze one taxonomy and one agent before writing another line.

Each per-course report ends with a numbered fix list with file and line references.
