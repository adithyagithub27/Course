# Review: Course 3, Production Voice AI Agents with Python

Reviewed 2026-10-01 against `CLAUDE.md`, `09-heygen/PRODUCTION-GUIDE.md`, `01-curriculum/curriculum.md` (v1.1), all 15 script files in `02-lecture-scripts/`, `09-production/{video-generation-plan,slide-deck-outline,recording-guide,qa-checklist}.md`, `04-labs/`, `05-projects/`, `06-assessments/`, and `03-code/` (installed with `uv sync --extra dev`, livekit-agents 1.8.3; `make test` run).

All paths below are relative to `/home/user/Course/voice-ai-agents-course/` unless absolute. Word counts come from `scratchpad/analyze_scripts.py` (spoken narration plus scripted demo dialogue, excluding cues, slide bullets, tables and code), at 140 wpm.

---

## (a) Executive summary: the 10 issues that matter most, ranked by learner impact

1. **Seven scripts contradict the student code, and the code is right (CLAUDE.md: "fix the prose").** Students who type along will produce files that differ from the reference, or be told a feature is missing when it exists.
   - 7.8 says the mid-call language switch "isn't in the repo file, so type it in" (`section-07-knowledge-and-handoffs.md:1095-1097`); `agents/s07_knowledge_agent.py:94-130` already has `follow_caller_language` behind `FOLLOW_CALLER_LANGUAGE=1`, and the README maps it. The script's snippet also uses `ev.language.language`, which does not exist (`LanguageCode` is a `str`); the repo's `str(ev.language).split("-")` is correct.
   - 13.3 and 12.8 say the capstone's `error` handler "only speaks the line" and invite students to add the transfer as an exercise (`section-13-capstone.md:674`, `section-12-deploy.md:1279`); `agents/s13_capstone_receptionist.py:246-320` already implements `recover_after_error` (transfer, else goodbye + hang-up). The 13.2 entrypoint code block (`section-13-capstone.md:478-484`) shows the old handler.
   - 5.9 spec and solution give `join_waitlist(..., part_of_day="any")` and `add_to_waitlist(..., part_of_day)` (`section-05-tools.md:1172-1173, 1212-1224`); the real tool (`agents/s05_booking_agent.py:72-100`) has no `part_of_day`. Curriculum (`curriculum.md:169`) and slide outline (`slide-deck-outline.md:85`) use a third signature, `join_waitlist(name, phone, preferred_day)`.
   - 4.3 builds `SPELLING_RULES` and passes `extra=SPELLING_RULES` (`section-04-prompting-for-the-ear.md:408-457`); `agents/s04_voice_prompting.py:62-68` has no such block, so the "Is that O, R, T, I, Z?" demo depends on a rule the reference file lacks.
   - 5.3/5.7 return value and the "diff your file against the mixin: the only differences should be names and comments" claim (`section-05-tools.md:421, 1094`) are false: `BookingToolsMixin` (`agents/common.py:485-600`) also has `_filler`/`can_say`, a `next_available` fallback, `_check_verified` and `last_offered_slots`.
   - 6.2 says a string filler "will fail the moment it tries to speak" on pure realtime (`section-06-realtime.md:266`); the mixin's `_filler` skips string fillers when there is no TTS (`agents/common.py:503-514`) and `tests/agent/test_mock_mode.py:81` tests exactly that.
   - 12.2 narrates a `uv.loc[k]` COPY glob and lists `uv.lock` in "Files used" (`section-12-deploy.md:201, 304-306`); `deploy/Dockerfile:32-33` has no such line and the repo ships no `uv.lock`, while 12.6/12.7 tell students to commit one.

2. **Flow break in Section 2.** Lecture 2.5 ends "See you in Section three, where you'll build this agent yourself" (`section-02-setup.md:542`), but 2.6 (the "quick win" the curriculum review added) and 2.7 follow it. Students hear a sign-off, then two more setup lectures.

3. **18 avatar blocks exceed the 60-second rule (>140 words with no visual cue).** Worst offenders: 9.2 (196 words, `section-09:186`), 10.1 (182, `section-10:103`), 6.3 (181, `section-06:486`), 8.1 (177, `section-08:48`), 1.3 (169, `section-01:388`), 6.1 (168 and 166, `section-06:64, 88`), 10.5 (165), 2.1 (164), 9.3 (163), 14.1 (159), 7.5 (157), 12.7 (156), 1.4, 4.5, 6.4, 8.1, 9.2 (second). Sections 6, 8, 9 and 10 (the "second author" format) are where this concentrates.

4. **Riley's pronoun changes mid-course.** Sections 1-5 and 11-15 call Riley "it"; Sections 6-9 say "she/her" (34 occurrences: 6.x 7, 7.x 6, 8.x 9, 9.x 12). Lecture 4.5 preaches "one Riley everywhere"; the scripts do not practise it. The avatar will read both.

5. **Slide-only lectures will come in 25-35% short of the curriculum minutes.** SL/TH lectures have no demo audio to fill time, yet 3.1 (0.72 of target), 3.5 (0.68), 3.6 (0.71), 1.5 (0.73), 15.3 (0.76) and 12.7 (0.64) have 2-3 minutes less narration than their slot. `qa-checklist.md` demands runtime within ±20% of curriculum minutes, so these fail QA as written. Across the course, spoken words total 73,909 (≈528 min at 140 wpm) against a claimed 687 min of video; the gap must be filled by demo/typing dwell, which is plausible for SC/DM but not for SL.

6. **Technical claims that are wrong or unverifiable on livekit-agents 1.8.3.** 6.1 slide 6 and its speaker note say LiveKit "recycles the connection by default every 20 minutes (`max_session_duration`)" (`section-06-realtime.md:110, 157`); the plugin default is `None`. 13.2 (`section-13-capstone.md:461`) and `agents/s13_capstone_receptionist.py:308` pass `preemptive_generation=True` to `AgentSession`, which 1.8.3 marks deprecated ("Use turn_handling=TurnHandlingOptions(...)"); the course teaches `TurnHandlingOptions` everywhere else. 7.8's `ev.language.language` (above). Stale editor notes: `section-12-deploy.md:40` says `agents/s12_chaos_demo.py` "must be added to the repo" (it exists); `section-13-capstone.md:730-ish` says `tests/agent/test_capstone.py` is "created live" and must be added (it exists). 13.4 quotes "20 passed, 28 deselected" (`section-13-capstone.md:755`); the actual offline run is 21 passed, 32 deselected.

7. **The four production documents disagree with each other and with the scripts.** `recording-guide.md:25-28` counts SC 47 / DM 9 / TH 7; `video-generation-plan.md:31-34` counts SC 33 / DM 13 / TH 10. `video-generation-plan.md:137` tells the recorder to revoke a key in `.env.chaos` for 12.8, while the 12.8 script uses the `s12_chaos_demo.py` kill-switch file. `slide-deck-outline.md:150` still lists `PipelineTask`/`PipelineRunner` (deprecated; scripts and repo use `PipelineWorker`/`WorkerRunner`). `qa-checklist.md:131` asks the QA reviewer to confirm "`UsageCollector` forms match §6" when §6 says it is deprecated and not used. The curriculum itself carries the same stale names (`curriculum.md:22, 73, 233` UsageCollector; `:282` PipelineTask) and types 5.9 as SC (`:169`) while the script and review call it CE.

8. **`slide-deck-outline.md` does not cover every lecture.** No entry for SC lectures 3.4, 7.2, 12.2, 12.3, 12.5 or 14.2, nor for any lab/assignment intro (2.5, 3.8, 4.6, 5.8, 6.5, 7.6, 8.7, 9.11, 10.6, 12.7); the slide-count table is labelled a "v1.0 planning estimate". The scripts themselves are specific enough to build from (every `[SLIDE]` has a title plus exact bullets or a layout description), so the outline is redundant where it exists and silent where it is needed.

9. **Engagement rule misses.** Banned phrase "Welcome back" opens 5.9's solution (`section-05-tools.md:1199`) and 13.2 Part A (`section-13-capstone.md:215`). 29 lectures open without a hook: every quiz/lab/assignment intro starts "Five questions..." / "Time to..." / "Your turn...", plus 2.1 ("Let's talk about money"), 3.3, 5.6, 7.2, 7.5, 13.2, 15.3. Several teaching lectures contain zero questions to camera despite the "every 60-90 s" rule: 2.7, 3.3, 3.4, 4.5, 5.9, 7.1 (839 words, 0 questions), 7.3 (704, 0).

10. **Lab time estimates contradict the lecture intros.** 2.5 says Lab 1 "takes about ten minutes" (`section-02-setup.md:531`); `lab-01-environment.md:6` says 45 minutes. 6.5 says 45 min vs `lab-04:6` 75 min; 10.6 says 45 min vs `lab-06:6` 75 min; 12.7 says 45-60 min vs `lab-07:6` 90 min.

What is solid (briefly, because it changes the fix priorities): the curriculum/script mapping is complete (all 97 IDs present, titles match except Part A/B suffixes and "Bonus Lecture: keep building"); every demo command, `BROKEN=` case, tool name and quoted number I could reproduce offline does reproduce exactly (`make test` 211 passed in 1.2 s; WER 26.32% → 3.76%, key-term misses 12 → 1; latency p95 1474 ms / FAIL by 274 ms at 1200; cost 6.35/16.23/27.67 c/min and the 10-minute $0.6838 table; `simulated_caller.py --mock` 4/4). No lecture is over its word budget.

---

## (b) Per-section table

Demo = lectures (excluding quizzes) with at least one `[DEMO]`, `[SCREEN]` or `[CODE]` cue. Slide-cue quality and engagement are 1-5. "longAV" = avatar blocks over 140 words.

| Section | Lectures (video) | Demo Y / video lectures | Slide-cue quality | Engagement | Flow notes |
|---|---|---|---|---|---|
| 1 Welcome | 6 (5) | 2/5 | 5 (10-11 fully specified slides per SL lecture, diagrams described, comparison tables written out) | 5 | Strong hook chain (call 1/2/3). 1.2-1.4 are slides-only by design. 2 longAV (1.3:388, 1.4:530). 1.6 is 0.66 of target but it is a quiz intro. |
| 2 Setup | 7 (7) | 7/7 | 3 (only 11 slides; mostly screen cues, which is right for setup) | 4 | **2.5 says "See you in Section three" before 2.6/2.7.** All SC lectures 46-71% of target; acceptable only if typing/dashboard dwell fills them. 2.1 opens with a statement, not a hook. |
| 3 First agent | 10 (9) | 6/9 | 5 (42 slides; D4/D5 diagrams; code slides ≤15 lines) | 5 | Best build section. `BROKEN=` table matches `s03_hello_agent.py:52-81` exactly. 3.1/3.5/3.6 are 28-32% under target with no demo to fill. 3.3 and 3.4 have zero questions to camera. |
| 4 Prompting | 8 (7) | 5/7 | 4 | 4 | 4.1 before/after audio clips are the right move. **4.3 `SPELLING_RULES` not in `s04_voice_prompting.py`.** 4.5 is a 5-block talking head (1 longAV at :694) with no questions. |
| 5 Tools | 10 (9) | 8/9 | 4 (21 slides; slot-filling and filler timelines described in the outline but not as `[SLIDE]` cues in the scripts) | 4 | **5.9 `join_waitlist` signature mismatch; "Welcome back" at :1199.** 5.3/5.7 "diff against the mixin" claim false. Failure-first demos in 5.5 and 5.6 are excellent. 8 of 9 SC lectures <65% of target. |
| 6 Realtime | 6 (5) | 4/5 | 4 | 3 | Format switches here (`### Recap`, "One idea" row, `uv run agents/...` without `python`), pronoun switches to "she". **4 longAV blocks** (6.1 ×2, 6.3, 6.4). 6.1 20-minute recycle claim unverified; 6.2 filler claim contradicts code. 6.4 side-by-side waveform playback is the best "hear it" moment in the course. |
| 7 Knowledge & handoffs | 8 (7) | 5/7 | 4 | 4 | 7.1 is SL but already shows the `on_user_turn_completed` code (good bridge to 7.2). **7.8 says the switch code is not in the repo; it is. `ev.language.language` wrong.** 7.1 and 7.3 have zero questions. 1 longAV (7.5:831). |
| 8 Telephony | 8 (7) | 6/7 | 4 (D6 call-flow diagram; every console step carries a verify banner) | 4 | Solid. 2 longAV in 8.1 (:48 at 177 words, :124). `telephony/*.json` are created live and not shipped in `03-code/` (project 2 refers to them). Twilio/LiveKit console steps correctly flagged. |
| 9 Testing | 14 (13) | 12/13 | 5 (failure→test map, pyramid, cheat sheets) | 5 | Signature section and it earns it: 9 of 13 video lectures show a red state before green. All numbers reproduce. 3 longAV (9.2:186 at 196 words, 9.2:210, 9.3:473). Pronoun "she" (12×). |
| 10 Observability | 7 (6) | 4/6 | 4 (D3/D10/D11 specified) | 4 | 10.2 version note on `metrics_collected`/`session.usage` is correct for 1.8.3. 2 longAV (10.1:103 at 182 words, 10.5:691). 10.4 numbers reproduce exactly. |
| 11 Security | 6 (5) | 4/5 | 4 | 4 | Good red-team loop (11.5 red→fix→green matches `test_safety.py`, 14 offline tests confirmed). No longAV. |
| 12 Deploy | 9 (8) | 7/8 | 4 | 4 | **12.2 `uv.loc[k]`/`uv.lock` mismatch; stale "s12_chaos_demo must be added" note at :40; 12.8 note at :1279 contradicts `recover_after_error`.** 12.8 Part C key revocation contradicts the video plan's instruction. 1 longAV (12.7:1030). |
| 13 Capstone | 8 (8) | 4/8 | 4 (D14 architecture, AT table) | 4 | 13.1a gate is a strong design. **13.2 "Welcome back"; stale `on_error` block at :478; deprecated `preemptive_generation=` kwarg at :461; 13.3 "handler only speaks the line" at :674; 13.4 count 20/28 vs actual 21/32.** |
| 14 Pipecat | 4 (3) | 1/3 | 4 (translation table, D15) | 4 | Correct on 1.12 renames. 1 longAV (14.1:46). Slide outline still says `PipelineTask`. 14.2 at 0.76 of a 12-minute target is fine for a code-along. |
| 15 Wrap-up | 4 (3) | 0/3 | 3 | 4 | TH lectures, no demo expected. 15.3 is 24% under its 5-minute slot. Upload-order note (15.4 before 15.3) is correct for Udemy. |

---

## (c) Evidence list

### 1. FLOW

- **Curriculum ↔ script mapping:** all 97 curriculum IDs have a script lecture and no script lecture is missing from the curriculum (`analyze_scripts.py` output). Title mismatches: 13.2 and 13.5 scripts append "(Part A and Part B)"; 15.3 script title "Bonus Lecture: keep building" vs curriculum "Bonus lecture" (`curriculum.md:329`). Durations: every script header target equals the curriculum minutes except where a lab/quiz has a shorter video intro.
- **Section 1 runtime:** `curriculum.md:106` says "≈38 min"; the totals table (`curriculum.md:335`) and the script header (`section-01-welcome.md:4`) say 39.
- **2.5 → 2.6 bridge:** `section-02-setup.md:542` "See you in Section three, where you'll build this agent yourself from an empty file." Next lectures are 2.6 and 2.7. The written `**Transition:**` line at :546 is correct; the spoken avatar line is not.
- **Format drift between author passes:** Sections 1-5 and 11-15 use `**Recap:**` / `**Transition:**` and a "Learning objectives" table row; Sections 6-10 use `### Recap` / `### Transition`, a "One idea" row and a bold "Learning objectives" list. `tools/scene_extractor.py:33-34` handles both heading styles, so this is cosmetic for production, but it also brought the pronoun drift (6-9 "she") and the `uv run agents/x.py` vs `uv run python agents/x.py` command inconsistency (26 vs 26 occurrences split by section).
- **Concept-before-use check:** passes. `on_user_turn_completed` is introduced in 3.2 before 7.1 uses it; `ToolError` in 5.1 before 5.6; `metrics_collected` in 3.2/6.4 before 9.8/10.2; `CallState.silence_prompts` is used in 4.4 with an explicit forward reference to 5.7; `GuardedRiley` appears in 9.9's harness with a forward reference to Section 11 (`section-09:1507`). `contains_agent_handoff` is used in Lab 5 (7.6) with a forward reference to 9.4. One real gap: 9.9 and 11.5 share the `injection_attacker` persona but the `opt_out` persona added live in 9.9 (`section-09:1577-1595`) is not in `tests/evals/simulated_caller.py` (4 personas in `PERSONAS`, `simulated_caller.py:61`), so a student who runs `--persona opt_out` after the lecture gets an error.
- **Running example continuity:** continuous. Demo patients (Jordan Lee 555-0142 / DOB 1988-04-12, Priya Patel, Sam Rivera), `MAPLE_TODAY=2026-10-05`, the Thursday-afternoon slots and the Delta Dental/Medicaid FAQ are the same across 2.6, 5.x, 9.x, 11.2, 13.5 and match `ClinicScheduler.with_demo_data`.
- **Redundancy:** the LiveKit Inference vs plugins explanation appears in full in 2.1, 2.3 and 3.5. The "read-back before commit" rule is restated in 5.3, 5.4, 5.9, 9.4, 11.2 and 13.2 (acceptable as spaced repetition, but 5.4 is almost entirely restatement).
- **Lab time claims:** `section-02:531` ten minutes vs `lab-01:6` 45 min; `section-06:678` 45 min vs `lab-04:6` 75; `section-10` 10.6 header "about 45 minutes" vs `lab-06:6` 75; `section-12:996` 45-60 min vs `lab-07:6` 90.
- **Assessments alignment:** quiz counts match the scripts (S1 8, S3 5, S4 5, S5 5, S6 8, S7 6, S8 5, S9 10, S10 5, S11 8, S12 5, S14 6; practice test 40). Note `quizzes/section-05.md:5` says Section 6's quiz covers `ToolError`/filler/userdata and `section-06.md` covers 5.1-5.7 plus 6.x, which the 5.10 intro ("questions on tool schemas, read-backs, filler speech, tool errors and userdata", `section-05:1281`) contradicts.

### 2. DEMOS

Per-lecture table (video lectures only; "backed" = the demo's file/command exists in `03-code/`; "fail-first" = a failure or before-state is shown before the fix).

| ID | Demo cue | Backed by 03-code | Fail-first | Notes |
|---|---|---|---|---|
| 1.1 | Y (DEMO×2, SCREEN×4) | unclear (recordings of capstone + a naive agent; test names "use the real names at recording time") | Y | Naive agent config (0.2 s endpointing, no tools) is not a `BROKEN=` case; recorder must hand-build it |
| 1.2-1.4 | N (SL) | n/a | N | Expected for SL; B-ROLL would help 1.4's "2.5-second silence" hook |
| 1.5 | Y (SCREEN×8) | Y (`README.md`, `Makefile` targets exist) | N | |
| 2.1 | Y (SCREEN×4) | n/a (provider dashboards) | N | |
| 2.2 | Y | Y (`.env.example` matches excerpt) | N | |
| 2.3 | Y | n/a (`lk` CLI) | N | |
| 2.4 | Y | Y (`make test`, `s03_hello_agent.py console --text`) | N | Troubleshooting table only |
| 2.5 | Y (lab doc) | Y | N | |
| 2.6 | Y | Y (`make console AGENT=agents/s13_capstone_receptionist.py`) | N | "Try to break it" at the end, not first |
| 2.7 | Y | Y (`MOCK_MODE`, cost snippet reproduces `$0.6838`) | N | |
| 3.3 | Y (CODE×9) | Y (`HELLO_INSTRUCTIONS`, `common` import) | N | Typed file intentionally differs from `s03_hello_agent.py` (explained) |
| 3.4 | Y | unclear (Agents Playground UI) | N | |
| 3.5 | Y (SCREEN×4) | Y (`config.py`, `build_stt/llm/tts`, `create_session`) | N | |
| 3.7 | Y | Y (`MIN/MAX_ENDPOINTING_DELAY` in `.env.example`) | Y | Rounds 2 and 3 are deliberate failures |
| 3.8 | Y | Y | N | |
| 3.9 | Y (DEMO×10) | Y (`broken_overrides`, 5 cases match) | Y | Exemplary |
| 4.1 | B-ROLL audio clips | unclear (clips recorded with a chat prompt; no `BROKEN=markdown`-style toggle named) | Y | |
| 4.2 | CODE reveals | Y (`prompts.py` blocks) | N | |
| 4.3 | Y | **partial** (`SPELLING_RULES` not in `s04_voice_prompting.py`; helpers exist) | Y (hook) | |
| 4.4 | Y | Y (`s04_voice_prompting.py:79-115`; script awaits `say()` playout, code does not) | N | |
| 4.6, 4.7 | Y (lab/template docs) | Y | Y / N | |
| 5.2 | Y | Y (shell session reproduces; `test_double_booking_raises` exists) | Y | |
| 5.3 | Y | partial (return string differs from mixin) | N | |
| 5.4 | Y | Y (`BOOKING_RULES`) | partial (correction case) | |
| 5.5 | Y (DEMO×3) | Y (`MAPLE_SIMULATED_LATENCY`, `_backend_call`) | Y | 2 s dead air first |
| 5.6 | Y (DEMO×4) | Y (`_speakable_error`) | Y | Sunday crash first |
| 5.7 | Y | Y (`CallState` fields match) | N | |
| 5.8 | Y (project doc) | Y | N | |
| 5.9 | Y | **partial** (signature mismatch) | N | Pause card present |
| 6.2 | Y (DEMO×3) | Y (`s06_realtime_agent.py` matches line for line) | N | |
| 6.3 | Y | Y (`REALTIME_HYBRID`) | N | |
| 6.4 | Y (DEMO×4 incl. side-by-side playback) | partial (temporary metrics logger pasted live; comparison uses lab files) | Y | Best audio demo in the course |
| 6.5 | Y | Y (lab) | N | |
| 7.2 | Y (DEMO×3) | Y (`KnowledgeRiley`, `KNOWLEDGE_MODE`) | N | Botox no-match shown last |
| 7.5 | Y | Y (`s07_multi_agent.py` matches) | N | |
| 7.6 | Y | Y (lab) | N | |
| 7.8 | Y | Y, but script says not in repo | Y (hook) | |
| 8.2 | Y (SCREEN×8) | partial (`telephony/*.json` created live, not shipped) | N | |
| 8.3 | Y | Y (`build_turn_handling`, `caller_number`) | Y (hook narration) | |
| 8.4 | Y | Y (`TelephonyToolsMixin`; code now delegates to `transfer_sip_caller`/`hang_up` helpers not shown) | N | "Test the failure path on purpose" is told, not shown |
| 8.5 | Y | Y (`dispatch` sub-command, `ReminderRiley`) | N | |
| 8.6 | SCREEN of checklist | Y | n/a | |
| 8.7 | Y | Y | N | |
| 9.1 | B-ROLL + trace walk-through | unclear (recorded early-Riley call) | Y | |
| 9.3 | Y | Y (`test_greeting.py` 4 tests match) | Y | Removes disclosure, shows red |
| 9.4 | Y | Y (`test_booking_flows.py` matches; `--count=5` needs pytest-repeat, not in `dev` extras) | Y | |
| 9.5 | Y | Y | Y (mocks are failure paths) | |
| 9.6 | Y | Y (`test_conversation_quality.py`, 10 goldens) | Y | Breaks the judge |
| 9.7 | Y | Y (numbers reproduce exactly) | Y | |
| 9.8 | Y | Y (numbers reproduce exactly) | Y | |
| 9.9 | Y | Y except `opt_out` persona | Y | |
| 9.10 | Y | Y (`ci.yml` matches) | N | |
| 9.11 | Y | Y | N | |
| 9.13 | Y | Y (`audio_in_eval.py`; no WAVs ship, by design) | Y | |
| 9.14 | Y | partial (`on_simulation_end` exists; Cloud feature flagged "verify") | Y | |
| 10.2 | Y | Y (`attach_observers`) | N | |
| 10.3 | Y | Y (`setup_observability`) | N (slow turn found after) | |
| 10.4 | Y | Y (numbers reproduce) | N | |
| 10.6 | Y | Y | N | |
| 11.2 | Y | Y (`VerificationToolsMixin`) | N | |
| 11.3 | Y | Y (`pii.py`, tests) | Y | PII in a log line first |
| 11.4 | Y | Y (`GuardrailsMixin`) | Y | Dosage advice first |
| 11.5 | Y | Y (14 offline tests confirmed; 8 live incl. the "new" one already in repo) | Y | |
| 12.2 | Y | partial (Dockerfile lacks the narrated lock-file COPY) | N | |
| 12.3 | Y | unclear (`lk agent` commands flagged verify) | N (rollback shown) | |
| 12.5 | Y | Y (`frontend/README.md` has both commands) | N | |
| 12.7 | Y | Y | N | |
| 12.8 | Y | Y (`s12_chaos_demo.py` matches) | Y | Part C contradicts video plan |
| 13.2 | Y | partial (stale `on_error` block) | N | |
| 13.3 | Y | partial (`recover_after_error` not mentioned) | Y | `not-a-real-model` run |
| 13.4 | Y (SCREEN×11) | Y (`test_capstone.py` exists; counts off by 1/4) | Y | |
| 13.5 | Y | partial (`lk agent`, Langfuse UI) | N | |
| 14.2 | Y (CODE×9) | Y (`s14_pipecat_bot.py` matches) | N | |
| 1.6, 3.10, 4.8, 5.10, 6.6, 7.7, 8.8, 9.12, 10.7, 11.6, 12.9, 14.4, 15.2 | N (quiz intros) | n/a | n/a | |
| 4.5, 8.6, 13.1, 13.1a, 13.6, 13.7, 15.1, 15.3, 15.4 | N (TH/SL/AS) | n/a | n/a | Acceptable; 13.7 would benefit from a 20-second clip of one swapped-domain call |

Lectures where a learner would expect to see it working but gets slides only: **1.4** (the "2.5-second silence" hook is narrated with `[PAUSE] [PAUSE]`, never played), **3.6** (nine minutes on turn-taking with no audio; everything is deferred to 3.7, which is only 5 minutes), **7.3** and **7.4** (fine as theory), **10.5** (a mock dashboard B-ROLL is specified; good). Demos referencing things that do not exist in `03-code/`: `opt_out` persona (9.9), `SPELLING_RULES` (4.3), `uv.lock` and the `uv.loc[k]` line (12.2), `part_of_day` on `join_waitlist` (5.9), `telephony/` JSON templates (8.2, 8.5; created live), `labs/` directory for lab outputs (labs tell students to create it; fine).

Tests: `make test` → 211 passed in 1.21 s (matches 13.4's "211 passed"). `pytest tests/agent tests/evals -m offline` → 21 passed, 32 deselected (13.4 says 20/28). `pytest tests/agent/test_safety.py -m offline` → 14 passed (matches 11.5). `simulated_caller.py --mock` → 4/4. Live tests not run (no `OPENAI_API_KEY`).

### 3. SLIDES AND IMAGES

- **Cue specificity:** every `[SLIDE n: title]` in all 15 files carries the exact bullet text, table or diagram layout. Diagram cues describe elements and build order (e.g., `section-01:166-176` D1, `section-03:54-56` SFU, `section-03:689-696` turn-taking timeline, `section-08:38` call path, `section-09:142-153` failure→test map, `section-13:112-119` architecture). Comparison tables are fully written (1.3 slide 6, 6.4 slide 3, 12.1 slide 7, 14.3 slide 6). This is the strongest part of the package.
- **Engaging visuals present:** before/after audio (3.7, 3.9, 4.1, 6.4 three-lane waveform playback, 12.8), failure demos (5.5, 5.6, 9.3, 9.4, 9.6, 9.8, 9.9, 11.4, 11.5, 13.4), trace visualisations (1.1 Langfuse, 9.1 trace walk-through, 10.3), dashboard mock-up B-ROLL (10.5), animated graphs (7.4 handoff, 9.2 pyramid, 10.1 timed turn, 11.1 ringing phone). Not bullet-only.
- **Avatar >60 s violations per section** (blocks >140 words): S1 2, S2 1, S3 0, S4 1, S5 0, S6 4, S7 1, S8 2, S9 3, S10 2, S11 0, S12 1, S13 0, S14 1, S15 0. Total 18 (line numbers in the executive summary, item 3).
- **`slide-deck-outline.md` coverage:** no entry for 3.4, 7.2, 12.2, 12.3, 12.5, 14.2 (all SC) or for any lab/assignment intro. Stale names at `:85` (`join_waitlist(name, phone, preferred_day)`) and `:150` (`PipelineTask`, `PipelineRunner`). Slide-count table (`:161-180`) is explicitly a v1.0 estimate. The outline references a 10-second "You can now..." section-end card for every section; the scripts never cue it (zero occurrences of "You can now" in `02-lecture-scripts/`), so the editor has to invent it from `recording-guide.md §9`.
- **Version banner:** every section header carries the footer rule; 6-10 restate it as a lower third for the first 10 s. Consistent.

### 4. ENGAGEMENT

- **Hooks:** teaching lectures open well (1.2 IVR menu, 3.6 "two complaints", 5.2 "a rule that will save you weeks", 9.1 recorded failure, 11.1 Doctor Chen, 12.1 "two hundred callers at 9 AM", 13.1a "Stop here."). 29 lectures open without a hook (list in item 9 above): all 13 quiz intros, 7 lab/assignment intros, and 2.1, 3.3, 5.6, 7.2, 7.5, 13.2, 15.3.
- **Promise:** present in nearly every teaching lecture ("By the end of this lecture, you'll..." or equivalent in the first 60 words). Missing in 7.3, 7.4, 10.5, 12.4 (they state the topic, not the outcome).
- **Questions to camera:** zero question marks in spoken text for 2.7, 3.3, 3.4, 4.5, 5.8, 5.9, 7.1, 7.3 (plus quiz/lab intros). 3.3 and 3.4 are the first code-along and first live demo; 7.1 is 839 words of exposition with no question.
- **Concrete numbers:** abundant (latency budget line items, 7 c vs 28 c per minute, 26% → 3.76% WER, $78 vs $192 per day, 4 failures in 4 turns). Pass.
- **Recap with 3 bullets:** every lecture has a `Recap` line, but it is a single sentence, not a 3-bullet card; the production guide requires "exactly 3 bullet points". The scripts never cue a `[SLIDE: Recap]` with three bullets, so the editor must derive them.
- **Bridge:** every lecture has a `Transition` line. 2.5's spoken bridge contradicts it (item 2).
- **Banned phrases (grep over spoken text):** "welcome back" ×2 (`section-05-tools.md:1199`, `section-13-capstone.md:215`). "basically", "let's dive in", "in this video we will", "without further ado", "as I mentioned earlier", "so yeah", "before we get started", "hi guys": 0 each. ("Let's walk through" / "Let's build" appear but are not on the banned list.)

### 5. WORD COUNT VS DURATION (140 wpm)

Method: `scratchpad/analyze_scripts.py` (output in `scratchpad/analysis.json`). Target = the video minutes in each lecture's header (video intro length for labs/quizzes), which equals the curriculum minutes for all teaching lectures.

- **No lecture is more than 20% over.** The highest ratios are 8.8 (1.17, quiz intro), 4.6 (1.10), 4.7 (1.07), 5.8 (1.07), 3.8 (1.05), 6.6 (1.05).
- **Lectures more than 20% under target (ratio < 0.80):** 69 of 97. Of these, the ones with no demo audio to fill the gap are the real problem: **3.1 (0.72), 3.5 (0.68), 3.6 (0.71), 1.5 (0.73), 15.3 (0.76), 12.7 (0.64)**, plus the quiz intros 1.6 (0.66), 4.8 (0.75), 5.10 (0.76), 11.6 (0.68), 14.4 (0.76).
- **Deepest shortfalls (< 0.55) in SC/DM lectures:** 2.3 (0.48, 472 words / 7:00), 5.5 (0.48), 5.6 (0.47), 3.3 (0.49), 2.2 (0.54), 2.4 (0.55), 5.2 (0.55), 5.7 (0.55), 3.9 (0.56), 5.4 (0.56), 13.4 (0.57), 13.5 (0.57), 3.4 (0.58), 5.3 (0.58), 12.5 (0.58), 7.5 (0.59), 12.3 (0.59). These need 3-6 minutes of non-narration screen time each. 5.6 (9:00 target, 4:12 of talking) and 2.3 (7:00, 3:22) are the least plausible.
- **Course total:** 73,909 spoken words ≈ 528 min of narration vs 687 min claimed video (77%). Section totals (words / claimed video min): S1 4,279/39, S2 3,667/44, S3 5,916/68, S4 4,355/45, S5 5,468/70, S6 4,234/42, S7 5,393/56, S8 5,787/57, S9 9,103/88, S10 4,297/47, S11 3,791/38, S12 5,677/57, S13 6,392/67, S14 3,242/32, S15 2,308/18.
- The per-lecture "~N spoken words" numbers in the section header tables are accurate to within ±10% of my counts in every case checked (e.g., 1.1 header ~625 vs 623; 9.3 ~1,000 vs 1,047; 13.2 ~1,280 vs 1,285).

### 6. CORRECTNESS SPOT CHECKS (livekit-agents 1.8.3 installed; pipecat not installed in this environment)

Verified correct by introspection: `AgentServer`/`@server.rtc_session(on_simulation_end=...)`/`cli.run_app`; `TurnHandlingOptions{turn_detection, endpointing, interruption, preemptive_generation, user_turn_limit}`; `EndpointingOptions{mode, min_delay, max_delay}`; `InterruptionOptions{enabled, min_duration, min_words, resume_false_interruption, false_interruption_timeout, ...}`; `RunContext.with_filler(source, *, delay, interval, max_steps)`, `.disallow_interruptions()`, `.wait_for_playout()`; `get_job_context(required=False)`; `JobContext.is_fake_job/delete_room/transfer_sip_participant/add_sip_participant/simulation_context/primary_session`; `AgentSession.reset_away_timer/usage/history/shutdown`, `user_away_timeout=15.0` default, `max_tool_steps=3` default; `ChatMessage.metrics`; `session.start(agent, capture_run=...)`; `RunAssert.{next_event, skip_next_event_if, contains_message, contains_function_call, contains_agent_handoff, no_more_events}`; `ChatMessageAssert.judge` is a coroutine; `mock_tools(agent, mocks, *, session=None)`; `metrics.UsageCollector` deprecated; `metrics_collected` logs a deprecation; `telemetry.set_tracer_provider(provider, *, metadata, allow_pii)`; `SessionConnectOptions{stt/llm/tts_conn_options, max_unrecoverable_errors}`; `inference.STT(..., fallback=, extra_kwargs=)`, `inference.TTS(..., fallback=)`, `inference.TTS.update_options(voice, model, language, extra_kwargs)`; `llm.FallbackAdapter(llm, attempt_timeout, max_retry_per_llm, retry_interval, retry_on_chunk_sent)`; `Agent.update_tools/update_instructions`; `Agent.default.llm_node`; `StopResponse`; `livekit.agents.beta.EndCallTool`, `beta.workflows.WarmTransferTask`; `SimulationContext`/`SimulationVerdict` in `livekit.agents.simulation`; `openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin", modalities=, turn_detection=, input_audio_transcription=, max_session_duration=)`; `openai.types.realtime.realtime_audio_input_turn_detection.SemanticVad`; default `tts_text_transforms=["filter_markdown", "filter_emoji"]`; preemptive generation `enabled` defaults to `True` (3.6's claim is right).

Wrong or unverified:
- `section-06-realtime.md:110, 157`: "LiveKit recycles the connection by default every 20 minutes (`max_session_duration`)". The 1.8.3 plugin default is `None`. Remove or re-verify.
- `section-07-knowledge-and-handoffs.md:1119`: `spoken = ev.language.language`. `UserInputTranscribedEvent.language` is `LanguageCode | None`, a `str` subclass with no `.language` attribute. Use the repo's `str(ev.language).split("-", 1)[0]`.
- `section-13-capstone.md:461` and `agents/s13_capstone_receptionist.py:308`: `preemptive_generation=True` on `AgentSession` is deprecated in 1.8.3 ("Use turn_handling=TurnHandlingOptions(...) instead"). It is also the default, so the line can simply be removed (the warning is hidden by `filterwarnings` in `pyproject.toml`).
- `section-06-realtime.md:73, 78`: default side-channel transcription `gpt-4o-mini-transcribe`. The string exists in the plugin, so plausible, but `RealtimeModel.input_audio_transcription` defaults to `NOT_GIVEN`; say "the plugin's default" rather than asserting the model name, or verify in the plugin source before recording.
- `section-08-telephony.md:555-561, 648` (8.4) shows `transfer_to_human` with inline try/except; the repo now routes through `transfer_sip_caller()` and `hang_up()` helpers (`agents/common.py:745-800`) so the on-screen code no longer matches the file it claims to open.
- 9.4 uses `pytest-repeat` (`--count=5`, `section-09:706`) which is not in the `dev` extra (`pyproject.toml:14-20`).
- "verify" flags that look stale or contradictory: `section-12-deploy.md:40` ("`agents/s12_chaos_demo.py` ... must be added to the repo") and `section-13-capstone.md` 13.4 recording note (`test_capstone.py` "created live ... make sure both exist") describe work already done; `video-generation-plan.md:137` (".env.chaos key revocation") contradicts the 12.8 script's kill-switch design; `qa-checklist.md:131` asks to verify `UsageCollector` forms. The fallback model strings (`google/gemini-2.5-flash`, `assemblyai/universal-streaming`, `deepgram/aura-2`) remain correctly flagged as unverified in 12.x/13.3 and should be checked before recording 12.8/13.3.
- Curriculum stale rows: `curriculum.md:22, 73, 233` (UsageCollector), `:282` (PipelineTask/PipelineRunner), `:169` (5.9 typed SC, signature without `patient_name`).

---

## (d) Recommended fixes (concrete, in priority order)

1. **Reconcile prose to code (CLAUDE.md rule):**
   - 7.8: delete "It isn't in the repo file" (`section-07:1095-1097`); replace the snippet with the real `follow_caller_language()` and `FOLLOW_CALLER_LANGUAGE=1`; fix `ev.language.language` → `str(ev.language).split("-", 1)[0]`.
   - 13.3 (`section-13:674`) and 12.8 note (`section-12:1279`): describe `recover_after_error` (transfer if SIP caller + number, else `ERROR_GOODBYE` + hang-up); replace the 13.2 `on_error` block at `section-13:478-484` with the current code.
   - 5.9: remove `part_of_day` from the spec slide, docstring and `add_to_waitlist` call (`section-05:1172-1173, 1212-1224`), or add it to `agents/s05_booking_agent.py` and `ClinicScheduler.add_to_waitlist` (the challenge doc `05-projects/challenges.md:127` already describes an optional `part_of_day`, so adding it to the code is the smaller change). Align `curriculum.md:169` and `slide-deck-outline.md:85`.
   - 4.3: add `SPELLING_RULES` to `agents/s04_voice_prompting.py` (or to `prompts.py` as `NAME_RULES`) so the reference matches the typed file.
   - 5.3/5.7: show the mixin's real `find_available_slots` (with `next_available` fallback and `_filler`) at the 5.7 refactor, and replace "the only differences should be names and comments" with a list of the three extras.
   - 6.2 (`section-06:266`): say the mixin skips string fillers in pure realtime mode (`can_say`) and point to `test_string_fillers_are_skipped_only_in_pure_realtime_mode`.
   - 12.2: either add `COPY pyproject.toml README.md uv.loc[k] ./` + `uv sync --locked` to `deploy/Dockerfile` and commit `uv.lock`, or cut the narration at `section-12:304-306` and the `uv.lock` entry at `:201`.
   - 8.4: update the on-screen `transfer_to_human`/`end_call` blocks to the helper-based code.
   - 9.9: add the `opt_out` persona to `tests/evals/simulated_caller.py` (the lecture tells students it "stays in the file").
   - 13.2/code: drop `preemptive_generation=True` (default is on) or move it into `TurnHandlingOptions` inside `build_turn_handling`.
   - 13.4: change "20 passed, 28 deselected" to the real numbers, or say "about twenty".
   - Delete the stale "must be added to the repo" notes (`section-12:40`, 13.4 recording note).

2. **Fix the Section 2 bridge:** change `section-02:542` to "Next, before you build anything, you'll run the finished Riley and hear where you're headed."

3. **Split the 18 avatar blocks over 140 words** by inserting a `[SLIDE]` or `[B-ROLL]` cue mid-block. Priority: 9.2:186, 10.1:103, 6.3:486, 8.1:48, 1.3:388, 6.1:64 and :88, 10.5:691, 2.1:126, 9.3:473.

4. **Pick one pronoun for Riley** (the prompt says "AI assistant", 1-5 use "it") and apply it to Sections 6-9 (34 edits). Add the decision to `recording-guide.md §2` so the avatar voice direction matches.

5. **Close the slide-only runtime gap:** either lower the curriculum minutes for 3.1 (8→6), 3.5 (9→7), 3.6 (9→7), 1.5 (7→6), 15.3 (5→4) or add a short demo to each (3.6 is the obvious candidate: play the 3.7 "round two" cut-off clip as the hook). Then re-check `qa-checklist.md`'s ±20% rule.

6. **Make the production docs agree:** regenerate the lecture-type counts in `recording-guide.md:23-30` from the curriculum (or delete them and point to `video-generation-plan.md §2`); change `video-generation-plan.md:137` to the kill-switch procedure; update `slide-deck-outline.md:150` to `PipelineWorker`/`WorkerRunner` and `:85` to the real signature; change `qa-checklist.md:131` to "`metrics_collected`, `metrics.log_metrics`, `session.usage` forms match §6; `UsageCollector` must not appear"; fix `curriculum.md:22, 73, 169, 233, 282`.

7. **Complete `slide-deck-outline.md`:** add entries for 3.4, 7.2, 12.2, 12.3, 12.5, 14.2 and one generic "lab/assignment intro" template; add a `[SLIDE: Recap]` with three bullets to every lecture script (or state in the outline that K6 bullets are the three learning objectives) and a `[SLIDE: You can now...]` cue at the end of each section's last lecture, since no script currently cues either.

8. **Engagement pass:** replace the two "Welcome back" openings (5.9 → "Here's the version I'd ship, and the three places most first attempts go wrong"; 13.2 → "Three hundred lines. That's the whole production receptionist, and almost none of it is new"). Give the 13 quiz intros and 7 lab intros a one-line hook before the question count. Add at least two questions to camera in 2.7, 3.3, 3.4, 4.5, 5.9, 7.1 and 7.3.

9. **Align lab time estimates:** change the spoken estimates in 2.5, 6.5, 10.6 and 12.7 to the lab headers (45 / 75 / 75 / 90 min), or shorten the labs.

10. **Before recording, verify the remaining flagged claims:** 6.1 `max_session_duration` (remove the 20-minute figure), the fallback model strings in `.env.example` against LiveKit Inference's current list, `lk agent` and `lk sip` CLI flags, LiveKit Simulations availability (9.14), and the Agents Playground UI (3.4). Add `pytest-repeat` to the `dev` extra if 9.4's `--count=5` demo stays.
