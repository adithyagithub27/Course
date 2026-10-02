# Section 1: Welcome and How Voice Agents Work

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈38 min (6 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with the agent. Record the real audio. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word counts in each header are spoken words only (narration plus scripted demo dialogue), not cues or code. Where talking time is shorter than the target duration, the rest is demo audio, live typing, command output and on-screen dwell.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 1.1 | Meet Riley: one call that works, one that fails, one that's fixed | DM | 5:00 | ~625 |
| 1.2 | What a voice agent actually is | SL | 7:00 | ~900 |
| 1.3 | Cascaded vs speech-to-speech architectures | SL | 8:00 | ~975 |
| 1.4 | The latency budget: why 800 ms is the magic number | SL | 8:00 | ~1,000 |
| 1.5 | Course roadmap, repo tour and how to get help | SC | 6:00 | ~775 |
| 1.6 | Quiz: Voice agent fundamentals | QZ | 4:00 (1:30 video) | ~175 |

---

## Lecture 1.1 — Meet Riley: one call that works, one that fails, one that's fixed

| Field | Value |
|---|---|
| ID | 1.1 |
| Type | DM (live demo, three recorded calls) |
| Target duration | 5:00 (~625 spoken words, about 4:28 of talking at 140 wpm, including demo dialogue) |
| Learning objectives | 1. Hear the difference between a production voice agent and a naive one on the same request. 2. Name the three failures a naive agent makes (talking over the caller, mishearing, inventing availability) and the discipline that prevents them: testing. 3. State what you will have built by Section 13. |
| Prerequisites | None |
| Files used | Capstone demo recording (`agents/s13_capstone_receptionist.py` on a phone number), failure recording (naive agent: short endpointing, no tools, chat prompt), `make test` / eval run of the capstone suite |

### Script

[SCREEN: Black screen. Caption: "Call 1". A phone on a desk, caller ID overlay reads "Maple Street Dental". Ring tone plays twice.]

[DEMO: Call 1. Real recorded call to the capstone agent. Keep the audio unedited, including natural pauses. Live captions: caller in white, Riley in maple-orange.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**Caller:** Hi. I think I chipped a tooth last night. Can I get in this week?

**Riley:** Oh no, sorry to hear that. One moment while I check the schedule.

[PAUSE]

**Riley:** I have Thursday at one in the afternoon, or Friday at eight in the morning. Which works better?

**Caller:** Thursday. Wait, no, sorry. Friday.

**Riley:** No problem. Friday at eight. Can I get your first and last name?

**Caller:** Sam Ortiz.

**Riley:** Thanks, Sam. And the best number to reach you?

**Caller:** Five one two, five five five, zero one four eight.

**Riley:** Just to confirm: Sam Ortiz, Friday, October ninth at eight in the morning, for a chipped tooth. Shall I go ahead?

**Caller:** Yes, please. Oh, and can I talk to someone about an old bill?

**Riley:** You're booked for Friday at eight. And of course, I'm transferring you to our front desk now.

[B-ROLL: Short hold chime, then a human voice: "Front desk, this is Dana."]

[SCREEN: Caption: "Call 2". Same phone, same caller. Red caption tag: "Naive agent: chat prompt, no tools, default everything".]

[DEMO: Call 2. Same request to a naive agent. Record it for real: endpointing min delay 0.2 s, no tools, a chat-style prompt. Keep the talk-over audible. No reference file ships this agent; the closest is `BROKEN=markdown MIN_ENDPOINTING_DELAY=0.2 uv run python agents/s03_hello_agent.py console` (no tools, a markdown chat prompt, aggressive endpointing; it also turns off the symbol filters, so keep or trim any symbols read aloud).]

**Naive agent:** Hello! Thank you for calling Maple Street Dental! I'd be happy to help you with any questions you might have about our services, hours, or...

**Caller:** (talking over it) Hi, I chipped a...

**Naive agent:** ...appointments! How can I help?

**Caller:** I chipped a tooth. Can I get in... [pause] ...this week?

**Naive agent:** I'm sorry to hear that! Can you get in touch with us this week? Absolutely!

**Caller:** No, I mean, is there an appointment? Maybe Friday?

**Naive agent:** Great news! We have openings on Friday at nine, ten thirty, eleven, one, two fifteen and three forty-five. Which would you prefer?

[AVATAR]
That second call failed three ways in thirty seconds. [PAUSE] It talked over the caller. It cut her off mid-sentence and misheard the question. And then it confidently offered six Friday times. None of them are real. There's no calendar behind that agent. It made them up.

The caller hangs up happy. Then she shows up on Friday at nine to a full waiting room.

Here's the uncomfortable part. Both agents use the same kind of models. The difference isn't a smarter AI. It's engineering. Turn-taking settings. A prompt written for the ear. Real tools with real data. And tests that catch the failures before a caller does.

[SCREEN: Caption: "Call 3". Terminal. Run the capstone test suite: unit tests, behavior tests, evals. Wall of green. Zoom on three checks: `test_checks_availability_before_offering_times` and `test_reads_back_before_booking_then_books` in `tests/agent/test_booking_flows.py`, then the latency budget check `tests/evals/latency_report.py`, which exits non-zero when p95 is over budget (confirm the names at recording time). Then a latency report with p50 and p95 voice-to-voice, and a cost-per-minute line.]

This is call three. It's the fixed agent, and this time I'm not calling it. I'm testing it. Every failure you just heard has a test. One checks that Riley only offers slots returned by the scheduler tool. One checks that Riley reads back the details before booking. One fails the build if turn-taking pushes latency over budget. There are simulated callers that rush it, confuse it and try to trick it.

On the right, the numbers your boss will ask for. Median voice-to-voice latency, the slow tail at the ninety-fifth percentile, and cost per minute.

[SCREEN: Langfuse trace of Call 1. Expand one turn: STT, LLM, tool call `find_available_slots`, TTS. Hover over the timing bars.]

And this is the trace of call one. Every turn, every tool call, every millisecond. When a caller complains, you can find out exactly what happened.

[AVATAR]
So here's the promise. By Section thirteen, your Riley makes call one. On a real phone number. And it passes call three's tests, in continuous integration, every time you push.

You'll build it from an empty folder. Tools to book, reschedule and cancel. A knowledge base. Handoffs to a human. Guardrails against tricks. Deployment, monitoring and cost tracking.

Most voice AI tutorials stop at "it talks." That's call two. This course is about getting from call two to call one, and proving it with call three. [PAUSE] Let's start by looking inside.

[SLIDE 1: Recap]
- Naive agents talk over, mishear and invent slots
- The fix is engineering, not a smarter model
- Your Riley will pass call three's tests

**Recap:** A naive voice agent talks over callers, mishears them and invents availability, and this course teaches the engineering and testing that turn it into a production receptionist.

**Transition:** Next, we'll open the hood and name every component inside those calls, starting with what a voice agent actually is.

### Speaker notes: common student mistakes / Q&A

- "Is call one sped up?" No. Record it live and say so in the lecture description. Students trust the later latency lectures more when the hook is unedited.
- "Did you make the naive agent bad on purpose?" Only by using defaults a first-time builder picks: a chat prompt, no tools, an aggressive endpointing delay. Lecture 3.9 recreates each failure so students can hear it themselves.
- "Do I need a phone number to take the course?" No. Sections 1 to 7 run on your laptop mic and a browser. The phone number arrives in Section 8, on a Twilio trial.
- "Is Maple Street Dental real?" No. It's a fictional clinic, and all phone numbers in the course use the five-five-five range.

---

## Lecture 1.2 — What a voice agent actually is

| Field | Value |
|---|---|
| ID | 1.2 |
| Type | SL (slides) |
| Target duration | 7:00 (~900 spoken words, about 6:26 of talking at 140 wpm) |
| Learning objectives | 1. Distinguish a voice agent from an IVR and from a text chatbot. 2. Name the seven components of a voice pipeline: transport, VAD, STT, turn detection, LLM, tools and TTS. 3. Predict a typical failure for each component. |
| Prerequisites | 1.1 |
| Files used | Diagram: voice pipeline (slide 3); `03-code/agents/common.py` (`create_session`, shown briefly) |

### Script

[AVATAR]
Press one for appointments. Press two for billing. Press nine to hear these options again. [PAUSE] You've been trapped in that menu. Everyone has. That's an IVR, an interactive voice response system. And it's the thing voice agents are replacing.

So what exactly is the difference? Let's put three systems side by side.

[SLIDE 1: IVR vs chatbot vs voice agent]
- IVR: fixed menu tree, keypad or keywords, no understanding
- Chatbot: understands language, but text in, text out, and you wait for full replies
- Voice agent: understands language, speaks in real time, takes actions, handles interruptions

An IVR is a decision tree. It only understands what it was built to expect. Say "I chipped my tooth" and it has no idea what to do.

A chatbot understands language. But it lives in text. You type, you wait, you read a full paragraph. Nobody minds a two second pause in a chat window.

A voice agent understands language like a chatbot. But it has to behave like a person on the phone. It listens while you talk. It decides when you're finished. It answers in under a second. And when you interrupt, it stops talking. That last part sounds small. It's actually one of the hardest problems in this whole course.

[SLIDE 2: A voice agent is a real-time system, not a chatbot with a speaker]
- Audio arrives as a continuous stream, twenty milliseconds at a time
- The agent must decide when the caller has finished
- Every reply is a race against silence

Here's the mindset shift. A chatbot is request and response. A voice agent is a real-time system. Audio arrives in tiny frames, about fifty of them every second. The agent has to make decisions on a live stream, with a clock running.

[SLIDE 3: The voice pipeline, seven components]
Diagram, left to right: Caller → Transport (WebRTC / SIP) → VAD → STT → Turn detection → LLM (+ Tools) → TTS → Transport → Caller.
Each box has a one-line label:
- Transport: moves audio in and out
- VAD: is someone speaking right now?
- STT: speech to text
- Turn detection: are they done?
- LLM: decide what to say or do
- Tools: act on the world
- TTS: text to speech

Let's walk the pipeline one box at a time. I'll tell you what each part does, and the way it usually breaks.

[SLIDE 4: Transport: WebRTC and SIP]
- WebRTC: browsers and apps, low latency, built for real-time media
- SIP: the telephone network, via a SIP trunk
- Failure: packet loss, jitter, eight kilohertz phone audio

Box one is transport. It moves audio between the caller and your agent. In a browser or mobile app, that's WebRTC, the same technology behind video calls. On a phone, it's SIP, the protocol that connects the phone network to the internet.

In this course, LiveKit handles transport for you. That's a big deal. You never touch a raw audio socket.

How does it fail? Bad networks. Packets arrive late or not at all. And phone audio is sampled at eight kilohertz, half the quality of a browser. That will matter when we pick a speech-to-text model in Section 8.

[SLIDE 5: VAD: voice activity detection]
- Small, fast model: speech or not speech, every frame
- Runs locally (Silero), in a few milliseconds
- Failure: background noise triggers it, or soft speakers get missed

Box two is VAD, voice activity detection. It answers one question, many times a second. Is someone speaking right now? We'll use Silero, a tiny model that runs on your CPU in a few milliseconds.

VAD fails in noisy rooms. A TV in the background, a dog barking, a car on the road. Suddenly the agent thinks the caller is talking and stops mid-sentence.

[SLIDE 6: STT: speech-to-text]
- Streams partial transcripts while the caller speaks, then a final transcript
- Default in this course: Deepgram Nova-3
- Failure: names, drug names, numbers, accents

Box three is STT, speech-to-text. It streams words as the caller speaks, then settles on a final transcript. Our default is Deepgram Nova-3.

STT fails on exactly the words that matter most. Surnames. Medication names. Phone numbers. If the caller says "Ortiz" and STT hears "or tease," your booking is wrong before the LLM even sees it.

[SLIDE 7: Turn detection: are they done?]
- Silence alone is a bad signal: people pause mid-thought
- Semantic turn detector reads the words, not just the silence
- Failure: cutting people off, or awkward long waits

Box four is turn detection. This one surprises people. How does the agent know you've finished your turn? The obvious answer is silence. But think about how you give a phone number. "Five five five... two zero one..." You pause. You haven't finished.

So we combine silence with a small model that reads the transcript and predicts whether the sentence is complete. Get this wrong in one direction and Riley interrupts people. Get it wrong the other way and there's a painful gap before every reply. Section 3 is where you'll tune it.

[SLIDE 8: LLM and tools: the brain and the hands]
- LLM decides: reply, ask a question, or call a tool
- Tools: find slots, book, reschedule, cancel, look up clinic info, transfer
- Failure: hallucinated availability, wrong arguments, long rambling answers

Boxes five and six are the LLM and its tools. The LLM reads the conversation and decides what happens next. Sometimes that's a reply. Sometimes it's a tool call, like checking the schedule or booking a slot.

Here's the scariest failure in voice. Remember call two from the first lecture? The LLM invented six Friday times without ever calling a tool. The caller hangs up happy, and shows up to a full waiting room. That's why tools, and tests for tools, get two full sections.

[SLIDE 9: TTS: text-to-speech]
- Streams audio back sentence by sentence
- Default in this course: Cartesia Sonic-3
- Failure: reads markdown aloud, mangles numbers, mispronounces names

Box seven is TTS, text-to-speech. It turns the LLM's words into audio and streams it back, starting before the full reply is written. Our default is Cartesia Sonic-3.

TTS fails in funny ways that aren't funny in production. It reads "asterisk asterisk" out loud because the LLM wrote markdown. It says a phone number as "five hundred fifty-five million." Section 4 exists to fix this.

[SLIDE 10: Every box adds latency and a failure mode]
Table: Component | Typical failure | Where we fix it
- Transport | packet loss, 8 kHz audio | S8
- VAD | noise triggers | S3
- STT | names and numbers | S3, S9
- Turn detection | interrupts or long gaps | S3
- LLM | rambling, hallucination | S4, S9
- Tools | wrong args, fake availability | S5, S9
- TTS | reads symbols, bad numbers | S4

[SCREEN: VS Code, `03-code/agents/common.py`, scrolled to `create_session`. Highlight the `stt=`, `llm=`, `tts=`, `vad=` and `turn_handling=` lines one at a time, while a thumbnail of slide 3 in the corner lights up the matching box.]

And here's that same pipeline in the code you'll use from Section four on. One function in `agents/common.py` builds Riley's session. Speech-to-text, one line. The LLM, one line. Text-to-speech, one line. VAD, one line. Turn detection, one line. Transport is LiveKit itself, so it isn't a line at all, and tools live on the agent, which you'll meet in Section five. Seven boxes on a slide, five lines of Python.

[AVATAR]
Here's the key idea. Every box adds time. And every box adds a way to fail. A voice agent isn't one model. It's a relay race of seven runners, and the caller only hears the final time.

That's also why testing voice agents is different. A wrong answer might be the LLM's fault. Or the STT misheard. Or turn detection cut the caller off halfway through. You'll learn to test each box on its own, and the whole relay together.

[SLIDE 11: Recap]
- Seven boxes, from transport to TTS
- Every box adds latency and a failure mode
- Test each box, then the whole relay

**Recap:** A voice agent is a real-time pipeline of transport, VAD, STT, turn detection, an LLM with tools, and TTS, and each stage has its own failure mode.

**Transition:** Next, you'll see there are two very different ways to wire that pipeline together: cascaded and speech-to-speech.

### Speaker notes: common student mistakes / Q&A

- Mistake: treating VAD and turn detection as the same thing. VAD says "someone is making sound." Turn detection says "they've finished their thought." Riley needs both.
- "Why not just use a longer silence timeout?" Because every extra hundred milliseconds of waiting is felt on every single turn. Lecture 1.4 puts numbers on this.
- "Does the agent hear itself?" LiveKit applies echo cancellation on the client side for WebRTC. On speakerphone setups you may still see self-interruptions; Section 3 covers interruption thresholds.
- "Can I skip STT and TTS entirely?" Yes, that's the speech-to-speech approach in the next lecture.

---

## Lecture 1.3 — Cascaded vs speech-to-speech architectures

| Field | Value |
|---|---|
| ID | 1.3 |
| Type | SL (slides) |
| Target duration | 8:00 (~975 spoken words, about 6:58 of talking at 140 wpm) |
| Learning objectives | 1. Explain the cascaded STT → LLM → TTS pipeline and the realtime speech-to-speech approach. 2. Compare them on control, cost, latency, voice quality and tool reliability. 3. Describe the half-cascade hybrid and when to choose it. |
| Prerequisites | 1.2 |
| Files used | Comparison table (slide 6), `10-resources/architecture-decision-matrix.md` (preview), `03-code/src/maple/costs.py` (cost calculator run), console log from `03-code/agents/s03_hello_agent.py` |

### Script

[AVATAR]
There are two ways to build Riley. One uses three separate models passing text between them. The other uses a single model that hears audio and speaks audio directly. [PAUSE] Teams argue about this constantly. By the end of this lecture, you'll know which one to pick for which job, and why this course teaches both.

[SLIDE 1: Architecture 1: cascaded]
Diagram: Audio in → STT → text → LLM (+ tools) → text → TTS → audio out
- Three specialist models
- Text is the handoff format between them

The first design is called cascaded. Audio comes in. A speech-to-text model turns it into words. A text LLM decides what to say. A text-to-speech model turns that into audio. Three specialists in a row, passing text like a baton.

This is the pipeline you saw in the last lecture. It's also the default for Riley in Sections 3, 4 and 5.

[SLIDE 2: Architecture 2: speech-to-speech]
Diagram: Audio in → Realtime model (hears, thinks, speaks) → audio out
- One model, audio in and audio out
- Example: OpenAI `gpt-realtime`
- Transcripts produced on a side channel

The second design is speech-to-speech, sometimes called realtime. One model takes audio in and produces audio out. There's no separate transcription step and no separate voice. OpenAI's gpt-realtime is the model we'll use, in Section 6.

It still gives you text transcripts. But they're a side channel for your logs, not the thing the model reasons over.

[SLIDE 3: Why speech-to-speech sounds more human]
- Hears tone, hesitation, emphasis
- Can respond with matching emotion
- One network hop instead of three

Why would you want that? Because the model hears more than words. It hears hesitation. It hears that the caller sounds stressed. A cascaded pipeline throws all of that away the moment STT turns audio into text. "I'm fine" and "I'm... fine" look identical in a transcript.

It's also simpler on the wire. One model call instead of three. That can mean lower latency, especially on the first word of a reply.

[SLIDE 4: Why cascaded is still the production default]
- Swap any component: best STT, cheapest LLM, brand voice
- Inspect and test the text at every step
- Mature tool calling in text LLMs
- Usually cheaper per minute

So why doesn't everyone use speech-to-speech? Four reasons.

First, control. In a cascaded pipeline, you pick the best model for each job. A speech-to-text model tuned for phone audio. The cheapest LLM that passes your tests. A voice that matches your brand. With speech-to-speech, you get one vendor's bundle.

[SCREEN: Terminal log from a console session of `03-code/agents/s03_hello_agent.py` (the agent you'll run in Lecture 2.4). Highlight the caller's transcript line, then Riley's reply line: one turn, two plain-text records.]

Second, visibility. Every stage produces text. You can log it, redact it, test it and diff it. When Riley books the wrong day, you can see whether STT misheard "Thursday" or the LLM misread it.

Third, tool reliability. Text LLMs have had tool calling for years. Realtime models are catching up fast, but for a system that writes to a real calendar, you want the most predictable tool calls you can get.

Fourth, cost. Audio tokens are more expensive than text tokens. For long calls, cascaded is usually cheaper per minute. We'll measure the exact difference in Section 10, with your own numbers, not mine.

[SLIDE 5: Where cascaded hurts]
- Loses tone and emotion at the STT step
- Three network hops can add latency
- More moving parts to configure

To be fair, cascaded has costs too. It's flat. It can't hear sarcasm. And three hops means three chances for a slow response. The good news is that streaming hides most of that. Each stage starts working before the previous one finishes.

[SLIDE 6: Head-to-head comparison]
Table: Dimension | Cascaded | Speech-to-speech
- Control over each model | High | Low
- Voice and brand choice | Any TTS voice | Vendor voices only
- Emotion and prosody | Lost at STT | Preserved
- Latency to first word | Good with streaming | Often better
- Tool-call reliability | Mature | Improving
- Debuggability | Text at every step | Transcripts on side channel
- Cost per minute | Usually lower | Usually higher
- Best for | Transactions, compliance, scale | Natural conversation, coaching, companionship

Here's the whole comparison on one slide. Pause the video and screenshot this one.

Read it as a trade. Cascaded wins on control, debuggability and cost. Speech-to-speech wins on naturalness and emotion. Latency is closer than people think, and it depends more on your configuration than on the architecture.

[PAUSE]

Think about Riley for a second. Riley books appointments. Riley reads back phone numbers. Riley has to get a date exactly right. Does Riley need to hear emotion? A little. Does Riley need perfectly reliable tool calls? Absolutely. That's why cascaded is our default.

[SLIDE 7: The hybrid: half-cascade]
Diagram: Audio in → Realtime model (text output only) → your TTS → audio out
- Realtime model understands audio directly
- You keep your own brand voice
- Code: `modalities=["text"]` plus a separate TTS

There's a third option, and it's quietly very popular. The half-cascade. You send audio into the realtime model, so it hears tone and hesitation. But you ask it for text output only, and you speak that text with your own TTS voice.

You get better listening, and you keep your brand voice and your text logs. You'll build exactly this in Section 6.

[SLIDE 8: Where each design spends its time]
Two stacked bars.
- Cascaded: endpointing → STT final → LLM time-to-first-token → TTS time-to-first-byte
- Speech-to-speech: endpointing (server VAD) → model time-to-first-audio
- Label: "Endpointing is in both bars. Tool calls add time to both."

Let's look at latency a bit more carefully, because it's where the marketing claims live. In a cascaded pipeline, time goes to four places: deciding the caller has finished, the final transcript, the LLM's first token and the voice's first audio. In speech-to-speech, the middle steps collapse into one: time to the first audio from the model.

[B-ROLL: Slide 8's two bars animate. The middle segments of the cascaded bar merge into one "time to first audio" block, then the "Endpointing" segment pulses in both bars, and a grey "tool call" block slides into both bars at the same width.]

So speech-to-speech removes a hop or two. But look at what's in both bars. Endpointing. Deciding the caller is done is the same problem in both designs, and it's usually the biggest single slice. And when the agent calls a tool, like checking the calendar, both designs wait for it the same way. We'll put real numbers on every slice in the next lecture.

[SLIDE 9: Cost per minute, a first look (placeholder prices)]
- Cascaded, typical receptionist call: roughly 7 cents per minute
- Speech-to-speech, same call: roughly 28 cents per minute
- Source: the course's cost calculator, `src/maple/costs.py`, with placeholder list prices
- Check current pricing; you'll recompute with real usage in Section 10

[SCREEN: Terminal in the course repo. Run the cost calculator for a ten-minute call, cascaded first, then realtime. Zoom on the two "per minute" lines.]

[CODE: the course's cost calculator, `src/maple/costs.py` (you'll run it yourself in Lecture 2.7)]
```bash
uv run python -c "from maple.costs import cost_breakdown, typical_cascaded_usage, typical_realtime_usage; print(cost_breakdown(typical_cascaded_usage(10)).format()); print(cost_breakdown(typical_realtime_usage(10)).format())"
```

[DEMO: Output (excerpt: the last two lines of each report)]
```text
total          $0.6838
per minute     $0.0684  (10.00 min)
...
total          $2.7665
per minute     $0.2767  (10.00 min)
```

And cost. The course repo includes a small cost calculator. With its placeholder list prices, a typical ten-minute receptionist call costs around seven cents a minute cascaded, and around twenty-eight cents a minute speech-to-speech. That's roughly four times more.

Those are placeholder numbers, and prices move every few months. But the shape is common: audio tokens cost more than text, and a realtime model re-reads the growing conversation as audio on every turn. For a clinic taking a thousand calls a month, that difference is real money.

[SLIDE 10: How to decide]
- Transactions with strict data: cascaded
- Emotion-heavy conversation: speech-to-speech
- Want both: half-cascade
- Always: measure latency, cost and tool accuracy on your own calls

[AVATAR]
Here's my rule of thumb. If a mistake costs money or trust, like a wrong booking or a wrong dose, start cascaded. If the conversation itself is the product, like language practice or coaching, try speech-to-speech. If you're torn, try the hybrid.

And here's the most important part. Don't take anyone's word for it. Not a vendor's. Not mine. In Section 6, you'll run the same five test calls through both architectures and measure latency, cost per minute and tool accuracy yourself.

The best part? In LiveKit Agents, switching is mostly one line. The `Agent` class, the tools and the prompt stay the same. Only the model you hand to the session changes. That's a big reason we're using this framework.

[SLIDE 11: Recap]
- Cascaded: control, visibility, lower cost
- Speech-to-speech: hears tone, fewer hops
- Half-cascade: realtime ears, your own voice

**Recap:** Cascaded pipelines trade some naturalness for control, debuggability and cost, speech-to-speech trades the opposite, and the half-cascade hybrid splits the difference.

**Transition:** Both architectures live or die by one number, and in the next lecture you'll learn exactly where every millisecond of it goes.

### Speaker notes: common student mistakes / Q&A

- Mistake: assuming speech-to-speech is always faster. Endpointing and tool calls dominate latency in both designs. Measure before you migrate.
- "Can a realtime model call tools?" Yes. Riley's same `@function_tool` methods work with `openai.realtime.RealtimeModel`. Section 6 proves it.
- "Which is cheaper for my use case?" Depends on call length, talk ratio and prices that change often. Section 10's cost calculator answers it with your data.
- "Is the half-cascade officially supported?" Yes. It's a configuration of the realtime model plus a TTS on the session, not a hack.

---

## Lecture 1.4 — The latency budget: why 800 ms is the magic number

| Field | Value |
|---|---|
| ID | 1.4 |
| Type | SL (slides) |
| Target duration | 8:00 (~1,000 spoken words, about 7:09 of talking at 140 wpm) |
| Learning objectives | 1. Define voice-to-voice latency and explain why the human turn gap sets the target. 2. Break a response into five budget line items: network, endpointing, STT final, LLM time-to-first-token and TTS time-to-first-byte. 3. Build an example budget that stays under one second and identify the biggest levers. |
| Prerequisites | 1.2, 1.3 |
| Files used | `10-resources/latency-budget-worksheet.md`, `03-code/tests/evals/latency_report.py` (sample-data run), hook clip recorded from `03-code/agents/s03_hello_agent.py` with `BROKEN=long_endpointing` |

### Script

[AVATAR]
Say "hello" to a friend. They answer in about two hundred milliseconds. [PAUSE] Say "hello" to a badly built voice agent. [PAUSE] [PAUSE] Two and a half seconds later, it answers. By then, you've already said "hello?" again, and now you're both talking at once.

[DEMO: Audio clip with waveform and a running timer, recorded with `BROKEN=long_endpointing uv run python agents/s03_hello_agent.py console` (minimum endpointing delay 2.5 s; Lecture 3.9 explains the toggle). Caller: "Yes." Flat waveform while the timer counts past two seconds. Caller: "Hello?" Riley starts answering at the same moment, and the two voices collide.]

[AVATAR]
That gap is the single biggest reason voice agents feel robotic. So let's put a number on it, and then spend it wisely.

[SLIDE 1: How fast do humans take turns?]
- Typical gap between speakers: about 200 to 300 milliseconds
- Measured across many languages
- Past about one second, the silence feels awkward

Researchers who study conversation have timed this across many languages. The typical gap between one person finishing and the next person starting is around two hundred to three hundred milliseconds. That's faster than you can consciously react. We start planning our answer while the other person is still talking.

Machines can't quite hit that yet. But there's a threshold where it stops feeling broken. Somewhere around one second, silence goes from "thinking" to "is anyone there?"

[SLIDE 2: Voice-to-voice latency]
Timeline: caller stops speaking ——— [gap] ——— caller hears first audio from agent
- Measured from the end of the caller's speech
- To the first sound the caller hears
- Target: under one second, aim for about 800 ms

So here's the metric that matters. Voice-to-voice latency. The clock starts when the caller stops speaking. It stops when the caller hears the first sound of the reply. Not when the reply is finished. The first sound.

Our target is under one second. We'll aim for about eight hundred milliseconds, to leave headroom for the bad days.

[SLIDE 3: Where the time goes]
Stacked bar, left to right: Network in → Endpointing → STT final → LLM TTFT → TTS TTFB → Network out

Now let's split that second into line items. Think of it like a household budget. You have one thousand milliseconds to spend. Each stage in the pipeline takes a slice.

[SLIDE 4: Line item 1: network]
- Audio from the caller's device to your agent, and back
- WebRTC to a nearby region: tens of milliseconds each way
- Phone calls add carrier and SIP hops

Line item one is network. Audio has to travel from the caller to your agent, and the reply has to travel back. Over WebRTC to a nearby data center, that's tens of milliseconds each way. Put your agent on another continent and it's a lot more. Phone calls add carrier hops on top.

[SLIDE 5: Line item 2: endpointing]
- Deciding the caller has finished their turn
- Silence threshold plus the turn-detector model
- Usually the biggest single line item

Line item two is endpointing. This is the decision "the caller is done." Remember the phone number example? Five five five, pause, two zero one. If Riley answered after every short pause, it would talk over people constantly. So we wait a little, and we ask a turn-detection model whether the sentence sounds finished.

Here's the uncomfortable truth. That waiting is usually the biggest line item in the budget. And it's the one you have the most control over. It's a setting, not a model.

[SLIDE 6: Line item 3: STT final]
- Streaming STT has most of the words before the caller stops
- After endpointing, we wait for the final transcript
- Usually under about 100 ms with streaming

Line item three is the STT final transcript. Because STT streams, it already has most of the words while the caller is still speaking. After the turn ends, we just wait for it to confirm the last few words. With a good streaming model, that's typically under a hundred milliseconds.

[SLIDE 7: Line item 4: LLM time-to-first-token]
- TTFT: time until the model emits its first token
- Grows with prompt size and model size
- Small, fast models are your friend

Line item four is LLM time-to-first-token. People shorten this to TTFT. It's how long the model takes to produce its very first word. Not the whole answer. Just the first token.

Bigger models are slower to start. Longer prompts are slower to start. A giant system prompt with forty pages of FAQ pasted in? That costs you on every single turn. This is why Riley uses a small, fast model, and why Section 7 retrieves knowledge on demand instead of stuffing it into the prompt.

[SLIDE 8: Line item 5: TTS time-to-first-byte]
- TTFB: time until the first chunk of audio is ready
- Streaming TTS starts on the first sentence, not the whole reply
- Short first sentences start speaking sooner

Line item five is TTS time-to-first-byte, or TTFB. How long until the voice model hands back the first chunk of audio. Streaming TTS doesn't wait for the full reply. It starts speaking the first sentence while the LLM is still writing the second.

And that gives you a sneaky trick. Short first sentences. "Sure, let me check." Four words. The caller hears something almost immediately.

[SLIDE 9: An example budget under one second]
Table: Stage | Example budget
- Network in (caller → agent) | 40 ms
- Endpointing (turn detection) | 250 ms
- STT final transcript | 80 ms
- LLM time-to-first-token | 280 ms
- TTS time-to-first-byte | 110 ms
- Network out (agent → caller) | 40 ms
- **Total voice-to-voice** | **800 ms**
Footer: "Example numbers for illustration. You'll measure your own in Sections 9 and 10."

Here's a complete example budget. Let's add it up together.

Network in, forty milliseconds. Endpointing, two hundred and fifty. STT final, eighty. LLM time-to-first-token, two hundred and eighty. TTS time-to-first-byte, one hundred and ten. Network out, forty.

[PAUSE]

Forty plus two fifty is two ninety. Plus eighty is three seventy. Plus two eighty is six fifty. Plus one ten is seven sixty. Plus forty. Eight hundred milliseconds. Under one second, with two hundred to spare.

These are illustrative numbers, not a promise. Your region, your models and your prompt will change every line. But notice where the big items are. Endpointing and the LLM together are more than half the budget. That's where you tune first.

[SLIDE 10: What blows the budget]
- Tool calls: +300 to +1,500 ms (fix: filler speech, Section 5)
- Long prompts and big models: slower TTFT (fix: smaller model, retrieval)
- Cautious endpointing: +500 ms per turn (fix: tuning, Section 3)
- Far-away regions: +100 to +300 ms (fix: deploy near callers, Section 12)
- Averages hide pain: watch p95, not just p50

Now, what blows the budget? Tool calls are the big one. When Riley checks the calendar, that's an extra network call before it can answer. That could be three hundred milliseconds or a full second and a half. We can't make that disappear. But we can hide it, with a short filler like "One moment while I check the schedule." That's Section 5.

The other budget killers are long prompts, cautious endpointing and servers far from your callers.

And one more warning. Don't trust averages. If your median is seven hundred milliseconds but one call in twenty takes three seconds, that's a lot of confused callers. We'll track the ninety-fifth percentile, p ninety-five, not just the median.

[SLIDE 11: How we'll measure it]
- LiveKit emits metrics every turn: `end_of_utterance_delay`, `transcription_delay`, LLM `ttft`, TTS `ttfb`
- Section 9: fail a test if p95 exceeds the budget
- Section 10: dashboards and alerts

[SCREEN: Terminal in the course repo. Run the latency report on the sample call metrics that ship with the repo, with the voice-to-voice budget set to our 800 ms target. Zoom on the `voice_to_voice` row and the FAIL line.]

```bash
uv run python tests/evals/latency_report.py --voice-to-voice 800
```

[DEMO: Output]
```text
Files: sample_metrics.jsonl  (62 records)
Budget checked at p95 (milliseconds)

stage               n      p50      p90      p95   budget  status
-----------------------------------------------------------------
eou_delay          14      560      617      634      700  OK
stt_final          14      225      257      267      500  OK
llm_ttft           15      470      598      661      700  OK
tts_ttfb           14      170      217      227      300  OK
voice_to_voice     14     1215     1434     1474      800  OVER

FAIL voice_to_voice: p95=1474 ms exceeds budget 800 ms by 674 ms
```

Here's a preview of where this goes. This report reads per-turn metrics from a set of sample calls in the repo and checks each line item against a budget. Every stage on its own looks fine. But voice to voice, at the ninety-fifth percentile, is fourteen hundred and seventy-four milliseconds. Six hundred and seventy-four over our target. So what does the command do? It fails, on purpose. That's the check you'll put in your build in Section nine.

[AVATAR]
Here's the good news. You won't need a stopwatch. LiveKit Agents reports these numbers on every turn: end-of-utterance delay, transcription delay, LLM time-to-first-token and TTS time-to-first-byte. In Section 9, you'll write a test that fails the build if p ninety-five goes over budget. In Section 10, you'll put it on a dashboard.

Grab the latency budget worksheet in the resources folder. Fill in the example column now. You'll fill in your real numbers later, and it's very satisfying to compare.

[SLIDE 12: Recap]
- Clock runs from caller silence to first sound
- Five line items; endpointing is usually biggest
- Aim for about 800 ms, and watch p95

**Recap:** Voice-to-voice latency is the sum of network, endpointing, STT final, LLM time-to-first-token and TTS time-to-first-byte, and a budget of around eight hundred milliseconds keeps conversations feeling natural.

**Transition:** You now know what you're building and the number it has to hit, so next let's tour the roadmap and the code repository you'll build it in.

### Speaker notes: common student mistakes / Q&A

- Mistake: measuring latency from when the agent *starts thinking* instead of from when the caller *stops speaking*. That hides endpointing, the biggest line item.
- Mistake: comparing your console-mode latency on laptop speakers with a phone call. Phone calls add carrier hops. Always compare like with like.
- "Why not make endpointing zero?" Riley would interrupt every pause mid-sentence. Lecture 3.6 shows the trade-off and the dynamic endpointing option.
- "Does preemptive generation break the budget math?" It overlaps the LLM with endpointing, so real totals can be lower than the sum. The line items still tell you where to look.

---

## Lecture 1.5 — Course roadmap, repo tour and how to get help

| Field | Value |
|---|---|
| ID | 1.5 |
| Type | SC (screencast) |
| Target duration | 6:00 (~775 spoken words, about 5:32 of talking at 140 wpm, plus screen dwell; reduced from 7:00 in the 2026-10 review) |
| Learning objectives | 1. Describe the course path from first agent to production deployment. 2. Navigate the `voice-agents-course` repo: `src/maple`, `agents`, `tests`, `deploy`. 3. Ask a question in Q&A that gets a fast, useful answer. |
| Prerequisites | None |
| Files used | `03-code/README.md`, `03-code/Makefile` (`make help`, `make test`), `03-code/src/maple/`, `03-code/agents/`, `03-code/tests/` |

### Script

[AVATAR]
Fifteen sections, one agent. Every section adds one capability to Riley, and every capability gets tested. Let me show you the path, then the code, then how to get unstuck fast.

[SLIDE 1: The roadmap: Build]
- S1 Welcome and how voice agents work
- S2 Setup: accounts, keys, dev environment
- S3 Your first voice agent
- S4 Prompting for the ear
- S5 Tools: booking, rescheduling, cancelling
- S6 Speech-to-speech with OpenAI Realtime
- S7 Knowledge and multi-agent handoffs
- S8 Telephony: a real phone number

The course has three phases. Build, test and operate.

The build phase is Sections one to eight. You'll set up your environment, get Riley talking in about thirty lines, teach it to speak like a receptionist instead of a chatbot, give it tools to book appointments, try the speech-to-speech version, add a knowledge base and specialist agents, and put it on a phone number.

[SLIDE 2: The roadmap: Test and Operate]
- S9 Testing and evaluating voice agents (signature section)
- S10 Observability, latency and cost
- S11 Security, safety and guardrails
- S12 Deploying to production
- S13 Capstone: Riley, production receptionist
- S14 Pipecat and choosing your stack
- S15 Wrap-up and next steps

Then the part most courses skip. Section nine is the heart of this course: behavior tests, tool-call assertions, LLM judges, word error rate, latency budgets and simulated callers. Section ten measures latency and cost. Section eleven defends Riley against prompt injection and social engineering. Section twelve deploys it.

Section thirteen is the capstone, where everything comes together. Section fourteen rebuilds Riley in Pipecat, so you can compare frameworks with real code. And Section fifteen points you to what's next.

[SCREEN: Browser on the course GitHub repo `voice-agents-course`, then switch to VS Code with the repo open. Font size 18, dark theme, file explorer on the left.]

Now let's look at the code. This is the repo you'll work in for the whole course. You'll clone it in the next section. For now, just get oriented.

[SCREEN: Expand `src/maple/` in the explorer. Hover over each file.]

The first folder is `src/maple`. This is plain Python business logic. No network calls, no API keys. The scheduler that holds the clinic calendar. The prompts. The FAQ retriever. PII redaction. The cost and latency math. Word error rate.

Why keep this separate from the agent? Because you can test it in milliseconds, for free, offline. When something is pure logic, it belongs here. You'll see this pattern pay off in Section five.

[SCREEN: Open `src/maple/config.py` briefly. Highlight the environment variable names.]

One file to know now: `config.py`. Every model name comes from an environment variable with a sensible default. Speech-to-text model, LLM, voice. When a provider renames a model, and they will, you change one line in your `.env` file. Not your code.

[SCREEN: Expand `agents/`.]

Next, the `agents` folder. One file per section, numbered by section. `s03_hello_agent.py` is your first agent. `s05_booking_agent.py` adds tools. `s08_telephony_agent.py` goes on the phone. `s13_capstone_receptionist.py` is the finished Riley you heard in lecture one.

Each file is runnable on its own. If you fall behind, or something breaks, you can always open the file for the section you're on and compare.

[SCREEN: Expand `tests/`: `unit/`, `agent/`, `evals/`, `data/`.]

Then `tests`. Three layers. `unit` runs offline with no keys, and it should always be green. `agent` holds behavior tests that talk to a real LLM, so they skip automatically if you don't have an OpenAI key. And `evals` holds the heavier evaluations: conversation quality, word error rate, latency reports and simulated callers.

[SCREEN: Terminal in the repo folder. Run `make test`. Let the dots scroll, then zoom on the final "passed" line and its time.]

Want proof that the first layer is free? Watch. Make test runs every unit test, a couple of hundred of them, in about a second, with no keys and no network. You'll see that green line more than anything else in this course.

[SCREEN: Show `deploy/`, `pipecat/`, `frontend/README.md`, `.github/workflows/ci.yml`.]

The rest you'll meet later. `deploy` has the Dockerfile. `pipecat` has the comparison build. `frontend` explains how to put a web page in front of Riley. And the CI workflow runs your tests on every push.

[SCREEN: Terminal. Run `make help`, then open `Makefile` beside it.]

[CODE: `make help` output (excerpt: seven of the twenty targets)]
```text
  install          Install the project with dev tools (uv sync --extra dev)
  console          Talk to an agent locally: make console AGENT=agents/s13_capstone_receptionist.py
  dev              Dev mode with hot reload; connect from the Agents Playground
  test             Offline unit tests (no keys needed)
  test-agent       LiveKit behavior tests (live ones need OPENAI_API_KEY)
  eval             DeepEval judge + WER + latency reports
  lint             Ruff lint + format check
```

Last stop, the Makefile. `make help` lists every shortcut with a one-line description. These seven are the ones to know first, and `make install`, `make test`, `make console` and `make dev` are the ones you'll use every day. Under the hood they're ordinary `uv run` commands, and I'll always show you the full command the first time.

[SCREEN: Open `README.md`, scroll to the "Lecture → file map" table.]

And if you ever wonder "which file goes with this lecture?", the README has a lecture-to-file map.

[AVATAR]
Now, how to get help. Voice agents have a lot of moving parts, so you will get stuck at some point. That's normal. Here's how to get unstuck fast.

[SLIDE 3: How to ask a question that gets answered]
- Lecture number, for example "3.3"
- The exact command you ran
- The full error text, not a screenshot of half of it
- Your OS, Python version and `livekit-agents` version (`uv pip show livekit-agents`)
- What you already tried

When you post in Q&A, include five things. The lecture number. The exact command. The full error text. Your operating system, Python version and livekit-agents version. And what you already tried. A question like that usually gets answered in one reply instead of five.

And please, never paste your API keys. If you see a key in a screenshot, rotate it.

[SLIDE 4: How to use labs, projects and quizzes]
- Labs: short, guided, checklist style. Do them right after the lecture.
- Projects: open-ended. Build, record a demo, share it.
- Quizzes: check understanding before moving on.

Finally, the practice. Labs are short and guided, and they come right after the lectures they practice. Projects are bigger and open-ended. Quizzes check the ideas before you build on them. Do the labs. The students who finish this course are the ones who ran the code, not just watched it.

[SLIDE 5: Recap]
- Fifteen sections: build, test, operate
- Repo layers: `src/maple`, `agents`, `tests`
- Good questions: lecture, command, full error, versions

**Recap:** The course moves from build to test to operate, the repo mirrors that with `src/maple`, `agents` and `tests`, and a precise Q&A question gets you unstuck fastest.

[SLIDE 6: You can now]
- Name the seven parts of a voice pipeline
- Choose cascaded, speech-to-speech or half-cascade
- Read a latency budget and find the biggest lever

**Transition:** Before we set anything up, a quick quiz to lock in how voice agents work.

### Speaker notes: common student mistakes / Q&A

- Mistake: editing the section files directly and losing the reference version. Suggest students work on a branch or copy the file, for example `agents/my_riley.py`.
- Mistake: putting business logic inside tool methods. Point them to `src/maple/scheduler.py` as the pattern.
- "Do I need to know async Python?" Basic `async` and `await` is enough. Every async pattern is explained the first time it appears.
- "Windows?" Supported. Use PowerShell or WSL2. Console mode needs microphone permission for the terminal app.

---

## Lecture 1.6 — Quiz: Voice agent fundamentals

| Field | Value |
|---|---|
| ID | 1.6 |
| Type | QZ (quiz with short video intro) |
| Target duration | 4:00 total (1:30 video intro, ~175 spoken words, about 1:15 of talking at 140 wpm; the rest is quiz time) |
| Learning objectives | 1. Check understanding of pipeline components, architectures and the latency budget. 2. Identify any Section 1 lecture to rewatch before building. |
| Prerequisites | 1.1 to 1.5 |
| Files used | `06-assessments/quizzes/section-01.md` |

### Script

[AVATAR]
One idea trips up more students in this section than any other: VAD and turn detection sound like the same thing, and they aren't. [PAUSE] Let's see if it trips you. Eight questions, about four minutes.

[SLIDE 1: Section 1 quiz: what's covered]
- The seven components of a voice pipeline
- VAD vs turn detection
- Cascaded vs speech-to-speech vs half-cascade
- The five latency line items and the 800 ms target

You'll see questions on the seven pipeline components, the difference between VAD and turn detection, the three architectures, and the latency budget.

Here's a tip for the latency questions. When a question asks where to tune first, think about which line items were biggest in our example budget. Endpointing and the LLM.

Every question has an explanation. If you miss one, read the explanation before you move on, and rewatch the lecture it points to. Section 3 builds directly on these ideas, especially turn detection.

[PAUSE]

No pressure. Nobody sees your score. It's there to help you, not to grade you.

**Recap:** The quiz checks the pipeline, the architectures and the latency budget before you start building.

**Transition:** Next up, Section 2: you'll create your accounts, get your keys and set up your development environment.

### Speaker notes: common student mistakes / Q&A

- Most missed question in beta: confusing VAD with turn detection. Point students back to Lecture 1.2, slides 5 and 7.
- Second most missed: thinking latency is measured until the reply *finishes*. It's to the *first* audio the caller hears.
- "Can I retake it?" Yes, as many times as you like.
