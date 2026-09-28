# Section 13: Deploying the Stack and CI Budget Gates

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈40 min (6 lectures, curriculum v1.0)
> **Source of truth:** `01-curriculum/curriculum.md`; checklist `10-resources/production-checklist.md`; lab `04-labs/lab-07-self-host.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Verification note:** The Langfuse self-host compose file (services, env vars, ports) and every Grafana and OTel Collector detail below must be checked against the **current** upstream docs before recording. Say "verify against current docs" on screen wherever the cue says so. OTel SDK exporter and processor arguments (`OTLPSpanExporter(timeout=)`, `BatchSpanProcessor(max_queue_size=, schedule_delay_millis=, max_export_batch_size=, export_timeout_millis=)`) and Langfuse client arguments (`flush_at`, `flush_interval`, `timeout`, `release`, `environment`) were checked on the installed packages on 2026-09-28.

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with Atlas, Docker or a dashboard. Record the real screen. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only, not cues, code, tables or slide text.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 13.1 | Self-hosting Langfuse with Docker Compose | SC | 9:00 | ~659 |
| 13.2 | OTel Collector as the traffic cop | SC | 7:00 | ~618 |
| 13.3 | Code-along: the CI budget gate | SC | 9:00 | ~800 |
| 13.4 | Production readiness checklist for observability | SL | 6:00 | ~614 |
| 13.5 | Chaos demo: kill the observability backend | DM | 5:00 | ~598 |
| 13.6 | Lab 7: Self-hosted stack end to end | LAB | 4:00 | ~362 |

**Names used in this section (match `03-code/`).** Deploy files: `deploy/docker-compose.langfuse.yml`, `deploy/docker-compose.observability.yml`, `deploy/otel-collector.yaml`, `deploy/prometheus.yml`, `deploy/alerts.yml`, `deploy/grafana/dashboards/atlas-ops.json`, `deploy/grafana/provisioning/`, `deploy/Dockerfile`. Budget gate: `tests/budget/test_budget_gate.py` with `test_cost_per_session_within_budget`, `test_p95_latency_within_budget`, `test_no_tenant_over_its_daily_soft_cap`, `test_task_success_slo_holds`; budgets from `Settings`: `budget_cost_per_session_usd` [`BUDGET_COST_PER_SESSION_USD`, 0.05], `budget_p95_latency_ms` [`BUDGET_P95_LATENCY_MS`, 4000], `tenant_soft_cap_usd` [`TENANT_SOFT_CAP_USD`, 25]; gate knobs `BUDGET_GATE_SESSIONS` (300), `BUDGET_GATE_INCIDENTS` (`none`), `BUDGET_GATE_SEED` (7). Simulator: `simulator/scenarios.py::generate_day(seed, sessions=, incidents=)`, `INCIDENT_PRESETS`; `simulator/replay.py::replay_day(seed, sessions=, incidents=, store=, judge_rate=, settings=) -> (ReplaySummary, LocalSpanStore)`. Telemetry: `telemetry/otel_setup.py::configure_tracing`, `SafeSpanExporter`, `FailingSpanExporter`, `exporter_health()`, `shutdown_tracing(timeout_ms=)`; `telemetry/metrics.py::EXPORTER_FAILURES` (`atlas_telemetry_export_failures_total{name}`). `.github/workflows/ci.yml` jobs: `test`, `budget-gate`, `live-evals`. Makefile targets: `make budget-check`, `make langfuse-up` / `make langfuse-down`, `make stack` / `make stack-down`, `make swarm RPS=`. Langfuse env: `LANGFUSE_BASE_URL=http://localhost:3000`, `LANGFUSE_RELEASE`.

---

## Lecture 13.1 — Self-hosting Langfuse with Docker Compose

| Field | Value |
|---|---|
| ID | 13.1 |
| Type | SC (screencast / code-along) |
| Target duration | 9:00 (~660 spoken words; the rest is Docker, UI and demo time) |
| Learning objectives | 1. Start a self-hosted Langfuse with Docker Compose, understand what each container does, and create the first organisation, project and API keys. 2. Point Atlas at the local instance and confirm a trace arrives. 3. Know the four settings that separate a laptop demo from a production self-host: secrets, persistence, backups and upgrades. |
| Prerequisites | Sections 2 and 4; Docker Desktop or Docker Engine with Compose |
| Files used | `deploy/docker-compose.langfuse.yml`, `.env.example`, `telemetry/langfuse_setup.py`, `Makefile` |

### Script

[B-ROLL: Terminal, `docker compose ps`, six containers all "healthy". Browser: `localhost:3000`, Langfuse login page.]

[AVATAR]
Six containers, one command, and every trace Atlas produces stays on hardware you control. Since Section 2 you've used Langfuse Cloud, which is the right way to start. This lecture is for the day your security team asks where the data goes, or your bill asks the same question.

Self-hosting Langfuse is a Compose file. But a Compose file that works on your laptop and one you can run for a company are different things, and I'll show you both.

[SLIDE 1: What is in the box]
- `langfuse-web`: the UI and public API, port 3000
- `langfuse-worker`: async ingestion and processing
- `postgres`: metadata, users, projects, prompts
- `clickhouse`: traces, observations and scores at scale
- `redis`: queues and cache
- `minio` (S3-compatible): event and media storage
- Verify against the current Langfuse self-host compose

Six services. The web container serves the UI and the API you've been calling. A worker processes ingestion asynchronously, which is why traces appear a few seconds after you send them. Postgres holds metadata: users, projects, prompts and labels. ClickHouse holds the big tables: traces, observations and scores. Redis is queues and cache. And an S3-compatible store, MinIO in the local compose, holds raw events and media.

Verify this list against the current Langfuse self-host compose file. The architecture moved to ClickHouse in version three, and the exact services and env vars can change between releases.

[SCREEN: `deploy/docker-compose.langfuse.yml` in VS Code. Footer visible. Scroll to the `langfuse-web` service.]

[CODE: the web service, abbreviated]
```yaml
services:
  langfuse-web:
    image: langfuse/langfuse:3          # verify tag against current docs
    ports: ["3000:3000"]
    depends_on: [postgres, clickhouse, redis, minio]
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/postgres
      NEXTAUTH_URL: http://localhost:3000
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      SALT: ${SALT}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}   # 64 hex chars
      CLICKHOUSE_URL: http://clickhouse:8123
      CLICKHOUSE_USER: clickhouse
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD}
      REDIS_HOST: redis
      LANGFUSE_S3_EVENT_UPLOAD_BUCKET: langfuse
      LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT: http://minio:9000
      # ... verify the full list against the current self-host docs
```

Look at the environment block, because this is where laptop and production diverge. `NEXTAUTH_SECRET`, `SALT` and `ENCRYPTION_KEY` are secrets Langfuse uses to sign sessions, hash API keys and encrypt stored keys. In the course repo they come from `.env`, and `.env.example` shows you how to generate them: `openssl rand -hex 32` for each, sixty-four hex characters for the encryption key. Never commit the real values, and never reuse the example ones.

[SCREEN: Terminal.]

[CODE: bring it up]
```bash
cp .env.example .env            # then fill the LANGFUSE_* and secret values
make langfuse-up                # docker compose -f deploy/docker-compose.langfuse.yml up -d
docker compose -f deploy/docker-compose.langfuse.yml ps
```

Copy the env example, fill the secrets, and `make langfuse-up`. First start pulls images and runs migrations, so give it two to three minutes. `ps` should show every service healthy. If ClickHouse is restarting, it's almost always memory: it wants a few gigabytes. Check Docker's resource limit before you check anything else.

[DEMO: Browser, `localhost:3000`. Sign up the first user. Create organisation "Northwind", project "atlas-dev". Settings → API keys → create. Copy public and secret keys into `.env` as `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and set `LANGFUSE_BASE_URL=http://localhost:3000`.]

Open port three thousand. Sign up; the first user becomes the admin. Create an organisation, Northwind, and a project, `atlas-dev`. Generate API keys. Now the only change on Atlas's side is three lines of env: public key, secret key, and the base URL, which is now localhost instead of the cloud.

[CODE: `telemetry/langfuse_setup.py::init_langfuse`, unchanged]
```python
_CLIENT = Langfuse(
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
    base_url=settings.langfuse_base_url,          # http://localhost:3000 now
    environment=settings.langfuse_environment,
    release=settings.langfuse_release,
    mask=langfuse_mask,
    ...
)
```

`langfuse_setup.py` doesn't change at all. It reads the base URL from settings. That's the portability point from Section 12 in miniature: the same SDK, a different address.

[SCREEN: `make run`, curl the VPN question, switch to the local Langfuse. Trace appears after a few seconds.]

Run Atlas, one question, and there's the trace in your own Langfuse. Agent span, retriever, generation with cost, tool. Same screen as Lecture 2.3, on your own disk.

Now the part that separates a demo from a deployment.

[SLIDE 2: Laptop versus production]
| Setting | Laptop | Production |
|---|---|---|
| Secrets | `.env` file | secret manager or CI secrets, rotated; never in the repo |
| Persistence | Docker volumes | named volumes on durable disks; ClickHouse and Postgres sized |
| Backups | none | Postgres dumps and ClickHouse backups on a schedule, restore tested |
| Upgrades | `pull` and `up` | read release notes, back up, upgrade web and worker together |
| TLS and auth | http, localhost | reverse proxy with TLS, SSO if available, `NEXTAUTH_URL` set to the real domain |
| Resources | whatever Docker has | ClickHouse memory and disk monitored; it is the component that grows |

Secrets. In production they come from a secret manager or CI secrets, and they rotate. Persistence. Named volumes on disks you'd trust with a database. Backups. Postgres and ClickHouse, scheduled, and you've tested a restore, because an untested backup is a hope. Upgrades. Read the release notes, back up, then upgrade web and worker together so migrations match. TLS and auth. A reverse proxy in front with a real certificate, and set `NEXTAUTH_URL` to the real domain or logins break. And resources. ClickHouse is the component that grows, so monitor its disk and memory. Retention, from Lecture 10.3, is what keeps it bounded.

[SLIDE 3: When to self-host]
- You must: data residency or no-egress rules
- You want: cost control at high volume, full retention control
- You should not: no one owns the database at 2 a.m.; then use Cloud with masking
- Middle path: Cloud for dev, self-host for prod, same SDK, different `LANGFUSE_BASE_URL`

When should you self-host? When you must, because of residency or egress rules. When volume makes it cheaper and you want full retention control. And not when nobody on your team can own Postgres and ClickHouse in the middle of the night. There's a middle path: Cloud for development, self-hosted for production. Same SDK, different base URL, which is exactly what you just did.

[AVATAR]
Your Langfuse is up. Next, we put a traffic cop in front of it, so Atlas never talks to a backend directly again.

**Recap:** Self-hosted Langfuse is six containers behind one Compose file; Atlas only changes its base URL; and production means secrets, persistence, backups, upgrades and TLS handled deliberately, with ClickHouse as the component to watch.

**Transition:** Next, the OpenTelemetry Collector: receivers, processors and exporters that mask, sample and fan out to two backends at once.

### Speaker notes: common student mistakes / Q&A

- Verify before recording: image tags, service names, required env vars and the S3/MinIO settings in the current Langfuse self-host docs. The compose in `deploy/` must match; update the script if service names differ.
- Most common failure: ClickHouse restart loop from low Docker memory. Second: `NEXTAUTH_URL` mismatch causing login redirects to fail.
- "Can I skip MinIO?" Not in v3+; event storage needs an S3-compatible bucket. Verify current docs.
- "Postgres-only mode?" Older Langfuse v2 was Postgres-only; v3+ requires ClickHouse. Say so if asked, and point to the migration docs.

---

## Lecture 13.2 — OTel Collector as the traffic cop

| Field | Value |
|---|---|
| ID | 13.2 |
| Type | SC (screencast / code-along) |
| Target duration | 7:00 (~620 spoken words) |
| Learning objectives | 1. Read a Collector config as a pipeline: receivers, processors, exporters. 2. Configure attribute masking and tail sampling once, for every backend. 3. Export the same spans to Langfuse and a second backend at the same time. |
| Prerequisites | 13.1; Lectures 3.2, 4.6, 10.2, 12.1 |
| Files used | `deploy/otel-collector.yaml`, `deploy/docker-compose.observability.yml`, `telemetry/otel_setup.py` |

### Script

[B-ROLL: Animated diagram. Atlas box on the left emits arrows. Without a Collector: three arrows to three backends, each labelled "mask? sample? retry?". With a Collector: one arrow into a box, three arrows out, the box labelled "mask, sample, batch, retry: once".]

[AVATAR]
Without a Collector, every backend you add means another exporter in Atlas, another place to mask, another place to sample, another thing that can slow down a request when the network is bad. With a Collector, Atlas has one exporter, forever, and everything else is configuration you can change without a deploy.

The OpenTelemetry Collector is a separate process. It receives telemetry, runs it through processors, and exports it. That's the whole mental model: receivers, processors, exporters, wired into pipelines.

[SCREEN: `deploy/otel-collector.yaml` in VS Code. Footer: "verify against current OTel Collector contrib docs".]

[CODE: receivers and the first processors]
```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  batch:
    send_batch_size: 512
    timeout: 2s
  attributes/mask:
    actions:
      - key: gen_ai.tool.call.result
        action: hash          # keep a join key, drop the content
      - key: user.id
        action: hash
      - key: user.email
        action: delete
```

Receivers first. One OTLP receiver, listening on the two standard ports: four three one eight for HTTP, four three one seven for gRPC. Atlas sends HTTP.

Processors. `memory_limiter` goes first in every pipeline; it drops data rather than letting the Collector die. `batch` groups spans for efficient export. And `attributes/mask`: this is Lecture 10.2's second layer. Hash the tool result so you keep a join key without the content. Hash the user id. Delete email outright. The SDK-side `mask=` function from Lecture 4.6 still runs; this is the layer that catches whatever the SDK missed, and it applies to every backend at once.

[CODE: tail sampling]
```yaml
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: keep-errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: keep-slow
        type: latency
        latency: {threshold_ms: 4000}
      - name: keep-expensive
        type: numeric_attribute
        numeric_attribute: {key: atlas.cost_usd, min_value: 0.05}
      - name: sample-the-rest
        type: probabilistic
        probabilistic: {sampling_percentage: 20}
```

Tail sampling. The Collector waits ten seconds for a trace to complete, then decides whether to keep it. Keep every trace with an error. Keep every trace slower than four seconds, which is our latency budget. Keep every trace that cost more than five cents, because those are the ones Incident 1 taught you to look at. And keep twenty percent of everything else. Four policies, and any match keeps the trace.

Compare that with head sampling in the SDK from Lecture 4.6, where you decide at the start of a trace, before you know if it will be slow or fail. Tail sampling is why you can drop eighty percent of normal traffic and still have every incident trace.

[CODE: exporters and pipelines]
```yaml
exporters:
  otlphttp/langfuse:
    endpoint: ${LANGFUSE_OTLP_ENDPOINT}     # e.g. http://langfuse-web:3000/api/public/otel
    headers:
      Authorization: "Basic ${LANGFUSE_BASIC_AUTH}"   # base64(public_key:secret_key)
  otlphttp/phoenix:
    endpoint: http://phoenix:6006
  debug:
    verbosity: basic

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, attributes/mask, tail_sampling, batch]
      exporters: [otlphttp/langfuse, otlphttp/phoenix]
```

Exporters. Two `otlphttp` exporters with different names, one to Langfuse's OTLP endpoint, one to Phoenix. Langfuse's endpoint takes basic auth built from your public and secret keys, base64 encoded, and verify the exact path against the current docs. A `debug` exporter for troubleshooting, not for pipelines in production.

And the pipeline. Receivers, processors in order, memory limiter first and batch last, then both exporters. Every span goes to both. That is the escape hatch from Lecture 12.1 in eleven lines.

[SCREEN: `deploy/docker-compose.observability.yml`, the collector service, then `make stack`.]

[CODE: Atlas points at the Collector now]
```bash
OTEL_EXPORTER=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

The observability compose file brings up the Collector, Prometheus and Grafana together. Atlas's exporter becomes plain OTLP to the Collector on four three one eight, and the Langfuse keys come *out* of Atlas's environment, because the Collector holds them now. Atlas no longer knows any backend secret. That's a security win on its own.

[DEMO: `make replay` for ten seconds. Watch `docker compose logs otel-collector` show batches exported to both. Open local Langfuse and Phoenix; both show the same traces. Open one tool span in Langfuse: `gen_ai.tool.call.result` is a hash.]

Replay traffic. The Collector logs show batches going out to both exporters. Langfuse and Phoenix both have the traces. Open a tool span: the result is a hash, not the payload. Masked once, delivered twice.

[SLIDE 1: Collector rules]
- `memory_limiter` first, `batch` last, in every pipeline
- Mask in the Collector as the second layer; the SDK `mask=` stays as the first
- Tail sample on error, latency and cost; probabilistic for the rest
- Credentials live in the Collector, not in Atlas
- One exporter per backend; add or remove without touching Atlas

Five rules. Memory limiter first, batch last. Mask in the Collector as the second layer, never the only one. Tail sample on error, latency and cost. Credentials in the Collector. And one exporter per backend, added or removed with no change to Atlas.

[AVATAR]
Two containers ago, Atlas talked to a vendor directly. Now it talks to a process you own, which masks, samples and fans out on your terms. Next, the thing that stops regressions from ever reaching this stack: a CI gate on cost and latency.

**Recap:** The Collector is receivers, processors and exporters in a pipeline; put masking and tail sampling there once, keep credentials there, and export to as many backends as you like without changing Atlas.

**Transition:** Next, the CI budget gate: a test that replays a day of traffic and fails the pull request when cost per session or p95 move.

### Speaker notes: common student mistakes / Q&A

- `tail_sampling`, `attributes` and `otlphttp` live in the Collector **contrib** distribution; the core image lacks some of them. The compose must use the contrib image. Verify names and fields against current docs; the `numeric_attribute` policy and `hash` action have been stable but confirm.
- Langfuse OTLP endpoint path and auth header format: verify against current Langfuse OpenTelemetry docs.
- Mistake: putting `batch` before `tail_sampling`. Tail sampling needs complete traces; batch after.
- `decision_wait` must exceed your longest trace, or late spans are orphaned. Ten seconds is fine for Atlas; long agent runs need more.

---

## Lecture 13.3 — Code-along: the CI budget gate

| Field | Value |
|---|---|
| ID | 13.3 |
| Type | SC (screencast / code-along) |
| Target duration | 9:00 (~800 spoken words; the rest is screen and CI time) |
| Learning objectives | 1. Write a budget gate test that replays a deterministic day offline and asserts cost per session, p95 latency and tokens per generation against budgets in `Settings`. 2. Wire it into GitHub Actions so it runs on every pull request without API keys. 3. Tag releases in Langfuse so a regression that reaches production is attributable to a commit. |
| Prerequisites | Sections 6, 7 and 11; Lecture 2.4 (offline replay) |
| Files used | `tests/budget/test_budget_gate.py`, `simulator/scenarios.py`, `simulator/replay.py`, `src/northwind/config.py`, `src/northwind/cost.py`, `src/northwind/latency.py`, `.github/workflows/ci.yml`, `telemetry/langfuse_setup.py` |

### Script

[B-ROLL: A GitHub pull request. Title: "KB retrieval tuning: ATLAS_TOP_K 4 → 20". A red check: "budget-gate: FAILED. p95 4,310 ms > 4,000 ms budget." Elapsed: 3m 41s.]

[AVATAR]
This is the pull request that caused Incident 2, if the budget gate had existed. Red, in under four minutes, before lunch, before anyone outside the knowledge base team knew it was proposed. That's the whole lecture. Everything else is how.

The idea is simple because you've built every piece. The mock LLM from Lecture 2.4 produces realistic token counts and latencies without a network call. `generate_day` from the simulator plans a full day of traffic, deterministically. The cost and latency modules from Sections 6 and 7 aggregate the results. All the gate does is assert on those numbers.

[SCREEN: `src/northwind/config.py`, the budget fields, and `.env.example`. Footer visible.]

[CODE: budgets in `Settings`]
```python
# src/northwind/config.py  (env: BUDGET_COST_PER_SESSION_USD, BUDGET_P95_LATENCY_MS)
budget_cost_per_session_usd: float = 0.05    # baseline day: about $0.006; headroom for legitimate growth
budget_p95_latency_ms: float = 4000.0        # the latency SLO from Lecture 7.1

# tests/budget/test_budget_gate.py
MAX_INPUT_TOKENS_PER_GENERATION = 8000       # system prompt + 4 snippets + history_token_budget (3000) + tool result (400), with headroom
REPLAY_SEED = 7
```

Budgets live in `Settings`, with a comment on where each number came from. Five cents per session, when the baseline day costs about six tenths of a cent; that's generous headroom while the product is young, and you tighten it as you learn. Four seconds p95, which is the SLO. And two more assertions in the same file: no tenant over its daily soft cap, and the task-success SLO holding on the replayed day. Plus a fixed seed, because a gate that flakes is a gate people learn to ignore.

Now the test.

[CODE: `tests/budget/test_budget_gate.py`]
```python
SESSIONS = int(os.environ.get("BUDGET_GATE_SESSIONS", "300"))
INCIDENTS = os.environ.get("BUDGET_GATE_INCIDENTS", "none")
SEED = int(os.environ.get("BUDGET_GATE_SEED", "7"))
STORE_PATH = os.environ.get("BUDGET_GATE_STORE", ".atlas/budget-gate.sqlite")


@pytest.fixture(scope="module")
def gate():
    settings = Settings.from_env()
    store = LocalSpanStore(STORE_PATH)
    store.clear()
    summary, _ = replay_day(
        SEED, sessions=SESSIONS, incidents=INCIDENTS, store=store, judge_rate=0.3, settings=settings
    )
    return settings, store, summary


def test_cost_per_session_within_budget(gate):
    settings, store, summary = gate
    cps = float(cost_per_session(store.cost_records("request")))
    ...
    assert cps <= settings.budget_cost_per_session_usd


def test_p95_latency_within_budget(gate):
    ...


def test_no_tenant_over_its_daily_soft_cap(gate):
    ...


def test_task_success_slo_holds(gate):
    ...
```

The fixture replays a three-hundred-session day with a fixed seed and no incidents, the baseline, into its own store, and the four tests read that store. `cost_per_session` over the request-level cost records against `budget_cost_per_session_usd`. `percentile` of the latency samples against `budget_p95_latency_ms`. Every tenant's rollup against its soft cap. And `compute_slis` against `DEFAULT_SLOS` for task success. [PAUSE] Three environment variables make the gate a demo: `BUDGET_GATE_INCIDENTS=latency_regression make budget-check` replays a bad day and fails; `BUDGET_P95_LATENCY_MS=2500` tightens the budget and fails; `BUDGET_GATE_SESSIONS=1000` makes it slower and more precise.

[DEMO: `BUDGET_GATE_INCIDENTS=latency_regression make budget-check`. `test_p95_latency_within_budget` fails: p95 above the 4,000 ms budget. Unset.]

Now the Incident 1 change. Diet off, top-k twelve. The tokens test fails with twenty-four thousand. That's the same number you read off turn two of the trace in Lecture 11.2, on a Monday morning, without a provider or a tenant involved.

Now CI.

[CODE: `.github/workflows/ci.yml`, abbreviated]
```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

defaults:
  run:
    working-directory: 03-code

env:
  OFFLINE: "1"
  OTEL_EXPORTER: none
  PYTHONPATH: ${{ github.workspace }}/03-code:${{ github.workspace }}/03-code/src

jobs:
  test:
    name: unit + integration (offline)
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: uv pip install --system -e ".[dev]"
      - name: Lint
        run: ruff check . && ruff format --check .
      - name: Unit tests
        run: pytest -q tests/unit
      - name: Integration tests
        run: pytest -q tests/integration
      - name: Incident datasets are deterministic
        run: |
          python incidents/generate.py --out /tmp/incidents-regen
          for d in incidents/incident-0*; do
            n=$(basename "$d"); cmp "$d/spans.jsonl" "/tmp/incidents-regen/$n/spans.jsonl"; cmp "$d/scores.jsonl" "/tmp/incidents-regen/$n/scores.jsonl";
          done

  budget-gate:
    name: budget gate (cost/session + p95, offline replay)
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - name: Replay the day and enforce budgets
        env:
          BUDGET_COST_PER_SESSION_USD: "0.05"
          BUDGET_P95_LATENCY_MS: "4000"
        run: pytest -q tests/budget -ra
      - name: Publish summary
        if: always()
        run: python console/ops_console.py --text --store .atlas/budget-gate.sqlite --seed -1 >> "$GITHUB_STEP_SUMMARY" || true

  live-evals:
    name: live judge (only when secrets exist)
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push'
    ...
```

Three jobs. Unit and integration tests, offline, on every pull request and push. The budget gate, offline, after unit passes, also on every pull request. No secrets needed for either, which means a contributor's fork can run them and nothing leaks.

The third job runs the live evals from Section 8 against the `atlas-failures` dataset, and it only runs on pushes to main, because it spends money and needs keys. Fifty items is about a dollar. It's the Incident 3 gate: the prompt version that reaches main gets scored against the traces that failed last time.

Verify the action versions against current GitHub Actions and uv docs before recording; they move.

[CODE: release tagging, `Settings` and `init_langfuse`]
```python
# src/northwind/config.py: langfuse_release comes from LANGFUSE_RELEASE, default "v1.0.0"
# CI sets LANGFUSE_RELEASE to the commit; locally the Makefile exports it:
#   LANGFUSE_RELEASE ?= $(shell git rev-parse --short HEAD)

# telemetry/langfuse_setup.py::init_langfuse (as shipped)
_CLIENT = Langfuse(..., environment=settings.langfuse_environment, release=settings.langfuse_release, ...)
# every trace now carries the release; build_resource() puts the same value on deployment.release for OTel
```

Last piece. The release tag. CI passes the commit SHA as `LANGFUSE_RELEASE`, and the Makefile falls back to `git rev-parse` locally. `init_langfuse` puts it on every trace, and `build_resource` puts the same value on the OTel resource, from Lectures 3.2 and 4.1. So when a regression does reach production, because no gate catches everything, the timeline in your incident template says "release abc123 at 12:30" and you go straight to the diff.

[SLIDE 1: What the gate catches, and what it doesn't]
- Catches: context diet off, top-k changes, model swaps, prompt length growth, step limit changes, retry settings that stack timeouts
- Catches: anything deterministic that changes tokens, steps or simulated latency, including env and config
- Doesn't catch: provider slowdowns, quality regressions, real-world intent shift
- For those: fallbacks and breakers (Section 7), online judge and drift (Section 8), the live-evals job

What the gate catches: anything deterministic that changes tokens, steps or simulated latency, including config and environment, which is where both of Monday's and Tuesday's causes lived. What it doesn't: provider slowdowns, because the mock is not the provider. Quality regressions, because the mock doesn't judge. Real intent shift. For those you have fallbacks, the breaker, the online judge, drift detection and the live-evals job. The gate is one layer, and it's the cheapest one.

[AVATAR]
Ninety seconds in CI, zero dollars, and two of the three incidents from Section 11 never happen. Next, the checklist that makes the whole stack production-ready.

**Recap:** The budget gate replays a deterministic offline day and asserts cost per session, p95, tenant soft caps and the task-success SLO against budgets in `Settings`, runs on every pull request without secrets, and release tags make anything that slips through attributable to a commit.

**Transition:** Next, the production readiness checklist: sampling, back-pressure, secrets, dashboards as code and alert ownership.

### Speaker notes: common student mistakes / Q&A

- Mistake: budgets set to the current baseline with no headroom. Every legitimate change fails and the gate gets disabled. The shipped default of $0.05 against a $0.006 baseline is deliberately loose for a young product; discuss tightening to 2-3x baseline once traffic is real.
- Mistake: a random seed. Show the flake once if you have time; a gate that fails randomly is worse than none.
- "Why mean cost per session, not p95?" Either works; p95 catches one runaway session, mean catches broad drift. Suggest both for the capstone.
- `simulator/replay.py::replay_day(seed, sessions=, incidents=, store=, judge_rate=, settings=)` returns `(ReplaySummary, LocalSpanStore)`; `LocalSpanStore.cost_records()`, `latency_samples()` and `spans(kind=)` in `telemetry/local_store.py` are what the assertions read.
- The replay must be fast enough for CI. If the day takes more than three minutes, reduce `sessions=` and say so.
- Verify `actions/checkout`, `astral-sh/setup-uv` versions before recording.

---

## Lecture 13.4 — Production readiness checklist for observability

| Field | Value |
|---|---|
| ID | 13.4 |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (~610 spoken words) |
| Learning objectives | 1. Walk the twelve-item production checklist and know what "done" means for each. 2. Explain exporter back-pressure and why telemetry must never block a request. 3. Assign ownership to every dashboard and alert. |
| Prerequisites | 13.1 to 13.3 |
| Files used | `10-resources/production-checklist.md`, `telemetry/otel_setup.py`, `telemetry/langfuse_setup.py`, `deploy/grafana/dashboards/atlas-ops.json` |

### Script

[B-ROLL: A checklist with twelve boxes. The first four tick quickly. The camera lingers on an unticked one: "Every alert has an owner."]

[AVATAR]
Here's a test for any observability setup. Ask: "If Langfuse went down right now, would Atlas keep answering?" Then: "If a cost alert fired at three a.m., whose phone rings?" Teams that can't answer both in one sentence have a demo, not production.

This checklist is twelve items. You've built most of them. The point of the lecture is to know what "done" means for each, because half-done observability fails exactly when you need it.

[SLIDE 1: Sampling and volume]
1. Sampling policy written down: head rate in the SDK, tail rules in the Collector
2. Volume estimated: spans per day × bytes per span; storage and cost projected for 90 days
3. Retention set per environment (Lecture 10.3); ClickHouse disk alarmed

First group: volume. One, a written sampling policy. What head rate the SDK applies, what the Collector keeps regardless. If it's not written, it's whatever someone last typed. Two, volume estimated. Spans per day times bytes per span, projected ninety days. Atlas at fourteen hundred sessions a day, four steps each, ten kilobytes a step is about fifty-six megabytes a day. Small. Your company's agent at fifty thousand sessions is two gigabytes a day, and that's a budget line. Three, retention set per environment, with an alarm on ClickHouse disk.

[SLIDE 2: Never block a request]
4. Exporter back-pressure: bounded queue, drop on overflow, export timeout ≤ 5 s
5. Telemetry failure is a warning log and a metric, never an exception in the request path
6. Flush on shutdown, with a deadline
```python
# telemetry/otel_setup.py, as shipped
BatchSpanProcessor(SafeSpanExporter(exp, name=kind), max_queue_size=2048, max_export_batch_size=256,
                   schedule_delay_millis=1000, export_timeout_millis=5000)
OTLPSpanExporter(endpoint=settings.otel_endpoint, timeout=5)
Langfuse(..., flush_at=50, flush_interval=2.0)          # telemetry/langfuse_setup.py
shutdown_tracing(timeout_ms=5000)                        # on app exit
```

Second group, and the most important: never block a request. Four, back-pressure. The batch processor has a bounded queue, two thousand spans, and when it's full it drops the oldest. Export timeout five seconds. The Langfuse client has the same knobs: flush at fifty, flush every two seconds. Five, a telemetry failure is a warning log and a counter, never an exception that reaches the user; `SafeSpanExporter` wraps every exporter for exactly that, and you'll see it tested in the next lecture. Six, flush on shutdown with a deadline, `shutdown_tracing` with five seconds, so a deploy doesn't lose the last batch, but also doesn't hang for a minute waiting for a dead backend.

[SLIDE 3: Secrets and separation]
7. No backend credentials in Atlas: the Collector holds them
8. Project per environment: `atlas-dev`, `atlas-staging`, `atlas-prod`; keys scoped to each
9. Masking tested: a unit test sends a fake email and employee ID through `pii.mask` and the Collector config

Third group: secrets. Seven, no backend credentials in Atlas; the Collector holds them, from Lecture 13.2. Eight, a project per environment, with keys scoped to each, so a dev key can never write to prod. Nine, masking *tested*. Not configured, tested. A unit test sends a fake email and employee ID through `pii.mask`, and an integration test asserts the span that leaves the Collector has a hash where the ID was. Masking that isn't tested drifts the first time someone adds a field.

[SLIDE 4: Dashboards and alerts as code, with owners]
10. Dashboards in the repo: `deploy/grafana/dashboards/atlas-ops.json`, provisioned, not hand-built
11. Alert rules in the repo, each with a runbook link (Lecture 9.5)
12. Every dashboard and every alert has a named owner; alerts without an owner are deleted

Fourth group. Ten, dashboards as code. `atlas-ops.json` lives in the repo and is provisioned into Grafana at start. A dashboard someone built by hand in the UI dies with their laptop. Langfuse dashboards are UI-built today, so document them with screenshots and the filters they use. Eleven, alert rules in the repo, each linking to a runbook, from Lecture 9.5. Twelve, and the one teams skip: every dashboard and every alert has a named owner. If an alert has no owner, delete it. An alert nobody owns trains everyone to ignore alerts.

[SLIDE 5: What "done" looks like]
- A one-page `OBSERVABILITY.md` in the repo: sampling policy, retention, projects, owners, how to run the stack
- The chaos test from the next lecture passes: backend down, Atlas up
- The budget gate is green and required for merge
- A new engineer can find "why was this session expensive" in under ten minutes using only the README

What does done look like? A one-page `OBSERVABILITY.md` in the repo: the policy, the retention, the projects, the owners, how to run the stack. The chaos test from the next lecture passes. The budget gate is a required check for merge. And the real test: a new engineer, given only the README, can answer "why was this session expensive" in under ten minutes.

[AVATAR]
Open `production-checklist.md` and tick what you have. Most students have eight of twelve after Section 13. The four they're missing are almost always the same: volume estimate, tested masking, alert owners and the shutdown deadline. Fix those before the capstone.

**Recap:** Production observability means a written sampling policy and volume estimate, exporters that drop rather than block, credentials in the Collector with masking tested, and dashboards and alerts as code with a named owner for each.

**Transition:** Next, we prove item five the hard way: kill the observability backend while Atlas is serving traffic and watch what happens.

### Speaker notes: common student mistakes / Q&A

- Verified on installed packages: `BatchSpanProcessor(span_exporter, max_queue_size=, schedule_delay_millis=, max_export_batch_size=, export_timeout_millis=)`; `OTLPSpanExporter(timeout=)`; `Langfuse(flush_at=, flush_interval=, timeout=)`. The values shown are the ones in the shipped `otel_setup.py` and `langfuse_setup.py`.
- "Isn't dropping telemetry dangerous?" Less dangerous than dropping requests. Say it plainly: telemetry is a means; the service is the end. The metric counting dropped spans is what tells you it happened.
- Grafana provisioning specifics (provider config, folder mapping): verify against current Grafana docs before recording.
- Item 12 gets pushback ("we can't delete alerts"). Offer the alternative: an alert with no owner is auto-assigned to the engineering manager. Ownership appears quickly.

---

## Lecture 13.5 — Chaos demo: kill the observability backend

| Field | Value |
|---|---|
| ID | 13.5 |
| Type | DM (live demo) |
| Target duration | 5:00 (~600 spoken words; the rest is live demo time) |
| Learning objectives | 1. Show that Atlas keeps serving with the same p95 when Langfuse and the Collector are down. 2. Read the warning logs and the export-failure metric that make the failure visible without making it fatal. 3. Recognise the two misconfigurations that turn a backend outage into a user-facing incident. |
| Prerequisites | 13.1 to 13.4 |
| Files used | `telemetry/otel_setup.py` (`SafeSpanExporter`, `configure_tracing(batch=)`, `exporter_health()`), `telemetry/metrics.py` (`EXPORTER_FAILURES`), `deploy/docker-compose.langfuse.yml`, `deploy/docker-compose.observability.yml`, `simulator/swarm.py` |

### Script

[B-ROLL: Split screen. Left: swarm traffic hitting Atlas, p95 ticking at 3.1 s. Right: a terminal cursor hovering over `docker compose stop langfuse-web otel-collector`.]

[AVATAR]
Everything in this section adds moving parts between Atlas and your traces. Every moving part can fail. So here's the question that decides whether this stack belongs in production: when the observability backend dies, does Atlas notice?

Let's find out. Live.

[SCREEN: Terminal one: `make swarm RPS=5` running against Atlas with the Collector and local Langfuse up. Terminal two: `watch 'curl -s localhost:8000/metrics | grep atlas_request_latency'` showing p95 around 3.1 s. Browser: local Langfuse, traces arriving.]

Swarm at five requests a second. The metrics endpoint shows p95 around three point one seconds. Langfuse is receiving traces. Everything healthy.

Now the outage.

[DEMO: Terminal three: `docker compose -f deploy/docker-compose.langfuse.yml stop langfuse-web langfuse-worker`. Then `docker compose -f deploy/docker-compose.observability.yml stop otel-collector`. Wait five seconds.]

Stop Langfuse. Web and worker. And stop the Collector too, so Atlas has nowhere at all to send spans. The worst case.

[SCREEN: Terminal two, the metrics watch. p95 still 3.1 s. `atlas_requests_total` still climbing at the same rate. Terminal one, swarm output: all 200s.]

Watch the metrics. p95: three point one. Requests: still flowing, all two hundreds. The swarm hasn't noticed. Users wouldn't notice. Atlas is serving exactly as before.

So where did the spans go?

[SCREEN: Atlas logs. Warning lines every few seconds: `WARNING atlas.otel exporter otlp failed: ConnectionError (localhost:4318); 256 spans dropped`. Then `curl localhost:8000/metrics | grep atlas_telemetry_export_failures_total` → `atlas_telemetry_export_failures_total{name="otlp"} 14`. Then `curl localhost:8000/healthz` showing `exporters: [{"name": "otlp", "healthy": false, "failures": 14}, {"name": "local_store", "healthy": true}]`.]

Into the logs and a counter. `SafeSpanExporter`, the wrapper around every exporter in `otel_setup.py`, catches the connection error, logs one warning per batch, counts it in `atlas_telemetry_export_failures_total`, and returns. The batch processor's queue is bounded at two thousand and forty-eight spans; when it fills, the oldest are dropped. And `/healthz` reports each exporter's health from `exporter_health()`, so a load balancer or a dashboard can see that the OTLP exporter is failing while the service is fine.

That counter is an alert in Lecture 9.5's rules: "telemetry export failing for five minutes" pages the platform owner, not the on-call for Atlas, because Atlas is fine.

This is item five from the checklist, working. The failure is loud in the right place, logs, a metric and a health field, and silent in the wrong place, the user's response.

[SLIDE 1: Why it worked]
- `BatchSpanProcessor`: export happens on a background thread, never in the request
- Bounded queue: `max_queue_size=2048`; overflow drops, never blocks
- `OTLPSpanExporter(timeout=5)` and `export_timeout_millis=5000`: a dead endpoint costs the background thread 5 s, not the request
- `SafeSpanExporter`: exceptions become a warning and a counter, never a raise
- Langfuse client: `flush_at=50`, `flush_interval=2.0`, same idea

Why did it work? Five settings from the previous lecture. Export runs on a background thread, so the request never waits. The queue is bounded and drops on overflow. The exporter times out in five seconds, on that background thread. Every exporter is wrapped so an exception becomes a warning and a number. And the Langfuse client behaves the same way.

Now let me show you how to break it, because you'll inherit code that does.

[DEMO: Restart Atlas with `configure_tracing(batch=False)` forced (env `ATLAS_TRACING_BATCH=0` in the demo branch), backends still down. Metrics watch: p95 climbs to 8.4 s within thirty seconds. Swarm output shows timeouts.]

[SLIDE 2: Two ways to turn a telemetry outage into a user outage]
- `SimpleSpanProcessor` (`batch=False`): exports synchronously inside the request; a dead backend adds the full timeout to every response
- No timeout, or a 30 s default, on the exporter: the background thread hangs, the queue fills, and shutdown blocks
- Both are one-line mistakes that pass every unit test

Force the simple processor, which `configure_tracing` supports for tests because it's easy to reason about, and restart with the backends down. p95 goes from three seconds to eight and a half within thirty seconds. Every request now waits for the export to fail. That's how a monitoring outage becomes a product outage, and it's one flag.

The second way is a missing or default timeout. A thirty-second exporter timeout means the background thread hangs, the queue fills faster, and worse, `shutdown_tracing` blocks for thirty seconds per batch. Your deploys start timing out. Also one line, which is why `_make_exporter` hard-codes five.

[DEMO: Revert to batch mode. Start Langfuse and the Collector again. Within a minute, new traces appear in Langfuse; `/healthz` shows `otlp: healthy`. Callout: the dropped spans are gone for good; the gap is visible in the Langfuse timeline.]

Revert, bring the backends back, and within a minute new traces arrive and the health field flips back. The dropped spans are gone; there's a gap in the timeline. That's the trade. You lost eight minutes of traces and kept eight minutes of a working helpdesk. Every time, take that trade.

[AVATAR]
Add this to your integration tests: configure tracing with an unreachable OTLP endpoint, send ten requests, assert every one returns two hundred within budget and that `exporter_health()` reports the failure. `FailingSpanExporter` in `otel_setup.py` exists for exactly this. It's a twelve-line test and it protects the most important property this stack has.

**Recap:** With a batch processor, a bounded queue, short timeouts and a safe exporter wrapper, a dead backend costs you spans, a warning and a counter, not requests; a synchronous processor or a default timeout turns the same outage into a user-facing incident.

**Transition:** Next, Lab 7: the whole self-hosted stack running end to end on your machine, with the budget gate green.

### Speaker notes: common student mistakes / Q&A

- Rehearse the stop and start sequence; first start of Langfuse after a stop can take thirty seconds while the worker reconnects. Cut the wait.
- The simple-processor demo needs the backends down to be dramatic; with backends up it's merely slower. `configure_tracing(batch=False)` is the shipped switch; the `ATLAS_TRACING_BATCH` env name is a demo-branch convenience, not in `Settings`.
- Metric and helper names as shipped: `atlas_telemetry_export_failures_total{name}` (`metrics.EXPORTER_FAILURES`), `SafeSpanExporter`, `FailingSpanExporter`, `exporter_health()`, `shutdown_tracing(timeout_ms=5000)`. Confirm the exact warning text and the `/healthz` payload against `otel_setup.py` and `server.py` before recording.
- "Should we buffer to disk instead of dropping?" You can, via a Collector file exporter or persistent queue, and for compliance logging (Lecture 10.4) you might have to. For operational tracing, dropping is the right default. Mention, don't build. Note that the local SQLite store keeps receiving spans throughout, so offline analysis still works.

---

## Lecture 13.6 — Lab 7: Self-hosted stack end to end

| Field | Value |
|---|---|
| ID | 13.6 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 (~360 spoken words); lab itself about 60 to 90 minutes |
| Learning objectives | 1. Run Langfuse, the Collector, Prometheus and Grafana locally and trace a replayed day through all of them. 2. Confirm masking and tail sampling are working from the data, not the config. 3. Get the budget gate green locally and in a CI run. |
| Prerequisites | 13.1 to 13.5 |
| Files used | `04-labs/lab-07-self-host.md`, `deploy/`, `tests/budget/test_budget_gate.py`, `.github/workflows/ci.yml` |

### Script

[AVATAR]
Everything from this section, running together, on your machine. That's Lab 7. It's the longest lab in the course, and it's the one that goes on your CV, because at the end you'll have a screenshot of a self-hosted observability stack you built and a green CI run you configured.

[SLIDE 1: Lab 7 checklist]
1. `make langfuse-up` and `make stack`: Langfuse, Collector, Prometheus, Grafana all healthy
2. Atlas exporting to the Collector only; no Langfuse keys in Atlas's env
3. `OFFLINE=1 make replay`: a day of traffic visible in Langfuse and on the Grafana Atlas Ops dashboard
4. Proof of masking: a tool span in Langfuse shows a hash, not a payload
5. Proof of tail sampling: every error and every >4 s trace present; normal traffic sampled
6. `make budget-check` green locally; CI run green on a branch
7. Chaos: stop Langfuse during a replay; Atlas p95 unchanged; `atlas_telemetry_export_failures_total` rises and `/healthz` shows the exporter unhealthy

Seven steps. Bring up both stacks and get every container healthy. Make sure Atlas exports to the Collector only; if there's a Langfuse key in Atlas's environment, you skipped Lecture 13.2. Replay a day offline and see it in Langfuse and Grafana.

Then prove two things from the data. Open a tool span and see a hash where the payload was. Filter to errors and slow traces and confirm they're all there, while normal traffic is sampled down. The config says it works; the data proves it.

Get the budget gate green locally, push a branch, and get it green in CI. Then run the chaos test yourself: stop Langfuse during a replay, watch p95 hold, watch the export-failure counter climb and the health endpoint say so.

[SLIDE 2: Deliverables]
- Screenshot: `docker compose ps` with all services healthy
- Screenshot: Grafana Atlas Ops dashboard with replayed data
- Screenshot: a masked tool span in Langfuse
- Link or screenshot: green CI run including `budget-gate`
- Three sentences: what you would change before running this for a real team

Five deliverables. Four screenshots and a link to the CI run. Plus three sentences: what would you change before running this for a real team? The checklist from Lecture 13.4 is your prompt.

[SLIDE 3: Where students get stuck]
- ClickHouse restarting: raise Docker memory to 6 GB or more
- Traces in Collector logs but not in Langfuse: check the OTLP endpoint path and the basic auth header
- Grafana dashboard empty: Prometheus target for Atlas `/metrics` not scraping; check `docker compose logs prometheus`
- Budget gate fails on a fresh clone: check `OFFLINE=1` and the seed; the baseline must be deterministic

Four places people get stuck. ClickHouse restarting means Docker needs more memory. Traces visible in the Collector logs but not in Langfuse means the endpoint path or the auth header is wrong; check the current Langfuse OTLP docs. An empty Grafana dashboard means Prometheus isn't scraping Atlas; read the Prometheus logs. And a budget gate that fails on a fresh clone almost always means offline mode isn't set.

[AVATAR]
Budget ninety minutes. When it's done, you have the deployment half of the capstone finished before the capstone begins. Post your Grafana screenshot in the Q&A. I want to see them.

**Recap:** Lab 7 runs the full self-hosted stack, proves masking and sampling from the data, gets the budget gate green in CI and repeats the chaos test on your own machine.

**Transition:** That completes Section 13. Next is the capstone: the Atlas Ops Console, built by you first, then compared with the reference.

### Speaker notes: common student mistakes / Q&A

- Windows students: Docker Desktop with WSL2 works; file permissions on volumes are the usual issue. Point to the lab's troubleshooting section.
- Low-spec machines: the lab allows running Langfuse Cloud instead of self-hosted for steps 3 to 6, with the Collector still local. Say so in Q&A; it's in the lab file.
- The CI step requires the student's own fork with Actions enabled; no secrets are needed for `test` and `budget-gate`.
- Grafana specifics (provisioning path, datasource UID in `atlas-ops.json`): verify against current Grafana docs and the dashboard file before recording.
