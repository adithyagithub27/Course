# Recording Guide

> Extends `09-heygen/PRODUCTION-GUIDE.md` (7-beat structure, 140 wpm word budget, -16 LUFS, 1920×1080 H.264 30 fps) and `10-graphics/design-system.md` for the voice course. The voice course brings two new challenges: **recording live audio from an agent** and **recording phone calls safely**.

---

## 1. Workflow overview

```
Script (02-lecture-scripts/) ──► Scene plan (per lecture)
        │
        ├─► Avatar scenes ──► HeyGen batch render (per section)
        ├─► Slides/diagrams ──► Figma/Canva (K1-K7 scene kits)
        ├─► Screencasts ──► OBS (one session per section, same layout)
        └─► Live demos (console, playground, phone) ──► OBS + audio loopback
                     │
                     ▼
        Assemble (DaVinci Resolve / CapCut) ──► Loudness normalize ──► Captions ──► QA ──► Upload
```

Lecture types from the curriculum map to recording methods:

| Type | Count | Recording method |
|---|---|---|
| SL (slides) | 26 | HeyGen avatar (picture-in-picture or cut-ins) + slide/diagram scenes |
| SC (screencast/code-along) | 47 | OBS screen + avatar intro/outro (beats 1-3, 6-7) |
| DM (live demo) | 9 | OBS screen + **live agent audio** (phone audio for 1.1 and 13.5; A/B audio for 3.9; the chaos demo 12.8; Simulations 9.14) |
| TH (talking head) | 7 | HeyGen avatar, or real camera for 1.1 intro / 13.1a gate / 15.3 bonus / 15.4 careers if possible |
| LAB walkthrough | 7 | Short OBS walkthrough of the lab doc and expected result |
| CE challenge (5.9) | 1 | Spec card → **pause card** ("Pause now and build it") → OBS solution walkthrough |

Counts are for curriculum v1.1. **Split 5.3, 7.5, 8.2, 9.3, 13.2 and 13.5 into Part A / Part B** at record time (same script, two uploads, each under ten minutes). Give Part B a 10-second recap hook instead of a cold hook.

## 2. HeyGen avatar

- Use the **same avatar and voice** as Courses 1 and 2 (see `09-heygen/avatar-config/` and `voice-config/`) for series consistency.
- **Pronunciation dictionary.** Add these before rendering anything: LiveKit ("LIVE-kit"), Pipecat ("PIPE-cat"), Deepgram, Cartesia ("car-TEE-zha" or check the vendor's own pronunciation), Silero ("sih-LEH-ro"), SIP ("sip"), PSTN (spell out), VAD (spell out, "V-A-D"), STT/TTS/LLM (spell out), WER ("W-E-R" or "word error rate"), TTFT/TTFB (say "time to first token/byte"), `gpt-realtime` ("G-P-T realtime"), uv ("U-V"), Maple Street, Riley.
- **Avatar vs agent voice.** The avatar's voice must sound clearly different from Riley's TTS voice so students always know who is speaking. Pick a Riley voice with a different gender, pitch or accent from the avatar, and label agent audio on screen (`Riley (agent)` waveform badge).
- Keep avatar segments ≤ 60 s without a visual change (PRODUCTION-GUIDE rule 1).
- **Disclosure:** see `07-udemy-listing/publish-checklist.md` §9 (verify Udemy's AI content policy).

## 3. OBS screencast setup

| Setting | Value |
|---|---|
| Canvas / output | 1920×1080, 30 fps |
| Encoder | x264 or hardware H.264; CRF ~18 / high-quality preset for the master recording |
| Recording format | MKV (crash-safe), remux to MP4 after |
| Scenes | `Code` (editor full screen), `Code+Terminal` (70/30 split), `Browser` (Playground/Langfuse/LiveKit dashboard), `Phone demo` (browser/terminal + phone camera or waveform) |
| Audio tracks | Track 1: narration mic (if not avatar), Track 2: **agent/system audio** (loopback), Track 3: **caller audio** (phone or second mic). Separate tracks let you balance the mix later |

### Editor and terminal theme

| Item | Setting |
|---|---|
| Editor | VS Code with a dark theme matched to the design system (background `#0A1628`; strings teal `#00D4AA`; functions amber `#FFB020`; comments `#94A3B8`) |
| Font | JetBrains Mono |
| **Editor font size** | **20-22 px** at 1920×1080 (so it reads on a 13" laptop and at 720p playback). Zoom (`Ctrl/Cmd +`) rather than scaling in post |
| **Terminal font size** | **20-22 px**. Prompt in teal; a short prompt such as `riley $` (hide user, host and path) |
| Visible lines | ≤ 15 lines of code per screen (design system); collapse the rest with `# ...` |
| Minimap, breadcrumbs, extensions UI | Off |
| Notifications | Do Not Disturb on the OS; close Slack/email; hide the dock and taskbar |
| File label | Filename visible top-left (matches `03-code/` paths) |
| Version banner | Corner note: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12" |

## 4. Audio chain

### Narration (if the instructor records voiceover or on-camera segments)

```
Dynamic or small-diaphragm condenser mic
  → audio interface (48 kHz / 24-bit)
  → OBS/DAW track: high-pass 80 Hz → noise gate/expander (light) → compressor (3:1, ~-18 dB threshold)
  → limiter (-1 dBTP) → loudness normalize in post to -16 LUFS integrated
```

- Treat the room (soft furnishings, no bare walls behind the mic); record a 10 s room-tone sample per session.
- Wear closed-back headphones. **Speakers + mic + voice agent = echo and self-interruption.** The agent will hear itself and barge in on its own speech.

### Agent audio (console mode, Playground, web front end)

- **Capture it digitally, not through the mic.** Use a loopback device: BlackHole or Loopback (macOS), VB-Audio Cable / VoiceMeeter (Windows), a PipeWire/PulseAudio monitor source (Linux). Route system output → loopback → OBS Track 2, and monitor on headphones.
- For console mode (`python agents/s03_hello_agent.py console`), the student-facing demo uses the laptop mic. **Use a headset mic when recording** so the agent's output doesn't leak back into its input.
- Don't process the agent's TTS audio (no compression or EQ) beyond level matching. Students should hear what the agent actually sounds like.

### Phone audio (Section 8, 1.1, 13.5)

- Phone audio is narrowband (8 kHz). It will sound thinner than console mode, and that's expected and teachable (8.1).
- Capture options, best first:
  1. **Softphone on the recording machine** (a SIP/WebRTC softphone or a VoIP app) → loopback → OBS. You get both sides digitally.
  2. **Mobile phone on speaker next to a second mic** → OBS Track 3. Simple, but picks up room noise. Use it only for "real phone" authenticity shots like the promo's cold open.
- Mix: caller and agent at similar perceived loudness; the combined dialogue at -16 LUFS.

## 5. Live demos: rehearsal rules

- Run every demo **3 times before recording**. Voice demos are non-deterministic, so if a demo needs a specific outcome, use `mock_tools` or a seeded scheduler state from `src/maple/scheduler.py`.
- **Keep genuine failures when they teach something** (turn-taking mistakes in 3.7, the failing case in 13.4). Cut failures that are just noise (a network blip).
- Say the lecture ID and the take number out loud at the start of each take ("3.7, take 2") to make editing easier.
- Pre-warm the agent (`download-files` done, the dev worker running) so viewers don't watch cold starts, unless the cold start is the lesson (12.1).

## 6. Recording phone-call demos safely (no numbers, no keys)

> The course puts an agent on a real phone number. One exposed number invites prank calls and toll fraud against your account. One exposed key can run up a large bill.

### Before recording

- [ ] **Use dedicated recording accounts and projects:** a separate LiveKit Cloud project, a separate Twilio (sub)account with its own number, and separate OpenAI/Deepgram/Cartesia keys created only for recording.
- [ ] **Spend limits and alerts on every provider** (usage caps where available; verify the options each provider offers).
- [ ] **Twilio number:** restrict geographic permissions for outbound calls to your own country; turn off international dialing in the recording account; set call-rate limits where available.
- [ ] **Outbound demos (8.5) call only phones you own** or a test number. Never call a real person without consent, and never a number from a list.
- [ ] `.env` is **never opened on screen**. Show `.env.example`, which has placeholders only.
- [ ] Clear shell history, or use a fresh shell with `HISTFILE=/dev/null`. Don't `echo $OPENAI_API_KEY` or `printenv`.
- [ ] Terminal prompt shows no username, hostname or home path.
- [ ] Browser: use a separate profile with no saved passwords, no bookmarks bar and no autofill; close other tabs.
- [ ] LiveKit and Twilio dashboards: before recording, check which fields show phone numbers, SIP URIs, trunk IDs, project URLs, API key IDs and billing details.

### During recording

- [ ] **On-screen phone numbers use the fictional 555-01XX range** (e.g., `+1 555 0100`) in slides, code comments and `livekit.toml.example`. The transfer example in curriculum §6 (`tel:+15551234567`) is fine as a placeholder.
- [ ] When a real number must appear (caller ID in SIP participant attributes, logs, dashboards), **mask it in OBS**: add a Blur or Pixelate filter or a solid Deep Navy rectangle source positioned over the field. Check that it still covers the field after any scroll or zoom.
- [ ] Log output: run demos with PII redaction on (`src/maple/pii.py`, lecture 11.3), so caller numbers are redacted in the terminal logs.
- [ ] Don't read your real number aloud. The agent's read-back of the caller number in demos should use a test phone whose number you don't mind being redacted, and you **also mute or bleep that part of the audio**.
- [ ] Anyone else who speaks on a recorded call (e.g., a colleague as "the human" in the transfer demo 8.4) gives written consent to be recorded and published. Check your local call-recording consent law (see `10-resources/telephony-compliance-checklist.md`; not legal advice).

### After recording

- [ ] **Scrub pass in the edit:** step through every frame that shows a terminal, a dashboard or a browser URL bar, looking for keys, numbers, SIP URIs, emails and project IDs.
- [ ] **Rotate every key used in recording**, even if you believe none was shown. Release or port the recording phone number after the course is published, or keep it locked down.
- [ ] Delete the call recordings and transcripts in provider dashboards that you don't need (data retention).

## 7. Screen content rules for voice lectures

- Show the **waveform or transcript panel** whenever agent audio plays, so viewers can follow on mute and captions can sync.
- Label speakers on screen: `Caller`, `Riley (agent)`, `Human (transfer)`.
- For latency demos, show a visible timer or the metrics output next to the audio.
- Use Alert Red only to highlight failures (design system rule).

## 8. Special recordings in curriculum v1.1

| Lecture | What's special | How to record |
|---|---|---|
| 1.1 | Three calls: works / naive agent fails / fixed agent passes tests | Record the naive-agent call using the lecture 3.9 failure toggles (`BROKEN=<case>` env var in `agents/s03_hello_agent.py`), or an equivalent deliberately misconfigured build. Label it on screen as `Naive agent (intentionally broken)`. Record the "works" call on the deployed capstone. Show the test run for call 3 |
| 2.6 | Talk to the finished capstone before building | Console mode, headset mic; keep it short and delightful |
| 2.7 | Spending caps + `MOCK_MODE=1` | Show provider limit screens with account IDs and billing details masked; run `MOCK_MODE=1 python agents/s03_hello_agent.py console --text` |
| 3.9 | Five failures with before/after audio | Record each failure and its fix back to back with identical caller lines. Level-match the pairs so the only difference is the behaviour |
| 6.4 | Same five calls, side by side | Record both builds with the same scripted caller audio; play them one after another or as a split-screen with two waveforms |
| 7.8 | Spanish and Hindi callers | Use native speakers (with consent) or clearly labelled synthetic caller audio; have native speakers check the captions |
| 9.13 | Audio-in tests | Use only recordings you have the rights to (your own voice, consenting speakers or licensed datasets); no real patient calls |
| 9.14 | LiveKit Simulations | **Verify availability and pricing before recording.** If it isn't available on your plan, record it as a demo-only walkthrough and say so on screen |
| 12.8 | Chaos: kill a provider mid-call | Use a throwaway key and revoke it live; mask the key ID; create a new key afterwards |
| 13.1a | Capstone gate | Full-screen pause card: "Stop here. Build it from the brief. Time box: one week." |
| 15.4 | Careers | No salary figures on screen or in narration |

## 9. Engagement mechanics (from `01-curriculum/curriculum-review.md` §5)

Build these into production. They aren't lecture content, but they affect ratings and completion.

1. **Section-end "You can now..." card.** A 10-second K6-style slide at the end of the **last lecture of every section**, listing three concrete abilities (e.g., Section 8: "You can now: answer a real phone number · transfer to a human · place a reminder call"). Design it to be screenshot-friendly: large text, the course name in small type, no URLs.
2. **Build log.** In 1.5 and 2.6, ask students to keep a `BUILD_LOG.md` in their repo and post one line per section in Q&A. Repeat the prompt verbally on each section-end card ("Add today's line to your build log"). This is an educational prompt, not a review request.
3. **Hear-it moments.** Every time a setting changes turn-taking or the voice (3.6, 3.7, 3.9, 4.3, 6.3, 6.4, 7.8, 8.3), play **before and after** audio with the same caller line, level-matched, and show an on-screen `BEFORE` (red) / `AFTER` (teal) label (design system 4.6).
4. **Failure-first demos.** Start each build section (3, 4, 5, 7, 8, 11, 12) with about 30 seconds of the broken version (talking over the caller, a wrong booking, a dead-air tool call, a leaked appointment, a provider outage) before building the fix. Use Alert Red overlays only on the failure.
5. **Q&A seeding.** On launch day, post the five most likely questions per section with answers (draw them from `10-resources/troubleshooting.md` and the pilot/beta feedback). Pin the setup and version threads.
6. **Announce version pins.** Put "Verified on livekit-agents 1.8 / pipecat-ai 1.12" on the **first slide of every code lecture**, and keep a pinned Q&A thread for breaking changes. Update the thread and send an educational announcement whenever the repo pins change.

Checklist for each lecture: see `qa-checklist.md` §1 (engagement mechanics item).

## 10. Export and delivery

- Master: 1920×1080, H.264, 30 fps, AAC 48 kHz stereo, -16 LUFS integrated, -1 dBTP true peak.
- File naming: `S{section}-L{lecture}-{slug}.mp4`, e.g., `S08-L04-transfer-to-human.mp4`.
- Keep the project files and raw OBS tracks until 6 months after publishing, for re-cuts after framework updates.
