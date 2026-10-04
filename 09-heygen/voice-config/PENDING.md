# Voice Configuration — PENDING

> **Status:** Awaiting the course owner's choice (see `MY_DECISIONS_REQUIRED.md`). Shared by Courses 2, 3 and 4.

| Setting | Value |
|---|---|
| **Voice** | `PENDING` — chosen by the course owner in HeyGen studio |
| **Where the ID lives** | Environment variable `HEYGEN_VOICE_ID` only (never in this repo) |
| **Language** | English (US) |
| **Speaking rate** | ~140 words per minute (scripts are written to this; if a script runs long, cut it, don't speed up the voice) |
| **Loudness target** | –16 LUFS (normalized in post-production) |
| **Pronunciation** | `voice-ai-agents-course/09-production/tools/pronunciation.json`. Course 2 terms are **not in it yet**: add DeepEval, RAGAS, G-Eval, promptfoo, Garak, PyRIT, GEval and gpt-4.1 (Langfuse, MCP, RAG and gpt-4.1-mini are already there) before the Module 3 pilot |

## Action Items

1. Course owner selects a voice that matches the tone below, together with the avatar (`../avatar-config/PENDING.md`).
2. Set `HEYGEN_VOICE_ID` in the environment.
3. Run the 3-scene pilot (see the avatar file) and listen for technical terms; add fixes to `pronunciation.json`.
4. Record the voice **name** here and rename the file to `voice-config.md`.

## Voice Tone Guidelines

- **Conversational:** a knowledgeable colleague, not robotic or formal.
- **Confident:** declarative statements. "This fails because…", not "This might possibly fail…".
- **Clear:** good enunciation on technical terms ("hallucination", "faithfulness", "retrieval-augmented generation", "guardrails").
- **Paced:** natural pauses at sentence breaks and at every `[PAUSE]` cue.
