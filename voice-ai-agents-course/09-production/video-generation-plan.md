# Video Generation Plan: Production Voice AI Agents with Python

> **Stack:** HeyGen (avatar + narration voice), OpenAI API (runs Riley in demos, polishes scripts for TTS, optional voiceover TTS and caption transcripts), OBS Studio (screencasts), CapCut or DaVinci Resolve (assembly), Udemy (publish).
> **Inherits:** the 7-beat lecture structure, tone rules, scene types and QA bar from `../../09-heygen/PRODUCTION-GUIDE.md`. This document covers only what is different or additional for a course whose subject is itself audio.
> **Curriculum:** v1.1, 97 lectures, ≈11.4 h video (683 min in the 89 video lectures) (`../01-curriculum/curriculum.md`).

---

## 1. The one thing that makes this course different to produce

Every other course you have made shows code and slides. This one has to let students **hear** a voice agent: its latency, its interruptions, its mistakes and its fixes. Roughly a third of the lectures contain a live conversation between a person and Riley. If those recordings are muddy, one-sided or out of sync, the course fails regardless of how good the avatar looks.

So the plan has three production tracks instead of two:

| Track | What it produces | Tool | Share of runtime |
|---|---|---|---|
| A. Avatar | Hooks, promises, context, teach beats on TH and SL lectures, recaps, bridges | HeyGen | ≈30% (≈200 min) |
| B. Screencast | Code-alongs, terminal, tests, dashboards, deploy | OBS + narration voice | ≈50% (≈340 min) |
| C. Call capture | Two-sided audio of Riley conversations, phone calls, failure demos, A/B comparisons | LiveKit recording or virtual audio device + OBS, with on-screen transcript | ≈20% (≈140 min) |

Track C is new. Section 5 below is dedicated to it.

---

## 2. Lecture inventory by production type

Counted from the lecture table in `../01-curriculum/curriculum.md` (v1.1, 115 items). This is the single place the production docs count lecture types; `recording-guide.md` and `qa-checklist.md` point here. Every item has a script in `02-lecture-scripts/`, including a short video intro for each lab, assignment and quiz.

| Type | Count | Lecture IDs | Video needed | Tracks |
|---|---|---|---|---|
| TH talking head | 7 | 4.5, 8.6, 13.1a, 13.6, 15.1, 15.3, 15.4 | Full avatar | A |
| SL slides | 26 | 1.2, 1.3, 1.4, 3.1, 3.2, 3.5, 3.6, 4.1, 4.2, 5.1, 6.1, 7.1, 7.3, 7.4, 8.1, 9.1, 9.2, 10.1, 10.5, 11.1, 12.1, 12.4, 12.6, 13.1, 14.1, 14.3 | Avatar for hook/recap/bridge, slides + voice for teach | A |
| SC screencast / code-along | 47 | 1.5, 2.1-2.4, 2.6, 2.7, 3.3, 4.3, 4.4, 5.2-5.7, 6.2, 6.3, 7.2, 7.5, 7.8, 8.2-8.5, 9.3-9.10, 9.13, 10.2-10.4, 11.2-11.4, 12.2, 12.3, 12.5, 13.2-13.4, 14.2 | Avatar hook and recap, OBS body | A + B (+ C when the code is run) |
| DM live demo | 9 | 1.1, 3.4, 3.7, 3.9, 6.4, 9.14, 11.5, 12.8, 13.5 | Avatar hook, call capture body | A + C |
| CE challenge | 1 | 5.9 | Spec slide, pause card, OBS solution walkthrough (full 6-minute lecture) | A + B |
| LAB intros | 7 | 2.5, 3.8, 4.6, 6.5, 7.6, 10.6, 12.7 | 1:30-2:00 avatar + slides (generic intro template in `slide-deck-outline.md`) | A |
| AS intros | 5 | 4.7, 5.8, 8.7, 9.11, 13.7 | 1:30-4:00 avatar + slides; the project itself is a Udemy assignment | A |
| QZ intros | 13 | 1.6, 3.10, 4.8, 5.10, 6.6, 7.7, 8.8, 9.12, 10.7, 11.6, 12.9, 14.4, 15.2 | 0:45-1:30 avatar + one topic slide; the questions are a Udemy quiz | A |
| **Total** | **115** | | **97 lectures** (TH + SL + SC + DM + CE + LAB) **+ 5 assignment intros + 13 quiz intros** | |

Udemy quiz and assignment items cannot hold a video, so upload each quiz or assignment intro as a short video lecture placed directly before its quiz or assignment (verify the current Udemy curriculum editor; if it allows a video inside the item, use that instead). Six lectures record as Part A/B (5.3, 7.5, 8.2, 9.3, 13.2, 13.5), which adds 6 uploads: **121 video files** in total.

---

## 3. Narration: two options, pick one before recording anything

Consistency rule from the production guide: one voice, one avatar, one look across the whole course. That forces a decision now.

| | Option A: fully synthetic | Option B: hybrid (recommended) |
|---|---|---|
| Avatar beats | HeyGen avatar, HeyGen voice | HeyGen avatar with **your cloned voice** |
| Screencast voiceover | Same HeyGen voice, audio-only export | **You narrate live while recording in OBS** |
| Call demos | Your real voice talking to Riley (unavoidable) | Your real voice talking to Riley |
| Voice consistency | Breaks: HeyGen voice on slides, your voice in demos | Consistent: it is your voice everywhere |
| Authenticity for code-alongs | Lower, TTS pacing does not follow typing | Higher, you react to what happens on screen |
| Production time | Lowest | Medium (narrating 340 min of screencasts) |
| HeyGen credits | Highest (avatar + all voiceover) | Lowest (avatar beats only) |
| Risk | Udemy learners are sensitive to fully synthetic technical courses; review risk on a fast-moving topic where you may need to re-record often | Voice clone quality must pass a listening test |

**Recommendation: Option B.** The demos force your real voice into the course anyway. Clone it in HeyGen so the avatar sounds like you, then narrate screencasts live. It also makes quarterly re-records cheaper: re-record the changed screencast, regenerate only the affected avatar beat.

If you choose Option A, at minimum record the call demos with your real voice and add a one-line note in lecture 1.5 that the presenter is an AI avatar. Check Udemy's current policy on AI-generated content before publishing either way.

---

## 4. Track A: HeyGen avatar pipeline

### 4.1 One-time setup

1. Choose or create the avatar (business casual, neutral dark background `#0f172a` or the course design-system colour). Record the avatar ID in `../../09-heygen/avatar-config/PENDING.md` (rename to `avatar-config.md` once filled).
2. Create the voice: clone from 2-3 minutes of clean speech (Option B) or pick a stock voice (Option A). Record the voice ID.
3. Generate a 30-second test with a paragraph from lecture 1.4 (contains numbers, "LiveKit", "Riley", "SIP", "OpenAI"). Check pronunciation, pacing at ~140 wpm, and lip sync.
4. Fix pronunciations once with a pronunciation glossary (see `tools/pronunciation.json`): LiveKit, Pipecat, Cartesia, Deepgram, SIP, PSTN, WebRTC, VAD, Riley, Twilio, Langfuse, RAG, LLM, TTS, STT, p95.
5. Create an API key (HeyGen API access is plan-dependent; verify your plan includes it).

### 4.2 Batch generation flow

```
02-lecture-scripts/section-XX.md
        │  tools/scene_extractor.py  (splits [AVATAR] blocks, polishes for TTS with OpenAI, chunks ≤1,400 chars)
        ▼
09-production/scenes/section-XX.json   (manifest: lecture_id, scene_id, text, est_seconds)
        │  tools/heygen_batch.py generate   (POST /v2/video/generate per scene, records video_id)
        ▼
09-production/scenes/section-XX.status.json
        │  tools/heygen_batch.py poll       (GET /v1/video_status.get until completed, downloads MP4)
        ▼
09-production/generated/S03/3.3-hook.mp4 ...
```

Rules:
- One HeyGen video per **scene**, never per lecture. Scenes are 15-60 seconds. This keeps regenerations cheap and matches the "avatar never talks more than 60 s" rule.
- Chunk at 1,400 characters per API call (HeyGen enforces a per-scene text limit; verify the current value).
- Generate a whole section in one batch, review, then move on. Never generate the entire course before reviewing Section 3.
- Keep `speed` at 1.0 and fix pacing in the script, not the voice setting.
- File names: `S{section:02}/{lecture_id}-{beat}.mp4`, beats: `hook`, `promise`, `context`, `teach1`, `teach2`, `recap`, `bridge`, `intro`.

### 4.3 Credit estimate

| Item | Minutes |
|---|---|
| Avatar runtime in final videos | ≈200 |
| Retakes and pronunciation fixes (30%) | ≈60 |
| Promo video and Udemy landing clips | ≈5 |
| **Total HeyGen generation** | **≈265 min** |

HeyGen sells credits by generated minute and API access by plan tier. Look up your tier's price per minute and multiply by 265. Budget a 20% buffer. Prices change; do not carry a number from this document into a budget without checking the pricing page.

### 4.4 Visual assets: diagrams and slide decks

Slides and diagrams are built from files in the repo, not drawn per lecture in Figma (decision A7 in `../../14-quality-review/2026-10-01-fix-plan.md`).

| Asset | Where it lives | How it is made |
|---|---|---|
| Master diagrams D1-D16 | `voice-ai-agents-course/10-graphics/diagrams/D{n}-{slug}.svg` (for example `D1-voice-pipeline.svg`, `D6-sip-call-flow.svg`) | Drawn once as SVG from the specs in `slide-deck-outline.md` (master diagram list), with the palette and type in the root `10-graphics/design-system.md`. Build steps are `<g id="build-N">` groups in the same file. Reused in every lecture that cues them |
| Section slide decks | `voice-ai-agents-course/10-graphics/slides/section-XX.pptx` (one per section, `XX` = `01` to `15`) | Generated from the `[SLIDE n: title]` cues in `02-lecture-scripts/section-XX-*.md`: one slide per cue, with the cue's title and its bullets or table as the slide text |
| Recap and "You can now" cards | Inside the section decks | Come from each lecture's `[SLIDE n: Recap]` cue (three bullets) and each section's `[SLIDE n: You can now]` cue (decisions A1/A2) |
| K1/K2/K7 cards, lower thirds, version banner | Editor templates | Built once in the editor from the design system |

Generate the decks with:

```bash
python voice-ai-agents-course/09-production/tools/slide_builder.py --course voice-ai-agents-course
```

Rules:
- Edit slide text in the script, then regenerate. Never hand-edit a generated `.pptx`; the next run overwrites it.
- Regenerate a section's deck whenever its script changes, before exporting slide images for the edit.
- Where a cue names a master diagram (D1-D16), place the SVG from `10-graphics/diagrams/` on that slide (export to PNG at 1920×1080 if the editor needs raster).
- Commit the SVGs and generated decks with the scripts so the slides and the narration never drift apart.

---

## 5. Track C: capturing Riley's voice (the part most instructors get wrong)

### 5.1 Why default screen recording fails

In console mode Riley speaks through your speakers and listens on your mic. If you record with OBS "desktop audio + mic", the mic picks up the speaker output, Riley's echo cancellation fights the recording, and viewers hear a hollow, half-duplex mess.

### 5.2 Three capture setups

| Setup | Use for | How |
|---|---|---|
| **1. LiveKit room recording (best quality)** | Web and phone demos in Sections 3-13 | Run the agent in `dev` mode, join from the Agents Playground or your web front end, and record the room with LiveKit Egress (room composite, audio + optional video). You get a clean, mixed, perfectly synced file of both sides. Requires LiveKit Cloud egress (verify availability and cost on the free tier). |
| **2. Virtual audio device + OBS** | Console-mode demos, quick failure demos in 3.9 | Route Riley's output to a virtual device (macOS: BlackHole 2ch; Windows: VB-Cable; Linux: PulseAudio/PipeWire loopback). OBS captures the virtual device on one track and your mic on a second track. Wear headphones so the mic never hears the speaker. Export both tracks; mix in the editor with Riley slightly left of centre and you slightly right so the ear separates them. |
| **3. Phone call recording** | Section 8 and 13 phone demos | Record from the platform side, not from a phone held to a mic: LiveKit room recording of the SIP room (setup 1) or Twilio call recording. Never record a phone speaker with a laptop mic. |

### 5.3 Always show the transcript

Viewers cannot rewind audio easily. For every call demo, overlay a live transcript: speaker label, text, and a timestamp. Two ways:

- **From the agent:** no course agent writes a transcript file (by design: `s10_observed_agent.py` exports metrics and a `call_summary`, and `s11_guarded_agent.py` only logs redacted lines). For recording sessions, add a temporary `@session.on("conversation_item_added")` handler to the demo copy that appends one JSON line per item with `t` (seconds since call start), `role` and `text`; `tools/transcript_to_srt.py` (in the same tools folder as the HeyGen scripts) converts that file to SRT for the editor. Don't commit the handler to the student files.
- **From the recording:** run the mixed audio through OpenAI's transcription API with speaker prompts if you did not capture events.

For latency demos (1.4, 3.7, 6.4, 9.8) also overlay the measured numbers from `metrics_collected` so students see "EOU 480 ms, LLM TTFT 610 ms, TTS TTFB 190 ms" as they hear the gap.

### 5.4 Failure demos need scripting

Lectures 1.1, 3.9, 6.4, 11.5 and 12.8 show Riley failing. Failures must be reproducible on camera:

- Use the `BROKEN=<case>` toggles in `agents/s03_hello_agent.py` for 3.9, and `MOCK_MODE=1` when you need an exact, repeatable wrong answer.
- For 12.8, use the kill switch in `agents/s12_chaos_demo.py`, exactly as the script does: run `uv run python agents/s12_chaos_demo.py dev`, then `touch /tmp/riley-kill-llm` in a second terminal to make the primary LLM fail every request, and `rm /tmp/riley-kill-llm` to recover; repeat with `CHAOS_NO_FALLBACK=1` for the no-fallback take. No key is revoked, so nothing needs rotating afterwards.
- Record each failure and its fix back to back in the same session so voice, room tone and settings match.

### 5.5 Privacy and safety on camera

- Never show real API keys, phone numbers or LiveKit credentials. Use a dedicated demo `.env` and blur or crop the terminal when it prints identities.
- Use your own phone numbers for outbound demos and say so on screen.
- Twilio trial accounts prepend a trial message to calls; upgrade the demo account before recording Section 8.

---

## 6. Track B: screencast standards for this course

Follow the production guide, plus:

- **Terminal:** dark theme, 20 pt font, 100×30 columns, cwd shown, no shell prompt noise. Agent logs are verbose; set `LOG_LEVEL=INFO` for recording, `DEBUG` only when the lecture teaches debugging.
- **Two windows max:** editor left, terminal right. Playground or phone dialer in a third scene when needed.
- **Type, don't paste,** for the first occurrence of every new API (`AgentServer`, `@function_tool`, `session.run`). Paste for repetition.
- **Version banner:** first slide of every code lecture shows "verified on livekit-agents 1.8 / pipecat-ai 1.12".
- **Tests on screen:** always show the pytest summary line; students trust green.

---

## 7. Where the OpenAI API is used in production

| Use | Model | Purpose | Estimated cost |
|---|---|---|---|
| Running Riley in demos | `gpt-4.1-mini` (cascaded), `gpt-realtime` (S6, S13) | ≈200 minutes of recorded conversation, plus rehearsals ×3 | Cascaded LLM only ≈$5-15; realtime audio is billed per audio token and is the expensive line, budget ≈$30-80 for S6/S13 demos and rehearsals (verify current pricing) |
| Script polish for TTS | `gpt-4.1-mini` via `tools/scene_extractor.py --polish` | Spell out numbers, remove markdown, expand acronyms on first use, apply pronunciation glossary | <$5 for the whole course |
| Optional voiceover TTS (Option A only) | `gpt-4o-mini-tts` | Alternative to HeyGen audio-only export | ≈340 min of narration ≈ 500k characters; check per-character pricing |
| Caption transcripts | `gpt-4o-transcribe` (or Whisper) | SRT for call demos when event capture is unavailable; Udemy auto-captions cover narration | <$10 |
| Quiz and lecture-description drafting | `gpt-4.1` | Already drafted in `06-assessments/` and `07-udemy-listing/`; use only for revisions | negligible |

Set a hard monthly spending cap on the OpenAI project used for production, separate from the project used for student-facing examples.

---

## 8. Assembly template (per lecture)

1. Import: avatar MP4s for the lecture, OBS screencast (two audio tracks), call capture (mixed WAV + SRT), slides PNG exports, recap card.
2. Timeline order follows the 7 beats: hook (avatar or failure audio), promise card, context (avatar or slide), teach (slides with voice), show (screencast or call capture), recap (card + voice), bridge (avatar).
3. Transcript overlay on every call segment. Latency numbers overlay where the script cues them.
4. Music sting on promise card only. No music under call demos; the pauses **are** the content.
5. Loudness: normalise the whole lecture to -16 LUFS. Riley's voice and yours should sit within 2 dB of each other.
6. Export 1920×1080, H.264, 30 fps, AAC 192 kbps. Name `S03-L3.3-hello-riley.mp4`.

---

## 9. Production schedule (12 weeks, batched by section)

| Week | Work | Output |
|---|---|---|
| 1 | Decisions (Section 11 below), avatar and voice setup, pronunciation test, capture-rig test with setups 1-3, record one full pilot lecture (3.3) end to end | Pilot approved |
| 2 | Freeze code repo v1 (`make test` green), record all Section 2-3 screencasts and call captures | S2-S3 raw |
| 3 | Generate S1-S3 avatar scenes, assemble S1-S3, QA, upload as unpublished | S1-S3 done |
| 4 | Record S4-S5 screencasts + call captures; generate avatars | S4-S5 raw + avatars |
| 5 | Assemble S4-S5; record S6-S7 (realtime demos need the most retakes) | S4-S5 done, S6-S7 raw |
| 6 | Telephony week: Twilio + SIP setup, record S8 phone calls with setup 3, generate S6-S8 avatars | S6-S8 raw + avatars |
| 7 | Assemble S6-S8; record S9 (testing) screencasts | S6-S8 done |
| 8 | Record S10-S11, generate S9-S11 avatars, assemble S9 | S9 done |
| 9 | Assemble S10-S11; record S12 deploy and chaos demo | S10-S11 done |
| 10 | Record S13 capstone (two sessions), S14 Pipecat, S15; generate avatars | S12-S15 raw |
| 11 | Assemble S12-S15, promo video, course image | All videos done |
| 12 | Full QA pass, captions review, quizzes and coding exercises entered in Udemy, landing page, publish | Live |

Buffer: none is built in. If any week slips, drop Section 14 (optional) from launch and add it as a free update in month 2.

---

## 10. QA additions for this course

On top of the production-guide checklist, every lecture with a call demo must pass:

- [ ] Both speakers clearly audible, no echo, no clipping, Riley and instructor within 2 dB.
- [ ] Transcript overlay matches the audio word for word.
- [ ] Latency numbers on screen match the audible gap (sanity check by ear).
- [ ] No credentials, real phone numbers or personal data visible.
- [ ] Failure demos are followed by the fix in the same lecture.
- [ ] Version banner present on code lectures.

---

## 11. Decisions and inputs required from the course owner

Blocking (needed before Week 1 ends):

| # | Item | Why |
|---|---|---|
| 1 | Narration option: A (fully synthetic) or B (hybrid, recommended) | Determines HeyGen credits, recording time and voice cloning |
| 2 | HeyGen avatar ID and voice ID (or a 3-minute clean voice sample to clone) | Batch generation cannot start without them |
| 3 | HeyGen plan with API access and a credit budget for ≈265 generated minutes | Confirms the pipeline in `tools/heygen_batch.py` can run |
| 4 | OpenAI project for production with a spending cap, separate from student examples | Cost control |
| 5 | LiveKit Cloud project for demos, with egress/recording enabled if available | Track C setup 1 |
| 6 | Deepgram and Cartesia keys (or LiveKit Inference only) | Riley must run for demos |
| 7 | Twilio account upgraded from trial, one phone number for Riley, one destination number for transfer demos | Section 8 and 13 |
| 8 | Brand: background colour, font, lower-third style, whether to disclose the AI avatar in lecture 1.5 | Consistency and policy |

Non-blocking (needed by Week 6):

| # | Item |
|---|---|
| 9 | Langfuse account (free tier) for Section 10 tracing demos |
| 10 | GitHub public repository name for the student code (README links must be final before recording S2) |
| 11 | A second machine or VM (Windows if you record on macOS, or vice versa) to record the setup lecture's OS differences |
| 12 | Udemy instructor profile, payout method, and premium instructor application if not already done |

Hardware and software (Option B):

- Dynamic or condenser USB microphone with pop filter, closed-back headphones (mandatory for Track C), quiet room.
- Virtual audio device installed and tested (BlackHole, VB-Cable, or PipeWire loopback).
- OBS Studio with two audio tracks configured; CapCut or DaVinci Resolve; `tools/slide_builder.py` for the decks (§4.4); Figma, Canva or Inkscape only for the course image and diagram touch-ups.
- Docker Desktop for Section 12.

---

## 12. Tools in this folder

| File | Purpose |
|---|---|
| `tools/scene_extractor.py` | Parses lecture scripts, extracts `[AVATAR]` blocks, optionally polishes text for TTS with OpenAI, writes scene manifests |
| `tools/heygen_batch.py` | Generates one HeyGen video per scene from a manifest, polls status, downloads MP4s, resumes safely |
| `tools/transcript_to_srt.py` | Converts agent conversation events (JSONL) to SRT captions for call demos |
| `tools/pronunciation.json` | Term → spoken form glossary applied during polish |
| `tools/slide_builder.py` | Builds one `.pptx` deck per section from the `[SLIDE]` cues in the scripts (see §4.4) |
| `tools/requirements.txt` | Python dependencies for the tools |

All tools read secrets from environment variables (`HEYGEN_API_KEY`, `OPENAI_API_KEY`). HeyGen endpoint paths and limits are the ones documented at the time of writing; the scripts print the URL they call so a mismatch is obvious. Verify against the HeyGen API reference before the first batch.
