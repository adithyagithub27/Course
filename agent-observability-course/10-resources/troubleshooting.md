# Troubleshooting Guide

**Used in:** 2.2-2.5 (setup and first trace), 3.6 (broken traces), 13.1-13.6 (self-hosting). Pin a copy in Q&A.

> Before posting in Q&A, run through the matching section below. If you're still stuck, post: **lecture number, OS, Python version (`python --version`), the command you ran, and the full error text** (with keys removed).

**Fast isolation trick:** if something fails, run **offline** first:

```bash
OFFLINE=1 make test        # no keys, no network: unit + integration tests
OFFLINE=1 make replay      # fills the local store with a day of spans from the mock LLM
OFFLINE=1 make console     # Ops Console over the local store
```

If offline works, the problem is **keys, network or the backend** (sections 3-5). If offline fails, the problem is **install or environment** (section 1). If offline works and Langfuse shows nothing, it's **export** (section 4).

---

## 1. Install and Python

| Symptom | Likely cause | Fix |
|---|---|---|
| `uv: command not found` | uv not installed or not on PATH | Install uv (see its docs), restart the terminal; or use the pip fallback from lecture 2.2 |
| Errors about Python version / syntax errors in packages | Python older than 3.11 | Install Python 3.11+; `uv python install 3.11` or your OS package manager; recreate the venv |
| `ModuleNotFoundError: langfuse` / `opentelemetry` | Running outside the project environment | `uv run ...` or activate `.venv`; re-run `make install` |
| `make: command not found` (Windows) | No make on Windows | Use WSL, install make (e.g., via a package manager), or run the underlying commands from the Makefile directly |
| Unit tests fail right after install | Wrong directory or partial install | Run from the repo root; `make install` again; check the output of `make test` for the first failure |
| Version mismatch warnings (`langfuse`, `opentelemetry-semantic-conventions`) | A newer version was installed than the course pins | `uv sync` respects the lock; if you upgraded on purpose, read the pinned Q&A thread on breaking changes; the GenAI conventions are incubating and attribute constants can move |
| `tiktoken` tries to download and fails | No network for encodings | Expected: `tokens.py` falls back to the approximation; tiktoken is optional |

## 2. Offline mode, replay and the Ops Console

| Symptom | Fix |
|---|---|
| `make replay` produces different numbers from the video | Different seed or fixture day: use `SEED=` and `DAY=` from the README; the course numbers are from one frozen day and a dated price table (and are simulated) |
| Ops Console shows an empty store | Replay didn't run or wrote elsewhere; check `LOCAL_STORE_PATH`; run `OFFLINE=1 make replay` then `make console` |
| Ops Console pages look different from the video | Streamlit version or theme: `uv sync` pins it; check `.streamlit/config.toml` exists |
| Replay is slow | Lower RPS or the day length via env (see README); the replay writes every span |
| `OFFLINE=1` but the app still tries to call OpenAI | Env var not exported in that shell, or set after import; export it before `make run`; check `config.py` reads it |

## 3. API keys and accounts

| Symptom | Likely cause | Fix |
|---|---|---|
| `KeyError` / "missing environment variable" at startup | `.env` not created or not in the repo root | `cp .env.example .env` and fill it in; run from the repo root |
| Langfuse `401` / "invalid credentials" | Wrong `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`, or keys from a different project | Regenerate the key pair in the Langfuse project settings; no quotes or spaces in `.env` |
| Langfuse traces never appear, no error | Wrong `LANGFUSE_BASE_URL` (Cloud **region** mismatch, or pointing at a self-host that isn't running) | Copy the base URL shown in your project settings; for self-host use your compose URL (13.1) |
| OpenAI `401` | Invalid key | Regenerate the key; no quotes or spaces in `.env` |
| OpenAI `429` / insufficient quota | No credit, a rate limit, or **your own hard cap** was hit | Add credit; check the cap you set in 2.1 (that's it working); wait and retry for rate limits |
| OpenAI "model not found" | A provider renamed a model | Set `ATLAS_MODEL` / `ESCALATION_MODEL` / `ROUTING_MODEL` env vars (names in `config.py`) to the current name; check the repo README |
| Judge runs cost more than expected | No cap | Set `JUDGE_MAX_CALLS` and a sample rate ≤ 10% (8.2) |
| Live evals in CI are skipped | No secrets in the fork | Expected: unit, integration and the budget gate always run; live evals only with secrets (13.3) |

**Never paste keys into Q&A.** If you did by accident, revoke the key immediately.

## 4. Tracing and export

| Symptom | Likely cause | Fix |
|---|---|---|
| Console exporter prints spans but Langfuse is empty | Exporter not configured for OTLP/Langfuse, or `flush()` never called | Check `telemetry/otel_setup.py` exporter selection (`console` vs `langfuse`); call `client.flush()` before exit (4.6); check `sample_rate` isn't 0 |
| Spans appear but as separate traces (orphans) | Context not propagated into an async task or thread | See 3.6: pass the context / use `start_as_current_span` inside the task; `tests/integration/test_spans.py` has the pattern |
| Tool span outside the agent span | Span opened before the parent or after it closed | Open tool spans inside the step span (5.2) |
| Every generation counted twice | Instrumented twice (manual + auto, or `instrument()` called twice) | Instrument once at startup; `OpenAIInstrumentor().instrument(...)` is idempotent per provider but not if you also add manual generation spans for the same call |
| `gen_ai.*` attribute missing in the backend | Attribute set with a hand-typed string that doesn't match the pinned semconv version | Use the `g.GEN_AI_*` constants (3.4); check `opentelemetry-semantic-conventions` version |
| Usage or cost shows 0 in Langfuse | `usage_details` / `cost_details` not set on the generation | `update_current_generation(usage_details=..., cost_details=...)` (4.2); check the usage object field names for Chat vs Responses (6.1) |
| Cached tokens show but cost didn't drop | Price table charges cached input at full rate | Fix `pricing.py` to use the cache-read rate (6.2) |
| `ImportError` for `opentelemetry.instrumentation.openai_v2` | You followed a different tutorial | The course uses OpenInference (3.5); the otel-contrib OpenAI instrumentor was broken at verification time |
| Traces appear in the wrong environment/project | `environment` or keys point elsewhere | One project per environment (10.3); check `LANGFUSE_*` vars for that shell |

## 5. Docker, self-hosting and the collector (Sections 9 and 13)

| Symptom | Likely cause | Fix |
|---|---|---|
| Compose fails on start | Compose file drifted from the current Langfuse release; missing env vars | **Verify against the current Langfuse compose file**; set the env vars it requires (it will tell you which); check port conflicts |
| Compose starts but the machine crawls | Not enough RAM for Langfuse + collector + Prometheus + Grafana | Close other apps; increase Docker's memory; run Langfuse Cloud for Sections 4-12 and self-host only for 13 |
| Apple Silicon image errors | Image architecture | Check for `platform:` overrides in the compose file; pull multi-arch images |
| Collector receives nothing | Wrong OTLP endpoint or port; http vs grpc mismatch | The course exporter is OTLP/HTTP (`opentelemetry.exporter.otlp.proto.http`); point it at the collector's HTTP receiver port; check the collector logs |
| Collector exports to Langfuse fail with auth errors | `Authorization` header not set from env | The header value is `${env:LANGFUSE_AUTH}` (basic auth of public:secret, base64); never a literal in the file |
| Prometheus target DOWN | `/metrics` not mounted or wrong host from inside Docker | `make_asgi_app()` mounted at `/metrics` (9.2); from a container, the host is `host.docker.internal` (Docker Desktop) or the compose service name, not `localhost` |
| Grafana dashboard import fails | Grafana version schema mismatch | Pin the Grafana image version in the compose file; re-export the JSON from that version |
| Alert never fires in Lab 6 | Threshold too high for the replayed traffic, or evaluation interval too long | Lower the threshold for the lab, or replay the incident scenario that breaches it |
| Atlas errors when Langfuse container is stopped | Exporter blocking or prompt fetch without fallback | This is lecture 13.5: set exporter timeouts/queue limits and pass `fallback=` to `get_prompt` |

## 6. Incident labs

| Symptom | Fix |
|---|---|
| I opened `solution.md` by accident | Close it, write your hypothesis anyway, and do the next incident blind; the fourth (Project 2) has no solution in the repo |
| The incident spans don't load in the Ops Console | Use the loader in the incident README (`make console STORE=incidents/incident-01-cost-spike/spans.jsonl`, see README for the exact flag) |
| My root cause differs from the reveal | Post it in the pinned incident thread with a spoiler tag; alternative explanations that fit the evidence are worth discussing |

## 7. Tests and CI

| Symptom | Fix |
|---|---|
| Budget gate fails locally but not in the video | Your price table or replay seed differs; check `pricing.py` date and `SEED=`; the gate compares against **your** budget values in `tests/budget/test_budget_gate.py` |
| Budget gate flaky | Replay not deterministic: check nothing uses wall-clock time or an unseeded random; the mock LLM must be seeded |
| CI green locally, red on GitHub | Different Python version or missing system dep; match the workflow's `python-version`; check the lock file is committed |

Still stuck? Post in Q&A with the details listed at the top.
