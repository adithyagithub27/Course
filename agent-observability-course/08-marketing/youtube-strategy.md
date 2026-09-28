# YouTube Strategy

**Goal:** bring engineers searching for LLM cost, tracing and LLMOps content to the Udemy course by giving them real value first. Every video is useful on its own, and the course is the natural next step.

**Brand:** same design system as the course (Deep Navy `#0A1628`, Electric Teal `#00D4AA`, Inter + JetBrains Mono). Same presenter style (HeyGen avatar or instructor on camera) as the course, with faster pacing.

**Funnel rules**

- One CTA per video, at the end: "The full build, with the incident labs, the dashboards and the CI gate, is in the course. Link in the description."
- The description has the course link (with a custom-price or best-price coupon when one is active and allowed; verify coupon rules), the repo link, timestamps and keywords.
- Pin a comment with the course link. Answer every comment in the first 48 hours.
- Show real code that runs. Use only the API forms in curriculum §6 on screen, with the "APIs verified on langfuse 4 / otel 1.45; GenAI conventions incubating" note.
- Every dollar figure on screen comes from the simulator against a dated price table and is labelled "simulated" or "example" (see `09-production/recording-guide.md` §6).
- Never show a real key, Langfuse project id or organisation name.

---

## 10 video ideas

| # | Title | Length | Hook (first 10 seconds) | Content | Funnels to | Timing |
|---|---|---|---|---|---|---|
| 1 | I Watched an AI Agent Burn $4,000 in a Weekend (Simulated). Here's the Trace. | 10-12 min | The cost meter climbing over a repeating red tool span. "One failing tool call. Sixty hours. Nobody watching." | Trimmed 1.1 + 5.6: the loop in the waterfall, the step limit, the budget guard, the alert | Whole course | W-4 |
| 2 | Cost per Resolved Session: The One Number Your Manager Wants From Your AI Agent | 8-10 min | "Your agent's OpenAI bill is one line. Your manager wants it by team, by feature and by outcome. Here's how." | 6.1 token anatomy + 6.3 rollups + the showback report, with simulated numbers | Section 6 | W-3 |
| 3 | Instrument Any LLM Agent With OpenTelemetry in 15 Minutes (GenAI Semantic Conventions) | 12-15 min | A bare `print()`-logged agent, then the same run as a waterfall. "Same code, one afternoon of instrumentation." | Condensed 3.2 + 3.4: TracerProvider, spans, `gen_ai.*` attributes, console then OTLP | Section 3 | W-2 |
| 4 | 4 Ways to Cut LLM Costs You Can Prove (Caching, Context Diet, Routing, Budgets) | 10-12 min | Before/after bars from the 40% challenge. "Not 'try a cheaper model'. Measured on the same day of traffic." | Condensed 6.4-6.7 with the Ops Console before/after | Section 6 | W+1 |
| 5 | Three AI Agent Incidents From Traces Alone: Can You Find Root Cause Before the Reveal? | 12-14 min | Incident 1 brief on screen. "Monday, 08:15. Cost is 6× normal on one tenant. You have the traces. Go." Pause card at 4 min | Incident 1 investigation and reveal (11.2) with the incident template; tease 2 and 3 | Section 11 (signature) | W+2 |
| 6 | Langfuse v4 Tutorial: Sessions, Prompts, Scores and Datasets on Top of OpenTelemetry | 12-15 min | The first-trace screen from 2.3. "Everything in this course explains and improves this one screen." | Condensed 4.1-4.5 | Section 4 | W+3 |
| 7 | Why Your Agent's p95 Doubled After Lunch (Latency Budgets, Fallbacks and Circuit Breakers) | 10-12 min | The p95 line climbing during the `slow_provider` chaos demo. "Averages said everything was fine." | 7.1 budgets + 7.4 fallbacks + 7.6 chaos demo | Section 7 | Month 2 |
| 8 | LLM-as-Judge in Production: Sampling, Cost of Judging and Catching Drift | 8-10 min | Judge scores sliding while every dashboard is green. "Nothing was red. Users were unhappy." | 8.2 + 8.5, tease Incident 3 | Section 8 | Month 2 |
| 9 | Langfuse vs LangSmith vs Arize Phoenix vs Datadog: Same Agent, Four Backends | 10-12 min | Four UIs showing the same trace. "Because we emit OpenTelemetry, switching took one exporter line." | 12.1-12.5 with the decision matrix; honest about what isn't portable | Section 12 | Month 2 |
| 10 | Your LLM Traces Are a Data Breach Waiting to Happen (PII Masking in the SDK and the OTel Collector) | 6-8 min | A trace with a redacted employee record. "Your prompt had a name. Your tool result had a payroll number. Your judge saw both." | 10.1 threat model + 10.2 masking; "not legal advice" on the governance slide | Section 10 | Month 3 |

## Shorts (from the same footage)

- The cost meter climbing, then the fixed run stopping at the step limit (from #1)
- "Your agent's bill is one line. Here it is by tenant." (from #2)
- One `@observe(as_type="tool")` decorator turning a function into a span (from #6)
- The p95 line recovering as the fallback rate rises (from #7)
- The before/after cost bars from the 40% challenge (from #4)

## Metadata template

```text
Title: [keyword-first title from the table]
Description:
  Line 1: one-sentence value summary with the primary keyword
  Line 2: Full course (tracing + cost + reliability + incidents + CI gate): [Udemy course link]
  Line 3: Code: [repo link]
  Timestamps
  Tools used: OpenTelemetry SDK 1.45, GenAI semantic conventions 0.66 (incubating), Langfuse 4, LiteLLM, DeepEval, Prometheus, Grafana
  Note: all cost figures are from a traffic simulator against a dated price table, not real bills
Tags: LLM observability, LLMOps, OpenTelemetry LLM, Langfuse tutorial, LLM cost optimization, AI agent tracing, LiteLLM router, LLM as judge
Thumbnail: dark navy, teal waterfall with one red span, 3-5 words max, no third-party logos
```

## Measure

Per video: click-through rate, average view duration and clicks to the course link (use a distinct coupon code per video where coupon rules allow it, or Udemy's traffic/referral reports if available; verify). After 5 videos, double down on the format with the best course-click rate. Expect the cost videos (#1, #2, #4) to draw managers and the tracing videos (#3, #6) to draw engineers; watch which converts.
