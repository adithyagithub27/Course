# Quiz: Portability (Section 12)

| Field | Value |
|---|---|
| Udemy lecture | 12.6 Quiz: Portability |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 12.1 to 12.5 |

---

### Q1. Northwind decides to move from Langfuse to another backend. Which parts of Atlas's observability move for free, and which do not?

*Related lecture: 12.1 Vendor lock-in and the OTel escape hatch*

- **A.** Traces (spans, attributes, sessions and users encoded as attributes) move by pointing the exporter or collector at the new backend; scores, prompt versions and labels, datasets and saved dashboards do not, because they are Langfuse-side state with no OTel equivalent, and would need export scripts and re-creation.
  - *Explanation:* Correct. Lecture 12.1's list of what is and is not portable. The decision matrix in 12.5 weighs this lock-in against features.
- **B.** Only Prometheus metrics move.
  - *Explanation:* Incorrect. Metrics are independent of the trace backend and were never in Langfuse to begin with; traces also move.
- **C.** Everything moves: it is all OpenTelemetry.
  - *Explanation:* Incorrect. Spans are OTel; several valuable things are backend state.
- **D.** Nothing moves: observability tools are all proprietary.
  - *Explanation:* Incorrect. The course emitted OTel spans with GenAI conventions precisely so traces are portable.

**Correct answer: A**

---

### Q2. Which is the correct LangSmith equivalent of the course's Langfuse instrumentation for a model call and its parent function?

*Related lecture: 12.2 Code-along: same Atlas, traced to LangSmith*

- **A.** LangSmith requires LangChain, so Atlas would need to be rewritten.
  - *Explanation:* Incorrect. `traceable` and `wrap_openai` work on plain Python and the OpenAI client without LangChain.
- **B.** `from langsmith import traceable; from langsmith.wrappers import wrap_openai`: wrap the client with `wrap_openai(OpenAI())` (Atlas ships this as `wrap_openai_if_enabled` in `OpenAIChatClient`), decorate `AtlasAgent.run` with `@traceable(run_type="chain")` (the `traced` helper in `telemetry/langsmith_setup.py`, your addition), with `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` set; feedback is attached with `Client().create_feedback(run_id, key=..., score=...)` (the `send_feedback` helper, wired into `/feedback` by you).
  - *Explanation:* Correct. `traceable` plays the role of `@observe`, `wrap_openai` plays the role of auto-instrumentation, and feedback maps to Langfuse scores. Differences: LangSmith's run tree is not OTel-native by default, so the OTel escape hatch is to export via OTLP to LangSmith's OTLP endpoint instead.
- **C.** `OpenAIInstrumentor().instrument()` alone; LangSmith reads OTel spans automatically.
  - *Explanation:* Incorrect as stated: LangSmith can ingest OTLP if you configure the exporter to its endpoint, but not automatically from a local instrumentor.
- **D.** `Langfuse(base_url="https://api.smith.langchain.com")`.
  - *Explanation:* Incorrect. The Langfuse SDK speaks Langfuse's API; pointing it at another vendor does not work.

**Correct answer: B**

---

### Q3. To send Atlas's traces to Arize Phoenix running locally, what changes, and what naming difference will you notice?

*Related lecture: 12.3 Arize Phoenix and OpenInference*

- **A.** Phoenix requires all traffic to go through Arize Cloud.
  - *Explanation:* Incorrect. Phoenix runs locally (the `phoenix` extra in `pyproject.toml`).
- **B.** Rewrite all spans with OpenInference attributes; Phoenix ignores `gen_ai.*`.
  - *Explanation:* Incorrect. Phoenix accepts any OTLP spans; OpenInference attributes render best, but `gen_ai.*` spans arrive and are searchable.
- **C.** Only the exporter endpoint changes (OTLP HTTP to `http://localhost:6006/v1/traces`, or the collector's `otlphttp/phoenix` exporter, which `make stack` already runs next to Langfuse); Phoenix renders OpenInference conventions (`openinference.span.kind`, `llm.token_count.prompt`) natively, while Atlas's manual spans carry `gen_ai.*`, so they arrive and are searchable but token panels may stay empty unless you add the optional OpenInference mirror.
  - *Explanation:* Correct. This is the escape hatch in practice: same code, different destination. One practical catch from 12.3: `make stack` already binds Phoenix to port 6006, so don't start a second Phoenix with `phoenix serve` alongside it.
- **D.** Phoenix needs its own SDK and cannot use OpenTelemetry.
  - *Explanation:* Incorrect. Phoenix is built on OpenTelemetry and OpenInference.

**Correct answer: C**

---

### Q4. A company already runs Datadog for its services and asks why it should not simply enable Datadog LLM Observability and skip Langfuse. What does lecture 12.4 say?

*Related lecture: 12.4 OpenLLMetry, Datadog and the enterprise APMs*

- **A.** Enterprise APMs are always cheaper than LLM-native tools.
  - *Explanation:* Incorrect. LLM observability add-ons are often priced per ingested span or per GB and can exceed an LLM-native tool at high volume.
- **B.** LLM observability should never be in the same tool as infrastructure monitoring.
  - *Explanation:* Incorrect. Correlating a slow generation with a saturated node is valuable; that is an argument *for* proximity.
- **C.** Datadog cannot trace LLM calls.
  - *Explanation:* Incorrect. Datadog LLM Observability and OpenLLMetry-style integrations do trace LLM calls with token usage.
- **D.** It can be the right choice: one pane of glass, existing alerting and on-call integration, and correlation with infrastructure traces are real advantages; the costs are the add-on's price per span or per host, thinner LLM-specific features (prompt management, datasets, human annotation queues), and the same lock-in question. A hybrid (OTel to the collector, fan out to the APM and to an LLM-native tool) is common.
  - *Explanation:* Correct. The lecture's position is a decision, not a verdict: use the matrix in 12.5.

**Correct answer: D**

---

### Q5. The backend decision matrix in lecture 12.5 scores options on control, cost, compliance, features and lock-in. Northwind must keep HR data in its own region and wants prompt management and datasets. Which option scores highest on the matrix for them?

*Related lecture: 12.5 Decision matrix: choosing your backend*

- **A.** Self-hosted Langfuse behind the OTel Collector: full control of data location, no per-span vendor fee, LLM-native features (prompts, datasets, scores), and the collector limits lock-in by keeping the exporter swappable; the cost is operating the stack (six containers in Lab 7).
  - *Explanation:* Correct. Data residency plus the need for LLM-native features points at self-hosting an LLM-native tool; the collector keeps the exit open.
- **B.** Langfuse Cloud in a default region: no operations burden.
  - *Explanation:* Incorrect for the residency constraint unless a compliant region is available and approved; the matrix would score compliance low otherwise.
- **C.** A generic APM only: cheapest to start.
  - *Explanation:* Incorrect. It fails the prompt-management and dataset requirement.
- **D.** Console exporter and a spreadsheet.
  - *Explanation:* Incorrect. Fine for a demo, not a production backend.

**Correct answer: A**
