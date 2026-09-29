# Production Hand-off: Running the Video Build with Claude Code on Your Laptop

The content for Courses 3 and 4 is complete in this repository. The video production (HeyGen generation, OBS screencasts, assembly, Udemy upload) has to happen on your laptop, because it needs your accounts, your microphone and your screen. This document tells you how to drive that work with Claude Code locally, phase by phase, with prompts you can paste.

---

## 1. One-time setup on the laptop

1. Install Claude Code and sign in (see the Claude Code docs for your OS).
2. Clone this repository and open a terminal in it:

```bash
git clone https://github.com/adithyagithub27/Course.git
cd Course
```

3. Create a local `.env` at the repo root (it is git-ignored) with your production keys:

```
HEYGEN_API_KEY=...
HEYGEN_AVATAR_ID=...
HEYGEN_VOICE_ID=...
OPENAI_API_KEY=...
```

4. Install the tool dependencies:

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r voice-ai-agents-course/09-production/tools/requirements.txt
```

5. Start Claude Code in the repo:

```bash
claude
```

Claude Code reads `CLAUDE.md` automatically, so it already knows the courses, the pipeline, the tools and the conventions. You do not need to explain the project each time.

### Two ways to work

- **Local session (simplest).** Run `claude` in the repo folder on the laptop and type the prompts below. Everything runs on your machine with your keys.
- **Remote Control from your phone or browser.** Run `claude remote-control` in the repo folder on the laptop. The session then appears in the Claude Code app, and you can send it instructions from anywhere while it executes on the laptop. Use this when a HeyGen batch or a long QA pass is running and you want to check in from elsewhere.

This cloud session cannot reach your laptop, so nothing below can be run from here.

---

## 2. Phase-by-phase prompts

Paste these into Claude Code on the laptop. Replace the course folder and section number as needed. Start with Course 3 (`voice-ai-agents-course`), Section 3, as the pilot.

### Phase 0: Decisions and pilot

```
Read voice-ai-agents-course/09-production/video-generation-plan.md and list the decisions in section 11 that are still open. Then generate a 30-second HeyGen test from the first [AVATAR] block of lecture 1.4 using the tools in voice-ai-agents-course/09-production/tools, and tell me the video URL when it is ready.
```

```
Record the pilot lecture 3.3 end to end: extract its avatar scenes, generate them in HeyGen, give me the OBS shot list for the screencast beats from the script, and produce the assembly checklist for CapCut. Do not generate any other lecture yet.
```

### Phase 1: Scene extraction for a section

```
Extract HeyGen avatar scenes for Section 3 of the voice course: run scene_extractor.py on 02-lecture-scripts/section-03-first-agent.md with --polish, write the manifest to 09-production/scenes/section-03.json, and show me the scene count, estimated avatar minutes and any scene over 1,400 characters.
```

### Phase 2: HeyGen batch generation

```
Generate the Section 3 avatar scenes in HeyGen from 09-production/scenes/section-03.json. Submit with heygen_batch.py generate, then poll with --wait and download into 09-production/generated/S03. Report any failed scenes with their error text and do not resubmit failures without asking me.
```

```
Scene 3.3-02-teach1 mispronounces "Cartesia". Add the correct spoken form to pronunciation.json, re-extract only lecture 3.3 with --polish, regenerate just that scene, and leave the other scenes untouched.
```

### Phase 3: Screencast preparation

```
For lecture 5.3 of the voice course, produce an OBS recording plan from the script: the exact files to have open, the commands to run in order, the terminal size and font from the recording guide, and the moments where I should pause for a cut. Then verify the code in 03-code runs by executing make test and the agent's --help.
```

```
Before I record Section 9, run the full test suite in voice-ai-agents-course/03-code and confirm every test the scripts show on screen passes. If anything fails, fix the code, keep the script unchanged, and tell me what changed.
```

### Phase 4: Call demos (Course 3 only)

```
Set up the call-capture rig from section 5 of the video plan for my operating system: tell me the virtual audio device to install, the OBS audio track configuration, and give me a checklist to confirm Riley's voice and my voice are on separate tracks before I record lecture 3.9.
```

```
Convert the conversation events in demos/lecture-3-9.jsonl into captions with transcript_to_srt.py, speaker labels Riley and Caller, and save them next to the recording.
```

### Phase 5: Assembly and QA

```
Build the assembly checklist for lecture 3.3 following the 7-beat order in 09-heygen/PRODUCTION-GUIDE.md: which generated avatar clip, screencast segment, slide and recap card goes where, with the timestamps from the script. Then run the QA checklist in 09-production/qa-checklist.md against my exported MP4 metadata (resolution, frame rate, loudness) using ffprobe.
```

### Phase 6: Udemy upload

```
Prepare the Udemy upload for Section 3 of the voice course: list every lecture with its title, the 1-2 sentence description from 07-udemy-listing/lecture-descriptions.md, the downloadable resources from resources-per-lecture.md, and the quiz questions from 06-assessments/quizzes/section-03.md formatted for Udemy's quiz editor.
```

```
Check the whole voice course against 07-udemy-listing/publish-checklist.md and tell me which items are still open.
```

### Phase 7: Keeping content current

```
The livekit-agents package released a new minor version. In voice-ai-agents-course/03-code, update the pin, run make test, and list every lecture script whose code blocks no longer match the repo so I can decide whether to re-record.
```

---

## 3. Working rhythm that keeps quality up

- One section at a time. Extract, generate, review, record, assemble, QA, upload. Then the next section.
- Review Section 3 fully before generating anything else in HeyGen. Pronunciation and pacing problems found there save credits on the remaining 14 sections.
- Ask Claude Code to update `BUILD_LOG.md` after every exported lecture. It keeps the status visible and gives you a natural place to resume after a break.
- Commit manifests, status files and the build log. MP4s stay out of git.

---

## 4. When something is unclear

Ask Claude Code to explain before acting. Useful patterns:

```
Read the curriculum for the observability course and tell me which lectures need a Grafana recording, in order, with the compose commands to have the stack running first.
```

```
Show me every place in the Course 4 scripts where a price is quoted, so I can verify them against current pricing before recording Section 6.
```

Nothing in this file needs to be memorised. `CLAUDE.md` gives every local session the same context, so any well-phrased request about a lecture, a section or a tool will land.
