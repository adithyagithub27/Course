# Section 6: Speech-to-Speech with OpenAI Realtime

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** about 42 minutes (6 lectures)
> **Running example:** Riley, the AI receptionist for Maple Street Dental
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

**Cue legend**

| Cue | Meaning |
|---|---|
| [AVATAR] | HeyGen avatar on camera. Keep each block under about 60 seconds of speech. |
| [SLIDE n: title] | Full-screen slide. Bullets listed underneath are the slide text. |
| [SCREEN: ...] | OBS screen recording of the editor, terminal or browser. |
| [CODE: ...] | Code shown or typed on screen. The fenced block is the exact code. |
| [DEMO: ...] | Live run with audio. Capture both mic and agent audio. |
| [B-ROLL] | Cutaway footage or animation. |
| [PAUSE] | One-beat pause (about 1 second) for emphasis or for the viewer to read. |

**Code names used in this section (matched to `03-code/`):** `RealtimeRiley` and `build_realtime_model` in `agents/s06_realtime_agent.py`; `RileyBookingAgent` in `agents/s05_booking_agent.py`; `BookingToolsMixin`, `CallState`, `create_session`, `build_tts` in `agents/common.py`; tools `find_available_slots`, `book_appointment`, `reschedule_appointment`, `cancel_appointment`; settings `realtime_model`, `realtime_voice` from `maple.config.load_settings()`; env `REALTIME_HYBRID=1` for the hybrid. On screen, every one of these agents is "Riley".

---

## Lecture 6.1: How realtime speech models work

| Field | Value |
|---|---|
| ID | 6.1 |
| Title | How realtime speech models work |
| Type | SL (slides + avatar) |
| Target duration | 8:00 (about 990 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | A speech-to-speech model hears audio and speaks audio in one model, which removes two hops but changes what you can control. |
| Prerequisites | Lecture 1.3 (cascaded vs speech-to-speech), Section 5 (Riley's booking tools) |
| Files used | None (conceptual). Diagram: `09-production` slide deck, "realtime pipeline". |

**Learning objectives**

1. Explain how a realtime speech model processes audio in, audio out, and where the transcript comes from.
2. Describe server-side turn detection (server VAD and semantic VAD) and how it differs from Riley's cascaded turn handling.
3. Name the session limits and control trade-offs that matter before you put a realtime model on a phone line.

### Script

[AVATAR]

For five sections, Riley has been a relay race. Your voice goes to a speech-to-text model. The text goes to a language model. The reply goes to a text-to-speech model. Three runners, three handoffs. [PAUSE] Today we fire two of those runners. We're going to let one model hear the caller and answer out loud, directly. That's what a realtime, speech-to-speech model does. And it changes more than latency.

[SLIDE 1: Two ways to build Riley]
- Cascaded: audio → STT → text → LLM → text → TTS → audio
- Speech-to-speech: audio → realtime model → audio
- Same tools, same prompt, different plumbing

[AVATAR]

Here's the picture. On the top, the cascaded pipeline you've been building. Three models, each one replaceable. On the bottom, the realtime pipeline. One model. Audio goes in. Audio comes out. [PAUSE] The good news is that almost nothing else changes. Riley keeps her instructions. Riley keeps her four booking tools. Riley keeps her `CallState` userdata. LiveKit's `AgentSession` hides the difference behind one parameter. You'll see that in the next lecture. Right now, let's understand what's happening inside the box.

[SLIDE 2: What "audio in, audio out" really means]
- Caller audio is streamed to the model as audio tokens, roughly every 20 to 100 milliseconds
- The model reasons over audio directly: tone, hesitation, emphasis
- It generates audio tokens back, streamed as it speaks
- Text is optional output, not an intermediate step

[AVATAR]

A realtime model doesn't convert your words to text first. It turns the audio into tokens, the same way a text model turns words into tokens. Then it reasons over those audio tokens. [PAUSE] That's why it can hear things a transcript throws away. A rising tone on "Tuesday?" A sigh before "I guess that works." A caller who sounds rushed. The reply is generated as audio tokens and streamed back to the caller while the model is still thinking about the rest of the sentence.

This is where the speed comes from. There's no waiting for a final transcript. There's no waiting for the first sentence of text before speech synthesis can start. In my own tests, a realtime Riley usually starts speaking somewhere between half a second and eight hundred milliseconds after the caller stops. A well-tuned cascaded Riley lands closer to eight hundred milliseconds to one point two seconds. We'll measure both properly in lecture 6.4, so don't take my word for it yet.

[SLIDE 3: Where the transcript comes from]
- The model does NOT need a transcript to answer
- A separate transcription model runs on the side channel
- LiveKit default: `gpt-4o-mini-transcribe`
- The transcript is for you: logs, tests, UI captions, compliance

[AVATAR]

Here's the part that surprises people. If the model reasons over audio, where does the transcript in your logs come from? [PAUSE] From a second model. The realtime API runs a transcription model on the side, in parallel. In LiveKit Agents 1.8 the default is `gpt-4o-mini-transcribe`. That side-channel transcript powers your captions, your logs, and every test in Section 9.

And that creates a subtle trap. The transcript and the model's understanding can disagree. The caller says "Dr. Okafor." The transcript says "Dr. O'Connor." But the model heard the audio and answered correctly. Or the reverse. When you debug a realtime agent, remember that the transcript is a witness, not the source of truth.

[SLIDE 4: Server-side turn detection]
- Server VAD: silence threshold, for example 500 ms of quiet ends the turn
- Semantic VAD: a classifier judges whether the caller sounds finished
- Eagerness: low, medium, high, auto (LiveKit default: medium; our code: auto)
- The model decides when to reply, and whether a barge-in cancels its answer

[AVATAR]

Next, turn-taking. In Section 3, Riley used Silero VAD plus LiveKit's turn detector model to decide when you'd finished talking. With a realtime model, the provider does that on their server. There are two flavors.

Server VAD is the simple one. It waits for a fixed stretch of silence, say five hundred milliseconds, and then declares the turn over. It's fast, but it cuts off people who pause to think.

Semantic VAD is smarter. A classifier listens to the words and the intonation and asks: does this person sound finished? "My phone number is five five five..." [PAUSE] Not finished. Semantic VAD waits. You tune it with one knob called eagerness. Low waits longer. High jumps in sooner. LiveKit's default for OpenAI is semantic VAD at medium eagerness. In our code we'll set it to auto, which lets the model adapt, and I'll show you when to switch to low: a dental clinic, where callers read out phone numbers and insurance IDs, is exactly that case.

[B-ROLL: animated waveform of a caller saying "my number is five five five... uh... two one two..." with a server-VAD cutoff marker firing too early, and a semantic-VAD marker waiting until the end]

[SLIDE 5: Voices]
- Voices are baked into the model, chosen per session
- `marin` and `cedar` are the newest, most natural options
- You get the provider's voice, not your brand's cloned voice
- Voice can't change mid-session once the model has spoken

[AVATAR]

Now voices. In a cascaded pipeline, the voice belongs to your TTS provider. You can pick from hundreds of voices or clone your own. In a realtime model, the voice belongs to the model. OpenAI ships a small set. We'll use `marin`, which is one of the two newest and most natural. [PAUSE] That's a real trade-off for a business. If Maple Street Dental already has a brand voice on their phone menu, a realtime model can't match it. Lecture 6.3 shows the hybrid fix for exactly that.

[SLIDE 6: Session limits you must design for]
- Max session length: OpenAI caps a realtime session (60 minutes at time of recording)
- LiveKit recycles the connection by default every 20 minutes (`max_session_duration`)
- Context grows every turn: long calls cost more per minute
- Audio tokens are priced far higher than text tokens

[AVATAR]

Limits. A realtime connection is a long-lived session with the provider. OpenAI caps how long it can live. When I recorded this, the cap was sixty minutes. LiveKit's plugin quietly recycles the connection every twenty minutes by default, and carries the chat history across. You'll almost never hit this on a receptionist call. But you will hit it if a caller is put on hold and forgets to hang up.

The bigger limit is money. Every turn, the whole conversation so far is fed back into the model. On a realtime model that history includes audio tokens. Audio tokens cost many times more than text tokens. So a ten-minute call doesn't cost ten times a one-minute call. It costs more. We'll put real numbers on this in lecture 10.4.

[SLIDE 7: What you trade for speed]
- Less control: no text step to filter, rewrite or pronounce-fix before speech
- Tool calling works, but is harder to observe and test
- Harder to swap one piece: model, voice and ears come as a bundle
- Test framework runs in text mode either way (Section 9)

[AVATAR]

So what do you give up? Control. In the cascaded pipeline, there's a moment where Riley's reply exists as plain text. You can check it for a phone number that shouldn't be there. You can rewrite "Dr." to "Doctor". You can add pronunciation hints. With pure speech-to-speech, that moment doesn't exist. The words go straight to audio.

You also give up modularity. If a better speech-to-text model comes out tomorrow, a cascaded Riley swaps one string. A realtime Riley waits for the provider.

The good news for this course is testing. LiveKit's test framework drives the agent with text either way. So the behavior tests you write in Section 9 cover both architectures.

[SLIDE 8: When realtime wins, when cascaded wins]
- Realtime: lowest latency, natural prosody, emotional or casual conversations
- Cascaded: strict wording, compliance review, brand voice, lowest cost per minute
- Hybrid: realtime brain, your TTS voice (lecture 6.3)
- Decide with data, not vibes (lecture 6.4)

[AVATAR]

Here's my rule of thumb. If the conversation is casual and speed is everything, realtime wins. If every word has to be controlled, like a clinic reading back appointment times and cancellation policies, cascaded usually wins. And there's a middle path that we'll build in lecture 6.3. [PAUSE] But rules of thumb are just opinions. By the end of this section you'll have your own latency and cost numbers for both versions of Riley.

### Recap

A realtime model hears audio and speaks audio in one hop, with a side-channel transcript and server-side turn detection, and you trade some control and cost for that speed.

### Transition

In the next lecture, we'll put Riley on `gpt-realtime` with one changed line, and find out which of her Section 5 habits break.

### Speaker notes: common mistakes and Q&A

- **"The transcript is wrong, so the model misheard."** Not necessarily. The transcript comes from a separate transcription model. Check the audio recording before blaming the realtime model.
- **"Can I use my ElevenLabs or Cartesia cloned voice with pure realtime?"** No. Built-in voices only. Use the hybrid setup in 6.3 with `modalities=["text"]` plus your own TTS.
- **"Is semantic VAD always better?"** It's better for callers who pause mid-sentence. Server VAD can feel snappier for short yes/no exchanges. Tune per use case and measure in 6.4.
- **Session cap numbers change.** Tell students to confirm the current provider session limit in OpenAI's docs; the 20-minute recycle is LiveKit's `max_session_duration` default in 1.8.

---

## Lecture 6.2: Code-along: Riley on `gpt-realtime`

| Field | Value |
|---|---|
| ID | 6.2 |
| Title | Code-along: Riley on `gpt-realtime` |
| Type | SC (screencast code-along) |
| Target duration | 10:00 (about 920 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Swapping Riley to speech-to-speech is one changed argument on `AgentSession`, plus one habit change: without a TTS, Riley can't `say()` fixed text. |
| Prerequisites | 6.1; Section 5 booking tools working; `OPENAI_API_KEY` in `.env` |
| Files used | `agents/s06_realtime_agent.py`, `agents/common.py` (`BookingToolsMixin`, `CallState`, `create_session`), `src/maple/config.py` |

**Learning objectives**

1. Configure `AgentSession(llm=openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin"))` and reuse Riley's four booking tools unchanged.
2. Tune server-side turn detection with semantic VAD and its eagerness setting.
3. Explain why `session.say(...)` and string filler speech need a TTS, and what to do instead in pure realtime mode.

### Script

[AVATAR]

Riley's brain is about to change. Her tools won't. By the end of this lecture, the same four booking tools from Section 5 will be driven by a speech-to-speech model, and you'll hear the difference. Let's open the editor.

[SCREEN: VS Code, repo root, `agents/` open. Lower third: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."]

The file for this lecture is `agents/s06_realtime_agent.py`. It reuses `BookingToolsMixin` and `CallState` from `agents/common.py`, the same building blocks as the Section 5 agent, so we don't copy a single tool.

First, config. Open `src/maple/config.py`. Every model name already comes from an environment variable, through one function, `load_settings`. Scroll to the realtime fields.

[CODE: `src/maple/config.py` (excerpt, highlight)]

```python
DEFAULT_REALTIME_MODEL = "gpt-realtime"
DEFAULT_REALTIME_VOICE = "marin"

@dataclass(frozen=True)
class Settings:
    ...
    realtime_model: str = DEFAULT_REALTIME_MODEL   # env: REALTIME_MODEL
    realtime_voice: str = DEFAULT_REALTIME_VOICE   # env: REALTIME_VOICE
```

Why environment variables again? Because realtime model names change more often than any other model name in this stack. When OpenAI ships the next one, you change `.env`, not your code.

Now the agent file. Imports first.

[CODE: `agents/s06_realtime_agent.py`, step 1: imports]

```python
import logging
import os

from common import (
    BookingToolsMixin,
    CallState,
    build_tts,
    create_session,
    get_scheduler,
    get_settings,
)
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import openai
from openai.types import realtime

from maple import prompts
from maple.config import Settings
from maple.scheduler import ClinicScheduler

logger = logging.getLogger("s06")
```

Notice what's missing. No Silero, no turn detector, no Deepgram, no Cartesia. The realtime model brings its own ears, its own turn detection and its own voice. We import `openai.types.realtime` only for the turn-detection settings.

[CODE: step 2: the agent]

```python
class RealtimeRiley(BookingToolsMixin, Agent):
    """Same tools and prompt as the cascaded booking agent; different model."""

    def __init__(self, *, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(today=self.scheduler.today, booking=True),
        )

    async def on_enter(self) -> None:
        """Realtime models generate the greeting themselves (there is no separate TTS)."""
        self.session.generate_reply(
            instructions=f"Greet the caller with exactly this sentence: {prompts.GREETING}"
        )
```

`RealtimeRiley` mixes in `BookingToolsMixin`, so she has `find_available_slots`, `book_appointment`, `reschedule_appointment` and `cancel_appointment`, exactly as in Section 5. Same instructions, built by `build_instructions` with the booking rules. Same scheduler.

One line is different, and it's the most important thing in this lecture. [PAUSE] In Section 5, Riley greeted with `session.say(prompts.GREETING)`. `say` speaks fixed text through the text-to-speech model. A pure realtime session has no text-to-speech model. OpenAI's realtime model can't read out arbitrary text you hand it. So calling `say` here raises an error: "trying to generate speech from text without a TTS model." Instead, we use `generate_reply` with instructions: "Greet the caller with exactly this sentence." The model speaks it in its own voice.

[SLIDE 1: `say()` needs a TTS]
- `session.say(text)` → spoken by the TTS → needs `tts=` on the session
- Pure realtime: no TTS → `RuntimeError: trying to generate speech from text without a TTS model...`
- Use `session.generate_reply(instructions="Say ...")` instead
- Same for string filler speech (`context.with_filler("One moment...")`)

[AVATAR]

The same rule applies to filler speech from lecture 5.5. When you pass `with_filler` a string, LiveKit speaks it with `say`. Our demo scheduler answers instantly, so the filler never fires and you won't see a problem today. But connect a slow, real booking system to a pure realtime Riley and the filler will fail the moment it tries to speak. You have two fixes: use the hybrid setup from the next lecture, which has a TTS again, or pass `with_filler` a function that calls `generate_reply`. There's a snippet in the lecture notes.

[CODE: step 3: the realtime model]

```python
def build_realtime_model(settings: Settings, *, hybrid: bool) -> openai.realtime.RealtimeModel:
    """Create the OpenAI Realtime model.

    ``hybrid=True`` asks the model for text only so a separate TTS voices it,
    which keeps Riley's brand voice identical across architectures (lecture 6.3).
    """
    return openai.realtime.RealtimeModel(
        model=settings.realtime_model,          # "gpt-realtime"
        voice=settings.realtime_voice,          # "marin"
        modalities=["text"] if hybrid else ["audio"],
        turn_detection=realtime.realtime_audio_input_turn_detection.SemanticVad(
            type="semantic_vad",
            eagerness="auto",
            create_response=True,
            interrupt_response=True,
        ),
    )
```

Model: `gpt-realtime`. Voice: `marin`. Ignore `modalities` and `hybrid` for now; that's next lecture. For pure speech-to-speech, the model returns audio.

Then turn detection. We use semantic VAD, from lecture 6.1. `create_response=True` means the model answers automatically when it decides the caller is done. `interrupt_response=True` means a caller can barge in and cut Riley off. And `eagerness`. We use `auto`, which lets the model adapt. If your callers read out phone numbers and insurance IDs and get cut off, try `low`, which waits longer. If Riley feels sluggish on short yes-and-no answers, try `high`.

We don't set the transcription model. LiveKit's default side-channel transcript is `gpt-4o-mini-transcribe`, which is fine here. You can override it with `input_audio_transcription` if clinic-specific words keep coming out wrong in your logs.

[CODE: step 4: the entrypoint]

```python
server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start the realtime (or hybrid) agent."""
    settings = get_settings()
    hybrid = os.getenv("REALTIME_HYBRID", "0") == "1"

    if settings.mock_mode:
        session = create_session(settings, userdata=CallState())
    else:
        extra = {"tts": build_tts(settings)} if hybrid else {}
        session = AgentSession(
            llm=build_realtime_model(settings, hybrid=hybrid),
            userdata=CallState(),
            max_tool_steps=5,
            **extra,
        )
    logger.info("starting realtime Riley (hybrid=%s)", hybrid)
    await session.start(agent=RealtimeRiley(), room=ctx.room)
```

Here's the whole switch. In Section 5, `AgentSession` took `stt`, `llm`, `tts`, `vad` and `turn_handling`. Here it takes one `llm`, and that `llm` happens to be a realtime model. LiveKit sees that and uses the model's server-side turn detection automatically. Riley's userdata, `CallState`, and `max_tool_steps=5` are the same as before.

Two branches you can ignore for now. `MOCK_MODE` swaps in the scripted fake LLM from Section 2 for zero-cost practice. And `REALTIME_HYBRID` is next lecture.

Let's run it.

[SCREEN: terminal]

```bash
uv run agents/s06_realtime_agent.py console
```

[DEMO: console mode. Riley greets in the `marin` voice. Speak: "Hi, I'd like to book a cleaning next Tuesday morning." Riley answers quickly and calls `find_available_slots`; the terminal log shows the function call and its arguments.]

Listen to how fast that first reply lands. [PAUSE] And look at the log. There's the `find_available_slots` call, with the day and part of day the model chose. Same tool. Different brain.

[DEMO: pick a time, give name and number "Alex Kim, 512 555 0188". Riley reads back and asks for confirmation. Say "yes". `book_appointment` fires with name, phone, slot_start and reason.]

The booking goes through. And listen to the read-back. Riley still confirms the name, day and time before calling `book_appointment`, because that rule lives in her instructions, and instructions travel with the agent.

One more check. Interrupt her.

[DEMO: while Riley reads back, say "No, Thursday." Riley stops mid-sentence and re-checks Thursday.]

The barge-in worked, because of `interrupt_response=True`. OpenAI's server heard me, cancelled the reply, and handled "No, Thursday" as a new turn.

[SCREEN: terminal log from the booking demo, scrolled back to the start of the call.]

Before we move on, let's read the log together, because realtime sessions log differently from cascaded ones. At the top, the realtime session connects to OpenAI. There's no "STT connected" line and no "TTS connected" line, because there's no separate STT or TTS. Then each of your turns shows up twice: once as the side-channel transcript of what you said, and once as the model's response. [PAUSE] Notice the transcript line sometimes arrives after Riley has already started speaking. That's normal. The model answered from the audio, and the transcription model finished a moment later. It's lecture 6.1's "the transcript is a witness" in action.

Look at the tool call too. The arguments are JSON, exactly like the cascaded version: a `day` and a `part_of_day`. The model chose "2026-10-06" for next Tuesday, because Riley's instructions include today's date through `build_instructions`. If you ever see a realtime Riley book the wrong week, check that line of the prompt first.

And one habit to keep from Section 5: run the booking twice. Realtime models vary more between runs in how they phrase things, and sometimes in which details they collect first. The tools and the scheduler keep the outcome correct either way. That's the architecture doing its job.

[AVATAR]

Let's review. Changed: one argument on `AgentSession`, and the greeting now uses `generate_reply` instead of `say`. Unchanged: the tools, the prompt, the userdata, and the scheduler logic in `src/maple/scheduler.py`. That's the payoff of keeping business logic out of the agent. You swapped the entire speech stack without touching the code that books appointments.

### Recap

`RealtimeRiley` runs on `gpt-realtime` with the `marin` voice and semantic VAD, reuses every Section 5 booking tool, and greets with `generate_reply` because a pure realtime session has no TTS for `say()`.

### Transition

Next, we'll keep the realtime brain but give Riley back a voice you choose, with the hybrid setup.

### Speaker notes: common mistakes and Q&A

- **`RuntimeError ... without a TTS model`**: `session.say(...)` or a string filler in pure realtime mode. Use `generate_reply(instructions=...)`, the hybrid mode (6.3), or a callable filler:
  ```python
  async with context.with_filler(
      lambda step: context.session.generate_reply(instructions="Say briefly that you're checking the schedule."),
      delay=0.8,
  ):
      ...
  ```
- **Mixing turn systems**: don't add `vad=` and `turn_handling=TurnHandlingOptions(turn_detection=inference.TurnDetector())` next to a realtime model with default settings; the model's server-side detection is already in charge.
- **"Riley sounds different from Section 5."** Expected: the voice now comes from `marin`, not Cartesia. That's what 6.3 fixes.
- **Makefile shortcut**: `make console AGENT=agents/s06_realtime_agent.py` runs the same thing.

---

## Lecture 6.3: Hybrid: realtime LLM with your own TTS

| Field | Value |
|---|---|
| ID | 6.3 |
| Title | Hybrid: realtime LLM with your own TTS |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 620 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Run the realtime model with text output and your own TTS to get audio understanding plus brand voice and text-level control. |
| Prerequisites | 6.2 |
| Files used | `agents/s06_realtime_agent.py` (`REALTIME_HYBRID`), `agents/common.py` (`build_tts`) |

**Learning objectives**

1. Configure `RealtimeModel(modalities=["text"])` with a separate `tts=` on `AgentSession`.
2. Explain what the hybrid gains (brand voice, text transforms, `session.say`) and what it costs (a TTS hop of latency).
3. Switch between realtime and hybrid with the `REALTIME_HYBRID` environment variable for side-by-side testing.

### Script

[AVATAR]

Maple Street Dental called. They love how fast Riley is. They don't love that she doesn't sound like the voice on their website. [PAUSE] This is the most common complaint I hear about speech-to-speech agents in business settings. The fix is called a half-cascade, or hybrid. The realtime model still listens to raw audio. But instead of speaking, it writes text. And your own TTS speaks that text.

[SLIDE 1: The hybrid pipeline]
- Caller audio → realtime model (hears tone, pauses; semantic VAD)
- Realtime model → text reply (`modalities=["text"]`)
- Text → your TTS (`cartesia/sonic-3` with Riley's voice) → caller
- Adds one TTS hop, typically 100 to 250 ms to first audio

[AVATAR]

Here's the shape. The input side is identical to lecture 6.2. Audio goes straight into `gpt-realtime`, so you keep semantic turn detection and the model still hears hesitation and tone. The output side changes. The model returns text, and Cartesia speaks it in Riley's Section 3 voice.

You pay for that with one extra hop. A good streaming TTS adds roughly a hundred to two hundred and fifty milliseconds before the first sound. You'll measure the real number in 6.4.

[SLIDE 2: What you get back]
- Brand voice or cloned voice
- `session.say(...)` and string fillers work again
- Text transforms and pronunciation fixes from Section 4
- A text checkpoint for guardrails (Section 11)

[AVATAR]

And here's what you get back. Your brand voice. `session.say` and plain string fillers work again, because there's a TTS. The pronunciation fixes from Section 4 apply again, because there's text to transform. And in Section 11, when we add output guardrails, there's a text checkpoint where you can catch a reply before anybody hears it.

[SCREEN: `agents/s06_realtime_agent.py`, highlight the `modalities` line and the `hybrid` branch in the entrypoint.]

The code is already in the file from last lecture. Two lines make the hybrid.

[CODE: the two hybrid lines]

```python
        modalities=["text"] if hybrid else ["audio"],
```

```python
        extra = {"tts": build_tts(settings)} if hybrid else {}
        session = AgentSession(
            llm=build_realtime_model(settings, hybrid=hybrid),
            userdata=CallState(),
            max_tool_steps=5,
            **extra,
        )
```

First, `modalities`. For pure speech-to-speech it's `["audio"]`: the model returns audio. For the hybrid it's `["text"]`: the model returns only text.

Second, the session. In hybrid mode we add `tts=build_tts(settings)`, the same helper every cascaded agent uses. It returns `cartesia/sonic-3` with Riley's voice ID, through LiveKit Inference. No STT. No VAD. The realtime model still does the listening and the turn detection. LiveKit sees a text-only realtime model plus a TTS, and routes the text into the TTS for you.

`REALTIME_HYBRID=1` switches it on. Run both. First, hybrid.

[SCREEN: terminal]

```bash
REALTIME_HYBRID=1 uv run agents/s06_realtime_agent.py console
```

[DEMO: say "Hi, do you have anything Thursday afternoon for a filling?" Riley answers in the Cartesia voice from Section 3.]

That's Riley's Section 3 voice again, with a realtime brain behind it.

Now pure realtime, same question.

```bash
uv run agents/s06_realtime_agent.py console
```

[DEMO: same question. Riley answers in `marin`.]

Can you hear the difference? The realtime voice is a bit more expressive. The hybrid is a bit more consistent with the brand. [PAUSE] Neither is wrong. It depends on what Maple Street Dental cares about more.

[SLIDE 3: Hybrid gotchas]
- Use `modalities=["text"]`, not the default `["text", "audio"]`, or you pay for audio you throw away
- The `voice=` argument is ignored in text mode
- Latency = realtime text TTFT + TTS TTFB
- Transcripts: caller side from the transcription model, Riley's side is her exact text

[AVATAR]

Four gotchas. One: set modalities to text only. The plugin's default is text and audio, and if you add a TTS on top, you pay for audio output tokens you never play. Two: the voice argument does nothing in text mode. Three: your latency is now the realtime model's time to first text token plus the TTS time to first byte. Four, a bonus: Riley's side of the transcript is now exact, because it's the text she actually spoke. That makes the judge tests in Section 9 more trustworthy.

[AVATAR]

So when should you choose the hybrid? Here's how I think about it. Pick it when the voice is part of the brand, when you need exact wording for things like policies and read-backs, or when you want the text checkpoint for guardrails, but you still want realtime's natural turn-taking and its ear for tone. Skip it when every millisecond counts and a built-in voice is acceptable, because pure realtime is still faster.

Let's put numbers on that trade. Say pure realtime starts speaking about six hundred and fifty milliseconds after the caller stops. The hybrid waits for the first text tokens, maybe four hundred milliseconds, then Cartesia needs another hundred and fifty or so to start the audio. That lands around eight hundred to eight hundred and fifty milliseconds. [PAUSE] Still under our one-second target from lecture 1.4, and still faster than a typical cascaded turn on a phone line. For Maple Street Dental, that's a very reasonable price for keeping their brand voice. In the next lecture, we'll check whether my guesses survive real measurement.

### Recap

Setting `modalities=["text"]` and adding `tts=build_tts(settings)` with `REALTIME_HYBRID=1` gives Riley a realtime brain with her brand voice and text-level control, for the price of one TTS hop.

### Transition

Now we have three Rileys: cascaded, realtime and hybrid. In the next lecture we put them head to head on the same five calls and let the numbers, and your ears, decide.

### Speaker notes: common mistakes and Q&A

- **Doubled cost**: `modalities` left at the default while also passing `tts=`. Set `["text"]` for hybrid.
- **`REALTIME_HYBRID` not picked up**: it must be exactly `1`, and set inline before `uv run` or exported in the same shell.
- **"Can I use my own STT with a realtime model?"** You can disable server turn detection (`turn_detection=None`) and let LiveKit's STT, VAD and turn detector drive turns, but most people don't need to.
- **Hybrid still pays realtime audio input**: savings versus pure realtime come only from the output side. Compare in 10.4.

---

## Lecture 6.4: Head-to-head: cascaded vs realtime

| Field | Value |
|---|---|
| ID | 6.4 |
| Title | Head-to-head: cascaded vs realtime |
| Type | DM (live demo) |
| Target duration | 10:00 (about 1,000 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Choose an architecture by running the same five calls through each version, hearing them side by side, and comparing latency, cost per minute, tool accuracy and interruption handling. |
| Prerequisites | 6.2, 6.3; `agents/s05_booking_agent.py` runs |
| Files used | `agents/s05_booking_agent.py` (`RileyBookingAgent`), `agents/s06_realtime_agent.py` (`RealtimeRiley`, `REALTIME_HYBRID`), `10-resources/architecture-decision-matrix.md`, `04-labs/lab-04-realtime-vs-cascaded.md` (comparison sheet) |

**Learning objectives**

1. Run a fair comparison using a fixed script of five test calls across cascaded, realtime and hybrid Riley, and hear the differences in side-by-side playback.
2. Read latency, cost-per-minute, tool-accuracy and interruption results and connect each to the architecture.
3. Fill the architecture decision matrix for a real business requirement.

### Script

[AVATAR]

Every opinion about realtime versus cascaded on the internet is someone else's test, on someone else's prompts, at someone else's prices. [PAUSE] Today you get your own. Same five calls. Three versions of Riley. Four numbers. Then we decide.

[SLIDE 1: The five test calls]
1. Simple FAQ: "What time do you close on Friday?"
2. Book: "Cleaning next Tuesday morning, name Alex Kim, 512-555-0188"
3. Correction: "Actually, make that Thursday"
4. Barge-in: interrupt Riley mid read-back with "No, the afternoon"
5. Cancel: "Cancel my appointment on the 14th"

[AVATAR]

Here's the script. Five calls that cover what a receptionist actually does. A quick question. A booking with a name and phone number. A correction. An interruption in the middle of a read-back. And a cancellation. I say the exact same words each time, from this card, at the same pace. That's the only way the comparison is fair.

[SLIDE 2: The four numbers]
- Latency: end of caller speech → first Riley audio (median of 5 turns)
- Cost per minute: from usage summary × price table
- Tool accuracy: right tool, right arguments, first try (out of 5)
- Interruptions: did she stop within half a second and handle the new request? (out of 5)

[AVATAR]

And here's what we measure. Latency is the gap between the moment I stop talking and the moment Riley starts. Cost per minute comes from the usage LiveKit reports, multiplied by a price table. Tool accuracy asks: did Riley call the right tool with the right arguments on the first try? And interruptions asks: when I cut her off, did she actually stop, and did she handle what I said?

For latency today, I've pasted a three-line metrics logger into each entrypoint, right after the session is created. It's a preview of Section 10, where we'll do this properly and export to a file. For now, it just prints each metric as it arrives.

[CODE: temporary metrics logger, added after `session = ...` in both entrypoints]

```python
from livekit.agents import MetricsCollectedEvent, metrics

    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
```

[SCREEN: terminal split in three panes: cascaded, realtime, hybrid. Each started with metrics logging on.]

```bash
# pane 1: cascaded (Section 5)
MAPLE_TODAY=2026-10-05 uv run agents/s05_booking_agent.py console

# pane 2: pure realtime
MAPLE_TODAY=2026-10-05 uv run agents/s06_realtime_agent.py console

# pane 3: hybrid
MAPLE_TODAY=2026-10-05 REALTIME_HYBRID=1 uv run agents/s06_realtime_agent.py console
```

[DEMO: Cascaded Riley, calls 1 to 5 from the card. Point out log lines for end-of-utterance delay, LLM time to first token and TTS time to first byte after each turn.]

Cascaded first. Call one, the Friday hours. Watch the log. End of utterance delay around half a second, because of the turn detector's minimum delay. LLM time to first token a bit under half a second. TTS time to first byte around a hundred and fifty milliseconds. Add them up and we're a little over a second. You can feel that small gap.

Call two, the booking. Riley asks for anything missing, reads back "Tuesday, October sixth at nine in the morning, Alex Kim," and then calls `book_appointment`. Look at the arguments in the log. Name, phone, reason, start time. All correct. That's one for one on tool accuracy.

Call four, the barge-in. I cut her off during the read-back. [PAUSE] She stops. She re-checks the afternoon. Good.

[DEMO: Realtime Riley, same five calls.]

Now pure realtime. Same card. Call one. [PAUSE] Did you hear that? The answer started noticeably sooner. There's no STT final and no TTS hop. The realtime metrics log a time to first token for the whole speech-to-speech response, and it's sitting around six hundred milliseconds on my connection.

Call two, the booking. The read-back is more natural. Listen to the phone number. "Five one two, five five five, zero one eight eight." It grouped the digits without our Section 4 text transforms. But look at the tool call. [PAUSE] On this run, it passed the phone number with dashes in one call and without in another. Our scheduler normalizes phone numbers, so the booking still worked. But if it didn't, that's the kind of drift you'd only catch with the tool-argument tests in Section 9.

Call four, the barge-in. Realtime is excellent here. It stops almost instantly, because the provider's server hears me while it's speaking.

[DEMO: Hybrid Riley, same five calls.]

Finally, hybrid. The answers start a little later than pure realtime, because of the Cartesia hop, but earlier than cascaded. The voice is the brand voice. And because there's a TTS again, `session.say` and string fillers would work here too. Tool calls look the same as pure realtime, because it's the same brain.

[DEMO: SIDE-BY-SIDE PLAYBACK. Pre-recorded audio of calls 2 and 4 from each architecture (captured with LiveKit session recording or OBS during the runs above). Editor layout: three stacked waveform lanes labelled Cascaded / Realtime / Hybrid, aligned so "caller stops speaking" sits on one vertical line; a red marker on each lane where Riley's first audio starts; the gap in milliseconds printed next to each marker. Play call 2 lane by lane, then call 4 (the barge-in) lane by lane.]

Numbers are easy to skim, so let's listen instead. Here's call two, the booking, from all three versions, lined up so the moment I stop talking sits on the same vertical line. [PAUSE] Cascaded. [PAUSE] Realtime. [PAUSE] Hybrid. Hear how the realtime answer lands almost on top of my last word? And how cascaded leaves a small breath first? That breath is the gap you saw in the logs.

Now call four, the barge-in. Watch the red markers. Cascaded stops a beat after I start talking. Realtime stops almost instantly. Hybrid is close to realtime, because the same server is listening. [PAUSE] Also listen to the voices. Realtime's `marin` is more expressive. Hybrid and cascaded share the Cartesia brand voice. That difference doesn't show up in any metric, and it might matter more to the clinic than a hundred milliseconds. And one more thing about those red markers. [PAUSE] The gap you can see on a waveform is the fairest latency number of all. Cascaded Riley reports separate stages, while realtime Riley mostly reports one time to first token, so their log numbers aren't directly comparable. What the caller hears is.

[SCREEN: `10-resources/architecture-decision-matrix.md` open, with a filled table. Numbers typed in live.]

[SLIDE 3: My results (illustrative; yours will differ)]

| | Cascaded | Realtime | Hybrid |
|---|---|---|---|
| Median latency | about 1.1 s | about 0.65 s | about 0.85 s |
| Cost per minute (3-min call) | about 6.5 cents | about 16 cents | about 10 to 13 cents |
| Tool accuracy | 5 / 5 | 4 / 5 | 4 / 5 |
| Clean interruptions | 4 / 5 | 5 / 5 | 5 / 5 |

[AVATAR]

Here's my sheet. Treat these numbers as illustrative. Prices move, networks differ, and five calls is a small sample. [PAUSE] Cascaded was the slowest at about one point one seconds, but the cheapest, at roughly six and a half cents a minute, and it went five for five on tool calls. Realtime was the fastest at about six hundred and fifty milliseconds, and the best at interruptions, but it cost roughly two and a half times as much per minute. Hybrid landed in the middle on both.

Why is realtime so much more expensive? Remember lecture 6.1. Audio tokens cost far more than text tokens, and every turn re-sends the conversation so far. Longer calls make that gap wider, not narrower. Lecture 10.4 turns this into an exact calculation in `src/maple/costs.py`.

[SLIDE 4: Decision matrix for Maple Street Dental]
- Must read back dates, times and names exactly → favors cascaded or hybrid
- Brand voice on the phone line → rules out pure realtime
- Budget: about 400 calls a day, 3 minutes each → cost per minute matters
- Callers are often older, pause mid-sentence → semantic VAD helps
- Decision: cascaded as default, hybrid as an A/B candidate

[AVATAR]

Now apply it to a real business. Maple Street Dental takes about four hundred calls a day, three minutes each. That's twelve hundred minutes a day. At six and a half cents a minute, that's about seventy-eight dollars a day. At sixteen cents a minute, it's about a hundred and ninety-two. [PAUSE] Over a month, that difference is around three thousand four hundred dollars. They also want their brand voice, and they want dates and names read back precisely.

So my decision for Riley is: cascaded as the default, which is what the rest of this course builds on. Hybrid is an A/B candidate for later, if callers complain about speed. Pure realtime is a great fit for a different business, like a casual language-practice app where expressiveness beats everything.

Your decision might differ. That's fine. What matters is that you made it with your numbers.

### Recap

Run the same scripted calls through each architecture, compare latency, cost per minute, tool accuracy and interruptions, and let the business requirements pick the winner.

### Transition

Your turn: in Lab 4 you'll run the same five calls and fill in your own comparison sheet.

### Speaker notes: common mistakes and Q&A

- **Unfair comparisons**: improvising different words per run, or testing one version on Wi-Fi and another on a hotspot. Read from the card, same network, same mic.
- **Reading one turn's latency**: always compare medians across all turns, not the first reply. The first turn includes connection warm-up.
- **"My realtime cost looks tiny."** Short console calls hide context growth. Run a 3-minute call before judging cost per minute.
- **Side-by-side clips**: record every run (OBS or LiveKit session recording) so the playback segment uses the real calls, not re-enactments. Align lanes on the end of caller speech, not on file start.
- **Prices in the table are illustrative.** The cost numbers match the placeholder `PriceTable` in `src/maple/costs.py` (`typical_cascaded_usage(3)` vs `typical_realtime_usage(3)`); point students to `10-resources/provider-cost-guide.md` and their own invoices for real prices.
- **Pin the date**: `MAPLE_TODAY=2026-10-05` makes "next Tuesday" identical across all three runs.

---

## Lecture 6.5: Lab 4: Measure both architectures

| Field | Value |
|---|---|
| ID | 6.5 |
| Title | Lab 4: Measure both architectures |
| Type | LAB (guided lab; video intro/walkthrough) |
| Target duration | Video 2:00 (about 220 spoken words at ~140 wpm, plus slide and pause time); lab work about 45 minutes off-video |
| One idea | Produce your own architecture comparison with real numbers and a written recommendation. |
| Prerequisites | 6.2, 6.3, 6.4 |
| Files used | `04-labs/lab-04-realtime-vs-cascaded.md`, `agents/lab04_cascaded.py` and `agents/lab04_realtime.py` (copies you make), `labs/lab04_compare.py` (you create it), `10-resources/architecture-decision-matrix.md` |

**Learning objectives**

1. Run the five scripted calls against cascaded, realtime and hybrid Riley with metrics and usage exported.
2. Compare latency fairly (perceived gap in a recording) and cost per minute (from usage and the price table).
3. Write a short, evidence-based architecture recommendation for Maple Street Dental.

### Script

[AVATAR]

Time to get your own numbers. This lab takes about forty-five minutes and costs roughly fifty cents to a dollar fifty in API usage, mostly realtime audio. It's the lab I'd most like you to do, because your network and your voice will give you different results from mine.

[SCREEN: `04-labs/lab-04-realtime-vs-cascaded.md`, scrolling through Steps 1 to 6.]

Open `04-labs/lab-04-realtime-vs-cascaded.md`. Step one pins "today" with `MAPLE_TODAY=2026-10-05`, so both agents offer the same slots. Step two: copy the booking agent and the realtime agent to `lab04_cascaded.py` and `lab04_realtime.py`, and paste in a small exporter that writes metrics and usage to the `metrics` folder. Step three: the same five calls from lecture 6.4, read from the card.

Step four is the one people skip, so don't. The two architectures report different metrics: cascaded gives you separate stages, realtime mostly gives you one time to first token. Comparing those numbers directly isn't fair. So you'll record your screen audio and measure the actual silence between the end of your words and the start of Riley's, like the side-by-side playback in lecture 6.4.

Step five: create `labs/lab04_compare.py`, which prints latency percentiles and cost for each architecture from your files. Step six: repeat with `REALTIME_HYBRID=1`.

[AVATAR]

Then write your recommendation: which architecture you'd pick for Maple Street Dental, and why, citing at least two of your numbers. Post your table in the Q&A if you'd like feedback. I read them.

### Recap

The lab turns lecture 6.4's demo into your own measured comparison and a data-backed recommendation.

### Transition

When your sheet is done, take the short quiz to lock in the section.

### Speaker notes: common mistakes and Q&A

- **Comparing cascaded `llm_ttft` with realtime `ttft`**: not apples to apples. Use the perceived gap from the recording as the headline latency.
- **Realtime run fails immediately**: the OpenAI account lacks realtime access or credit; test the key with a plain request first.
- **Hybrid sounds identical to realtime**: `REALTIME_HYBRID=1` wasn't set in the same command. Put it inline before `uv run`.
- **Cost numbers look wildly off**: placeholder `PriceTable`, or realtime usage priced as text (pass `realtime=True`).

---

## Lecture 6.6: Quiz: Architectures and tools

| Field | Value |
|---|---|
| ID | 6.6 |
| Title | Quiz: Architectures and tools |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 110 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Check you can choose and configure an architecture, and that your tools survive the switch. |
| Prerequisites | 6.1 to 6.5 |
| Files used | `06-assessments/quizzes/section-06.md` (8 questions) |

**Learning objectives**

1. Recall realtime configuration (`modalities`, voice, semantic VAD eagerness).
2. Apply trade-offs between cascaded, realtime and hybrid to a scenario.

### Script

[AVATAR]

Eight quick questions. They cover three things. First, how a realtime model hears, speaks and decides when your turn is over. Second, the configuration: what `modalities=["text"]` does, and why `session.say` breaks without a TTS. Third, choosing an architecture for a scenario.

[SLIDE 1: Quiz: 8 questions]
- Realtime internals and turn detection
- Configuration and gotchas
- Scenario: pick an architecture and justify it

[AVATAR]

A tip before you start: question three describes a clinic with a strict script for cancellation policies and a brand voice on its phone menu. Think about which parts of the pipeline each architecture lets you control, and the answer follows.

If you miss one, the feedback points to the exact lecture to revisit. No time limit. Take it now while the lab numbers are fresh.

### Recap

The quiz checks that you can explain, configure and choose between cascaded, realtime and hybrid voice architectures.

### Transition

Next up is Section 7, where Riley learns to answer clinic questions from a knowledge base and hand calls off to specialist agents.

### Speaker notes: common mistakes and Q&A

- Students often confuse "semantic VAD" with LiveKit's turn detector model. Both judge whether the caller is finished; one runs on OpenAI's server, the other in your agent process.
- The most-missed question is usually "which setup lets `session.say` work?" Answer: any setup with a TTS (cascaded or hybrid).
