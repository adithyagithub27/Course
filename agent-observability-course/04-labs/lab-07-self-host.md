# Lab 7: Self-Hosted Stack End to End

| Field | Details |
|---|---|
| **Section / lecture** | Section 13, lecture 13.6 |
| **Time estimate** | 90 minutes (plus image pull time) |
| **Difficulty** | Advanced |
| **Goal** | Run the complete observability stack locally: self-hosted Langfuse, the OpenTelemetry Collector fanning traces out to Langfuse and to a file, Prometheus and Grafana from Lab 6, Atlas pointed at the collector, PII masked in the collector as well as the SDK, and the CI budget gate green in GitHub Actions. Then kill Langfuse and prove Atlas keeps serving. |
| **You will produce** | A running `deploy/` stack, a trace visible in your own Langfuse, a masked attribute proven in the collector's file export, a green CI run, and `notes/lab-07.md` |

---

## Prerequisites

- Labs 1 to 6 complete (Lab 6's compose stack in particular).
- Lectures 13.1 to 13.5 watched.
- Docker with at least 4 GB RAM allocated (Langfuse v3 runs Postgres, ClickHouse, Redis and MinIO alongside its web and worker containers).
- A GitHub fork of the course repo for the CI step (or skip Step 6 and run the gate locally).
- Ports free: 3000 (Langfuse), 3001 (Grafana), 4317/4318 (collector), 9090 (Prometheus), 8000 (Atlas).

## Offline note

Everything here runs with `OFFLINE=1`; the mock LLM produces the traffic, and self-hosted Langfuse receives real OTLP spans. No API keys needed. Only Step 6 needs a GitHub account.

---

## Step 1: Start self-hosted Langfuse

```bash
docker compose -f deploy/docker-compose.langfuse.yml up -d
docker compose -f deploy/docker-compose.langfuse.yml ps
```

Expected after one to two minutes (first run pulls about 2 GB of images):

```text
NAME                       STATUS                    PORTS
langfuse-web               Up (healthy)              0.0.0.0:3000->3000/tcp
langfuse-worker            Up (healthy)
langfuse-postgres          Up (healthy)
langfuse-clickhouse        Up (healthy)
langfuse-redis             Up (healthy)
langfuse-minio             Up (healthy)
```

The compose file in `deploy/` is a pinned copy of the upstream Langfuse compose. **Version drift warning (lecture 13.1):** if `docker compose up` fails on an unknown environment variable or a missing service, compare with the current upstream file at `https://github.com/langfuse/langfuse/blob/main/docker-compose.yml` and update ours; Langfuse adds required secrets from time to time (`ENCRYPTION_KEY`, `SALT`, `NEXTAUTH_SECRET`, ClickHouse and MinIO credentials are all set in our file).

Open `http://localhost:3000`, create the first account, then a project called `atlas-local`. **Settings → API keys → Create**: note `pk-lf-...` and `sk-lf-...`.

> **Checkpoint 1:** six healthy containers and a Langfuse project with keys.

---

## Step 2: Point Atlas straight at it (sanity check)

Before adding the collector, confirm the SDK path works against your instance:

```dotenv
# .env
OFFLINE=1
OTEL_EXPORTER=langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
LANGFUSE_TRACING_ENVIRONMENT=local
LANGFUSE_RELEASE=lab7
```

```bash
make run
```

Send the Lab 1 curl. Within a few seconds the trace appears in **your** Langfuse at `http://localhost:3000` → Tracing, with environment `local` and release `lab7`.

> **Checkpoint 2:** a trace in self-hosted Langfuse via the SDK exporter.

---

## Step 3: Put the OTel Collector in the middle

Now switch Atlas to plain OTLP and let the collector decide where spans go. Open `deploy/otel-collector.yaml`:

```yaml
receivers:
  otlp:
    protocols:
      http: { endpoint: 0.0.0.0:4318 }
      grpc: { endpoint: 0.0.0.0:4317 }

processors:
  memory_limiter: { check_interval: 1s, limit_mib: 400 }
  batch: { timeout: 2s, send_batch_size: 512 }
  attributes/redact:
    actions:
      - key: user.email
        action: delete
      - key: northwind.user_id_raw
        action: hash            # SHA-256; keeps joins, drops identity
      - key: gen_ai.tool.call.result
        action: update
        # collector-side regex redaction (defence in depth; SDK masks first)
        # pattern replaces NW-123456 style ids
        from_attribute: gen_ai.tool.call.result
  transform/redact:
    trace_statements:
      - context: span
        statements:
          - replace_pattern(attributes["gen_ai.tool.call.result"], "NW-\\d{5}", "[EMPLOYEE_ID]")
          - replace_pattern(attributes["gen_ai.tool.call.arguments"], "NW-\\d{5}", "[EMPLOYEE_ID]")
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: keep-errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: keep-slow
        type: latency
        latency: { threshold_ms: 4000 }
      - name: keep-some
        type: probabilistic
        probabilistic: { sampling_percentage: 20 }

exporters:
  otlphttp/langfuse:
    endpoint: http://langfuse-web:3000/api/public/otel
    headers:
      Authorization: "Basic ${env:LANGFUSE_BASIC_AUTH}"    # base64(pk-lf-...:sk-lf-...)
  file/debug:
    path: /var/otel/spans.jsonl
  debug:
    verbosity: basic

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, attributes/redact, transform/redact, tail_sampling, batch]
      exporters: [otlphttp/langfuse, file/debug]
```

Note that the Langfuse OTLP endpoint is `/api/public/otel` (the collector appends `/v1/traces`), and it authenticates with HTTP Basic auth built from the public and secret key. Create the header value and restart the collector:

```bash
export LANGFUSE_BASIC_AUTH=$(printf 'pk-lf-...:sk-lf-...' | base64 -w0)
docker compose -f deploy/docker-compose.observability.yml up -d --force-recreate atlas-otel-collector
docker compose -f deploy/docker-compose.observability.yml logs -f atlas-otel-collector | head -20
```

Expected log lines: `Everything is ready. Begin running and processing data.` and no `authentication failed`.

Then switch Atlas:

```dotenv
OTEL_EXPORTER=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

Restart `make run`, send the shipment question from Lab 2 (it has a consignee email in the tool result), and confirm:

1. The trace appears in Langfuse (via the collector this time; the `service.name=atlas` resource attribute is preserved).
2. The file export has it too:

```bash
docker compose -f deploy/docker-compose.observability.yml exec atlas-otel-collector \
  sh -c 'tail -c 20000 /var/otel/spans.jsonl' | grep -o '"gen_ai.tool.call.result"[^}]*' | head -1
```

Expected: the result string contains `[EMAIL]` (masked by the SDK in `northwind.pii` before export) and `[EMPLOYEE_ID]` if any id was present (masked by the SDK **and** the collector). To prove the collector's layer works on its own, temporarily set `ATLAS_MASK=0` (SDK masking off), send the request again, and check the file: `NW-` ids must still be gone, emails will now be raw. Turn `ATLAS_MASK=1` back on. Write down what each layer caught.

> **Checkpoint 3:** traces flow Atlas → collector → Langfuse and file; the collector redacts employee ids even with SDK masking off.

---

## Step 4: Tail sampling: keep the errors, drop the boring

Run the swarm with the retry storm for two minutes:

```bash
OFFLINE=1 ATLAS_SCENARIO=retry_storm make run
OFFLINE=1 uv run python -m simulator.swarm --rps 2 --minutes 2 --seed 42
```

Count what the collector kept:

```bash
docker compose -f deploy/docker-compose.observability.yml exec atlas-otel-collector \
  sh -c 'grep -c "\"name\":\"atlas.chat\"" /var/otel/spans.jsonl'
```

And what Atlas sent:

```bash
curl -s http://localhost:8000/metrics | grep 'atlas_requests_total' | awk -F' ' '{s+=$2} END {print s}'
```

Expected: Atlas served about 240 requests; the collector exported roughly 110 to 130 `atlas.chat` root spans: **all** of the ~70 error traces (retry storm), all of the slow ones, and 20% of the healthy rest. Compare with head sampling at 20% (`TRACE_SAMPLE_RATE=0.2` in Atlas's own SDK): you would keep ~48 traces and, on average, only 14 of the 70 errors. That is why sampling moves to the collector once you self-host (lecture 13.2): the collector sees the whole trace before deciding.

> **Checkpoint 4:** you can show that error traces were kept at 100% while healthy traffic was sampled.

---

## Step 5: Kill the backend (chaos, lecture 13.5)

With Atlas serving traffic through the collector:

```bash
docker compose -f deploy/docker-compose.langfuse.yml stop langfuse-web langfuse-worker
```

Keep the swarm running. Check three things:

1. Atlas still answers: `curl` the Lab 1 request; you get a normal response in normal time.
2. Atlas's p95 did not move: Grafana p95 panel flat. The SDK's `BatchSpanProcessor` exports asynchronously with a bounded queue (`max_queue_size=2048`, `export_timeout_millis=30000` in `telemetry/otel_setup.py`), so a dead backend costs the request path nothing; when the queue is full, spans are **dropped**, not requests.
3. The collector is buffering and retrying: its logs show `Exporting failed. Will retry the request after interval.` with the `sending_queue`/`retry_on_failure` settings from the exporter block. Once the queue (default 1,000 batches) fills, the collector also drops.

Bring Langfuse back:

```bash
docker compose -f deploy/docker-compose.langfuse.yml start langfuse-web langfuse-worker
```

Traces from the outage window reappear in Langfuse after a minute (the collector's queue drains); traces beyond the queue capacity are gone for good. Record how many minutes of outage your queue covered at 2 RPS (about 8 minutes with defaults). In production you size the queue for your longest tolerable backend outage and alert on `otelcol_exporter_send_failed_spans`.

Now the wrong way: set `OTEL_EXPORTER=otlp` with `OTEL_BSP_EXPORT_TIMEOUT=60000` and `OTEL_BSP_MAX_QUEUE_SIZE=64` in Atlas, use a `SimpleSpanProcessor` (there is a flag `ATLAS_SYNC_EXPORT=1` for this demo), stop the collector, and send a request. It takes a minute to answer. That is what "telemetry in the request path" looks like, and it is the reason the production checklist (lecture 13.4) has "exporter back-pressure" as its own line.

> **Checkpoint 5:** Atlas served normally with Langfuse down; you know how long the queue lasted; you saw the synchronous anti-pattern once.

---

## Step 6: The CI budget gate

`.github/workflows/ci.yml` has three jobs:

| Job | Runs when | What it does |
|---|---|---|
| `unit-integration` | always | `make test` offline |
| `budget-gate` | always | `OFFLINE=1 make replay && make budget-check`: replays the day and fails if cost per session > `$0.05` or p95 > 4,000 ms or error rate > 2% |
| `live-evals` | only when `OPENAI_API_KEY` and Langfuse secrets exist | 50 real requests, judge sample, `create_score`s tagged with the commit SHA as `release` |

Push your fork and open a pull request that changes something harmless (a README line). Expected checks:

```text
✓ unit-integration    2m 10s
✓ budget-gate         1m 42s   cost/session $0.0421 (budget 0.05)  p95 2,140 ms (budget 4,000)
○ live-evals          skipped (no secrets)
```

Now make it fail on purpose. In the PR, set `ATLAS_TOP_K=12` in `.env.example` (the retrieval change from Incident 2; more chunks per prompt). Push. Expected:

```text
✗ budget-gate   FAILED tests/budget/test_budget_gate.py::test_cost_per_session_within_budget
    AssertionError: cost per session 0.0587 exceeds budget 0.05 (+17.4%)
```

The gate wrote a comment on the PR with the before/after table (via `tests/budget/report.py`). Revert the change, push, gate green again. Screenshot both runs.

Locally the same thing is:

```bash
OFFLINE=1 ATLAS_TOP_K=12 make replay && make budget-check
```

> **Checkpoint 6:** a PR that regresses cost is blocked; the revert passes.

---

## Step 7: Release tags in Langfuse

The CI `live-evals` job (and, offline, the replay) sets `LANGFUSE_RELEASE=$GITHUB_SHA`. In your local Langfuse, filter **Traces → release = lab7**, then run one replay with `LANGFUSE_RELEASE=lab7-topk12 ATLAS_TOP_K=12` and compare the two releases' mean cost in the Langfuse dashboard (**Dashboards → Cost by release**). The Grafana annotation from Lab 6 does the same on the metrics side. Both together mean every regression has a release boundary to point at.

> **Checkpoint 7:** two releases visible side by side in Langfuse with different cost.

---

## Step 8: Notes

`notes/lab-07.md`:

```markdown
# Lab 7

- Langfuse compose version used / any drift fixes needed:
- Screenshot: trace via collector in self-hosted Langfuse
- Redaction: what the SDK caught / what the collector caught (ATLAS_MASK=0 experiment)
- Tail sampling: served ___ requests, exported ___ traces, errors kept ___/___ 
- Backend outage: minutes covered by the queue at 2 RPS: ___; p95 during outage: ___
- CI: link to the red run and the green run
- One thing from the production checklist (13.4) my stack still lacks:
```

---

## Stretch goal

1. Add a second exporter to the collector pipeline (`otlphttp/phoenix` pointed at Arize Phoenix on `http://localhost:6006/v1/traces`, from the `phoenix` extra) and confirm the same trace appears in Langfuse and Phoenix. That is lecture 12.3 in practice.
2. Enable the collector's own metrics (`service.telemetry.metrics`) and scrape them with Prometheus; add a panel for `otelcol_exporter_send_failed_spans` and an alert when it increases.
3. Move the SDK's `mask` function out of the code path and rely on the collector alone, then write the argument for and against in one paragraph (hint: the debug exporter, local files and any exporter that bypasses the collector will see raw data).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `langfuse-web` restarts in a loop | Missing required secret or ClickHouse not ready | `docker compose logs langfuse-web`; compare env with the upstream compose; wait for `clickhouse` healthy |
| Langfuse UI loads but traces never appear via collector | Wrong endpoint path or auth | Endpoint is `/api/public/otel` (no `/v1/traces` suffix in `otlphttp` `endpoint`); header is `Basic base64(pk:sk)` |
| Collector logs `401` | Keys from a different project | Regenerate `LANGFUSE_BASIC_AUTH` from the `atlas-local` project's keys |
| Collector logs `connection refused` to `langfuse-web` | Collector and Langfuse on different Docker networks | Both compose files join the `atlas-net` external network; `docker network create atlas-net` if missing |
| `replace_pattern` errors on startup | Older collector-contrib without the transform processor syntax | Use image tag `>= 0.100.0`; or fall back to the `redaction` processor |
| Tail sampling keeps everything | `decision_wait` shorter than trace duration | Raise to 10 s; a trace that is still open when the decision is made is treated as complete with what has arrived |
| Atlas hangs when the collector is down | Synchronous export or huge timeout | Use `BatchSpanProcessor`, default timeouts; `ATLAS_SYNC_EXPORT` must be `0` |
| CI budget gate flaky | Non-deterministic seed | The gate replays with `--seed 42`; check nothing overrides `ATLAS_SCENARIO` in the CI env |
| PR comment missing | Workflow lacks `pull-requests: write` permission | Add it under `permissions:` in `ci.yml` |

---

## Solution notes

Reference files: `03-code/deploy/docker-compose.langfuse.yml`, `03-code/deploy/docker-compose.observability.yml`, `03-code/deploy/otel-collector.yaml`, `03-code/telemetry/otel_setup.py`, `03-code/tests/budget/test_budget_gate.py`, `03-code/.github/workflows/ci.yml`.

Reference numbers (seed 42, 2 RPS for 2 minutes with `retry_storm`): 240 served, 118 root spans exported, 71/71 error traces kept, 34/169 healthy kept (20%); head sampling at 20% would have kept ~14 errors. Backend outage coverage with default queues at 2 RPS: about 8 minutes before the collector drops; Atlas p95 unchanged (2,150 ms vs 2,140 ms baseline). CI red run: cost per session $0.0587 with `ATLAS_TOP_K=12` (+17%).

What a complete Lab 7 shows:

| Element | Evidence |
|---|---|
| Self-hosted Langfuse | Trace visible with environment `local`, release `lab7` |
| Collector in the path | Same trace via OTLP, `service.name` preserved, file export has it |
| Defence-in-depth masking | `ATLAS_MASK=0` experiment: collector still removed employee ids; SDK is the primary control because it also covers exporters that bypass the collector |
| Tail sampling | Errors kept at 100%, healthy at 20%, and the head-sampling comparison |
| Backend chaos | Atlas served, p95 flat, queue coverage measured, sync anti-pattern seen once |
| CI gate | Red run on `ATLAS_TOP_K=12`, green on revert, PR comment with the table |
| Releases | Two releases comparable in Langfuse and annotated in Grafana |

Key takeaways:

1. Self-hosting buys control over data and retention; it costs you the operations of six containers. The decision matrix in lecture 12.5 is not academic.
2. The collector is where portability, sampling and redaction policy live once you have more than one backend, or one you do not fully trust.
3. Telemetry must never be in the request path. Drop spans, never requests, and alert on the dropping.
4. A budget gate in CI turns "we should watch cost" into "this PR cannot merge". It is the cheapest incident prevention in the course.
