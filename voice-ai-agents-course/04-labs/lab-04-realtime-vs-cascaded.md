# Lab 4: Measure Both Architectures

| Field | Details |
|---|---|
| **Section / lecture** | Section 6, lecture 6.5 |
| **Time estimate** | 75 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Run the same five scripted calls against the cascaded booking agent (STT → LLM → TTS) and the OpenAI Realtime agent, collect latency, cost, tool accuracy and interruption data, and make a written, evidence-based architecture recommendation for Maple Street Dental. |
| **You will produce** | `metrics/lab04-*.jsonl`, `labs/lab04_compare.py`, and `notes/lab-04.md` containing the comparison sheet and a one-paragraph recommendation |

---

## Prerequisites

- Labs 1 and 2 complete; Project 1 (booking agent) started or the reference `agents/s05_booking_agent.py` working in console mode.
- Lectures 6.1 to 6.4 watched.
- `OPENAI_API_KEY` in `.env` (the realtime agent calls OpenAI directly through the `openai` plugin).
- Budget: this lab costs roughly $0.50 to $1.50 in API usage, mostly realtime audio tokens.
- Optional but recommended: a free audio recorder (Audacity, QuickTime, or your OS screen recorder) for measuring perceived latency.

---

## Step 1: Pin "today" so both agents see the same calendar

The scheduler resolves phrases like "next Tuesday" relative to today. Pin the date so both runs offer identical slots. `.env.example` already sets this; check your `.env` has it:

```dotenv
MAPLE_TODAY=2026-10-05
```

(2026-10-05 is a Monday. Clinic hours from `src/maple/data/faq.md`: Monday to Thursday 8:00 to 17:00 with lunch 12:00 to 13:00, Friday 8:00 to 14:00, Saturday 9:00 to 13:00, closed Sunday.)

Confirm:

```bash
uv run --env-file .env python -c "from maple.config import load_settings; print(load_settings().today_override)"
```

Expected: `2026-10-05`.

> **Checkpoint 1:** `today_override` prints `2026-10-05`.

---

## Step 2: Export metrics and usage from both agents

Make copies so the reference files stay clean:

```bash
cp agents/s05_booking_agent.py agents/lab04_cascaded.py
cp agents/s06_realtime_agent.py agents/lab04_realtime.py
```

In **each** copy, inside the entrypoint, right after the `session = AgentSession(...)` block and before `await session.start(...)`, add the exporter below. Set `LABEL = "cascaded"` in `lab04_cascaded.py` and `LABEL = "realtime"` in `lab04_realtime.py`.

```python
import json
import os
import time
from pathlib import Path

from livekit.agents import MetricsCollectedEvent, metrics
from maple.config import load_settings

LABEL = "cascaded"  # in lab04_realtime.py use: "hybrid" if os.getenv("REALTIME_HYBRID") == "1" else "realtime"
out_dir = Path(load_settings().metrics_dir)
out_dir.mkdir(parents=True, exist_ok=True)
metrics_file = out_dir / f"lab04-{LABEL}.jsonl"
usage_file = out_dir / f"lab04-{LABEL}-usage.jsonl"
call_started = time.monotonic()

@session.on("metrics_collected")
def _export_metrics(ev: MetricsCollectedEvent) -> None:
    metrics.log_metrics(ev.metrics)
    with metrics_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev.metrics.model_dump(mode="json")) + "\n")

async def _export_usage() -> None:
    entries = [u.model_dump(mode="json") for u in session.usage.model_usage]
    record = {"call_seconds": round(time.monotonic() - call_started, 1), "model_usage": entries}
    with usage_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

ctx.add_shutdown_callback(_export_usage)
```

Each metrics record keeps LiveKit's own `type` field (`eou_metrics`, `llm_metrics`, `tts_metrics`, `realtime_model_metrics`, ...), which is the format `maple.latency.samples_from_metrics()` expects. The usage records match what `maple.costs.usage_from_model_usage()` expects. This is the same export `agents/s10_observed_agent.py` does in Section 10.

If your installed release exposes usage through `metrics.UsageCollector` instead of `session.usage`, see the troubleshooting table.

Smoke-test the cascaded copy:

```bash
uv run agents/lab04_cascaded.py console
```

Say "hello", then `Ctrl+C`. Check:

```bash
wc -l metrics/lab04-cascaded.jsonl metrics/lab04-cascaded-usage.jsonl
```

Expected: a few metrics lines and exactly one usage line. **Delete both files** before the real runs:

```bash
rm metrics/lab04-*.jsonl
```

> **Checkpoint 2:** both copies write metrics while running and one usage line on exit.

---

## Step 3: The five scripted calls

Run each call as a **separate console session** (start the agent, run the call, `Ctrl+C`), so each call gets its own usage line. Use the same wording each time; print this table.

| Call | Script (you say) | Correct outcome |
|---|---|---|
| C1 Happy path | "I'd like to book a cleaning on Tuesday the thirteenth, in the morning." Then give name "Casey Morgan", phone "five one two, five five five, zero one six one", pick the first time offered, say "yes" to the read-back. | `find_available_slots` then `book_appointment` with Tuesday 2026-10-13 morning, correct name and phone |
| C2 Correction | Same as C1 but when Riley reads back, say "No, Thursday, not Tuesday." | Riley re-checks a Thursday (the 8th or the 15th; either is fine if Riley says the date), reads back again, books only after "yes" |
| C3 Closed day | "Can I come in this Sunday?" | No booking; Riley says the clinic is closed Sundays and offers the nearest open day. No invented slots |
| C4 Reschedule | Book as in C1, then in the same call: "Actually, can we move that to Wednesday afternoon?" | `reschedule_appointment` (not a second booking) to a Wednesday afternoon slot, read-back before commit |
| C5 Barge-in | Ask "What times do you have Friday?" and, while Riley is listing times, interrupt with "Sorry, wait, I meant Saturday." | Riley stops within about half a second and answers for Saturday |

Run all five against **cascaded** first:

```bash
uv run agents/lab04_cascaded.py console
```

then all five against **realtime**:

```bash
uv run agents/lab04_realtime.py console
```

After each call, fill one row of the observation sheet (Step 5) while it is fresh: which tools were called with which arguments (they appear in the console log), whether the outcome was correct, and how barge-in felt.

> **Checkpoint 3:** `metrics/lab04-cascaded-usage.jsonl` and `metrics/lab04-realtime-usage.jsonl` each contain 5 lines.

---

## Step 4: Measure perceived latency (the fair comparison)

The two architectures report different metrics. The cascaded pipeline reports EOU delay, LLM TTFT and TTS TTFB separately. A realtime model hears audio and speaks audio, so its end-of-turn detection happens inside OpenAI's servers and you mostly get a single `ttft` from `realtime_model_metrics`. Comparing cascaded `llm_ttft` with realtime `ttft` is **not** apples to apples.

The fair comparison is what the caller hears: silence between the end of your words and the start of Riley's.

1. Start your recorder so it captures both your mic and Riley's audio (in console mode both come through your laptop).
2. Replay C1 for each agent.
3. Open the recording in Audacity, zoom in, and for three turns per agent measure the gap between the end of your waveform and the start of Riley's.

Record the median of the three gaps per architecture.

> **Checkpoint 4:** you have a perceived-latency number (in ms) for each architecture.

---

## Step 5: Compute the comparison

Create `labs/lab04_compare.py`:

```python
"""Lab 4: compare cascaded and realtime runs from exported metrics and usage."""
from pathlib import Path

from maple.costs import cost_breakdown, usage_from_model_usage
from maple.latency import format_report, load_jsonl, samples_from_metrics

METRICS_DIR = Path("metrics")

for label, realtime in (("cascaded", False), ("realtime", True)):
    metrics_file = METRICS_DIR / f"lab04-{label}.jsonl"
    usage_file = METRICS_DIR / f"lab04-{label}-usage.jsonl"
    if not metrics_file.exists():
        print(f"== {label}: no data yet ({metrics_file} missing)\n")
        continue
    print(f"== {label}: latency (ms)")
    print(format_report(samples_from_metrics(load_jsonl(metrics_file))))
    calls = load_jsonl(usage_file) if usage_file.exists() else []
    if calls:
        usage = None
        for call in calls:
            one = usage_from_model_usage(call["model_usage"], call["call_seconds"], realtime=realtime)
            usage = one if usage is None else usage + one
        print(f"\n== {label}: cost for {len(calls)} calls (placeholder prices)")
        print(cost_breakdown(usage).format())
    print()
```

Run:

```bash
uv run python labs/lab04_compare.py
```

Expected shape (your numbers will differ):

```text
== cascaded: latency (ms)
stage               n      p50      p90      p95   budget  status
-----------------------------------------------------------------
eou_delay          38      559      710      736      700  OVER
stt_final          38      300      340      352      500  OK
llm_ttft           41      580      814      839      700  OVER
tts_ttfb           41      216      267      280      300  OK
voice_to_voice     37     1367     1607     1647     1600  OVER

== cascaded: cost for 5 calls (placeholder prices)
stt            $0.0290
llm            $0.0180
tts            $0.2250
realtime       $0.0000
platform       $0.0750
telephony      $0.0000
total          $0.3470
per minute     $0.0463  (7.50 min)

== realtime: latency (ms)
stage               n      p50      p90      p95   budget  status
-----------------------------------------------------------------
llm_ttft           36      370      418      428      700  OK

== realtime: cost for 5 calls (placeholder prices)
...
realtime       $1.3060
...
per minute     $0.1841  (7.50 min)
```

Prices come from `maple.costs.DEFAULT_PRICES`, which are **placeholders**. Before you draw conclusions, open `src/maple/costs.py`, update the `PriceTable` values from your providers' current pricing pages or invoices, and re-run.

Now fill in `notes/lab-04.md`:

```markdown
# Lab 4: cascaded vs realtime

## Per-call observations
| Call | Arch | Tools called (name + key args) | Outcome correct? | Barge-in stop time (feel) | Notes |
|------|------|--------------------------------|------------------|---------------------------|-------|
| C1 | cascaded | | | | |
| ... | | | | | |
| C5 | realtime | | | | |

## Summary
| Metric | Cascaded | Realtime |
|--------|----------|----------|
| Perceived latency, median of 3 (ms) | | |
| p95 voice-to-voice / ttft from metrics (ms) | | |
| Cost per minute (updated prices) | | |
| Tool accuracy (correct outcomes / 5) | | |
| Correct read-back before commit (/4 calls with a booking) | | |
| Barge-in quality (1-5) | | |
| Voice quality and naturalness (1-5) | | |
| Control over exact wording, pronunciation (1-5) | | |

## Recommendation for Maple Street Dental
(One paragraph: which architecture, why, and what evidence would change your mind.)
```

> **Checkpoint 5:** the summary table is complete and your recommendation cites at least three numbers from it.

---

## Step 6: Try the hybrid (half-cascade)

Lecture 6.3 showed a middle path: the realtime model listens and reasons, returns **text**, and your own TTS speaks it so Riley keeps her brand voice. `s06_realtime_agent.py` (and therefore your copy) switches to this mode with an environment variable; `build_realtime_model(settings, hybrid=True)` sets `modalities=["text"]` and the session adds `tts=build_tts(settings)`:

```bash
REALTIME_HYBRID=1 uv run agents/lab04_realtime.py console
```

With the `LABEL` line above, hybrid runs are written to `metrics/lab04-hybrid*.jsonl`. Rerun C1 and C5, add `("hybrid", True)` to the loop in `lab04_compare.py`, and add a third column to your summary. Listen for the trade-off: the voice now matches the cascaded agent, and you gain TTS TTFB back in the latency numbers.

---

## Stretch goal

Put both architectures under **phone-like conditions**. Play a recording of café noise (search "coffee shop ambience") from a second device near your mic and rerun C1 and C2 on both. Which architecture mishears the phone number more often? Then extend `lab04_compare.py` to print `cost_per_minute` for 1,000 calls per month at 3 minutes each for both architectures, using `maple.costs.typical_cascaded_usage()` and `typical_realtime_usage()`, and add a monthly-cost row to your summary.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `AttributeError: 'AgentSession' object has no attribute 'usage'` | Older release without `session.usage` | Use `usage = metrics.UsageCollector()`, call `usage.collect(ev.metrics)` in the metrics handler, and write `usage.get_summary()` fields in `_export_usage`; then map them to `UsageNumbers` by hand |
| Realtime agent: `401` / `invalid_api_key` | `OPENAI_API_KEY` missing; realtime does not go through LiveKit Inference | Add the key to `.env`, restart |
| Realtime agent speaks but tools never run | Tool docstrings unclear, or instructions not passed to the realtime model | Confirm the same `Agent` subclass (with tools) is used; check the log for `function_call` events |
| Realtime latency report only shows `llm_ttft` | Expected: EOU and TTS happen inside the realtime model | Use the perceived-latency measurement from Step 4 |
| Riley says Tuesday 10:00 is taken on a fresh start | The demo patients (Jordan Lee, Priya Patel, Sam Rivera) are booked on the first three open days | Expected; use the Casey Morgan identity from the script so you never collide with them |
| Different slots offered by the two agents | `MAPLE_TODAY` not set, or you booked in an earlier call that the in-memory scheduler still remembers | Set `MAPLE_TODAY`; restart the agent between calls (the scheduler is in memory, so a restart resets it) |
| Cost numbers look wildly off | Placeholder `PriceTable`, or realtime entries priced as text tokens | Update prices; make sure `realtime=True` for realtime usage files |
| Barge-in never works in console | Speaker echo is masking your voice, or the realtime model's server VAD threshold is high | Use headphones; note the behaviour as a finding rather than tuning it away |
| `json.dumps` fails on a metrics object | Called `model_dump()` without `mode="json"` | Use `model_dump(mode="json")` |

---

## Solution notes

A typical result from the course's test runs (quiet room, headphones, placeholder prices updated to list prices at recording time):

| Metric | Cascaded | Realtime |
|---|---|---|
| Perceived latency, median | ≈ 1,100-1,400 ms | ≈ 700-1,000 ms |
| Cost per minute | ≈ $0.04-0.07 | ≈ $0.15-0.30 |
| Tool accuracy | 5/5 | 4/5 or 5/5 (most common miss: booking before an explicit "yes" in C2) |
| Barge-in | Good; depends on `InterruptionOptions` | Very natural |
| Wording and pronunciation control | High (you control text and TTS) | Lower (voice is the model's) |

**A strong recommendation** reads something like: "For Maple Street Dental we recommend the cascaded pipeline. It was about 400 ms slower in perceived latency, but cost roughly a quarter as much per minute, got all five scripted outcomes right including the correction in C2, and lets us keep a consistent brand voice and exact pronunciation of dentist names. We would revisit realtime (or the hybrid) if caller surveys show latency complaints, or if realtime audio prices fall by half."

Graders should look for: numbers from the student's own runs (not copied from this table), acknowledgement that metric definitions differ between architectures, and a recommendation tied to the clinic's priorities (accuracy of bookings and cost) rather than to whichever feels cooler.

Reference files: `03-code/agents/s05_booking_agent.py` (`RileyBookingAgent`), `03-code/agents/s06_realtime_agent.py` (`RealtimeRiley`, `REALTIME_HYBRID`), `03-code/agents/s10_observed_agent.py` (`attach_observers`, the production version of the exporter), `03-code/src/maple/latency.py`, `03-code/src/maple/costs.py`, `10-resources/architecture-decision-matrix.md`.
