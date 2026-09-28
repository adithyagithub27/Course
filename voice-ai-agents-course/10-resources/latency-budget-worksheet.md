# Latency Budget Worksheet

**Course:** Production Voice AI Agents with Python · **Used in:** 1.4 (set the budget), 9.8 (test against it), 10.1 and 13.5 (monitor it)

> **Voice-to-voice latency** is the time from when the caller stops speaking to when they hear the first sound of the agent's reply. In normal conversation people take turns with gaps of only a few hundred milliseconds (lecture 1.4 uses ≈200-300 ms). A voice agent can't match that yet, but **keeping it under about one second** keeps the conversation feeling natural. This course uses **800 ms as an example target** for the cascaded pipeline on a web connection. Set your own target and measure it. Don't assume it.

---

## 1. The stages

```
caller stops speaking
│
├─ [A] Endpointing / end-of-utterance (VAD silence + turn detector decision)
├─ [B] STT final transcript (after end of speech)
├─ [C] LLM time to first token (TTFT)
├─ [D] TTS time to first byte of audio (TTFB)
├─ [E] Network + transport (both directions; WebRTC or SIP/PSTN)
│
caller hears the first audio  ◄── voice-to-voice latency = A + B + C + D + E (roughly; some stages overlap)
```

Stages can overlap (streaming STT, **preemptive generation** can start the LLM before the turn is confirmed, streaming TTS starts on the first sentence). Your measured total can therefore be *less* than the sum of the stages. Always measure end to end as well as per stage.

| Stage | LiveKit metric to read (lecture 10.2) | What you control |
|---|---|---|
| A. Endpointing | End-of-utterance delay in the EOU metrics | `EndpointingOptions(min_delay, max_delay)`, turn detector, VAD settings |
| B. STT | STT metrics (duration / final latency) | STT model, streaming, telephony-tuned model, language settings |
| C. LLM TTFT | LLM metrics (TTFT, tokens) | Model size, prompt length, output length ("1-2 sentences"), region, preemptive generation |
| D. TTS TTFB | TTS metrics (TTFB, characters) | TTS model/voice, streaming, first-sentence length |
| E. Network | Not a single metric; estimate from the total minus the stages | Region placement of agent and providers, SIP vs WebRTC |
| Tools (when called) | Your own timing around the tool / spans in traces | Fast tools, caching, **filler speech** (`with_filler`) to hide latency |

## 2. Set your budget

Fill in your target per stage. The "example" column is **illustrative only**, a starting split for an 800 ms target, not a benchmark. Replace it with your measurements.

| Stage | Example split (illustrative) | Your target (ms) | Measured p50 (ms) | Measured p95 (ms) | Over budget? |
|---|---|---|---|---|---|
| A. Endpointing / EOU | 250 | | | | |
| B. STT final | 100 | | | | |
| C. LLM TTFT | 250 | | | | |
| D. TTS TTFB | 150 | | | | |
| E. Network / transport | 50 | | | | |
| **Total voice-to-voice** | **800** | | | | |
| Tool call (when it happens) | covered by filler speech | | | | |

**Rules of thumb (for thinking, not measurements):**

- **Use p95 for budgets, not averages.** The slow calls are the ones callers remember.
- **Endpointing is a trade-off.** A shorter delay responds faster but cuts off callers who pause mid-sentence (lecture 3.9 "Break it"). Phone callers often need longer endpointing (8.3).
- **Output length is latency.** Shorter replies start and finish sooner.
- **Phone adds latency.** Budget separately for SIP/PSTN calls and for web calls.
- **Speech-to-speech is one stage.** For OpenAI Realtime, measure total voice-to-voice and compare it with your cascaded total (lecture 6.4).

## 3. Scenario comparison (fill in during Lab 4 / lecture 6.4)

| Scenario | Transport | Total p50 | Total p95 | Notes |
|---|---|---|---|---|
| Cascaded (Deepgram → GPT-4.1 mini → Cartesia) | Web | | | |
| Cascaded | Phone (SIP) | | | |
| Realtime (`gpt-realtime`) | Web | | | |
| Hybrid (realtime text + your TTS) | Web | | | |

## 4. Budget test (lecture 9.8)

Put your targets into the latency test so CI fails when a stage goes over budget:

- Export `metrics_collected` events to JSONL (lecture 10.2).
- Run `tests/evals/latency_report.py` (uses `src/maple/latency.py`) against the JSONL.
- The report computes p50/p90/p95 per stage and lists violations. Set the thresholds to **your** column above.

## 5. When you're over budget: fix list

| Over budget in | Try (in this order) |
|---|---|
| A. Endpointing | Tune `min_delay`; use the semantic turn detector; enable preemptive generation; check VAD sensitivity |
| B. STT | Streaming model; telephony-tuned model for phone; move closer to the provider region |
| C. LLM TTFT | Shorter system prompt; smaller/faster model; fewer tools in context (split agents, 7.4); limit output length |
| D. TTS TTFB | Streaming TTS; faster voice/model; make the first sentence short |
| E. Network | Deploy the agent in the same region as LiveKit and the providers; check SIP trunk region |
| Tools | Speed up the tool; cache; prefetch on turn completion (7.3); filler speech so silence never exceeds your target |
