# Quiz: Observability and Cost (Section 10)

| Field | Value |
|---|---|
| Udemy lecture | 10.7 Quiz: Observability and cost |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 10.1 to 10.5 |

---

### Q1. Callers say Riley "takes forever to answer". Your per-stage p95 numbers are: EOU delay 1,450 ms, LLM TTFT 520 ms, TTS TTFB 210 ms. Where should you look first?

*Related lecture: 10.1 What to measure on every call*

- **A.** The TTS provider, because audio is what callers hear.
  - *Explanation:* Incorrect. TTS TTFB is 210 ms, comfortably inside a typical 300 ms budget.
- **B.** End-of-utterance detection: endpointing delays and turn-detector settings, because EOU is by far the largest stage.
  - *Explanation:* Correct. At 1.45 s, EOU delay alone is more than the LLM and TTS stages combined. Check `MIN/MAX_ENDPOINTING_DELAY`, telephony overrides and STT final-transcript timing before touching models.
- **C.** The LLM, because LLMs are always the bottleneck.
  - *Explanation:* Incorrect. LLM TTFT is 520 ms here. Measure before assuming.
- **D.** Network bandwidth, because voice needs a lot of it.
  - *Explanation:* Incorrect. Nothing in these numbers points at the network, and voice audio uses little bandwidth.

**Correct answer: B**

---

### Q2. You want one usage record per call (tokens, STT audio seconds, TTS characters) written when the call ends, even if the caller hangs up abruptly. What is the right pattern?

*Related lecture: 10.2 Collecting metrics and usage*

- **A.** Register a shutdown callback with `ctx.add_shutdown_callback(...)` that reads `session.usage` (usage per model and provider) and writes the summary.
  - *Explanation:* Correct. `session.usage` accumulates usage throughout the call, and a shutdown callback runs when the job ends for any reason, including a hang-up, which makes it the reliable place to write the final summary. This is what `attach_observers` in `agents/s10_observed_agent.py` does. (Older tutorials total usage with `metrics.UsageCollector`, which is deprecated in livekit-agents 1.8.)
- **B.** Write usage in the `end_call` tool.
  - *Explanation:* Incorrect. `end_call` only runs when Riley ends the call. Caller hang-ups and errors would produce no record.
- **C.** Poll the provider dashboards once a day and divide by the number of calls.
  - *Explanation:* Incorrect. Averages from invoices cannot attribute cost to individual calls or catch expensive outliers.
- **D.** Ask the LLM to estimate its own token usage at the end of the call.
  - *Explanation:* Incorrect. Models cannot reliably report their own usage, and the call may already be over.

**Correct answer: A**

---

### Q3. You connect OpenTelemetry tracing to Langfuse and immediately see caller phone numbers and dates of birth in span attributes and tool arguments. What is the correct fix?

*Related lecture: 10.3 Tracing with OpenTelemetry and Langfuse*

- **A.** Make the Langfuse project private.
  - *Explanation:* Incorrect. The data still leaves your system and is stored with a third party; access control does not reduce what was collected.
- **B.** Delete traces manually every week.
  - *Explanation:* Incorrect. The data was still exported and stored in the meantime, and manual processes get skipped.
- **C.** Turn tracing off in production.
  - *Explanation:* Incorrect. You lose the visibility you need to debug latency and failures.
- **D.** Redact PII before export, for example by running transcripts and tool arguments through `maple.pii` before they are attached to spans or logs, and set a retention period in Langfuse.
  - *Explanation:* Correct. Redaction must happen before data leaves the process. Section 11.3 applies `maple.pii` to logs and traces and pairs it with a retention policy.

**Correct answer: D**

---

### Q4. Your cost report shows TTS is 60% of the cost of a typical three-minute call. Which change is most likely to cut cost without hurting call quality?

*Related lecture: 10.4 Cost per minute: the number your boss will ask for*

- **A.** Switch to the most expensive LLM so it needs fewer turns.
  - *Explanation:* Incorrect. A pricier LLM raises the LLM line, and there is no evidence it would shorten calls.
- **B.** Remove STT to save its cost.
  - *Explanation:* Incorrect. A cascaded agent cannot understand the caller without STT.
- **C.** Keep replies short (one or two sentences) and avoid re-reading long lists, because TTS is billed by characters spoken.
  - *Explanation:* Correct. Brevity is both good voice UX and the biggest TTS cost lever. Offering three slots instead of eight, for example, cuts characters directly.
- **D.** Raise the endpointing delay so fewer turns happen.
  - *Explanation:* Incorrect. Callers still need the same number of turns; they just wait longer for each one.

**Correct answer: C**

---

### Q5. You are setting up alerts for Riley in production. Which alert is the most useful?

*Related lecture: 10.5 Dashboards and alerts that matter*

- **A.** Alert whenever any single turn exceeds 2 seconds.
  - *Explanation:* Incorrect. Individual slow turns happen from network blips; alerting on each one creates noise that people learn to ignore.
- **B.** Alert when p95 voice-to-voice latency exceeds its budget (for example 1.6 s) for 15 minutes, or when the failed-tool-call rate or transfer rate jumps well above its normal baseline.
  - *Explanation:* Correct. Sustained percentile breaches and rate changes point to real incidents (a slow provider, a broken scheduler API, a prompt regression) while ignoring one-off noise.
- **C.** Alert on the total number of calls per day.
  - *Explanation:* Incorrect. Call volume is a business metric; it does not tell you whether Riley is healthy.
- **D.** Alert when the containment rate reaches 100%.
  - *Explanation:* Incorrect. Containment rate belongs on the dashboard as a business KPI, but a fixed alert at 100% is not a useful health signal. (A sudden drop in transfers to zero could mean the transfer tool is broken, which the rate-change alert in option B catches.)

**Correct answer: B**
