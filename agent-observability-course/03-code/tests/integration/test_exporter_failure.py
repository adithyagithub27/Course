"""Lecture 13.5: kill the observability backend; Atlas keeps serving."""

from fastapi.testclient import TestClient

from app.server import create_app
from northwind.config import Settings
from telemetry.local_store import LocalSpanStore
from telemetry.otel_setup import (
    FailingSpanExporter,
    configure_tracing,
    exporter_health,
    get_tracer,
    shutdown_tracing,
)


def test_requests_survive_a_dead_exporter():
    settings = Settings.from_env(
        {"OFFLINE": "1", "OTEL_EXPORTER": "memory", "ATLAS_LOCAL_STORE": ""}
    )
    dead = FailingSpanExporter(raise_exc=True)
    # configure with the dead exporter *in addition* to memory, then run the app on the same provider
    configure_tracing(settings, store=LocalSpanStore(":memory:"), extra_exporter=dead, batch=False)
    from app.agent import AtlasAgent

    agent = AtlasAgent(settings)
    r = agent.run("When is payroll paid?", tenant="hr")
    assert r.outcome == "resolved"
    health = {h["name"]: h for h in exporter_health()}
    assert health["extra"]["failures"] >= 1 and dead.calls >= 1
    shutdown_tracing()


def test_slow_exporter_does_not_block_request_path():
    settings = Settings.from_env({"OFFLINE": "1", "OTEL_EXPORTER": "none", "ATLAS_LOCAL_STORE": ""})
    slow = FailingSpanExporter(raise_exc=False, delay_s=0.2)
    configure_tracing(
        settings, extra_exporter=slow, batch=True
    )  # BatchSpanProcessor: export happens off-thread
    import time

    t0 = time.perf_counter()
    for _ in range(20):
        with get_tracer().start_as_current_span("x"):
            pass
    assert time.perf_counter() - t0 < 0.5
    shutdown_tracing(timeout_ms=1000)


def test_server_starts_with_otlp_exporter_pointing_nowhere():
    settings = Settings.from_env(
        {
            "OFFLINE": "1",
            "OTEL_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:9/v1/traces",
            "ATLAS_LOCAL_STORE": "",
        }
    )
    with TestClient(create_app(settings, store=LocalSpanStore(":memory:"))) as c:
        r = c.post("/chat", json={"message": "Hello Atlas!"}, headers={"X-Tenant": "eng"})
        assert r.status_code == 200 and c.get("/healthz").status_code == 200
