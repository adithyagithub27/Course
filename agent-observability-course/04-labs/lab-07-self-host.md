# Lab 7: Self-Hosted Stack End to End

| Field | Details |
|---|---|
| **Section / lecture** | Section 13, lecture 13.6 |
| **Time estimate** | 90 minutes (plus image pull time) |
| **Difficulty** | Advanced |
| **Goal** | Run the complete stack locally: self-hosted Langfuse; the OpenTelemetry Collector redacting and tail-sampling, then fanning traces out to Langfuse and Phoenix; Prometheus and Grafana from Lab 6; Atlas exporting only to the Collector. Prove redaction and sampling from the data, get the CI budget gate green (and red on purpose), and stop the Collector under load to show Atlas keeps serving. |
| **You will produce** | A running `deploy/` stack, a trace in your own Langfuse and in Phoenix, a redacted tool span, a red and a green CI run, and `notes/lab-07.md` |

---

## Prerequisites

- Labs 1 to 6 complete (Lab 6's stack in particular).
- Lectures 13.1 to 13.5 watched.
- Docker with at least 6 GB RAM allocated (Langfuse v3 runs Postgres, ClickHouse, Redis and MinIO next to its web and worker containers).
- A GitHub fork of the course repo for Step 6 (or run the gate locally only).
- Free ports: 3000 (Langfuse), 9090 (Langfuse's MinIO), 3001 (Grafana), 9091 (Prometheus), 4317/4318/8888 (Collector), 6006 (Phoenix), 8000 (Atlas).

## Offline note

Everything runs with `OFFLINE=1`: the mock LLM produces the traffic, and your own Langfuse and Phoenix receive real OTLP spans. No API keys. Only Step 6 needs GitHub. Use the swarm, not the replay, for traffic in this lab: `make replay` writes straight to the local store and never passes through the Collector or Prometheus.

---

## Step 1: Start self-hosted Langfuse

```bash
cp -n .env.example .env          # then fill the Langfuse self-host secrets the compose file asks for
make langfuse-up                 # docker compose -f deploy/docker-compose.langfuse.yml up -d
docker compose -f deploy/docker-compose.langfuse.yml ps
```

After one to three minutes (the first run pulls a few GB) six services are up: `langfuse-web` (port 3000), `langfuse-worker`, `postgres`, `clickhouse`, `redis` and `minio`. If `clickhouse` restarts in a loop, raise Docker's memory before anything else.

The compose file is a pinned copy of the upstream Langfuse self-host compose. If `up` fails on an unknown variable or service, compare with the current upstream file and the self-host docs (verify on the day you run this).

Open `http://localhost:3000`, create the first account (it becomes admin), an organisation and a project called `atlas-local`. **Settings → API keys → Create**: note the `pk-lf-...` and `sk-lf-...` values.

> **Checkpoint 1:** six healthy services and a Langfuse project with keys.

---

## Step 2: Point Atlas straight at it (sanity check)

Before adding the Collector, confirm the SDK path works against your instance. In `.env`:

```dotenv
OFFLINE=1
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
LANGFUSE_TRACING_ENVIRONMENT=local
LANGFUSE_RELEASE=lab7
```

Atlas doesn't load `.env` by itself, so export it into your shell, then run:

```bash
set -a; source .env; set +a
make run
```

Send the Lab 1 curl from another terminal. Within a few seconds the trace appears in **your** Langfuse (Tracing), with environment `local` and release `lab7`. Stop `make run` afterwards.

> **Checkpoint 2:** a trace in self-hosted Langfuse via the SDK.

---

## Step 3: Put the Collector in the middle

Read `deploy/otel-collector.yaml` (Lecture 13.2). In order: `memory_limiter`; `attributes/redact`, which **deletes** `gen_ai.tool.call.result`, the input and output message attributes, `gen_ai.system_instructions` and Langfuse's input and output fields, **hashes** `gen_ai.tool.call.arguments` (already masked at the source) and **deletes** `user.id` and `enduser.id` (the Collector's hash is unkeyed, so a hashed employee ID could be reversed; the SDK's keyed pseudonym is the joinable one); `tail_sampling` (keep errors, slow > 4 s, expensive > $0.05, ≥ 5 steps, escalated, and 20% of the rest); then `batch`. Exporters: `otlphttp/langfuse` (`${LANGFUSE_BASE_URL}/api/public/otel` with Basic auth), `otlphttp/phoenix` (the `phoenix` service), `debug`, and the `spanmetrics` connector.

Now move the Langfuse credentials from Atlas to the Collector. Edit `.env`: **blank** `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` (the stack's Atlas container reads `.env`, and with keys it would also export to Langfuse directly, doubling every trace). Then, in the shell that runs `make stack`:

```bash
export LANGFUSE_BASIC_AUTH=$(printf 'pk-lf-...:sk-lf-...' | base64 | tr -d '\n')
export LANGFUSE_BASE_URL=http://host.docker.internal:3000   # Langfuse runs in another compose project; verify this host name on your Docker
make stack
docker compose -f deploy/docker-compose.observability.yml logs otel-collector | tail -20
```

No `401` and no `connection refused` in the Collector log means it can reach Langfuse. The stack's Atlas container already exports OTLP to `http://otel-collector:4318/v1/traces`.

Drive some traffic and look at a tool span in both backends:

```bash
make swarm RPS=2 DURATION=120
```

1. Langfuse (`localhost:3000`) and Phoenix (`localhost:6006`) both show traces. Not every request: the tail sampler drops most healthy ones.
2. Open an `execute_tool lookup_ticket` span in Phoenix: there is **no** `gen_ai.tool.call.result` attribute, and `gen_ai.tool.call.arguments` is a hash string. That's the Collector's layer. Atlas's own SDK-side mask (`northwind.pii`) already replaced emails and `NW-` ids in the values before they left the process; the Collector deletes the content attributes outright as defence in depth.

> **Checkpoint 3:** traces flow Atlas → Collector → Langfuse and Phoenix; a tool span shows the Collector's deletions and hashes.

---

## Step 4: Tail sampling: keep the errors, drop the boring

Put the stack's Atlas into the `retry_storm` scenario (add `ATLAS_SCENARIO=retry_storm` to `.env`, then `docker compose -f deploy/docker-compose.observability.yml up -d atlas`) and run the swarm for two minutes:

```bash
make swarm RPS=2 DURATION=120
curl -s localhost:8000/metrics | grep '^atlas_requests_total' | awk '{s+=$2} END {print "served", s}'
```

Then count what reached Phoenix: in the Phoenix UI, filter the project's traces to the last few minutes, and separately to status error. Every trace with a timed-out (ERROR) generation is kept by the `errors` policy; healthy traces are kept at about 20%. Write down served, exported, and errors exported. Compare with head sampling at 20% (`TRACE_SAMPLE_RATE=0.2` in Atlas's own SDK), which keeps about a fifth of the errors too, because it decides before the trace finishes. That's why sampling moves to the Collector once you self-host.

Remove `ATLAS_SCENARIO` from `.env` and recreate the container when you're done.

> **Checkpoint 4:** you can show that error traces were kept while healthy traffic was sampled.

---

## Step 5: Kill the Collector (chaos, Lecture 13.5)

With the swarm running (`make swarm RPS=2 DURATION=600`), in a third terminal:

```bash
watch -n 2 "curl -s localhost:8000/metrics | grep -E '^atlas_requests_total|^atlas_telemetry_export_failures_total'"
docker compose -f deploy/docker-compose.observability.yml stop otel-collector
```

Check three things:

1. The swarm still gets 200s, and `atlas_requests_total` keeps climbing at the same rate.
2. `atlas_telemetry_export_failures_total{name="otlp"}` rises, and `docker compose -f deploy/docker-compose.observability.yml logs atlas` shows `telemetry exporter otlp failed (...); dropping spans`.
3. `curl -s localhost:8000/healthz` lists the `otlp` exporter with a growing `failures` count. Prometheus (`localhost:9091` → Alerts) fires `AtlasTelemetryExportFailures` (more than 20 failures in 10 minutes, a ticket, not a page).

Bring it back with `docker compose -f deploy/docker-compose.observability.yml start otel-collector`. New traces arrive within a minute; the ones dropped during the outage are gone, a visible gap in Phoenix's timeline.

Then see the anti-pattern once, offline and in seconds: `tests/integration/test_exporter_failure.py` pins the safe behaviour (`python -m pytest -q tests/integration/test_exporter_failure.py`, `3 passed`), and the ten-line script from Lecture 13.5 shows twenty spans taking 0.00 s with the batch processor and about four seconds with `batch=False` against a 200 ms exporter. There is no environment switch for the synchronous processor; `configure_tracing(batch=False)` is the only way in, which is the point.

> **Checkpoint 5:** Atlas served normally with the Collector down; you saw the failure counter, the log line and the health field.

---

## Step 6: The CI budget gate

`.github/workflows/ci.yml` has three jobs:

| Job | Runs when | What it does |
|---|---|---|
| `test` (unit + integration, offline) | every push and PR | lint, `pytest tests/unit`, `pytest tests/integration`, and a check that `incidents/generate.py` reproduces the datasets byte for byte |
| `budget-gate` | every push and PR, after `test` | `pytest tests/budget` with `BUDGET_COST_PER_SESSION_USD=0.05` and `BUDGET_P95_LATENCY_MS=4000`; the text console goes to the job summary |
| `live-evals` | pushes to `main` only, and only with secrets | the judge against live traffic, `LANGFUSE_RELEASE` set to the commit SHA |

Push your fork and open a pull request that changes something harmless. Both offline jobs go green. Locally the gate prints:

```text
cost/session $0.01454 (budget $0.05) total $4.36 over 300 sessions
p95 3822 ms (budget 4000 ms) over 781 requests
max input tokens/generation 17,992 (budget 24,000)
5 passed
```

Now make it fail on purpose, the way Incident 1's retrieval change would have. In the PR, add `ATLAS_TOP_K: "12"` to the `budget-gate` job's `env` block and push. Expected:

```text
FAILED tests/budget/test_budget_gate.py::test_p95_latency_within_budget - AssertionError: p95 4088 ms exceeds budget 4000 ms
FAILED tests/budget/test_budget_gate.py::test_max_input_tokens_per_generation - AssertionError: a generation sent 34,990 input tokens (> 24,000) ...
```

Cost per session rises to $0.0202 but stays under its $0.05 budget; p95 and the tokens test are what catch it. Revert, push, green again. Screenshot both runs. Locally:

```bash
ATLAS_TOP_K=12 make budget-check
```

> **Checkpoint 6:** a PR that regresses latency and prompt size is red; the revert is green.

---

## Step 7: Release tags in Langfuse

`LANGFUSE_RELEASE` becomes the release on every trace (and `service.version` on the OTel resource). Replay a small day to your Langfuse twice, with two releases (the replay writes through the Langfuse SDK, so put the keys back in your shell for this step):

```bash
set -a; source .env; set +a      # with LANGFUSE_PUBLIC_KEY / SECRET_KEY / BASE_URL=http://localhost:3000
LANGFUSE_RELEASE=lab7 make replay LANGFUSE=1 SESSIONS=200 STORE=.atlas/lab7-a.sqlite
LANGFUSE_RELEASE=lab7-topk12 ATLAS_TOP_K=12 make replay LANGFUSE=1 SESSIONS=200 STORE=.atlas/lab7-b.sqlite
```

In Langfuse, filter traces by release and compare cost per trace between the two (verify where your Langfuse version shows a release filter and cost aggregation). Offline, the Ops Console's **Compare replays** page shows the same comparison from the two stores.

> **Checkpoint 7:** two releases comparable side by side.

---

## Step 8: Notes

`notes/lab-07.md`:

```markdown
# Lab 7

- Langfuse compose: anything I had to change to match upstream:
- Screenshot: one trace in self-hosted Langfuse and in Phoenix, via the Collector
- Redaction: what the SDK mask changed, what the Collector deleted or hashed
- Tail sampling: served ___ requests, exported ___ traces, errors exported ___ of ___
- Collector outage: requests failed ___ (should be 0); export failures counted ___
- CI: link to the red run and the green run
- One item from the production checklist (13.4) my stack still lacks:
```

---

## Stretch goals

1. Scrape the Collector's own metrics (`otel-collector:8888`, already a Prometheus target) and add a Grafana panel for the exporter's failed spans; alert when it increases.
2. Write one paragraph for and against relying on the Collector alone for redaction (hint: the console and file exporters, and anything that bypasses the Collector, see whatever the SDK sends).
3. Add a `file` exporter to the Collector pipeline and diff one span before and after redaction.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `clickhouse` restarts in a loop | Low Docker memory | Raise to 6 GB or more |
| `langfuse-web` restarts | Missing secret | `docker compose -f deploy/docker-compose.langfuse.yml logs langfuse-web`; compare with the upstream self-host docs |
| Collector logs `401` | Keys from another project, or `LANGFUSE_BASIC_AUTH` not exported in the shell that ran `make stack` | Regenerate it from `atlas-local`'s keys and rerun `make stack` |
| Collector logs `connection refused` to Langfuse | Langfuse is in a different compose project; `localhost` inside a container is the container | Use a host-reachable URL for `LANGFUSE_BASE_URL` (Docker Desktop: `host.docker.internal`); verify on Linux |
| Every trace appears twice in Langfuse | Atlas still has Langfuse keys in `.env` and exports directly too | Blank them in `.env` and recreate the `atlas` container |
| Nothing in Phoenix or Langfuse after `make replay` | Expected: the replay doesn't use the Collector | Use `make swarm` against the stack |
| `make budget-check` passes with `ATLAS_TOP_K` set in `.env` | The gate doesn't read `.env` | Set it on the command line or in the CI job's `env` |

---

## Solution notes

Reference files: `03-code/deploy/docker-compose.langfuse.yml`, `03-code/deploy/docker-compose.observability.yml`, `03-code/deploy/otel-collector.yaml`, `03-code/deploy/prometheus.yml`, `03-code/deploy/alerts.yml`, `03-code/telemetry/otel_setup.py`, `03-code/tests/integration/test_exporter_failure.py`, `03-code/tests/budget/test_budget_gate.py`, `03-code/.github/workflows/ci.yml`.

Reference gate numbers (offline, deterministic): baseline `5 passed` (cost/session $0.01454, p95 3,822 ms, worst prompt 17,992 tokens); `ATLAS_TOP_K=12` 2 failed (p95 4,088 ms; 34,990 tokens; cost/session $0.0202, under budget). Swarm, sampling and outage counts depend on run length; grade the reasoning, not the exact numbers.

What a complete Lab 7 shows:

| Element | Evidence |
|---|---|
| Self-hosted Langfuse | trace with environment `local` and release `lab7` |
| Collector in the path | the same traces in Langfuse and Phoenix; no Langfuse keys in Atlas's env |
| Defence-in-depth masking | SDK-masked values in the local store, deleted and hashed attributes after the Collector |
| Tail sampling | errors kept, healthy traffic sampled, the head-sampling comparison |
| Backend chaos | every request served, failure counter and health field, the gap in the timeline |
| CI gate | red run on `ATLAS_TOP_K=12` with two named failures, green on revert |
| Releases | two releases comparable in Langfuse or on the Compare replays page |

Key takeaways:

1. Self-hosting buys control over data and retention; it costs you the operation of six containers. The decision matrix in Lecture 12.5 is not academic.
2. The Collector is where sampling and redaction policy live once you have more than one backend.
3. Telemetry must never be in the request path: drop spans, never requests, and alert on the dropping.
4. A budget gate turns "we should watch cost" into "this PR can't merge", and it catches latency and prompt size as well as cost.
