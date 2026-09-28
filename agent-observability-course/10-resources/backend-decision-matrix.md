# Backend Decision Matrix

**Used in:** 1.3 (preview), 12.1 (lock-in), 12.2-12.4 (LangSmith, Phoenix, OpenLLMetry, Datadog), 12.5 (the decision), 13.4 (production readiness)

> Two decisions: (1) **what you emit**: OpenTelemetry with the GenAI semantic conventions (the course default), a vendor SDK, or both; (2) **where it goes**: Langfuse, LangSmith, Arize Phoenix, OpenLLMetry/Traceloop, or an enterprise APM such as Datadog. The ratings below are **qualitative**, reflecting the general trade-offs taught in the course as of the curriculum's verification date (2026-09-28). They aren't benchmarks and they aren't vendor claims. Products change quickly, so **re-check any capability and any pricing before you decide**, and fill in the "Your measurement" rows from your own Section 12 runs.

---

## Part 1: What you emit

| | OTel + GenAI semconv (course default) | Vendor SDK only | Both (SDK on top of OTel) |
|---|---|---|---|
| Course build | `telemetry/otel_setup.py`, `genai_attrs.py`, OpenInference auto-instrumentation | e.g., LangSmith `traceable` / `wrap_openai` (12.2) | Langfuse SDK v4 is itself an OTel exporter (4.1): you get both |
| Portability of **traces** | ●●● (any OTLP backend) | ● | ●●● |
| Portability of **scores, prompts, datasets** | n/a (not an OTel concept) | ● (vendor format) | ● (vendor format; see "what isn't portable") |
| Effort | Medium (you name spans and attributes) | Low (decorators) | Medium |
| Risk | Semconv is incubating; attribute names may change (pin versions) | Vendor API changes | Both |

**What isn't portable (12.1):** scores, prompt versions and labels, datasets, saved views, dashboards and alert rules live in the backend's own model. Plan to export them (most backends have an API) or accept that switching backends means re-creating them.

## Part 2: Where it goes

### Qualitative comparison

| Criterion | Langfuse | LangSmith | Arize Phoenix | OpenLLMetry / Traceloop | Datadog LLM Observability |
|---|---|---|---|---|---|
| What it is | LLM-native tracing, scores, prompts, datasets, dashboards; OTel-based SDK v4; open source, cloud or self-host | LangChain's platform: tracing, evals, prompts, datasets; strongest inside the LangChain/LangGraph ecosystem | Open-source tracing and evaluation from Arize, built on OpenInference conventions; self-host or Arize cloud | Open-source OTel instrumentation for LLM apps (OpenLLMetry) plus Traceloop's backend; sends OTel anywhere | LLM observability inside an enterprise APM: traces next to your infra, logs and RUM |
| **Control / self-host** | ●●● (Docker Compose in 13.1) | ● to ●● (check self-host/enterprise options) | ●●● (open source) | ●●● (instrumentation) / ●● (backend) | ● (SaaS) |
| **Accepts OTel / GenAI semconv** | ●●● (native) | ●● (check current OTLP ingestion) | ●●● (OTLP; maps OpenInference and GenAI conventions; check coverage) | ●●● (it emits OTel) | ●● to ●●● (OTLP ingestion; check GenAI attribute mapping) |
| **Agent-specific views** (steps, tools, sessions) | ●●● (observation types, sessions) | ●●● (runs, threads) | ●● to ●●● (check) | ●● | ●● (check agent features) |
| **Scores / online evals** | ●●● (scores API, datasets) | ●●● | ●●● (evals are a core feature) | ●● (via backend) | ●● (check) |
| **Prompt management** | ●●● | ●●● | ●● (check) | ● | ● |
| **Cost tracking** | ●●● (usage + cost details per generation) | ●●● | ●● | ●● | ●● to ●●● (check) |
| **Metrics / SLO tooling** | ●● (dashboards; pair with Prometheus/Grafana as the course does) | ●● | ●● | ●● | ●●● (APM strength: SLOs, monitors, on-call integrations) |
| **Compliance control** (data residency, retention, RBAC) | ●●● self-host / ●● cloud (check regions and plans) | ●● (check) | ●●● self-host | ●●● self-host | ●● (enterprise contracts; check) |
| **Cost model** | Free tier, then by volume; self-host = infra only (check) | Free tier, then by traces/seats (check) | Open source; Arize cloud paid (check) | Open source; Traceloop paid tiers (check) | Usage-based add-on to an APM contract (check) |
| **Lock-in** | Low-Medium (OTel traces portable; scores/prompts not) | Medium-High (deepest when using LangChain) | Low | Low | Medium (APM contract) |
| **Best fit** | Teams that want an LLM-native backend they can self-host, with OTel portability | Teams already on LangChain/LangGraph | Teams that want open-source evals + tracing, or already use Arize | Teams that want to instrument once and pick a backend later | Companies that already run Datadog and want LLM traces next to everything else |

● = weaker, ●●● = stronger (qualitative, dated 2026-09-28; re-check)

### Your measurements (Section 12, same Atlas trace to each)

| Metric | Langfuse | LangSmith | Phoenix | Datadog (if available) |
|---|---|---|---|---|
| Lines of code changed to switch | | | | |
| Did agent / tool / retriever spans render as such? (y/n) | | | | |
| Did usage and cost appear without extra code? (y/n) | | | | |
| Sessions / users / tenant filtering works? (y/n) | | | | |
| Scores writable from `evals/online_judge.py`? (y/n, effort) | | | | |
| Self-host possible on your terms? (y/n) | | | | |
| Monthly cost at your volume (date: ____) | | | | |

### Decision guide

- **Choose Langfuse** (the course default) when you want LLM-native tracing with scores, prompts and datasets, the option to self-host, and OTel portability for the traces.
- **Choose LangSmith** when your agents are built on LangChain/LangGraph and the team already lives there; weigh the lock-in.
- **Choose Phoenix** when evaluation is the centre of your practice, you want open source, or you already use Arize.
- **Choose OpenLLMetry** as the instrumentation layer when you want to defer the backend decision; pair it with any OTLP backend.
- **Choose Datadog (or your existing APM)** when the company already pays for it and the on-call, SLO and incident tooling is there; consider a **hybrid**: metrics and alerts in the APM, deep LLM traces, prompts and datasets in Langfuse, both fed by the OTel Collector (13.2).
- **Whatever you choose, emit OTel with the GenAI conventions first.** The course's Section 12 shows that the trace side of a switch is one exporter line; the rest is the non-portable part.

## Decision record template

```
Decision: emit [OTel + GenAI semconv | vendor SDK | both] to [Langfuse | LangSmith | Phoenix | OpenLLMetry→? | Datadog | hybrid: ...]
Date:
Constraints (self-host / residency / retention / existing APM / team stack / volume / budget):
Measured (from the table above):
What is NOT portable in this choice and how we'd export it:
Why this option:
What would make us revisit (pricing change, semconv graduation, vendor OTel support change):
```
