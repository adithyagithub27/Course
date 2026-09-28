# Video Generation Plan: Production Voice AI Agents with Python

> **Stack:** HeyGen (avatar + narration voice), OpenAI API (runs Riley in demos, polishes scripts for TTS, optional voiceover TTS and caption transcripts), OBS Studio (screencasts), CapCut or DaVinci Resolve (assembly), Udemy (publish).
> **Inherits:** the 7-beat lecture structure, tone rules, scene types and QA bar from `../../09-heygen/PRODUCTION-GUIDE.md`. This document covers only what is different or additional for a course whose subject is itself audio.
> **Curriculum:** v1.1, 97 lectures, ≈11.3 h video (`../01-curriculum/curriculum.md`).

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

Derived from curriculum v1.1. Quizzes have no video. Labs, assignments and challenges get a 1-3 minute intro video.

| Type | Count | Video needed | Tracks |
|---|---|---|---|
| TH talking head | 10 | Full avatar | A |
| SL slides | 26 | Avatar for hook/recap/bridge, slides + voice for teach | A |
| SC screencast / code-along | 33 | Avatar hook and recap, OBS body | A + B (+ C when the code is run) |
| DM live demo | 13 | Avatar hook, call capture body | A + C |
| LAB / AS / CE intros | 15 | Short avatar or voice + slide | A |
| QZ quizzes | 13 | None (Udemy quiz) | none |
| **Total videos to produce** | **84** (of 97 lectures) | | |

Six lectures record as Part A/B (5.3, 7.5, 8.2, 9.3, 13.2, 13.5), so the upload count is **90 videos**.

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

- **From the agent:** `s10_observed_agent.py` and the capstone export `conversation_item_added` events to JSONL. `tools/transcript_to_srt.py` (in the same tools folder as the HeyGen scripts) converts them to SRT for the editor.
- **From the recording:** run the mixed audio through OpenAI's transcription API with speaker prompts if you did not capture events.

For latency demos (1.4, 3.7, 6.4, 9.8) also overlay the measured numbers from `metrics_collected` so students see "EOU 480 ms, LLM TTFT 610 ms, TTS TTFB 190 ms" as they hear the gap.

### 5.4 Failure demos need scripting

Lectures 1.1, 3.9, 6.4, 11.5 and 12.8 show Riley failing. Failures must be reproducible on camera:

- Use the `BROKEN=<case>` toggles in `agents/s03_hello_agent.py` for 3.9, and `MOCK_MODE=1` when you need an exact, repeatable wrong answer.
- For 12.8, revoke a key in a throwaway `.env.chaos` rather than your real one.
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
- OBS Studio with two audio tracks configured; CapCut or DaVinci Resolve; Figma or Canva for slides.
- Docker Desktop for Section 12.

---

## 12. Tools in this folder

| File | Purpose |
|---|---|
| `tools/scene_extractor.py` | Parses lecture scripts, extracts `[AVATAR]` blocks, optionally polishes text for TTS with OpenAI, writes scene manifests |
| `tools/heygen_batch.py` | Generates one HeyGen video per scene from a manifest, polls status, downloads MP4s, resumes safely |
| `tools/transcript_to_srt.py` | Converts agent conversation events (JSONL) to SRT captions for call demos |
| `tools/pronunciation.json` | Term → spoken form glossary applied during polish |
| `tools/requirements.txt` | Python dependencies for the tools |

All tools read secrets from environment variables (`HEYGEN_API_KEY`, `OPENAI_API_KEY`). HeyGen endpoint paths and limits are the ones documented at the time of writing; the scripts print the URL they call so a mismatch is obvious. Verify against the HeyGen API reference before the first batch.
