# Quiz: Tracing and Semantic Conventions (Section 3)

| Field | Value |
|---|---|
| Udemy lecture | 3.8 Quiz: Tracing and semantic conventions |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 3.1 to 3.7 |

---

### Q1. A trace shows a tool span with the correct name and attributes, but it appears as its own separate trace rather than under the agent span. Which explanation fits, and what is the fix?

*Related lecture: 3.6 Break it: orphan spans, missing context and double counting*

- **A.** The tool ran in a task or thread that did not inherit the agent span's context, so the span had no current parent and became a new root; fix by propagating context (for example `contextvars.copy_context().run(...)`) or by creating the span with `start_as_current_span` inside the parent's context.
  - *Explanation:* Correct. OpenTelemetry context lives in `contextvars`; a new thread or an `asyncio.create_task` without context copying starts empty. Lecture 3.6 reproduces exactly this orphan and its fix.
- **B.** Tool spans are always separate traces by OpenTelemetry design.
  - *Explanation:* Incorrect. Any span created while another span is current becomes its child, whatever its kind.
- **C.** The exporter only supports one span per trace.
  - *Explanation:* Incorrect. Exporters send batches of spans; trace structure is defined by span ids and parent ids, not by the exporter.
- **D.** The tool span was exported before the agent span finished; wait longer.
  - *Explanation:* Incorrect. Export order does not affect parentage; the parent relationship is set at span creation from the current context.

**Correct answer: A**

---

### Q2. In `telemetry/otel_setup.py` the demo starts with `ConsoleSpanExporter` wrapped in a `SimpleSpanProcessor`, then switches to `OTLPSpanExporter` wrapped in a `BatchSpanProcessor` for real use. Why the change of processor?

*Related lecture: 3.2 Code-along: manual OpenTelemetry instrumentation of Atlas*

- **A.** `BatchSpanProcessor` is required for OTLP; the SDK will not accept `SimpleSpanProcessor` with a network exporter.
  - *Explanation:* Incorrect. The SDK accepts either combination. The choice is about behaviour, not compatibility.
- **B.** `SimpleSpanProcessor` exports each span synchronously when it ends, which is fine for printing to a console but puts a network round-trip inside the request path; `BatchSpanProcessor` queues spans and exports them asynchronously in batches, so a slow or dead backend costs the request nothing.
  - *Explanation:* Correct. This is the difference that lecture 13.5 demonstrates by killing the backend: with batching, spans are dropped when the queue fills, but requests keep flowing.
- **C.** `BatchSpanProcessor` compresses spans so they are cheaper to store.
  - *Explanation:* Incorrect. Compression is an exporter/transport concern; the processor's job is buffering and scheduling.
- **D.** `SimpleSpanProcessor` drops all attributes longer than 1 KB.
  - *Explanation:* Incorrect. Attribute limits are configured on the TracerProvider, not by the processor type.

**Correct answer: B**

---

### Q3. Which set of attributes correctly identifies a span as an LLM chat call following the GenAI semantic conventions used in the course?

*Related lecture: 3.3 GenAI semantic conventions*

- **A.** `openinference.span.kind = "LLM"`, `llm.token_count.prompt = 3262`.
  - *Explanation:* Incorrect as the answer to this question: these are valid OpenInference conventions (Arize's), which Section 12 contrasts with the OTel GenAI conventions. The course's manual instrumentation uses `gen_ai.*`.
- **B.** `llm.model = "gpt-4.1-mini"`, `llm.tokens = 3306`.
  - *Explanation:* Incorrect. Those are ad hoc names. Tools that understand the conventions would not recognise them.
- **C.** `gen_ai.operation.name = "chat"`, `gen_ai.request.model = "gpt-4.1-mini"`, `gen_ai.usage.input_tokens = 3262`, `gen_ai.usage.output_tokens = 44`, plus `gen_ai.provider.name = "openai"`.
  - *Explanation:* Correct. Operation name distinguishes a chat call from `execute_tool` or `invoke_agent`; request model and usage fields are the standard names from `opentelemetry-semantic-conventions` 0.66b0 (incubating). Cached input tokens go in `gen_ai.usage.cache_read_input_tokens`.
- **D.** `span.kind = "generation"`, `model = "gpt-4.1-mini"`.
  - *Explanation:* Incorrect. `span.kind` in OpenTelemetry is CLIENT/SERVER/INTERNAL and so on; "generation" is a Langfuse observation type, not an OTel span kind, and `model` is not a convention attribute.

**Correct answer: C**

---

### Q4. You call `OpenAIInstrumentor().instrument(tracer_provider=provider)` and also keep the manual `gen_ai.*` generation span you wrote around each OpenAI call. Every model call now shows two generation spans. What is the correct resolution?

*Related lecture: 3.5 Auto-instrumentation with OpenInference*

- **A.** Instrument the client twice so the spans cancel out.
  - *Explanation:* Incorrect. Instrumenting twice creates more duplication, not less; instrumentors are generally idempotent but the manual span remains.
- **B.** Set `sample_rate=0.5` so on average only one span per call is kept.
  - *Explanation:* Incorrect. Sampling drops whole traces at random; it does not deduplicate spans within a trace.
- **C.** Keep both; two spans per call is harmless.
  - *Explanation:* Incorrect. Every cost roll-up would double-count tokens and dollars, and Langfuse would show twice the spend. Lecture 3.6 calls this the double-counting mistake.
- **D.** Pick one source of truth for the model call span: either rely on OpenInference's automatic span (and add your agent, step and tool spans around it), or keep the manual generation span and do not instrument the client. Never both for the same call.
  - *Explanation:* Correct. Auto-instrumentation gives you the model call for free with usage attached; manual spans still matter for the agent loop, steps, tools and retrieval, which no client instrumentor can see. Choose per layer, not per call.

**Correct answer: D**

---

### Q5. Why does the course use OpenInference's `openinference-instrumentation-openai` rather than `opentelemetry-instrumentation-openai-v2` for automatic instrumentation?

*Related lecture: 3.5 Auto-instrumentation with OpenInference*

- **A.** At the time the course was verified, the otel-contrib OpenAI instrumentor failed to import against the pinned `openai` 2.x client, while the OpenInference instrumentor worked and plugs into the same `TracerProvider`, so spans still flow through the standard OTel pipeline.
  - *Explanation:* Correct. The choice is pragmatic and documented in the curriculum's API reference. Because the instrumentor accepts `tracer_provider=`, exporters, processors and backends are unchanged.
- **B.** OpenInference spans cannot be exported to Langfuse, which is why the course teaches manual spans.
  - *Explanation:* Incorrect. OpenInference spans are ordinary OTel spans and export anywhere, including Langfuse and Phoenix.
- **C.** The otel-contrib package charges a licence fee.
  - *Explanation:* Incorrect. Both packages are open source.
- **D.** OpenInference is the official OpenTelemetry package.
  - *Explanation:* Incorrect. OpenInference is maintained by Arize; the otel-contrib package is the one under the OpenTelemetry organisation.

**Correct answer: A**

---

### Q6. Your test asserts that a successful tool span has `status.status_code == StatusCode.OK`, and it fails because the code is `UNSET`. What is going on?

*Related lecture: 3.4 Code-along: tag every LLM, tool and agent span correctly*

- **A.** The span is broken; a finished span must have status OK.
  - *Explanation:* Incorrect. `UNSET` is the default and the normal state for a span that completed without error.
- **B.** OpenTelemetry's convention is to leave status `UNSET` on success and set `ERROR` (with the exception recorded) on failure; `OK` is reserved for an explicit application decision and instrumentation should not set it. The test should assert `UNSET` for success.
  - *Explanation:* Correct. Setting `OK` everywhere is a common mistake that hides nothing but adds noise; backends treat `UNSET` and `OK` alike for "not an error". Lab 2's test asserts `UNSET` on success and `ERROR` on `ShipmentNotFound`.
- **C.** The exporter downgraded `OK` to `UNSET` to save bytes.
  - *Explanation:* Incorrect. Exporters do not rewrite status.
- **D.** The status was set on the parent span instead.
  - *Explanation:* Incorrect. Status is per span; a tool failure is recorded on the tool span, and the agent span's status reflects the request outcome independently.

**Correct answer: B**
