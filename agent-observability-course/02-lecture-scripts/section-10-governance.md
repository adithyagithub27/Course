# Section 10: Privacy, Security and Governance of Telemetry

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 32 minutes (5 lectures, including one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Any trace shown on screen in this section uses the synthetic Northwind data only; never a real employee record.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on langfuse 4.15 (`mask=`) / OpenTelemetry Collector contrib 0.116.1 as pinned in `deploy/docker-compose.observability.yml` (processor options: verify against the current collector docs)."
> **Standing disclaimer (lecture 10.4, on screen for the whole lecture):** "This lecture is not legal advice. Verify obligations with your counsel and your data protection officer."

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.pii` (`EMAIL_RE`, `EMPLOYEE_ID_RE`, `PHONE_RE`, `CARD_RE`, `mask_text`, `mask_with_stats`, `mask_value`, `stable_hash` / `short_hash`, `langfuse_mask`, `mask_fn` alias, `contains_pii`), `telemetry/genai_attrs.py` (`_safe`, `set_tool`, `set_llm_messages`), `telemetry/langfuse_setup.py` (`Langfuse(mask=langfuse_mask, ...)`), `deploy/otel-collector.yaml` (`memory_limiter`, `attributes/redact`, `tail_sampling`, `batch`), `tests/unit/test_pii.py`, `tests/integration/test_spans.py::test_no_raw_pii_reaches_any_span`, `10-resources/telemetry-governance-checklist.md`.

**The numbers card for this section (synthetic data):**

| Item | Value |
|---|---|
| What every stored agent span carries | `user.id` (an employee ID such as `NW-34624`), `session.id`, tenant and feature tags, the question and the answer: 10,184 of them on the replayed day |
| PII-in-output flags on the replayed day (8.4) | 678 answers, mostly policy text quoting the ID format `NW-12345` |
| Masking at the source | every content attribute passes `mask_value(..., hash_ids=True)` and is clipped to 4,000 characters (`genai_attrs._safe`) |
| Placeholders | `<EMAIL>`, `<PHONE>`, `<EMPLOYEE_ID>`, `<CARD>`; with `hash_ids=True`, `<EMPLOYEE_ID:a116ca8c>`; employee IDs match `NW-\d{5}`; ticket and shipment ids (`TCK-`, `SHP-`) are kept |
| The shipped hash | salted SHA-256, 8 hex characters (`stable_hash`); a five-digit employee ID falls to a brute-force loop in under a tenth of a second; production needs a keyed HMAC |
| Collector processors | `memory_limiter`, `attributes/redact` (deletes tool results, message bodies, system instructions and Langfuse input/output; hashes tool arguments, `user.id`, `enduser.id`), `tail_sampling`, `batch` |
| Retention (Atlas policy) | traces 30 days prod, 7 days dev; scores and aggregates 13 months; datasets indefinitely (reviewed quarterly); Prometheus 45 days (compose) |

---

## Lecture 10.1: Your traces are a data breach waiting to happen

| Field | Value |
|---|---|
| ID | 10.1 |
| Title | Your traces are a data breach waiting to happen |
| Type | SL (slides + avatar, with one terminal beat) |
| Target duration | 6:00 (about 580 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Telemetry copies the most sensitive data in your system into the least protected place, and you need a threat model for it before you need a lawyer. |
| Prerequisites | Sections 3 to 9 (you have been emitting all of this) |
| Files used | Diagram D10 "Where PII leaks in telemetry"; `.atlas/spans.sqlite` (the local span store) |

**Learning objectives**

1. List what an Atlas trace contains that the original request did not intend to share: identifiers, questions, tool results, answers, judge inputs, feedback comments.
2. Name the places that data ends up, and who can read each.
3. State the four threats the rest of the section mitigates: over-collection, over-retention, over-access and leakage to third parties.

### Script

[SCREEN: terminal: print one agent span from the replayed day's local store]

```bash
uv run python -c "
from telemetry.local_store import LocalSpanStore
from northwind.config import Settings
a = LocalSpanStore(Settings.from_env().local_store_path).spans(kind='agent')[2].attributes
for k in ('user.id', 'session.id', 'atlas.tenant', 'langfuse.trace.tags', 'langfuse.observation.input', 'langfuse.observation.output'):
    print(k, '=', str(a[k])[:90])
"
```

[DEMO: output:]

```
user.id = NW-34624
session.id = s07-00006
atlas.tenant = ops
langfuse.trace.tags = ['tenant:ops', 'feature:shipment_status', 'intent:shipment', 'prompt:v1']
langfuse.observation.input = Where is shipment SHP-517225?
langfuse.observation.output = Shipment SHP-517225 is **in transit** at the Lyon hub, ETA 2026-09-22. (Source: Internal s
```

[AVATAR]

That's one span from the replayed day, sitting in a file on your laptop. An employee ID. The conversation it belongs to. The department. The question, and the answer. [PAUSE] Nobody put those in the store to share them. The instrumentation copied them because they're useful for debugging, and that's the problem. The same copy goes to a vendor's backend. Then a judge model reads it. Then a screenshot of it goes into a chat thread for a debugging session. Your production database has a security review. Does your tracing backend?

[SLIDE 1: What a trace contains]
- Identifiers: `user.id`, `session.id`, tenant; IPs and emails if you're careless
- User input: whatever the employee typed, including what they shouldn't have
- Tool arguments and results: records from ticketing, HR and shipping, sometimes whole documents
- The model's output: which may echo any of the above
- Retrieval context: knowledge-base passages, sometimes internal-only
- Copies: judge inputs (Section 8), feedback comments (8.3), screenshots

[AVATAR]

Everything. Identifiers, starting with the user id on every single request. The input, which is whatever the employee typed, including the password they pasted by mistake. Tool results, which are records from systems that have their own access controls. The output, which echoes the above. The retrieval context. And then the copies: the judge sees the question and the answer, and feedback comments are free text. [PAUSE] Your agent's memory is also your telemetry's memory, and telemetry remembers longer.

[SLIDE 2: Where it goes (Atlas as built so far)]

Diagram: D10 build 1, the flow and the leaks.

| Destination | Who can read it | Retention |
|---|---|---|
| Langfuse (Cloud or self-hosted) | every project member | project setting; verify |
| OTel Collector → any exporter (Langfuse, Phoenix) | whoever runs the collector, plus every backend it fans out to | per backend |
| Local span store (`.atlas/*.sqlite`) | anyone with the laptop | until `make clean` |
| Structured logs | log platform users; often the widest group in the company | 30 to 90 days, typically |
| Judge model provider (8.2) | the provider, under its data terms | per the provider's policy; verify |
| Prometheus | dashboard viewers; no ids by design (9.2) | 45 days in our compose |

[AVATAR]

Six destinations. Langfuse, where every project member can read every trace. The collector, which fans out to whatever backends you configure; Atlas's sends to Langfuse and Phoenix. The local span store on your laptop, which keeps everything until you run `make clean`. Logs, which in most companies have the widest audience of any system. The judge provider, which sees what you send it under its own data terms. And Prometheus, the one place ids shouldn't be, because the label allow-list keeps them out. [PAUSE] Count how many of those had a security review at your company. In most places the answer is one, and it's the database the data came from.

[SLIDE 3: The scale (one replayed day, synthetic)]
- An employee ID on every one of the 10,184 agent spans
- Every question and every answer, in plain text, on the agent span
- 678 answers flagged by the PII detector in 8.4, before anyone reviewed them
- Illustrative: multiply by 30 days of retention and four destinations, and a helpdesk holds over a million identifiers at rest
- Masking a value costs a fraction of a millisecond and no tokens

[AVATAR]

Here's the scale on the replayed day. An employee ID on every one of ten thousand requests. Every question and every answer, in plain text. Six hundred seventy-eight answers flagged by the PII detector from 8.4. Multiply by a month of retention and a few destinations, and a helpdesk is holding over a million identifiers at rest. [PAUSE] Masking a value before it leaves the process costs a fraction of a millisecond. No tokens. No dollars. This is the cheapest security control you will ever ship.

[SLIDE 4: Four threats, four answers]
- Over-collection: you captured what you didn't need → masking at the source, the SDK and the collector (10.2)
- Over-retention: you kept it longer than you needed → retention windows (10.3)
- Over-access: more people can read it than should → projects, roles, tenant separation (10.3)
- Third-party leakage: vendors and judge models see it → masking before export, data terms, self-hosting (10.2, 10.4)
- Plus: what the regulations require you to keep, which is not "nothing" (10.4)

[AVATAR]

Four threats, and the section maps onto them. Over-collection: you captured more than you needed. Over-retention: you kept it too long. Over-access: too many readers. And third-party leakage: vendors and judge models. Masking handles the first and most of the fourth. Retention and access handle the second and third. [PAUSE] And there's a twist in 10.4: some regulations require you to keep certain logs. Governance isn't "delete everything." It's "keep exactly what you must, protect it, and delete the rest on schedule."

[B-ROLL: D10 build 2, the same flow with shields: SDK `mask=`, the collector's attributes processor, retention, RBAC, "judge: send it masked data".]

One principle for the whole section. The safest data is the data you never collected. Every control downstream, retention, access, encryption, is a mitigation for a value that shouldn't have been there. So the order is: don't capture it; if you must, mask it before it leaves the process; if you must keep it raw, keep it short and keep it locked.

[SLIDE 5: Recap]
- A trace copies identifiers, questions and answers
- Six destinations, each with its own readers
- Mask before export: the cheapest control

### Recap

A trace copies identifiers, questions, records, answers and judge inputs into six destinations with wide access and long retention; the threats are over-collection, over-retention, over-access and third-party leakage, and masking before export is the cheapest fix.

### Transition

Next, the code-along: masking at the source, in the Langfuse SDK and in the OpenTelemetry collector, with a hash that keeps your joins working, and a hard look at how strong that hash is.

### Speaker notes: common mistakes and Q&A

- **"We self-host, so it's fine."** Self-hosting changes who the vendor is, not who on your team can read the traces. Access and retention still apply.
- **"Prometheus has no PII."** Only if you followed the label rule. One `user_id` label and it does; `test_metrics_label_allowlist` keeps Atlas honest.
- **Why the replay's spans show plain text.** The replay writes synthetic questions and answers straight into the store for the batch judge; the live agent masks every content attribute (10.2). Treat a store from real traffic as production data.
- **Judge provider data terms.** Vary by provider and plan; some offer zero-retention endpoints. Verify; don't assume.
- **Screenshots in chat.** The most common leak in practice. Masking at the source means the screenshot is safer too.

---

## Lecture 10.2: Code-along: masking in the SDK and the collector

| Field | Value |
|---|---|
| ID | 10.2 |
| Title | Code-along: masking in the SDK and the collector |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 680 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Mask PII in three layers, at the source when a span attribute is set, in the Langfuse SDK with `mask=`, and in the collector for everything else, replace identifiers with a hash so joins still work, and make sure the hash is strong enough for the identifier. |
| Prerequisites | 10.1; 4.6 (`mask=` introduced) |
| Files used | `src/northwind/pii.py`, `telemetry/genai_attrs.py`, `telemetry/langfuse_setup.py`, `deploy/otel-collector.yaml`, `tests/unit/test_pii.py`, `tests/integration/test_spans.py` |

**Learning objectives**

1. Read `mask_text` for emails, phones, employee IDs and card numbers (with a Luhn check), the placeholders it writes, and `stable_hash` for identifiers.
2. Trace the three layers: `genai_attrs._safe` on every content attribute, `Langfuse(mask=langfuse_mask)`, and the collector's `attributes/redact` processor that deletes and hashes.
3. Run `test_no_raw_pii_reaches_any_span`, the test that fails if raw PII ever reaches a span, and explain why an unkeyed hash of a five-digit ID is not a pseudonym.

### Script

[AVATAR]

Three layers, because each one catches what the others miss. [PAUSE] At the source, so a value is masked the moment it becomes a span attribute. In the SDK, so anything the Langfuse client captures on its own is masked on the way out. And in the collector, so a span from a library you don't control gets scrubbed before it reaches any backend. One masker, installed three times.

[SCREEN: VS Code, `src/northwind/pii.py`]

[CODE: `src/northwind/pii.py` (excerpt)]

```python
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMPLOYEE_ID_RE = re.compile(r"\bNW-\d{5}\b")
# +49 30 1234567, (555) 123-4567, 555-123-4567, +1 555 123 4567
PHONE_RE = re.compile(
    r"(?<![\w-])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.-]?\d{3,4}[\s.-]?\d{3,4}(?![\w-])"
)
CARD_RE = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
# Ticket ids and tracking ids are *not* PII and must survive masking.
_SAFE_RE = re.compile(r"\b(?:TCK|SHP)-\d{4,8}\b")


def short_hash(value: str, salt: str = "northwind", length: int = 8) -> str:
    """Deterministic short hash for joinable pseudonyms."""
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:length]


def mask_with_stats(
    text: str, *, hash_ids: bool = False, salt: str = "northwind"
) -> tuple[str, MaskStats]:
    """Mask PII in one string; returns the masked text and counts."""
    ...
    def tag(kind: str, raw: str) -> str:
        if hash_ids:
            return f"<{kind}:{short_hash(raw, salt)}>"
        return f"<{kind}>"
    ...
    def sub_card(m: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            counts["cards"] += 1
            return tag("CARD", digits)
        return m.group(0)
    ...


def langfuse_mask(*, data: Any) -> Any:
    """Drop-in for ``Langfuse(mask=langfuse_mask)``: keyword-only ``data`` argument."""
    return mask_value(data, hash_ids=True)
```

Four patterns. Email, phone, the Northwind employee ID, `NW-` and five digits, and anything that looks like a card number. Card candidates go through a Luhn check, so a long reference number stays readable and a real card doesn't. Ticket and shipment ids are protected before the phone pattern runs, so `TCK-100231` survives.

[SCREEN: zoom on `tag()` and `short_hash`]

Each match becomes a placeholder: `<EMAIL>`, `<PHONE>`, `<EMPLOYEE_ID>`, `<CARD>`. With `hash_ids=True`, the placeholder carries an eight-character hash of the value, so the same employee always gets the same token and you can still join a trace to a feedback score. `langfuse_mask` walks any structure, dicts, lists, strings, and applies that to every string. That's the shape the Langfuse SDK expects.

[SCREEN: terminal]

```bash
uv run python -c "
from northwind.pii import mask_with_stats, mask_text
text = 'My card 4111 1111 1111 1111 was declined, open a ticket for dana.whitfield@northwind.example, call me on +1 415 555 0142, id NW-04471, ticket TCK-100231'
print(mask_with_stats(text)[0]); print(mask_with_stats(text)[1]); print(mask_text(text, hash_ids=True))
"
```

[DEMO: output:]

```
My card <CARD> was declined, open a ticket for <EMAIL>, call me on <PHONE>, id <EMPLOYEE_ID>, ticket TCK-100231
MaskStats(emails=1, phones=1, employee_ids=1, cards=1)
My card <CARD:ed595cb8> was declined, open a ticket for <EMAIL:c8124ed3>, call me on <PHONE:953a8f02>, id <EMPLOYEE_ID:a116ca8c>, ticket TCK-100231
```

Four kinds of PII in, four placeholders out, and the ticket id untouched. Now, how private is `<EMPLOYEE_ID:a116ca8c>`?

```bash
uv run python -c "
from northwind.pii import stable_hash
print(next(f'NW-{n:05d}' for n in range(100_000) if stable_hash(f'NW-{n:05d}') == 'a116ca8c'))
"
```

[DEMO: prints `NW-04471` in about five hundredths of a second.]

[AVATAR]

Five hundredths of a second. [PAUSE] An employee ID has only a hundred thousand possible values, and the salt is in the source code, so anyone with the repo can hash all of them and look yours up. A hash of a low-entropy identifier is a lookup table, not a pseudonym. In production, use a keyed HMAC with a secret from your secret store, rotated on a schedule, so the hash is useless without the key. The shipped `stable_hash` is fine for synthetic data and for teaching the join; it is not what you ship.

[SLIDE 1: Layer one: at the source (`telemetry/genai_attrs.py`)]
- Every content attribute goes through `_safe(value, redact=True)`: `mask_value(..., hash_ids=True)`, then clipped to 4,000 characters
- That covers message bodies, tool arguments and results, retrieval queries, and Langfuse input/output
- Masked before the span exists, so the local store and every exporter get the masked text
- `user.id` is set as-is in-process: the local store needs it for the showback; the collector hashes it on export
- Exporting straight to Langfuse, without the collector? Hash `user.id` yourself first

[SCREEN: VS Code, `telemetry/genai_attrs.py`: `_safe`, then `set_tool` calling it for `gen_ai.tool.call.arguments` and `gen_ai.tool.call.result`]

```python
def _safe(value: Any, redact: bool) -> str:
    return _clip(mask_value(value, hash_ids=True) if redact else value)
```

Layer one is the one that does most of the work. Every helper that puts content on a span calls `_safe` first: mask, then clip to four thousand characters. Tool results are where most of the sensitive data arrives, and this is the line that catches it before the span exists. [PAUSE] One deliberate gap: `user.id` goes on the span as-is, because the local store needs the real id for the user showback in 6.3. The collector hashes it on the way out. If you export straight to Langfuse without the collector, hash it yourself before it becomes an attribute.

Layer two: the SDK.

[CODE: `telemetry/langfuse_setup.py` (excerpt from `init_langfuse`)]

```python
    _CLIENT = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        base_url=settings.langfuse_base_url,
        environment=settings.langfuse_environment,
        release=settings.langfuse_release,
        sample_rate=settings.langfuse_sample_rate,
        mask=langfuse_mask,
        blocked_instrumentation_scopes=["httpx", "urllib3", "sqlite3"],
        tracer_provider=tracer_provider,
        should_export_span=_should_export,
        ...
    )
```

One argument, `mask=langfuse_mask`, and every input, output and metadata value the Langfuse SDK records passes through it before export. That's the layer that protects the Langfuse-native `@observe` code from Section 4, which never calls `_safe`.

Layer three: the collector.

[SCREEN: `deploy/otel-collector.yaml`]

[CODE: `deploy/otel-collector.yaml` (excerpt; verify processor options against the collector-contrib docs)]

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 400
    spike_limit_mib: 100
  attributes/redact:
    actions:
      - key: gen_ai.tool.call.result
        action: delete
      - key: gen_ai.input.messages
        action: delete
      - key: gen_ai.output.messages
        action: delete
      - key: gen_ai.system_instructions
        action: delete
      - key: langfuse.observation.input
        action: delete
      - key: langfuse.observation.output
        action: delete
      - key: gen_ai.tool.call.arguments
        action: hash            # keep a stable fingerprint so identical calls can still be grouped
      - key: user.id
        action: hash            # joinable pseudonym, never the employee id
      - key: enduser.id
        action: hash
  tail_sampling: { ... }        # keep errors, slow, expensive, many-step and escalated traces (13.2)
  batch: { ... }

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, attributes/redact, tail_sampling, batch]
      exporters: [otlphttp/langfuse, otlphttp/phoenix, debug, spanmetrics]
```

Four processors, in order: `memory_limiter`, `attributes/redact`, `tail_sampling`, `batch`. The redaction step deletes outright what a backend never needs: tool results, message bodies, the system instructions, and the Langfuse input and output copies. It hashes what you still want to group by: tool arguments, `user.id` and `enduser.id`.

[SCREEN: zoom on the `delete` and `hash` actions]

[PAUSE] Delete versus hash is the whole design. Delete when nobody downstream needs the value. Hash when you need to count or join on it. And the collector's hash has the same weakness as ours: unkeyed, so a hashed employee ID is still guessable. The collector is the safety net for spans from libraries you never wrote a mask for. It is not the plan.

Now the test that makes this permanent.

[SCREEN: `tests/integration/test_spans.py`, then terminal]

[CODE: `tests/integration/test_spans.py::test_no_raw_pii_reaches_any_span`]

```python
def test_no_raw_pii_reaches_any_span(client):
    """10.2: four kinds of PII go in; none of the raw values comes out in any span attribute."""
    import json

    raw = ["dana.whitfield@northwind.example", "+1 415 555 0142", "NW-04471", "4111 1111 1111 1111"]
    _chat(
        client,
        f"My card {raw[3]} was declined, open a ticket for {raw[0]}, call me on {raw[1]}, id {raw[2]}",
        headers={"X-Tenant": "finance", "X-User": "u-1"},
    )
    blob = json.dumps([dict(s.attributes) for s in _spans(client)], default=str)
    for value in raw:
        assert value not in blob, f"raw PII in spans: {value}"
    assert "<CARD" in blob and "<EMAIL" in blob and "<EMPLOYEE_ID" in blob
```

Send a question containing all four kinds of PII through the real `/chat` endpoint with an in-memory exporter. Serialise every span's attributes. Assert none of the raw values is anywhere in the blob, and that the placeholders are. [PAUSE] This test runs on every pull request. If anyone adds a tool that copies a record into a span without `_safe`, it goes red. That's the control that lasts after you've stopped paying attention.

```bash
uv run pytest tests/unit/test_pii.py tests/integration/test_spans.py -q
```

[DEMO: `34 passed`]

[SLIDE 2: Masking rules]
- Mask before export, never after: at the source and in the SDK, not a cleanup job
- Delete what nobody needs; hash what you join on; placeholder the rest
- Low-entropy ids need a keyed HMAC, not a salted hash
- Luhn-check card candidates; protect ticket and shipment ids
- One test, in CI, that fails on any raw value

[AVATAR]

Rules. Mask before export, never with a cleanup job, because a cleanup job runs after the leak. Delete what nobody needs, hash what you join on, placeholder the rest. Key your hashes for anything with a small value space. Luhn-check cards so you don't blind yourself. And one test in CI that fails on any raw value.

[SLIDE 3: Recap]
- Three layers: source, SDK, collector
- Delete, hash or placeholder each field
- A CI test fails on any raw value

### Recap

One masker, three layers: `_safe` on every content attribute at the source, `mask=langfuse_mask` in the Langfuse client, and the collector's `attributes/redact` deleting bodies and hashing ids, with `test_no_raw_pii_reaches_any_span` in CI; and a salted hash of a five-digit ID is reversible, so production keys it.

### Transition

Masking limits what gets in. Next, the other two threats: how long it stays, and who can read it. Retention, access and tenant separation.

### Speaker notes: common mistakes and Q&A

- **The hash is the lesson.** `stable_hash` uses a public salt. Show the brute-force loop once; then show what changes in production: `hmac.new(secret, value, sha256)` with the secret from the environment, and a rotation plan that accepts broken historical joins.
- **Phone regex false positives.** Long numeric strings can match. The lookbehind and lookahead help, and ticket and shipment ids are protected; tune patterns per domain and test with real-shaped data.
- **Format examples.** The detector also matches documentation like "format `NW-12345`" (8.4). An allowlist for known examples keeps the PII-in-output metric honest.
- **Masking the retrieval context.** Knowledge-base passages rarely contain PII; if they do, the KB is the problem. Mask anyway; it's cheap.
- **Collector config drift.** `attributes` is a contrib processor; option names have changed before. Verify against the pinned image (0.116.1) before recording.
- **Coding exercise.** "PII masking" in `06-assessments/coding-exercises.md` is `mask_text` with stdlib `re` only.

---

## Lecture 10.3: Retention, access and tenant separation

| Field | Value |
|---|---|
| ID | 10.3 |
| Title | Retention, access and tenant separation |
| Type | SL (slides + avatar, with one screen beat) |
| Target duration | 6:00 (about 600 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Set a retention window per data class, one project per environment with roles, and decide tenant tags versus separate projects by who is allowed to see whom. |
| Prerequisites | 10.2; 4.3 (sessions, users, tags) |
| Files used | `10-resources/telemetry-governance-checklist.md` (retention and access sections), `deploy/docker-compose.observability.yml`, `Makefile` (`clean`), `.gitignore` |

**Learning objectives**

1. Write a retention table per data class: raw traces, scores, aggregates, datasets, logs, metrics.
2. Structure Langfuse as one project per environment with least-privilege roles, and set collector and Prometheus retention to match.
3. Choose between tenant tags in one project and separate projects per tenant, using a three-question test.

### Script

[AVATAR]

How long do you need a trace? [PAUSE] Long enough to debug an incident and to run the weekly drift report. That's about two weeks, and thirty days to be safe. Most teams keep traces for a year, because nobody set the number. A year of traces is a year of liability for a two-week need. Let's set the numbers.

[SLIDE 1: Retention by data class (Atlas policy)]

| Data class | Contains PII? | Retention | Why |
|---|---|---|---|
| Raw traces, prod | masked, hashed ids | 30 days | incidents and drift need 2 weeks; 30 is the margin |
| Raw traces, dev and staging | synthetic only | 7 days | nobody debugs last month's dev run |
| Scores (judge, feedback) | no (trace id and value) | 13 months | year-over-year drift |
| Aggregates (cost, latency, SLIs) | no | 13 months+ | showback history; finance wants trend |
| Datasets (`atlas-failures`) | masked inputs | indefinite, reviewed quarterly | they are your tests |
| Structured logs | masked, trace id | 30 days | same as traces |
| Prometheus | no PII by design | 45 days | 28-day SLO window plus margin |
| Local span store (laptops) | synthetic only in OFFLINE; else masked | purge on `make clean`; never commit | it's a laptop |

[AVATAR]

One table, one row per data class. Raw production traces, masked, thirty days. Dev and staging, seven, because nobody debugs last month's dev run. Scores and aggregates carry no PII, just ids and numbers, so thirteen months for year-over-year comparison. Datasets are your tests, so they stay, with a quarterly review. Logs match traces. Prometheus, forty-five days, the twenty-eight-day SLO window plus margin. And the local store on your laptop: synthetic only in offline mode, purged on clean, never committed.

[SCREEN: three files side by side. `deploy/docker-compose.observability.yml` with `--storage.tsdb.retention.time=45d` highlighted; the `Makefile` `clean` target (`rm -rf .atlas .pytest_cache .ruff_cache ...`); `.gitignore` with `.atlas/` and `*.sqlite` highlighted]

[PAUSE] Where do you set these? Prometheus takes a retention flag, and in Atlas's compose file it's right there: forty-five days. The local store is `.atlas`, which `make clean` deletes and `.gitignore` keeps out of every commit. Langfuse has a project-level data retention setting; the exact screen depends on your plan and version, so verify. Logs are your log platform's setting. Write all of them in the checklist, with a date.

[SLIDE 2: Projects and roles]
- One Langfuse project per environment: `atlas-dev`, `atlas-staging`, `atlas-prod`; keys differ, retention differs
- Roles: Owner (2 people), Admin (the on-call rotation), Member (engineers on Atlas), Viewer (stakeholders, 9.4)
- Prod traces: Members and above; dev traces: anyone on the team
- API keys per service, never per person; rotate on departure
- Judge and `to_dataset` jobs run with a scoped key that can write scores and dataset items, not delete

[AVATAR]

Projects. One per environment, with different keys and different retention. Roles, least privilege: two owners, the on-call rotation as admins, the engineers who work on Atlas as members, and stakeholders as viewers. The role names vary by Langfuse version; the shape doesn't. API keys belong to services, not people, so a departure doesn't mean a rotation of every key. And the judge and the dataset job run with a key that can write scores and items, and can't delete a project. [PAUSE] The question to ask about every reader is: what's the worst thing this role can do at three in the morning?

[SLIDE 3: Tenant tags or separate projects? Three questions]
1. May an engineer who supports tenant A see tenant B's traces? If no: separate projects
2. Are tenants different legal entities or jurisdictions? If yes: separate projects, maybe separate regions
3. Do you need cross-tenant dashboards (the showback, 6.3)? If yes: tags, or aggregate outside Langfuse
- Northwind: four departments of one company, one legal entity, shared support team, showback needed → tags in one project
- A SaaS with external customers → project per customer, aggregates in Prometheus

[AVATAR]

Tags or projects for tenants. Three questions. May an engineer supporting one tenant see another's traces? If not, separate projects. Are the tenants different legal entities, or in different jurisdictions? If so, separate projects, possibly separate regions. And do you need cross-tenant dashboards, like the showback? If so, tags, or aggregate outside Langfuse. [PAUSE] Northwind is four departments of one company with one support team and a showback report: tags in one project, which is what we've done since Section 4. If Atlas were a product sold to external customers, the answer flips: a project per customer, and the cross-customer numbers live in Prometheus, which has no PII to begin with.

[SLIDE 4: Access to the other destinations]
- Collector: runs in your network; config in git; exporters use secrets from the environment, never from the YAML
- Logs: same retention as traces; PII masked at the source, so the wide audience is acceptable
- Prometheus and Grafana: viewer accounts for stakeholders; the compose default admin password is for the lab only
- Judge provider: check the data terms; prefer zero-retention endpoints where offered; masked inputs regardless
- Laptops: `OFFLINE=1` uses synthetic data; a real-data export needs a ticket and a deletion date

[AVATAR]

And the other destinations. The collector's secrets come from the environment, never the YAML in git. Logs get the same retention as traces, and because masking happened at the source, their wide audience is acceptable. Grafana gets viewer accounts, and the compose admin password is for the lab, not for anything with a public IP. The judge provider: read the data terms, prefer zero-retention endpoints, and remember it only ever sees masked inputs anyway. And laptops: offline mode is synthetic. If someone needs a real-data export to debug something, that's a ticket, with a deletion date on it.

[SLIDE 5: The checklist]
- `10-resources/telemetry-governance-checklist.md`: retention table, project and role map, tenant decision, destinations and their owners
- Fill it once, date it, review quarterly
- Every row has an owner and a place where the setting lives
- It's the document your security team asks for; have it before they ask

[AVATAR]

All of this is in the governance checklist in the resources folder. Retention table, project and role map, the tenant decision with the three answers, and every destination with its owner and where the setting lives. Fill it once, date it, review it quarterly. [PAUSE] It's the document your security team will ask for. Having it before they ask is the difference between a review and an audit.

[SLIDE 6: Recap]
- Retention per data class, written down
- One project per environment, least privilege
- Tags or projects: ask who may see whom

### Recap

Set retention per data class, thirty days for masked prod traces and thirteen months for scores and aggregates; one project per environment with least-privilege roles and service keys; and tenant tags versus separate projects by three questions about who may see whom.

### Transition

Everything so far is about keeping less. Next, the regulations that require you to keep certain things, and what an audit trail for an agent looks like. Not legal advice; a map for the conversation with counsel.

### Speaker notes: common mistakes and Q&A

- **Retention set but not verified.** Have students check that a 31-day-old trace is actually gone. Settings drift.
- **Personal API keys in `.env` on shared machines.** Service keys, scoped, rotated.
- **"Tags are fine" for external customers.** Walk the three questions; question 1 usually flips it.
- **Langfuse retention and role names** differ between Cloud plans and self-hosted versions. Verify on screen.

---

## Lecture 10.4: Regulatory logging obligations (not legal advice)

| Field | Value |
|---|---|
| ID | 10.4 |
| Title | Regulatory logging obligations (not legal advice) |
| Type | TH (talking head, with slides and one terminal beat) |
| Target duration | 6:00 (about 800 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Some rules require you to keep an audit trail of what your agent did; know the shape of those obligations, build the trail from the spans you already have, and confirm the specifics with counsel. |
| Prerequisites | 10.1 to 10.3 |
| Files used | `10-resources/telemetry-governance-checklist.md` (obligations section); the local span store; `northwind.pii.stable_hash` |

**Learning objectives**

1. State, in plain terms, what record-keeping the EU AI Act asks of high-risk systems and why an internal helpdesk may or may not be in scope.
2. Distinguish an audit trail (what the system did) from debugging telemetry (what it saw), and list what belongs in each.
3. Produce a short list of questions to take to counsel and the data protection officer.

### Script

[SLIDE 0 (stays on screen as a lower third for the whole lecture): "This lecture is not legal advice. Verify obligations with your counsel and your data protection officer."]

[AVATAR]

I'm an engineer, not a lawyer, and this lecture is not legal advice. [PAUSE] It's the map I'd want before the meeting with counsel: which rules might apply to an agent like Atlas, what shape their logging requirements take, and how to build that from the spans you already have. Every specific in here needs to be checked by someone qualified for your jurisdiction and your use case.

[SLIDE 1: Why "delete everything" is also wrong]
- Section 10 so far: collect less, keep it shorter, restrict who reads it
- Some regulations require the opposite for specific records: keep an audit trail, for a minimum period
- The two are compatible: a small, deliberate audit trail; short-lived, masked debugging telemetry
- The mistake is treating them as one dataset with one retention

[AVATAR]

So far this section has said: collect less, keep it shorter, restrict access. Some regulations say the opposite for specific records: keep a trail, for a minimum period. Both are right, about different data. A small, deliberate audit trail with a long retention. And short-lived, masked debugging telemetry. [PAUSE] The mistake is treating them as one dataset with one retention setting. Then you either keep everything for years, or delete the thing an auditor asks for.

[SLIDE 2: The EU AI Act, in one slide (verify with counsel)]
- Applies in tiers; the strict record-keeping rules target "high-risk" systems listed in the Act's annexes
- Employment-related uses are on that list: recruitment, promotion, termination, task allocation, monitoring and evaluation of workers
- Atlas today answers policy questions, opens tickets, resets passwords: probably not making employment decisions
- Atlas tomorrow, if it triages leave requests or flags "underperforming" employees: that's a different conversation
- High-risk obligations include automatic logging of events over the system's lifetime, kept for a minimum period (the Act sets a floor in months; verify the current number), plus human oversight and technical documentation
- Also: general transparency duties for AI that interacts with people; telling users they're talking to an AI

[AVATAR]

The EU AI Act works in tiers, and the strict record-keeping rules target systems it classifies as high-risk, in an annex of use cases. Employment is on that list: recruitment, promotion, termination, task allocation, monitoring workers. Atlas today answers policy questions, opens tickets and resets passwords. It's probably not making employment decisions. [PAUSE] Atlas next year, wired into leave approvals or asked to flag underperformers, might be. Have that conversation with counsel before the feature ships.

For high-risk systems, the obligations include automatic logging of events over the system's lifetime, kept for a minimum period the Act sets in months, verify the current number, plus human oversight and documentation. Separately, transparency duties: users should know they're talking to an AI. Say so in the interface where people meet Atlas, and keep it that way.

[SLIDE 3: Other rules that touch telemetry (verify which apply to you)]
- GDPR and similar: traces are personal data; lawful basis, minimisation, purpose limitation, and subject rights apply. Access and erasure requests reach your tracing backend. The hash in 10.2 is how you find one person's traces
- Sector rules: health (HIPAA), finance (GLBA, PCI DSS for card data: a card number stored raw in a trace is a PCI event)
- Audit and assurance: SOC 2, ISO 27001: expect "show me who accessed what, when"
- Contracts: your enterprise customers' DPAs may set retention and location; your vendor's DPA sets theirs

[AVATAR]

Beyond the AI Act. Data protection law: traces are personal data, so lawful basis, minimisation and subject rights apply. An erasure request reaches your tracing backend, and the hash from 10.2, keyed in production, is how you find one person's traces. Sector rules for health and finance: a card number stored raw is a PCI problem; masked before export, it's a non-event. Assurance frameworks expect an access log for the telemetry itself. And contracts on both sides set terms. [PAUSE] None of this is exotic. It's the rules your production database already lives under, applied to a copy of its data you forgot you were making.

[SLIDE 4: An audit trail for an agent (what to keep, long)]
- Per request: timestamp, trace id, hashed user, tenant, prompt name and version, model and version actually served, tool calls with arguments hashed or summarised, decisions taken (ticket created, password reset, escalated to human), guardrail outcomes, the final answer's hash
- Not the raw prompt, not the raw tool results, not the retrieval chunks
- Built from spans you already emit (Sections 3 to 5); a small job writes one line per request to an append-only store
- Retention: long, per counsel; access: narrower than debugging telemetry

[AVATAR]

So what's the audit trail? Per request: when, the trace id, the hashed user, the tenant, which prompt version and model actually answered, which tools were called, with arguments hashed or summarised, what decisions were taken, guardrail outcomes, and a hash of the final answer. Not the raw prompt. Not the raw tool results. Not the retrieval chunks. [PAUSE] Every field is already a span attribute from Sections 3 to 5. Here's one line, built from a real span in the replayed day's store.

[SCREEN: terminal]

```bash
uv run python -c "
import hashlib, json
from telemetry.local_store import LocalSpanStore
from northwind.config import Settings
from northwind.pii import stable_hash
span = LocalSpanStore(Settings.from_env().local_store_path).spans(kind='agent')[2]
a = span.attributes
record = {
    'ts': round(span.start_time, 3), 'trace_id': span.trace_id, 'user': stable_hash(str(a['user.id'])),
    'tenant': a['atlas.tenant'], 'prompt_version': a['atlas.prompt_version'], 'model': a['gen_ai.request.model'],
    'tools': a['atlas.tool_calls'], 'outcome': a['atlas.outcome'],
    'answer_sha256': hashlib.sha256(str(a['langfuse.observation.output']).encode()).hexdigest()[:16],
}
print(json.dumps(record))
"
```

[DEMO: output (the replay is deterministic, so yours matches):]

```
{"ts": 1789345407.419, "trace_id": "3cd9a47a01a79a3015b08f81975765a3", "user": "14c293e9", "tenant": "ops", "prompt_version": "v1", "model": "gpt-4.1-mini", "tools": ["check_shipment"], "outcome": "resolved", "answer_sha256": "de5cf5fb05dbf7cb"}
```

When, which trace, which user as a hash, which department, which prompt and model, which tools, what happened, and a fingerprint of the answer. No question text, no answer text, no phone number. A job writes one of these per request to an append-only store with long retention and narrow access. [PAUSE] It answers "what did the system do, and could a human have intervened" without containing anyone's data. And remember 10.2: for an audit trail, the user hash should be a keyed HMAC, not this demo's salted hash.

[SLIDE 5: What never to log, anywhere]
- Credentials and secrets: passwords, tokens, one-time codes, the answers to identity verification questions
- Full payment card numbers, bank details
- Special-category data: health, biometrics, beliefs; if the helpdesk sees it, mask it at the source
- Raw content of a suspected prompt injection beyond what security needs
- Anything the DPA with your vendor prohibits sending to that vendor

[AVATAR]

And the list of things that go nowhere. Credentials, including one-time codes and verification answers: Atlas's `reset_password` takes only an employee ID and a verified flag, and the code goes to the employee's phone, never through Atlas. Keep it that way. Full card and bank numbers. Special-category data, like health, if the helpdesk ever sees it. Raw injection payloads beyond what security needs. And anything your vendor's agreement says can't go to that vendor. [PAUSE] Build this list into the source-level masking from 10.2, and the CI test, so it's enforced rather than remembered.

[SLIDE 6: Questions to take to counsel and the DPO]
1. Is Atlas, or any planned feature, in scope for high-risk obligations under the AI Act or a national equivalent?
2. What is our lawful basis for processing employee data in traces, and does the retention table match it?
3. What is the minimum audit-trail retention that applies to us, and what must it contain?
4. Does our tracing vendor's DPA cover the data we send, in the region we send it to?
5. How do we fulfil an access or erasure request against traces, scores and datasets?
6. Who signs off the governance checklist, and how often?

[AVATAR]

Six questions for the meeting, on the slide. [PAUSE] Bring the checklist from 10.3 and the retention table. Counsel will change some numbers. That's the point. What you're bringing is the engineering: masked telemetry, a separate audit trail, and a hash that finds one person's data. Those don't change.

[AVATAR]

Last word. This is a map, not the territory. Laws differ, they change, and your use case is yours. Get it checked. [PAUSE] But don't wait for the lawyer to start masking. That part is right under every regime I've seen.

[SLIDE 7: Recap]
- Audit trail and telemetry are different datasets
- Keep decisions and hashes; never credentials
- Take six questions to counsel

[SLIDE 8: You can now]
- Mask PII in three layers and prove it in CI
- Set retention and access per data class
- Separate an audit trail from debugging telemetry

### Recap

Regulations can require a long-lived audit trail of what the agent did, separate from short-lived masked debugging telemetry; build the trail from spans you already emit, keep credentials and raw records out of everything, and take the six questions to counsel. Not legal advice.

### Transition

The Section 10 quiz, and then Section 11, where you go on call and investigate three real-shaped incidents from their traces.

### Speaker notes: common mistakes and Q&A

- **Say the disclaimer out loud** at the start and the end, and keep the lower third on screen. Udemy reviewers and students both need it.
- **Don't quote article numbers or month counts** as fixed facts on camera; they change and differ by jurisdiction. Say "verify the current number".
- **"We're not in the EU."** The AI Act has extraterritorial reach in some cases, and other jurisdictions have similar frameworks. Point to counsel, not to a map.
- **Audit trail as "just keep the traces longer."** The whole lecture argues against that. Separate store, separate fields, separate access.
- **Password reset verification answers** are the most common credential leak into spans in helpdesk agents. Mention it twice.

---

## Lecture 10.5: Quiz: Governance

| Field | Value |
|---|---|
| ID | 10.5 |
| Title | Quiz: Governance |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 130 spoken words at ~140 wpm, plus slide time); quiz about 6 minutes |
| One idea | Check you can place a masking control at the right layer, set retention per data class, and separate an audit trail from debugging telemetry. |
| Prerequisites | 10.1 to 10.4 |
| Files used | `06-assessments/quizzes/section-10.md` (6 questions) |

**Learning objectives**

1. Choose the right masking layer and the right replacement (placeholder versus keyed hash) for a given field.
2. Decide tags versus projects for a tenant scenario, and audit trail versus telemetry for a given record.

### Script

[AVATAR]

Six questions. One on which layer catches PII from a library you don't control. One on when to hash versus when to placeholder. One retention question. One tenant scenario, tags or projects, using the three questions. One on which fields belong in an audit trail and which never go anywhere. And one on the difference between a record you must delete and a record you must keep.

[SLIDE 1: Quiz: 6 questions]
- Masking layers and hash vs placeholder
- Retention by data class
- Tags vs projects
- Audit trail vs telemetry

[AVATAR]

A tip: for any field, ask two questions in order. Do I need to join on it later? If yes, hash. Do I need it at all? If no, don't collect it.

### Recap

The quiz checks that you can apply masking, retention, access and audit-trail decisions to concrete fields and scenarios.

### Transition

Next section, you're on call. Three incidents, real-shaped spans, and the answer isn't revealed until you've looked.

### Speaker notes: common mistakes and Q&A

- Most-missed: "Where does the verification answer for a password reset go?" Answer: nowhere; it's never logged.
- Second: students choose "tags" for a SaaS with external customers; walk the three questions.
