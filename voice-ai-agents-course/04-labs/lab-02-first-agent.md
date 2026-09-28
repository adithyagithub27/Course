# Lab 2: Customise Your First Agent

| Field | Details |
|---|---|
| **Section / lecture** | Section 3, lecture 3.8 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Beginner to intermediate |
| **Goal** | Change Riley's voice, LLM, endpointing and interruption settings one at a time, hear the effect of each change, and record evidence (latency numbers and notes) you will reuse when you tune the phone agent in Section 8. |
| **You will produce** | `notes/lab-02.md` with a filled-in observation table and your chosen "best" configuration |

---

## Prerequisites

- Lab 1 complete (console mode works, `make test` is green).
- Lectures 3.3 to 3.7 watched, especially 3.6 (VAD, turn detection and interruptions).
- Headphones.
- `agents/s03_hello_agent.py` open in your editor.

## How this lab works

You will run **one experiment at a time**, changing a single variable, and say the same four test lines each time:

| # | Say this | What it tests |
|---|---|---|
| T1 | "Hi, what can you help me with?" | Baseline response time and voice |
| T2 | "My name is... (pause 1 second) ...Siobhan Nguyen." | Premature end-of-turn during a mid-sentence pause |
| T3 | Ask a question, and while Riley is answering, say "wait, sorry" | Barge-in (interruption) behaviour |
| T4 | Cough, or say "mm-hmm" while Riley is talking | False interruptions from backchannels and noise |

---

## Step 1: Turn on metrics logging

You cannot tune what you cannot see. Open `agents/s03_hello_agent.py` and, directly after the `session = AgentSession(...)` block and **before** `await session.start(...)`, add:

```python
from livekit.agents import MetricsCollectedEvent, metrics  # put this with the other imports

@session.on("metrics_collected")
def _on_metrics(ev: MetricsCollectedEvent) -> None:
    metrics.log_metrics(ev.metrics)
```

Run the baseline:

```bash
uv run agents/s03_hello_agent.py console
```

Say T1. Among the log lines you should now see entries similar to:

```text
INFO  livekit.agents - EOU metrics  {"end_of_utterance_delay": 0.62, "transcription_delay": 0.31, ...}
INFO  livekit.agents - LLM metrics  {"ttft": 0.41, "prompt_tokens": 512, "completion_tokens": 24, ...}
INFO  livekit.agents - TTS metrics  {"ttfb": 0.19, "audio_duration": 3.2, ...}
```

(Formatting differs slightly between releases; the field names are what matter.) Write down `end_of_utterance_delay`, `ttft` and `ttfb` for T1. Their sum is a good approximation of the silence you hear after you stop speaking.

> **Checkpoint 1:** you can read EOU delay, LLM TTFT and TTS TTFB from the logs for a single turn.

---

## Step 2: Experiment A: change the voice

Riley's voice comes from two environment variables read by `src/maple/config.py`:

```dotenv
TTS_MODEL=cartesia/sonic-3
TTS_VOICE=f786b574-daa5-4673-aa0c-cbe3e8534c02
```

The agent passes `settings.tts_model_with_voice` (for example `cartesia/sonic-3:f786b574-...`) to `AgentSession(tts=...)`.

1. Browse the Cartesia voice library (https://play.cartesia.ai) and copy the ID of a different voice. Pick one that suits a dental receptionist: calm, clear, mid-pace.
2. Set `TTS_VOICE=<new id>` in `.env`.
3. Restart console mode and run T1 to T4.

Optional: try a different TTS provider through LiveKit Inference by putting the voice in the model string, which makes `config.py` ignore `TTS_VOICE`:

```dotenv
TTS_MODEL=deepgram/aura-2:athena
```

Voice names differ per provider; check the LiveKit Inference TTS docs for valid values.

Record in your notes: voice ID, TTS TTFB for T1, and a one-line impression (clarity, warmth, pacing, how it says "Siobhan").

> **Checkpoint 2:** Riley speaks with the new voice and you recorded its TTFB.

---

## Step 3: Experiment B: change the LLM

Restore your preferred voice, then switch to a smaller model:

```dotenv
LLM_MODEL=openai/gpt-4.1-nano
```

Run T1 to T4 and record LLM `ttft`. Then switch back to `openai/gpt-4.1-mini` and ask both models the same slightly tricky question: "If I come in Tuesday and need a follow-up two weeks later, what day would that be?"

Record: TTFT for each model, and whether each answer was correct and short enough for voice.

> **Checkpoint 3:** you have TTFT numbers for two LLMs and a quality note for each.

---

## Step 4: Experiment C: endpointing delay

Endpointing decides how long Riley waits after you stop talking before treating your turn as finished. `config.py` reads:

```dotenv
MIN_ENDPOINTING_DELAY=0.5
MAX_ENDPOINTING_DELAY=3.0
```

and the agent passes them to `TurnHandlingOptions(endpointing=EndpointingOptions(min_delay=..., max_delay=...))`.

Run T1 and T2 three times, once per setting:

| Run | `MIN_ENDPOINTING_DELAY` | `MAX_ENDPOINTING_DELAY` |
|---|---|---|
| C1 | 0.2 | 3.0 |
| C2 | 0.5 | 3.0 (default) |
| C3 | 1.0 | 6.0 |

For each run record `end_of_utterance_delay` on T1 and whether Riley cut you off during the pause in T2.

What you should notice: C1 feels snappy but Riley is more likely to jump in during your pause; C3 almost never cuts you off but feels sluggish. The semantic turn detector (`inference.TurnDetector()`) is what lets the default C2 wait longer when your sentence sounds unfinished ("My name is...") and respond quickly when it sounds complete. `config.py` rejects a max lower than the min with a `ConfigError`.

> **Checkpoint 4:** your table shows EOU delay rising from C1 to C3.

---

## Step 5: Experiment D: turn detector off

To feel what the turn detector contributes, temporarily switch to silence-only (VAD) endpointing. In `s03_hello_agent.py` change:

```python
turn_handling=TurnHandlingOptions(
    turn_detection=inference.TurnDetector(),
    ...
)
```

to:

```python
turn_handling=TurnHandlingOptions(
    turn_detection="vad",
    ...
)
```

Run T2 with the default 0.5 s minimum delay. Riley should now interrupt your mid-sentence pause far more often, because silence alone cannot tell "My name is..." from a finished sentence. **Revert the change** when done.

> **Checkpoint 5:** you have reproduced at least one premature interruption with `turn_detection="vad"` that did not happen with the turn detector.

---

## Step 6: Experiment E: interruption sensitivity

Find (or add) the interruption options in the same `TurnHandlingOptions` block:

```python
from livekit.agents import InterruptionOptions

turn_handling=TurnHandlingOptions(
    turn_detection=inference.TurnDetector(),
    endpointing=EndpointingOptions(min_delay=settings.min_endpointing_delay,
                                   max_delay=settings.max_endpointing_delay),
    interruption=InterruptionOptions(min_duration=0.5),
)
```

Run T3 and T4 with each setting:

| Run | Setting | Expected behaviour |
|---|---|---|
| E1 | `InterruptionOptions(min_duration=0.5)` (default in the course) | "Wait, sorry" stops Riley; a short cough may too |
| E2 | `InterruptionOptions(min_duration=1.0)` | Coughs and "mm-hmm" rarely stop Riley; real barge-in feels slightly laggy |
| E3 | `InterruptionOptions(min_duration=0.5, min_words=2)` | Riley only stops once STT has heard at least two words; backchannels no longer interrupt |

Record which setting gave the best balance for you.

> **Checkpoint 6:** you can explain, in one sentence each, what `min_duration` and `min_words` trade off.

---

## Step 7: Choose and record your configuration

Create `notes/lab-02.md`:

```markdown
# Lab 2 observations

| Exp | Setting | EOU (s) | LLM TTFT (s) | TTS TTFB (s) | Cut-offs on T2? | Barge-in OK on T3? | False stop on T4? | Notes |
|-----|---------|---------|--------------|--------------|-----------------|--------------------|-------------------|-------|
| Base | defaults | | | | | | | |
| A | voice ... | | | | | | | |
| B | gpt-4.1-nano | | | | | | | |
| C1 | min 0.2 | | | | | | | |
| C3 | min 1.0 / max 6.0 | | | | | | | |
| D | turn_detection="vad" | | | | | | | |
| E2 | min_duration 1.0 | | | | | | | |
| E3 | min_words 2 | | | | | | | |

## My chosen configuration
- TTS_VOICE=
- LLM_MODEL=
- MIN/MAX_ENDPOINTING_DELAY=
- InterruptionOptions(...)
- Why:
```

> **Checkpoint 7:** the table has numbers in every row and a justified final configuration.

---

## Stretch goal

Create two environment profiles and switch between them without editing code:

```bash
cp .env .env.snappy
cp .env .env.careful
# edit .env.snappy:  MIN_ENDPOINTING_DELAY=0.3, LLM_MODEL=openai/gpt-4.1-nano
# edit .env.careful: MIN_ENDPOINTING_DELAY=0.8, MAX_ENDPOINTING_DELAY=5.0
uv run --env-file .env.snappy  agents/s03_hello_agent.py console
uv run --env-file .env.careful agents/s03_hello_agent.py console
```

Ask a friend (ideally someone who speaks more slowly than you, or is less comfortable with technology) to try both blind, and ask which felt more natural. Add their verdict to your notes. This is the seed of the "confused senior" simulated caller you will build in lecture 9.9.

---

**Cross-check with lecture 3.9.** `s03_hello_agent.py` can reproduce the five classic failures on purpose. Run each once and match it to a row of your table:

```bash
BROKEN=short_endpointing uv run agents/s03_hello_agent.py console
BROKEN=long_endpointing  uv run agents/s03_hello_agent.py console
BROKEN=no_interruptions  uv run agents/s03_hello_agent.py console
BROKEN=markdown          uv run agents/s03_hello_agent.py console
BROKEN=wrong_stt         uv run agents/s03_hello_agent.py console
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No metrics lines in the log | Handler registered after `session.start()`, or log level above INFO | Register `@session.on("metrics_collected")` before `start`; run with `--log-level INFO` if your CLI supports it |
| `ConfigError: MAX_ENDPOINTING_DELAY ... must be >= MIN_ENDPOINTING_DELAY` | Max set lower than min | Raise the max or lower the min |
| New voice ID ignored | `TTS_MODEL` already contains `:voice`, so `TTS_VOICE` is not appended | Remove the `:...` suffix from `TTS_MODEL` or change the suffix itself |
| TTS error "voice not found" | Voice ID copied with spaces, or it belongs to another Cartesia model | Re-copy the ID; pick a voice listed for `sonic-3` |
| `ValueError` / unknown model for `gpt-4.1-nano` | Model not available through LiveKit Inference in your region/account | Try `openai/gpt-4o-mini`, or switch to `MAPLE_PROVIDER_MODE=plugins` with your own OpenAI key |
| Riley stops talking whenever you breathe | Speaker echo or a sensitive mic | Headphones; raise `min_duration`; try E3 |
| Changes to `.env` have no effect | `.env` read only at process start | Stop and restart the agent (dev mode reloads code, not always env) |

---

## Solution notes

There is no single right configuration; graders (and you) should look for **evidence-based** choices. A typical good result for a quiet room:

| Setting | Typical outcome |
|---|---|
| Default Cartesia voice, `gpt-4.1-mini`, min 0.5 / max 3.0, turn detector on, `min_duration=0.5` | EOU ≈ 0.5-0.8 s, TTFT ≈ 0.3-0.6 s, TTFB ≈ 0.15-0.3 s; total ≈ 1.0-1.5 s |
| `gpt-4.1-nano` | TTFT typically 20-40% lower, but more likely to mis-handle the date arithmetic question |
| min 0.2 | EOU drops by ~0.3 s but T2 cut-offs appear |
| `turn_detection="vad"` | Frequent T2 cut-offs: evidence that semantic turn detection earns its cost |
| `min_words=2` | Removes most backchannel false stops; barge-in feels slightly later because STT must emit words first |

Key takeaways to write in your notes:

1. Endpointing delay is often the **single largest** latency component and the cheapest to tune.
2. Lower latency settings trade directly against cut-offs; the semantic turn detector reduces that trade-off rather than removing it.
3. Settings that feel right in a quiet room with headphones need re-tuning on the phone (8 kHz audio, line noise). You will revisit this in lecture 8.3.

Reference implementation: `03-code/agents/s03_hello_agent.py` and `03-code/src/maple/config.py`.
