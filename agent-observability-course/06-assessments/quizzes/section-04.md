# Quiz: Langfuse (Section 4)

| Field | Value |
|---|---|
| Udemy lecture | 4.8 Quiz: Langfuse |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 4.1 to 4.7 |

---

### Q1. Langfuse SDK v4 is described as "an OpenTelemetry exporter plus semantics". Which statement about this design is accurate?

*Related lecture: 4.1 How Langfuse sits on OpenTelemetry*

- **A.** Langfuse only accepts spans of type generation.
  - *Explanation:* Incorrect. Generic spans are accepted and shown as spans; typed observations add richer rendering.
- **B.** Langfuse replaces the OpenTelemetry SDK, so you cannot use other exporters alongside it.
  - *Explanation:* Incorrect. Langfuse registers a span processor on the OTel TracerProvider; other processors and exporters (console, OTLP to a collector) can coexist.
- **C.** Langfuse observations are OTel spans with extra attributes that carry Langfuse-specific meaning: observation type (agent, tool, generation, retriever, guardrail, chain), usage and cost details, session and user ids, tags, environment and release.
  - *Explanation:* Correct. That is why a span created with plain OTel and `gen_ai.*` attributes still shows in Langfuse, and why `@observe(as_type=...)` is a thin layer that sets the type attribute for you.
- **D.** Sessions and users are OpenTelemetry primitives that every backend understands.
  - *Explanation:* Incorrect. Sessions, users, scores, prompts and datasets are Langfuse semantics on top of OTel; Section 12 lists them as the parts that do not port automatically.

**Correct answer: C**

---

### Q2. Inside a function decorated with `@observe(as_type="generation")`, you want Langfuse to show the correct model, tokens (including 900 cached input tokens out of 1,200) and cost. Which call is right?

*Related lecture: 4.2 Code-along: `@observe` and observation types*

- **A.** `get_client().update_current_trace(usage={"tokens": 1380})`
  - *Explanation:* Incorrect. Usage belongs on the generation, not the trace, and a single token total loses the input/output/cached split that pricing needs.
- **B.** `get_client().update_current_span(metadata={"tokens": 1380, "model": "gpt-4.1-mini"})`
  - *Explanation:* Incorrect. Metadata is free-form and not used for cost; Langfuse's usage and cost views read `usage_details` and `cost_details` on generations.
- **C.** `get_client().score_current_trace(name="tokens", value=1380)`
  - *Explanation:* Incorrect. Scores are evaluation signals, not usage accounting.
- **D.** `get_client().update_current_generation(model="gpt-4.1-mini", usage_details={"input": 1200, "output": 180, "cache_read_input_tokens": 900}, cost_details={"input": 0.00012, "cache_read_input_tokens": 0.00009, "output": 0.000288})`
  - *Explanation:* Correct. `usage_details` takes the usage categories, with cached tokens as a separate key so Langfuse can price them at the cached rate (or accept your `cost_details`). Input includes the cached portion, matching the provider's usage object.

**Correct answer: D**

---

### Q3. Northwind has four departments, thousands of employees and many conversations per employee. How does lecture 4.3 map these onto Langfuse so the UI can slice production traffic?

*Related lecture: 4.3 Sessions, users, tenants and tags*

- **A.** Department as a tag and metadata (`tenant`), employee as `user_id` (hashed), conversation as `session_id`, set via `update_current_trace(session_id=..., user_id=..., tags=[...], metadata={...})`.
  - *Explanation:* Correct. Tags and metadata filter and group; `user_id` powers the Users view; `session_id` powers the Sessions view. Low-cardinality dimensions (tenant) go in tags, high-cardinality identity goes in the dedicated fields.
- **B.** Department as `user_id`, employee as `session_id`.
  - *Explanation:* Incorrect. That misuses both fields: a department is not a user, and an employee is not a conversation; per-conversation grouping would be lost.
- **C.** Everything in the trace name, for example `hr/NW-10433/sess-42`.
  - *Explanation:* Incorrect. Names are not indexed for filtering the way tags, users and sessions are, and this would leak raw identifiers.
- **D.** One Langfuse project per employee.
  - *Explanation:* Incorrect. Projects are for environments or strict isolation boundaries, not for individuals; thousands of projects would be unmanageable and cross-user views impossible.

**Correct answer: A**

---

### Q4. Atlas fetches its system prompt with `client.get_prompt("atlas-system", label="production", fallback=LOCAL_PROMPT, cache_ttl_seconds=60)`. What does each argument buy you?

*Related lecture: 4.4 Prompt management and versions*

- **A.** `label` pins a specific version number; `fallback` is used when the label is missing; `cache_ttl_seconds` makes the prompt immutable for a minute.
  - *Explanation:* Incorrect on the first point: a label such as `production` is a movable pointer to whichever version currently carries it, not a fixed version number. That is what makes label-based rollback possible.
- **B.** `label` selects whichever version currently carries the `production` label (so promotion and rollback are label moves, no deploy); `fallback` keeps Atlas serving if Langfuse is unreachable; `cache_ttl_seconds` avoids a network call per request while still picking up a label change within a minute.
  - *Explanation:* Correct. This is the mechanism Incident 3 uses for rollback: move `production` back to v1 and every instance picks it up within the TTL.
- **C.** `label` is the prompt's display name; `fallback` is the model to use; `cache_ttl_seconds` is the model's timeout.
  - *Explanation:* Incorrect. None of these describe the arguments; the prompt name is the first positional argument, and models are configured elsewhere.
- **D.** All three are optional cosmetics; the prompt is embedded in the code anyway.
  - *Explanation:* Incorrect. If the prompt were only in code, there would be no versioning, labels or rollback without a deploy.

**Correct answer: B**

---

### Q5. A trace shows an answer that hallucinated a leave entitlement. You want it to become a regression test for future prompt versions. Which Langfuse call sequence does lecture 4.5 recommend?

*Related lecture: 4.5 Scores, datasets and the feedback loop*

- **A.** Delete the trace so it does not affect the average score.
  - *Explanation:* Incorrect. Deleting evidence hides the problem and breaks the audit trail Section 10 cares about.
- **B.** `client.create_score(trace_id=..., name="hallucination", value=1)` only; scores are enough.
  - *Explanation:* Incorrect. A score records the judgement on that trace, but it does not give you something to run new prompts against.
- **C.** `client.create_dataset(name="atlas-failures")` once, then `client.create_dataset_item(dataset_name="atlas-failures", input=<the question>, expected_output=<the correct KB passage>, source_trace_id=<the trace>)`, so the item links back to the production trace and offline evals can run against every new prompt version.
  - *Explanation:* Correct. Production becomes your next regression suite; `source_trace_id` preserves the provenance. Lecture 8.6 automates this from low judge scores.
- **D.** Screenshot the trace and attach it to a ticket.
  - *Explanation:* Incorrect. Useful for humans, useless for automated regression testing.

**Correct answer: C**

---

### Q6. `Langfuse(mask=mask_fn, sample_rate=0.2)` is configured. Which statement is correct?

*Related lecture: 4.6 Masking, sampling and cost of observability itself*

- **A.** `sample_rate` only affects scores.
  - *Explanation:* Incorrect. It affects trace ingestion; scores attach to traces that exist.
- **B.** Masking is unnecessary because Langfuse encrypts data at rest.
  - *Explanation:* Incorrect. Encryption at rest protects the disk, not the analyst, the judge or the export who can all read the raw values.
- **C.** `mask_fn` runs in Langfuse's servers after ingestion; `sample_rate=0.2` drops 80% of spans within every trace.
  - *Explanation:* Incorrect on both counts. Masking runs client-side before data leaves the process, and sampling is per trace, not per span.
- **D.** `mask_fn` is applied client-side to inputs, outputs and metadata before export, so raw PII never leaves the process; `sample_rate=0.2` keeps roughly 20% of *traces* (decided at the trace level so a kept trace is complete), which reduces ingestion volume and cost at the price of missing 80% of errors on average.
  - *Explanation:* Correct. This is head sampling. Lecture 13.2 and Lab 7 show why tail sampling in the collector is better once you self-host: it can keep 100% of errors.

**Correct answer: D**

---

### Q7. Atlas exits right after a request and the last trace never appears in Langfuse. What is the most likely cause and fix?

*Related lecture: 4.6 Masking, sampling and cost of observability itself*

- **A.** Spans are buffered in the batch processor and the process exited before they were sent; call `client.flush()` (or `client.shutdown()`) on exit, and in short-lived scripts always flush before returning.
  - *Explanation:* Correct. Asynchronous batching means nothing is sent until the batch timeout or size triggers. `flush()` forces the send; `shutdown()` flushes and stops the exporter. Atlas registers this in the FastAPI shutdown hook.
- **B.** Langfuse rejects traces that finish in under 100 ms.
  - *Explanation:* Incorrect. There is no minimum duration.
- **C.** The `mask` function raised an exception and swallowed the trace.
  - *Explanation:* Incorrect as the likely cause; a failing mask function would affect all traces and log an error, not just the last one.
- **D.** The trace was sampled out; raise `sample_rate`.
  - *Explanation:* Incorrect as the first suspect: with `sample_rate=1.0` the behaviour persists, and the symptom is "always the last trace".

**Correct answer: A**

---

### Q8. In Challenge 4.7, a student wraps the injection check as a guardrail observation but creates it *before* opening the agent span, and scores the guardrail observation instead of the trace. What are the two consequences?

*Related lecture: 4.7 Challenge: add a guardrail observation*

- **A.** Nothing changes; observation placement and score target are cosmetic.
  - *Explanation:* Incorrect. Both choices determine what you can query later.
- **B.** The guardrail becomes a separate root trace with no tenant, user or session on it, so refusal rate per tenant cannot be computed; and a score on the observation does not appear in trace-level filters or the Scores dashboard, so `injection_flagged` cannot be used as a trace metric.
  - *Explanation:* Correct. The lecture's two common mistakes. Fix: open the agent span first (it carries the identity attributes), run the guardrail inside it, and call `score_current_trace(name="injection_flagged", value=1 or 0, data_type="BOOLEAN")`.
- **C.** The agent span will fail to start because a guardrail already exists.
  - *Explanation:* Incorrect. Spans do not conflict; the agent span simply starts a new trace after the orphaned guardrail.
- **D.** Langfuse will reject a `guardrail` type unless the trace has a generation.
  - *Explanation:* Incorrect. A refused request legitimately has a guardrail and no generation; that trace shape is exactly what the challenge asks for.

**Correct answer: B**
