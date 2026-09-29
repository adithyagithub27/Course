# Claude Code project guide: Udemy AI course production

This repository holds the full production packages for a series of Udemy courses. Read this file first, then the curriculum of the course you are working on. Treat each course's `01-curriculum/curriculum.md` as the source of truth for lecture IDs, titles, durations and file names.

## Courses in this repo

| Folder | Course | Status |
|---|---|---|
| `/` (root folders `00-` to `15-`) | Course 2: AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse) | Content written; positioning needs the refresh in `00-course-strategy/next-course-market-research.md` §6 |
| `voice-ai-agents-course/` | Course 3: Production Voice AI Agents with Python (LiveKit Agents 1.8, OpenAI Realtime, Pipecat 1.12, Twilio SIP) | Complete package, ready to record |
| `agent-observability-course/` | Course 4: AI Agent Observability & Cost Control (OpenTelemetry, Langfuse 4, LiteLLM, Prometheus, Grafana) | Complete package, ready to record |
| `00-course-strategy/next-course-market-research.md` | Market research and ranking for all courses | Reference |

Course 1 (Generative AI & AI Agents: Zero to Production) is produced elsewhere and is not in this repo.

## Production pipeline

Avatar narration with **HeyGen**, screencasts with **OBS Studio**, assembly in **CapCut or DaVinci Resolve**, publishing on **Udemy**. The rules (7-beat lecture structure, tone, scene types, QA bar) are in `09-heygen/PRODUCTION-GUIDE.md`. The per-course video plans are `voice-ai-agents-course/09-production/video-generation-plan.md` and `agent-observability-course/09-production/video-generation-plan.md`.

Production tools live in `voice-ai-agents-course/09-production/tools/` and are shared by both courses:

- `scene_extractor.py` turns lecture scripts into HeyGen scene manifests (optionally polishing text for TTS with the OpenAI API).
- `heygen_batch.py generate|poll` submits scenes to HeyGen and downloads finished MP4s. It is resumable.
- `transcript_to_srt.py` converts agent conversation events to captions.
- `pronunciation.json` is the spoken-form glossary. Add terms here, never inline in scripts.

Secrets come from environment variables only: `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, `OPENAI_API_KEY`. Never write them into files or commit `.env`.

## Conventions

- Lecture IDs look like `3.3` or `13.1a`. Generated files are named `S{section:02}/{lecture_id}-{beat}.mp4`.
- Spoken narration runs at about 140 words per minute. If a script runs long, cut it; do not speed up the voice.
- Every code lecture opens with a version banner naming the verified library versions from the curriculum.
- Scripts contain production cues in square brackets: `[AVATAR]`, `[SLIDE n: ...]`, `[SCREEN: ...]`, `[CODE: ...]`, `[DEMO: ...]`, `[PAUSE]`. Only `[AVATAR]` blocks go to HeyGen.
- Prices, Udemy policy details and third-party UI steps are flagged "verify" in the content. Check them before recording; do not remove the flags without checking.
- When a script and the student code disagree, the code is right unless the code has a bug. Fix the prose.

## Student code repos

- `voice-ai-agents-course/03-code/`: run `make test` (offline unit tests) and `make console AGENT=...`. Needs PortAudio for console mode. Verified on livekit-agents 1.8.3 and pipecat-ai 1.12.0.
- `agent-observability-course/03-code/`: run `make test` (329 offline tests) and `OFFLINE=1 make replay` for a free day of traffic. Verified on langfuse 4.15, opentelemetry-sdk 1.45, litellm 1.103.

Always run the tests before recording a code lecture. If a library upgrade breaks them, pin the version in `pyproject.toml` rather than rewriting scripts mid-recording.

## Working style

- Work one section at a time: extract scenes, generate, review, record screencasts, assemble, QA, then move on.
- Never generate the whole course in HeyGen before Section 3 has passed review.
- Keep a `BUILD_LOG.md` at the repo root with one line per completed lecture (ID, date, status). Update it whenever a lecture is exported.
- Commit generated manifests and status files; do not commit MP4s (they are ignored).
