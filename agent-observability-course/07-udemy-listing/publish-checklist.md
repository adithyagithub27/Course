# Udemy Publish Checklist

> Work through this list before you press **Submit for Review**. The Udemy minimums quoted here are as the author understands Udemy's course quality checklist. **Udemy updates these rules, so confirm each one in the Teaching Center and in the "Submit for review" validator in course management.** Items marked (verify) especially need checking.

---

## 0. Pre-flight: curriculum reconciliation

- [ ] **Counts per `01-curriculum/curriculum.md`:** **105 items**: 76 video lectures (44 screencast, 20 slide, 6 demo, 6 talking-head) + 7 labs + 5 challenges (4.7, 6.8, 11.2, 11.3, 11.4) + 3 assignments (6.9, 11.6, 14.6) = **91 video items**, plus **14 quizzes** (13 section quizzes + the practice test 15.3). Prefer quoting hours over a lecture count.
- [ ] **Runtime:** the curriculum table minutes (equal to the script header targets as of 2026-10-04) add up to **671 min** in total and **627 min of video** without quizzes (≈10.5 h); the header, the totals table and the README agree. Public copy says "about 10.5 hours"; use the figure Udemy shows after upload, and update the description if the real total differs by more than ~15 min.
- [ ] **Part A / Part B splits** (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3) raise the uploaded lecture count by 7. Udemy counts uploaded items, so don't quote a lecture count in the promo video or social posts. Quote hours instead.
- [ ] Section and lecture titles in Udemy match `01-curriculum/curriculum.md` IDs and titles exactly (prefix titles with IDs, e.g., "2.3 Quick win: one request, one trace", if you want students to match them to repo files and incident folders)
- [ ] Every lecture's code references match `03-code/` paths (`src/northwind/`, `app/`, `telemetry/`, `simulator/`, `evals/`, `console/`, `incidents/`, `deploy/`, `tests/`)
- [ ] Lecture 14.1a (capstone gate) sits directly before 14.2

## 1. Udemy minimum requirements (verify current numbers)

- [ ] **At least 30 minutes of video content** (this course: ~630 min of video lectures)
- [ ] **At least 5 lectures** (this course: 91 non-quiz items, 76 of them video lectures)
- [ ] **Video at least 720p HD**. We export 1920×1080, H.264, 30 fps (per `../../09-heygen/PRODUCTION-GUIDE.md`)
- [ ] **Audio:** clear, no echo, no background noise, both channels, consistent loudness (-16 LUFS target), with no silent gaps longer than a few seconds except in intentional pause cards
- [ ] Every video lecture has an **instructional** purpose. No lecture is only a promo
- [ ] Course isn't a duplicate of other published courses by the instructor (it reuses concepts from Courses 2 and 3, such as DeepEval judges and latency budgets, but not footage)
- [ ] Paid course meets Udemy's minimum paid-course video length (historically 30 min; verify)

## 2. Video and audio quality (spot-check every section)

- [ ] Picture: 1080p, no letterboxing, no pixelation, consistent frame rate
- [ ] Screen recordings: code font legible on a 13" laptop at 1080p (JetBrains Mono ≥ 18 pt equivalent; see `09-production/recording-guide.md`)
- [ ] **Dashboard and trace captures** (Langfuse, Grafana, Ops Console): browser zoom 125-150%, span names and attribute values legible at 720p, address bar cropped, no keys or project IDs (recording guide §6)
- [ ] Audio: mono voice centred, stereo mix, -16 LUFS integrated, true peak ≤ -1 dBTP, music ≤ -24 LUFS under voice
- [ ] Avatar scenes: lip sync correct, no artefacts, pronunciation checked for Langfuse, OpenTelemetry, OTLP, OpenInference, LiteLLM, DeepEval, Prometheus, Grafana, TTFT, TPOT, p95, SLO, EWMA, PSI, Northwind, Atlas
- [ ] No uploaded video longer than ~10 min after the Part A/B splits (the curriculum's longest, 11.2-11.4 and 14.2-14.3 at 12 min, are split)

## 3. Captions and accessibility

- [ ] English captions on every video lecture (Udemy auto-captions reviewed and corrected, or script-based captions uploaded)
- [ ] Domain terms spelled correctly in captions (see the spelling list in `10-resources/glossary.md`)
- [ ] Diagrams described in narration, so meaning doesn't depend on seeing them (the waterfall, the cost rollup tree and the burn-rate chart in particular)
- [ ] Color never the only signal (pass/fail also uses ✓/✗ glyphs or labels; SLO breaches labelled, not only red)
- [ ] Downloadable resources are text-based Markdown/PDF (screen-reader friendly)

## 4. Curriculum content in Udemy

- [ ] **Lecture descriptions** entered for every lecture (from `lecture-descriptions.md`)
- [ ] **Resources attached** per `resources-per-lecture.md` (downloads plus external links to the course repo where Udemy allows external resource links; verify)
- [ ] Section titles are descriptive and keyword-bearing (e.g., "Section 6: Cost Engineering: Token FinOps for Agents")
- [ ] Lecture 1.1 marked as **free preview**. Also consider 1.2, 2.3 and 6.1 (Udemy allows a limited share of free preview content; verify)
- [ ] Labs uploaded as video walkthrough + article/resource with the lab Markdown
- [ ] **Incident solutions** (`incidents/*/solution.md`) are NOT attached as resources to 11.2-11.4 before the reveal; attach them to the reveal Part B only, or reference the repo tag that includes them

## 5. Quizzes, practice test, coding exercises, assignments

- [ ] 13 section quizzes created (S1-S12, S14). Every question has an explanation for the correct and incorrect answers
- [ ] **Practice test** (15.3): 40 questions, pass mark and time limit set, and each question has an explanation plus a "related lecture" reference
- [ ] **Coding exercises**: 5 pure-Python exercises (per-token cost, percentile latency, EWMA anomaly, PII masking, context trimming)
  - [ ] Each exercise has instructions, starter code, a solution and hidden tests
  - [ ] Runs in Udemy's in-browser environment: **no network, no third-party packages** (no `litellm`, `tiktoken`, `langfuse`), compatible Python version (verify runner version)
  - [ ] Tested by solving each exercise from a student account view
- [ ] **Assignments**: Project 1 (6.9 showback report), Project 2 (11.6 fourth incident postmortem), capstone (14.1 brief, 14.5 submission), 14.6 domain swap. Each has instructions, questions and the instructor's example solution
- [ ] **Challenges (type CH: 4.7, 6.8, 11.2, 11.3, 11.4)** depend on `langfuse`, the local store and replayed spans, so they **can't run in Udemy's in-browser coding exercise runner**. Publish them as video lectures with a clear pause card and repo links
- [ ] **14.1a capstone gate** placed directly before the reference-solution lectures (14.2 onwards)

## 6. Landing page

- [ ] Title ≤ 60 chars and subtitle ≤ 120 chars (`title-and-subtitle.md`, verified by script)
- [ ] Description ≥ 200 words (Udemy minimum, verify); ours is ~1,230 words (`course-description.md`)
- [ ] 4+ learning objectives, each ≤ 160 chars (ours: 10, verified)
- [ ] Requirements and "who this course is for" filled in
- [ ] Language, level, category, subcategory and primary topic set (`course-settings.md`)
- [ ] Course image 750×422, meets image standards (`course-image-brief.md`)
- [ ] Promo video uploaded and processed (`promo-video-script.md`); the "$4,000" is labelled as simulated
- [ ] Instructor profile complete: photo, headline, bio with real credentials (`instructor-bio.md`)
- [ ] Read the whole landing page in preview mode on desktop and mobile. Check for typos, and that there are no placeholder brackets `[ ]`

## 7. Pricing, promotions and payouts

- [ ] **Premium instructor application approved** (needed to sell paid courses; verify current process)
- [ ] **Payout method** set up and **tax forms** submitted (verify current options)
- [ ] Price tier set (`course-settings.md` §4)
- [ ] Decision made on opting in or out of Udemy promotional programs (verify current program names and terms)
- [ ] Launch coupons drafted but **not created until verified** against current coupon rules (`course-settings.md` §5)

## 8. Messages and communication

- [ ] Welcome message and congratulations message entered, each under 1,000 characters (`welcome-and-congratulations-messages.md`)
- [ ] Q&A on; pinned setup, versions, Docker and incident-lab posts drafted (from `10-resources/troubleshooting.md`); 5 likely questions per section seeded on launch day
- [ ] Direct messages on
- [ ] Launch educational announcement drafted

## 9. Policy compliance

### Promotional policy (verify current Trust & Safety / promotional guidelines)

- [ ] No external links, coupons, promotional content or contact details in lecture videos, captions, lecture descriptions, quizzes, messages, Q&A or resources. The **only exception is the final bonus lecture (15.4)**, within Udemy's bonus-lecture rules
- [ ] Bonus lecture (15.4) is the last lecture, is labelled "Bonus", and follows the current rules on what may be linked (Udemy courses with coupons; limits on off-platform links and lead capture; verify)
- [ ] The course repo is referenced as a required learning resource, not as a marketing funnel. If the repo README links to other courses, check this is allowed when linked from within Udemy (verify)
- [ ] Cross-links to Course 2 (offline evals) and Course 3 (latency budgets) inside lectures 4.5, 7.1, 8.6 and 14.6 are **factual one-liners**, not promotion, and carry no links or coupons. If in doubt, move them to 15.4
- [ ] No request for reviews in exchange for anything; no "please rate 5 stars"
- [ ] No collection of student emails or personal data through the course

### AI-generated content disclosure (avatar-narrated lectures)

> **Flag: verify Udemy's current policy on AI-generated content, AI avatars and synthetic voices before submission.** Udemy has published guidance on generative-AI use in course creation, and the rules may require disclosure, human instructor presence, or quality thresholds for AI-narrated content.

- [ ] Read Udemy's current AI content policy and record the date checked: `____`
- [ ] Decide on disclosure: at minimum, state in the description, or in lecture 1.5, that "lectures are presented by an AI avatar of the instructor (HeyGen) from instructor-written scripts; all code demos, traces and dashboards are real recordings"
- [ ] The instructor has rights to their avatar and voice clone (HeyGen consent and verification done in HeyGen). **No avatar or voice resembles a real person other than the instructor**
- [ ] The promo video and lecture 1.1 include real instructor presence where possible (see `promo-video-script.md`)
- [ ] AI-generated scripts, images and captions have been **reviewed by the instructor for accuracy**, especially the API calls and attribute names (curriculum §6) and the governance statements

### Content and legal

- [ ] Governance lecture (10.4) and `telemetry-governance-checklist.md` are labelled "not legal advice"; the EU AI Act references are flagged "verify with counsel"
- [ ] Careers lecture (15.2) and `interview-questions.md` contain **no salary figures** and no promotional content
- [ ] **No real cost figures presented as real bills.** The $4,000 weekend and all showback numbers come from the simulator against a price table, and are labelled "simulated" or "example" on screen
- [ ] Prices in lectures and resources are labelled "check current pricing"; `pricing.py`'s pinned fallback table carries a date
- [ ] `docker-compose.langfuse.yml` (13.1) is flagged "verify against the current Langfuse compose file" on screen and in the README
- [ ] GenAI semantic conventions are labelled "incubating, names may change" on screen (3.3) and in the cheat sheet
- [ ] No real employee data, tickets, PII or company records anywhere; Northwind Logistics and Atlas are fictional and labelled as such; knowledge-base documents are invented
- [ ] Third-party trademarks (Langfuse, OpenTelemetry, LangSmith, Arize Phoenix, Datadog, Grafana, Prometheus, LiteLLM, OpenAI) used descriptively only; no logos in the course image; comparison statements in Section 12 are qualitative and dated
- [ ] Music and stock assets licensed; licences archived

## 10. Final review

- [ ] One full pass in student preview mode, watching every lecture at 1.5× at minimum
- [ ] Repo freshly cloned on a clean machine: `make install`, `make test` pass offline; `make replay` and `make console` work with `OFFLINE=1`; with keys, `make eval` and the live path in 2.3 work
- [ ] Version banner shown: "APIs verified on langfuse 4 / opentelemetry-sdk 1.45 / semconv 0.66 (incubating)"
- [ ] `09-production/qa-checklist.md` signed off per lecture
- [ ] Keys used in recording rotated (recording guide §6)
- [ ] Submit for review. Record the submission date and any reviewer feedback in `CHANGELOG`
