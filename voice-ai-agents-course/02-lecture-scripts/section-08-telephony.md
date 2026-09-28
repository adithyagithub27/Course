# Section 8: Telephony: Put Riley on a Phone Number

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** about 57 minutes (8 lectures)
> **Running example:** Riley, the AI receptionist for Maple Street Dental
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. For phone demos, record the handset audio with a phone patch or a second laptop on speaker, and add on-screen captions.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Console-step warning (8.2, 8.5, on screen):** "Console menus change often. Verify each step in the current LiveKit Cloud and Twilio consoles; the repo README keeps the latest screenshots."

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run with audio · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (matched to `03-code/`):** `PhoneRiley` and `PHONE_RULES` (`agents/s08_telephony_agent.py`); `ReminderRiley`, `dispatch_call`, the `dispatch` sub-command (`agents/s08_outbound_call.py`); from `agents/common.py`: `CallState` (`caller_id_number`, `caller_phone`, `transfer_requested`, `call_outcome`, `notes`), `BookingToolsMixin`, `KnowledgeToolsMixin`, `TelephonyToolsMixin` (`transfer_to_human`, `end_call`), `find_sip_participant`, `caller_number`, `create_session`, `build_stt`, `build_turn_handling`, `DENTAL_KEYTERMS`, `get_settings`; settings `agent_name` (`LIVEKIT_AGENT_NAME`), `transfer_sip_uri` (`TRANSFER_PHONE_NUMBER`), `sip_outbound_trunk_id` (`SIP_OUTBOUND_TRUNK_ID`); prompt pieces `GREETING`, `REMINDER_CALL_EXTRA`, `speak_phone`. All phone numbers shown are fictional 555 numbers. On screen, every agent is "Riley".
---

## Lecture 8.1: PSTN, SIP and trunks in plain English

| Field | Value |
|---|---|
| ID | 8.1 |
| Title | PSTN, SIP and trunks in plain English |
| Type | SL (slides + avatar) |
| Target duration | 8:00 (about 900 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | A phone call reaches Riley through a chain: phone network, SIP trunk, LiveKit SIP, a room, and a dispatched agent; each link has a job and a failure mode. |
| Prerequisites | Section 3 (rooms, participants, dispatch) |
| Files used | None (conceptual). Diagram: "call path" (phone → Twilio → LiveKit SIP → room → agent). |

**Learning objectives**

1. Trace an inbound call from a caller's phone to Riley's `AgentSession`, naming each component.
2. Explain what a SIP trunk, an inbound trunk, an outbound trunk and a dispatch rule each do.
3. Describe why 8 kHz narrowband phone audio changes STT accuracy and endpointing.

### Script

[AVATAR]

Most of Maple Street Dental's patients will never open a web page to talk to Riley. They'll do what they've always done. Pick up a phone and dial. [PAUSE] So far, Riley has lived in your laptop's microphone and a browser tab. In this section she gets a real phone number. Before we touch a console, let's understand the path a call takes, because every telephony bug you'll ever debug lives on one link of this chain.

[SLIDE 1: The call path]
- Caller's phone → PSTN (the public phone network)
- PSTN → SIP trunk provider (Twilio Elastic SIP Trunking)
- Twilio → LiveKit SIP service (your project's SIP URI)
- LiveKit SIP → a new room with the caller as a SIP participant
- Dispatch rule → Riley's agent joins the room

[B-ROLL: animated call path. A phone icon rings; a line travels through a "PSTN" cloud, into a Twilio box, into a LiveKit box, into a "room" circle where a caller icon and a Riley icon appear.]

[AVATAR]

Here's the path. A caller dials the clinic's number. That call travels over the PSTN, the public switched telephone network. That's the same network your grandparents' landline used. It's run by carriers, and it speaks old telephone protocols.

Our software doesn't speak those. It speaks SIP, the Session Initiation Protocol, which is how internet phone systems set up calls. So we need a bridge. That bridge is a SIP trunk. Twilio owns the phone number, receives the call from the carrier, and forwards it over SIP to LiveKit.

LiveKit's SIP service receives it and does something very familiar. It creates a room, and puts the caller into it as a participant. A special kind of participant, a SIP participant, but still a participant with an audio track. [PAUSE] And then a dispatch rule tells LiveKit which agent to send into that room. Riley joins, exactly like she joins a browser room today.

That's the key insight of this whole section. From Riley's point of view, a phone caller is just another participant. Almost none of her code changes.

[SLIDE 2: Four things you'll configure]
- Twilio Elastic SIP trunk: owns the number; origination points to LiveKit, termination accepts calls from LiveKit
- LiveKit inbound trunk: "accept calls for +1 512 555 0100"
- LiveKit dispatch rule: "put each caller in a new room and dispatch riley-receptionist"
- LiveKit outbound trunk: "place calls through Twilio" (for reminders, lecture 8.5)

[AVATAR]

You'll configure four things. First, a Twilio Elastic SIP trunk. It owns the number. Its "origination" settings say where inbound calls go, which is LiveKit. Its "termination" settings let LiveKit place outbound calls through Twilio.

Second, a LiveKit inbound trunk. It tells LiveKit which numbers to accept calls for.

Third, a dispatch rule. It says what to do with each call: create a new room per caller, and dispatch the agent named `riley-receptionist`.

Fourth, for outbound calls, a LiveKit outbound trunk that points back at Twilio.

[SLIDE 3: Explicit dispatch and agent names]
- Browser rooms in dev: an unnamed agent is auto-dispatched to every room
- Telephony: a named agent (`riley-receptionist`) is dispatched only when asked
- Name comes from `LIVEKIT_AGENT_NAME` (dev) or `[agent] name` in `livekit.toml` (production)
- The dispatch rule and the outbound script both use this name

[AVATAR]

One idea from Section 3 becomes important now: agent names. In dev, Riley had no name, so LiveKit dispatched her into every room automatically. That's handy for a playground and dangerous for a phone system. With a name, like `riley-receptionist`, the agent is only dispatched when something asks for it by name. The dispatch rule asks for it. The outbound reminder script asks for it. Nothing else does. In LiveKit Agents 1.8, the name comes from the `LIVEKIT_AGENT_NAME` environment variable, or from the `[agent]` section of `livekit.toml` when you deploy.

[SLIDE 4: Phone audio is not laptop audio]
- Phone networks carry 8 kHz narrowband audio (G.711); your laptop mic gives 48 kHz
- Consonants blur: "fifteen" vs "fifty", "B" vs "D"
- Background noise: cars, kitchens, speakerphones
- Extra network delay: often 100 to 300 ms more round trip

[AVATAR]

Now the part that bites people. Phone audio is terrible. [PAUSE] A traditional phone call carries audio sampled at eight kilohertz. Your laptop mic records at forty-eight. The phone network throws away most of the high frequencies, and that's exactly where consonants live. "Fifteen" and "fifty" start to sound alike. So do "B" and "D." For a receptionist reading back appointment times, that's a real problem.

Callers also call from cars, kitchens and speakerphones. And the phone network adds its own delay, often a hundred to three hundred milliseconds of extra round trip on top of everything we've already budgeted.

[SLIDE 5: What this means for Riley]
- STT: pick a model that's strong on telephony audio; add keyterms (lecture 8.3, measured in 9.7)
- Turn-taking: slightly longer endpointing; callers pause more on phones
- Read-backs matter more: always confirm dates, times and numbers
- Latency budget: phone adds delay you can't remove, so save it elsewhere

[AVATAR]

So we'll tune for it. A speech-to-text model that's strong on phone audio, with a keyterm list for dental words and dentists' names. A slightly longer endpointing delay, because phone callers pause more. Read-backs become non-negotiable. And we'll protect the latency budget, because the phone network just spent some of it for us. Lecture 8.3 does all of that, and in Section 9 we'll measure it.

[SLIDE 6: Where calls fail]
- Twilio: number not attached to trunk, wrong origination URI
- LiveKit inbound trunk: number format wrong (must be E.164: +15125550100)
- Dispatch rule: agent name typo, so the caller hears silence
- Agent: not running, or running without the name set

[AVATAR]

Last slide, and keep it handy. When a test call fails, it fails at one of these links. Twilio rejects it because the number isn't attached to the trunk. LiveKit rejects it because the number isn't in E.164 format, which means plus, country code, then the number, with no spaces. The dispatch rule has a typo in the agent name, so the call connects and the caller hears nothing. Or the agent simply isn't running with its name set. Nine out of ten "my phone agent doesn't work" questions in the Q&A are one of these four.

[SLIDE 7: One inbound call, second by second]
- 0.0 s: caller dials; carrier routes to Twilio
- ~0.3 s: Twilio sends a SIP INVITE to your LiveKit SIP URI
- ~0.4 s: LiveKit matches the inbound trunk and the dispatch rule, creates room `call-...`
- ~0.5 s: `riley-receptionist` is dispatched; the job starts (faster with prewarmed processes)
- ~1 to 2 s: caller hears Riley's greeting
- Audio: G.711 at 8 kHz on the phone side; LiveKit converts for the agent

[AVATAR]

Here's the chain again, as a timeline, so you know what "fast" looks like. The caller dials. The carrier hands the call to Twilio. Twilio sends a SIP INVITE, which is SIP's way of saying "incoming call," to your LiveKit SIP address. LiveKit checks the number against your inbound trunk, applies the dispatch rule, creates a fresh room, and dispatches Riley. With prewarmed agent processes, that's all well under a second. Then Riley greets, and the caller hears her within a second or two of the call connecting.

On the audio side, the phone network typically uses a codec called G.711 at eight kilohertz. LiveKit converts it for the agent, so your code doesn't change. [PAUSE] But the audio quality is still eight kilohertz. Conversion doesn't bring back the frequencies the phone network threw away. That's why the tuning in lecture 8.3 matters.

[AVATAR]

A question from the Q&A: "Why not just use WebRTC in the browser and skip all this?" For many products you should. Web and app callers get wideband audio, no per-minute phone charges and simpler setup. But a dental clinic's patients call a phone number. So does almost every small business's. Meeting callers where they already are is the whole point of this section.

### Recap

A phone call reaches Riley through the phone network, a Twilio SIP trunk, LiveKit's SIP service, a room and a named-agent dispatch, and phone audio needs its own tuning.

### Transition

Next, we'll set up every link in that chain and make the first real call to Riley.

### Speaker notes: common mistakes and Q&A

- **"Do I need Twilio?"** No. Any SIP trunk provider works (Telnyx, Plivo, Vonage and others), and LiveKit also sells phone numbers directly in some regions. The course uses Twilio because its trial is easy to start.
- **"Why doesn't my agent join browser rooms anymore?"** Once `LIVEKIT_AGENT_NAME` is set, the agent needs explicit dispatch. Unset it for playground testing, or dispatch explicitly.
- **E.164 everywhere.** `+15125550100`, not `(512) 555-0100`, in trunks, dispatch rules and transfer targets.
- **Wideband calls exist** (HD voice, WebRTC callers), but design for 8 kHz; you can't control what the caller's carrier does.

---

## Lecture 8.2: Inbound calls: Twilio trunk + LiveKit dispatch rule

| Field | Value |
|---|---|
| ID | 8.2 |
| Title | Inbound calls: Twilio trunk + LiveKit dispatch rule |
| Type | SC (screencast code-along) |
| Target duration | 12:00 (about 970 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Four configuration steps and one environment variable put Riley on a real phone number. |
| Prerequisites | 8.1; `lk` CLI authenticated (lecture 2.3); Twilio account (trial is fine) |
| Files used | `livekit.toml.example`, `.env`, `telephony/inbound-trunk.json`, `telephony/dispatch-rule.json` (created in this lecture), `agents/s08_telephony_agent.py` |

**Learning objectives**

1. Buy a Twilio number and configure an Elastic SIP trunk whose origination points at your LiveKit SIP URI.
2. Create a LiveKit inbound trunk and a dispatch rule with the `lk` CLI that dispatches `riley-receptionist` into a new room per call.
3. Run the named agent and complete an inbound test call end to end.

### Script

[AVATAR]

By the end of this lecture, you'll dial a real phone number from your mobile and Riley will answer. [PAUSE] There are a few consoles involved, so I'll go step by step, and I'll tell you what each setting is for, so you can adapt when the screens change. And they do change. If a menu on your screen doesn't match mine, the repo README has the latest notes.

[SLIDE 1: The plan]
1. LiveKit: find your project's SIP URI
2. Twilio: buy a number, create an Elastic SIP trunk, point origination at LiveKit, attach the number
3. LiveKit: create an inbound trunk for that number (`lk sip inbound create`)
4. LiveKit: create a dispatch rule to `riley-receptionist` (`lk sip dispatch create`)
5. Run the named agent and call it

[SCREEN: LiveKit Cloud dashboard → project Settings. Highlight the "SIP URI" field. On-screen banner: "Verify in current LiveKit/Twilio console."]

Step one. In the LiveKit Cloud dashboard, open your project's settings. Find the SIP URI. It looks like `sip:` followed by a project-specific host ending in `sip.livekit.cloud`. Copy it. This is the address Twilio will send calls to.

[SCREEN: Twilio Console → Phone Numbers → Buy a number. Search a local area code, buy a voice-capable number.]

Step two, in Twilio. Buy a phone number with voice capability. On a trial account, you get one free, and you can only call it from numbers you've verified in Twilio. For this demo, my clinic number is plus one, five one two, five five five, zero one zero zero. Yours will be different.

[SCREEN: Twilio Console → Elastic SIP Trunking → Trunks → Create new SIP Trunk. Name it "maple-dental-livekit".]

Now create an Elastic SIP trunk. I'll call it `maple-dental-livekit`.

[SCREEN: Trunk → Origination → Add new Origination URI. Paste `sip:<your-project>.sip.livekit.cloud;transport=tcp`. Priority 10, weight 10.]

Open the trunk's Origination section. Origination is Twilio's word for "calls coming in from the phone network, going out to you." Add an origination URI: your LiveKit SIP URI, with `;transport=tcp` on the end. TCP is more reliable than UDP for SIP signaling across the internet.

[SCREEN: Trunk → Phone Numbers → Add an existing number → select the clinic number.]

Then open the trunk's Phone Numbers section and attach your number. [PAUSE] This is the step people forget. If the number isn't attached to the trunk, Twilio sends the call to its default voice webhook instead, and you'll hear a Twilio demo message, not Riley.

We'll configure Termination, the outbound direction, in lecture 8.5. For now, inbound is enough.

[SCREEN: VS Code. Create folder `telephony/` in the repo root. New file `telephony/inbound-trunk.json`.]

Step three, back in LiveKit. We'll use the `lk` CLI, because JSON files in your repo are easier to review and repeat than console clicks. Create `telephony/inbound-trunk.json`.

[CODE: `telephony/inbound-trunk.json`]

```json
{
  "trunk": {
    "name": "Maple Street Dental inbound",
    "numbers": ["+15125550100"],
    "krispEnabled": true
  }
}
```

Three fields. A name for humans. The numbers this trunk accepts, in E.164 format. And `krispEnabled`, which turns on LiveKit's noise cancellation for callers on this trunk. Phone callers in cars and kitchens will thank you.

[SCREEN: terminal]

```bash
lk sip inbound create telephony/inbound-trunk.json
```

[DEMO: CLI prints the new trunk with an ID starting `ST_`.]

The CLI prints the new trunk and its ID, which starts with `ST_`. Copy that ID.

Step four: the dispatch rule. Create `telephony/dispatch-rule.json`.

[CODE: `telephony/dispatch-rule.json`]

```json
{
  "dispatch_rule": {
    "name": "Riley inbound",
    "trunk_ids": ["ST_REPLACE_WITH_YOUR_TRUNK_ID"],
    "rule": {
      "dispatchRuleIndividual": {
        "roomPrefix": "call-"
      }
    },
    "roomConfig": {
      "agents": [
        { "agentName": "riley-receptionist" }
      ]
    }
  }
}
```

Let's read it. `trunk_ids` limits the rule to our inbound trunk. `dispatchRuleIndividual` means every caller gets their own brand-new room. The room names start with `call-`, so they're easy to spot in the dashboard. That matters. You never want two callers in the same room with Riley. And `roomConfig.agents` says which agent to dispatch into each new room: `riley-receptionist`.

```bash
lk sip dispatch create telephony/dispatch-rule.json
lk sip inbound list
lk sip dispatch list
```

[DEMO: both list commands show the trunk and rule.]

Create it, and list both to double-check. Trunk, number, rule, agent name. Everything is there.

Now the agent side. Two places carry the agent name. For local development, your `.env`.

[CODE: `.env` (add one line)]

```bash
LIVEKIT_AGENT_NAME=riley-receptionist
```

And for deployment, `livekit.toml`. Copy the example file.

[CODE: `livekit.toml.example` → `livekit.toml`]

```toml
[agent]
name = "riley-receptionist"
```

Why both? In LiveKit Agents 1.8, `dev` and `console` read the environment variable. The `livekit.toml` name is used when the agent runs in production, which we'll do in Section 12. Setting the name in the decorator is deprecated, so we don't.

Now the phone-ready agent file, `agents/s08_telephony_agent.py`. We'll dig into its phone-specific parts in the next two lectures, but let's read it once and run it.

[CODE: `agents/s08_telephony_agent.py` (imports trimmed)]

```python
PHONE_RULES = """\
Phone calls:
- Callers are on a phone line; audio may be noisy. If you are unsure what you heard, ask again.
- Before transferring, say one short sentence such as "I'm transferring you to the front desk now",
  then call transfer_to_human.
- When the caller is finished, say goodbye in one sentence, then call end_call."""


class PhoneRiley(BookingToolsMixin, KnowledgeToolsMixin, TelephonyToolsMixin, Agent):
    """Riley for phone calls."""

    def __init__(self, *, caller_id: str | None = None, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        caller_line = ""
        if caller_id:
            caller_line = (
                f"\nCaller ID shows {prompts.speak_phone(caller_id)}. Ask whether this is the best "
                "number to reach them instead of asking for a number from scratch."
            )
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today,
                booking=True,
                knowledge=True,
                extra=PHONE_RULES + caller_line,
            ),
        )

    async def on_enter(self) -> None:
        """Answer the phone immediately with the disclosure greeting."""
        self.session.say(prompts.GREETING)


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Wait for the caller, read caller ID, then start Riley."""
    settings = get_settings()
    caller_id = None
    if not ctx.is_fake_job():  # console mode has no real room or caller
        await ctx.connect()
        participant = await ctx.wait_for_participant()
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            caller_id = caller_number(participant)
            logger.info(
                "inbound call",
                extra={"trunk_number": participant.attributes.get("sip.trunkPhoneNumber")},
            )

    state = CallState(caller_id_number=caller_id)
    session = create_session(settings, proc=ctx.proc, userdata=state, telephony=True, max_tool_steps=5)
    await session.start(agent=PhoneRiley(caller_id=caller_id), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
```

This is the same Riley you've built all along, assembled from mixins. `BookingToolsMixin` from Section 5. `KnowledgeToolsMixin` from Section 7. And a new one, `TelephonyToolsMixin`, which adds `transfer_to_human` and `end_call`; we'll open it in lecture 8.4. `PHONE_RULES` adds three lines to her prompt: ask again when the line is unclear, announce a transfer before doing it, and say goodbye before hanging up.

`on_enter` answers immediately with the fixed greeting, AI disclosure included. On the phone, silence after pickup makes callers think the line is dead.

The entrypoint waits for the caller, reads caller ID, which is next lecture's topic, and builds the session with `create_session(..., telephony=True)`. That flag switches on the phone tuning we'll look at in 8.3.

Run it in dev mode. Not console. Console mode uses your laptop mic and never registers with LiveKit, so phone calls can't reach it.

```bash
uv run agents/s08_telephony_agent.py dev
```

[DEMO: terminal shows the agent registering with agent name `riley-receptionist`. Then pick up a mobile phone, dial the clinic number. Captions on screen. Riley: "Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?" Caller: "What time do you close on Friday?" Riley: "On Fridays we're open from eight until two in the afternoon." Hang up.]

Look at the log first: "registered worker," with our agent name. Now I'll call from my mobile.

[PAUSE]

There she is. On a real phone line. And she answered the Friday hours question from the FAQ, in one sentence.

[SCREEN: LiveKit Cloud dashboard → Sessions / Rooms. A room named `call-...` with two participants: a SIP participant and the agent.]

In the LiveKit dashboard, you can see the room the dispatch rule created. Its name starts with `call-`, and it has two participants: the SIP participant, which is me on my mobile, and Riley.

[AVATAR]

If your call didn't connect, go back to the last slide of lecture 8.1 and walk the chain in order. Number attached to the trunk. Origination URI correct. Number in E.164 on the inbound trunk. Agent name identical in the dispatch rule and your `.env`. Agent running in `dev`, not `console`.

[SLIDE 2: Debugging an inbound call, in order]
1. `lk sip inbound list`: is the number there, in E.164?
2. `lk sip dispatch list`: right trunk ID, right agent name?
3. Agent log: "registered worker" with `riley-receptionist`?
4. LiveKit dashboard: was a `call-...` room created?
5. Twilio call log: did the call reach the trunk, and what SIP response came back?

[AVATAR]

Here's the checklist I use when a test call fails, in order. Each step rules out one link in the chain. First, the inbound trunk: is the number there, in E.164? Second, the dispatch rule: does it point at the right trunk ID and the exact agent name? Third, the agent log: did the worker register with that name? Fourth, the LiveKit dashboard: was a `call-` room created at all? If yes, the phone side worked and the problem is dispatch or the agent. If no, the problem is before LiveKit. Fifth, Twilio's call log, which shows whether the call reached your trunk and what SIP response came back. [PAUSE] Five checks, about two minutes, and you'll find almost every inbound problem.

[AVATAR]

One more thing about the files we just created: they belong in version control, secrets removed. The inbound trunk and dispatch rule JSON are your phone system's configuration. When someone asks in six months "why do calls go to room names starting with call-?", the answer is in `telephony/dispatch-rule.json`, with a commit message. [PAUSE] Console clicks leave no history. Files do.

### Recap

A Twilio trunk pointed at your LiveKit SIP URI, an inbound trunk for the number, a dispatch rule to `riley-receptionist`, and `LIVEKIT_AGENT_NAME` in `.env` put Riley on a real phone line.

### Transition

It works, but it's tuned for a laptop microphone. Next, we'll tune Riley for real phone callers.

### Speaker notes: common mistakes and Q&A

- **Twilio demo message plays instead of Riley**: the number isn't attached to the Elastic SIP trunk (it's still on a voice webhook / TwiML app).
- **Call connects, then silence**: agent name mismatch between `dispatch-rule.json` and `LIVEKIT_AGENT_NAME`, or the agent is running in `console` mode. Check `lk sip dispatch list` and the "registered worker" log line.
- **Trial account restrictions**: Twilio trials only connect verified caller numbers and play a trial preamble. Upgrade before real users call.
- **JSON field names**: the `lk` CLI accepts the protobuf JSON field names shown here; if a newer CLI rejects a field, run `lk sip inbound create --help` and check the current LiveKit SIP docs. Verify in current LiveKit/Twilio console.

---

## Lecture 8.3: Phone-specific tuning

| Field | Value |
|---|---|
| ID | 8.3 |
| Title | Phone-specific tuning |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 660 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Phone callers need a phone-tuned STT with keyterms, a slightly longer endpointing delay, noise handling, and caller ID from SIP attributes. |
| Prerequisites | 8.2 |
| Files used | `agents/s08_telephony_agent.py` (`PhoneRiley`), `agents/common.py` (`build_stt`, `build_turn_handling`, `DENTAL_KEYTERMS`, `caller_number`, `find_sip_participant`, `create_session`) |

**Learning objectives**

1. Configure STT keyterms and a longer minimum endpointing delay for phone audio.
2. Read the caller's number from the SIP participant's `sip.phoneNumber` attribute and store it in `CallState`.
3. Use caller ID to confirm rather than ask for the callback number.

### Script

[AVATAR]

On my first real test call, I said "I'd like to see Doctor Alvarez." [PAUSE] Riley heard "doctor all the rest." Then she asked for my phone number, which she already had, because I was calling from it. Two small things. Together they make an AI receptionist feel like a phone tree. Let's fix both.

[SCREEN: `agents/common.py`, scroll to `DENTAL_KEYTERMS` and `build_stt`.]

First, hearing. Open `agents/common.py`. At the top there's a list called `DENTAL_KEYTERMS`: the clinic's name, the dentists' names, words like "hygienist" and "Invisalign," drug names like "amoxicillin," and insurance names like "Delta Dental."

[CODE: `agents/common.py`, `build_stt` (highlight, don't type)]

```python
def build_stt(settings: Settings, *, telephony: bool = False) -> Any:
    provider, model = split_model(settings.stt_model)
    if settings.provider_mode == "plugins":
        ...
    if provider == "deepgram":
        return inference.STT(
            model=settings.stt_model,
            language=settings.language,
            extra_kwargs={"keyterm": DENTAL_KEYTERMS, "smart_format": True},
        )
    return settings.stt_model_with_language
```

For Deepgram models, `build_stt` passes that list as keyterms. Keyterm prompting tells Deepgram's Nova-3 model to expect these words, so "Doctor Alvarez" stops becoming "doctor all the rest." It's the single cheapest accuracy win on a phone line. In lecture 9.7 we'll measure it with word error rate, before and after. Notice the `telephony` flag doesn't change the model: Nova-3 handles eight-kilohertz phone audio well on its own.

If you want to try a model trained specifically on phone calls, it's one environment variable. LiveKit Inference lists `deepgram/nova-2-phonecall`, for example. But don't switch on vibes. Switch when your WER numbers in Section 9 say so.

[CODE: `agents/common.py`, `build_turn_handling` (highlight)]

```python
def build_turn_handling(settings: Settings, *, telephony: bool = False) -> TurnHandlingOptions:
    min_delay = max(settings.min_endpointing_delay, 0.7) if telephony else settings.min_endpointing_delay
    return TurnHandlingOptions(
        turn_detection=inference.TurnDetector(),
        endpointing=EndpointingOptions(min_delay=min_delay, max_delay=settings.max_endpointing_delay),
        interruption=InterruptionOptions(
            min_duration=0.5,
            resume_false_interruption=True,
            false_interruption_timeout=1.5,
        ),
    )
```

Second, turn-taking. `create_session(..., telephony=True)` passes the flag through, and with it, the minimum endpointing delay goes from half a second to at least seven hundred milliseconds. Phone callers pause more, often because they're reading a card or checking a calendar. That extra two hundred milliseconds stops Riley from jumping in mid-thought. It costs us two hundred milliseconds of latency on every turn, which is why we don't do it for browser callers.

Interruptions stay on, with `resume_false_interruption=True`. On a phone line, a cough or a car horn can look like an interruption. If the caller doesn't actually say anything within one and a half seconds, Riley picks up where she left off instead of going silent.

Noise is the third piece. We already turned on Krisp noise cancellation on the inbound trunk in the last lecture, so the audio is cleaned before it reaches the agent.

Now caller ID.

[CODE: `agents/common.py`, caller ID helpers (highlight)]

```python
def find_sip_participant(room: rtc.Room) -> rtc.RemoteParticipant | None:
    """Return the first SIP (phone) participant in the room, if any."""
    for participant in room.remote_participants.values():
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            return participant
    return None


def caller_number(participant: rtc.RemoteParticipant | None) -> str | None:
    """Caller ID from SIP participant attributes (``sip.phoneNumber``)."""
    if participant is None:
        return None
    return participant.attributes.get("sip.phoneNumber") or None
```

A SIP participant carries attributes set by LiveKit. `sip.phoneNumber` is the caller's number. There are others, like `sip.trunkPhoneNumber`, the number they dialed, which is handy if one agent answers several clinic lines.

[CODE: `agents/s08_telephony_agent.py`, the caller ID path (highlight)]

```python
    caller_id = None
    if not ctx.is_fake_job():  # console mode has no real room or caller
        await ctx.connect()
        participant = await ctx.wait_for_participant()
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            caller_id = caller_number(participant)
            logger.info(
                "inbound call",
                extra={"trunk_number": participant.attributes.get("sip.trunkPhoneNumber")},
            )

    state = CallState(caller_id_number=caller_id)
```

```python
        caller_line = ""
        if caller_id:
            caller_line = (
                f"\nCaller ID shows {prompts.speak_phone(caller_id)}. Ask whether this is the best "
                "number to reach them instead of asking for a number from scratch."
            )
```

In the entrypoint, we connect, wait for the first participant, and if it's a SIP participant, read the number. In console mode there's no real room, so `is_fake_job()` skips all of this. We store the number in `CallState`, so tools can use it, and pass it to `PhoneRiley`. Her constructor turns it into one extra prompt line, spoken the way a person reads a number, with `speak_phone` from Section 4: "Ask whether this is the best number to reach them." [PAUSE] One question instead of ten digits read aloud over a noisy line. That's faster, and it removes a whole class of transcription errors.

Run it and call again.

```bash
uv run agents/s08_telephony_agent.py dev
```

[DEMO: call from mobile. "Hi, I'd like to book a cleaning with Doctor Alvarez next Thursday." Riley repeats "Doctor Alvarez" correctly. When she needs a number: "Is the number you're calling from, the one ending in zero one four two, the best one to reach you?" Caller: "Yes." Booking completes.]

"Doctor Alvarez," heard correctly. And instead of asking for my number, she asked if the one I'm calling from is best. One word, "yes," and we're done.

[AVATAR]

A caller's number is personal data. It's now in your prompt, which means it's in your LLM provider's logs and in your traces. That's fine for a clinic that already has your number, but it's a deliberate decision. We'll come back to redacting it in logs in Section 11.

[AVATAR]

A quick word on how to know your tuning worked, because "it sounds better" isn't evidence. Make five test calls before the change and five after, from a real phone, ideally from a car or a noisy room. Listen for three things: did Riley cut you off while you read a number, did she mishear a name, and did she ask for information she already had? Then, in Section 9, we'll replace this listening with numbers: word error rate for the ears, and the end-of-utterance delay budget for turn-taking. [PAUSE] Tuning without measuring is guessing. For now, your ears are the measuring tool.

### Recap

Keyterms, a slightly longer endpointing delay, trunk-level noise cancellation, and caller ID from `sip.phoneNumber` make Riley sound built for the phone.

### Transition

Next: the two tools every phone agent needs, handing a caller to a human and hanging up cleanly.

### Speaker notes: common mistakes and Q&A

- **Caller ID is `None`**: calls from blocked or withheld numbers, and browser test rooms, have no `sip.phoneNumber`. Always handle `None`.
- **Keyterms not applied**: `MAPLE_PROVIDER_MODE=plugins` with a non-Deepgram STT, or a custom STT string. Keyterms are provider-specific.
- **Too-long endpointing**: pushing `min_delay` past about 1.0 seconds makes Riley feel slow. Measure in 9.8 before raising it.
- **Treating caller ID as identity**: numbers can be spoofed. Caller ID can pre-fill a callback number, but it isn't verification. Section 11 adds `verify_caller`.

---

## Lecture 8.4: Transfer to a human and ending calls

| Field | Value |
|---|---|
| ID | 8.4 |
| Title | Transfer to a human and ending calls |
| Type | SC (screencast code-along) |
| Target duration | 9:00 (about 890 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | A phone agent must know when to hand a caller to a person and how to hang up, and both tools must fail safely. |
| Prerequisites | 8.2, 8.3; a second phone number to receive transfers; call transfer enabled on the Twilio trunk |
| Files used | `agents/common.py` (`TelephonyToolsMixin`), `agents/s08_telephony_agent.py`, `.env` (`TRANSFER_PHONE_NUMBER`) |

**Learning objectives**

1. Implement `transfer_to_human` with `get_job_context().transfer_sip_participant(...)`, including a spoken announcement and a safe fallback.
2. Explain cold versus warm transfer and when each fits a clinic.
3. Implement `end_call` so Riley says goodbye before disconnecting everyone.

### Script

[AVATAR]

Every AI phone agent needs an exit. A caller who's upset about a bill. A caller who just wants a person. A caller Riley has failed twice. [PAUSE] If Riley can't hand them to a human, you haven't built a receptionist. You've built a trap. So in this lecture we build two tools: `transfer_to_human` and `end_call`.

[SLIDE 1: Cold vs warm transfer]
- Cold (blind) transfer: agent announces, then hands the call over; the human starts fresh
- Warm transfer: agent puts caller on hold, briefs the human, then connects them
- Cold: simple, one API call, SIP REFER on the trunk
- Warm: better experience, more moving parts (LiveKit ships a beta `WarmTransferTask`)

[AVATAR]

Two kinds of transfer. A cold transfer is what most phone systems do. Riley says "I'm transferring you now," and the call is handed to the front desk number. The human picks up with no context. It's one API call.

A warm transfer is what a great human receptionist does. Put the caller on hold, call the colleague, say "I've got Priya, she's asking about a charge on her last visit," and then connect them. It's a better experience with more moving parts. LiveKit Agents 1.8 includes a beta building block for it called `WarmTransferTask`. We'll build the cold transfer here, because it's what most clinics need first.

[SCREEN: Twilio Console → Elastic SIP Trunking → your trunk → General. Enable "Call Transfer (SIP REFER)". Banner: "Verify in current LiveKit/Twilio console."]

One console step first. A cold transfer uses a SIP message called REFER, which asks Twilio to move the call. Twilio only honors it if call transfer is enabled on the trunk. In your trunk's general settings, turn on call transfer. If you're transferring to a regular phone number, also allow transfers to the PSTN. Without this, the transfer fails silently and the caller stays with Riley.

[CODE: `.env` (add)]

```bash
TRANSFER_PHONE_NUMBER=+15125550111
```

Then tell Riley where to transfer. That's the front desk's number, in E.164. `get_settings()` turns it into a `tel:` URI for us, as `settings.transfer_sip_uri`.

[SCREEN: `agents/common.py`, scroll to `class TelephonyToolsMixin`.]

Now the tool. It lives in `agents/common.py`, in `TelephonyToolsMixin`, so the capstone can reuse it. Let's build it up.

[CODE: `transfer_to_human`, step 1: signature and docstring]

```python
class TelephonyToolsMixin:
    """Adds ``transfer_to_human`` and ``end_call``."""

    @function_tool
    async def transfer_to_human(self, context: RunContext[CallState], reason: str) -> str:
        """Transfer the caller to a person at the front desk. Before calling this, tell the
        caller you are transferring them.

        Args:
            reason: One short sentence for the staff member explaining why.
        """
```

The docstring does two jobs. It tells the model what the tool does. And it tells the model to announce the transfer first. The `reason` argument forces the model to say why, in one sentence. We store it, so the front desk dashboard and our tests can see it.

When does Riley use it? That's in her prompt already, in the `ESCALATION_RULES` block from `prompts.py`: offer a human if the caller asks for one, is upset, has a billing dispute, or Riley has failed twice. And transfer immediately, without arguing, if they ask a second time.

[CODE: step 2: guard rails]

```python
        settings = get_settings()
        state = context.userdata
        state.transfer_requested = True
        state.notes.append(f"transfer: {reason}")
        job_ctx = get_job_context(required=False)
        caller = find_sip_participant(job_ctx.room) if job_ctx is not None else None
        if job_ctx is None or caller is None or not settings.transfer_sip_uri:
            state.call_outcome = "transfer_unavailable"
            raise ToolError(
                "Transfers aren't available on this line. Apologize and offer to take a message "
                "so the front desk can call back."
            )
```

Before we transfer anything, three checks. Is there a job context at all? In a test, there isn't. Is there a phone caller in the room? In a browser session, there isn't. Is a transfer number configured? If any answer is no, we raise a `ToolError` with a speakable instruction: apologize and offer to take a message. [PAUSE] The failure path is part of the feature. A transfer tool that crashes leaves the caller in silence, which is the worst possible outcome.

[CODE: step 3: announce, transfer, handle failure]

```python
        await context.wait_for_playout()  # let "I'm transferring you now" finish first
        try:
            await job_ctx.transfer_sip_participant(caller, settings.transfer_sip_uri)
        except Exception as exc:  # SIP errors surface as API errors
            logger.exception("transfer failed")
            state.call_outcome = "transfer_failed"
            raise ToolError("The transfer didn't go through. Apologize and offer to take a message.") from exc
        state.call_outcome = "transferred"
        return "The caller has been transferred."
```

`context.wait_for_playout()` waits for whatever Riley said just before calling this tool, like "Of course, I'm transferring you to the front desk now," to finish playing. Without it, the transfer can cut her off mid-sentence.

Then the one line that does the work: `transfer_sip_participant`, with the caller and the `tel:` URI. It returns once the phone system accepts the transfer. If it fails, say because REFER isn't enabled, we log it, record the outcome, and give Riley a speakable fallback.

Now `end_call`.

[CODE: `end_call`]

```python
    @function_tool
    async def end_call(self, context: RunContext[CallState]) -> None:
        """Hang up. Only call this after you have said goodbye and the caller has nothing else."""
        state = context.userdata
        if state.call_outcome == "in_progress":
            state.call_outcome = "completed"
        await context.wait_for_playout()  # let the goodbye finish
        job_ctx = get_job_context(required=False)
        if job_ctx is None or job_ctx.is_fake_job():
            context.session.shutdown()
            return None
        # Deleting the room disconnects everyone, including the SIP caller.
        await job_ctx.delete_room()
        return None
```

Why does Riley need a hang-up tool at all? Because on a phone, if the agent never hangs up, the line stays open. You pay per minute for silence, and the caller hears nothing until they give up.

The pattern is the same. Say goodbye, wait for playout, then act. Deleting the room disconnects every participant, including the SIP caller, which ends the phone call. In console mode or tests there's no room to delete, so we just shut the session down. We also record the call outcome. That field becomes one of our dashboard metrics in Section 10.

LiveKit also ships a ready-made `EndCallTool` in `livekit.agents.beta`. It's a good option. We wrote our own so you can see exactly what happens and set the outcome field.

[SCREEN: `agents/s08_telephony_agent.py`; the class line already includes `TelephonyToolsMixin`, and `PHONE_RULES` tells Riley to announce transfers and say goodbye first.]

`PhoneRiley` already inherits both tools through `TelephonyToolsMixin`, and her `PHONE_RULES` tell her to announce a transfer and say goodbye before acting. Let's test.

```bash
uv run agents/s08_telephony_agent.py dev
```

[DEMO: call Riley. "I have a question about a charge on my bill, can I talk to someone?" Riley: "Of course. I'm transferring you to a member of our front desk team now." A second phone (the front desk) rings; answer it. Split-screen captions. Then a second call: book nothing, say "That's all, thanks, bye." Riley: "Thanks for calling Maple Street Dental. Have a great day. Goodbye." Call ends; dashboard shows the room closed.]

"Can I talk to someone about a charge on my bill?" Riley announces the transfer, and there's the front desk phone ringing. [PAUSE] Second call. "That's all, thanks, bye." Riley says goodbye, and the line drops. In the dashboard, the room is gone.

[AVATAR]

One more production habit. Test the failure path on purpose. Unset `TRANSFER_PHONE_NUMBER`, call, and ask for a human. Riley should apologize and offer to take a message. If she goes silent instead, your caller would too.

[SLIDE 2: When to upgrade to a warm transfer]
- Callers complain about repeating themselves to staff
- Transfers are for complex issues (billing disputes, clinical questions)
- Staff are busy: the agent can hold, brief and connect when someone's free
- Building block: `WarmTransferTask` (beta) in `livekit.agents.beta.workflows`

[AVATAR]

When is it worth moving from cold to warm transfers? When callers complain about repeating themselves. When transfers are mostly complex issues, like billing disputes, where a thirty-second briefing saves five minutes of the staff member's time. And when staff are busy, so the agent can keep the caller company on hold instead of dropping them into a ringing line.

A warm transfer has more moving parts: put the caller on hold, dial the staff member into a separate conversation, summarise the call for them, then connect the two and leave. LiveKit Agents 1.8 ships a beta building block for this, `WarmTransferTask`, in `livekit.agents.beta.workflows`. It's beta, so check its current API before you build on it. [PAUSE] For most clinics, a cold transfer with a clear reason logged in `CallState` is the right first step.

### Recap

`transfer_to_human` announces, waits for playout, calls `transfer_sip_participant` and falls back to a message, and `end_call` says goodbye before deleting the room.

### Transition

So far callers have called Riley. Next, Riley calls them, with appointment reminder calls.

### Speaker notes: common mistakes and Q&A

- **Transfer fails with a SIP error**: call transfer (SIP REFER) isn't enabled on the Twilio trunk, or PSTN transfer isn't allowed. Verify in current LiveKit/Twilio console.
- **Riley is cut off mid-announcement**: `context.wait_for_playout()` missing before the transfer or hang-up.
- **Awaiting `session.say(...)` inside the tool**: can deadlock because the tool's own speech is still in progress. Tell the model to announce first (docstring) and use `context.wait_for_playout()`.
- **Transfer to a transfer**: never set `TRANSFER_PHONE_NUMBER` to the same number Riley answers, or calls loop.

---

## Lecture 8.5: Outbound calls: appointment reminders

| Field | Value |
|---|---|
| ID | 8.5 |
| Title | Outbound calls: appointment reminders |
| Type | SC (screencast code-along) |
| Target duration | 10:00 (about 910 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | An outbound call is an explicit dispatch with metadata, then a `CreateSIPParticipantRequest` that dials the patient into the agent's room. |
| Prerequisites | 8.2 to 8.4; Twilio trunk termination configured |
| Files used | `agents/s08_outbound_call.py` (`ReminderRiley`, `dispatch` sub-command), `telephony/outbound-trunk.json`, `.env` (`SIP_OUTBOUND_TRUNK_ID`) |

**Learning objectives**

1. Configure Twilio termination and a LiveKit outbound trunk with the `lk` CLI.
2. Place a reminder call: explicitly dispatch a named agent with `CreateAgentDispatchRequest` metadata, then dial with `CreateSIPParticipantRequest(wait_until_answered=True)`.
3. Handle failed and unanswered calls, and know when answering-machine detection helps.

### Script

[AVATAR]

Maple Street Dental loses about one appointment in ten to no-shows. Each empty chair costs them around a hundred and fifty dollars. [PAUSE] A reminder call the day before cuts that. Today, Riley makes those calls.

[SLIDE 1: How an outbound call works]
1. A script asks LiveKit to dispatch a named agent into a new room, with metadata: who to call
2. The agent starts in that room and reads `ctx.job.metadata`
3. The agent asks LiveKit SIP to dial the patient into its room (`CreateSIPParticipantRequest`)
4. The patient answers → they're a participant → conversation as usual

[AVATAR]

Outbound is inbound in reverse. Instead of a dispatch rule creating a room when someone calls, a small script creates the dispatch itself. It gives the agent's job some metadata: the phone number and the patient's name. The agent starts, reads that metadata, and asks LiveKit's SIP service to dial the patient into its own room. When they pick up, they're a participant, and Riley talks to them like any caller.

[SCREEN: Twilio Console → your trunk → Termination. Set a Termination SIP URI like `maple-dental.pstn.twilio.com`. Under Authentication, create a Credential List with a username and strong password. Banner: "Verify in current LiveKit/Twilio console."]

First, Twilio. Open your trunk's Termination section. Termination is Twilio's word for "calls coming from you, going out to the phone network." Pick a termination SIP URI. Mine is `maple-dental.pstn.twilio.com`. Then add a credential list: a username and a strong password. LiveKit will use those to authenticate.

[CODE: `telephony/outbound-trunk.json`]

```json
{
  "trunk": {
    "name": "Maple Street Dental outbound",
    "address": "maple-dental.pstn.twilio.com",
    "numbers": ["+15125550100"],
    "authUsername": "riley-outbound",
    "authPassword": "REPLACE_WITH_THE_TWILIO_CREDENTIAL_PASSWORD"
  }
}
```

Now the LiveKit side. The outbound trunk points at Twilio's termination address. `numbers` is the caller ID the patient will see, which should be the clinic's own number, so they recognize it. And the credentials match the Twilio credential list. Don't commit the real password. Keep this file out of git, or template it from your secrets.

```bash
lk sip outbound create telephony/outbound-trunk.json
```

[DEMO: CLI prints the outbound trunk ID, starting `ST_`.]

Copy the trunk ID into `.env`.

```bash
SIP_OUTBOUND_TRUNK_ID=ST_REPLACE_WITH_YOUR_OUTBOUND_TRUNK_ID
```

[SCREEN: `agents/s08_outbound_call.py`]

Now open `agents/s08_outbound_call.py`. It has two halves: the agent, and a small dispatcher you run from the command line. Let's start with the dispatcher.

[CODE: the dispatcher]

```python
async def dispatch_call(agent_name: str, to: str, name: str) -> str:
    """Create an explicit agent dispatch in a fresh room. Returns the room name."""
    room = f"reminder-{uuid.uuid4().hex[:8]}"
    lkapi = api.LiveKitAPI()  # reads LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
    try:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room,
                metadata=json.dumps({"phone_number": to, "patient_name": name}),
            )
        )
        logger.info("created dispatch %s in room %s", dispatch.id, room)
    finally:
        await lkapi.aclose()
    return room
```

`api.LiveKitAPI()` reads your LiveKit URL and keys from the environment. We make a unique room name that starts with `reminder-`. Then `create_dispatch` with a `CreateAgentDispatchRequest`: the agent's name, the room, and the metadata as a JSON string, with the phone number and the patient's name. That's explicit dispatch. It starts one job for that agent, in that room. The rest of the file wires this function to a `dispatch` sub-command with `--to`, `--name` and `--agent-name` flags.

Now the agent. First, the reminder persona.

[CODE: `ReminderRiley`]

```python
class ReminderRiley(BookingToolsMixin, TelephonyToolsMixin, Agent):
    """Riley placing a reminder call about one appointment."""

    def __init__(self, *, patient_name: str, appointment_summary: str) -> None:
        self.scheduler = get_scheduler()
        context = (
            f"\nYou are calling {patient_name} about this appointment: {appointment_summary}."
        )
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today,
                booking=True,
                extra=prompts.REMINDER_CALL_EXTRA + context,
            ),
        )
```

`ReminderRiley` has the booking tools, so a patient can reschedule on the spot, and the telephony tools, so she can hang up or transfer. Her prompt adds `REMINDER_CALL_EXTRA` from `prompts.py`. It says: this is an outbound call you placed, say who you are and why you're calling in the first sentence, confirm the appointment, help them reschedule if needed, and if you reach voicemail, leave a short message with the day, time and clinic number, then end the call. The appointment itself is looked up from the scheduler by phone number, so the metadata only carries a number and a name, never medical details.

[CODE: the entrypoint]

```python
@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Dial the patient from dispatch metadata, then start the reminder conversation."""
    settings = get_settings()
    meta = parse_metadata(ctx.job.metadata)
    phone = meta.get("phone_number", "")
    patient = meta.get("patient_name", "the patient")

    agent = ReminderRiley(patient_name=patient, appointment_summary=appointment_summary(phone))
    session = create_session(settings, proc=ctx.proc, userdata=CallState(caller_phone=phone), telephony=True)

    if not phone:  # console / playground test: no call to place
        await session.start(agent=agent, room=ctx.room)
        await session.generate_reply(instructions="Start the reminder call.")
        return
    if not settings.sip_outbound_trunk_id:
        logger.error("SIP_OUTBOUND_TRUNK_ID is not set; cannot place outbound calls")
        ctx.shutdown(reason="missing outbound trunk")
        return

    # Start the session first so Riley is listening the moment the patient answers.
    await session.start(agent=agent, room=ctx.room)
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=settings.sip_outbound_trunk_id,
                sip_call_to=phone,
                participant_identity=f"patient-{normalize_phone(phone)}",
                participant_name=patient,
                wait_until_answered=True,
            )
        )
    except api.TwirpError as exc:
        logger.error(
            "outbound call failed: %s (SIP status %s)",
            exc.message,
            exc.metadata.get("sip_status_code"),
        )
        ctx.shutdown(reason="outbound call failed")
        return
    # Answered. Let the patient say "hello" first on real calls; this nudge speaks
    # first if they stay silent. Voicemail handling is described in the prompt.
    await session.generate_reply(instructions="The patient answered. Introduce yourself and the reason for the call.")
```

Let's walk through it. The entrypoint reads `ctx.job.metadata`, the JSON the dispatcher sent, and builds `ReminderRiley` with the patient's name and appointment. If there's no phone number, we're in console or playground testing, so it just starts the conversation. If there's no outbound trunk configured, it logs a clear error and shuts down.

Then the order matters. We start the session first, so Riley is already listening when the patient answers. Then `ctx.api.sip.create_sip_participant` with a `CreateSIPParticipantRequest`: our room, our outbound trunk, the number to call, an identity for the patient, and `wait_until_answered=True`, which means this line doesn't return until they pick up or the call fails.

If it fails, LiveKit raises a `TwirpError`. The SIP status code tells you why: four eighty-six means busy, four eighty means unavailable or no answer. We log it and shut the job down, so Riley isn't left alone in an empty room.

Once answered, a short `generate_reply` has Riley introduce herself and the reason for the call. [PAUSE] There's a shortcut you'll see in LiveKit's docs: `ctx.add_sip_participant(call_to=..., trunk_id=..., participant_identity=...)`. It sends the same request, but it doesn't wait for an answer, so we use the API directly here.

Let's call my own mobile. On a Twilio trial, the destination must be a verified number. The reminder worker runs under its own agent name, so it can't be confused with the inbound receptionist.

[SCREEN: terminal, two panes]

```bash
# pane 1: the reminder agent worker
LIVEKIT_AGENT_NAME=riley-outbound uv run agents/s08_outbound_call.py dev

# pane 2: place the call
uv run agents/s08_outbound_call.py dispatch --agent-name riley-outbound \
    --to +15125550142 --name "Jordan Lee"
```

[DEMO: pane 2 prints "Dispatched riley-outbound to room reminder-...; the agent will dial +15125550142." The phone rings. Answer: "Hello?" Riley: "Hi, this is Riley, the AI assistant from Maple Street Dental, calling to remind Jordan Lee about a cleaning on Tuesday at ten in the morning. Will you be able to make it?" Answer: "Actually, can we move it to Wednesday?" Riley calls `find_available_slots`, reads back a new time, and calls `reschedule_appointment` after a yes. Then a second dispatch that goes to voicemail: Riley leaves a short message and calls `end_call`.]

The phone rings. I answer, and Riley introduces herself as an AI assistant, says why she's calling, names the appointment from the demo calendar, and asks one question. I ask to move it. She uses the same `find_available_slots` and `reschedule_appointment` tools as inbound calls. And on the second call, which goes to voicemail, she leaves a short message and hangs up.

[SLIDE 2: Answering machines and failed calls]
- Voicemail picks up a large share of reminder calls
- Prompt-level handling: recognise a greeting, leave a 15-second message, `end_call`
- LiveKit Agents 1.8 also includes `AMD` (answering-machine detection): start it before dialing so it hears the first words
- Retry policy: no answer → retry once, later in the day; never loop

[AVATAR]

Now the messy part. Many reminder calls reach voicemail. Riley's prompt already handles the simple case. For higher volumes, LiveKit Agents 1.8 includes an answering-machine detection helper, `AMD`, which classifies the greeting as a human, a voicemail or a phone menu. Start it before you dial, so it hears the first words. And whatever you do, retry at most once, later in the day. A system that redials an unanswered number five times in an hour is exactly what the rules in the next lecture are designed to stop.

[AVATAR]

One design decision worth pointing out. We run the reminder agent as a separate worker, with its own agent name, `riley-outbound`, instead of adding reminder logic to the inbound receptionist. That keeps each agent simple, it means a bug in reminder calls can never affect inbound callers, and it lets you scale them separately: inbound needs capacity at nine in the morning, reminders can run in a quiet afternoon batch. [PAUSE] In production, the `dispatch` step usually isn't a person at a terminal. It's a scheduled job that reads tomorrow's appointments, checks consent and do-not-call lists, and dispatches one reminder per patient, a few at a time.

### Recap

An outbound call is an explicit dispatch with metadata, then `CreateSIPParticipantRequest(wait_until_answered=True)` from the agent's own room, with `ReminderRiley` reading `ctx.job.metadata` to know who she's calling and why.

### Transition

Riley can now call real people. Before she does, let's talk about the rules: disclosure, consent and recording.

### Speaker notes: common mistakes and Q&A

- **`TwirpError` immediately**: wrong `SIP_OUTBOUND_TRUNK_ID`, bad Twilio credentials, or the destination isn't verified on a Twilio trial. Verify in current LiveKit/Twilio console.
- **Nothing happens after `dispatch`**: the worker's `LIVEKIT_AGENT_NAME` doesn't match `--agent-name`. Explicit dispatch needs an exact match.
- **Riley talks over "Hello?"**: on real calls, let the callee speak first; keep the post-answer nudge short.
- **Reminder data in metadata**: metadata is visible to anyone who can read the room. Send a phone number and a name, never medical details; look the rest up server-side.
- **Consent**: only call numbers that agreed to reminder calls (lecture 8.6).

---

## Lecture 8.6: Compliance: disclosure, consent and recording

| Field | Value |
|---|---|
| ID | 8.6 |
| Title | Compliance: disclosure, consent and recording |
| Type | TH (talking head / avatar) |
| Target duration | 6:00 (about 650 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Before a voice agent takes or places real calls, check five compliance areas: AI disclosure, recording consent, outbound calling rules, do-not-call, and data retention. This is not legal advice. |
| Prerequisites | 8.2 to 8.5 |
| Files used | `10-resources/telephony-compliance-checklist.md` |

**Learning objectives**

1. Name the five compliance areas that apply to AI phone agents and where each shows up in Riley's design.
2. Distinguish one-party and two-party (all-party) recording consent and apply the safe default.
3. Explain why outbound AI calls face stricter rules (TCPA consent, do-not-call) than inbound calls.

### Script

[AVATAR]

Before we go any further, one important sentence. [PAUSE] This lecture is not legal advice. I'm an engineer, not a lawyer. Laws differ by country, by state, and by industry, and they change often, especially for AI. What I can give you is an engineer's checklist: the questions to bring to a qualified lawyer before Riley takes a real patient's call.

[SLIDE 1: Not legal advice]
- This lecture is general information, not legal advice
- Laws vary by country, state and industry, and change often
- Use the checklist to prepare questions for a qualified lawyer
- `10-resources/telephony-compliance-checklist.md`

[SLIDE 2: Five areas to check]
1. AI disclosure
2. Call-recording consent
3. Outbound calling rules (TCPA in the US)
4. Do-not-call lists
5. Data retention and health privacy

[AVATAR]

Five areas. Let's take them one at a time.

One: AI disclosure. More and more jurisdictions require, or strongly expect, that a caller is told when they're talking to an AI. Even where it isn't required, it's the right default. Riley's first sentence already does it: "This is Riley, the clinic's AI assistant." And her prompt says that if anyone asks whether she's a person, she says plainly that she's an AI. [PAUSE] Don't let a persona tweak remove that sentence. In Section 9, we'll write a test that fails if it disappears.

[SLIDE 3: Recording consent]
- One-party consent: one participant may consent (many US states)
- Two-party / all-party consent: everyone must consent (some US states, many countries)
- Your agent is recording if you store audio or transcripts
- Safe default: announce recording at the start of every call

[AVATAR]

Two: recording consent. If you store call audio, or even full transcripts, you're probably recording. In the US, some states only need one party's consent. Others need everyone's. Many other countries also require all parties to be told. You can't always know where your caller is standing. So the safe engineering default is simple: announce it. "This call may be recorded for quality and training." Put it in the greeting, and make recording a setting you can switch off per region.

[SLIDE 4: Outbound calls: stricter rules]
- US TCPA: AI-generated voices count as "artificial" voices for robocall rules (FCC, 2024)
- Prior express consent needed; written consent for marketing calls
- Calling-hour limits, caller ID must be accurate, easy opt-out
- Appointment reminders are generally treated differently from marketing, but still need consent

[AVATAR]

Three: outbound calls. This is where the rules get strict. In the US, the Telephone Consumer Protection Act, the TCPA, governs automated and artificial-voice calls. In 2024 the FCC clarified that AI-generated voices count as artificial voices under those rules. In practice, that means you need the patient's prior consent to call them with Riley. Marketing calls need even stronger, written consent. There are limits on calling hours, your caller ID must be accurate, and the person must be able to opt out easily.

Appointment reminders to your own patients are generally treated more leniently than sales calls. But "more leniently" isn't "no rules." Collect consent at booking time, store it, and have your lawyer check the wording.

[SLIDE 5: Do-not-call and opt-out]
- Check national and internal do-not-call lists before dialing
- "Stop calling me" → record it and never call again
- Opt-out must work by voice, on the call itself
- Test it (Section 9): simulated caller says "take me off your list"

[AVATAR]

Four: do-not-call. Before any outbound call, check the relevant do-not-call lists and your own internal opt-out list. And when someone says "stop calling me," Riley must record it and the system must honor it, on the call, by voice. That's a behavior you can test. We'll add it to the simulated-caller personas in lecture 9.9.

[SLIDE 6: Data retention and health privacy]
- Health providers: HIPAA in the US; GDPR special-category data in the EU/UK
- Business associate agreements (BAAs) with every vendor that touches patient data
- Minimize: redact PII in logs and traces (Section 11)
- Retention: define how long transcripts and audio live, then delete them

[AVATAR]

Five: data. Maple Street Dental is a health provider. In the US, that likely means HIPAA applies, and every vendor that handles patient information, your telephony provider, your speech-to-text and LLM providers, your tracing tool, may need a business associate agreement. In Europe and the UK, health data is special-category data under GDPR. Engineering can help a lot here. Collect less. Redact personal data before it reaches logs and traces, which we'll build in Section 11. And set a retention period, then actually delete old transcripts and recordings.

[SLIDE 7: Compliance you can build into code]
- Disclosure: in `GREETING`, protected by a behavior test (9.3)
- Recording: a per-region setting, off unless you've announced it
- Consent: a stored consent flag checked before any outbound dispatch
- Opt-out: "stop calling me" writes to a do-not-call list the dispatcher checks
- Retention: a scheduled job that deletes transcripts and recordings past your retention period

[AVATAR]

Here's the good news for engineers. Most of these items turn into small, testable pieces of code. Disclosure lives in the greeting, and a behavior test in Section 9 fails if anyone removes it. Recording is a setting you can switch per region. Consent is a stored flag that the outbound dispatcher checks before it ever dials. Opt-out is a list that "stop calling me" writes to and the dispatcher reads. And retention is a scheduled job that deletes old transcripts and recordings. [PAUSE] Your lawyer tells you the rules. Your code makes sure they're followed every time, not just when someone remembers.

[SCREEN: `10-resources/telephony-compliance-checklist.md` scrolled slowly; each item has a checkbox and a "question for counsel" column.]

[AVATAR]

The checklist in the resources folder turns all of this into boxes to tick and questions for your lawyer. Use it before your first real caller, and again before your first outbound campaign. Once more, because it matters: this is not legal advice. It's a list of things to get proper advice on.

### Recap

Check AI disclosure, recording consent, outbound calling rules, do-not-call and data retention with a qualified lawyer before Riley talks to real patients; this lecture is not legal advice.

### Transition

Now it's your turn to put all of Section 8 together: Project 2, your own phone receptionist.

### Speaker notes: common mistakes and Q&A

- **"Is disclosure optional if the voice is really good?"** Treat disclosure as mandatory. The trend in law and platform policy is toward more disclosure, not less.
- **"My trial number is only for testing."** Testing on real people still counts. Test with your own verified numbers.
- **Vendor agreements**: students assume the LLM provider "handles HIPAA." Many providers offer BAAs only on specific plans or endpoints. Check each vendor.
- **Regional variation**: students outside the US should look up their local equivalents (for example, GDPR/ePrivacy, Ofcom rules, CRTC rules). Reiterate: not legal advice.

---

## Lecture 8.7: Project 2: Phone receptionist

| Field | Value |
|---|---|
| ID | 8.7 |
| Title | Project 2: Phone receptionist |
| Type | AS (assignment; video intro/walkthrough) |
| Target duration | Video 2:30 (about 280 spoken words at ~140 wpm, plus slide and pause time); project work 2 to 3 hours off-video |
| One idea | Ship a receptionist that answers, books and transfers on a real call, by phone number or, where that isn't possible, by web client plus a SIP test call. |
| Prerequisites | 8.1 to 8.6 |
| Files used | `05-projects/project-2-phone-receptionist.md`, `agents/s08_telephony_agent.py`, `telephony/*.json`, `10-resources/telephony-compliance-checklist.md` |

**Learning objectives**

1. Deploy an inbound line that books an appointment and transfers to a human, via Path A (phone number) or Path B (no phone number).
2. Document the telephony configuration so another engineer can reproduce it.
3. Complete the compliance checklist for your scenario.

### Script

[AVATAR]

Project 2. You're going to put your own receptionist on a real call. It can be Riley for Maple Street Dental, or your own business from the Section 4 challenge.

[SCREEN: `05-projects/project-2-phone-receptionist.md`: requirements, the two paths, deliverables, rubric.]

Open `05-projects/project-2-phone-receptionist.md`. The requirements fit on one screen. The call opens with an AI disclosure. A booking completes, with a read-back. A transfer reaches a second destination. And the call ends cleanly with `end_call`.

There are two ways to do it. Path A is what we did in this section: a Twilio number, an Elastic SIP trunk, and a LiveKit inbound trunk and dispatch rule.

Path B is for you if you can't get a Twilio number. Some countries require identity documents or a local business address, and some students simply don't want to pay for one. Path B has two parts. First, a web client: connect to your named agent from the Agents Playground or the React starter, and dispatch it explicitly with `lk dispatch create`. Second, a SIP test: use a free softphone app such as Linphone to call your LiveKit SIP URI directly, so the call still goes through your inbound trunk, your dispatch rule and the `sip.phoneNumber` caller ID path. The project file has the exact steps, and a note to verify them in the current LiveKit console. For the transfer requirement on Path B, transfer to a second SIP address instead of a phone number.

[SLIDE 1: Deliverables]
- 2-minute recording of a real call, with captions (phone or softphone)
- `telephony/` JSON files with secrets removed, plus a short README
- Completed compliance checklist, with the "question for counsel" column filled in
- One failure path shown: transfer unset, withheld caller ID, or 20 seconds of silence

[AVATAR]

The rubric rewards the failure paths. What happens when the transfer number is unset? When caller ID is withheld? When the caller says nothing for twenty seconds? Show at least one of those in your recording. Both paths earn full marks. Post your recording in the Q&A. I'd love to hear your receptionist.

### Recap

Project 2 proves you can put a voice agent on a real call, by phone number or by web client plus a SIP test, that books, transfers and hangs up safely.

### Transition

Before Section 9, a five-question quiz to check the telephony essentials.

### Speaker notes: common mistakes and Q&A

- **Recording shows only the happy path**: remind students the rubric requires one failure path.
- **Secrets committed**: `outbound-trunk.json` and any inbound trunk auth contain passwords. Check with `git diff` before pushing.
- **Path B softphone call rejected**: the inbound trunk's `numbers`, allowed addresses or auth settings don't match the softphone's request. Check the trunk with `lk sip inbound list`, and verify in current LiveKit/Twilio console.
- **Path B web client, agent never joins**: a named agent needs explicit dispatch; the Playground won't auto-dispatch it.

---

## Lecture 8.8: Quiz: Telephony

| Field | Value |
|---|---|
| ID | 8.8 |
| Title | Quiz: Telephony |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 120 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Check you can trace a call path and choose the right telephony tool for each job. |
| Prerequisites | 8.1 to 8.7 |
| Files used | `06-assessments/quizzes/section-08.md` (5 questions) |

**Learning objectives**

1. Recall the role of trunks, dispatch rules and agent names in the call path.
2. Apply transfer, hang-up and outbound patterns, and the compliance basics, to short scenarios.

### Script

[AVATAR]

Five questions. One on the call path: a caller hears silence after the call connects, so which link do you check first? One on agent names and explicit dispatch. One on `transfer_to_human`, and why Riley waits for playout before transferring. One on outbound reminder calls. And one on compliance: disclosure, consent and do-not-call.

[SLIDE 1: Quiz: 5 questions]
- Call path and dispatch
- Transfer and end call
- Outbound calls and compliance basics

[AVATAR]

A tip for the call-path question: walk the chain from the caller to the agent, in order, and ask at each link whether the call could have got this far. The first link where the answer is "no" is where to look.

Every answer links back to its lecture. About five minutes. And remember, the compliance question tests what to check, not legal advice.

### Recap

The quiz checks the telephony chain, the phone-specific tools and the compliance checklist.

### Transition

Riley is now live on a phone. That makes Section 9 the most important section of the course: how to test and evaluate her before real patients find the bugs.

### Speaker notes: common mistakes and Q&A

- Most-missed: "Call connects, silence." Answer: agent name mismatch or agent not running in `dev`/`start`.
- Students often think caller ID verifies identity. It pre-fills a number; verification comes in Section 11.
