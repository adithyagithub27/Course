# Production Checklist — Course 2: AI Agent Testing & Evaluation

> **Purpose:** phase-by-phase checklist from discovery to launch. Check items off with a date. Module-level detail: `COURSE_STATUS.md`. Production rules: `09-heygen/PRODUCTION-GUIDE.md`.
>
> **Last updated:** 2026-10-04. Course facts: 16 modules (M00–M15), **55 lectures, 400 min (6 h 40 min)**, 5 projects, 12 labs, 14 quizzes (`01-curriculum/full-curriculum.md`).

---

## Phase 1: Discovery — Done

- [x] Competitor analysis: eight overlapping Udemy courses plus Maven and DeepLearning.AI (`00-course-strategy/next-course-market-research.md` §6, 2026-09-28; `course-differentiation.md` v2.0, 2026-10-04)
- [x] Tool evaluation and pinned versions (`uv.lock`, checked 2026-10-01): openai 2.54.0, deepeval 4.2.7, ragas 0.4.3, langfuse 4.16.0, mcp 2.2.0, opentelemetry-sdk 1.45.0, promptfoo 0.123.1, garak 0.17.0, pyrit 1.1.0
- [x] All tools work together in one environment (Garak and PyRIT in separate environments by design)
- [x] API cost: $0 offline; a few dollars to run the labs live (verify current pricing)
- [x] Personas P1–P4 (curriculum)
- [x] Positioning: full lifecycle + CI/CD gates + enterprise scenarios, no "first"/"only" claims (T8)
- [ ] Validate positioning with 2–3 trusted reviewers

## Phase 2: Content Architecture — Done

- [x] 16 modules, 55 lectures with objectives, types and durations (2026-10-02, incl. Lecture 8.5)
- [x] Runtime reconciled: 400 min (T7; supersedes the 8.5–9.5 h target)
- [x] Frozen taxonomies: six failure modes (T2), five quality dimensions (T3), five-layer eval pyramid (T4)
- [x] 5 projects and 12 labs specified; lab IDs follow modules (Lab 1.1 … Lab 13.1)
- [x] Metric reference: `06-evaluation-frameworks/`, `11-course-assets/cheatsheets/`
- [x] Visual design system (shared by Courses 2–4) and slide-deck outline (`10-graphics/`)
- [ ] Course thumbnail concepts (3 options) — after the Module 3 pilot
- [ ] Owner approval of the visual design system

## Phase 3: Scripts & Code

### Scripts (`02-course-content/`, one file per module)
- [x] All 55 lecture scripts written in the Course 3/4 cue format (T5); legacy `09-heygen/scripts/` removed
- [ ] QA pass per module: 7 beats, hook, word count vs target, recap card (A1), "You can now" card (A2), no avatar run > 140 words (A3), banned phrases (A4), screen beat in slide lectures (A5), no unsourced statistics (A6)
  - [ ] M00 Welcome & Course Overview
  - [ ] M01 AI Agents: What You Need to Know for Testing
  - [ ] M02 Why Traditional Testing Breaks for AI Agents
  - [ ] M03 Your First Agent Evaluation
  - [ ] M04 Evaluation Metrics Deep Dive
  - [ ] M05 RAG Agent Evaluation
  - [ ] M06 Testing Tool Calling & MCP
  - [ ] M07 Multi-Agent System Testing
  - [ ] M08 Security Testing & Red Teaming
  - [ ] M09 Agent Observability & Tracing
  - [ ] M10 Performance & Reliability Testing
  - [ ] M11 Regression Testing & Synthetic Data
  - [ ] M12 CI/CD for Agent Evaluation
  - [ ] M13 Production Monitoring & Governance
  - [ ] M14 Enterprise Capstone
  - [ ] M15 Career & Next Steps

### Code (`04-code-examples/agent-eval-framework/`)
- [x] Five agents, evaluators, security, observability, performance, regression, monitoring, capstone
- [x] Offline mode (mock LLM + mock judge); `make test`: 204 passed, 5 live skipped
- [x] 61 lecture demos run offline (`make demos`)
- [x] `pyproject.toml` + committed `uv.lock` (A10); `requirements.txt` generated for pip users
- [x] CI workflow `.github/workflows/agent-eval.yml`
- [ ] Run the Garak scan once (configured, not yet run) and capture real numbers for Lecture 8.5
- [ ] Test on Windows and macOS (or document platform notes)

### Datasets
- [x] Golden and red-team datasets in the student repo (`datasets/`)
- [x] Five enterprise scenario datasets with one schema (`05-datasets/enterprise-scenarios/`)
- [ ] Dataset license note in the student repo README

### Labs, projects, demo specs
- [x] 12 labs and 5 projects rewritten on the current APIs; student code verified offline (2026-10-02)
- [x] 50 demo recording specs with real output (`03-demos/`)
- [ ] Time each lab with a test student; adjust durations in the lab headers
- [ ] Live re-run (with a key) of the labs whose numbers will be shown live

## Phase 4: Prototype (Module 3 pilot)

- [ ] Owner chooses avatar and voice (`09-heygen/avatar-config/`, `voice-config/`); IDs in env vars only
- [ ] Add Course 2 terms to `pronunciation.json`
- [ ] `scene_extractor.py` on `section-03-first-eval.md`; 3-scene HeyGen pilot
- [ ] Generate the Module 3 slide deck (`slide_builder.py`)
- [ ] Record Module 3 screencasts from demo specs 02, 14, 15, 16
- [ ] Assemble, caption, export at final settings
- [ ] Owner review and explicit go/no-go for full production

## Phase 5: Full Production (one module at a time)

For each module M00–M15: extract scenes → generate avatar clips → generate deck → record screencasts → assemble → QA → export → `BUILD_LOG.md` line per lecture.

- [ ] All avatar clips generated and QA'd (lip sync, audio, artifacts)
- [ ] All screencasts recorded at 1080p from `03-demos/` specs
- [ ] All decks generated; every slide checked against `10-graphics/slide-deck-outline.md`
- [ ] All lectures assembled; audio normalized to –16 LUFS; captions added
- [ ] All 55 lectures exported (1920×1080, H.264, 30 fps)

## Phase 6: Quality Assurance

### Technical
- [ ] Code on screen matches the repository; outputs reproducible (offline numbers labelled offline)
- [ ] Models are `gpt-4.1-mini` / `gpt-4.1`; every price says "verify current pricing"
- [ ] No API keys or secrets visible; throwaway Langfuse project for UI shots
- [ ] Version banners match `uv.lock`

### Educational
- [ ] Each lecture delivers its objectives; flow between lectures is smooth
- [ ] Taxonomies used exactly as frozen (T2, T3, T4)
- [ ] Recap cards and "You can now" cards present

### Visual
- [ ] Text readable at 720p; code font legible
- [ ] Consistent with the design system; captions accurate

## Phase 7: Launch

### Udemy
- [ ] Upload 55 lectures into 16 sections matching the modules; mark preview lectures (suggest 0.1, 1.4, 3.1)
- [ ] Title, subtitle, description, objectives, audience, prerequisites from `12-udemy/course-description.md` (verify Udemy limits)
- [ ] Attach 14 quizzes and downloadable resources (`11-course-assets/`)
- [ ] Welcome and completion messages
- [ ] Thumbnail and promo video (`13-marketing/promo-video-script.md`)

### Marketing
- [ ] Pricing and coupon strategy (owner)
- [ ] LinkedIn sequence (`13-marketing/linkedin-launch.md`), social plan, YouTube teasers
- [ ] Launch date scheduled; first 48 hours monitored

### Post-launch
- [ ] Q&A daily for 2 weeks; reviews answered
- [ ] Content fixes logged; first update planned (yearly stack refresh)
