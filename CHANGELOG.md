# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.0] - 2026-10-02

Course 2 review fixes (`14-quality-review/2026-10-01-fix-plan.md`, decisions T1–T9 and A1–A10). Docs package T-DOCS, completed 2026-10-04.

### Changed
- `01-curriculum/full-curriculum.md` v2.0: real totals (**55 lectures, 400 min = 6 h 40 min**, 14 quizzes, 35 interview questions, 15 scenarios); TechCorp support agent replaces TechGear (T1); six failure modes, five dimensions and the five-layer eval pyramid each defined once (T2–T4); every "Code Examples Needed" block replaced by real student-repo files and exact excerpts (OpenAI tool calling, DeepEval 4.2 `SingleTurnParams`, RAGAS 0.4 `SingleTurnSample`/`reference`, Langfuse v4 `observe`/`propagate_attributes`/`create_score`, official OpenTelemetry `gen_ai_attributes`, mcp 2.x `MCPServer`); "Demonstrations Planned" name the real `demos/*.py` files and outputs; routing saving 29.1% (not 50%), prompt diet 42.8%; models `gpt-4.1-mini`/`gpt-4.1` with "verify current pricing" (A8); enterprise scenarios labelled illustrative (A6); lab index aligned with `07-labs/`; Lab 13.1 added; capstone quiz rewritten to match the five-rule gate.
- `07-labs/`: all 12 labs rewritten on the current APIs with student code verified offline; headers renamed to module lab IDs (Lab 1.1 … Lab 13.1, filenames kept); Lab 7.1 is the 3-agent Supervisor/Research/Writing system with four failure injections; Lab 9.1 on Langfuse v4; Lab 5.1 on RAGAS 0.4; Lab 11.1 uses DeepEval's Synthesizer.
- `08-projects/`: Projects 1–5 rewritten to the code (Project 1's three metrics; Project 2's 14 documents / 15 cases; Project 3's six-tool operations agent; Project 4's SecureBank v1/v2 with the real BRT-10/BRT-05 findings; Project 5 and `ARCHITECTURE.md` aligned to `capstone/platform.py` and the SHIP/BLOCK gate).
- `03-demos/demo-scripts/`: the six demo scripts updated to real files, commands and outputs.
- `09-heygen/PRODUCTION-GUIDE.md` (dated, scripts in `02-course-content/`, no `scene-plans/`/`visual-specs/` (T9), Visual Assets section, shared tools workflow) and `SCRIPT-TEMPLATE.md` (Course 3/4 cue format, T2 taxonomy); avatar/voice config files point to env-var IDs.
- `10-graphics/design-system.md` v2.0: generalised for Courses 2–4; diagram tooling and asset naming aligned.
- `11-course-assets/`: cheat sheets on DeepEval 4.2/RAGAS 0.4; test-strategy template with the five pyramid layers as rows (Lecture 2.3); scorecard template on the five dimensions and the release gate.
- Positioning (T8): `00-course-strategy/course-differentiation.md` v2.0 lists the eight competitors and positions on full lifecycle + CI/CD gates + enterprise scenarios; `12-udemy/course-description.md` and `13-marketing/` drop "first"/"only" claims, match the 16-section structure, point setup to Lecture 0.2 and use the real runtime.
- Root docs: `README.md`, `COURSE_STATUS.md` (real per-module status), `COURSE_DECISIONS.md` (Decisions 2 and 6 superseded; Decisions 8–10 added, incl. T1–T9 by reference), `PRODUCTION_CHECKLIST.md`, `MY_DECISIONS_REQUIRED.md` (items 9–11: openai 2.x vs 3.x, Garak with torch, live re-capture of offline numbers).

### Added
- Lecture 8.5 "Beyond promptfoo: Garak and PyRIT" (8 min) with objectives, demos and quiz question Q4 (T7).
- 44 new demo recording specs (`demo-07` … `demo-50`) and the index `03-demos/README.md`.
- `10-graphics/slide-deck-outline.md`: master diagrams D1–D16 and a slide map for all 55 lectures, generated from the scripts (T9).
- `11-course-assets/templates/30-day-practice-plan.md` (Lecture 15.2 resource).

### Removed
- Legacy `09-heygen/scripts/` (converted into `02-course-content/` by the script packages).

---

## [0.1.0] - 2026-09-24

### Added
- Initial project structure (16 folders: `00-course-strategy` through `15-release`)
- Course differentiation document
- Complete curriculum (16 modules; then stated as 60 lectures, corrected to 54 + 1 = 55 in 0.2.0)
- Evaluation metrics taxonomy
- Agent testing framework skeleton
- Visual design system
- Marketing strategy documents
- Production pipeline templates
- Project management documents (README, STATUS, DECISIONS, CHECKLIST, CHANGELOG)
