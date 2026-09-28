# Production Readiness Checklist

**Used in:** 12.6 (production readiness), 12.1, 12.8 (chaos demo), 13.1 and 13.3 (capstone hardening)
**Companion:** `voice-agent-readiness-scorecard.md` (a scored go/no-go gate built on this list)

> Tick every item before a voice agent takes real calls. Items reference the course lectures where each one is built.

---

## 1. Resilience

- [ ] **Fallback providers** for STT, LLM and TTS (provider fallback lists), tested by killing a provider mid-call (12.8, 13.3)
- [ ] **Timeouts** on every provider connection (`conn_options`) and every tool call; no single stage can hang a call
- [ ] **Spoken error recovery:** every failure path says something useful ("Sorry, I'm having trouble with our booking system. Let me transfer you.") instead of going silent
- [ ] **Graceful degradation:** if booking is down, Riley can still answer FAQs and take a message or transfer
- [ ] **Human escape hatch** always available: `transfer_to_human` + a fallback number when transfer fails (8.4)
- [ ] **Retry policy** for transient tool errors, with a maximum number of retries and spoken acknowledgement (5.6)
- [ ] `max_tool_steps` set to prevent tool loops (5.1)

## 2. Performance

- [ ] Latency budget set per stage (`latency-budget-worksheet.md`) and **p95 within budget** in the latency report (9.8)
- [ ] Filler speech on every tool that may exceed your silence target (5.5)
- [ ] **Prewarm** enabled (`AgentServer(setup_fnc=prewarm)`); idle processes sized for expected concurrency (12.1)
- [ ] Load tested at expected peak concurrency; `load_threshold` behaviour understood (12.1)
- [ ] Agent, LiveKit region and providers co-located where possible

## 3. Quality gates (CI)

- [ ] Unit tests pass on every push (`make test`)
- [ ] Behavior tests (greeting, booking flows, safety) pass when secrets are present (`make test-agent`)
- [ ] Evals (conversation quality, WER, latency report) pass thresholds (`make eval`)
- [ ] Simulated caller personas pass (9.9); audio-in tests pass (9.13); LiveKit Simulations if available (9.14)
- [ ] Failing any gate blocks deploy (9.10)

## 4. Observability

- [ ] `metrics_collected` handled; usage summary logged at shutdown (10.2)
- [ ] OpenTelemetry traces to Langfuse (or your backend) with spans per turn and per tool (10.3)
- [ ] **Cost per minute** computed and dashboarded (10.4)
- [ ] Dashboard panels: p95 latency, cost/min, containment rate, transfer rate, failed tool calls, interruptions (10.5)
- [ ] **Alerts** with thresholds and an owner for each (10.5)
- [ ] Call outcome logged per call (booked / rescheduled / cancelled / answered / transferred / abandoned)

## 5. Security and privacy

- [ ] Identity verification before revealing or changing appointments (11.2)
- [ ] Least-privilege tools; irreversible actions need a read-back (11.2)
- [ ] PII redacted **before** logs and traces (11.3); retention policy implemented
- [ ] Prompt-injection and social-engineering tests in CI (11.5)
- [ ] Topic boundaries: no medical/legal/financial advice (11.4)
- [ ] Secrets in a secrets manager; keys rotated; nothing in the repo or image
- [ ] Toll-fraud controls: outbound destinations restricted, rate limits, spend alerts (11.1)
- [ ] Container runs as non-root; minimal image (12.2)

## 6. Compliance (not legal advice; see `telephony-compliance-checklist.md`)

- [ ] AI disclosure in the greeting
- [ ] Recording/transcription notice and consent approach decided for caller jurisdictions
- [ ] Outbound: consent records, DNC checks, calling hours
- [ ] BAAs in place with every vendor that touches PHI (healthcare)
- [ ] Legal review completed

## 7. Deployment and operations

- [ ] Reproducible build (`deploy/Dockerfile`, pinned versions, `download-files` at build time) (12.2)
- [ ] Deploy and **rollback** rehearsed (12.3)
- [ ] Draining on deploy so live calls finish (12.1)
- [ ] Health endpoint monitored (self-host) (12.4)
- [ ] **On-call runbook** written: who gets paged, how to disable outbound calling, how to force transfers to humans, how to roll back, provider status pages, how to rotate a leaked key
- [ ] Version pins documented; a plan for framework upgrades (re-run the full suite before bumping)

## 8. Launch plan

- [ ] Soft launch: limited hours or a percentage of calls, with humans ready to take over
- [ ] Review the first 50 calls by hand (transcripts with PII redacted), and add every new failure to the test suite
- [ ] Define success metrics before launch (containment, transfer rate, booking accuracy, p95 latency, cost/min)
