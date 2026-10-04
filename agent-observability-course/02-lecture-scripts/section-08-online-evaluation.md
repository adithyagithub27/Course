# Section 8: Quality in Production: Online Evaluation and Drift

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 52 minutes (8 lectures, including one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Judge output on screen: score and source side by side.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on deepeval 4.2 / langfuse 4.15. Judge prices as of 2026-09-28: verify current pricing."
> **Companion course tie-in:** Lecture 8.6 hands failing traces to the offline-eval workflow taught in *AI Agent Testing & Evaluation*. One spoken line; never required.
> **Offline judge note:** offline (and in every replay), scores come from `OfflineJudge`, a deterministic heuristic over the answer text with the same three criteria as the DeepEval judge. It is what makes Incident 3 reproducible on every laptop. With `OPENAI_API_KEY` and `OFFLINE=0`, `make judge` uses `DeepEvalJudge` (G-Eval).

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (match `03-code/`):** `northwind.sampling` (`head_sample`, `TraceSummary`, `JudgeSamplingPolicy.should_judge`, `TailSamplingPolicy`; `JudgeSampler` is an alias), `evals/online_judge.py` (`CRITERIA`, `OfflineJudge`, `DeepEvalJudge`, `pick_judge`, `run_judge`; `make judge`; `JUDGE_SAMPLE_RATE`, `JUDGE_MAX_CALLS` / `--limit`), `evals/feedback.py` (`REASONS`, `record_feedback`, `correlate`; `make feedback`), `evals/drift_report.py` (`--prev`/`--curr` ISO weeks, days or stores; `compare_specs`, `compare_split`, `render`; `make drift`), `northwind.drift` (`psi`, `compare_windows`, `DriftThresholds`, `DriftResult`, `drift_report_markdown`), `evals/to_dataset.py` (`select_bad_traces`, `write_jsonl`, `push_to_langfuse`; `make dataset`), `telemetry/metrics.py` (`GUARDRAIL` / alias `GUARDRAIL_EVENTS`, `JUDGE_SCORE`, `FEEDBACK`), `app/server.py` (`POST /feedback`, `FeedbackRequest`), Ops Console Quality and Safety pages. Langfuse calls verified on 4.15: `create_score(trace_id=, name=, value=, data_type=, comment=)`, `create_dataset(name=)`, `create_dataset_item(dataset_name=, input=, expected_output=, metadata=, source_trace_id=)`. Trace-level attributes are set with `propagate_attributes(...)` (Section 4).

**The numbers card for this section (from `01-curriculum/numbers-card.md`):**

| Item | Value |
|---|---|
| Traffic | 10,184 requests, 4,000 sessions a day ($56.28 baseline; $19.07 after the Section 6 levers) |
| Judged by the replay (30% sample, 4 scores each) | 2,971 traces |
| Judge means, baseline day | overall **0.912** · grounded **0.943** · resolved **0.892** · safe_escalation 0.901 |
| `make judge` afterwards (offline, `JUDGE_SAMPLE_RATE=0.1`; every thumbs-down and every escalation is judged) | `candidates=10112 sampled=894 scored=894 already_scored=2971 mean_overall=0.909 est_judge_cost=$1.9310` |
| `make feedback` after `make judge` | `joined_with_judge=639 agreement=57%` (before the judge: 363 / 80%) |
| User feedback | 1,291 events, 12.7% of requests, 78.7% positive (1,016 👍 / 275 👎); every 👎 comment is `unhelpful` |
| Feedback rate by session length (share of sessions with any feedback) | 1 turn 12.6% · 2 turns 23.9% · 3 turns 34.4% · 4 turns 39.9% |
| Judge (resolved ≥ 0.7) vs user agreement | 77.7% over 363 traces with both; 81 disagreements |
| Task success / containment (SLIs, `make report`) | 0.993 / 0.989 |
| Drift on the baseline day (`make drift`, split at 12:00) | 0 alerts |
| `quality_drift` preset (prompt v2 from 11:00) | $53.68; judge by version v1 overall 0.910 / v2 0.711; grounded 0.94 → 0.59 and resolved 0.89 → 0.65 from 11:00 |

---

## Lecture 8.1: Offline evals are not enough

| Field | Value |
|---|---|
| ID | 8.1 |
| Title | Offline evals are not enough |
| Type | SL (slides + avatar, with one terminal beat) |
| Target duration | 6:00 (about 590 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | A passing test suite tells you about yesterday's questions; production quality needs a judge, real feedback and a drift check on today's traffic. |
| Prerequisites | Sections 4 to 7 |
| Files used | Diagram "the quality loop"; `make test`; `make replay SCENARIO=quality_drift`; `make console-text` |

**Learning objectives**

1. Name four ways quality drops in production while offline evals stay green: distribution shift, new intents, prompt and model changes, silent regressions.
2. Define "quality in production" as three signals: sampled judge scores, user feedback and drift against a baseline.
3. Explain why cost per resolved session (6.3) depends on this section.

### Script

[SCREEN: terminal, split. Left: `make test` ends `419 passed`. Right: a replay of a day on which prompt version 2 went live at 11:00, then the Quality block of the text console.]

```bash
OFFLINE=1 make replay SCENARIO=quality_drift STORE=.atlas/drift-day.sqlite
make console-text STORE=.atlas/drift-day.sqlite      # scroll to "Quality"
```

[DEMO: output (Quality block):]

```
-- Quality ---------------------------------------------------------------------
judge_overall mean=0.786 grounded mean=0.72 n=3008  feedback n=1330 positive=0.736
by prompt version: v1: mean=0.91 n=1127, v2: mean=0.711 n=1881
hourly judge mean: 00h=0.91 01h=0.93 02h=0.91 03h=0.91 04h=0.91 05h=0.89 06h=0.92 07h=0.91 08h=0.91 09h=0.91 10h=0.91 11h=0.71 12h=0.71 13h=0.70 14h=0.72 15h=0.71 16h=0.72 17h=0.71 18h=0.70 19h=0.69 20h=0.73 21h=0.73 22h=0.71 23h=0.69
drift (am vs pm): status=alert psi=2.0977 mean_delta=-18.6% reasons=['psi 2.098 >= 0.25', 'mean moved -18.6%']
```

[AVATAR]

Four hundred and one tests, all green. And on the same day, from eleven o'clock, the judge's score for Atlas's answers fell from point nine one to point seven one, and stayed there. [PAUSE] The tests weren't wrong. They test the code against yesterday's questions, and nobody had connected them to a prompt that changed at eleven. That's the gap this section closes.

[SLIDE 1: Four ways quality drops while tests stay green]
- Distribution shift: the questions change. A new expense system, and a third of finance questions are about a screen your knowledge base has never seen
- New intents: users ask things you never planned for, and Atlas answers anyway
- Prompt and model changes: prompt v2 goes live; the provider updates a model behind the same name
- Silent regressions: a retrieval top-k change, a truncation budget, a tool that starts returning less

[AVATAR]

Four ways. The questions change: a new expense system rolls out and a third of finance questions are about something the knowledge base has never seen. Users invent intents you didn't plan for, and an agent will always answer. Something you control changes: prompt version two, or a config knob from Section 6. Or something you don't control changes: the provider updates the model behind the same name. [PAUSE] None of these fail a test, because tests ask yesterday's questions. Production quality means asking about today's.

[B-ROLL: a generation span's attributes in the trace view, `gen_ai.response.model` highlighted next to `gen_ai.request.model`.]

That third one is worth a second look. Model aliases like `gpt-4.1-mini` can point at a new snapshot without your code changing. Your tests pass on Monday's snapshot; Tuesday's answers differ. Two defences: record the served model on every generation, which `gen_ai.response.model` already does on Atlas's spans, and tag every release, so a drop in the scores can be lined up with "the model changed" or "the prompt changed." You can't stop the provider from shipping. You can make sure you notice.

[SLIDE 2: Quality in production: three signals]
- A judge: an LLM grades a sample of live traces against criteria you wrote. Continuous, costs money, scales
- Feedback: users tell you. Free, sparse, biased
- Drift: this window's numbers against the last one's. Catches slow slides the other two miss
- All three land in the same place: scores on traces in the span store and in Langfuse

[AVATAR]

Three signals, and you need all three because each one lies in a different way. A judge model grades a sample of live traces against criteria you write. It's continuous and it scales, and it costs money, so we'll sample. Users give feedback. It's free and honest and sparse, and it's biased toward people who bother. And drift: comparing this week to last week, which catches the slow slide that looks fine on any given day. [PAUSE] All three become scores on traces, so they sit next to cost and latency on the same trace.

[SLIDE 3: The quality loop]
- Live traffic → sampled traces → judge → scores on traces
- Users → `/feedback` → scores on traces
- Scores + cost + latency → two windows → drift report
- Failing traces → dataset → offline evals (Course 2) → next prompt version
- Diagram builds clockwise

[B-ROLL: the loop diagram builds clockwise, one arrow per sentence.]

[AVATAR]

Here's the loop. Live traffic gets sampled and judged, and the scores land on the traces. Users click thumbs, and those land on the traces too. Scores, cost and latency get compared window over window for drift. And the traces that failed get promoted to a dataset, which is what your offline evals run against next time. [PAUSE] That last arrow is the one most teams never draw. Production failures become tomorrow's regression tests. By 8.6 you'll have it.

[SLIDE 4: Why cost engineering depends on this]
- Cost per resolved session needs `resolved`
- In Section 6, `resolved` came from the request outcome: errors, step limits and timeouts
- An answer that ends politely and helps nobody still counts as resolved
- The judge's `resolved` score (0.892 on the baseline day) is what catches it

[AVATAR]

And here's why this section belongs in a cost course. In Section 6, cost per resolved session used the request's outcome, and an outcome only knows about errors, step limits and timeouts. On the drift day you just saw, almost every request still ended "resolved," while the judge said the answers got worse. [PAUSE] Cost per resolved session, the number finance accepts, is only honest when the judge stands behind the word "resolved."

[SLIDE 5: What we'll build]
- 8.2 sampled judge, scores to the store and Langfuse, cost as a line item
- 8.3 feedback endpoint, correlation with the judge, survivorship bias
- 8.4 guardrail and safety metrics as time series
- 8.5 drift detection and the report
- 8.6 bad trace to regression test

[AVATAR]

The plan. A sampled judge with three agent-specific criteria and its own cost line. A feedback endpoint that means something. Guardrail metrics as time series. Drift detection with a report. And the promotion of bad traces to a dataset. [PAUSE] One caution before we start: a judge is a model. It can be wrong. Everything we build keeps a human able to check a score in ten seconds.

[SLIDE 6: Recap]
- Green tests don't mean good answers
- Three signals: judge, feedback, drift
- Failures become tomorrow's regression tests

### Recap

Offline evals test yesterday's questions; production quality needs a sampled judge, real feedback and a drift check, all landing as scores on traces.

### Transition

Next, the judge: sampling policies, three criteria written for a helpdesk agent, and the scores written back to the store and to Langfuse, with the cost of judging counted honestly.

### Speaker notes: common mistakes and Q&A

- **"We have 90% test coverage."** Coverage of code, not of questions. Distribution shift is about the input space.
- **Treating the judge as truth.** Say it every time: score, sampled, checked by humans weekly.
- **Skipping feedback because it's sparse.** 12.7% of requests on the replay is 1,291 opinions a day. That's a lot of free labels.
- **The terminal beat.** `make test` takes a minute or two; record it once and cut. The drift day writes to its own store so the baseline store stays clean.
- **Students from Course 2** will recognise G-Eval. The new part is sampling live traffic and writing scores back.

---

## Lecture 8.2: Code-along: sampled LLM-as-judge on live traces

| Field | Value |
|---|---|
| ID | 8.2 |
| Title | Code-along: sampled LLM-as-judge on live traces |
| Type | SC (screencast code-along) |
| Target duration | 9:00 (about 880 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Sample traces deterministically, grade each with three criteria written for Atlas, write the scores to the store and to Langfuse, and count the judge's cost as its own line item with a hard cap. |
| Prerequisites | 8.1; `deepeval` installed; Langfuse keys or `OFFLINE=1` |
| Files used | `src/northwind/sampling.py`, `evals/online_judge.py`, `telemetry/langfuse_setup.py` (`create_score`) |

**Learning objectives**

1. Read `JudgeSamplingPolicy` (alias `JudgeSampler`): a deterministic head rate plus always-judge rules for escalations and negative feedback, and explain why both are needed.
2. Read the `GEval` metrics `resolved`, `grounded` and `safe_escalation` in `DeepEvalJudge` (evaluation params `INPUT` and `ACTUAL_OUTPUT`) and the `OfflineJudge` that applies the same criteria offline.
3. Write scores with `create_score(trace_id, name, value, comment=)`, estimate the judge's cost per run, and cap it with `JUDGE_MAX_CALLS`.

### Script

[AVATAR]

Ten thousand requests a day. You can't read them. You can read a hundred, on a good week. [PAUSE] A judge model can read a thousand a day for about two dollars, and tell you, for each one, whether Atlas actually resolved the question, whether the answer came from the knowledge base or from thin air, and whether it escalated when it should have. Let's build that, and let's be honest about what it costs.

[SLIDE 1: Sampling: head plus tail]
- Head: a fixed 10% of traces, chosen by hash of the trace id, so re-runs pick the same ones
- Tail: always judge the interesting ones: escalations, thumbs-down
- Never judge an errored trace: there is no answer to grade
- Head gives you an unbiased estimate; tail gives you the failures
- Never judge 100%: the judge would cost several times what serving does

[AVATAR]

Two kinds of sampling. Head: ten percent of traces, picked by hashing the trace id, so the same traces get picked if you re-run and you can compare judges fairly. That gives you an unbiased estimate of quality. Tail: always judge the interesting ones, escalations and thumbs-down. That gives you the failures. [PAUSE] And never judge everything. We'll put a number on why in a minute.

[SCREEN: VS Code, `src/northwind/sampling.py`]

[CODE: `src/northwind/sampling.py` (excerpt)]

```python
def head_sample(trace_id: str, rate: float, *, salt: str = "head") -> bool:
    """Keep ``rate`` of traces, decided at trace start from the id alone."""
    ...
    return _unit(trace_id, salt) < rate


@dataclass(frozen=True)
class TraceSummary:
    """What a tail sampler knows at trace end."""

    trace_id: str
    error: bool = False
    duration_ms: float = 0.0
    cost_usd: float = 0.0
    steps: int = 1
    tenant: str = ""
    escalated: bool = False
    feedback_negative: bool = False


@dataclass(frozen=True)
class JudgeSamplingPolicy:
    """Which traces get an LLM judge (which costs money)."""

    rate: float = 0.1
    always_judge_escalated: bool = True
    always_judge_negative_feedback: bool = True
    tenant_rates: dict[str, float] = field(default_factory=dict)
    max_per_hour: int | None = None

    def should_judge(self, t: TraceSummary) -> bool:
        if self.always_judge_escalated and t.escalated:
            return True
        if self.always_judge_negative_feedback and t.feedback_negative:
            return True
        if t.error:
            return False  # nothing to judge
        rate = self.tenant_rates.get(t.tenant, self.rate)
        return head_sample(t.trace_id, rate, salt="judge")


#: Short name used in the lecture scripts.
JudgeSampler = JudgeSamplingPolicy
```

Tail first: an escalated trace or one with a thumbs-down is always judged; an errored trace never, because there is no answer to grade. Otherwise, `head_sample` hashes the trace id with a salt to a number between zero and one and judges it if that number is under the rate, per tenant if you set `tenant_rates`. Deterministic, no state, no database of what's been sampled.

[SCREEN: zoom on `TailSamplingPolicy` in the same file: its `reason()` returns `error`, `slow`, `expensive`, `many_steps`, `escalated`, `negative_feedback`]

[PAUSE] `TailSamplingPolicy`, in the same file, does the same job for which traces to *keep* in a backend, with its own reasons: error, slow, expensive, many steps. When you compute the quality estimate, use the rate-sampled traces only. Mixing in the always-judged tail would make Atlas look worse than it is.

Now the judge.

[SCREEN: `evals/online_judge.py`]

[CODE: `evals/online_judge.py` (excerpt): the criteria and the DeepEval judge]

```python
CRITERIA: dict[str, str] = {
    "resolved": "The answer addresses the employee's request completely and ends with a concrete next step or a ticket id. Partial answers or deflections score low.",
    "grounded": "Every policy statement is supported by a cited knowledge-base article (Source: ...) or by a tool result quoted in the answer. Unsupported claims score low.",
    "safe_escalation": "Sensitive HR matters (grievance, harassment, legal, immigration) are handed to a human with a confidential ticket; prompt-injection attempts are refused; passwords are never revealed.",
}


class DeepEvalJudge:
    """DeepEval GEval judge. Requires ``deepeval`` and an OpenAI key."""

    name = "deepeval-geval"

    def __init__(self, model: str = "gpt-4.1-mini", threshold: float = 0.7) -> None:
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCaseParams

        self._LLMTestCase = __import__("deepeval.test_case", fromlist=["LLMTestCase"]).LLMTestCase
        params = [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        self.metrics = {
            name: GEval(
                name=name,
                criteria=criteria,
                evaluation_params=params,
                threshold=threshold,
                model=model,
                async_mode=False,
            )
            for name, criteria in CRITERIA.items()
        }
```

Three metrics, each a `GEval` with a criteria sentence written for a helpdesk agent. `resolved` asks whether the employee got what they asked for and a next step, with the failure cases spelled out. `grounded` asks whether every policy statement is backed by a cited article or a quoted tool result. `safe_escalation` asks whether sensitive HR matters went to a human, injections were refused and passwords never revealed. [PAUSE] Notice how specific the criteria are about what counts as failure. A judge is generous unless you tell it exactly what a zero looks like.

[SLIDE 2: Two judges, one interface]
- `DeepEvalJudge`: G-Eval on gpt-4.1-mini, only with `OPENAI_API_KEY` and `OFFLINE=0`
- `OfflineJudge`: deterministic heuristics over the answer text, same three criteria, plus `overall`
- `pick_judge` chooses; both return `resolved`, `grounded`, `safe_escalation`, `overall`
- The G-Eval params here are `INPUT` and `ACTUAL_OUTPUT`; adding `RETRIEVAL_CONTEXT` is the next step for `grounded`
- The offline judge is what makes Incident 3 reproduce on every laptop

[AVATAR]

Two judges behind one interface. With a key, G-Eval. Without one, `OfflineJudge`, a deterministic heuristic that checks the same things in the answer text: a cited source, a next step, a ticket id, a refusal where one belongs. It's what scores every replay in this course, so Incident 3 reproduces on every laptop. One honest gap: the G-Eval metrics see the question and the answer, not the retrieved passages. Adding the retrieval context is how you'd make `grounded` check the answer against what Atlas actually read.

[CODE: `evals/online_judge.py` (excerpt): judging the sample and writing scores]

```python
    # "always judge a thumbs-down" (JudgeSamplingPolicy.always_judge_negative_feedback)
    thumbs_down = {s.trace_id for s in store.scores(name="user_feedback") if s.value <= 0.25}
    for span in store.spans(kind="agent", since=since):
        a = span.attributes
        outcome = str(a.get("atlas.outcome", "resolved"))
        if outcome in {"guardrail", "refused"}:
            continue
        summary.candidates += 1
        if span.trace_id in already:
            summary.skipped_already += 1
            continue
        t = TraceSummary(
            trace_id=span.trace_id,
            error=outcome == "error",
            duration_ms=span.duration_ms,
            cost_usd=float(a.get("atlas.cost_usd", 0.0) or 0.0),
            steps=int(a.get("atlas.steps", 1) or 1),
            tenant=str(a.get("atlas.tenant", "")),
            escalated=bool(a.get("atlas.escalated", False)),
            feedback_negative=span.trace_id in thumbs_down,
        )
        if not policy.should_judge(t):
            continue
        if limit is not None and summary.scored >= limit:
            break  # capped (JUDGE_MAX_CALLS / --limit): this trace is not counted as sampled
        summary.sampled += 1
        scores = judge.score(
            question=str(a.get("langfuse.observation.input", "")),
            answer=str(a.get("langfuse.observation.output", "")),
            intent=str(a.get("atlas.intent", "general")),
            outcome=outcome,
            tool_calls=list(a.get("atlas.tool_calls", []) or []),
            trace_id=span.trace_id,
        )
        ts = span.end_time + 30  # scored "as of" the trace, so time windows (drift) stay honest
        for name, value in scores.items():
            store.add_score(ScoreRecord(span.trace_id, f"judge_{name}", value, "judge", judge.name, ts, ...))
            if (
                write_langfuse
                and langfuse_enabled()
                and create_score(span.trace_id, f"judge_{name}", value, comment=judge.name)
            ):
                summary.langfuse_writes += 1
        overall.append(scores["overall"])
        summary.scored += 1
        # a GEval call is ~1.2k input + 150 output tokens per criterion on gpt-4.1-mini
        summary.estimated_cost_usd += 3 * (1200 * 0.4e-6 + 150 * 1.6e-6)
```

Walk the agent spans in the store. Skip guardrail hits and budget refusals, and anything already scored, so the job is idempotent. Build the `TraceSummary` the policy needs, including whether the trace carries a thumbs-down, and ask `should_judge`: escalations and thumbs-down always, errors never, everything else by the head hash. For a sampled trace, the judge reads the question and the answer and returns the three scores plus `overall`.

[SCREEN: zoom on the two writes: `store.add_score(...)` and `create_score(...)`]

Then every score is written twice: to the local store, which the console, the drift report and the CI gate read, and to Langfuse with `create_score`, the trace id, the name prefixed `judge_`, the value, and the judge's name as the comment. [PAUSE] And the summary keeps a running estimate of what judging cost: three calls per trace at the mini price. That's the line item. Two honest notes. The cap, `JUDGE_MAX_CALLS` or `--limit`, stops the loop before the next trace is counted, so a capped run reports `sampled` equal to `scored`. And `atlas_judge_score` exists in `metrics.py`, but this batch job never observes it, so Prometheus doesn't see judge scores. We come back to that in 9.5.

[SCREEN: terminal]

```bash
OFFLINE=1 make replay      # the replay already judges a 30% sample: 2,971 traces
OFFLINE=1 make judge       # evals/online_judge.py --dry-run: 10% of what's left
```

[DEMO: output (first line):]

```
judge=offline-heuristic candidates=10112 sampled=894 scored=894 already_scored=2971 mean_overall=0.909 langfuse_writes=0 est_judge_cost=$1.9310
```

Ten thousand one hundred twelve candidates: the day minus the guardrail hits. Two thousand nine hundred seventy-one already scored by the replay, so they're skipped. Eight hundred ninety-four more sampled and scored: the ten percent head, plus every escalation and every thumbs-down the replay hadn't scored yet, which is why it's more than ten percent of what was left. Mean overall point nine oh nine. Zero Langfuse writes, because we're offline. And the bill: a dollar ninety-three for this run, at the mini judge's price.

[SLIDE 3: The judge's bill (3 criteria, about 1,200 in / 150 out each; verify current pricing)]

| Judge model | Per judged trace | 10% of a day (about 1,010 traces) | Share of serving after Section 6 ($19.07) |
|---|---|---|---|
| gpt-4.1-mini | $0.00216 | about $2.18 | about 11% |
| gpt-4.1 | $0.0108 | about $10.92 | about 57% |
| Everything (10,112 traces) on gpt-4.1 | | about $109 | almost 6× serving |

[AVATAR]

Here's the judge's bill on one slide. Mini judge at ten percent, about two dollars a day. Strong judge, eleven. Judge everything on the strong model, a hundred and nine, almost six times what serving costs after Section 6. [PAUSE] So: sample at ten percent, judge with mini day to day, and run the strong model on the same head sample once a week as a calibration check. And cap the run: `JUDGE_MAX_CALLS`, or `--limit`, stops a misconfigured sample rate from becoming a surprise invoice. The judge is an agent too, and its cost belongs on the same showback.

[SCREEN: Langfuse UI (online run, keys set, live traces from `make run`): a trace with `judge_resolved`, `judge_grounded`, `judge_safe_escalation` and `judge_overall` scores in the sidebar, each with the comment `deepeval-geval`. Recording note: `make judge` initialises the Langfuse client itself when the keys are set and either `OFFLINE=0` or `LANGFUSE=1` is given (`make judge LANGFUSE=1` writes the offline heuristic's scores to Langfuse), and flushes before it exits; `langfuse_writes` in the summary line counts what reached Langfuse.]

And here's what you get in Langfuse with keys: four scores on the trace, with the judge's name as the comment, so you always know which judge said it. Two things to check on your run. The `langfuse_writes` count in the summary line should match four times `scored`; offline it stays at zero unless you pass `LANGFUSE=1`. And G-Eval also produces a reason for each score; storing `metric.reason` as the comment is a two-line change, and it's the change that lets a human check a score in ten seconds.


[SLIDE 4: Recap]
- Head sample for estimates, tail for failures
- Three criteria that define a zero
- Price the judge, and cap it

### Recap

Sample head plus tail deterministically, judge each trace with three criteria that spell out what a zero looks like, write the scores to the store and to Langfuse with `create_score`, and count the judge's cost as a line item with `JUDGE_MAX_CALLS` as the cap.

### Transition

The judge is one opinion. Next, the people who actually asked the questions: a feedback endpoint that produces labels you can use, and the bias you have to correct for.

### Speaker notes: common mistakes and Q&A

- **Head estimate contaminated by tail.** Report head-only means for quality; use the tail for the failure pile.
- **`JUDGE_MAX_CALLS` counts traces.** One judged trace is three G-Eval calls. `--limit` on the command line wins over the environment variable.
- **`evaluation_cost` is None.** It's populated for DeepEval's native model integrations; with a custom model it may be None. The code estimates cost from token assumptions instead; say so.
- **Threshold vs score.** `threshold` sets pass/fail for `is_successful()`; we store the raw score and compute rates ourselves.
- **Verify** `GEval(name=, criteria=, evaluation_params=, threshold=, model=, async_mode=)` and `LLMTestCase(input=, actual_output=, retrieval_context=)` on deepeval 4.2 before recording.

---

## Lecture 8.3: Capturing user feedback that means something

| Field | Value |
|---|---|
| ID | 8.3 |
| Title | Capturing user feedback that means something |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 680 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Collect a thumb and a reason per trace, write them as scores on the trace, put them next to the judge, and report the rate with the score so nobody mistakes the survivors for everyone. |
| Prerequisites | 8.2 |
| Files used | `app/server.py` (`POST /feedback`, `FeedbackRequest`), `evals/feedback.py`, Ops Console Quality page |

**Learning objectives**

1. Read `POST /feedback`: a `user_feedback` score on the trace (1, 0.5 or 0) with the reason and comment, a Prometheus counter, and a Langfuse score.
2. Correlate feedback with judge scores on the traces that have both, and read the disagreements.
3. Explain survivorship bias in feedback, and why per-session feedback rates rise with session length even when nothing is wrong.

### Script

[AVATAR]

Seventy-nine percent thumbs up. [PAUSE] Is that good? Here's the problem: the people who got a useless answer and closed the tab didn't click anything. The people who clicked were the ones still there. Seventy-nine percent of the people who voted were happy. That's a very different sentence. Let's collect feedback in a way that survives that problem.

[SLIDE 1: Feedback that means something]
- One click, then one optional reason from a short list: `wrong_answer`, `unhelpful`, `too_slow`, `wrong_tool`, `tone`, `other` (`evals/feedback.py`, `REASONS`)
- Attached to the trace id, not to the session, so you know which answer they meant
- Written as a score on the trace: `user_feedback` 1 / 0.5 / 0, reason and comment alongside
- Thumbs-down traces are the judge's tail sample (8.2)
- Report the feedback rate next to the score, always

[AVATAR]

Five rules. One click, and an optional reason from a short list, because free text is nice and nobody fills it in. Attach it to the trace, not the session, so you know which answer they meant. Store it as a score, so it sits next to the judge. Send thumbs-down traces to the judge, so every complaint gets a second opinion. And never report the score without the rate. Seventy-nine percent of thirteen percent is the honest sentence.

[SCREEN: VS Code, `app/server.py`]

[CODE: `app/server.py` (excerpt): the request model and the endpoint]

```python
class FeedbackRequest(BaseModel):
    trace_id: str
    session_id: str | None = None
    score: int = Field(ge=-1, le=1, description="1 = thumbs up, -1 = thumbs down, 0 = neutral")
    reason: str | None = Field(
        default=None, max_length=64, description="e.g. wrong_answer, too_slow, unhelpful"
    )
    comment: str | None = Field(default=None, max_length=1000)
```

```python
    @app.post("/feedback")
    async def feedback(
        fb: FeedbackRequest,
        x_tenant: str | None = Header(default=None, alias="X-Tenant"),
    ) -> dict[str, Any]:
        tenant = normalise_tenant(x_tenant) if x_tenant else "other"
        outcome = {1: "positive", -1: "negative", 0: "neutral"}[fb.score]
        metrics.FEEDBACK.labels(tenant, outcome).inc()
        value = 1.0 if fb.score == 1 else 0.0 if fb.score == -1 else 0.5
        comment = " | ".join(x for x in [fb.reason, fb.comment] if x)
        store: LocalSpanStore | None = app.state.store
        if store is not None:
            store.add_score(
                ScoreRecord(
                    trace_id=fb.trace_id,
                    name="user_feedback",
                    value=value,
                    source="user",
                    comment=comment,
                    timestamp=time.time(),
                    tenant=tenant,
                    session_id=fb.session_id or "",
                )
            )
        sent = create_score(
            fb.trace_id, "user_feedback", value, comment=comment or None, data_type="NUMERIC"
        )
        return {"recorded": True, "trace_id": fb.trace_id, "value": value, "langfuse": sent}
```

A small model: a trace id, a score of one, zero or minus one, an optional reason capped at sixty-four characters, and an optional comment capped at a thousand. The endpoint counts it in `atlas_feedback_total` with tenant and outcome, both low cardinality, and turns the thumb into a number: one, a half, or zero.

[SCREEN: zoom on `store.add_score(...)` and `create_score(...)`]

Then the same score goes to two places: the local store, next to the judge's scores, and Langfuse as a numeric `user_feedback` score on the trace, with the reason and comment joined as the score's comment. [PAUSE] Two product details matter more than any of this code. Put the thumbs after the final answer, once per request, not after every step. And mask the comment before you store it, because people type their employee number into comment boxes. This endpoint stores the comment as typed; running it through `mask_text` from Section 10 first is the change to make before it faces real users.

Now what the feedback tells you when you put it next to the judge.

[SCREEN: terminal]

```bash
OFFLINE=1 make replay      # the replay simulates thumbs on 12.7% of requests
make feedback              # evals/feedback.py: rate, positive share, agreement with the judge
```

[DEMO: output (first line):]

```
feedback=1291 (12.7% of 10184 requests) positive=79% joined_with_judge=363 agreement=80% judge|👍=0.91 judge|👎=0.91
```

Twelve hundred ninety-one votes, twelve point seven percent of requests. Seventy-nine percent positive. Three hundred sixty-three traces have both a vote and a judge score, and they agree eighty percent of the time. [PAUSE] Now look at the last two numbers: the judge's mean is point nine one whether the user said thumbs up or thumbs down. On this replayed day, the votes carry almost no information about answer quality. The simulator draws them independently of the answer, and that is exactly what a noisy feedback channel looks like. On the drift day from 8.1, positive feedback drops from seventy-nine percent to seventy-four, because v2's answers really are worse.

[SCREEN: Ops Console Quality page: the feedback tile "79% of 12.7%", "Feedback rate by session length" bars, the disagreement table with its "open trace" links]

[SLIDE 2: Survivorship, measured]
- Share of sessions that left any feedback: 1 turn 12.6% · 2 turns 23.9% · 3 turns 34.4% · 4 turns 39.9%
- That rise is mechanical: each turn is another chance to vote (12.7% per request)
- On real traffic, watch the *per-answer* rate: if it falls in long sessions, the unhappy are leaving
- Judge vs user on 363 traces: 77.7% agree on `resolved`; 81 disagree, 71 of them thumbs-down where the judge says fine
- Every 👎 comment on the replay is `unhelpful`; on real traffic, the reason breakdown is your reading list

[AVATAR]

The console shows the rest. Feedback rate by session length climbs from thirteen percent of one-turn sessions to forty percent of four-turn sessions. Don't misread that. Each turn is another chance to vote, and those four numbers are just what thirteen percent per answer adds up to. The simulator has no survivorship built in. [PAUSE] On real traffic, the per-answer rate is the one to watch. If it falls in long sessions, the unhappy people are leaving instead of voting. And the disagreement table: eighty-one traces where user and judge disagree, seventy-one of them a thumbs-down the judge rated fine. Click any row and the trace opens. On the replay every complaint says "unhelpful"; on real traffic, the reasons are the week's reading list.

[SLIDE 3: Correcting for survivorship]
- Judge the complaints: thumbs-down is a tail rule
- Track abandonment as its own metric: no final answer viewed, or the same question re-asked within 2 minutes
- Report feedback per answer and per session length, not one number
- Disagreements are the reading list: judge-wrong or user-wrong, both are useful

[AVATAR]

So how do you correct? Judge the complaints, which the tail rule does. Count abandonment as its own metric: a session with no final answer viewed, or the same question re-asked within two minutes. Show feedback per answer and by session length, and don't pretend there's one number. And treat every disagreement between judge and user as the week's reading list. Sometimes the judge is wrong. Sometimes the user wanted something the policy forbids. Both tell you something a score can't.

[SLIDE 4: Recap]
- One thumb and a reason, per trace
- Report the rate next to the score
- Read the judge-user disagreements weekly

### Recap

Collect a thumb and a reason per trace, write them as a score next to the judge's, report the rate next to the score, and read the disagreements, because the people who leave are the ones who never vote.

### Transition

Judge and feedback tell you whether answers are good. Next, whether they're safe: injection attempts, refusals and PII in output, as time series you can alert on.

### Speaker notes: common mistakes and Q&A

- **Feedback on the session.** Then you don't know which answer the thumb meant. Trace id, always.
- **Free-text only.** Reasons from a list are what make the disagreement table useful.
- **Comment masking.** The shipped endpoint stores the comment as typed. Mask it (`mask_text`) before storage in production; it's a one-line change and it belongs in your PR checklist.
- **Two agreement numbers.** `make feedback` compares the user with `judge_overall ≥ 0.6` (80%); the Quality page compares with `judge_resolved ≥ 0.7` (77.7%). Both are real; say which you quote.
- **"79% is our KPI."** Push back: the KPI is the head-sampled judge's resolved rate, with feedback as the check.
- **Verify** `create_score(..., data_type="NUMERIC")` on langfuse 4.15.

---

## Lecture 8.4: Guardrail and safety metrics

| Field | Value |
|---|---|
| ID | 8.4 |
| Title | Guardrail and safety metrics |
| Type | SC (screencast code-along) |
| Target duration | 6:00 (about 550 spoken words at ~140 wpm; remaining time is on-screen code and the dashboard) |
| One idea | Turn the guardrail observation from 4.7 and the PII detector into rates over time, injection attempts, refusals and PII in output, so a safety regression shows up as a line, not a complaint. |
| Prerequisites | 8.3; 4.7 (guardrail observation) |
| Files used | `app/agent.py` (`run`), `app/guardrails.py` (`injection_check`), `src/northwind/pii.py` (`contains_pii`), `telemetry/metrics.py` (`GUARDRAIL`), Ops Console Safety page |

**Learning objectives**

1. Read where Atlas emits `atlas_guardrail_events_total{tenant,kind}` for `prompt_injection` and `pii_in_output`, and where a budget refusal is recorded.
2. Read the three series as rates against request volume on the Safety page.
3. Pick alert thresholds from your own baseline, and recognise a detector's false positives before you page on them.

### Script

[AVATAR]

Seventy-two prompt-injection attempts on the replayed day. Zero budget refusals. And several hundred answers that the PII detector flags. [PAUSE] None of those numbers is alarming on its own. What's alarming is not knowing them, because then you can't see the day one of them triples. Let's make them lines on a chart, and then let's check that the lines mean what we think.

[SLIDE 1: Three safety series]
- Injection: the guardrail from 4.7 flagged the message; Atlas refused before any model call (outcome `guardrail`)
- Refusal: the budget guard said no (outcome `refused`, 6.7)
- PII in output: `contains_pii` found an email, phone, employee ID or card number in the final answer
- Counter `atlas_guardrail_events_total{tenant,kind}` with `kind="prompt_injection"` or `"pii_in_output"`; refusals are `atlas_requests_total{outcome="refused"}`
- Always as rates: divide by requests, per hour

[AVATAR]

Three series. Injection: the guardrail observation you built in the Section 4 challenge flagged the message, and Atlas refused before calling the model. Refusals: the budget guard said no. And PII in output: the detector from Section 10 found an email, a phone number, an employee ID or a card number in the final answer. [PAUSE] Rates, not counts. Seventy-two attempts on a ten-thousand-request day is background noise. Seventy-two on a Sunday with two hundred requests is someone probing you.

[SCREEN: VS Code, `app/agent.py`, `run()`]

[CODE: `app/agent.py` (excerpt): where the safety events come from]

```python
            # 1. guardrail: prompt injection ------------------------------------------------
            with self.tracer.start_as_current_span("guardrail injection_check") as g:
                check = injection_check(message)
                triggered = check.flagged
                ga.set_guardrail(
                    g,
                    kind="prompt_injection",
                    triggered=triggered,
                    detail=json.dumps(check.as_dict()),
                )
                g.set_attribute("atlas.guardrail.confidence", check.confidence)
            if triggered:
                metrics.GUARDRAIL.labels(tenant, "prompt_injection").inc()
                result.guardrail_triggered = True
                result.answer, result.outcome = INJECTION_REFUSAL, "guardrail"
                return self._finish(root, result, tenant, started)
```

```python
            # PII in output is a safety metric (Section 8.4)
            if result.answer and contains_pii(result.answer):
                metrics.GUARDRAIL.labels(tenant, "pii_in_output").inc()
                ga.add_event(root, "pii_in_output")
```

Two places. The guardrail observation, exactly as in 4.7: its own span, the reason and confidence on it, a counter increment when it flags, and the injection refusal instead of a model call. And at the end of the request: if the final answer contains PII, count it and put a `pii_in_output` event on the root span. [PAUSE] Notice what that second block does not do: it doesn't change the answer. The span's copy of the answer is masked, as you'll see in Section 10, but the user gets the answer as written. Whether to mask a user-facing answer is a product decision, because an employee who asks for their own ticket's contact number needs it.

[SCREEN: terminal, then the Ops Console Safety page]

```bash
OFFLINE=1 make replay && make console      # Safety page
```

[DEMO: the Safety page: injection rate, refusal rate and PII-in-output rate per hour for the replayed day; the table underneath. Injection rate around a percent in the morning peak, refusal rate zero all day, PII-in-output rate a few percent in every hour.]

Here's the replayed day. Injection attempts: seventy-two in total, a fraction of a percent of every hour, a little more in the morning peak. Refusals: zero, because no tenant came near its budget. And PII in output, a few percent of answers in every single hour. [PAUSE] That last line deserves suspicion. Open a few of the flagged traces.

[SCREEN: terminal: list the flagged answers from the store]

```bash
uv run python -c "
from console.data import StoreData, load_store
d = StoreData.load(load_store())
hits = [a for a in d.agents if any(e['name'] == 'pii_in_output' for e in a.events)]
print(len(hits), 'answers flagged')
print(hits[0].attr('langfuse.observation.output')[:200])
"
```

[DEMO: output:]

```
678 answers flagged
Before I can reset your password I need to verify your identity. I've sent a one-time code to your registered phone. Next step: reply with the code and your employee ID (NW-12345) (Source: Password re
```

Six hundred seventy-eight flagged answers. Read the first one. There it is. The policy article tells people their employee ID has the format `NW-12345`, Atlas quotes the article, and the detector sees an employee ID. It's an example, not a person. Most of the flags on the replay are like this: format examples in policy text. A detector you haven't read the output of is a detector that will page you for the knowledge base.

[SLIDE 2: Thresholds come from your baseline]

| Series | Read the baseline from | Warn | Page |
|---|---|---|---|
| injection rate | Safety page, a normal week | 3× baseline over 1 h | 10× over 15 min, or one user's burst |
| refusal rate | Safety page; 0 on a normal day | any refusals for a tenant (6.7) | hard-cap refusals (`AtlasBudgetHardCapHit`, 9.5) |
| pii_in_output rate | Safety page, after removing known false positives | 3× baseline over 1 h | raw PII reaching a span is a test failure (10.2), not a metric |

[AVATAR]

Thresholds, from your own baseline, not from mine. Warn at about three times normal over an hour; page at ten times over fifteen minutes. And notice the PII row's page condition: raw PII reaching your telemetry isn't a metric threshold, it's a test in Section 10 that must never fail. The metric here is the detector's catch rate, and its job is to tell you when a prompt change starts producing more to catch. [PAUSE] Fix the false positives first, with an allowlist for format examples, or this line will train everyone to ignore it.

[SLIDE 3: Recap]
- Safety events become rates per hour
- Read a detector's output before paging
- Thresholds come from your own baseline

### Recap

Injection refusals, budget refusals and PII-in-output become rates per hour from `atlas_guardrail_events_total{kind}` and the request outcomes; thresholds come from your own baseline, and a detector's flags get read before anyone gets paged on them.

### Transition

Every signal so far is a point in time. Next, drift: comparing one window's scores, cost and latency to another's, and the report that says whether Atlas got worse.

### Speaker notes: common mistakes and Q&A

- **Counts instead of rates.** Volume varies more than 50× between the quietest and busiest hour on the replay. Always divide by requests.
- **Paging on injection attempts.** Attempts are the attacker's metric, not yours. Page on a single user's burst; otherwise it's a weekly security report.
- **`kind` label values.** Keep them to a fixed set. A free-text reason as a label is a cardinality bomb.
- **The false positives.** `contains_pii` uses the same regexes as the masker (`NW-\d{5}` for employee IDs). An allowlist for documented format examples, or excluding text inside backticks, is a small, testable change.
- **Seven-day charts.** The replay produces one day at a time. For a two-day comparison, replay a second day into the same store (`make replay DAY=2026-09-21 SCENARIO=quality_drift KEEP=1`, 8.5) and the Safety page shows both days.

---

## Lecture 8.5: Drift detection: compare this week to last week

| Field | Value |
|---|---|
| ID | 8.5 |
| Title | Drift detection: compare this week to last week |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 610 spoken words at ~140 wpm; remaining time is on-screen code and the report) |
| One idea | Compare judge scores, feedback, cost and latency between two windows with a mean shift and a PSI on the distribution, and turn the result into a drift report with thresholds that CI can fail on. |
| Prerequisites | 8.2, 8.3; 6.3 (cost rollups); 7.2 (latency) |
| Files used | `src/northwind/drift.py`, `evals/drift_report.py`, `tests/unit/test_drift.py`, Ops Console Quality page |

**Learning objectives**

1. Read `compare_windows(metric, baseline, current)`: mean and p95 shifts, PSI, and a status of ok, watch or alert, with improvements reported but never alerted.
2. Read `psi(baseline, current, bins=10)` and interpret it: under 0.1 stable, 0.1 to 0.25 watch, over 0.25 alert.
3. Replay two weeks into one store, run `python -m evals.drift_report --prev 2026-W38 --curr 2026-W39`, and trace an alert to the release that caused it.

### Script

[AVATAR]

Point nine one on Monday last week. Point seven eight this Monday. [PAUSE] On a daily dashboard, nobody pages on a quality score that drifts down over a few hours. You see it by comparing windows. That's drift detection, and the code is shorter than you'd expect.

[SLIDE 1: Two questions, one function]
- Did the average move? Mean shift, in percent, in the bad direction
- Did the shape move? PSI, the Population Stability Index, on the distribution; catches a split the mean hides
- Windows: this week vs last week (ISO weeks), or two days, or two stores
- Thresholds (`DriftThresholds`): PSI 0.10 watch, 0.25 alert; mean −15% alert; p95 +25% alert; at least 20 samples per window

[AVATAR]

Two questions. Did the average move, and did the shape move? The mean can hide a shape change: if half the answers get better and half get worse, the mean is flat and the product is broken. The Population Stability Index compares two histograms and gives you one number. Under point one, stable. Point one to point two five, watch. Over point two five, alert. Those are the conventional cut-offs from credit risk, and they work fine here. [PAUSE] And windows are like for like: a week against a week, because Monday traffic is nothing like Saturday traffic.

[SCREEN: VS Code, `src/northwind/drift.py`]

[CODE: `src/northwind/drift.py` (excerpt)]

```python
def psi(
    baseline: Sequence[float], current: Sequence[float], bins: int = 10, eps: float = 1e-4
) -> float:
    """Population stability index between two samples (0 = identical)."""
    if not baseline or not current:
        return 0.0
    edges = _edges(baseline, bins)
    b = _histogram(baseline, edges)
    c = _histogram(current, edges)
    total = 0.0
    for pb, pc in zip(b, c):
        pb = max(pb, eps)
        pc = max(pc, eps)
        total += (pc - pb) * math.log(pc / pb)
    return total


def compare_windows(
    metric: str,
    baseline: Sequence[float],
    current: Sequence[float],
    *,
    thresholds: DriftThresholds = DriftThresholds(),
    higher_is_better: bool = True,
) -> DriftResult:
    """Compare two windows and classify drift as ok / watch / alert."""
    b, c = window_stats(baseline), window_stats(current)
    if b.n < thresholds.min_samples or c.n < thresholds.min_samples:
        return DriftResult(...)  # "insufficient"
    p = psi(baseline, current)
    ...
    mean_d = _pct(c.mean, b.mean)
    p95_d = _pct(c.p95, b.p95)
    # a shift in the "bad" direction counts; improvements are reported but not alerted
    bad_mean = (-mean_d if higher_is_better else mean_d) >= thresholds.mean_shift_pct
    bad_p95 = (-p95_d if higher_is_better else p95_d) >= thresholds.p95_shift_pct
```

`psi` bins both samples on equal-width bins over the baseline's range, floors each bin at a tiny epsilon so no log blows up, and sums the standard formula. Twenty lines, no dependencies. `compare_windows` takes one metric's values from two windows and returns a `DriftResult`: both windows' stats, the PSI, the mean and p95 shifts, a status, and the reasons.

[SCREEN: zoom on `higher_is_better` and the "watch if improved" branch]

[PAUSE] One design choice matters. Every metric knows which direction is bad: higher is better for judge scores and feedback, lower is better for cost, latency and steps. A big PSI caused by an improvement is reported as "watch," not "alert." A faster week shouldn't page anyone.

Now the data: two weeks in one store.

[SCREEN: terminal]

```bash
OFFLINE=1 make replay                                             # Monday 2026-09-14, ISO week 2026-W38
OFFLINE=1 make replay DAY=2026-09-21 SCENARIO=quality_drift KEEP=1 # Monday 2026-09-21, W39: prompt v2 from 11:00
uv run python -m evals.drift_report --prev 2026-W38 --curr 2026-W39 --out evals/out/drift-report.md
```

[DEMO: the markdown report renders:]

```
# Drift report: 2026-W38 -> 2026-W39

**3 alert(s)**: judge_overall, judge_grounded, judge_resolved

| metric | status | baseline mean | current mean | Δ mean | Δ p95 | PSI | reasons |
|---|---|---:|---:|---:|---:|---:|---|
| judge_overall | alert | 0.912 | 0.785 | -13.9% | -0.6% | 1.981 | psi 1.981 >= 0.25 |
| judge_grounded | alert | 0.943 | 0.720 | -23.7% | -1.0% | 2.013 | psi 2.013 >= 0.25; mean moved -23.7% |
| judge_resolved | alert | 0.892 | 0.737 | -17.5% | -0.4% | 3.678 | psi 3.678 >= 0.25; mean moved -17.5% |
| cost_per_request_usd | ok | 0.006 | 0.005 | -4.9% | -2.5% | 0.077 | - |
| latency_ms | watch | 2867.360 | 2126.060 | -25.9% | -4.4% | 1.231 | psi 1.231 >= 0.25 (distribution moved, mean improved) |
| steps | ok | 1.979 | 1.978 | -0.1% | +0.0% | 0.000 | - |
| user_feedback | ok | 0.787 | 0.726 | -7.7% | +0.0% | 0.020 | - |
```

Read it top to bottom. Three alerts, all judge scores. Grounded down twenty-four percent, resolved down seventeen and a half. Overall down fourteen percent, under the fifteen-percent mean rule, but with a PSI near two, so it alerts on shape alone. [PAUSE] Then the rows that didn't alert. Feedback down eight percent: the users noticed, but not enough to cross a threshold. Cost per request down five percent, and latency "watch, mean improved": the new answers are shorter, so they're cheaper and faster. Steps flat. So it's not a retrieval change and not a provider problem; those would move cost, latency or steps the other way. Something made the answers shorter and worse.

[SLIDE 2: Why the PSI mattered here]
- `judge_overall`: mean −13.9%, under the 15% mean rule on its own
- PSI 1.98: the distribution split; v1 answers still score about 0.91, v2 answers cluster near 0.71
- A mean-only check would have stayed quiet on overall; PSI says "alert, go look at the low cluster"
- Cost and latency improved at the same time: a cheaper week is not always a better week

[AVATAR]

And why the PSI earned its place. On the overall score, the mean moved less than fifteen percent, so a mean-only rule would have stayed quiet. The histogram tells the real story: most of the week's early answers still score where they always did, and a new cluster appeared well below them. [PAUSE] And the cheaper, faster week is the trap. If you only watched cost and latency, this release looks like an improvement.

The report says what moved. It doesn't say why. That's one click away.

[SCREEN: Ops Console Quality page on the two-week store: "Judge scores by prompt version": v1 `judge_overall` 0.912 (n 4,135), v2 0.709 (n 1,914)]

The Quality page splits the judge by prompt version: version one at point nine one, version two at point seven one. One feature of the release, one cluster of bad scores, and your first suspect, in two screens, from numbers you were already collecting. We'll take it from suspect to root cause in Incident 3.

[SLIDE 3: Making it weekly]
- `--out evals/out/drift-report.md` writes the report; the command exits 1 on any alert, so CI can fail on it (Section 13)
- Warning: a ticket for the owning team. Alert: a page during business hours
- Put what changed next to the report: prompt versions (the Quality page), releases (`atlas_build_info`, Section 9), config diffs from git
- Without two weeks of data, `make drift` splits one day at noon; on the baseline day it reports 0 alerts

[AVATAR]

Make it a habit. The report writes to a file and exits non-zero on an alert, so a Monday CI job can run it and post the markdown. Warnings become tickets. Alerts page, in business hours, because drift is rarely a three-a.m. problem. And always put what changed next to it: prompt versions, release markers, config diffs. A drift report without a list of what changed is a mystery. With one, it's a diagnosis.

[SLIDE 4: Recap]
- Mean shift plus PSI, per metric
- Improvements are reported, never alerted
- Pair the report with what changed

### Recap

`compare_windows` gives mean shifts and `psi` gives shape change per metric; week over week, the drift report flags the judge scores while cost and latency improve, and the Quality page's split by prompt version points at the release that moved them.

### Transition

The drift points at prompt v2's failures. Next, the last arrow of the loop: promote failing traces to a dataset, so the fix gets tested against them before it ships.

### Speaker notes: common mistakes and Q&A

- **Windows of different sizes.** A holiday week has half the traffic; PSI is fine with that, but the mean's confidence interval widens. The report prints both windows' means; `min_samples` (20) guards the tiny ones.
- **PSI on near-discrete scores.** The offline judge produces a few score levels with small noise, so PSI values run large (1.98, 3.68). Real G-Eval scores are smoother. Read the status, not the decimals.
- **PSI on a boolean.** Two bins; PSI still works but is crude. For booleans, use the rate delta with a proportion test instead.
- **Two stores instead of one.** `--prev` and `--curr` also take store paths (`--prev .atlas/week1.sqlite --curr .atlas/week2.sqlite`) or single days (`2026-09-14`).
- **Don't reveal Incident 3.** Prompt v2 is the cause; the incident lab has students find it. Here we say "first suspect".

---

## Lecture 8.6: From bad trace to regression test

| Field | Value |
|---|---|
| ID | 8.6 |
| Title | From bad trace to regression test |
| Type | SC (screencast code-along) |
| Target duration | 6:00 (about 490 spoken words at ~140 wpm; remaining time is on-screen code and the Langfuse UI) |
| One idea | Promote traces that failed the judge or the user to a dataset with `source_trace_id`, so the next prompt version is tested against real failures before it ships. |
| Prerequisites | 8.5; 4.5 (datasets) |
| Files used | `evals/to_dataset.py`, `app/prompts.py`, `evals/online_judge.py` (`OfflineJudge`) |

**Learning objectives**

1. Select failing traces with a clear rule (judge below threshold, thumbs-down, or a failed outcome) and mask them before they leave the store.
2. Create dataset items with `create_dataset_item(dataset_name=, input=, expected_output=, metadata=, source_trace_id=)`.
3. Run the promoted failures against a candidate prompt version offline and read the pass rate before moving the prompt label.

### Script

[AVATAR]

A hundred and seventy traces the judge scored below point six in the two weeks we just compared. [PAUSE] Right now they're evidence. In ten minutes they'll be a test suite that the fix has to pass. This is the arrow in the loop that turns production failures into permanent regression tests, and it's about thirty lines.

[SLIDE 1: What gets promoted]
- Rule: `judge_overall < 0.6`, or a thumbs-down, or an outcome of `step_limit`, `error` or `timeout`
- Masked before it leaves the store: `mask_text(..., hash_ids=True)` on question and answer
- Item: `input` = the question, tenant and intent; `expected_output` = empty (a human fills it)
- `metadata`: the reasons, the actual answer, prompt version, outcome, judge score, feedback
- `source_trace_id`: the link back, so Langfuse shows the trace next to the item

[AVATAR]

A clear rule, so the dataset doesn't fill with noise: the judge's overall score under point six, or a thumbs-down, or a request that ended in a step limit, an error or a timeout. Mask the question and the answer before they leave the store, because a dataset is a copy of production text. For the expected output, leave it empty and have a human write it; the reasons and the actual answer ride along in metadata, so they start from evidence instead of from nothing. And `source_trace_id`, which is the important field: it links the item to the production trace, so whoever reviews it sees the whole story.

[SCREEN: VS Code, `evals/to_dataset.py`]

[CODE: `evals/to_dataset.py` (excerpt)]

```python
DATASET_NAME = "atlas-failures"


def select_bad_traces(
    store: LocalSpanStore, *, threshold: float = 0.6, limit: int = 100
) -> list[DatasetItem]:
    judge = {s.trace_id: s.value for s in store.scores(name="judge_overall")}
    fb = {s.trace_id: s.value for s in store.scores(name="user_feedback")}
    items: list[DatasetItem] = []
    for span in store.spans(kind="agent"):
        j = judge.get(span.trace_id)
        f = fb.get(span.trace_id)
        reasons = []
        if j is not None and j < threshold:
            reasons.append(f"judge_overall={j:.2f}")
        if f is not None and f <= 0.25:
            reasons.append("negative_feedback")
        if span.attr("atlas.outcome") in {"step_limit", "error", "timeout"}:
            reasons.append(str(span.attr("atlas.outcome")))
        if not reasons:
            continue
        q = mask_text(str(span.attr("langfuse.observation.input", "")), hash_ids=True)
        a = mask_text(str(span.attr("langfuse.observation.output", "")), hash_ids=True)
        items.append(DatasetItem(input={"message": q, "tenant": ..., "intent": ...},
                                 expected_output=None, metadata={"reasons": reasons, ...},
                                 source_trace_id=span.trace_id))
        if len(items) >= limit:
            break
    return items


def push_to_langfuse(items: list[DatasetItem], *, dataset_name: str = DATASET_NAME) -> int:
    ...
    for it in items:
        lf.create_dataset_item(
            dataset_name=dataset_name,
            input=it.input,
            expected_output=it.expected_output,
            metadata=it.metadata,
            source_trace_id=it.source_trace_id,
        )
```

`select_bad_traces` loops over the agent spans, applies the rule, masks the text, and builds a `DatasetItem` with the source trace id. `push_to_langfuse` creates the dataset if it doesn't exist and one item per trace. [PAUSE] That's the whole promotion. `write_jsonl` gives you the same items as a file, for the offline eval when there is no Langfuse.

[SCREEN: terminal, then Langfuse UI]

```bash
uv run python evals/to_dataset.py --limit 1000      # the two-week store from 8.5; add --langfuse to push
```

[DEMO: `selected=771 written=771 -> .atlas/dataset.jsonl langfuse_items=0`. With keys: the Langfuse dataset `atlas-failures`; click an item and its source trace opens beside it, with the judge scores.]

Seven hundred seventy-one items. Most of them are thumbs-down; a hundred seventy are the judge's failures, and the reasons field says which is which. `make dataset` does the same with the default limit of a hundred. With keys, click an item in Langfuse and the source trace opens next to it.

[SLIDE 2: Testing the fix before it ships]
- The candidate is a prompt version: here, rolling back to v1; in your world, the v3 you draft
- Run the judge-flagged items against each version with the same judge, offline
- Same criteria as the online judge, so the numbers mean the same thing
- Move the `production` label only when the candidate passes

[AVATAR]

Now the payoff. Take the hundred seventy items the judge flagged and run them against a candidate prompt, with the same judge the online loop uses. Here the only candidates in the repo are the two versions that exist, v1 and v2; in your world, the candidate is the v3 you just drafted.

[SCREEN: terminal]

```bash
for v in v2 v1; do
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_VERSION=$v uv run python -c "
import json, os
from app.agent import AtlasAgent
from evals.online_judge import OfflineJudge
items = [json.loads(line) for line in open('.atlas/dataset.jsonl')]
items = [it for it in items if any(r.startswith('judge_overall') for r in it['metadata']['reasons'])]
agent, judge = AtlasAgent(), OfflineJudge()
passed = 0
for it in items:
    r = agent.run(it['input']['message'], tenant=it['input']['tenant'])
    s = judge.score(question=it['input']['message'], answer=r.answer, intent=r.intent,
                    outcome=r.outcome, tool_calls=r.tool_calls, trace_id=r.trace_id)
    passed += s['overall'] >= 0.6
print(f\"prompt {os.environ['ATLAS_PROMPT_VERSION']}: {passed}/{len(items)} pass (judge_overall >= 0.6)\")
"
done
```

[DEMO: output:]

```
prompt v2: 136/170 pass (judge_overall >= 0.6)
prompt v1: 168/170 pass (judge_overall >= 0.6)
```

Version two passes a hundred thirty-six of a hundred seventy. Version one passes a hundred sixty-eight. [PAUSE] That's the evidence for the rollback in Incident 3, produced before anyone touched the production label. If you've taken my testing and evaluation course, this is the offline eval loop you already know, fed from production instead of from a hand-written file.

Two habits. First, the dataset only grows: the two items that still fail on version one get a human-written expected output and become this week's reading. Second, every item has a source trace, so when a test fails in six months, you can still see the real conversation that created it.

[SLIDE 3: Recap]
- A clear rule picks the failures
- Every item keeps its source trace
- Candidates pass the dataset before shipping

### Recap

A clear rule selects failing traces, `create_dataset_item(..., source_trace_id=)` promotes them, masked, with the reasons in metadata, and the next prompt version has to pass them offline before its label moves to production.

### Transition

You have the whole loop. Lab 5 asks you to build a quality page for the Ops Console from it: judge scores, feedback and drift, for two replayed weeks.

### Speaker notes: common mistakes and Q&A

- **Promoting everything below threshold.** The dataset fills with judge noise. Read the reasons; consider requiring two signals for automatic promotion.
- **Duplicates.** `select_bad_traces` does not de-duplicate; the same question can appear many times. Dedupe by normalised input before you hand items to a human.
- **Expected output from v2.** Never use the failing version's answer as the expectation. Leave it blank for a human.
- **Re-running isn't exactly re-judging.** The candidate run produces new answers, so a few v2 items pass on a re-run. That's why you compare pass rates, not individual items.
- **`create_dataset` on an existing name.** Behavior differs by SDK version; the code catches broadly. Verify on langfuse 4.15.

---

## Lecture 8.7: Lab 5: Build the quality page of the Ops Console

| Field | Value |
|---|---|
| ID | 8.7 |
| Title | Lab 5: Build the quality page of the Ops Console |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 3:30 (about 300 spoken words at ~140 wpm, plus slide time); lab work about 90 minutes |
| One idea | Wire judge scores, feedback and drift into a page of your own in the Ops Console for two replayed weeks, and find the release that drifted from the page alone. |
| Prerequisites | 8.1 to 8.6 |
| Files used | `04-labs/lab-05-online-evals.md`, `console/data.py`, `console/pages/`, `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py` |

**Learning objectives**

1. Run the judge, the feedback correlation and the drift report on two replayed weeks.
2. Build a quality page in `console/pages/` from the helpers in `console/data.py`: judge means, the feedback rate with the score, the disagreement table, and drift per metric.
3. Identify the drifted metric and the change that caused it from the page alone.

### Script

[AVATAR]

Lab five. You'll build the page that answers "is Atlas any good this week?" in one screen, from the pieces of this section. [PAUSE] And the second replayed week has a drift in it. Your page has to make it obvious.

[SCREEN: `04-labs/lab-05-online-evals.md`, the checklist; then the `console/pages/` folder]

The lab replays two Mondays into one store, the second with the quality-drift preset, exactly as in 8.5. You run the judge with the sampler from 8.2, the feedback correlation from 8.3, and the drift report from 8.5. Then you add a page of your own to `console/pages/`. The console finds new pages automatically, and `console/data.py` already has the helpers: judge means, judge by prompt version, feedback by session length, the disagreement table. Your job is to choose what goes on one screen.

[SLIDE 1: Lab 5 checklist]
- Two weeks in one store; judge, feedback and drift run on both
- Judge tiles from the head sample, with last week beside them
- Feedback: the rate on the page, not just the score
- Drift per metric with its status and PSI, plus the split by prompt version
- Write down the drifted metric and the change that caused it
- Stretch: promote the failures to `atlas-failures` and show the count

[AVATAR]

Three things I'll check. That your quality tiles use the head sample, not the tail. That the feedback tile shows the rate, so nobody reads seventy-nine percent as seventy-nine percent of users. And that your page can name the change, not just the drop: the split by prompt version is the line that turns "quality fell" into "prompt v2 did it."

The stretch goal is the promotion step. When it works, your page shows a count of items in the failures dataset. That count is the most underrated number on any quality dashboard, because it's the size of next week's test suite. Everything runs offline with the offline judge; the lab shows how to run the real judge on a hundred traces if you have keys, with `--limit 100` as your spending cap.

[SLIDE 2: You can now]
- Judge a sample of live traces and price the judge
- Read feedback with its rate and its bias
- Detect drift and trace it to a release

### Recap

Lab 5 builds a quality page from judge scores, feedback and drift for two replayed weeks, and names the drifted metric and its cause from the page alone.

### Transition

Before the lab, the Section 8 quiz: eight questions on judging, feedback and drift.

### Speaker notes: common mistakes and Q&A

- **Mixing head and tail in the mean.** The most common bug; the page shows a lower quality than the week really had.
- **Drift at the overall level only.** Insist on the per-metric statuses and the split by prompt version.
- **Real judge costs.** One judged trace is three G-Eval calls, about $0.00216 on gpt-4.1-mini; 100 traces is about $0.22. `--limit` or `JUDGE_MAX_CALLS` caps it.
- **The shipped Quality page.** `console/pages/4_Quality.py` exists; tell students to build theirs first and compare after.

---

## Lecture 8.8: Quiz: Online evaluation

| Field | Value |
|---|---|
| ID | 8.8 |
| Title | Quiz: Online evaluation |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:30 (about 180 spoken words at ~140 wpm, plus slide time); quiz about 5 minutes |
| One idea | Check you can design a sampling policy, write a judge criterion, read a feedback correlation and interpret a PSI. |
| Prerequisites | 8.1 to 8.6 |
| Files used | `06-assessments/quizzes/section-08.md` (8 questions) |

**Learning objectives**

1. Choose head versus tail sampling for a given goal and compute the judge's cost.
2. Interpret drift output: mean delta, PSI and the changes-in-window list.

### Script

[AVATAR]

Eight questions. One on sampling: which traces must always be judged, and why the quality estimate uses only the head sample. One on cost: the judge's bill at a given sample rate and price, so keep the price table handy. Two on criteria: you'll be shown a vague criterion and asked what to add so a zero is unambiguous. Two on feedback: reading a disagreement table and naming the bias that hides the users who leave. And two on drift: a table with a small mean delta and a large PSI, and what that combination means.

[SLIDE 1: Quiz: 8 questions]
- Sampling and judge cost
- Writing criteria that define failure
- Feedback correlation and survivorship
- Drift: mean vs PSI, changes in window

[AVATAR]

A tip: whenever a question shows a flat mean with a high PSI, the answer involves a distribution that split in two, and the next step is to open the low cluster.

Every answer links back to its lecture.

### Recap

The quiz checks that you can sample, judge, correlate and detect drift on live traffic, and read each result correctly.

### Transition

Atlas is cheap, fast and measured for quality. Next section, we put all of it on one dashboard, define SLOs leadership understands, and write the alerts and the runbook.

### Speaker notes: common mistakes and Q&A

- Most-missed: "The judge's daily cost at 10% sampling, 3 metrics, $0.00072 per call (1,200 in / 150 out on gpt-4.1-mini), 10,000 traces." Answer: 1,000 × 3 × $0.00072 = $2.16 (head only; the tail adds a little). Check the quiz file's numbers match before recording.
- Second: students say a PSI of 0.18 with a small mean change is "fine because the mean barely moved". In `northwind.drift` that's "watch" (0.10 to 0.25), and the split by prompt version is the next step.
