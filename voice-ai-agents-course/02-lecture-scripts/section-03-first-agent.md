# Section 3: Your First Voice Agent with LiveKit Agents

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈68 min (10 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only; where talking time is shorter than the target duration, the rest is demo audio, typing, command output and on-screen dwell. Code-along lectures are paced below 140 words per minute to leave room for typing and running commands.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 3.1 | LiveKit mental model: rooms, participants, tracks, dispatch | SL | 8:00 | ~800 |
| 3.2 | AgentSession and Agent: the two core classes | SL | 7:00 | ~800 |
| 3.3 | Code-along: hello Riley in 30 lines | SC | 10:00 | ~675 |
| 3.4 | Dev mode and the Agents Playground | DM | 6:00 | ~475 |
| 3.5 | Choosing STT, LLM and TTS providers | SL | 9:00 | ~850 |
| 3.6 | VAD, turn detection and interruptions | SL | 9:00 | ~875 |
| 3.7 | Tuning turn-taking live | DM | 5:00 | ~475 |
| 3.8 | Lab 2: Customise your first agent | LAB | 4:00 (1:30 video) | ~225 |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | 7:00 | ~550 |
| 3.10 | Quiz: First agent and turn-taking | QZ | 3:00 (1:00 video) | ~125 |

**API guardrails for this section (do not deviate on screen):** `AgentServer()` + `@server.rtc_session()` + `cli.run_app(server)`; `AgentSession(..., turn_handling=TurnHandlingOptions(...))`; `session.start(agent=..., room=ctx.room)`; turn detection with `inference.TurnDetector()`. Never show `WorkerOptions(entrypoint_fnc=...)`, `room_input_options=`, or `MultilingualModel` from the deprecated `turn_detector` plugin, even as "the old way".

---

## Lecture 3.1 — LiveKit mental model: rooms, participants, tracks, dispatch

| Field | Value |
|---|---|
| ID | 3.1 |
| Type | SL (slides) |
| Target duration | 8:00 (~800 spoken words, about 5:43 of talking at 140 wpm) |
| Learning objectives | 1. Explain rooms, participants and tracks, and why the agent is "just another participant". 2. Describe how an agent server registers with LiveKit and gets dispatched into rooms as jobs. 3. Map those ideas to `AgentServer`, `@server.rtc_session()` and `JobContext`. |
| Prerequisites | Section 2 complete |
| Files used | Diagram: LiveKit architecture (slides 2 and 6) |

### Script

[AVATAR]
Here's the idea that makes LiveKit click. Your agent doesn't "receive a call." It joins a room, exactly like a human joins a video meeting. [PAUSE] Once you see it that way, phones, browsers, multiple agents and human transfers all make sense. Let's build that picture.

[SLIDE 1: Four words to know]
- Room: a live session, like a meeting
- Participant: anyone in the room, human or agent
- Track: a stream of audio or video a participant publishes
- Dispatch: how an agent gets sent into a room

Four words. Room, participant, track and dispatch. If you understand these four, you understand LiveKit.

[SLIDE 2: The SFU in the middle]
Diagram: Three participants (Caller's browser, Riley agent, a phone via SIP) around a central box labeled "LiveKit server (SFU)". Arrows: each participant sends one audio stream up, and receives the others' streams down.

At the center is the LiveKit server. It's an SFU, a selective forwarding unit. That's a fancy name for a smart router for media. Every participant sends their audio to the SFU once. The SFU forwards it to whoever needs it.

Why does that matter to you? Because your agent never talks directly to the caller's device. Both of them talk to the SFU. So the caller can be on Chrome, an iPhone app or a landline, and your agent code doesn't change.

[SLIDE 3: Rooms]
- A room is created when the first participant joins (or via the API)
- Each call to Riley is one room
- Room closes when everyone leaves

A room is one live session. For Riley, one phone call is one room. When the caller hangs up and everyone leaves, the room closes. You saw this in Lecture 2.3, when `lk room list` came back empty. No calls, no rooms.

[SLIDE 4: Participants]
- Caller: a human participant (browser, app, or phone via SIP)
- Riley: an agent participant
- Later: a human receptionist joins for transfers (Section 8)

A participant is anyone in the room. The caller is a participant. Riley is a participant too. And in Section eight, when Riley transfers a call, a human receptionist is just one more participant.

That's the big insight. The agent is not special plumbing. It's a participant with a Python brain.

[SLIDE 5: Tracks]
- Participants publish tracks: microphone audio, camera video, screen
- Other participants subscribe to tracks
- Riley subscribes to the caller's audio track and publishes its own audio track
- Transcripts travel alongside as text

Participants publish tracks. A track is a single stream, like microphone audio. Other participants subscribe to the tracks they care about.

So Riley subscribes to the caller's microphone track. That's what it listens to. And Riley publishes its own audio track. That's what the caller hears. Transcripts travel alongside as text, which is how the playground shows live captions. You'll see that in Lecture 3.4.

[SLIDE 6: How the agent gets into the room]
Diagram, numbered steps:
1. Agent server starts and opens a WebSocket to LiveKit Cloud: "I'm available."
2. Caller joins a new room.
3. LiveKit dispatches a job to an available agent server.
4. Agent server starts a job process and calls your entrypoint with a `JobContext`.
5. Your code starts an `AgentSession` in that room. Riley speaks.

Now the fourth word, dispatch. This is where your code comes in.

Step one. You start your agent server. It opens a connection to LiveKit Cloud and says, "I'm available for work." Notice the direction. Your server connects out. You don't need to open any ports or set up a public URL. That makes local development and deployment much simpler.

Step two. A caller joins a new room.

Step three. LiveKit picks an available agent server and sends it a job. A job means "please put an agent in this room."

Step four. The agent server starts a fresh process for that job and calls your entrypoint function. It hands you a job context, which includes the room.

Step five. Your code starts a session in that room, and Riley starts talking.

[SLIDE 7: One server, many calls]
- Each job runs in its own process
- One slow or crashed call doesn't take down the others
- Scale out by running more agent servers (Section 12)

One agent server can handle many calls at once. Each job runs in its own process, so if one call crashes, the others keep going. And when you need more capacity, you run more agent servers. LiveKit spreads the jobs across them. We'll tune all of this in Section twelve.

[SLIDE 8: When the call ends]
- Caller hangs up → their participant leaves the room
- The session closes; your shutdown callbacks run (log the outcome, save metrics)
- The job process ends; the room closes when empty
- Your agent server keeps running, ready for the next job

What about the end of a call? The caller hangs up, so their participant leaves the room. Riley's session notices and closes. Any shutdown callbacks you registered run, which is where you'll log how the call went in Section five, and export metrics in Section ten. Then the job's process ends, and the empty room closes.

Your agent server doesn't stop. It's still registered, still saying "I'm available," waiting for the next job. That separation, one long-lived server and many short-lived jobs, is what lets you deploy an update without dropping live calls. We'll use that in Section twelve.

[SLIDE 9: Automatic vs explicit dispatch]
- Automatic: no agent name, joins every new room (great for development)
- Explicit: named agent, dispatched only when asked (telephony, production, multiple agents)
- Name comes from `LIVEKIT_AGENT_NAME` or `livekit.toml`

There are two dispatch styles. With automatic dispatch, your agent joins every new room in the project. That's perfect while you're developing, and it's what we'll use in this section.

With explicit dispatch, you give the agent a name, and it only joins when something asks for it by name. You'll need that for phone numbers in Section eight, and whenever one project runs more than one kind of agent.

[SLIDE 10: How this maps to code]
```python
from livekit.agents import AgentServer, JobContext, cli

server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    # ctx.room is the room you were dispatched into
    ...

if __name__ == "__main__":
    cli.run_app(server)
```
- `AgentServer`: the process that registers with LiveKit
- `@server.rtc_session()`: "call this for every new job"
- `JobContext`: the job, including `ctx.room`
- `cli.run_app(server)`: adds the console, dev, start and download-files commands

Here's how the picture maps to code. You'll type this in two lectures.

`AgentServer` is the thing that registers with LiveKit. The `rtc_session` decorator marks your entrypoint. It says, "every time a job arrives, call this function." The function receives a `JobContext`, and `ctx.room` is the room you were dispatched into. And `cli.run_app` gives the file its commands: console, dev, start and download-files.

[AVATAR]
So when you hear "the agent joins the room," picture it literally. A new participant walks into a meeting, subscribes to the caller's microphone, and starts publishing its own voice. Everything else in this course, including phones, handoffs and transfers, is a variation on that picture.

**Recap:** LiveKit calls are rooms full of participants publishing tracks, and your agent server gets dispatched into those rooms as jobs through an `@server.rtc_session()` entrypoint.

**Transition:** Next, let's meet the two classes you'll use inside that entrypoint: `AgentSession` and `Agent`.

### Speaker notes: common student mistakes / Q&A

- Mistake: thinking the agent needs a public URL or webhook. It connects outbound over WebSocket. Firewalls only need outbound HTTPS/WSS.
- Mistake: running two copies of `dev` at once with automatic dispatch. Both register, and you can't predict which one gets your test room. Stop old terminals.
- "Is LiveKit only for voice?" No. Video and data tracks work the same way. This course only uses audio and text.
- "Does console mode use a room?" Console mode simulates the job locally with your mic and speakers. Dev mode uses a real room in LiveKit Cloud.

---

## Lecture 3.2 — AgentSession and Agent: the two core classes

| Field | Value |
|---|---|
| ID | 3.2 |
| Type | SL (slides) |
| Target duration | 7:00 (~800 spoken words, about 5:43 of talking at 140 wpm) |
| Learning objectives | 1. Explain what belongs on `Agent` (instructions, tools, per-agent overrides, lifecycle hooks) versus `AgentSession` (models, turn handling, userdata, events). 2. Read an `AgentSession(...)` constructor and name each argument's job. 3. Describe what `session.start(agent=..., room=ctx.room)` does. |
| Prerequisites | 3.1 |
| Files used | None (slides only) |

### Script

[AVATAR]
Two classes do almost all the work in LiveKit Agents. `Agent` and `AgentSession`. Beginners mix them up constantly, and then wonder why their settings don't apply. So here's a simple rule you can keep in your head. The session is the phone line. The agent is the person on the line.

[SLIDE 1: Session = the line. Agent = who's talking.]
- `AgentSession`: the runtime for one call: audio in and out, models, turn-taking, state
- `Agent`: a role: instructions, tools, behavior
- One session can switch between agents (handoffs, Section 7)

Picture Maple Street Dental's front desk phone. The phone line, the headset, the call timer and the notepad, that's the session. The person answering, with their job description and the tools on their desk, that's the agent.

Why split them? Because in Section seven, Riley hands a caller from a greeter to a booking specialist to billing. The phone line stays connected. Only the person on the line changes. Same session, different agent.

[SLIDE 2: Agent: the role]
```python
from livekit.agents import Agent

class Riley(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are Riley, the receptionist for Maple Street Dental...",
        )
```
- `instructions`: the system prompt
- `tools`: what this agent can do (or `@function_tool` methods, Section 5)
- Optional per-agent overrides: `stt`, `llm`, `tts`, `turn_handling`
- Lifecycle hooks: `on_enter`, `on_exit`, `on_user_turn_completed`

Let's start with `Agent`. You create one by subclassing it. The one required argument is `instructions`, which is the system prompt.

An agent also owns its tools. In Section five, you'll add tools by decorating methods on this class. And an agent can override the session's models. For example, a billing specialist could use a bigger LLM, while the greeter uses a fast small one.

Finally, agents have lifecycle hooks. `on_enter` runs when the agent takes over the call. That's where Riley will greet the caller in Section four. `on_user_turn_completed` runs after each thing the caller says, which is handy for looking up knowledge in Section seven.

[SLIDE 3: AgentSession: the runtime]
```python
from livekit.agents import AgentSession, TurnHandlingOptions, inference
from livekit.plugins import silero

session = AgentSession(
    stt="deepgram/nova-3",
    llm="openai/gpt-4.1-mini",
    tts="cartesia/sonic-3",
    vad=silero.VAD.load(),
    turn_handling=TurnHandlingOptions(
        turn_detection=inference.TurnDetector(),
    ),
    userdata=CallState(),          # Section 5
)
```
- `stt`, `llm`, `tts`: the three models of the cascade
- `vad`: voice activity detection
- `turn_handling`: turn detection, endpointing, interruptions
- `userdata`: your own per-call state
- Also: `max_tool_steps`, `user_away_timeout`, `preemptive_generation`

Now the session. This is where the models live. Speech-to-text, the LLM and text-to-speech. Here they're LiveKit Inference strings, the ones you met in Section two.

Then VAD. Silero, loaded once.

Then `turn_handling`. This groups every setting about who speaks when. The turn detector, how long to wait at the end of a turn, and how interruptions work. It gets its own lecture, 3.6.

Then `userdata`. That's a slot for your own data about this call. Caller name, phone number, the appointment being booked. Section five fills it in.

There are a few more settings you'll meet later. `max_tool_steps` limits how many tool calls the LLM can chain in one turn. `user_away_timeout` decides when a quiet caller counts as "away." And preemptive generation lets the LLM start early, which we'll talk about in 3.6.

[SLIDE 4: Starting the session]
```python
await session.start(agent=Riley(), room=ctx.room)
await session.generate_reply(instructions="Greet the caller.")
```
- Connects to the room and subscribes to the caller's audio
- Publishes Riley's audio track and transcripts
- Hands control to the agent
- `generate_reply`: ask the LLM to speak now

Once you have both, you connect them. `session.start` takes the agent and the room from the job context. That one line joins the room, subscribes to the caller's microphone, publishes Riley's voice, and puts Riley in charge.

The session doesn't talk first by default. It waits for the caller. So we'll ask it to speak with `generate_reply`, and give it a one-line instruction: greet the caller.

[SLIDE 5: Two ways to speak]
- `session.generate_reply(instructions=...)`: the LLM writes the words. Flexible, adds LLM latency.
- `session.say("...")`: exact words, straight to TTS. Fast and predictable.

Speaking of speaking, there are two ways to make Riley talk. `generate_reply` asks the LLM to write something, guided by an instruction. It's flexible, but it costs an LLM round trip.

`session.say` sends exact words straight to text-to-speech. It's faster and it never goes off script. That's perfect for fixed lines like a legal disclosure or a greeting. You'll use both.

[SLIDE 6: The session tells you what's happening]
```python
@session.on("user_input_transcribed")     # live speech-to-text, partial and final
@session.on("conversation_item_added")    # a user or agent message was committed
@session.on("agent_state_changed")        # initializing, listening, thinking, speaking
@session.on("user_state_changed")         # speaking, listening, away (Section 4)
@session.on("metrics_collected")          # latency and usage numbers (Sections 9 and 10)
```
- Events are how you observe a live call without changing it
- Handlers are plain functions; start async work with `asyncio.create_task`

The session also tells you what's happening, through events. You subscribe with `session.on` and an event name.

User input transcribed fires as the speech-to-text hears words. Conversation item added fires when a message is committed to the history. Agent state changed tells you whether Riley is listening, thinking or speaking. User state changed tells you whether the caller is speaking, listening, or away, and you'll use that in Section four to handle silence. And metrics collected delivers latency and usage numbers after each step. That one powers Sections nine and ten.

You don't need any of these for a first agent. But when you're debugging, "what state was Riley in when the caller interrupted?" is exactly the question these events answer.

[SLIDE 7: The agent's states, in order]
- initializing → listening → thinking → speaking → listening ...
- "thinking" is the gap the caller hears as silence
- Long "thinking" usually means a slow LLM or a slow tool

Here's the loop of agent states you'll see in logs. Initializing, then listening. When the caller finishes, thinking. When audio starts, speaking. Then back to listening.

Thinking is the state the caller experiences as silence. So when someone says "Riley feels slow," the first question is: how long was it in thinking, and why? A slow LLM, or a slow tool. Section five shows how to cover a slow tool with a short filler phrase.

[SLIDE 8: Where does a setting go?]
Table: Setting | Put it on
- System prompt | Agent
- Tools | Agent
- Default models | AgentSession
- A different model for one specialist | Agent (override)
- Turn-taking defaults | AgentSession
- Caller details for this call | AgentSession `userdata`
- Greeting | Agent `on_enter` (Section 4)

Here's a cheat sheet. Instructions and tools go on the agent. Default models and turn-taking go on the session. Per-call data goes in the session's userdata. And if one specialist needs something different, override it on that agent.

[AVATAR]
When a setting "doesn't work," the first question is always: did I put it on the session or the agent? Because agent settings override session settings. And that's usually the answer.

**Recap:** `AgentSession` is the per-call runtime that owns models, turn-taking and state, and `Agent` is the swappable role that owns instructions, tools and hooks.

**Transition:** Enough slides, let's write the code and hear Riley say hello in about thirty lines.

### Speaker notes: common student mistakes / Q&A

- Mistake: passing `instructions=` to `AgentSession`. Instructions belong to `Agent`.
- Mistake: forgetting `await` on `session.start(...)`. The session never connects and nothing happens, with no error.
- "Is `generate_reply` required?" No. Without it, Riley waits for the caller to speak first. Many phone systems prefer the agent to speak first, so we add it.
- "Why is `userdata` on the session, not the agent?" Because it must survive handoffs between agents in Section 7.

---

## Lecture 3.3 — Code-along: hello Riley in 30 lines

| Field | Value |
|---|---|
| ID | 3.3 |
| Type | SC (code-along) |
| Target duration | 10:00 (~675 spoken words, about 4:49 of talking at 140 wpm) |
| Learning objectives | 1. Build a working cascaded voice agent from an empty file with `AgentServer`, `@server.rtc_session()`, `AgentSession` and `Agent`. 2. Configure STT, LLM, TTS, VAD and the semantic turn detector with `TurnHandlingOptions`. 3. Run it in console mode and read the logs. |
| Prerequisites | 3.1, 3.2, Section 2 complete |
| Files used | You type: `03-code/agents/my_hello_agent.py`. Reference: `03-code/agents/s03_hello_agent.py`. Also `03-code/src/maple/prompts.py` (`HELLO_INSTRUCTIONS`), `03-code/agents/common.py`. |

### Script

[AVATAR]
Time to build. In about thirty lines, you'll write a voice agent that listens, thinks and speaks, running on the same framework companies use in production. I'll type every line and explain it as we go. Open your editor and follow along.

[SCREEN: VS Code, repo open. Right-click `agents/` → New File → `my_hello_agent.py`.]

We'll work in a new file called `my_hello_agent.py`, in the agents folder. The finished reference is `s03_hello_agent.py`, right next to it. That one has a few extras we'll add in later lectures, so if you compare them now, don't worry about the differences.

[CODE: step 1, docstring and imports]
```python
"""Hello Riley: my first cascaded voice agent (Lecture 3.3)."""

import common  # noqa: F401  (loads .env and makes src/ importable)
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)
from livekit.plugins import silero

from maple.prompts import HELLO_INSTRUCTIONS
```

Start with imports. The first one is our own helper module, `common`. Importing it does two useful things: it loads your dot env file, and it makes the `maple` package in `src` importable. We'll use much more of it later.

Then from LiveKit Agents: Agent, AgentServer, AgentSession and JobContext, the classes from the last two lectures. TurnHandlingOptions for turn-taking. `cli` for the command line. And `inference`, for the turn detector.

From the plugins, Silero, our voice activity detector. And from our own code, `HELLO_INSTRUCTIONS`, Riley's first system prompt.

[SCREEN: Split view. Ctrl+click `HELLO_INSTRUCTIONS` to open `src/maple/prompts.py` briefly, then return.]

Quick peek at those instructions. They're built from three blocks: identity, style rules and output rules. Riley is the AI receptionist for Maple Street Dental, it's on the phone, and it keeps replies to one or two short sentences with no markdown. We'll take this apart properly in Section four.

[CODE: step 2, the agent]
```python
class HelloRiley(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=HELLO_INSTRUCTIONS)
```

Now the agent. A class called HelloRiley that extends Agent. For now it only has instructions. No tools yet. Tools arrive in Section five.

[CODE: step 3, the server]
```python
server = AgentServer()
```

Next, the agent server. One line. This is the process that will register with LiveKit and receive jobs.

[CODE: step 4, the entrypoint and the session]
```python
@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt="deepgram/nova-3",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(turn_detection=inference.TurnDetector()),
    )
```

Now the entrypoint. The `rtc_session` decorator tells the server, "run this function for every new call." It receives the job context.

Inside, we build the session. Speech-to-text is Deepgram Nova-3. The LLM is GPT four point one mini. The voice is Cartesia Sonic-3. These are LiveKit Inference strings, so they're billed through your LiveKit project, and you don't need separate provider keys.

VAD is Silero, loaded right here. And turn handling uses the semantic turn detector. It reads the words and predicts whether the caller has finished. Remember, all turn-taking settings live inside TurnHandlingOptions. We'll add endpointing and interruption settings in Lecture 3.6.

[CODE: step 5, start and greet]
```python
    await session.start(agent=HelloRiley(), room=ctx.room)
    await session.generate_reply(
        instructions="Greet the caller as Riley from Maple Street Dental and ask how you can help."
    )
```

Two more lines. `session.start` joins the room with our agent in charge. Notice both awaits. Forget the await on start, and nothing happens, with no error message.

Then `generate_reply`, with a one-off instruction to greet the caller. Without this, Riley would sit silently until the caller spoke first.

[CODE: step 6, run the app]
```python
if __name__ == "__main__":
    cli.run_app(server)
```

And finally, `cli.run_app`. This turns the file into a command-line tool with console, dev, start, connect and download-files commands.

[SCREEN: Show the full file, scrolled to fit on one screen. Line count visible in the status bar: about 40 lines including blanks and imports.]

[CODE: the complete file, `agents/my_hello_agent.py`]
```python
"""Hello Riley: my first cascaded voice agent (Lecture 3.3)."""

import common  # noqa: F401  (loads .env and makes src/ importable)
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)
from livekit.plugins import silero

from maple.prompts import HELLO_INSTRUCTIONS


class HelloRiley(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=HELLO_INSTRUCTIONS)


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt="deepgram/nova-3",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(turn_detection=inference.TurnDetector()),
    )
    await session.start(agent=HelloRiley(), room=ctx.room)
    await session.generate_reply(
        instructions="Greet the caller as Riley from Maple Street Dental and ask how you can help."
    )


if __name__ == "__main__":
    cli.run_app(server)
```

Here's the whole file. Strip out the imports and blank lines, and it's about thirty lines of real code. That's a complete voice agent.

[SCREEN: Terminal in the repo folder.]

Let's run it. If you skipped the download step in Section two, do it now. Any agent file can download the model files, so this one works too.

[CODE: download local model files (once per machine)]
```bash
uv run python agents/my_hello_agent.py download-files
```

[CODE: talk to it]
```bash
uv run python agents/my_hello_agent.py console
```

[DEMO: Riley greets. Say: "Hi, do you do teeth cleanings?" Riley answers in one or two sentences. Then: "Great, what should I bring to my first visit?" Riley answers. Then say "Thanks, bye" and press Ctrl+C.]

[PAUSE]

There it is. Riley greets me, I ask about cleanings, and it answers in a sentence or two. That's the output rules from the prompt doing their job.

[SCREEN: Scroll up through the terminal log output. Highlight the user transcript line, the agent reply, and any metrics lines.]

Now scroll up through the logs. You can see what the speech-to-text heard. You can see Riley's reply text. And depending on your log level, you'll see timing information for each stage. Hold that thought. Those numbers become our latency budget measurements in Sections nine and ten.

[SLIDE 1: What each line does]
| Line | Job |
|---|---|
| `AgentServer()` | Registers with LiveKit, receives jobs |
| `@server.rtc_session()` | "Run this for every new call" |
| `AgentSession(...)` | The runtime: STT, LLM, TTS, VAD, turn handling |
| `HelloRiley(Agent)` | The role: instructions (tools later) |
| `session.start(...)` | Join the room, subscribe, publish, hand control to the agent |
| `generate_reply(...)` | Speak first |
| `cli.run_app(server)` | console, dev, start, connect, download-files |

[AVATAR]
Here's every line and its job on one slide. If any of these feel fuzzy, rewatch Lecture 3.2. Everything else in this course builds on this file.

One more thing. Right now the model names are hard-coded. That's fine for a first agent, but it means changing a voice means changing code. In Lecture 3.5, we'll move them into configuration.

**Recap:** About thirty lines of Python give you a working voice agent: an `AgentServer`, an `@server.rtc_session()` entrypoint, an `AgentSession` with STT, LLM, TTS, VAD and turn detection, and an `Agent` with instructions.

**Transition:** Console mode works on your laptop, so next let's run Riley in dev mode and call it from a browser through LiveKit Cloud.

### Speaker notes: common student mistakes / Q&A

- Mistake: `ModuleNotFoundError: No module named 'maple'`. Either the file isn't in `agents/` (so `import common` fails), or `import common` was removed. Keep the file in `agents/` and keep that import first.
- Mistake: forgetting `await` on `session.start(...)`. The console hangs silently. Add the `await`.
- Mistake: putting `instructions=` in `AgentSession(...)`. It's an `Agent` argument.
- "Why does `import common` come before the LiveKit imports?" It loads `.env` first, so every later import sees your keys and settings. Linters may complain about import order; the `noqa` comment is deliberate.

---

## Lecture 3.4 — Dev mode and the Agents Playground

| Field | Value |
|---|---|
| ID | 3.4 |
| Type | DM (live demo) |
| Target duration | 6:00 (~475 spoken words, about 3:24 of talking at 140 wpm) |
| Learning objectives | 1. Run the agent server in `dev` mode and explain how it differs from `console`. 2. Connect to Riley from the LiveKit Agents Playground and read live transcripts. 3. Use hot reload to change Riley's behavior without restarting. |
| Prerequisites | 3.3 |
| Files used | Your `agents/my_hello_agent.py` (reference: `03-code/agents/s03_hello_agent.py`) |

### Script

[AVATAR]
Console mode is great for quick checks, but it's a simulation on your laptop. Real callers join rooms in LiveKit Cloud. Dev mode puts your agent there, while it still runs on your machine, with hot reload. It's how you'll work for most of the course.

[SLIDE 1: console vs dev vs start]
- `console`: local mic and speakers, no room, fastest feedback
- `dev`: registers with LiveKit Cloud, joins real rooms, hot reload, debug logs
- `start`: production mode, no reload (Section 12)

Quick comparison. Console runs a simulated session with your mic and speakers, and no room. Dev registers your agent server with LiveKit Cloud, so it gets dispatched into real rooms, like the ones a browser or phone would create. It also reloads when you save a file. Start is the production version, which we'll use in Section twelve.

[SCREEN: Terminal in the repo folder.]

[CODE: run the agent server in dev mode]
```bash
uv run python agents/my_hello_agent.py dev
```

[DEMO: Logs show the server starting, then a "registered" line with a worker ID and region.]

Look for the registered line. That means your agent server connected out to LiveKit Cloud and said "I'm available." Remember, you didn't open any ports. It dialed out.

It's also waiting. No room, no job. So let's make a room.

[SCREEN: Browser, open https://agents-playground.livekit.io. Choose to connect to your LiveKit Cloud project and sign in. Click "Connect".]

This is the LiveKit Agents Playground. It's a web page that creates a room in your project and joins it as a caller, with your browser's microphone. Connect it to your LiveKit Cloud project, and click connect.

[DEMO: Browser asks for mic permission. Allow. Within a second or two, the agent joins and Riley greets you. Transcript panel fills in live.]

The browser asks for the microphone. Allow it. And a moment later, Riley joins and greets me.

[PAUSE]

Look at the terminal. You'll see a new job appear. LiveKit dispatched it to my laptop, my server started a process, and the entrypoint ran. Exactly the five steps from Lecture 3.1.

[DEMO: Ask: "Hi Riley, do you do teeth whitening?" Riley answers briefly. Point at the transcript panel.]

Now look at the playground's transcript panel. My words appear as I speak them. That's the live speech-to-text. Then Riley's reply appears, synced with the audio. This is the fastest way to spot a mishearing. If Riley's answer seems odd, check what it actually heard.

[SCREEN: New terminal tab.]

[CODE: see the live room]
```bash
lk room list
```

[DEMO: One room listed, with two participants.]

And in a second terminal, lk room list. This time there's a room, with two participants. Me, and Riley.

[SCREEN: VS Code, `agents/my_hello_agent.py`. Change the greeting instruction to "Greet the caller as Riley from Maple Street Dental, mention we're open Saturday mornings, and ask how you can help." Save.]

Now, hot reload. I'll change the greeting instruction to mention that we're open on Saturday mornings. And save.

[DEMO: Terminal shows the server reloading.]

The server reloaded. But notice the call that's already running keeps the old code. Hot reload applies to new jobs. So I'll disconnect in the playground and connect again.

[DEMO: Disconnect, reconnect. Riley greets with the new Saturday line.]

New room, new job, new greeting. That's your edit loop for the rest of the course. Edit, save, reconnect.

[SLIDE 2: Your development loop]
1. `dev` running in one terminal
2. Playground (or console) as the caller
3. Edit and save → server reloads
4. Reconnect to get a fresh job
5. Read transcripts and logs

[AVATAR]
Two more tips. First, keep only one dev server running. If you have two terminals both running dev, both register, and you can't predict which one gets your call. That one confuses everybody at least once.

Second, you're not limited to the playground. In Section twelve, you'll put a real web front end in front of Riley using LiveKit's React starter. And in Section eight, a phone number. The agent code won't change. Only the caller does.

**Recap:** `dev` mode registers your local agent server with LiveKit Cloud so the Agents Playground can call it, with live transcripts and hot reload for new sessions.

**Transition:** Riley works, so now let's look at the three models inside it and how to choose them.

### Speaker notes: common student mistakes / Q&A

- Agent never joins the playground room: check that exactly one `dev` server is running, that `.env` has the right `LIVEKIT_URL`, and that `LIVEKIT_AGENT_NAME` is *not* set yet. A name switches to explicit dispatch (Section 8), and the playground won't request it.
- Mistake: expecting hot reload to change an in-progress call. Reload affects new jobs only. Reconnect.
- The playground's URL and UI evolve. If it looks different, the LiveKit Cloud dashboard also has a built-in way to talk to your agent. The idea is the same: create a room, join as the caller.
- Corporate VPNs sometimes block WebRTC in the browser. If audio never connects, try without the VPN.

---

## Lecture 3.5 — Choosing STT, LLM and TTS providers

| Field | Value |
|---|---|
| ID | 3.5 |
| Type | SL (slides with a short code walkthrough) |
| Target duration | 9:00 (~850 spoken words, about 6:04 of talking at 140 wpm) |
| Learning objectives | 1. Compare STT, LLM and TTS providers on accuracy, latency, price, voices and languages. 2. Switch between LiveKit Inference model strings and direct provider plugins. 3. Drive every model choice from `.env` via `src/maple/config.py`, and know the builder helpers in `agents/common.py` used from Section 4 on. |
| Prerequisites | 3.3, 2.1 |
| Files used | `03-code/src/maple/config.py`, `03-code/agents/common.py` (`build_stt`, `build_llm`, `build_tts`, `create_session`), `03-code/agents/s03_hello_agent.py`, your `agents/my_hello_agent.py` |

### Script

[AVATAR]
Every few months, a new speech model claims to be the fastest, most accurate, most human-sounding ever. [PAUSE] You don't need to chase them. You need two things: a way to judge them on your own calls, and code that lets you swap one in by editing a single line. This lecture gives you both.

[SLIDE 1: Five questions for every model]
- Accuracy: does it get *your* words right? (names, numbers, domain terms)
- Latency: time-to-first-token or time-to-first-byte, at p95
- Price: per minute, per token or per character
- Voice and language coverage
- Data handling: retention, region, compliance

Ask five questions of every model. Accuracy on your words, not a benchmark's. Latency, and specifically the slow tail. Price. Voice and language coverage. And data handling, meaning where audio goes and how long it's kept. For a dental clinic, that last one matters.

[SLIDE 2: STT: speech-to-text]
| What matters | Why |
|---|---|
| Streaming with fast finals | Feeds the endpointing and STT-final line items |
| Keyterm or keyword boosting | "Invisalign", "Doctor Alvarez", "Delta Dental" |
| Phone-audio accuracy | 8 kHz calls in Section 8 |
| Default | `deepgram/nova-3` |
| Alternatives | AssemblyAI Universal-Streaming, others via LiveKit Inference |

For speech-to-text, you want streaming with fast final transcripts, because that feeds the latency budget. You want keyterm boosting, so it hears "Invisalign" and not "invisible line." And you want good accuracy on phone audio, which we'll test in Section eight.

Our default is Deepgram Nova-3. The repo also lists AssemblyAI's streaming model as a fallback. In Section nine, you'll measure word error rate on Maple Street's own vocabulary and decide with data.

[SLIDE 3: LLM]
| What matters | Why |
|---|---|
| Time-to-first-token | Largest line item after endpointing |
| Reliable tool calling | Booking must be exact |
| Instruction following | Short answers, one question at a time |
| Default | `openai/gpt-4.1-mini` |
| Fallback in config | `google/gemini-2.5-flash` |

For the LLM, bigger is not better on the phone. You want fast time-to-first-token, reliable tool calls and good instruction following. A small, fast model that follows "one or two sentences" beats a giant model that writes an essay.

Our default is GPT four point one mini. The config also names a fallback from a different provider, so an outage at one vendor doesn't take Riley down. We'll wire up fallbacks in Section thirteen.

[SLIDE 4: TTS: text-to-speech]
| What matters | Why |
|---|---|
| Time-to-first-byte | Caller hears something sooner |
| Naturalness and pacing | Trust and comprehension |
| Voice library and cloning policy | Brand fit (Section 4) |
| Pronunciation control | Names and numbers |
| Default | `cartesia/sonic-3` |
| Alternatives | Deepgram Aura-2, ElevenLabs, others |

For text-to-speech, time-to-first-byte comes first, then naturalness. Then voice choice, because the voice is your brand. And pronunciation control, for names and numbers.

Our default is Cartesia Sonic-3, chosen for fast first audio. Deepgram Aura-2 and ElevenLabs are common alternatives. Pick by listening. Record the same three sentences with each voice and play them to someone who isn't you.

[SLIDE 5: Prices change: compare structure, not numbers]
- STT: billed per audio minute
- LLM: billed per input and output token (short replies keep this small)
- TTS: billed per character, often the largest slice of a cascaded call
- Check current pricing; the repo's price table is a placeholder

I'm not putting prices on this slide on purpose. They change too often. What stays stable is the structure. STT bills per minute of audio. LLMs bill per token. TTS bills per character, and it's often the largest slice of a cascaded call. So short replies save money twice: fewer output tokens and fewer characters to speak.

[SLIDE 6: Two ways to plug a model in]
```python
# LiveKit Inference: a string, billed through LiveKit Cloud
stt="deepgram/nova-3"
tts="cartesia/sonic-3:f786b574-daa5-4673-aa0c-cbe3e8534c02"   # model:voice

# Direct plugins: your own provider keys, every provider option
from livekit.plugins import cartesia, deepgram, openai
stt=deepgram.STT(model="nova-3", keyterm=["Invisalign", "Delta Dental"])
llm=openai.LLM(model="gpt-4.1-mini")
tts=cartesia.TTS(model="sonic-3", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02")
```

Two ways to plug in a model, which you met in Section two. Model strings through LiveKit Inference. One account, one bill. Note the colon trick for voices. "Cartesia slash sonic three colon" and then a voice ID picks the voice.

Or direct plugins, with your own keys. You get every provider option, and you pay the provider directly.

When should you switch to plugins? When you need an option LiveKit Inference doesn't expose, when you have negotiated pricing with a provider, or when compliance says audio must go straight to a specific vendor.

[SCREEN: VS Code, `src/maple/config.py`. Scroll through `Settings` fields and `load_settings()`.]

Now let's see how the repo makes swapping painless. Open `src/maple/config.py`. The Settings dataclass holds every model choice: STT model, LLM model, TTS model and voice, realtime model, and provider mode. `load_settings` reads each one from the environment, with the course defaults as fallbacks. It's pure Python, and it has its own unit tests.

[SCREEN: Scroll to `tts_model_with_voice` and `split_model`.]

Two helpers worth knowing. `tts_model_with_voice` glues the voice ID onto the TTS string, using that colon format. And `split_model` turns "openai slash gpt four point one mini" into the provider and the model name, which the plugin path needs.

[SCREEN: VS Code, `agents/my_hello_agent.py`. Replace the three hard-coded strings with settings.]

[CODE: refactor the session in `my_hello_agent.py` to read from config]
```python
from common import get_settings

# inside entrypoint:
    settings = get_settings()
    session = AgentSession(
        stt=settings.stt_model,                 # "deepgram/nova-3"
        llm=settings.llm_model,                 # "openai/gpt-4.1-mini"
        tts=settings.tts_model_with_voice,      # "cartesia/sonic-3:<voice>"
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(turn_detection=inference.TurnDetector()),
    )
```

Now let's use it. In our hello agent, import get settings from common, load the settings inside the entrypoint, and replace the three hard-coded strings. Speech-to-text, the LLM, and the TTS model with its voice. This is exactly how the reference file, `s03_hello_agent.py`, does it.

[SCREEN: VS Code, `agents/common.py`. Scroll to `build_stt`, `build_llm`, `build_tts`, then `create_session`.]

From Section four onward, the agents go one step further. `agents/common.py` has three builders: build STT, build LLM and build TTS. Each one checks the provider mode. In inference mode, it returns a model string, or, for Deepgram, an inference STT with a list of dental keyterms attached, so it hears "Invisalign" and "Delta Dental." In plugins mode, it builds the provider plugin with your own key.

And `create_session` wraps all of it: models, VAD, turn handling and call state, in one call. You'll use it from Section four on, so every agent is configured the same way.

[SLIDE 7: Swapping is now a one-line change in `.env`]
```bash
# try a different voice
TTS_VOICE=<voice-id-from-the-cartesia-library>

# try a different LLM through LiveKit Inference
LLM_MODEL=google/gemini-2.5-flash

# use your own provider keys instead (agents built with create_session, Section 4 on)
MAPLE_PROVIDER_MODE=plugins
```

And now every experiment is a one-line change in dot env. A different voice. A different LLM. Or, for the agents that use create session, plugins mode with your own keys. No code edits, no merge conflicts, and when a provider renames a model next year, you fix it in one place.

[AVATAR]
Here's my advice for choosing. Start with the defaults. Get the whole agent working. Then measure. In Section nine, you'll measure STT accuracy on your words. In Section ten, you'll measure latency and cost per minute. Then change one model at a time, and let the numbers decide.

**Recap:** Judge models on accuracy, latency, price, voice and data handling, plug them in as LiveKit Inference strings or direct plugins, and keep every choice in `.env` through `config.py` and the builders in `common.py`.

**Transition:** Next, the settings that make Riley feel human or robotic: VAD, turn detection and interruptions.

### Speaker notes: common student mistakes / Q&A

- Mistake: expecting `MAPLE_PROVIDER_MODE=plugins` to change `s03_hello_agent.py`. The hello agent uses model strings only; plugins mode applies to agents built with `create_session` (Section 4 on).
- Mistake: switching to `MAPLE_PROVIDER_MODE=plugins` without setting `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY` and `OPENAI_API_KEY`. Plugins mode needs all three.
- Mistake: pasting a voice *name* ("Katie") where a voice *ID* is required. Use the ID from the provider's voice library.
- Mistake: comparing TTS voices on laptop speakers only. Listen on a phone speaker too; that's what callers hear in Section 8.
- "Is there one best provider?" No. It depends on your language, vocabulary, budget and compliance needs. Measure with your own calls.

---

## Lecture 3.6 — VAD, turn detection and interruptions

| Field | Value |
|---|---|
| ID | 3.6 |
| Type | SL (slides) |
| Target duration | 9:00 (~875 spoken words, about 6:15 of talking at 140 wpm) |
| Learning objectives | 1. Explain how Silero VAD, endpointing delays and the semantic turn detector work together to end a turn. 2. Configure `TurnHandlingOptions` with `EndpointingOptions` (fixed vs dynamic, `min_delay`, `max_delay`) and `InterruptionOptions` (`min_duration`, `min_words`, false-interruption resume). 3. Describe preemptive generation and its trade-off. |
| Prerequisites | 3.3, 1.4 |
| Files used | Diagram: turn-taking timeline (slides 2 and 5) |

### Script

[AVATAR]
Two complaints account for most bad reviews of voice agents. "It kept cutting me off." And "it took forever to answer." [PAUSE] They're the same problem pointing in opposite directions. Both come down to one decision, made many times per call: has the caller finished? Let's look at exactly how Riley makes that decision, and every setting that controls it.

[SLIDE 1: Three layers decide "your turn is over"]
- VAD: is there speech right now? (Silero, frame by frame)
- Endpointing: how long has it been quiet? (`min_delay`, `max_delay`)
- Turn detector: do the words sound finished? (`inference.TurnDetector()`)

Three layers work together. VAD hears whether there's speech right now. Endpointing counts how long it's been quiet. And the turn detector reads the words and asks, does this sound like a finished thought?

[SLIDE 2: Timeline of one turn]
Diagram, horizontal time axis:
- Caller speaks: "I'd like to book for... [pause 400 ms] ...Thursday morning." 
- VAD: speech / silence / speech / silence
- Turn detector at the first pause: "unlikely finished" → keep waiting
- At the final silence: "likely finished" → wait only `min_delay` → end of turn
- Label: "end-of-utterance delay" from last speech to end of turn

Here's one turn on a timeline. The caller says "I'd like to book for..." and pauses. VAD sees silence. But the turn detector reads "I'd like to book for" and says that sentence isn't finished. So Riley keeps waiting, up to the maximum delay.

Then the caller says "Thursday morning" and stops. VAD sees silence again. This time the detector says, that's a complete thought. So Riley waits only the minimum delay, then ends the turn and starts answering.

That gap, from the last bit of speech to the end of the turn, is the end-of-utterance delay. It's the endpointing line item from our latency budget.

[SLIDE 3: VAD: Silero settings]
```python
vad = silero.VAD.load(
    min_speech_duration=0.05,     # seconds of speech to start a speech segment
    min_silence_duration=0.55,    # seconds of silence to end a speech segment
    activation_threshold=0.5,     # higher = less sensitive to noise
)
```
- Defaults are good for most calls
- Noisy environments: raise `activation_threshold`
- Don't use `min_silence_duration` to tune turn-taking: that's endpointing's job

Let's take each layer's settings. VAD first. These are Silero's main knobs, shown with their defaults. Minimum speech duration, minimum silence duration and activation threshold.

My advice: leave them alone at first. The one you might change is activation threshold. If callers are in noisy places and background sounds keep triggering Riley, raise it a little. Higher means less sensitive.

And a common mistake: using VAD's silence setting to control turn-taking. Don't. That's what endpointing is for.

[SLIDE 4: Endpointing options]
```python
from livekit.agents import EndpointingOptions

endpointing=EndpointingOptions(
    mode="fixed",       # or "dynamic"
    min_delay=0.5,      # wait at least this long after speech ends
    max_delay=3.0,      # never wait longer than this
)
```
- `min_delay`: used when the turn detector is confident the caller is done
- `max_delay`: the ceiling when it thinks they're still going
- `"dynamic"`: adapts between the two based on this caller's pause patterns

Endpointing has three settings. Minimum delay is how long Riley waits after speech ends when the turn detector is confident the caller is done. The default is half a second. Maximum delay is the ceiling when the detector thinks they're still going. The default is three seconds.

Then there's mode. Fixed uses those numbers as they are. Dynamic learns from the caller's own pauses during the call and adjusts within that range. It's worth trying for callers who speak slowly, like many older patients.

Think about what each number costs. Lower the minimum, and Riley feels snappier but interrupts more. Raise the maximum, and Riley is more patient with slow speakers but has longer awkward gaps when the detector is unsure.

[SLIDE 5: The semantic turn detector]
```python
turn_detection=inference.TurnDetector()
```
- A small language model trained on conversation
- Reads the transcript so far and predicts "finished" or "not finished"
- "My number is five five five..." → not finished
- "Thursday morning works." → finished
- Runs on LiveKit Inference, with a local fallback (that's why we ran `download-files`)

The turn detector is the clever part. It's a small language model trained on real conversations. It reads the transcript so far and predicts whether the speaker is done.

"My number is five five five..." Not finished. Keep waiting. "Thursday morning works." Finished. Answer now.

Without it, you only have silence to go on, and you'd have to pick one delay for everything. With it, Riley can be quick when the sentence is clearly done and patient when it's clearly not. That's the single biggest improvement in turn-taking you can make.

It runs on LiveKit Inference, with a local fallback model. That's one of the files you downloaded in Section two.

[SLIDE 6: Interruptions]
```python
from livekit.agents import InterruptionOptions

interruption=InterruptionOptions(
    enabled=True,
    min_duration=0.5,                  # seconds of caller speech to count as an interruption
    min_words=0,                       # also require this many transcribed words
    resume_false_interruption=True,    # resume if it was just a cough or "mm-hm"
    false_interruption_timeout=2.0,    # silence after which it counts as false
)
```

Now the other direction. What happens when the caller talks while Riley is talking?

By default, Riley stops. That's what a polite human does. But not every sound is an interruption. A cough. A "mm-hm." Someone in the background.

So there are guards. Minimum duration means the caller must speak for at least half a second to count. Minimum words means STT must transcribe at least that many words. Set it to two, and "mm-hm" won't stop Riley, but "wait, no" will.

And there's a safety net called false interruption resume. If Riley stops, but the caller then says nothing for two seconds, Riley decides it was a false alarm and picks up where it left off.

[SLIDE 7: When not to allow interruptions]
- Legal or compliance disclosures
- Reading back a booking right before committing it (Section 5)
- Per-utterance: `session.say(..., allow_interruptions=False)`
- In a tool: `context.disallow_interruptions()`

Sometimes you don't want Riley to be interruptible at all. A required disclosure. Or the moment it commits a booking. You can switch it off for a single sentence, or from inside a tool. You'll use both in Section five.

[SLIDE 8: Preemptive generation]
- The LLM starts drafting a reply before the turn is confirmed
- If the caller keeps talking, the draft is thrown away
- Saves time on the LLM line item; costs some extra tokens
- On by default in LiveKit Agents 1.8

One more setting, and it's a latency trick. Preemptive generation. As soon as the transcript looks final, the LLM starts drafting a reply, even before endpointing officially ends the turn. If the caller keeps talking, the draft is thrown away. If not, Riley's reply is already partly written.

It overlaps the LLM's time-to-first-token with the endpointing wait. That's two of our biggest line items running in parallel. The cost is some wasted tokens on drafts that get thrown away. It's on by default, and for most agents that's the right call.

[SLIDE 9: Putting it together]
```python
session = AgentSession(
    stt="deepgram/nova-3",
    llm="openai/gpt-4.1-mini",
    tts="cartesia/sonic-3",
    vad=silero.VAD.load(),
    turn_handling=TurnHandlingOptions(
        turn_detection=inference.TurnDetector(),
        endpointing=EndpointingOptions(min_delay=0.5, max_delay=3.0),
        interruption=InterruptionOptions(min_duration=0.5, min_words=0),
    ),
)
```

Here's everything in one place. It all lives inside turn handling options. Turn detection, endpointing and interruption. These are the defaults, written out so you can see them. In the next lecture, we'll change them and listen to the difference.

[AVATAR]
Here's the mental model to keep. The turn detector decides whether the caller is probably done. Endpointing decides how long to wait in each case. And interruption settings decide what happens when both of you talk at once. Tune them in that order.

**Recap:** VAD detects speech, the semantic turn detector judges whether the words are finished, endpointing delays set how long to wait, and interruption options decide what counts as a real interruption.

**Transition:** Now let's change those settings live and hear exactly what each one does to Riley.

### Speaker notes: common student mistakes / Q&A

- Mistake: setting `min_delay` to 0.1 to "make it faster," then wondering why Riley talks over people mid-sentence.
- Mistake: tuning everything at once. Change one setting, run the same three test phrases, then change the next.
- Mistake: using the old `turn_detector` plugin's `MultilingualModel`. It's deprecated in 1.8. Use `inference.TurnDetector()` inside `TurnHandlingOptions`.
- "Does turn detection work in other languages?" The inference turn detector is multilingual. Test it with your language and your callers.

---

## Lecture 3.7 — Tuning turn-taking live

| Field | Value |
|---|---|
| ID | 3.7 |
| Type | DM (live demo) |
| Target duration | 5:00 (~475 spoken words, about 3:24 of talking at 140 wpm) |
| Learning objectives | 1. Change endpointing delays through `.env` and hear the effect on the same three test phrases. 2. Adjust interruption settings so backchannels don't stop Riley but real interruptions do. 3. Avoid the three most common tuning mistakes. |
| Prerequisites | 3.6 |
| Files used | `03-code/agents/s03_hello_agent.py`, your `agents/my_hello_agent.py`, `03-code/.env` (`MIN_ENDPOINTING_DELAY`, `MAX_ENDPOINTING_DELAY`) |

### Script

[AVATAR]
Tuning turn-taking by reading numbers is like tuning a guitar by reading the manual. You have to listen. So let's use three test phrases, change one setting at a time, and hear what happens.

[SLIDE 1: Three test phrases (say them the same way every time)]
1. The pause test: "My number is five one two... [pause] ...five five five... [pause] ...zero one four eight."
2. The hesitation test: "I'd like to book a cleaning for, um... [pause] ...Thursday."
3. The snap test: "Yes." (Riley should answer quickly.)

Here are the three phrases. The pause test, a phone number with natural gaps. The hesitation test, with an "um" in the middle. And the snap test, a one-word answer, where Riley should respond quickly.

Say them the same way every time. Consistency is what makes the comparison fair.

[SCREEN: Terminal. Show the `.env` endpointing lines first.]

[CODE: default endpointing in `.env`]
```bash
MIN_ENDPOINTING_DELAY=0.5
MAX_ENDPOINTING_DELAY=3.0
```

Round one, the defaults. Half a second minimum, three seconds maximum. The reference hello agent reads these from config and passes them into its endpointing options.

[CODE: run in console mode]
```bash
uv run python agents/s03_hello_agent.py console
```

[DEMO: Say all three phrases. Riley waits through the phone-number pauses, waits through the "um", and answers "Yes" promptly.]

Listen. [PAUSE] It waited through my phone number pauses, because the turn detector knew the number wasn't finished. It waited through the "um." And on "yes," it came back fast. That's the semantic turn detector doing its job.

[CODE: round two, too snappy (edit `.env`, then restart)]
```bash
MIN_ENDPOINTING_DELAY=0.1
MAX_ENDPOINTING_DELAY=0.6
```

Round two. I'll make it aggressive. A tenth of a second minimum, and a ceiling of just over half a second. Save, and restart.

[DEMO: Same three phrases. Riley jumps in after "five one two" and again after "um".]

Hear that? Riley jumped in right after "five one two." Even though the turn detector said "not finished," the maximum delay of point six seconds forced the turn to end. The ceiling beat the model. That's the most common tuning mistake: a low maximum delay silently overrides the turn detector.

[CODE: round three, too patient]
```bash
MIN_ENDPOINTING_DELAY=1.5
MAX_ENDPOINTING_DELAY=5.0
```

Round three. The opposite. One and a half seconds minimum.

[DEMO: Same phrases. No interruptions, but a long, awkward silence after "Yes."]

No interruptions. But listen to the silence after "yes." [PAUSE] [PAUSE] It feels like the line dropped. That's the minimum delay applying even when the caller is obviously done.

[CODE: back to the defaults]
```bash
MIN_ENDPOINTING_DELAY=0.5
MAX_ENDPOINTING_DELAY=3.0
```

Back to the defaults. For most callers on a laptop, these are a good starting point. In Section eight, phones get a slightly longer minimum, because phone lines add their own delay.

[SCREEN: VS Code, `agents/my_hello_agent.py`. Expand the `TurnHandlingOptions` to include endpointing and interruption settings.]

Now interruptions. In my hello agent, I'll spell out the full turn handling options, the same way the reference file does, and add one new setting.

[CODE: update `turn_handling` in `my_hello_agent.py`]
```python
from livekit.agents import EndpointingOptions, InterruptionOptions

        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            endpointing=EndpointingOptions(
                min_delay=settings.min_endpointing_delay,
                max_delay=settings.max_endpointing_delay,
            ),
            interruption=InterruptionOptions(min_duration=0.5, min_words=2),
        ),
```

Endpointing now reads the two values from dot env, so the rounds we just did work in your file too. And for interruptions, I'm setting min words to two. Now a single "mm-hm" shouldn't stop Riley, but "wait, stop" should.

[DEMO: Ask Riley "What services do you offer?" While it answers, say "mm-hm". Riley keeps going. Ask again, and say "wait, stop" mid-answer. Riley stops and listens.]

"Mm-hm." Riley keeps going. [PAUSE] "Wait, stop." Riley stops. That's the behavior you want on a phone call.

Keep min words at two if you like it. It's a good default for phone calls, and you'll see it again in Section eight.

[SLIDE 2: Three tuning mistakes]
- A low `max_delay` that overrides the turn detector
- Changing several settings at once
- Tuning on speakers instead of headphones (echo looks like interruptions)

[AVATAR]
Three mistakes to avoid. A low maximum delay that overrides the turn detector. Changing several settings at once, so you can't tell what helped. And tuning with speakers instead of headphones, where Riley hears its own voice and "interrupts" itself.

**Recap:** Use the same three test phrases, change one setting at a time, and listen: `max_delay` protects pauses, `min_delay` sets snappiness, and `min_words` stops backchannels from interrupting.

**Transition:** Next is Lab 2, where you'll run these experiments yourself with your own voice, model and turn settings.

### Speaker notes: common student mistakes / Q&A

- Mistake: editing `.env` and not restarting console mode. Settings load at startup.
- Mistake: running your own `my_hello_agent.py` with hard-coded delays, then wondering why `.env` changes have no effect. Read them from `settings` as shown.
- "`min_words` did nothing." It needs STT words, so very short sounds may never produce a transcript. Combine it with `min_duration`.
- "Should I use dynamic endpointing?" Try `mode="dynamic"` for slow or elderly callers, and compare with the same phrases.

---

## Lecture 3.8 — Lab 2: Customise your first agent

| Field | Value |
|---|---|
| ID | 3.8 |
| Type | LAB (text lab with short video walkthrough) |
| Target duration | 4:00 total (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Change Riley's voice, LLM and turn-taking settings through `.env` without editing code. 2. Record structured before-and-after observations. |
| Prerequisites | 3.3 to 3.7, Lab 1 observations |
| Files used | `04-labs/lab-02-first-agent.md`, `03-code/.env`, `03-code/agents/s03_hello_agent.py` |

### Script

[AVATAR]
Your turn to tune Riley. This lab is about building an ear for voice agents, and that only comes from changing one thing at a time and listening.

[SCREEN: Open `04-labs/lab-02-first-agent.md`. Scroll through the three experiments.]

There are three experiments. Experiment one, the voice. Pick two voices from your TTS provider's library, set `TTS_VOICE` in your dot env, and have the same short conversation with each. Experiment two, the model. Try a second LLM model string and note whether replies get faster, slower, longer or shorter. Experiment three, turn-taking. Run the three test phrases from Lecture 3.7 with three endpointing settings: the default, a snappy one and a patient one.

[SCREEN: Scroll to the observation table: columns "Setting", "Felt latency (1-5)", "Interruptions", "Mishearings", "Notes".]

For each run, fill in one row of this table. Felt latency from one to five. How many times Riley cut you off. Anything it misheard. And a short note.

[SCREEN: Scroll to the "Compare with Lab 1" box.]

Finally, compare with your first impressions from Lab 1. What changed? What would you ship?

[AVATAR]
Two rules. Change one setting per run. And always restart the agent after editing dot env. At the end, put back the settings you liked best. We'll build on them in Section four.

**Recap:** Lab 2 has you swap voice, model and endpointing through `.env`, one change at a time, and record what you hear.

**Transition:** Next, you'll break your agent on purpose, five ways, so you can recognise each failure by ear.

### Speaker notes: common student mistakes / Q&A

- Students change three settings at once and can't tell which one helped. Enforce one change per run.
- A new `LLM_MODEL` string must be one LiveKit Inference supports. If you get a model error, check the LiveKit Inference model list or switch `MAPLE_PROVIDER_MODE=plugins` with your own key.
- Voice IDs are long identifiers. Copy them exactly from the provider's voice library.

---

## Lecture 3.9 — Break it: five ways your first agent fails, and what each sounds like

| Field | Value |
|---|---|
| ID | 3.9 |
| Type | DM (live demo with before/after audio) |
| Target duration | 7:00 (~550 spoken words, about 3:56 of talking at 140 wpm, plus recorded audio) |
| Learning objectives | 1. Recognise five common voice-agent failures by ear. 2. Pair each failure with the one setting that fixes it. 3. Use `BROKEN=<case>` toggles to reproduce failures on purpose for testing and demos. |
| Prerequisites | 3.6, 3.7 |
| Files used | `03-code/agents/s03_hello_agent.py` (reads `BROKEN=<case>`; see `broken_overrides()`) |

**Recording note:** record each "before" and "after" as a real console session with the same caller line, then cut them back to back. Keep the failures unedited. Toggle names below must match the code at recording time.

| `BROKEN=` case | What it changes (in `s03_hello_agent.py`) | Fix |
|---|---|---|
| `short_endpointing` | VAD-only turn detection, `EndpointingOptions(min_delay=0.05, max_delay=0.3)` | Turn detector on, `min_delay=0.5`, `max_delay=3.0` |
| `long_endpointing` | `EndpointingOptions(min_delay=2.5, max_delay=6.0)` | `min_delay=0.5` (or `mode="dynamic"`) |
| `no_interruptions` | `InterruptionOptions(enabled=False)` | Interruptions on, `min_words=2` for backchannels |
| `markdown` | markdown-demanding prompt line + `tts_text_transforms=None` | Voice output rules + default filters |
| `wrong_stt` | `stt="deepgram/nova-2"` (older, general model) | Current model (`deepgram/nova-3`); keyterms via `build_stt` from Section 4; phone tuning in Section 8 |

### Script

[AVATAR]
You've heard Riley work. Now let's break it. On purpose, five different ways. [PAUSE] Why? Because in production, you won't get a stack trace. You'll get a caller saying "it kept cutting me off" or "it said something weird." If you know what each failure sounds like, you can go straight to the right setting.

[SLIDE 1: How the toggles work]
```bash
BROKEN=short_endpointing uv run python agents/s03_hello_agent.py console
```
- Cases: `short_endpointing`, `long_endpointing`, `no_interruptions`, `markdown`, `wrong_stt`
- One environment variable, one failure
- No code edits, so "before" and "after" are identical except for the toggle
- You'll reuse these in Section 9 to prove your tests catch each failure

The reference hello agent, `s03_hello_agent.py`, has a built-in switch. Set BROKEN to a case name, and it deliberately misconfigures one thing. Leave it unset, and you get the healthy agent. Same code, same prompt, one variable.

[SCREEN: Terminal. Run `BROKEN=short_endpointing ...console`.]

Failure one. Endpointing too short.

[DEMO: Before. Caller: "My number is five one two... [pause] ...five five five..." Riley: "Thanks! And what's the rest of your..." Caller keeps talking over it.]

The caller pauses after the area code, and Riley pounces. Now they're talking over each other, and the transcript is split into fragments.

[DEMO: After, with `BROKEN` unset. Riley waits through the pauses and reads back the full number.]

The broken version turned off the semantic turn detector and used VAD silence alone, with a ceiling of three tenths of a second. Any breath ended the turn. The fix is the default: the turn detector on, half a second minimum, three seconds maximum.

[SCREEN: Terminal. `BROKEN=long_endpointing`.]

Failure two. Endpointing too long.

[DEMO: Before. Caller: "Yes." Two and a half seconds of silence. Caller: "Hello?" Riley starts answering at the same moment.]

The caller says "yes," and then nothing. [PAUSE] [PAUSE] The caller says "hello?" just as Riley starts talking. Now they collide. A long delay doesn't just feel slow. It causes talk-over too, because callers fill the silence.

[DEMO: After. "Yes." Riley replies promptly.]

The fix is a sensible minimum delay. If you have slow speakers, try dynamic endpointing rather than a big fixed number.

[SCREEN: Terminal. `BROKEN=no_interruptions`.]

Failure three. Interruptions disabled.

[DEMO: Before. Riley reads a long answer about services. Caller: "Sorry, I just need the hours." Riley keeps talking to the end.]

The caller tries to redirect. Riley ignores them and finishes its speech. Every caller has met this bot, and every caller hates it.

[DEMO: After. Caller says "Sorry, I just need the hours." Riley stops and answers the hours.]

The fix: interruptions on, with min words set to two, so "mm-hm" doesn't stop Riley but "sorry, I just need the hours" does. Keep "uninterruptible" for the few moments that truly need it, like committing a booking in Section five.

[SCREEN: Terminal. `BROKEN=markdown`.]

Failure four. The chat prompt, with the text filters turned off.

[DEMO: Before. Caller: "What are your hours?" Riley: "Here are our hours, asterisk asterisk Monday to Thursday asterisk asterisk, eight A M dash five P M..."]

Asterisk, asterisk. [PAUSE] This is what happens with a chatbot prompt and no safety net. The model writes markdown, and the voice reads the symbols.

[DEMO: After. "We're open eight to five Monday through Thursday, and eight to two on Fridays."]

Two fixes, in order. The voice output rules in the prompt, which you'll write in Section four. And the default text filters, which strip markdown and emojis before speech. The broken case had both removed.

[SCREEN: Terminal. `BROKEN=wrong_stt`.]

Failure five. The wrong speech-to-text model.

[DEMO: Before. Caller: "Do you take Delta Dental? I'm due for Invisalign." Transcript panel shows "Do you take delta dinner? I'm due for invisible line." Riley answers about the wrong thing.]

Look at the transcript. "Delta dinner." "Invisible line." Riley's answer is perfectly sensible, for the words it received. This is the failure people blame on the LLM, and it's not the LLM's fault at all.

[DEMO: After. Transcript shows "Delta Dental" and "Invisalign" correctly. Riley answers correctly.]

The broken case swapped in an older, general-purpose model. The fix is a current model suited to the audio. From Section four on, our build STT helper also adds keyterms: a list of dental terms and clinic names the model should listen for. Phone audio is harder still, and Section eight tunes for it. Section nine measures it with word error rate.

[SLIDE 2: Symptom → setting]
| What the caller says | Likely cause | First setting to check |
|---|---|---|
| "It kept cutting me off" | Endpointing too short | `max_delay`, turn detector on |
| "It was so slow to answer" | Endpointing too long | `min_delay` |
| "It wouldn't let me talk" | Interruptions off | `InterruptionOptions(enabled=True)` |
| "It said weird symbols" | Chat prompt, filters off | Output rules, `tts_text_transforms` |
| "It didn't understand me" | Wrong or outdated STT | STT model, keyterms; check the transcript first |

[AVATAR]
Here's the cheat sheet. Symptom, cause and the first setting to check. Screenshot it. When you get a complaint, start at the matching row, and always read the transcript before blaming the LLM.

**Recap:** Short endpointing cuts callers off, long endpointing causes awkward silences and collisions, disabled interruptions talk over callers, chat prompts make TTS read symbols, and mismatched STT mishears domain words, each with one setting to fix it.

**Transition:** Let's lock this in with a short quiz on your first agent and turn-taking.

### Speaker notes: common student mistakes / Q&A

- Mistake: leaving `BROKEN` set in the shell after the demo. Run `unset BROKEN` (macOS/Linux) or `Remove-Item Env:BROKEN` (PowerShell) and restart.
- "Is `short_endpointing` just a small `min_delay`?" It also switches turn detection to VAD only, so nothing reads the words. Lecture 3.7 shows how a low `max_delay` alone can override the turn detector.
- "Why keep broken modes in the repo?" In Section 9, a good test suite should fail when you set each `BROKEN` case. It's how you test your tests.
- The STT demo depends on the speaker's accent and mic. If your "before" recording transcribes correctly, add light background noise or use a phone speaker, and say so on screen.

---

## Lecture 3.10 — Quiz: First agent and turn-taking

| Field | Value |
|---|---|
| ID | 3.10 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~125 spoken words, about 0:54 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of dispatch, `AgentSession` vs `Agent`, and turn-taking settings. 2. Identify which lecture to revisit before adding prompts and tools. |
| Prerequisites | 3.1 to 3.9 |
| Files used | `06-assessments/quizzes/section-03.md` |

### Script

[AVATAR]
Five questions on your first agent. About three minutes.

[SLIDE 1: Section 3 quiz: what's covered]
- Rooms, participants, tracks and dispatch
- What belongs on `Agent` vs `AgentSession`
- `min_delay`, `max_delay` and the turn detector
- Interruptions and backchannels
- Matching a symptom to a setting

You'll see questions on dispatch, on where settings belong, on endpointing and the turn detector, on interruptions, and one that gives you a caller complaint and asks which setting to check first.

Tip: if you're torn on a turn-taking question, picture the timeline from Lecture 3.6. Where is the caller in the timeline, and which setting is the clock running on?

Every answer has an explanation. If you miss one, rewatch the lecture it points to. Section four builds on all of it.

**Recap:** The quiz checks dispatch, the two core classes and turn-taking settings.

**Transition:** Next, Section 4: why chat prompts fail on voice, and how to write prompts for the ear.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which setting overrides the turn detector?" Answer: a low `max_delay`.
- Second most missed: putting `instructions` on the session. They belong on `Agent`.
