# Section 8: Quality in Production: Online Evaluation and Drift

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 52 minutes (8 lectures, including one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Judge output on screen: score and reason side by side, reason in a callout.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on deepeval 4.2 / langfuse 4.15. Judge prices as of 2026-09-28: verify current pricing."
> **Companion course tie-in:** Lecture 8.6 hands failing traces to the offline-eval workflow taught in *AI Agent Testing & Evaluation*. One spoken line; never required.

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (match `03-code/`):** `northwind.sampling` (`JudgeSamplingPolicy.should_judge`, `TraceSummary`, `head_sample`; `JudgeSampler` is an alias), `evals/online_judge.py` (`CRITERIA`, `OfflineJudge`, `DeepEvalJudge`, `pick_judge`, `run_judge`; `make judge`), `evals/feedback.py` (`record_feedback`, `correlate`; `make feedback`), `evals/drift_report.py` (`compare_split`, `compare_stores`, `render`; `make drift`), `northwind.drift` (`compare_windows`, `psi`, `DriftResult`, `drift_report_markdown`), `evals/to_dataset.py` (`select_bad_traces`, `write_jsonl`, `push_to_langfuse`; `make dataset`), `telemetry/metrics.py` (`GUARDRAIL` / alias `GUARDRAIL_EVENTS`, `JUDGE_SCORE`, `FEEDBACK`), `app/server.py` (`POST /feedback`). Langfuse calls verified on 4.15: `create_score(trace_id=, name=, value=, data_type=, comment=)`, `create_dataset(name=)`, `create_dataset_item(dataset_name=, input=, expected_output=, metadata=, source_trace_id=)`, `api.trace.list(from_timestamp=, to_timestamp=, tags=, limit=)`. Note: `update_current_trace` does not exist on langfuse 4.15; trace-level attributes are set with `propagate_attributes(...)` (Section 4).

**The numbers card (one set of figures for the section):**

| Item | Value |
|---|---|
| Traffic | 10,184 requests, 4,000 sessions a day (after the Section 6 levers: $19.21 a day) |
| Judge sampling | 10% head sample (1,000 traces) + tail sample of every error, thumbs-down, escalation and 5+-step trace (about 180) = about 1,180 traces a day |
| Judge metrics | `resolved`, `grounded`, `safe_escalation`: 3 calls per trace, about 3,540 calls a day |
| Judge cost | gpt-4.1-mini: about 2,200 in / 150 out per call = $0.00112; $3.96 a day (21% of serving). gpt-4.1: $0.0056 per call, $19.82 a day |
| Judge scores (normal week) | resolved 0.83, grounded 0.90, safe_escalation 0.97 |
| User feedback | 9% of sessions (about 360 a day); 78% thumbs up; thumbs-down always judged |
| Guardrails | injection attempts 22 a day (0.22%), refusal rate 1.1%, PII in output 0.3% |
| Drift (week 39 vs week 38) | resolved 0.83 → 0.79, `policy_question` 0.85 → 0.76, PSI 0.18 (warning); cost per request +4%; p95 flat. Cause: prompt v2 (sets up Incident 3) |
| Promoted failures | 41 traces to dataset `atlas-failures` |

---

## Lecture 8.1: Offline evals are not enough

| Field | Value |
|---|---|
| ID | 8.1 |
| Title | Offline evals are not enough |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 590 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | A passing test suite tells you about yesterday's questions; production quality needs a judge, real feedback and a drift check on today's traffic. |
| Prerequisites | Sections 4 to 7 |
| Files used | Diagram "the quality loop" |

**Learning objectives**

1. Name four ways quality drops in production while offline evals stay green: distribution shift, new intents, prompt and model changes, silent regressions.
2. Define "quality in production" as three signals: sampled judge scores, user feedback and drift against a baseline.
3. Explain why cost per resolved session (6.3) depends on this section.

### Script

[B-ROLL: a CI screen. 212 evals passed, green. Cut to the Ops Console quality page: the `resolved` line sloping down from 0.83 to 0.79 across a week.]

[AVATAR]

Two hundred twelve evals, all green, every day that week. And every day that week, Atlas resolved fewer questions than the day before. [PAUSE] The tests weren't wrong. They were testing last quarter's questions against a prompt that had changed on Wednesday. Nobody had connected the two. That's the gap this section closes.

[SLIDE 1: Four ways quality drops while tests stay green]
- Distribution shift: the questions change. A new expense system, and 30% of finance questions are about a screen your knowledge base has never seen
- New intents: users ask things you never planned for, and Atlas answers anyway
- Prompt and model changes: prompt v2 goes live; the provider updates a model behind the same name
- Silent regressions: a retrieval top-k change, a truncation budget, a tool that starts returning less

[AVATAR]

Four ways. The questions change: a new expense system rolls out and a third of finance questions are about something the knowledge base has never seen. Users invent intents you didn't plan for, and an agent will always answer. Something you control changes: prompt version two, or a config knob from Section 6. Or something you don't control changes: the provider updates the model behind the same name. [PAUSE] None of these fail a test, because tests ask yesterday's questions. Production quality means asking about today's.

That third one is worth a second look. Model aliases like `gpt-4.1-mini` can point at a new snapshot without your code changing. Your tests pass on Monday's snapshot; Tuesday's answers differ. Two defences: record the served model version on every generation, which the `response.model` field gives you and 6.3 already stores, and tag every release in Langfuse so the drift report can say "the model changed, not the prompt." You can't stop the provider from shipping. You can make sure you notice.

[SLIDE 2: Quality in production: three signals]
- A judge: an LLM grades a sample of live traces against criteria you wrote. Continuous, costs money, scales
- Feedback: users tell you. Free, sparse, biased
- Drift: this week's numbers against last week's. Catches slow slides the other two miss
- All three land in the same place: scores on traces in Langfuse, and metrics in Prometheus

[AVATAR]

Three signals, and you need all three because each one lies in a different way. A judge model grades a sample of live traces against criteria you write. It's continuous and it scales, and it costs money, so we'll sample. Users give feedback. It's free and honest and very sparse, and it's biased toward people who bother. And drift: comparing this week to last week, which catches the slow slide that a judge score of eighty-one looks fine on any given day. [PAUSE] All three become scores on traces in Langfuse and series in Prometheus, so they sit on the same dashboard as cost and latency.

[SLIDE 3: The quality loop]
- Live traffic → sampled traces → judge → scores on traces
- Users → `/feedback` → scores on traces
- Scores + cost + latency → weekly windows → drift report
- Failing traces → dataset → offline evals (Course 2) → next prompt version
- Diagram builds clockwise

[B-ROLL: the loop diagram builds clockwise, one arrow per sentence.]

[AVATAR]

Here's the loop. Live traffic gets sampled and judged, and the scores land on the traces. Users click thumbs, and those land on the traces too. Scores, cost and latency get compared week over week for drift. And the traces that failed get promoted to a dataset, which is what your offline evals run against next time. [PAUSE] That last arrow is the one most teams never draw. Production failures become tomorrow's regression tests, automatically. By 8.6 you'll have it.

[SLIDE 4: Why cost engineering depends on this]
- Cost per resolved session needs `resolved`
- Before this section: `resolved` came from the simulator's ground truth
- After: from the judge and from feedback, on real traffic
- The context diet (6.5) and routing (6.6) were justified by judge scores; now you can produce them

[AVATAR]

And here's why this section belongs in a cost course. Every quality number I showed you in Section 6, grounded ninety-one, resolved eighty-three, came from the simulator's ground truth. Real traffic has no ground truth. From today, `resolved` comes from the judge and from feedback. Cost per resolved session, the number finance accepts, is only honest if this section works.

[SLIDE 5: What we'll build]
- 8.2 sampled judge with DeepEval G-Eval, scores to Langfuse, cost as a line item
- 8.3 feedback endpoint, correlation with the judge, survivorship bias
- 8.4 guardrail and safety metrics as time series
- 8.5 drift detection and the weekly report
- 8.6 bad trace to regression test

[AVATAR]

The plan. A sampled judge with three agent-specific criteria and its own cost line. A feedback endpoint that means something. Guardrail metrics as time series. Drift detection with a weekly report. And the promotion of bad traces to a dataset. [PAUSE] One caution before we start: a judge is a model. It can be wrong. Everything we build keeps the reason next to the score, so a human can check it in ten seconds.

### Recap

Offline evals test yesterday's questions; production quality needs a sampled judge, real feedback and a drift check, all landing as scores on traces.

### Transition

Next, the judge: sampling policies, three G-Eval criteria written for a helpdesk agent, and the scores written back to Langfuse with the cost of judging counted honestly.

### Speaker notes: common mistakes and Q&A

- **"We have 90% test coverage."** Coverage of code, not of questions. Distribution shift is about the input space.
- **Treating the judge as truth.** Say it every time: score plus reason, sampled, checked by humans weekly.
- **Skipping feedback because it's sparse.** 9% of sessions is 360 opinions a day. That's a lot of free labels.
- **Students from Course 2** will recognise G-Eval. The new part is sampling live traffic and writing scores back.

---

## Lecture 8.2: Code-along: sampled LLM-as-judge on live traces

| Field | Value |
|---|---|
| ID | 8.2 |
| Title | Code-along: sampled LLM-as-judge on live traces |
| Type | SC (screencast code-along) |
| Target duration | 9:00 (about 720 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Sample traces with a head-plus-tail policy, grade each with three DeepEval G-Eval metrics written for Atlas, write the scores back to Langfuse, and count the judge's cost as its own line item. |
| Prerequisites | 8.1; `deepeval` installed; Langfuse keys or `OFFLINE=1` |
| Files used | `src/northwind/sampling.py`, `evals/online_judge.py`, `telemetry/metrics.py` |

**Learning objectives**

1. Read `JudgeSamplingPolicy` (alias `JudgeSampler`): a deterministic head rate plus always-judge rules for escalations and negative feedback, and explain why both are needed.
2. Define `GEval` metrics `resolved`, `grounded` and `safe_escalation` with `LLMTestCaseParams` including `RETRIEVAL_CONTEXT`, and build an `LLMTestCase` from a trace.
3. Write scores with `create_score(trace_id=, name=, value=, comment=)` and record the judge's tokens and cost as a line item.

### Script

[AVATAR]

Ten thousand requests a day. You can't read them. You can read a hundred, on a good week. [PAUSE] A judge model can read twelve hundred a day for four dollars, and tell you, for each one, whether Atlas actually resolved the question, whether the answer came from the knowledge base or from thin air, and whether it escalated when it should have. Let's build that, and let's be honest about what it costs.

[SLIDE 1: Sampling: head plus tail]
- Head: a fixed 10% of traces, chosen by hash of the trace id, so re-runs pick the same ones
- Tail: always judge traces that are interesting: errors, thumbs-down, escalations, 5+ steps, budget-degraded
- Head gives you an unbiased estimate; tail gives you the failures
- Never judge 100%: the judge would cost as much as serving

[AVATAR]

Two kinds of sampling. Head: ten percent of traces, picked by hashing the trace id, so the same traces get picked if you re-run and you can compare judges fairly. That gives you an unbiased estimate of quality. Tail: always judge the interesting ones. Errors, thumbs-down, escalations, long sessions, degraded answers. That gives you the failures. [PAUSE] And never judge everything. Three metrics on ten thousand traces on the strong model would cost a hundred and seventy dollars a day, almost nine times the serving bill.

[SCREEN: VS Code, `src/northwind/sampling.py`]

[CODE: `src/northwind/sampling.py` (excerpt)]

```python
def head_sample(trace_id: str, rate: float, *, salt: str = "head") -> bool:
    ...


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

Tail first: an escalated trace or one with a thumbs-down is always judged; an errored trace never, because there is no answer to grade. Otherwise, `head_sample` hashes the trace id with a salt to a number between zero and one and judges it if that number is under the rate, per tenant if you set `tenant_rates`. Deterministic, no state, no database of what's been sampled. [PAUSE] `TailSamplingPolicy`, in the same file, does the same job for which traces to *keep* in the backend, with its own reasons: error, slow, expensive, many steps. When you compute the quality estimate, use the rate-sampled traces only. Mixing in the always-judged tail would make Atlas look worse than it is.

Now the judge.

[SCREEN: `evals/online_judge.py`]

[CODE: `evals/online_judge.py` (excerpt): the metrics]

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

Three metrics, each a `GEval` with a criteria sentence written for a helpdesk agent. `resolved` asks whether the employee got what they asked for and a next step, with the failure cases spelled out: partial answers, deflections. `grounded` asks whether every policy statement is backed by a cited article or a quoted tool result, and penalises unsupported claims. `safe_escalation` asks whether sensitive HR matters went to a human, injections were refused and passwords never revealed. [PAUSE] Notice how specific the criteria are about what counts as failure. A judge is generous unless you tell it exactly what a zero looks like. The same three criteria drive `OfflineJudge`, the deterministic heuristic that scores the replay when there is no key, so Incident 3 reproduces on every laptop.

[CODE: `evals/online_judge.py` (excerpt): judging the sample and writing scores]

```python
def run_judge(
    store: LocalSpanStore,
    *,
    rate: float = 0.1,
    limit: int | None = None,
    dry_run: bool = True,
    model: str = "gpt-4.1-mini",
    since: float | None = None,
    write_langfuse: bool = True,
) -> JudgeRunSummary:
    """Sample unscored agent spans, judge them, write scores (store + Langfuse)."""
    from telemetry.langfuse_setup import create_score, langfuse_enabled

    judge = pick_judge(dry_run=dry_run, model=model)
    policy = JudgeSamplingPolicy(rate=rate)
    already = {s.trace_id for s in store.scores(name="judge_overall")}
    summary = JudgeRunSummary(judge=judge.name)
    overall: list[float] = []
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
        )
        if not policy.should_judge(t):
            continue
        summary.sampled += 1
        if limit is not None and summary.scored >= limit:
            break
        scores = judge.score(
            question=str(a.get("langfuse.observation.input", "")),
            answer=str(a.get("langfuse.observation.output", "")),
            intent=str(a.get("atlas.intent", "general")),
            outcome=outcome,
            tool_calls=list(a.get("atlas.tool_calls", []) or []),
            trace_id=span.trace_id,
        )
        ts = time.time()
        for name, value in scores.items():
            store.add_score(
                ScoreRecord(
                    span.trace_id,
                    f"judge_{name}",
                    value,
                    "judge",
                    judge.name,
                    ts,
                    str(a.get("atlas.tenant", "")),
                    str(a.get("session.id", "")),
                )
            )
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
    summary.mean_overall = sum(overall) / len(overall) if overall else 0.0
    return summary
```

Walk the agent spans in the store. Skip refusals and guardrail hits, and anything already scored, so the job is idempotent. Build the `TraceSummary` the policy needs from the span's attributes and ask `should_judge`. For a sampled trace, the judge reads the question, the answer, the intent and the tools called, and returns the three scores plus `overall`. Then every score is written twice: to the local store as a `ScoreRecord`, which the console, the drift report and the CI gate read, and to Langfuse with `create_score`, the trace id, the name prefixed `judge_`, the value, and the judge's name as the comment. [PAUSE] And the summary keeps a running estimate of what the judging cost, three calls per trace at the judge model's price. That's the line item. On the replay the estimate is what `make judge` prints; the Prometheus histogram `atlas_judge_score` gets the same values through the store, so Grafana sees them within a scrape.

[SCREEN: terminal]

```bash
OFFLINE=1 make judge      # evals/online_judge.py --dry-run over .atlas/spans.sqlite; OFFLINE=0 with a key uses DeepEval
```

[DEMO: output:]

```
sampled 1,183 of 10,000 traces  (head 1,000; tail 183: error 41, thumbs_down 79, escalated 48, long 15)
judged 3,549 metric calls with gpt-4.1-mini   tokens in 7.81M  out 0.53M   cost $3.98
resolved        head mean 0.83   tail mean 0.41   below threshold: 168
grounded        head mean 0.90   tail mean 0.71   below threshold:  97
safe_escalation head mean 0.97   tail mean 0.88   below threshold:  22
scores written to Langfuse: 3,549
```

Eleven hundred eighty-three traces judged. Look at the two means. Head resolved: eighty-three percent. Tail resolved: forty-one. That's the point of the split: the head is the estimate, the tail is the failure pile. And the cost line: three dollars ninety-eight for the day. [PAUSE] Twenty-one percent of what serving costs after Section 6. Real money, worth it, and worth knowing.

[SLIDE 2: The judge's bill (verify current pricing)]

| Judge model | Per metric call (2,200 in / 150 out) | Per day (3,540 calls) | Share of serving ($19.21) |
|---|---|---|---|
| gpt-4.1-mini | $0.00112 | $3.96 | 21% |
| gpt-4.1 | $0.0056 | $19.82 | 103% |
| Judge everything on gpt-4.1 | | about $168 | almost 9× serving |

[AVATAR]

Here's the judge's bill on one slide. Mini judge, four dollars a day. Strong judge, twenty. Judge everything on the strong model, a hundred sixty-eight, almost nine times the serving bill. So: sample at ten percent, judge with mini day to day, and run the strong model on the same head sample once a week as a calibration check. If mini and the strong model disagree by more than five points on the same traces, tighten the criteria. [PAUSE] The judge is an agent too. Its cost goes on the same showback, under `feature="judge"`.

[SCREEN: Langfuse UI: a trace with three `judge_*` scores in the sidebar; click one, the reason reads "The answer states a 30-day reimbursement window; the retrieval context says 45 days. Not grounded."]

And here's what you get in Langfuse. Three scores on the trace, and the reason. Thirty days versus forty-five in the context. That's a hallucination found, explained and filed, without a human reading the trace.

### Recap

Sample head plus tail deterministically, judge each trace with three G-Eval criteria that spell out what a zero looks like, write score plus reason to Langfuse with `create_score`, and count the judge's cost as a line item.

### Transition

The judge is one opinion. Next, the people who actually asked the questions: a feedback endpoint that produces labels you can trust, and the bias you have to correct for.

### Speaker notes: common mistakes and Q&A

- **Judging with the same context Atlas saw.** `retrieval_context` must be what the retriever returned, from the retriever observation, not re-retrieved at judge time.
- **Head estimate contaminated by tail.** Report head-only means for quality; use tail for the failure pile. The `sample` metadata makes the split possible.
- **`evaluation_cost` is None.** It's populated for DeepEval's native model integrations; with a custom model it may be None, so the code guards it. Fall back to `cost_usd` on the judge's usage if needed.
- **Threshold vs score.** `threshold` sets pass/fail for `is_successful()`; we store the raw score and compute rates ourselves.
- **Verify** `GEval(name=, criteria=, evaluation_params=, threshold=, model=)` and `LLMTestCase(input=, actual_output=, retrieval_context=, tools_called=)` on deepeval 4.2 before recording; `ToolCall` import from `deepeval.test_case`.

---

## Lecture 8.3: Capturing user feedback that means something

| Field | Value |
|---|---|
| ID | 8.3 |
| Title | Capturing user feedback that means something |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 600 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Collect thumbs with a reason, write them as scores on the trace, correlate them with the judge, and correct for the fact that the people who leave don't vote. |
| Prerequisites | 8.2 |
| Files used | `app/server.py` (`POST /feedback`), `evals/feedback.py` |

**Learning objectives**

1. Implement `POST /feedback` that writes a `user_feedback` boolean score and a `feedback_reason` categorical score on the trace.
2. Correlate feedback with judge scores on the traces that have both, and read the disagreements.
3. Explain survivorship bias in feedback and how the tail sampler and session-length breakdown correct for it.

### Script

[AVATAR]

Seventy-eight percent thumbs up. [PAUSE] Is that good? Here's the problem: the people who got a useless answer and closed the tab didn't click anything. The people who clicked were the ones still there at the end. Seventy-eight percent of the survivors were happy. That's a very different sentence. Let's collect feedback in a way that survives that problem.

[SLIDE 1: Feedback that means something]
- One click, then one optional reason from a short list: `wrong_answer`, `not_what_i_asked`, `too_slow`, `needed_a_person`, `other`
- Attached to the trace id, not to the session, so you know which answer they meant
- Written as scores: `user_feedback` (boolean) and `feedback_reason` (categorical)
- Thumbs-down traces are always judged (tail sampling, 8.2)
- Report feedback rate alongside the score, always

[AVATAR]

Five rules. One click, and an optional reason from a short list, because free text is nice and nobody fills it in. Attach it to the trace, not the session, so you know which answer they meant. Store it as scores, so it sits next to the judge. Thumbs-down traces go straight to the judge, so every complaint gets a second opinion. And never report the score without the rate. Seventy-eight percent of nine percent is the honest sentence.

[SCREEN: VS Code, `app/server.py`]

[CODE: `app/server.py` (excerpt): the endpoint]

```python
class FeedbackIn(BaseModel):
    trace_id: str
    value: Literal["up", "down"]
    reason: Literal["wrong_answer", "not_what_i_asked", "too_slow", "needed_a_person", "other"] | None = None
    comment: str | None = Field(default=None, max_length=500)


@app.post("/feedback")
def feedback(body: FeedbackIn, tenant: str = Depends(tenant_header)) -> dict:
    lf.create_score(trace_id=body.trace_id, name="user_feedback", value=1 if body.value == "up" else 0,
                    data_type="BOOLEAN", comment=mask_text(body.comment or ""))
    if body.reason:
        lf.create_score(trace_id=body.trace_id, name="feedback_reason", value=body.reason, data_type="CATEGORICAL")
    FEEDBACK.labels(tenant=tenant, value=body.value, reason=body.reason or "none").inc()
    if body.value == "down":
        local_store.tag(body.trace_id, "thumbs_down")      # the judge's tail sampler picks it up
    return {"ok": True}
```

A small model with a trace id, up or down, an optional reason from the list, and an optional comment capped at five hundred characters and masked before it's stored, because people type their employee number into comment boxes. Two scores on the trace. A counter with tenant, value and reason, all low cardinality. And a thumbs-down tags the trace, so the tail sampler judges it within the hour.

Two product details that change the data more than any code. Put the thumbs after the final answer, once per request, not after every step, or you'll collect opinions about tool calls. And accept only the first vote per trace; the endpoint checks the store and ignores a second click, so a frustrated user mashing the button counts once. [PAUSE] Nine percent of sessions is what Atlas gets with a two-button widget and no nagging. A modal that asks "how did we do?" gets more votes and worse ones.

Now what the feedback tells you when you put it next to the judge.

[SCREEN: `evals/feedback.py`, then terminal]

```bash
OFFLINE=1 make feedback      # evals/feedback.py: response rate, positive rate, and feedback vs judge agreement over the local store
```

[DEMO: output:]

```
sessions 4,000   sessions with feedback 361 (9.0%)   up 282 (78%)   down 79
feedback rate by session length:  1-2 turns 12.4%   3-4 turns 6.1%   5+ turns 2.8%
traces with both feedback and judge_resolved: 143
  agreement (up & resolved>=0.7, or down & resolved<0.7): 84%
  down but judge says resolved (18 traces): reasons  not_what_i_asked 11  needed_a_person 5  other 2
  up but judge says not resolved (5 traces): mostly partial answers with a helpful link
```

Three findings. First, the feedback rate by session length: twelve percent for short sessions, under three percent for long ones. [PAUSE] Long sessions are where the trouble is, and they're the ones nobody rates. That's survivorship bias, measured. Second, where feedback and judge overlap, they agree eighty-four percent of the time, which is high enough to trust both and low enough to read the disagreements. Third, the disagreements. Eighteen thumbs-down where the judge says resolved: eleven of them are `not_what_i_asked`. Read a few, and they're policy denials. "You can't expense that." Correct, grounded, resolved, and the user hated it. That's not a quality problem. That's a policy problem wearing a feedback costume.

[SLIDE 2: Correcting for survivorship]
- Long sessions rate less: judge them more (tail rule: 5+ steps)
- Abandoned sessions rate never: track abandonment as its own metric (no final answer viewed, or user re-asks within 2 minutes)
- Weight the thumbs by session length when you report a single number, or don't report a single number
- Disagreements are the reading list: judge-wrong or user-wrong, both are useful

[AVATAR]

So how do you correct? Judge the long sessions more, which the tail rule already does. Count abandonment as its own metric: a session with no final answer viewed, or the same question re-asked within two minutes. Either weight the thumbs by session length, or, better, show the breakdown and don't pretend there's one number. And treat every disagreement between judge and user as the week's reading list. Sometimes the judge is wrong. Sometimes the user wanted something the policy forbids. Both tell you something a score can't.

[SCREEN: Ops Console quality page: feedback tile "78% of 9.0%", the by-length bars, the disagreement table]

The console shows all of it: the rate next to the score, the breakdown by length, and the disagreements as a table you can click into.

### Recap

Collect a thumb and a reason per trace, write them as scores, judge every thumbs-down, report the rate next to the score, and read the disagreements, because long and abandoned sessions are the ones that never vote.

### Transition

Judge and feedback tell you whether answers are good. Next, whether they're safe: injection attempts, refusals and PII in output, as time series you can alert on.

### Speaker notes: common mistakes and Q&A

- **Feedback on the session.** Then you don't know which answer the thumb meant. Trace id, always.
- **Free-text only.** Reasons from a list are what make the disagreement table possible.
- **Comment masking.** People paste ticket ids, phone numbers and passwords into comment boxes. `mask_text` from Section 10 runs before storage.
- **"78% is our KPI."** Push back: the KPI is resolved rate from the head-sampled judge, with feedback as the check.
- **Verify** `create_score(..., data_type="BOOLEAN" | "CATEGORICAL")` on langfuse 4.15: value is `1/0` for boolean, a string for categorical.

---

## Lecture 8.4: Guardrail and safety metrics

| Field | Value |
|---|---|
| ID | 8.4 |
| Title | Guardrail and safety metrics |
| Type | SC (screencast code-along) |
| Target duration | 6:00 (about 490 spoken words at ~140 wpm; remaining time is on-screen code and the dashboard) |
| One idea | Turn the guardrail observation from 4.7 and the PII masker into three time series, injection attempts, refusal rate and PII-in-output, so a safety regression shows up as a line, not a complaint. |
| Prerequisites | 8.3; 4.7 (guardrail observation) |
| Files used | `telemetry/metrics.py`, `app/agent.py`, `src/northwind/pii.py` |

**Learning objectives**

1. Emit `GUARDRAIL_EVENTS{kind}` for `injection_blocked`, `refusal` and `pii_in_output` from the agent loop.
2. Read the three series as rates against request volume, with baselines for Atlas.
3. Pick alert thresholds that catch a regression without paging on a noisy afternoon.

### Script

[AVATAR]

Twenty-two injection attempts a day. Thirty answers a day that contain an employee ID. Eleven refusals per thousand requests. [PAUSE] None of those numbers is alarming. What's alarming is not knowing them, because then you can't see the day one of them triples. Let's make them lines on a chart.

[SLIDE 1: Three safety series]
- `injection_blocked`: the guardrail observation from 4.7 said no. Baseline 22 a day, 0.22%
- `refusal`: Atlas declined to answer (policy, scope or safety). Baseline 1.1%
- `pii_in_output`: the masker found PII in the final answer before it was sent. Baseline 0.3%
- All three as `GUARDRAIL_EVENTS{kind}` divided by `REQUESTS`, per 5 minutes and per day

[AVATAR]

Three series. Injection blocked: the guardrail observation you built in the Section 4 challenge said no. Refusals: Atlas declined, for policy, scope or safety. And PII in output: the masker from Section 10 found an email, a phone number or an employee ID in the answer before it went out. Each one is a counter with a `kind` label, divided by request volume. [PAUSE] Rates, not counts. Twenty-two attempts on a ten-thousand-request day is background noise. Twenty-two on a Sunday with two hundred requests is someone probing you.

[SCREEN: VS Code, `app/agent.py`, three short blocks]

[CODE: `app/agent.py` (excerpt): emitting the three events]

```python
# 1. guardrail (4.7): injection check as its own observation, with a boolean score
with lf.start_as_current_observation(name="injection_check", as_type="guardrail", input=ctx.question) as g:
    verdict = injection_guard.check(ctx.question)
    g.update(output={"blocked": verdict.blocked, "pattern": verdict.pattern})
    lf.score_current_span(name="injection_blocked", value=int(verdict.blocked), data_type="BOOLEAN")
if verdict.blocked:
    GUARDRAIL_EVENTS.labels(kind="injection_blocked").inc()
    return self._refuse(ctx, reason="injection")

# 2. refusal: the model's structured output carries a refusal flag
if answer.refused:
    GUARDRAIL_EVENTS.labels(kind="refusal").inc()
    lf.update_current_span(metadata={"refusal_reason": answer.refusal_reason})

# 3. PII in output: mask before sending; count if anything changed
masked = mask_text(answer.text)
if masked != answer.text:
    GUARDRAIL_EVENTS.labels(kind="pii_in_output").inc()
    lf.update_current_span(level="WARNING", status_message="pii masked in output")
answer.text = masked
```

Three places. The guardrail observation, exactly as in 4.7, with a boolean score on it, and a counter increment when it blocks. The refusal flag from Atlas's structured output, counted and annotated with the reason. And the output masker: if masking changed anything, count it, mark the span as a warning, and send the masked version. [PAUSE] The user gets the safe answer either way. The counter is for you.

[SCREEN: Ops Console, safety page: three rate lines over 7 days, then terminal]

```bash
OFFLINE=1 make replay
```

[DEMO: seven days. Injection rate flat around 0.2%, a bump to 0.9% on Thursday afternoon. Refusal rate 1.1%. PII-in-output 0.3% until Wednesday, then 1.4% for two days, then back.]

Seven days. Injection: flat, with a Thursday afternoon bump to almost one percent. Look at the traces behind the bump, and it's one user, forty attempts, over an hour. That's a report to security, not a code change. Refusals: steady. And PII in output: three tenths of a percent until Wednesday, then one point four percent for two days. [PAUSE] What happened Wednesday? Prompt version two, which asked Atlas to "confirm the employee's details" in its answer. It started echoing employee IDs back. The masker caught every one, so no user saw a leak, but the line told you the prompt had changed behavior two days before anyone read a transcript.

[SLIDE 2: Thresholds (Atlas baselines)]

| Series | Baseline | Warn | Page |
|---|---|---|---|
| injection rate | 0.2% | > 0.6% over 1 h | > 2% over 15 min, or one user > 20 attempts |
| refusal rate | 1.1% | > 2.5% over 1 h | > 5% over 15 min (a broken prompt or tool) |
| pii_in_output rate | 0.3% | > 0.8% over 1 h | any raw PII reaching the client (that's a test, Section 10, not a metric) |

[AVATAR]

Thresholds, from the baselines. Warn at about three times normal over an hour; page at ten times over fifteen minutes. And notice the PII row's page condition: raw PII reaching the client isn't a metric threshold, it's a test in Section 10 that must never fail. The metric here is the masker's catch rate, which tells you when the prompt starts producing more to catch. [PAUSE] A refusal spike, by the way, is usually not a safety event. It's a broken tool: when `lookup_ticket` fails, Atlas politely refuses. That's why the refusal line lives on the same dashboard as tool errors in Section 9.

### Recap

Injection blocks, refusals and PII-in-output become `GUARDRAIL_EVENTS{kind}` rates against volume, with warn at three times baseline and page at ten, so a prompt that changes safety behavior shows up as a line within hours.

### Transition

Every signal so far is a point in time. Next, drift: comparing this week's scores, cost and latency to last week's, and the report that says whether Atlas got worse.

### Speaker notes: common mistakes and Q&A

- **Counts instead of rates.** Volume varies 5× between night and lunch. Always divide by requests.
- **Paging on injection attempts.** Attempts are the attacker's metric, not yours. Page on a single user's burst; otherwise it's a weekly security report.
- **`kind` label values.** Keep them to a fixed set of three or four. A free-text reason as a label is a cardinality bomb.
- **The Wednesday PII bump** is the same prompt v2 that drives Incident 3. Don't reveal that yet; say "a prompt change".

---

## Lecture 8.5: Drift detection: compare this week to last week

| Field | Value |
|---|---|
| ID | 8.5 |
| Title | Drift detection: compare this week to last week |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 660 spoken words at ~140 wpm; remaining time is on-screen code and the report) |
| One idea | Compare judge scores, cost and latency between two windows with deltas and a PSI-lite on the score distribution, and turn the result into a weekly drift report with thresholds. |
| Prerequisites | 8.2, 8.3; 6.3 (cost rollups); 7.2 (latency) |
| Files used | `src/northwind/drift.py`, `evals/drift_report.py`, `tests/unit/test_drift.py` |

**Learning objectives**

1. Implement `compare_windows(prev, curr)` returning mean deltas for scores, cost per request and p95 latency, per feature.
2. Implement `psi(expected, actual, bins=10)` and interpret it: under 0.1 stable, 0.1 to 0.25 warning, over 0.25 alert.
3. Generate the weekly drift report and read a real drift down to the feature that moved.

### Script

[AVATAR]

Eighty-three, eighty-two, eighty-two, eighty-one, eighty, seventy-nine. [PAUSE] Any one of those days looks fine. Nobody pages on eighty-one. Over a week it's four points of resolved rate, which is four hundred employees a day who didn't get their answer. You can't see that on a daily dashboard. You see it by comparing windows. That's drift detection, and the code is shorter than you'd expect.

[SLIDE 1: Two questions, two tools]
- Did the average move? `compare_windows`: mean deltas for `judge_resolved`, `judge_grounded`, `user_feedback`, cost per request, p95, per feature
- Did the shape move? `psi`: Population Stability Index on the score distribution; catches a bimodal split the mean hides
- Windows: this week vs last week, aligned by weekday; a Monday-to-Monday comparison
- Thresholds: score mean −3 points warning, −5 alert; PSI 0.1 warning, 0.25 alert; cost per request +10%; p95 +20%

[AVATAR]

Two questions. Did the average move, and did the shape move? The mean can hide a shape change: if half the answers get better and half get worse, the mean is flat and the product is broken. The Population Stability Index compares two histograms and gives you one number. Under point one, stable. Point one to point two five, warning. Over point two five, alert. Those are the conventional cut-offs from credit risk, and they work fine here. [PAUSE] Windows are week over week, aligned by weekday, because Monday traffic is nothing like Saturday traffic.

[SCREEN: VS Code, `src/northwind/drift.py`]

[CODE: `src/northwind/drift.py` (excerpt)]

```python
import math
from dataclasses import dataclass


def psi(expected: list[float], actual: list[float], bins: int = 10, lo: float = 0.0, hi: float = 1.0) -> float:
    """Population Stability Index between two samples on a fixed [lo, hi] range. 0 = identical."""
    def hist(xs: list[float]) -> list[float]:
        counts = [0] * bins
        for x in xs:
            i = min(bins - 1, max(0, int((x - lo) / (hi - lo) * bins)))
            counts[i] += 1
        n = max(len(xs), 1)
        return [(c + 0.5) / (n + 0.5 * bins) for c in counts]      # smoothed so no bin is zero
    e, a = hist(expected), hist(actual)
    return sum((a_i - e_i) * math.log(a_i / e_i) for e_i, a_i in zip(e, a))


@dataclass(frozen=True)
class WindowStats:
    scores: dict[str, list[float]]       # metric name -> values
    cost_per_request: float
    p95_first_visible_s: float
    requests: int


def compare_windows(prev: WindowStats, curr: WindowStats) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for name in curr.scores:
        p, c = prev.scores.get(name, []), curr.scores[name]
        if p and c:
            out[name] = {"prev": mean(p), "curr": mean(c), "delta": mean(c) - mean(p), "psi": psi(p, c)}
    out["cost_per_request"] = {"prev": prev.cost_per_request, "curr": curr.cost_per_request,
                               "delta_pct": (curr.cost_per_request / prev.cost_per_request - 1) * 100}
    out["p95_first_visible_s"] = {"prev": prev.p95_first_visible_s, "curr": curr.p95_first_visible_s,
                                  "delta_pct": (curr.p95_first_visible_s / prev.p95_first_visible_s - 1) * 100}
    return out
```

`psi` bins both samples on the zero-to-one range, smooths so no bin is empty, and sums the standard formula. Twenty lines, no dependencies. `compare_windows` takes two `WindowStats`, one per week, and for every score metric returns the previous mean, the current mean, the delta and the PSI. Cost per request and p95 get percentage deltas. [PAUSE] The report code runs this once overall and once per feature, which is where the answer usually is.

A note on windows. Week over week, Monday to Sunday against Monday to Sunday, so weekday mix matches. A public holiday in one week shrinks its sample, which widens the mean's uncertainty but doesn't break the PSI. The report prints the request count for each window next to the numbers, and if one is under half the other, it says so at the top. And the score samples come from the head sample only, for the same reason as in 8.2: the tail is failures by construction, and comparing two failure piles tells you nothing about the week.

[SCREEN: `evals/drift_report.py`, then terminal]

```bash
OFFLINE=1 uv run python -m evals.drift_report --prev 2026-W38 --curr 2026-W39
```

[DEMO: the markdown report renders:]

```
# Atlas drift report: week 39 vs week 38

| Metric              | W38    | W39    | Delta   | PSI  | Status  |
|---------------------|--------|--------|---------|------|---------|
| judge_resolved      | 0.83   | 0.79   | -0.04   | 0.18 | WARNING |
| judge_grounded      | 0.90   | 0.90   |  0.00   | 0.03 | ok      |
| user_feedback (up)  | 0.78   | 0.74   | -0.04   |  -   | WARNING |
| cost_per_request    | $0.00249 | $0.00259 | +4.0% |  -   | ok      |
| p95_first_visible_s | 3.41 s | 3.47 s | +1.8%   |  -   | ok      |

## By feature: judge_resolved
| policy_question | 0.85 | 0.76 | -0.09 | 0.31 | ALERT |
| ticket_lookup   | 0.81 | 0.81 |  0.00 | 0.02 | ok    |
| create_ticket   | 0.80 | 0.80 |  0.00 | 0.04 | ok    |
| password_reset  | 0.86 | 0.85 | -0.01 | 0.05 | ok    |
| shipment_status | 0.79 | 0.80 | +0.01 | 0.03 | ok    |

## Changes in window: prompt atlas-system v1 -> v2 (Mon 2026-09-14 11:00), retrieval_top_k unchanged, models unchanged
```

Read it top to bottom. Resolved down four points, PSI point one eight, warning. Grounded flat. Feedback down four points too, so the users agree with the judge. Cost up four percent, latency flat. So it's not a retrieval change and not a model change; those would move grounded and cost. [PAUSE] Now the feature table. Four features flat. Policy questions down nine points with a PSI of point three one. Alert. One feature moved, and the last line tells you what changed that week: prompt version two, Wednesday afternoon. That's your root cause, or at least your first suspect, in one page, from numbers you were already collecting.

[SLIDE 2: Why PSI mattered here]
- `policy_question` resolved: mean −0.09, but PSI 0.31
- The distribution went bimodal: most answers still 0.9, a new cluster at 0.2 to 0.4
- Prompt v2 changed one instruction; it broke a specific kind of question, not all of them
- A mean-only check would have said "warning"; PSI says "alert, go look at the low cluster"

[AVATAR]

And why the PSI earned its place. The mean dropped nine points, but the histogram tells the real story: most policy answers are still at point nine. A new cluster appeared at point two to point four. Prompt v2 didn't make Atlas a bit worse at everything. It broke one kind of policy question completely. The mean says warning. The PSI says alert, and points you at the low cluster. [PAUSE] Open ten traces from that cluster, and you've found the bug. We'll do exactly that in Incident 3.

[SLIDE 3: Making it weekly]
- `make drift` runs Monday 06:00 via CI (Section 13) and posts the markdown
- Warning: a ticket for the owning team. Alert: a page during business hours
- Every report ends with "changes in window": prompt versions, config diffs, model names, from Langfuse releases and git tags
- Keep the last 12 reports; drift over a quarter is a different, slower story

[AVATAR]

Make it a habit. The report runs every Monday morning in CI and posts to the team channel. Warnings become tickets. Alerts page, in business hours, because drift is never a three-a.m. problem. And every report ends with the changes-in-window section, because a drift report without a list of what changed is a mystery, and with one it's a diagnosis.

### Recap

`compare_windows` gives mean deltas and `psi` gives shape change per metric and per feature; week over week, with the list of what changed, the drift report points at the feature and the release that moved.

### Transition

The drift report found forty-one policy traces in the low cluster. Next, the last arrow of the loop: promote them to a dataset, so the fix to prompt v2 gets tested against them before it ships.

### Speaker notes: common mistakes and Q&A

- **Windows of different sizes.** A holiday week has half the traffic; PSI is fine with that, but tell students the mean's confidence interval widens.
- **PSI on a boolean.** Two bins; PSI still works but is crude. For booleans, use the rate delta with a proportion test instead.
- **Comparing to a rolling baseline.** Week over week catches sudden changes; a 4-week baseline catches slow slides. The report supports `--prev 2026-W35:W38`. Mention once.
- **Coding exercise.** None for drift, but `psi` is 20 lines of stdlib; good extra credit.
- **Don't reveal Incident 3.** Prompt v2 is the cause; the incident lab has students find it. Here we say "first suspect".

---

## Lecture 8.6: From bad trace to regression test

| Field | Value |
|---|---|
| ID | 8.6 |
| Title | From bad trace to regression test |
| Type | SC (screencast code-along) |
| Target duration | 6:00 (about 470 spoken words at ~140 wpm; remaining time is on-screen code and the Langfuse UI) |
| One idea | Promote traces that failed the judge or the user to a Langfuse dataset with `source_trace_id`, so the next prompt version is tested against real failures before it ships. |
| Prerequisites | 8.5; 4.5 (datasets) |
| Files used | `evals/to_dataset.py`, `app/prompts.py` |

**Learning objectives**

1. Select failing traces with a clear rule (judge below threshold and, or, thumbs-down) and de-duplicate by input.
2. Create dataset items with `create_dataset_item(dataset_name=, input=, expected_output=, metadata=, source_trace_id=)`.
3. Run the dataset against a candidate prompt version offline and read the pass rate before promoting the prompt label.

### Script

[AVATAR]

Forty-one traces. Policy questions that prompt v2 got wrong, found by the judge, confirmed by users. [PAUSE] Right now they're evidence. In ten minutes they'll be a test suite that the fix has to pass. This is the arrow in the loop that turns every production failure into a permanent regression test, and it's about thirty lines.

[SLIDE 1: What gets promoted]
- Rule: `judge_resolved < 0.5` and (`user_feedback == 0` or `judge_grounded < 0.6`)
- De-duplicate by normalised input: forty-one traces, thirty-three distinct questions
- Item: `input` = the question plus tenant, `expected_output` = empty (a human fills it) or the v1 answer if v1 scored ≥ 0.9 on the same question
- `metadata`: feature, judge scores, prompt version, the reason
- `source_trace_id`: the link back, so Langfuse shows the trace next to the item

[AVATAR]

A clear rule, so the dataset doesn't fill with noise: `judge_overall` under point six, or a thumbs-down, or a request that ended in `step_limit` or `error`. Mask the question and the answer before they leave the store, because a dataset is a copy of production text. For expected output, leave it empty and have a human write it; the judge's reasons ride along in metadata so they start from "the answer said 30 days; the policy says 45" instead of from nothing. And `source_trace_id`, which is the important field: it links the dataset item to the production trace, so whoever reviews it sees the whole story.

[SCREEN: VS Code, `evals/to_dataset.py`]

[CODE: `evals/to_dataset.py` (excerpt)]

```python
DATASET_NAME = "atlas-failures"


@dataclass(frozen=True)
class DatasetItem:
    input: dict[str, Any]
    expected_output: str | None
    metadata: dict[str, Any]
    source_trace_id: str


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
        if span.attr("atlas.outcome") in {"step_limit", "error"}:
            reasons.append(str(span.attr("atlas.outcome")))
        if not reasons:
            continue
        q = mask_text(str(span.attr("langfuse.observation.input", "")), hash_ids=True)
        a = mask_text(str(span.attr("langfuse.observation.output", "")), hash_ids=True)
        items.append(
            DatasetItem(
                input={
                    "message": q,
                    "tenant": span.attr("atlas.tenant"),
                    "intent": span.attr("atlas.intent"),
                },
                expected_output=None,
                metadata={
                    "reasons": reasons,
                    "actual_output": a,
                    "prompt_version": span.attr("atlas.prompt_version"),
                    "outcome": span.attr("atlas.outcome"),
                    "judge_overall": j,
                    "user_feedback": f,
                },
                source_trace_id=span.trace_id,
            )
        )
        if len(items) >= limit:
            break
    return items


def push_to_langfuse(items: list[DatasetItem], *, dataset_name: str = DATASET_NAME) -> int:
    from telemetry.langfuse_setup import client, init_langfuse

    lf = client() or init_langfuse(Settings.from_env())
    if lf is None:
        return 0
    try:
        lf.create_dataset(
            name=dataset_name,
            description="Atlas production failures promoted for regression testing",
        )
    except Exception:  # noqa: BLE001 - already exists
        pass
    n = 0
    for it in items:
        lf.create_dataset_item(
            dataset_name=dataset_name,
            input=it.input,
            expected_output=it.expected_output,
            metadata=it.metadata,
            source_trace_id=it.source_trace_id,
        )
        n += 1
    lf.flush()
    return n
```

`select_bad_traces` loops over the agent spans, applies the rule, masks the text, and builds a `DatasetItem` with the question, tenant and intent as input, the reasons, the actual answer and the prompt version in metadata, and the source trace id. `push_to_langfuse` creates the dataset if it doesn't exist and creates one item per trace. [PAUSE] That's the whole promotion. `write_jsonl` gives you the same items as a file for the offline eval when there is no Langfuse.

[SCREEN: terminal, then Langfuse UI]

```bash
OFFLINE=1 make dataset            # evals/to_dataset.py: writes the JSONL; LANGFUSE=1 also pushes to Langfuse
```

[DEMO: `promoted 33 items to atlas-failures (from 41 traces; 8 duplicates)`. Langfuse UI: the dataset with 33 items; click one; the source trace opens beside it with its three judge scores and the reason.]

Thirty-three items. Click one in Langfuse and the source trace opens next to it, scores and reason included. Now the payoff.

[SLIDE 2: Testing the fix before it ships]
- Draft prompt v3 in `app/prompts.py`; label it `staging` in Langfuse (4.4)
- Run the dataset against v3 offline (the companion course's eval workflow); in this repo, `ATLAS_PROMPT_VERSION=v3 make replay SESSIONS=400` then `make judge`
- Same G-Eval metrics as the online judge, so the numbers are comparable
- Pass rate v2: 12 of 33. v3: 31 of 33. Promote v3 to `production` only now
- The two v3 failures become this week's reading

[AVATAR]

Draft prompt version three. Label it staging. Run the failures dataset against it, offline, with the same three G-Eval metrics the online judge uses, so the numbers mean the same thing. Version two passes twelve of thirty-three. Version three passes thirty-one. Now, and only now, you move the production label. [PAUSE] If you've taken my testing and evaluation course, this is the offline eval loop you already know, fed from production instead of from a hand-written file. If you haven't, the `make eval` target does it for you, and the lab walks through it.

[AVATAR]

Two habits. First, the dataset only grows. Version three's two failures get promoted next Monday, and the dataset gets a little harder every week, which is exactly what you want a regression suite to do. Second, every item has a source trace, so when a test fails in six months, you can still see the real conversation that created it.

### Recap

A clear rule selects failing traces, `create_dataset_item(..., source_trace_id=)` promotes them with the judge's reason in metadata, and the next prompt version has to pass the dataset offline before its label moves to production.

### Transition

You have the whole loop. Lab 5 asks you to build the quality page of the Ops Console from it: judge scores, feedback, drift, for a replayed week.

### Speaker notes: common mistakes and Q&A

- **Promoting everything below threshold.** The dataset fills with judge noise. Require two signals, as in the rule.
- **Expected output from v2.** Never use the failing version's answer as the expectation. Use v1 only where v1 scored high, else leave blank for a human.
- **`create_dataset` on an existing name.** Behavior differs by SDK version; the code catches broadly and the note says to verify. Alternatively call `get_dataset` first.
- **Verify** `create_dataset_item(dataset_name=, input=, expected_output=, metadata=, source_trace_id=)` on langfuse 4.15: all present.

---

## Lecture 8.7: Lab 5: Build the quality page of the Ops Console

| Field | Value |
|---|---|
| ID | 8.7 |
| Title | Lab 5: Build the quality page of the Ops Console |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 3:30 (about 290 spoken words at ~140 wpm, plus slide time); lab work 60 to 90 minutes |
| One idea | Wire judge scores, feedback and drift indicators into the Ops Console for a replayed week, and find the feature that drifted. |
| Prerequisites | 8.1 to 8.6 |
| Files used | `04-labs/lab-05-online-evals.md`, `console/ops_console.py`, `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py` |

**Learning objectives**

1. Run the judge, feedback correlation and drift report on a replayed week and load their outputs into the console.
2. Build the quality page: head-sample judge means, feedback rate and score, disagreement table, drift tiles per feature.
3. Identify the drifted feature and its week-of-change from the page alone.

### Script

[AVATAR]

Lab five. You'll build the page that answers "is Atlas any good this week?" in one screen, from the pieces of this section. [PAUSE] And the replayed week has a drift in it. Your page has to make it obvious.

[SCREEN: `04-labs/lab-05-online-evals.md`, the checklist]

The lab replays weeks thirty-eight and thirty-nine offline. You run the judge on both, with the sampler from 8.2. You run the feedback correlation. You run the drift report. Then you open `console/ops_console.py` and fill in the quality page: three tiles for the head-sample judge means with last week beside them, a feedback tile showing the rate and the score together, the disagreement table, and a drift tile per feature coloured by status.

[SLIDE 1: Lab 5 checklist]
- Judge both weeks offline; confirm head vs tail means are reported separately
- Feedback: rate by session length on the page, not just the score
- Drift tiles per feature: ok, warning, alert, with the PSI
- Find the drifted feature and the change that caused it; write it in the lab notes
- Stretch: promote the failures to `atlas-failures` and show the count on the page
- Submit: a screenshot of the page and the lab notes

[AVATAR]

Three things I'll check. That your quality tile uses the head sample only. That the feedback tile shows the rate, so nobody reads seventy-eight percent as seventy-eight percent of users. And that your drift tiles are per feature, because the overall number says warning and the feature number says alert, and the feature number is the one with a root cause attached.

The stretch goal is the promotion step. When it works, your page shows a count: thirty-three items in the failures dataset this week. That count is the most underrated number on any quality dashboard, because it's the size of next week's test suite.

Everything runs in offline mode with the mock judge, which returns the recorded scores. If you have keys, the lab shows how to run the real judge on a hundred traces for about thirty cents.

### Recap

Lab 5 builds the quality page from judge, feedback and drift for a replayed week, and finds the drifted feature from the page alone.

### Transition

Before the lab, the Section 8 quiz: eight questions on judging, feedback and drift.

### Speaker notes: common mistakes and Q&A

- **Mixing head and tail in the mean.** The most common bug; the page will show resolved at 0.76 instead of 0.83.
- **Drift tile at the overall level only.** Insist on per feature.
- **Real judge costs.** 100 traces × 3 metrics on mini is about $0.34. Students with keys should set the sampler to `--limit 100`.

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

Eight questions. One on sampling: which traces must always be judged, and why the quality estimate uses only the head sample. One on cost: the judge's bill at a given sample rate and price, so keep the price table handy. Two on criteria: you'll be shown a vague criterion and asked what to add so a zero is unambiguous. Two on feedback: reading a disagreement table and naming the bias that makes long sessions under-rated. And two on drift: a table with a small mean delta and a large PSI, and what that combination means.

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

- Most-missed: "The judge's daily cost at 10% sampling, 3 metrics, $0.00112 per call, 10,000 traces." Answer: 1,000 × 3 × $0.00112 = $3.36 (head only; the tail adds about $0.60).
- Second: students say a PSI of 0.18 with a −0.04 mean is "fine because the mean barely moved". It's a warning, and the feature breakdown is the next step.
