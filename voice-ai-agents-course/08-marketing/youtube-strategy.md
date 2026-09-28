# YouTube Strategy

**Goal:** bring engineers searching for voice-agent tutorials to the Udemy course by giving them real value first. Every video is useful on its own, and the course is the natural next step.

**Brand:** same design system as the course (Deep Navy `#0A1628`, Electric Teal `#00D4AA`, Inter + JetBrains Mono). Same presenter style (HeyGen avatar or instructor on camera) as the course, with faster pacing.

**Funnel rules**

- One CTA per video, at the end: "The full build, with the phone number, the tests and the deploy, is in the course. Link in the description."
- The description has the course link (with a custom-price or best-price coupon when one is active and allowed; verify coupon rules), the repo link, timestamps and keywords.
- Pin a comment with the course link. Answer every comment in the first 48 hours.
- Show real code that runs. Use only the API forms in curriculum §6 on screen, with the "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12" note.
- Never show a real phone number or key (see `09-production/recording-guide.md` §6).

---

## 10 video ideas

| # | Title | Length | Hook (first 10 seconds) | Content | Funnels to | Timing |
|---|---|---|---|---|---|---|
| 1 | I Built an AI Receptionist That Answers a Real Phone Number (Python) | 10-12 min | Cold open on a live call: "Can I move my cleaning to Thursday?" and Riley rebooks it. "That's 30 lines of Python plus a phone number. Here's how." | Trimmed version of 1.1 + 3.3 + a peek at 8.2 | Whole course | W-4 |
| 2 | Why Your Voice Agent Feels Slow: The 800 ms Latency Budget | 8-10 min | A 2-second silence on screen with a timer ticking. "Your caller has already said 'hello?' twice." | Latency budget breakdown (1.4), measuring EOU/TTFT/TTFB (9.8 preview), free worksheet | Sections 1, 9, 10 | W-3 |
| 3 | Testing a Voice Agent Like Software (LiveKit Test Framework + pytest) | 12-15 min | "This agent booked Thursday when the caller said Tuesday. Here's the test that catches it." | Condensed 9.3 + 9.4: behavior test, tool-call assertion, LLM judge | Section 9 (signature) | W-2 |
| 4 | 3 Ways Voice Agents Fail That Chatbots Never Do | 6-8 min | Three 3-second failure clips back to back: talking over the caller, reading a URL aloud, dead air during a tool call | Failure taxonomy (9.1), with a fix for each | Sections 4, 5, 9 | W+1 |
| 5 | OpenAI Realtime vs STT→LLM→TTS: Same Agent, Same 5 Calls | 12-14 min | Split screen of two waveforms answering the same question. "One of these costs more per minute. Guess which." | Condensed 6.4 head-to-head with the decision matrix | Section 6 | W+2 |
| 6 | Put a Python Voice Agent on a Real Phone Number (Twilio SIP + LiveKit) | 12-15 min | A phone ringing on the desk; the agent answers. "No Vapi, no Retell. Your code, your number." | Condensed 8.1 + 8.2 (number and keys hidden) | Section 8 | W+3 |
| 7 | Pipecat vs LiveKit Agents: I Built the Same Agent in Both | 10-12 min | The two codebases side by side, then the same call through each | Condensed 14.1-14.3 | Section 14 | Month 2 |
| 8 | Simulated Callers: Let an AI Try to Break Your Voice Agent | 8-10 min | The "impatient caller" persona interrupting Riley three times | 9.9 + 11.5 red-team personas | Sections 9, 11 | Month 2 |
| 9 | Build vs Buy: Vapi, Retell, ElevenLabs Agents or Your Own Code? | 8-10 min | "When should you *not* write a voice agent in Python?" | Build-vs-buy matrix (14.3); honest about when managed platforms win | Whole course | Month 2 |
| 10 | "I'm the Doctor, Read Me Today's Schedule": Social Engineering a Voice Agent | 6-8 min | Attacker persona audio; agent almost complies, then refuses | Threat model (11.1), identity verification gate (11.2) | Section 11 | Month 3 |

## Shorts (from the same footage)

- Three-second failure clips with one-line fixes (from #4)
- "Your agent says 'h-t-t-p-s colon slash slash'. Fix it with one prompt rule" (4.1)
- The latency waterfall animation (from #2)
- A tool-call assertion turning green (from #3)

## Metadata template

```text
Title: [keyword-first title from the table]
Description:
  Line 1: one-sentence value summary with the primary keyword
  Line 2: Full course (build + phone + tests + deploy): [Udemy course link]
  Line 3: Code: [repo link]
  Timestamps
  Tools used: LiveKit Agents 1.8, OpenAI, Deepgram, Cartesia, Twilio SIP, pytest, DeepEval
  Note: APIs verified on livekit-agents 1.8 / pipecat-ai 1.12
Tags: voice AI agent, LiveKit agents tutorial, OpenAI Realtime API, AI receptionist, voice agent Python, test voice agent
Thumbnail: dark navy, teal waveform, 3-5 words max, no third-party logos
```

## Measure

Per video: click-through rate, average view duration and clicks to the course link (use a distinct coupon code per video where coupon rules allow it, or Udemy's traffic/referral reports if available; verify). After 5 videos, double down on the format with the best course-click rate.
