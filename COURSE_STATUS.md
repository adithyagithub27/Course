# Course Production Status — Course 2: AI Agent Testing & Evaluation

> **Last updated:** 2026-10-04 (after the 2026-10-01 review and fix plan T1–T9)
>
> Module titles, lecture counts and minutes come from `01-curriculum/full-curriculum.md`. Courses 3 and 4 track their status in their own folders; `CLAUDE.md` has the one-line summary for each course.

---

## Status Legend

| Status | Meaning |
|---|---|
| Not Started | Work has not begun |
| In Progress | Actively being worked on |
| Drafted, in review | Written; awaiting the coordinator's QA pass |
| Done | Finalized against the code (may still be re-checked before recording) |
| Blocked | Waiting on a dependency or owner decision |

---

## Totals

| Item | Value |
|---|---|
| Modules / lectures | 16 / **55** |
| Runtime | **400 min (6 h 40 min)** |
| Scripts | 55 of 55 written in `02-course-content/` (Course 3/4 cue format) — in review |
| Student code | Done: `04-code-examples/agent-eval-framework/`, **204 offline tests pass** (5 live skipped), 61 demos run offline |
| Labs / projects | 12 lab guides + Thought Exercise 2.1 / 5 projects — rewritten on the current APIs, code verified offline |
| Demo specs | 50 specs in `03-demos/demo-scripts/` (index `03-demos/README.md`) |
| Graphics | 16 master diagrams (D1–D16) done; slide-deck outline done; PPTX decks not generated yet |
| HeyGen | Not started (avatar and voice choice pending) |
| Exported lectures | 0 (`BUILD_LOG.md`) |

---

## Module-Level Status

| Module | Title (curriculum) | Lectures / min | Curriculum | Scripts | Code & demos | Labs / projects | Demo specs | Graphics | HeyGen | QA / export |
|---|---|---|---|---|---|---|---|---|---|---|
| M00 | Welcome & Course Overview | 2 / 8 | Done | Drafted, in review | Done | Done (setup (in Lab 1.1)) | 01, 07 | Diagrams done; deck pending | Not Started | Not Started |
| M01 | AI Agents: What You Need to Know for Testing | 4 / 28 | Done | Drafted, in review | Done | Done (Lab 1.1) | 08–10 | Diagrams done; deck pending | Not Started | Not Started |
| M02 | Why Traditional Testing Breaks for AI Agents | 3 / 21 | Done | Drafted, in review | Done | Done (Thought Exercise 2.1) | 11–13 | Diagrams done; deck pending | Not Started | Not Started |
| M03 | Your First Agent Evaluation | 4 / 30 | Done | Drafted, in review | Done | Done (Lab 3.1, Project 1) | 02, 14–16 | Diagrams done; deck pending | Not Started | Not Started |
| M04 | Evaluation Metrics Deep Dive | 4 / 32 | Done | Drafted, in review | Done | Done (Lab 4.1) | 17–20 | Diagrams done; deck pending | Not Started | Not Started |
| M05 | RAG Agent Evaluation | 4 / 30 | Done | Drafted, in review | Done | Done (Lab 5.1, Project 2) | 21–24 | Diagrams done; deck pending | Not Started | Not Started |
| M06 | Testing Tool Calling & MCP | 4 / 28 | Done | Drafted, in review | Done | Done (Lab 6.1, Project 3) | 25–28 | Diagrams done; deck pending | Not Started | Not Started |
| M07 | Multi-Agent System Testing | 3 / 24 | Done | Drafted, in review | Done | Done (Lab 7.1) | 29–31 | Diagrams done; deck pending | Not Started | Not Started |
| M08 | Security Testing & Red Teaming | 5 / 40 | Done | Drafted, in review | Done | Done (Lab 8.1, Project 4) | 03, 32–35 | Diagrams done; deck pending | Not Started | Not Started |
| M09 | Agent Observability & Tracing | 3 / 24 | Done | Drafted, in review | Done | Done (Lab 9.1) | 04, 36–37 | Diagrams done; deck pending | Not Started | Not Started |
| M10 | Performance & Reliability Testing | 3 / 21 | Done | Drafted, in review | Done | Done (Lab 10.1) | 38–40 | Diagrams done; deck pending | Not Started | Not Started |
| M11 | Regression Testing & Synthetic Data | 3 / 24 | Done | Drafted, in review | Done | Done (Lab 11.1) | 41–43 | Diagrams done; deck pending | Not Started | Not Started |
| M12 | CI/CD for Agent Evaluation | 3 / 21 | Done | Drafted, in review | Done | Done (Lab 12.1) | 05, 06 | Diagrams done; deck pending | Not Started | Not Started |
| M13 | Production Monitoring & Governance | 3 / 21 | Done | Drafted, in review | Done | Done (Lab 13.1) | 44–46 | Diagrams done; deck pending | Not Started | Not Started |
| M14 | Enterprise Capstone | 5 / 40 | Done | Drafted, in review | Done | Done (Project 5) | 47–49 | Diagrams done; deck pending | Not Started | Not Started |
| M15 | Career & Next Steps | 2 / 8 | Done | Drafted, in review | Done | Done (30-day plan) | 50 | Diagrams done; deck pending | Not Started | Not Started |

Column notes:
- **Scripts:** all 55 written by the T-W1..3 packages from `14-quality-review/course2-bible.md`; legacy `09-heygen/scripts/` removed. Review against `09-heygen/SCRIPT-TEMPLATE.md` before generating avatar scenes.
- **Code & demos:** `make test` (204 passed, 5 skipped) and `make demos` (61/61) offline. Garak scan configured but **not run** (Lecture 8.5); PyRIT and promptfoo were run.
- **Graphics:** diagrams in `10-graphics/diagrams/` (`index.json`); decks are generated with `python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content` once scripts pass review.

---

## Cross-Cutting Status

### Strategy & positioning

| Deliverable | Status | Notes |
|---|---|---|
| Market research (all courses) | Done | `00-course-strategy/next-course-market-research.md` (2026-09-28) |
| Differentiation and competitor analysis | Done | `00-course-strategy/course-differentiation.md` v2.0 (eight competitors, T8) |
| Personas | Done | Curriculum P1–P4 |

### Udemy and marketing

| Deliverable | Status | Notes |
|---|---|---|
| Title | Done (recommended) | Owner to confirm (`MY_DECISIONS_REQUIRED.md`) |
| Subtitle and description | Drafted | `12-udemy/course-description.md` v2.0 (55 lectures, 6 h 40 min, 16 sections) |
| Positioning, SEO, launch posts, promo script | Drafted | `13-marketing/` refreshed 2026-10-04; no "first"/"only" claims |
| Course image, promo video | Not Started | After the Module 3 pilot |
| Pricing and coupons | Blocked | Owner decision |
| Section and lecture structure on Udemy | Not Started | Mirror the 16 modules |
| Quizzes | Drafted | 14 quizzes in the curriculum |
| Downloadable resources | Drafted | `11-course-assets/` (cheat sheets, test-strategy and scorecard templates, 30-day plan) |

### Student repository

| Deliverable | Status | Notes |
|---|---|---|
| Code, tests, demos | Done | Offline mode (T6), `uv.lock` committed (A10) |
| README and Makefile | Done | |
| CI workflow | Done | `.github/workflows/agent-eval.yml` |
| Public repo decision | Blocked | Owner decision (hybrid GitHub strategy, Decision 5) |

### Production and launch

| Deliverable | Status | Notes |
|---|---|---|
| Production guide and script template | Done | `09-heygen/PRODUCTION-GUIDE.md`, `SCRIPT-TEMPLATE.md` (2026-10-04) |
| Avatar and voice | Blocked | Owner decision |
| Module 3 HeyGen pilot | Not Started | Never generate the whole course before Module 3 passes review |
| Screencasts, assembly, QA, upload | Not Started | |
| Launch | Not Started | |

---

## Next Steps (in order)

1. Coordinator QA of `02-course-content/` against the template and the code (word counts, A1–A6).
2. Owner decisions in `MY_DECISIONS_REQUIRED.md` (avatar/voice, pricing, live re-capture of numbers).
3. Generate slide decks; review against `10-graphics/slide-deck-outline.md`.
4. Module 3 pilot: scene extraction, 3-scene HeyGen test, screencasts from `03-demos/`, assembly, QA, `BUILD_LOG.md`.
5. Remaining modules one at a time.
