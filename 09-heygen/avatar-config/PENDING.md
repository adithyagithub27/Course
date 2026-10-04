# Avatar Configuration — PENDING

> **Status:** Awaiting the course owner's choice (see `MY_DECISIONS_REQUIRED.md`). Shared by Courses 2, 3 and 4: one avatar across all three courses.

| Setting | Value |
|---|---|
| **Avatar** | `PENDING` — chosen by the course owner in HeyGen studio |
| **Avatar style** | TBD (business casual recommended) |
| **Background** | TBD (Deep Navy `#0A1628` or a subtle dark gradient, per `10-graphics/design-system.md`) |
| **Where the ID lives** | Environment variable `HEYGEN_AVATAR_ID` only. Never write the ID or any API key into this repo (`CLAUDE.md`). |

## Requirements

- Chosen before the first HeyGen batch (Module 3 pilot, per `PRODUCTION-GUIDE.md`: never generate the whole course before Module 3 has passed review).
- Record the **name** of the chosen avatar and style here (not the ID), then rename this file to `avatar-config.md`.

## Action Items

1. Course owner selects the avatar and the voice (`../voice-config/PENDING.md`) together.
2. Set `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` in the shell (or an untracked `.env`).
3. Pilot: `python voice-ai-agents-course/09-production/tools/heygen_batch.py generate 09-heygen/scenes/section-03.json --limit 3`; check lip sync, pacing and tone.
4. If approved, generate Module 3 in full, review, then the remaining modules one at a time.
