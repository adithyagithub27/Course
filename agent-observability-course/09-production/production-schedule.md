# Production Schedule: 12 Weeks

> Assumes a single instructor-producer, part-time help for editing optional, and the curriculum done (it is). Scripts, code, labs and assessments may already be partly drafted in `02-lecture-scripts/` to `06-assessments/`. If they are, compress Weeks 1-3. Target Udemy launch in **Q2 2027** (the market research roadmap). Work backwards from the chosen launch date, and let the marketing plan (`../08-marketing/launch-plan.md`) start at W-4, which overlaps Weeks 9-12 here.

**Scope (curriculum tables):** 91 video items: 76 lectures (627 min of non-quiz video by table minutes, incl. labs, challenges and assignment intros; ≈10.5 h) + 7 lab walkthroughs + 5 challenge videos (4.7, 6.8, 11.2, 11.3, 11.4) + 13 quizzes + practice test + 5 coding exercises + 2 projects + capstone + domain swap. Seven long lectures (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3) are uploaded as Part A / Part B.

---

## Milestones

| # | Milestone | End of week | Exit criteria |
|---|---|---|---|
| M1 | Code freeze v1 + frozen fixture day | 3 | `make test` green offline (419 tests); `OFFLINE=1 make replay` reproduces `numbers-card.md` (seed 7, 2026-09-14, $56.28); numbers card regenerated for Sections 6-9, 11, 14; versions pinned (langfuse 4.15.x, opentelemetry-sdk 1.45.x, semconv 0.66b0, litellm 1.103.x, deepeval 4.2.x); live path (2.3) works with keys; three incident datasets final with solutions, plus incident 4 (solution instructor-only) |
| M2 | Pilot lectures approved | 4 | 4 pilot lectures (1.2 SL, 2.3 SC live, 6.3 SC capture-heavy, 11.2 CH investigation) fully produced and QA'd; pipeline timing measured; Track C legibility confirmed on a phone |
| M3 | Sections 1-5 recorded | 6 | Raw screencasts, captures and avatar renders done |
| M4 | Sections 6-10 recorded | 8 | Same |
| M5 | Sections 11-15 recorded + promo | 9 | Same, plus promo video |
| M6 | All lectures assembled + captions | 10 | Every lecture passes `qa-checklist.md`; attribute names correct in captions |
| M7 | Udemy build complete | 11 | Landing page, quizzes, practice test, coding exercises, assignments, resources, messages all in Udemy |
| M8 | Submitted for review | 11 | `../07-udemy-listing/publish-checklist.md` fully ticked |
| M9 | Published + launch | 12 | Approved; launch week per marketing plan |

## Week by week

| Week | Focus | Tasks | Output |
|---|---|---|---|
| 1 | **Code, environment, fixture** | Run the full repo on clean macOS, Windows (WSL) and Linux; fix setup friction; pin versions and record them in the README; confirm the fixture day (seed 7, Monday 2026-09-14) reproduces the numbers card; set up the recording accounts (`recording-guide.md` §6.2); test the capture rig (Langfuse 150%, Grafana kiosk, Ops Console theme) | Clean-machine install log; pinned `pyproject.toml`; numbers card re-verified |
| 2 | **Scripts S1-S8 final** | Script review against the PRODUCTION-GUIDE 7-beat structure and word budget; check every code line and attribute name against curriculum §6; check every number against `numbers-card.md`; regenerate decks with `slide_builder.py` (diagrams D1-D12 are built) | Final scripts S1-S8; diagrams D1-D7 |
| 3 | **Scripts S9-S15 final + code freeze (M1)** | Same for S9-S15; diagrams D8-D12; incident datasets final and `solution.md` written; capstone reference solution runs end to end; compose stacks verified on the recording machine | Final scripts; all diagrams; **M1** |
| 4 | **Pilot (M2)** | Produce 1.2, 2.3, 6.3, 11.2 end to end; measure hours per finished minute; test Track C legibility on a phone at 720p; adjust the plan; get feedback from 2-3 reviewers (ideally one who runs agents in production) | 4 finished lectures; revised estimates; **M2** |
| 5 | **Record S1-S3** | HeyGen batch render S1-S3; OBS sessions S2-S3 (incl. 2.3 live, 2.4 console reference frame); demos 1.1 (cost meter), 3.6 (broken traces) | Raw S1-S3 |
| 6 | **Record S4-S5 (M3)** | Renders + OBS + Langfuse captures for S4-S5 (4.7 challenge pause card, 5.6 loop demo); assemble S1-S3 in parallel | Raw S4-S5; S1-S3 assembled; **M3** |
| 7 | **Record S6-S7** | Signature cost section (S6: every BEFORE/AFTER card from the same replay; 6.8 challenge) and reliability (S7: **7.6 chaos demo**, most retakes) | Raw S6-S7 |
| 8 | **Record S8-S10 (M4)** | Online evals (S8: live judge runs, capped), dashboards (S9: compose stack, Grafana, **9.6 alert firing**), governance (S10: 10.4 with "not legal advice" on every card); assemble S4-S7 | Raw S8-S10; **M4** |
| 9 | **Record S11-S15 + promo (M5)** | **Incident labs S11** (three rehearsed investigations from the solution-free checkout, three reveals), portability (S12: four backends), deploy (S13: Docker, collector, CI gate, **13.5 chaos**), capstone (S14: 14.1a gate, two reference sessions, 14.4 report), wrap-up (S15: **15.2 careers**, no salaries); re-record 1.1 from the final capstone console if it changed; promo shoot (real camera for Shots 2 and 9 if possible) | Raw S11-S15; promo; **M5** |
| 10 | **Assemble + captions + QA (M6)** | Assemble S8-S15; numbers overlays; loudness normalize; captions corrected (attribute names!); full QA pass; scrub pass for keys, project ids, org names | All lectures final; **M6** |
| 11 | **Udemy build + submit (M7, M8)** | Upload videos; lecture descriptions; resources (PDF exports; incident solutions on Part B only); quizzes; practice test; coding exercises tested in Udemy's runner; assignments; landing page; messages; pricing; verify policies (AI content, coupons, bonus lecture); submit | **M7, M8** |
| 12 | **Review buffer + launch (M9)** | Respond to Udemy review feedback; fix; publish; launch week (see `../08-marketing/launch-plan.md` W0); rotate recording keys | **M9** |

## Capacity assumptions (planning estimates, replace with pilot measurements)

| Lecture type | Est. production hours per finished minute |
|---|---|
| SL (avatar + slides) | 1.0-1.5 h |
| SC (screencast) | 1.5-2.0 h (incl. retakes) |
| SC with Track C captures (Langfuse/Grafana/console) | 2.0-2.5 h (zoom, masks, numbers overlays, re-takes when a number drifts) |
| DM (live demo, chaos) | 2.0-3.0 h (retakes, timing the alert or the fallback) |
| CH incident investigation + reveal | 2.5-3.0 h (rehearsal, solution-free checkout, red herring, two uploads) |
| TH (avatar) | 0.5-1.0 h |

At ~627 video minutes, total effort lands in the **hundreds of hours**. The Week 4 pilot exists to replace these guesses with real numbers. If the pilot shows more than a 20% overrun, either extend to 14 weeks or move Section 12 (portability) to a post-launch update (keep 12.5 decision matrix at launch).

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| GenAI semantic conventions rename attributes mid-production (they are incubating) | Re-records of 3.3, 3.4, cheat sheet, captions | Pin `opentelemetry-semantic-conventions` 0.66b0; say "incubating, names may change" on screen; use the `g.GEN_AI_*` constants in code so a rename is a version bump, not a code change; plan a post-launch update window |
| Langfuse SDK minor release changes a method name (`propagate_attributes`, `update_current_generation`, `score_current_trace`) | Code lectures go stale | Pin langfuse 4.15.x; record Section 4 in one tight window; keep the version banner; pinned Q&A thread for breaking changes |
| Langfuse self-host compose file changes | 13.1 screencast out of date | Record 13.1 last within Week 9; flag "verify against current compose" on screen; keep a text "current steps" resource |
| OpenAI model renames or pricing changes | Numbers and price table stale | Models come from env vars in `config.py` (by design); `pricing.py` fallback table is dated; every dollar figure is labelled simulated with a price-table date; say "default model" in narration |
| Numbers on screen drift from narration after a replay regeneration | Confusing lectures, bad reviews | One fixture day (M1, deterministic replay); numbers card generated, not typed; regenerate and re-record a whole section if the replay changes |
| Track C captures unreadable on phones | Core value of the course lost | Pilot legibility test in Week 4; the 25% rule in `recording-guide.md` §6.1 |
| Exposed keys, project ids or org names in footage | Security incident, re-edit | Recording accounts, OBS masks, address bar crop, scrub pass, rotate keys after recording |
| Docker/self-hosted stack too heavy for the recording machine or students' machines | 9.x and 13.x fail | Check RAM in Week 1; offline path and Langfuse Cloud remain the default; Section 13 is optional depth |
| Judge sampler runs away during 8.2 recording | Real spend | `JUDGE_MAX_CALLS` cap and the OpenAI project hard cap |
| Udemy policy on AI avatars changes | Rework | Verify at Week 1 and Week 11; film real-camera segments for promo, 14.1a, 15.2 and 15.4 |
| Udemy review rejection | Launch slips | Week 12 buffer; the publish checklist is completed before submitting |
