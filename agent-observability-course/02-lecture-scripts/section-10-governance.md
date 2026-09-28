# Section 10: Privacy, Security and Governance of Telemetry

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 32 minutes (5 lectures, including one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `operations`, `warehouse`, `finance`, `sales`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Any trace shown on screen in this section uses the synthetic Northwind data only; never a real employee record.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on langfuse 4.15 (`mask=`, `mask_otel_spans=`) / OpenTelemetry Collector contrib (processor names: verify against the current collector docs)."
> **Standing disclaimer (lecture 10.4, on screen for the whole lecture):** "This lecture is not legal advice. Verify obligations with your counsel and your data protection officer."

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.pii` (`mask_text`, `mask_fn`, `stable_hash`, `PATTERNS`), `telemetry/langfuse_setup.py` (`Langfuse(mask=mask_fn, ...)`), `telemetry/otel_setup.py`, `deploy/otel-collector.yaml` (`redaction` and `transform` processors), `app/tools.py` (`summarise_for_span`), `tests/unit/test_pii.py`, `tests/integration/test_no_pii_in_spans.py`, `10-resources/telemetry-governance-checklist.md`.

**The numbers card (one replayed day, synthetic data):**

| Item | Value |
|---|---|
| PII found in raw traces before masking | 1,240 email addresses, 310 phone numbers, about 10,000 employee IDs (one per request), 6 payment card numbers (expense questions), 90 postal addresses |
| Where it lives | 62% in tool results (`lookup_ticket`, `check_shipment`), 31% in user input, 7% in Atlas's output |
| Masking cost | about 0.4 ms per span; zero tokens, zero dollars |
| After masking | 0 raw values in spans; `user_id` is a 16-hex HMAC; joins still work |
| Retention (Atlas policy) | traces 30 days prod, 7 days dev; scores and aggregates 13 months; datasets indefinitely (reviewed quarterly) |

---

## Lecture 10.1: Your traces are a data breach waiting to happen

| Field | Value |
|---|---|
| ID | 10.1 |
| Title | Your traces are a data breach waiting to happen |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 580 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Telemetry copies the most sensitive data in your system into the least protected place, and you need a threat model for it before you need a lawyer. |
| Prerequisites | Sections 3 to 9 (you have been emitting all of this) |
| Files used | Diagram "where the data goes" |

**Learning objectives**

1. List what an Atlas trace contains that the original request did not intend to share: prompts with PII, tool results with records, judge inputs, feedback comments.
2. Name the five places that data ends up, and who can read each.
3. State the four threats the rest of the section mitigates: over-collection, over-retention, over-access and leakage to third parties.

### Script

[B-ROLL: a raw Atlas trace in a viewer, synthetic data. Zoom in on a tool result: `{"ticket": "NW-48213", "employee": "Dana Whitfield", "id": "NW-004471", "phone": "+1 415 555 0142", "issue": "expense card ending 4412 declined"}`. Each field lights up red one by one.]

[AVATAR]

That's a trace from Section 5. It has a name, an employee ID, a phone number and the last four digits of a payment card. [PAUSE] Nobody put those in the trace on purpose. `lookup_ticket` returned them, the agent needed them, and the instrumentation faithfully copied the whole thing into a span. Then the exporter sent it to a vendor. Then the judge read it. Then a screenshot of it went into Slack for a debugging thread. Your production database has a security review. Does your tracing backend?

[SLIDE 1: What a trace contains]
- User input: whatever the employee typed, including what they shouldn't have
- Tool arguments and results: records from ticketing, HR, shipping, sometimes whole documents
- The model's output: which may echo any of the above
- Retrieval context: knowledge-base chunks, sometimes internal-only
- Judge inputs (Section 8): all of the above, sent to a second model
- Feedback comments (8.3): free text, and people paste anything
- Metadata: `user_id`, `session_id`, tenant, IPs if you're careless

[AVATAR]

Everything. The input, which is whatever the employee typed, including the password they pasted by mistake. Tool results, which are records from ticketing, HR and shipping systems that have their own access controls. The output, which echoes the above. The retrieval context. And then the copies: the judge sees all of it, and feedback comments are free text. [PAUSE] Your agent's memory is also your telemetry's memory, and telemetry remembers longer.

[SLIDE 2: Where it goes (Atlas as built so far)]

| Destination | Who can read it | Default retention |
|---|---|---|
| Langfuse (Cloud or self-hosted) | every project member | project setting; verify |
| OTel Collector → any exporter | whoever runs the collector, plus every backend it fans out to | per backend |
| Local span store (`local_store.py`) | anyone with the laptop | forever |
| Structured logs | log platform users; often the widest group in the company | 30 to 90 days, typically |
| Judge model provider (8.2) | the provider, under its data terms | per the provider's policy; verify |
| Prometheus | dashboard viewers; no PII by design if you followed 5.5 | 45 days in our compose |

[B-ROLL: the diagram builds: Atlas in the centre, six arrows out, each destination with a small "who can read" badge.]

[AVATAR]

Six destinations. Langfuse, where every project member can read every trace. The collector, which fans out to whatever backends you configure. The local span store on your laptop, which has no retention at all. Logs, which in most companies have the widest audience of any system. The judge provider, which sees the full trace under its own data terms. And Prometheus, which is the one place PII shouldn't be, because we never put ids in labels. [PAUSE] Count how many of those had a security review at your company. In most places the answer is one, and it's Prometheus.

[SLIDE 3: The numbers (one replayed day, synthetic)]
- 1,240 email addresses, 310 phone numbers, about 10,000 employee IDs, 6 card numbers, 90 addresses
- 62% in tool results, 31% in user input, 7% in Atlas's output
- Multiply by 30 days of retention and 4 destinations: about 1.5 million PII values at rest
- Cost of masking all of it: about 0.4 ms per span, zero tokens

[AVATAR]

Here's the scale, from the replayed day. Twelve hundred emails. Three hundred phone numbers. An employee ID in essentially every request. Six card numbers, from people asking about declined expense cards. Most of it, sixty-two percent, arrived in tool results, which is the part nobody looks at in the UI. Thirty days of retention, four destinations: about a million and a half personal data values at rest, for a helpdesk. [PAUSE] And the cost of masking every one of them before they leave the process is four tenths of a millisecond per span. No tokens. No dollars. This is the cheapest security control you will ever ship.

[SLIDE 4: Four threats, four lectures]
- Over-collection: you captured what you didn't need → masking at the SDK and the collector (10.2)
- Over-retention: you kept it longer than you needed → retention windows (10.3)
- Over-access: more people can read it than should → projects, roles, tenant separation (10.3)
- Third-party leakage: vendors and judge models see it → masking before export, data terms, self-hosting (10.2, 10.4)
- Plus: what the regulations require you to keep, which is not "nothing" (10.4)

[AVATAR]

Four threats, and the section maps onto them. Over-collection: you captured more than you needed. Over-retention: you kept it too long. Over-access: too many readers. And third-party leakage: vendors and judge models. Masking handles the first and most of the fourth. Retention and access handle the second and third. [PAUSE] And there's a twist in 10.4: some regulations require you to keep certain logs. Governance isn't "delete everything." It's "keep exactly what you must, protect it, and delete the rest on schedule."

[AVATAR]

One principle for the whole section. The safest data is the data you never collected. Every control we add downstream, retention, access, encryption, is a mitigation for a value that shouldn't have been there. So the order is: don't capture it; if you must, mask it before it leaves the process; if you must keep it raw, keep it short and keep it locked. [PAUSE] Let's start with the code.

### Recap

A trace copies prompts, records, outputs and judge inputs into six destinations with wide access and long retention; the threats are over-collection, over-retention, over-access and third-party leakage, and masking before export is the cheapest fix.

### Transition

Next, the code-along: masking in the Langfuse SDK, in the OpenTelemetry collector, and at the source in tool results, with a hash that keeps your joins working.

### Speaker notes: common mistakes and Q&A

- **"We self-host, so it's fine."** Self-hosting changes who the vendor is, not who on your team can read the traces. Access and retention still apply.
- **"Prometheus has no PII."** Only if you followed the label rule. One `user_id` label and it does.
- **Judge provider data terms.** Vary by provider and plan; some offer zero-retention endpoints. Verify; don't assume.
- **Screenshots in Slack.** The most common leak in practice. Masking at the source means the screenshot is safe too.

---

## Lecture 10.2: Code-along: masking in the SDK and the collector

| Field | Value |
|---|---|
| ID | 10.2 |
| Title | Code-along: masking in the SDK and the collector |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 700 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Mask PII in three layers, at the source in tool results, in the Langfuse SDK with `mask=`, and in the collector for everything else, and replace identifiers with a keyed hash so joins still work. |
| Prerequisites | 10.1; 4.6 (`mask=` introduced) |
| Files used | `src/northwind/pii.py`, `telemetry/langfuse_setup.py`, `deploy/otel-collector.yaml`, `app/tools.py`, `tests/unit/test_pii.py`, `tests/integration/test_no_pii_in_spans.py` |

**Learning objectives**

1. Implement `mask_text` for emails, phones, employee IDs and card numbers (with a Luhn check), and `stable_hash` for identifiers.
2. Install `mask_fn` on the Langfuse client with `mask=` and confirm masked spans in the UI.
3. Configure the collector's `redaction` and `transform` processors as the last line of defence, and write the test that fails if raw PII ever reaches a span.

### Script

[AVATAR]

Three layers, because each one catches what the others miss. [PAUSE] At the source, so a tool result never carries a whole record into a span. In the SDK, so anything that reaches Langfuse is masked on the way out. And in the collector, so a span from a library you don't control gets scrubbed before it reaches any backend. Let's write the masker once and install it three times.

[SCREEN: VS Code, `src/northwind/pii.py`]

[CODE: `src/northwind/pii.py` (excerpt)]

```python
import hashlib
import hmac
import os
import re
from typing import Any

PATTERNS: dict[str, re.Pattern[str]] = {
    "email":       re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone":       re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"),
    "employee_id": re.compile(r"\bNW-\d{6}\b"),                       # Northwind employee ids
    "card":        re.compile(r"\b(?:\d[ -]?){13,19}\b"),
}
_SECRET = os.environ.get("PII_HASH_KEY", "dev-only-key").encode()


def _luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
        alt = not alt
    return total % 10 == 0


def stable_hash(value: str, length: int = 16) -> str:
    """Keyed hash: same input -> same output, so joins work; no way back without the key."""
    return hmac.new(_SECRET, value.encode(), hashlib.sha256).hexdigest()[:length]


def mask_text(text: str) -> str:
    if not text:
        return text
    def card_repl(m: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        return "[card]" if _luhn_ok(digits) else m.group(0)         # only real card numbers; not ticket numbers
    text = PATTERNS["card"].sub(card_repl, text)
    text = PATTERNS["email"].sub("[email]", text)
    text = PATTERNS["employee_id"].sub(lambda m: f"[emp:{stable_hash(m.group(0), 8)}]", text)
    text = PATTERNS["phone"].sub("[phone]", text)
    return text


def mask_fn(data: Any) -> Any:
    """Langfuse `mask=` hook: walks any structure and masks every string."""
    if isinstance(data, str):
        return mask_text(data)
    if isinstance(data, dict):
        return {k: mask_fn(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return type(data)(mask_fn(v) for v in data)
    return data
```

Four patterns. Email, phone, the Northwind employee ID format, and anything that looks like a card number. Two details that matter. Card candidates go through a Luhn check, so a ticket number with sixteen digits stays readable and a real card doesn't. And employee IDs aren't just replaced with a placeholder; they're replaced with a keyed hash, eight characters, using HMAC with a secret from the environment. Same ID, same hash, every time. So you can still count requests per employee, still join a trace to a feedback score, still find every trace for one person when they ask you to. But nobody can turn the hash back into the ID without the key. [PAUSE] `mask_fn` walks any structure, dicts, lists, strings, and applies `mask_text` to every string. That's the shape the Langfuse SDK expects.

Layer one: the SDK.

[SCREEN: `telemetry/langfuse_setup.py`]

[CODE: `telemetry/langfuse_setup.py` (excerpt)]

```python
from langfuse import Langfuse
from northwind.pii import mask_fn

lf = Langfuse(
    public_key=settings.langfuse_public_key, secret_key=settings.langfuse_secret_key, base_url=settings.langfuse_base_url,
    environment=settings.environment, release=settings.release,
    mask=mask_fn,                    # every input, output and metadata value passes through here before export
    sample_rate=settings.trace_sample_rate,
)
```

One argument. `mask=mask_fn`, and every input, output and metadata value on every observation passes through it before it's exported. Verified on langfuse four fifteen; there's also `mask_otel_spans=` for spans that arrive from other OpenTelemetry instrumentation, which the note on screen mentions.

Layer two: the source. The SDK masks what it sees, but a tool result is still a whole record in memory, and OpenInference or a log line might copy it elsewhere. So tools summarise for the span.

[SCREEN: `app/tools.py`]

[CODE: `app/tools.py` (excerpt)]

```python
def lookup_ticket(ticket_id: str) -> dict:
    record = ticket_store.get(ticket_id)                       # full record: name, phone, issue text
    with lf.start_as_current_observation(name="lookup_ticket", as_type="tool", input={"ticket_id": ticket_id}) as span:
        span.update(output=summarise_for_span(record))         # {"ticket": id, "status": ..., "employee": "[emp:3f9a..]", "issue": mask_text(issue)[:200]}
    return record                                              # the model still gets what it needs, in process


def summarise_for_span(record: dict) -> dict:
    return {"ticket": record["id"], "status": record["status"], "priority": record["priority"],
            "employee": f"[emp:{stable_hash(record['employee_id'], 8)}]", "issue": mask_text(record["issue"])[:200]}
```

The tool returns the full record to the agent, in process, because the model needs it. But the span gets a summary: the ticket id, status, priority, the hashed employee, and the first two hundred characters of the issue, masked. [PAUSE] This is the layer that fixes sixty-two percent of the problem, because tool results are where most of the PII was. And it's a design choice, not a regex: decide what a span needs to be useful for debugging, and send only that.

Layer three: the collector.

[SCREEN: `deploy/otel-collector.yaml`]

[CODE: `deploy/otel-collector.yaml` (excerpt; verify processor names against the current collector-contrib docs)]

```yaml
processors:
  redaction:
    allow_all_keys: true
    blocked_values:                       # regexes; matches are replaced with ****
      - "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
      - "\\bNW-\\d{6}\\b"
      - "\\b(?:\\d[ -]?){13,19}\\b"
    summary: info                         # adds counts of redacted values as span attributes, for the dashboard
  transform:
    trace_statements:
      - context: span
        statements:
          - replace_all_patterns(attributes, "value", "\\+?\\d[\\d\\s().-]{7,}\\d", "[phone]")
          - delete_key(attributes, "http.request.header.authorization")
  batch: {}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [redaction, transform, batch]
      exporters: [otlphttp/langfuse, otlphttp/phoenix]
```

Two processors, in front of every exporter. `redaction` takes a list of regexes and replaces matches in every attribute value, and with `summary: info` it adds a count of what it redacted to the span, which is a nice metric. `transform` uses the collector's OTTL language for the phone pattern and for deleting an attribute outright, like an authorization header that an HTTP instrumentation might have captured. [PAUSE] Processor names and options change between collector releases; the on-screen note says to verify. The idea doesn't change: the collector is the last line, and it catches spans from libraries you never wrote a `mask=` for.

Now the test that makes this permanent.

[SCREEN: `tests/integration/test_no_pii_in_spans.py`, then terminal]

[CODE: `tests/integration/test_no_pii_in_spans.py` (excerpt)]

```python
RAW = ["dana.whitfield@northwind.example", "+1 415 555 0142", "NW-004471", "4111 1111 1111 1111"]


def test_no_raw_pii_reaches_any_span(atlas_offline, in_memory_exporter):
    atlas_offline.chat(question=f"My card {RAW[3]} was declined, ticket for {RAW[0]}, call me on {RAW[1]}, id {RAW[2]}",
                       tenant="finance", user_id=RAW[2])
    blob = json.dumps([span_to_dict(s) for s in in_memory_exporter.get_finished_spans()])
    for value in RAW:
        assert value not in blob, f"raw PII in spans: {value}"
    assert "[card]" in blob and "[email]" in blob and "[emp:" in blob
```

Send a question containing all four kinds of PII, through the offline agent, with an in-memory exporter. Serialise every span. Assert none of the raw values is anywhere in the blob, and that the placeholders are. [PAUSE] This test runs on every pull request. If anyone adds a tool that copies a record into a span, it goes red. That's the control that lasts after you've stopped paying attention.

```bash
uv run pytest tests/unit/test_pii.py tests/integration/test_no_pii_in_spans.py -q
```

[DEMO: 9 passed. Then the Langfuse UI: the same trace as the 10.1 hook, now reading `"employee": "[emp:3f9a1c2b]", "phone": "[phone]", "issue": "expense card ending [card] declined"`.]

Nine green. And the trace from the hook, in Langfuse, now: a hashed employee, a placeholder phone, a placeholder card. Still perfectly debuggable. Still joinable by the hash. Not a breach.

[SLIDE 1: Masking rules]
- Mask before export, never after: the SDK hook and the source summary, not a cleanup job
- Hash identifiers you need for joins; placeholder everything else
- Luhn-check card candidates; don't mask ticket numbers into uselessness
- Collector processors are the safety net, not the plan
- One test, in CI, that fails on any raw value

[AVATAR]

Rules. Mask before export, never with a cleanup job, because a cleanup job runs after the leak. Hash what you need for joins, placeholder the rest. Luhn-check cards so you don't blind yourself. The collector is the net, not the plan. And one test in CI that fails on any raw value.

### Recap

One masker, three layers: `summarise_for_span` at the source, `mask=mask_fn` in the Langfuse client, `redaction` and `transform` in the collector, with a keyed hash for identifiers so joins survive, and a CI test that fails on any raw value.

### Transition

Masking limits what gets in. Next, the other two threats: how long it stays, and who can read it. Retention, access and tenant separation.

### Speaker notes: common mistakes and Q&A

- **`PII_HASH_KEY` in dev.** The default is `dev-only-key`; production must set a real secret, and rotating it breaks historical joins. Say both.
- **Phone regex false positives.** Long numeric strings like shipment ids can match. The lookbehind and lookahead help; tune `PATTERNS` per domain and test with real-shaped data.
- **Masking the retrieval context.** Knowledge-base chunks rarely contain PII; if they do, the KB is the problem. Mask anyway; it's free.
- **Collector config drift.** `redaction` and `transform` are contrib processors; option names have changed before. Verify before recording and keep the YAML in the repo with a version comment.
- **Coding exercise.** "PII masking" in `06-assessments/coding-exercises.md` is `mask_text` with stdlib `re` only.

---

## Lecture 10.3: Retention, access and tenant separation

| Field | Value |
|---|---|
| ID | 10.3 |
| Title | Retention, access and tenant separation |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 650 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Set a retention window per data class, one project per environment with roles, and decide tenant tags versus separate projects by who is allowed to see whom. |
| Prerequisites | 10.2; 4.3 (sessions, users, tags) |
| Files used | `10-resources/telemetry-governance-checklist.md` (retention and access sections) |

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
| Prometheus | no PII by design | 45 days | 30-day SLO window plus margin |
| Local span store (laptops) | synthetic only in OFFLINE; else masked | purge on `make clean`; never commit | it's a laptop |

[AVATAR]

One table, one row per data class. Raw production traces, masked, thirty days. Dev and staging, seven, because nobody debugs last month's dev run. Scores and aggregates carry no PII, just ids and numbers, so thirteen months for year-over-year comparison. Datasets are your tests, so they stay, with a quarterly review. Logs match traces. Prometheus, forty-five days, a thirty-day SLO window plus margin. And the local store on your laptop: synthetic only in offline mode, purged on clean, never committed. [PAUSE] Where do you set these? Langfuse has a project-level data retention setting; the exact screen depends on your plan and version, so verify. Prometheus takes a retention flag in the compose file. Logs are your log platform's setting. Write all of them in the checklist, with a date.

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
| Type | TH (talking head, with slides) |
| Target duration | 6:00 (about 750 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Some rules require you to keep an audit trail of what your agent did; know the shape of those obligations, build the trail from the spans you already have, and confirm the specifics with counsel. |
| Prerequisites | 10.1 to 10.3 |
| Files used | `10-resources/telemetry-governance-checklist.md` (obligations section) |

**Learning objectives**

1. State, in plain terms, what record-keeping the EU AI Act asks of high-risk systems and why an internal helpdesk may or may not be in scope.
2. Distinguish an audit trail (what the system did) from debugging telemetry (what it saw), and list what belongs in each.
3. Produce a short list of questions to take to counsel and the data protection officer.

### Script

[SLIDE 0 (stays on screen as a lower third for the whole lecture): "This lecture is not legal advice. Verify obligations with your counsel and your data protection officer."]

[AVATAR]

I'm an engineer, not a lawyer, and this lecture is not legal advice. [PAUSE] It's the map I'd want before the meeting with counsel: which rules might apply to an agent like Atlas, what shape their logging requirements take, and how to build that from the spans you already have. Every specific in here needs to be checked by someone qualified for your jurisdiction and your use case. Keep the lower third in mind the whole way through.

[SLIDE 1: Why "delete everything" is also wrong]
- Section 10 so far: collect less, keep it shorter, restrict who reads it
- Some regulations require the opposite for specific records: keep an audit trail, for a minimum period
- The two are compatible: a small, deliberate audit trail; short-lived, masked debugging telemetry
- The mistake is treating them as one dataset with one retention

[AVATAR]

So far this section has said: collect less, keep it shorter, restrict access. Some regulations say the opposite for specific records: keep a trail, for a minimum period. Both are right, because they're talking about different data. A small, deliberate audit trail with a long retention. And short-lived, masked debugging telemetry. [PAUSE] The mistake is treating them as one dataset with one retention setting. Then you either keep everything for years, or delete the thing an auditor asks for.

[SLIDE 2: The EU AI Act, in one slide (verify with counsel)]
- Applies in tiers; the strict record-keeping rules target "high-risk" systems listed in the Act's annexes
- Employment-related uses are on that list: recruitment, promotion, termination, task allocation, monitoring and evaluation of workers
- Atlas today answers policy questions, opens tickets, resets passwords: probably not making employment decisions
- Atlas tomorrow, if it triages leave requests or flags "underperforming" employees: that's a different conversation
- High-risk obligations include automatic logging of events over the system's lifetime, kept for a minimum period (the Act sets a floor in months; verify the current number), plus human oversight and technical documentation
- Also: general transparency duties for AI that interacts with people; telling users they're talking to an AI

[AVATAR]

The EU AI Act works in tiers, and the strict record-keeping rules target systems it classifies as high-risk, in an annex of use cases. Employment is on that list: recruitment, promotion, termination, task allocation, monitoring workers. Atlas today answers policy questions, opens tickets and resets passwords. It's probably not making employment decisions. [PAUSE] Atlas next year, wired into leave approvals or asked to flag underperformers, might be. Have that conversation with counsel before the feature ships.

For high-risk systems, the obligations include automatic logging of events over the system's lifetime, kept for a minimum period the Act sets in months, verify the current number, plus human oversight and documentation. Separately, transparency duties: users should know they're talking to an AI. Atlas says so in its greeting. Keep it that way.

[SLIDE 3: Other rules that touch telemetry (verify which apply to you)]
- GDPR and similar: traces are personal data; lawful basis, minimisation, purpose limitation, and subject rights apply. Access and erasure requests reach your tracing backend. The hash in 10.2 is how you find one person's traces
- Sector rules: health (HIPAA), finance (GLBA, PCI DSS for card data: the six card numbers from 10.1 are a PCI event if stored raw)
- Audit and assurance: SOC 2, ISO 27001: expect "show me who accessed what, when"
- Contracts: your enterprise customers' DPAs may set retention and location; your vendor's DPA sets theirs

[AVATAR]

Beyond the AI Act. Data protection law: traces are personal data, so lawful basis, minimisation and subject rights apply. An erasure request reaches your tracing backend, and the keyed hash from 10.2 is how you find one person's traces. Sector rules for health and finance. Card data: the six numbers from the replayed day are a PCI problem if stored raw, and a non-event because they were masked before export. Assurance frameworks expect an access log for the telemetry itself. And contracts on both sides set terms. [PAUSE] None of this is exotic. It's the rules your production database already lives under, applied to a copy of its data you forgot you were making.

[SLIDE 4: An audit trail for an agent (what to keep, long)]
- Per request: timestamp, trace id, hashed user, tenant, prompt name and version, model and version actually served, tool calls with arguments hashed or summarised, decisions taken (ticket created, password reset, escalated to human), guardrail outcomes, the final answer's hash
- Not the raw prompt, not the raw tool results, not the retrieval chunks
- Built from spans you already emit (Sections 3 to 5); a small exporter writes one line per request to an append-only store
- Retention: long, per counsel; access: narrower than debugging telemetry

[AVATAR]

So what's the audit trail? Per request: when, the trace id, the hashed user, the tenant, which prompt version and model actually answered, which tools were called, with arguments hashed or summarised, what decisions were taken, guardrail outcomes, and a hash of the final answer. Not the raw prompt. Not the raw tool results. Not the retrieval chunks. [PAUSE] Every field is already a span attribute from Sections 3 to 5. A small exporter writes one line per request to an append-only store with long retention and narrow access. It answers "what did the system do, and could a human have intervened" without containing anyone's phone number.

[SLIDE 5: What never to log, anywhere]
- Credentials and secrets: passwords, tokens, the answers to identity verification questions in `reset_password`
- Full payment card numbers, bank details
- Special-category data: health, biometrics, beliefs; if the helpdesk sees it, mask it at the source
- Raw content of a suspected prompt injection beyond what security needs
- Anything the DPA with your vendor prohibits sending to that vendor

[AVATAR]

And the list of things that go nowhere. Credentials, including the answers to the verification questions in the password reset flow: `reset_password` takes them, checks them, and never puts them on a span. Full card and bank numbers. Special-category data, like health, if the helpdesk ever sees it. Raw injection payloads beyond what security needs. And anything your vendor's agreement says can't go to that vendor. [PAUSE] Build this list into the source-level masking from 10.2, and the CI test, so it's enforced rather than remembered.

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
| Target duration | Video 1:00 (about 140 spoken words at ~140 wpm, plus slide time); quiz about 6 minutes |
| One idea | Check you can place a masking control at the right layer, set retention per data class, and separate an audit trail from debugging telemetry. |
| Prerequisites | 10.1 to 10.4 |
| Files used | `06-assessments/quizzes/section-10.md` (6 questions) |

**Learning objectives**

1. Choose the right masking layer and the right replacement (placeholder versus keyed hash) for a given field.
2. Decide tags versus projects for a tenant scenario, and audit trail versus telemetry for a given record.

### Script

[AVATAR]

Six questions. One on which layer catches PII from a library you don't control. One on when to hash versus when to placeholder. One retention question with a data class you have to place in the table. One tenant scenario, tags or projects, using the three questions. One on which fields belong in an audit trail and which never go anywhere. And one on the difference between a record you must delete and a record you must keep.

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
