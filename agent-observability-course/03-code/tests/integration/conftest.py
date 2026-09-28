import pytest
from fastapi.testclient import TestClient

from app.server import create_app
from northwind.config import Settings
from telemetry.local_store import LocalSpanStore
from telemetry.otel_setup import get_memory_exporter


@pytest.fixture
def app_settings() -> Settings:
    return Settings.from_env({"OFFLINE": "1", "OTEL_EXPORTER": "memory", "ATLAS_LOCAL_STORE": ""})


@pytest.fixture
def client(app_settings):
    store = LocalSpanStore(":memory:")
    app = create_app(app_settings, store=store)
    with TestClient(app) as c:
        c.app_store = store  # type: ignore[attr-defined]
        exporter = get_memory_exporter()
        assert exporter is not None
        exporter.clear()
        c.exporter = exporter  # type: ignore[attr-defined]
        yield c
