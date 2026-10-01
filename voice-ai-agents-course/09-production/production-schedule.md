# Production Schedule: 12 Weeks

> Assumes a single instructor-producer, part-time help for editing optional, and the curriculum done (it is). Scripts, code, labs and assessments may already be partly drafted in `02-lecture-scripts/` to `06-assessments/`. If they are, compress Weeks 1-3. Target Udemy launch in **Q1 2027** (the market research roadmap). Work backwards from the chosen launch date, and let the marketing plan (`08-marketing/launch-plan.md`) start at W-4, which overlaps Weeks 9-12 here.

**Scope (curriculum v1.1):** 89 video lectures (683 min by curriculum minutes, ≈11.4 h) + 7 lab walkthroughs (~31 min) + 1 challenge video (5.9) + 12 quizzes + practice test + 5 coding exercises + 5 assignments + capstone. Six long lectures (5.3, 7.5, 8.2, 9.3, 13.2, 13.5) are uploaded as Part A / Part B.

---

## Milestones

| # | Milestone | End of week | Exit criteria |
|---|---|---|---|
| M1 | Code freeze v1 | 3 | `make test` green offline; agent tests and evals green with keys; versions pinned (livekit-agents 1.8.x, pipecat-ai 1.12.x); phone demo works end to end |
| M2 | Pilot lectures approved | 4 | 4 pilot lectures (1.2 SL, 3.3 SC, 8.2 SC + phone, 9.4 SC) fully produced and QA'd; pipeline timing measured |
| M3 | Sections 1-5 recorded | 6 | Raw screencasts + avatar renders done |
| M4 | Sections 6-10 recorded | 8 | Same |
| M5 | Sections 11-15 recorded + promo | 9 | Same, plus promo video |
| M6 | All lectures assembled + captions | 10 | Every lecture passes `qa-checklist.md` |
| M7 | Udemy build complete | 11 | Landing page, quizzes, practice test, coding exercises, assignments, resources, messages all in Udemy |
| M8 | Submitted for review | 11 | `07-udemy-listing/publish-checklist.md` fully ticked |
| M9 | Published + launch | 12 | Approved; launch week per marketing plan |

## Week by week

| Week | Focus | Tasks | Output |
|---|---|---|---|
| 1 | **Code and environment** | Run the full repo on clean macOS, Windows and Linux; fix setup friction; pin versions; record the exact versions in the README; set up the recording accounts (`recording-guide.md` §6) | Clean-machine install log; pinned `pyproject.toml` |
| 2 | **Scripts S1-S8 final** | Script review against the PRODUCTION-GUIDE 7-beat structure and word budget; check every code line against curriculum §6; draw diagrams D1-D7 as SVG in `10-graphics/diagrams/` (specs in `slide-deck-outline.md`); generate the S1-S8 decks with `tools/slide_builder.py` | Final scripts S1-S8; diagrams D1-D7; decks S1-S8 |
| 3 | **Scripts S9-S15 final + code freeze (M1)** | Same for S9-S15; diagrams D8-D16 and decks S9-S15; phone number + SIP trunk live on the recording accounts; capstone runs end to end | Final scripts; all diagrams; **M1** |
| 4 | **Pilot (M2)** | Produce 1.2, 3.3, 8.2, 9.4 end to end; measure hours per finished minute; adjust the plan; get feedback from 2-3 reviewers | 4 finished lectures; revised estimates; **M2** |
| 5 | **Record S1-S3** | HeyGen batch render S1-S3; OBS sessions S2-S3 (incl. 2.6 quick win, 2.7 mock mode); live demos 1.1 (placeholder until 13.5 is recorded), 3.4, 3.7, **3.9 break-it A/B audio** | Raw S1-S3 |
| 6 | **Record S4-S5 (M3)** | Renders + OBS for S4-S5; assemble S1-S3 in parallel | Raw S4-S5; S1-S3 assembled; **M3** |
| 7 | **Record S6-S8** | Realtime (S6, with side-by-side audio in 6.4), knowledge/handoffs (S7) incl. **7.8 multilingual** (book a native-speaker check for Spanish and Hindi), **telephony (S8)** with the safe phone recording protocol and the no-phone-number path | Raw S6-S8 |
| 8 | **Record S9-S10 (M4)** | Signature testing section (S9, incl. 9.13 audio-in tests and 9.14 LiveKit Simulations after verifying availability) and observability (S10); assemble S4-S7 | Raw S9-S10; **M4** |
| 9 | **Record S11-S15 + promo (M5)** | Security, deploy (incl. **12.8 chaos demo**), capstone (13.1a gate, real 13.5 calls, 13.7 domain swap), Pipecat (optional section), wrap-up incl. **15.4 careers**; re-record 1.1 (three calls) from the final capstone; promo shoot (real camera for Shots 2 and 9 if possible) | Raw S11-S15; promo; **M5** |
| 10 | **Assemble + captions + QA (M6)** | Assemble S8-S15; loudness normalize; captions corrected; full QA pass; scrub pass for keys/numbers | All lectures final; **M6** |
| 11 | **Udemy build + submit (M7, M8)** | Upload videos; lecture descriptions; resources (PDF exports); quizzes; practice test; coding exercises tested in Udemy's runner; assignments; landing page; messages; pricing; verify policies (AI content, coupons, bonus lecture); submit | **M7, M8** |
| 12 | **Review buffer + launch (M9)** | Respond to Udemy review feedback; fix; publish; launch week (see `08-marketing/launch-plan.md` W0) | **M9** |

## Capacity assumptions (planning estimates, replace with pilot measurements)

| Lecture type | Est. production hours per finished minute |
|---|---|
| SL (avatar + slides) | 1.0-1.5 h |
| SC (screencast) | 1.5-2.0 h (incl. retakes) |
| DM (live demo, phone) | 2.0-3.0 h (non-deterministic retakes, masking) |
| TH (avatar) | 0.5-1.0 h |

At ~690 video minutes (683 plus the 5.9 challenge), total effort lands in the **hundreds of hours**. The Week 4 pilot exists to replace these guesses with real numbers. If the pilot shows more than a 20% overrun, either extend to 14 weeks or move the S14 Pipecat build to a post-launch update (keep 14.3 build-vs-buy at launch).

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LiveKit Agents or Pipecat ships breaking changes mid-production | Re-records | Pin versions; record code lectures in one tight window per section; keep the version banner; plan a post-launch update window |
| Provider model renames (`gpt-4.1-mini`, `nova-3`, `sonic-3`, `gpt-realtime`) | Code and on-screen strings go stale | Model strings come from env vars in `config.py` (by design); say "default model" in narration rather than stressing names |
| Phone/SIP setup UI changes at Twilio or LiveKit | 8.2 screencast out of date | Record 8.2 last within Week 7; keep CLI-based steps where possible; add a text "current steps" resource |
| Non-deterministic demos | Retakes | `mock_tools`, seeded scheduler state, rehearsal rule (3 runs) |
| Exposed keys or numbers in footage | Security incident, re-edit | Recording accounts, OBS masks, scrub pass, rotate keys after recording |
| Udemy policy on AI avatars changes | Rework | Verify at Week 1 and Week 11; film real-camera segments for promo, 1.1 and 15.3 |
| Udemy review rejection | Launch slips | Week 12 buffer; the publish checklist is completed before submitting |
