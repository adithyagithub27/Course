# Architecture Decision Matrix

**Used in:** 1.3 (preview), 6.4 (cascaded vs realtime head-to-head), Lab 4, 14.3 (LiveKit vs Pipecat vs managed platforms)

> Two decisions: (1) **pipeline architecture**: cascaded, speech-to-speech (realtime) or hybrid; (2) **stack**: LiveKit Agents, Pipecat or a managed platform. The ratings below are **qualitative**, reflecting the general trade-offs taught in the course. They aren't benchmarks. Fill in the "Your measurement" rows with numbers from Lab 4 and your own calls. Products change quickly, so re-check any vendor capability before you decide.

---

## Part 1: Pipeline architecture

### The three options

| | Cascaded | Speech-to-speech (realtime) | Hybrid ("half-cascade") |
|---|---|---|---|
| Shape | STT → LLM → TTS | One model, audio in → audio out | Realtime model (audio in, **text out**) → your TTS |
| Course build | `agents/s03…`–`s05…` (Deepgram, GPT-4.1 mini, Cartesia) | `agents/s06_realtime_agent.py` (`RealtimeModel(model="gpt-realtime", voice="marin")`) | `agents/s06_realtime_agent.py` with text modality + separate TTS (6.3) |

### Qualitative comparison

| Criterion | Cascaded | Realtime | Hybrid | Why |
|---|---|---|---|---|
| Control over each stage | ●●● | ● | ●● | Cascaded lets you swap, tune and test every stage independently |
| Latency potential | ●● | ●●● | ●● | Realtime removes stage hand-offs, but cascaded can be tuned to be competitive (measure it) |
| Naturalness / prosody / emotion | ●● | ●●● | ●● | Realtime models hear tone and can respond expressively |
| Voice/brand choice and pronunciation control | ●●● | ● | ●●● | Your own TTS gives you voice choice and pronunciation control |
| Tool-call reliability and testability | ●●● | ●● | ●● | Text LLMs with text transcripts are easier to assert on (Section 9) |
| Transcript for logs/compliance | ●●● | ●● | ●● | Cascaded always has an STT transcript; realtime relies on a transcription side channel |
| Cost transparency per stage | ●●● | ● | ●● | Realtime bills as one line (usually audio tokens) |
| Cost per minute | Measure | Measure | Measure | Depends on current prices. Use `provider-cost-guide.md` |
| Language/accent coverage | Depends on STT/TTS | Depends on model | Mixed | Check for your languages (7.8 covers multilingual) |
| Provider lock-in | Low (swap any stage) | Higher | Medium | |

● = weaker, ●●● = stronger (qualitative)

### Your measurements (Lab 4 / lecture 6.4, same 5 calls)

| Metric | Cascaded | Realtime | Hybrid |
|---|---|---|---|
| Voice-to-voice p50 (ms) | | | |
| Voice-to-voice p95 (ms) | | | |
| Cost per minute ($, date: ____) | | | |
| Tool-call accuracy (x/5 correct `book_appointment` args) | | | |
| Interruption handling (x/5 handled cleanly) | | | |
| Subjective naturalness (1-5) | | | |

### Decision guide

- **Choose cascaded** when you need tight testability, a specific brand voice, per-stage cost control, a transcript for compliance, or you're on phone lines where STT choice matters (8 kHz audio).
- **Choose realtime** when naturalness and low latency matter most, the tool surface is small, and you can accept less per-stage control.
- **Choose hybrid** when you want realtime's understanding but must control the voice (brand, pronunciation, language-specific voices).
- **Whatever you choose, keep the same test suite.** The course's behavior tests and evals run against both (Section 9).

---

## Part 2: Stack: build vs buy

| Criterion | LiveKit Agents | Pipecat | Managed platforms (Vapi, Retell, ElevenLabs Agents, Bland) |
|---|---|---|---|
| Model | Open-source Python framework + LiveKit (Cloud or self-hosted) transport/SIP | Open-source Python frame-pipeline framework, transport of choice | Hosted platform, configured via dashboard/API |
| Control over pipeline | ●●● | ●●● (lowest-level) | ● to ●● (varies by platform) |
| Time to first working call | ●● | ●● | ●●● |
| Telephony | Built-in SIP (inbound, outbound, transfer) | Via transports/integrations (check current options) | Usually built in |
| Testing in your CI | ●●● (built-in test framework, `mock_tools`) | ●● (you build the harness) | ● to ●● (check each platform's testing/simulation features) |
| Observability | Metrics events, OTel | Observers/metrics, OTel (check) | Platform dashboards; export options vary |
| Compliance control (data residency, BAA, retention) | ●●● (self-host option; BAAs with each provider) | ●●● | Depends on the vendor's terms (check BAA availability and plan) |
| Cost model | Pay providers + platform minutes | Pay providers + transport | Per-minute platform fee ± provider costs (check) |
| Lock-in | Low-Medium | Low | Higher (prompts, flows and tools live in the vendor's format) |
| Team skills needed | Python, async, some ops | Python, async, more assembly | Low-code/configuration, some API |

### Build when…
- Voice is core to your product, and you need to test, tune and own it.
- Compliance needs control over where audio and transcripts go.
- You expect scale where per-minute platform markups matter.
- You need custom tools, handoffs or integrations a platform can't express.

### Buy when…
- You need a pilot live quickly, and voice isn't your core differentiator.
- The team has no Python/async/ops capacity.
- The platform's compliance terms, testing features and pricing fit your use case today.

### LiveKit Agents vs Pipecat (both "build")

| Prefer LiveKit Agents when… | Prefer Pipecat when… |
|---|---|
| You want an integrated stack: transport, SIP, agents, a test framework and a cloud deploy target | You want a transport-agnostic frame pipeline and fine-grained processor control |
| You value the `AgentSession` abstractions (turn handling, tools, handoffs) | You're comfortable composing processors and aggregators yourself |
| You want built-in behavior testing (`session.run`, `result.expect`) | You already run another transport, or need its specific integrations |

## Decision record template

```
Decision: [cascaded | realtime | hybrid] on [LiveKit | Pipecat | platform]
Date:
Use case / constraints (latency target, languages, compliance, volume):
Measured (p95 latency, cost/min, tool accuracy):
Why this option:
What would make us revisit:
```
