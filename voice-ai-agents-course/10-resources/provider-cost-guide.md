# Provider Cost Guide

**Used in:** 2.1 (accounts), 2.7 (spending caps and mock mode), 6.1/6.4 (architecture costs), 10.4 (cost per minute), 14.3 (build vs buy)

> **Check current pricing.** Every price and free-tier detail in voice AI changes often: model launches, renames, plan changes. **This guide contains no vendor prices on purpose.** It tells you *how each provider charges*, *where to look*, and *how to calculate cost per minute*, and it gives you a table to fill in on the day you start. The course's overall student estimate is **about $10-20 in total** using free tiers and starter credits (curriculum), but **check current pricing**, since it may be different when you take the course.

---

## 1. How each provider charges (units)

| Provider (course default) | Role | Pricing unit (typical; check current pricing) | Free tier / credits (check current pricing) | Where it shows up in `costs.py` |
|---|---|---|---|---|
| LiveKit Cloud | Rooms, agents, SIP, Inference gateway | Agent session minutes, connection minutes, SIP minutes; Inference usage passed through per model | Free tier with monthly minutes (check current limits) | Transport / platform line |
| OpenAI `gpt-4.1-mini` | LLM (cascaded) | Per 1M input tokens and per 1M output tokens (cached input may be cheaper) | Pay-as-you-go | LLM line: prompt tokens × input price + completion tokens × output price |
| OpenAI `gpt-realtime` | Speech-to-speech | Per 1M **audio** input/output tokens and per 1M text tokens (audio tokens usually cost much more than text) | Pay-as-you-go | Realtime line (replaces STT + LLM + TTS) |
| Deepgram `nova-3` | STT | Per minute of audio streamed | Starter credit (check current amount) | STT line: audio minutes × price |
| Cartesia `sonic-3` | TTS | Per character, or credits per character, depending on plan | Free/starter plan (check) | TTS line: characters × price |
| ElevenLabs (optional) | TTS | Per character / credits by plan | Free plan (check) | TTS line |
| Twilio Elastic SIP Trunking | Telephony | Phone number per month + per-minute origination (inbound) and termination (outbound), which varies by country | Trial credit (check; trial accounts have restrictions such as verified numbers only) | Telephony line |
| Langfuse | Tracing | Free cloud tier or self-host; paid tiers by volume | Free tier (check) | Usually excluded from per-minute cost |
| Judge LLM (tests/evals) | Testing | Same as the LLM line | | Test budget, not production cost |

> **LiveKit Inference vs direct plugins (2.1, 3.5):** model strings like `"deepgram/nova-3"` go through LiveKit Inference, which bills through LiveKit. Direct plugins like `openai.LLM(...)` bill through your own provider account. Check which one you're using before you estimate costs.

## 2. Fill in your price table (date: __________)

| Line item | Unit | Price per unit (check current pricing) | Source URL (provider pricing page) |
|---|---|---|---|
| STT | per audio minute | | |
| LLM input | per 1M tokens | | |
| LLM output | per 1M tokens | | |
| TTS | per 1K characters | | |
| Realtime audio input | per 1M audio tokens | | |
| Realtime audio output | per 1M audio tokens | | |
| LiveKit agent/session | per minute | | |
| SIP inbound | per minute | | |
| SIP outbound | per minute | | |
| Phone number | per month | | |

Put the same values into the price table in `src/maple/costs.py` (lecture 10.4), and keep the date next to them.

## 3. Cost per minute formula (lecture 10.4)

```
cost_per_minute = ( STT_minutes × STT_price
                  + LLM_input_tokens × in_price / 1e6
                  + LLM_output_tokens × out_price / 1e6
                  + TTS_characters × tts_price / 1e3
                  + platform_minutes × platform_price
                  + telephony_minutes × telephony_price ) / call_minutes
```

`session.usage.model_usage` gives you the usage numbers per model (read it in a shutdown callback, as `agents/s10_observed_agent.py` does). `usage_from_model_usage()` in `src/maple/costs.py` turns them into `UsageNumbers`, and `cost_breakdown()` multiplies them by your price table. (`metrics.UsageCollector` from older tutorials is deprecated in livekit-agents 1.8; the course does not use it.)

**Worked example with made-up round numbers (NOT real prices):** a 3-minute call with 1.5 min of caller audio sent to STT, 6,000 LLM input tokens, 400 output tokens and 1,500 TTS characters. With hypothetical prices of STT $0.01/min, LLM $1 per 1M input / $4 per 1M output, TTS $0.05 per 1K chars and platform $0.01/min:
- STT 1.5 × 0.01 = $0.015
- LLM 6,000 × 1/1e6 + 400 × 4/1e6 = $0.0076
- TTS 1,500 × 0.05/1e3 = $0.075
- Platform 3 × 0.01 = $0.03
- **Total ≈ $0.128 → ≈ $0.043 per minute** (hypothetical)

The exercise shows *which lines dominate* with your real prices. In many cascaded setups, TTS and platform/telephony minutes matter more than people expect, and LLM input tokens grow with every turn because the conversation history is re-sent. Check this with your own numbers.

## 4. Keeping your course spend low (lecture 2.7)

- [ ] **Set hard spending limits / budget alerts** on OpenAI, Deepgram, Cartesia and Twilio before running anything (where each provider offers them).
- [ ] Check the LiveKit Cloud free-tier minutes on your project dashboard.
- [ ] **Use offline mode for practice:** `make test` runs the unit tests with no keys. `MOCK_MODE=1 python agents/s03_hello_agent.py console --text` runs Riley with a scripted fake LLM and text I/O at zero cost (lecture 2.7).
- [ ] Use text-session behavior tests (Section 9) instead of live audio calls while iterating.
- [ ] Keep realtime (`gpt-realtime`) experiments short. Audio tokens are usually the priciest line (check current pricing).
- [ ] Twilio: one number is enough; release it when you're done. Trial accounts may only call verified numbers (check).
- [ ] **Estimate before you run:** minutes × your cost per minute from Section 3, before each lab.
- [ ] Revoke keys you no longer need.

## 5. Build vs buy cost models (lecture 14.3)

| Option | How you pay (typical; check current pricing) | Hidden costs to include |
|---|---|---|
| LiveKit Agents (self-built, LiveKit Cloud) | Platform minutes + each provider separately | Your engineering and ops time; monitoring |
| LiveKit Agents (self-hosted) | Infrastructure + providers | Scaling, on-call, SFU/SIP ops |
| Pipecat (self-built) | Transport of choice + providers | Same as above |
| Managed platforms (Vapi, Retell, ElevenLabs Agents, Bland) | Usually a per-minute platform fee, with or without provider costs bundled (check each) | Lock-in, limited test hooks, compliance terms (BAA availability), per-minute markup at scale |
