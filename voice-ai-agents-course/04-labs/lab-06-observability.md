# Lab 6: Build a Call-Quality Report

| Field | Details |
|---|---|
| **Section / lecture** | Section 10, lecture 10.6 |
| **Time estimate** | 75 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Run 10 realistic calls against the observed agent, then turn the exported metrics and usage into a one-page call-quality report: latency percentiles against budget, cost per minute and where the money goes, call outcomes and containment rate, plus traces in Langfuse. |
| **You will produce** | `metrics/*.jsonl`, `labs/lab06_report.py`, Langfuse traces, and `notes/lab-06-report.md` with findings and one recommended alert |

---

## Prerequisites

- Lectures 10.1 to 10.5 watched.
- Labs 1 and 4 done (you have exported metrics once before).
- Optional but recommended: a free Langfuse Cloud account (https://cloud.langfuse.com) for Step 5.
- Budget: roughly $0.30 to $0.80 for 10 short calls with the default models.

---

## Step 1: Install the observability extra and configure tracing

```bash
uv sync --extra observability
```

In Langfuse, create a project called `maple-street-dental`, open **Settings → API keys**, create a key pair and add it to `.env`:

```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
METRICS_DIR=metrics
MAPLE_TODAY=2026-10-05
```

(Use the host shown in your Langfuse project if it is a regional one, such as `https://us.cloud.langfuse.com`.) Tracing is optional: without these variables `s10_observed_agent.py` still writes metrics and cost files; it only skips the OpenTelemetry exporter. Any OTLP backend also works via `OTEL_EXPORTER_OTLP_ENDPOINT`.

Clear old files so the report only covers this lab:

```bash
mkdir -p metrics && rm -f metrics/*.jsonl
```

> **Checkpoint 1:** `uv run python -c "import opentelemetry; print('otel ok')"` prints `otel ok`.

---

## Step 2: Understand what the observed agent records

Open `agents/s10_observed_agent.py` and find `attach_observers()`. For every call it:

1. Appends every `metrics_collected` event (EOU, STT, LLM, TTS, VAD) as one JSON line to `$METRICS_DIR/<room>.jsonl`, keeping LiveKit's `type` and `speech_id` fields.
2. Logs per-turn end-to-end latency from `ChatMessage.metrics` (the newer per-turn API).
3. At shutdown, reads `session.usage.model_usage`, converts it with `maple.costs.usage_from_model_usage()` and `cost_breakdown()`, and appends one `call_summary` line with `call_seconds`, `cost_components`, `cost_total`, `cost_per_minute` and the call `outcome` from `CallState`.

Version note: in livekit-agents 1.8, `metrics_collected` and `metrics.UsageCollector` still work but log deprecation warnings; `session.usage` and per-message metrics are the replacements. The file shows both, so older tutorials still make sense.

---

## Step 3: Run 10 calls

Start the agent:

```bash
uv run agents/s10_observed_agent.py console
```

Run each call below as its own session (`Ctrl+C` ends the call and triggers the shutdown summary; restart for the next one). Vary your pace and pauses the way real callers do.

| # | Call | Expected outcome |
|---|---|---|
| 1 | Book a cleaning next Wednesday morning (new patient, name and number of your choice) | `booked` |
| 2 | "What are your hours on Friday?" then goodbye | `completed` |
| 3 | "Where do I park?" then "Do you take MetLife?" | `completed` |
| 4 | Book, then change your mind about the time before confirming | `booked` |
| 5 | Ask for a Sunday appointment, accept the offered alternative | `booked` |
| 6 | Long, rambling request with pauses: "So I, um, I think I need... a filling? Maybe?" | `booked` or `completed` |
| 7 | "How much is a crown?" (listen for a grounded range) | `completed` |
| 8 | Interrupt Riley twice while she is offering times | any |
| 9 | Ask something off-topic ("Can you help with my homework?") then hang up | `completed` |
| 10 | Book with `MAPLE_SIMULATED_LATENCY=1.5` set, so tools are slow and filler speech plays | `booked` |

For call 10:

```bash
MAPLE_SIMULATED_LATENCY=1.5 uv run agents/s10_observed_agent.py console
```

At the end of each call the log prints a cost block similar to:

```text
INFO riley - call cost report
stt            $0.0118
llm            $0.0041
tts            $0.0525
realtime       $0.0000
platform       $0.0153
telephony      $0.0000
total          $0.0837
per minute     $0.0546  (1.53 min)
```

Check the files:

```bash
ls metrics/
grep -c '"call_summary"' metrics/*.jsonl
```

In console mode several calls may land in the same file (the room name can repeat); that is fine, because each call writes exactly one `call_summary` line.

> **Checkpoint 2:** the `grep` counts add up to 10 call summaries.

---

## Step 4: Build the report

Create `labs/lab06_report.py`:

```python
"""Lab 6: call-quality report over the JSONL files written by agents/s10_observed_agent.py.

Usage: uv run python labs/lab06_report.py [metrics_dir]   (default: $METRICS_DIR or "metrics")
Exit code 1 if any latency stage is over budget, so the script can gate CI.
"""
import sys
from collections import Counter
from pathlib import Path

from maple.config import load_settings
from maple.latency import LatencyBudget, check_budget, format_report, load_jsonl, samples_from_metrics

TRANSFER_OUTCOMES = {"transferred", "transfer_failed", "transfer_unavailable"}


def main(metrics_dir: Path) -> int:
    files = sorted(metrics_dir.glob("*.jsonl"))
    if not files:
        print(f"No .jsonl files in {metrics_dir}. Run agents/s10_observed_agent.py first.")
        return 1
    records = [record for path in files for record in load_jsonl(path)]
    calls = [r for r in records if r.get("type") == "call_summary"]

    print(f"# Call-quality report ({len(files)} files, {len(calls)} calls)\n")
    budget = LatencyBudget()
    samples = samples_from_metrics(records)
    print("## Latency (ms)\n")
    print(format_report(samples, budget))

    if calls:
        minutes = sum(c["call_seconds"] for c in calls) / 60
        total = sum(c["cost_total"] for c in calls)
        components = Counter()
        for call in calls:
            components.update(call.get("cost_components", {}))
        outcomes = Counter(c.get("outcome", "unknown") for c in calls)
        transferred = sum(n for outcome, n in outcomes.items() if outcome in TRANSFER_OUTCOMES)
        print("\n## Cost\n")
        print(f"calls {len(calls)}, minutes {minutes:.1f}, total ${total:.4f}, per minute ${total / minutes:.4f}")
        for name, value in components.most_common():
            share = value / total * 100 if total else 0.0
            print(f"  {name:<10} ${value:.4f}  ({share:.0f}%)")
        print("\n## Outcomes\n")
        for outcome, n in outcomes.most_common():
            print(f"  {outcome:<22} {n}")
        print(f"\ncontainment rate {(len(calls) - transferred) / len(calls):.0%} (calls not transferred)")

    violations = check_budget(samples, budget)
    print("\n## Budget\n")
    print("PASS: every stage within its p95 budget" if not violations else "\n".join(f"FAIL {v}" for v in violations))
    return 1 if violations else 0


if __name__ == "__main__":
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(load_settings().metrics_dir)
    sys.exit(main(directory))
```

Run it:

```bash
uv run python labs/lab06_report.py
```

Expected shape (your numbers will differ):

```text
# Call-quality report (3 files, 10 calls)

## Latency (ms)

stage               n      p50      p90      p95   budget  status
-----------------------------------------------------------------
eou_delay          60      573      757      782      700  OVER
stt_final          60      323      417      431      500  OK
llm_ttft           60      564      763      776      700  OVER
tts_ttfb           60      219      282      294      300  OK
voice_to_voice     60     1330     1676     1700     1600  OVER

## Cost

calls 10, minutes 22.0, total $0.8400, per minute $0.0382
  tts        $0.5000  (60%)
  platform   $0.2000  (24%)
  stt        $0.1000  (12%)
  llm        $0.0400  (5%)
  ...

## Outcomes

  booked                 4
  completed              2
  ...

containment rate 80% (calls not transferred)

## Budget

FAIL eou_delay: p95=782 ms exceeds budget 700 ms by 82 ms
...
```

The budget comes from `maple.latency.LatencyBudget` (p95: EOU 700 ms, STT final 500 ms, LLM TTFT 700 ms, TTS TTFB 300 ms, voice-to-voice 1,600 ms). The script exits with status 1 when any stage is over budget, the same behaviour as `tests/evals/latency_report.py` in CI. Prices come from `maple.costs.DEFAULT_PRICES`, which are **placeholders**: update the `PriceTable` from your own invoices before quoting a number to anyone.

Cross-check your latency table against the course's CI script, which reads the same files:

```bash
uv run python tests/evals/latency_report.py metrics/*.jsonl
make latency FILES="metrics/*.jsonl"          # same thing through the Makefile
```

Its exit code is 0 when every stage is within budget, 1 on a violation and 2 when there is no data.

> **Checkpoint 3:** the report prints all four sections and a PASS/FAIL budget line, and its latency numbers match `latency_report.py`.

---

## Step 5: Read the traces

Open your Langfuse project → **Traces**. Pick call 10 (the slow one) and find:

1. The spans for one user turn: STT, LLM (with prompt and completion tokens), TTS, and the tool call span for `find_available_slots` or `book_appointment`.
2. The tool span's duration: it should include the 1.5 s simulated backend latency.
3. The gap between the tool finishing and the next TTS starting.

Then look for personal data. Search the trace for the phone number you gave in call 1. You will probably find it in tool arguments and the transcript. Note where: you will fix this in lecture 11.3 by redacting with `maple.pii` before export.

> **Checkpoint 4:** you have a screenshot of one turn's spans and a list of where PII appears in traces.

---

## Step 6: Write the one-page report

Create `notes/lab-06-report.md`:

```markdown
# Riley call-quality report (Lab 6)

**Scope:** 10 console calls, <date>, models: <STT / LLM / TTS>, prices: <placeholder or updated>

## Headline numbers
| Metric | Value | Budget / target | Status |
|---|---|---|---|
| p95 voice-to-voice | | 1,600 ms | |
| p95 EOU delay | | 700 ms | |
| p95 LLM TTFT | | 700 ms | |
| Cost per minute | | (your target) | |
| Containment rate | | | |

## Three findings
1. (Largest latency contributor and evidence)
2. (Largest cost component and one change that would reduce it)
3. (Something from the traces: slow tool, PII in spans, retries...)

## One alert I would set up
(Metric, threshold, window, and why it will not be noisy.)

## Next experiment
(One change to try and the number you expect it to move.)
```

> **Checkpoint 5:** the report fits on one page and every finding cites a number.

---

## Stretch goal

Compare cascaded and realtime cost per minute on the same calls. Run calls 1 and 3 against `agents/s06_realtime_agent.py` with an exporter (the Lab 4 snippet, or `attach_observers(session, ctx, realtime=True)` from `s10_observed_agent.py`), then extend `lab06_report.py` to group call summaries by architecture. Finally, write a GitHub Actions step that runs the report over `tests/data/sample_metrics.jsonl` and fails the build on a budget violation.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No `call_summary` lines | Process killed before shutdown callbacks ran (for example closing the terminal) | End calls with `Ctrl+C` once and wait for the cost block in the log |
| `ModuleNotFoundError: opentelemetry` | Observability extra not installed | `uv sync --extra observability` |
| No traces in Langfuse | Keys missing or wrong host (EU vs US region) | Check `LANGFUSE_HOST` matches the region shown in your project; restart the agent after editing `.env` |
| `voice_to_voice` row missing | Stages could not be joined on `speech_id` (for example, realtime calls have no TTS stage) | Expected for realtime; for cascaded runs check that EOU, LLM and TTS records share `speech_id` |
| Deprecation warnings about `metrics_collected` / `UsageCollector` | Expected in livekit-agents 1.8 | Safe to ignore in this lab; `session.usage` is already used for costs |
| Cost per minute looks very low or very high | Placeholder `PriceTable` | Update `src/maple/costs.py` prices from provider pages or invoices |
| Report says `No .jsonl files` | Different `METRICS_DIR` | Pass the directory explicitly: `uv run python labs/lab06_report.py path/to/metrics` |

---

## Solution notes

A typical result from the course's test runs with default models and placeholder prices:

- **Latency:** p95 voice-to-voice around 1.4 to 1.8 s. EOU delay is usually the largest single stage, especially on calls with hesitant speech (call 6); LLM TTFT spikes on turns that follow tool calls because the prompt is longer. Call 10 shows the tool latency directly in traces, with filler speech covering it.
- **Cost:** around $0.04 to $0.07 per minute for web calls. TTS is typically the largest component (billed per character), followed by the platform fee; the LLM is small thanks to prompt caching. Phone calls add a telephony line (`PHONE_PRICES` in `maple.costs`).
- **Outcomes:** most calls `booked` or `completed`; containment near 100% in this lab because no call asks for a human. In production, track the transfer rate next to containment.
- **Traces:** caller phone numbers and names appear in tool arguments and transcripts. That is the motivating finding for lecture 11.3.
- **A good alert:** "p95 voice-to-voice over 1.6 s for 15 consecutive minutes, with at least 20 turns in the window", which ignores one-off network blips and low-traffic noise.

Graders should look for numbers taken from the student's own run, findings that name the stage or component responsible, and an alert with a window and a minimum sample size.

Reference files: `03-code/agents/s10_observed_agent.py`, `03-code/src/maple/latency.py`, `03-code/src/maple/costs.py`, `03-code/tests/evals/latency_report.py`.
