import pytest

HDR = {"X-Tenant": "hr", "X-User": "NW-40213"}


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert (
        body["status"] == "ok" and body["offline"] is True and isinstance(body["exporters"], list)
    )


def test_chat_requires_tenant(client):
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 400 and "X-Tenant" in r.json()["detail"]


def test_chat_response_shape(client):
    r = client.post("/chat", json={"message": "When is payroll paid?"}, headers=HDR)
    assert r.status_code == 200
    b = r.json()
    for k in [
        "answer",
        "session_id",
        "trace_id",
        "model",
        "steps",
        "outcome",
        "intent",
        "usage",
        "cost_usd",
        "latency_ms",
        "ttft_ms",
        "tool_calls",
        "escalated",
        "retries",
        "budget_decision",
        "prompt_version",
    ]:
        assert k in b
    assert (
        b["outcome"] == "resolved"
        and b["usage"]["input_tokens"] > 0
        and b["budget_decision"] == "allow"
    )


def test_unknown_scenario_422(client):
    r = client.post("/chat", json={"message": "hi", "scenario": "meteor"}, headers=HDR)
    assert r.status_code == 422


def test_message_validation(client):
    assert client.post("/chat", json={"message": ""}, headers=HDR).status_code == 422


def test_tenant_alias_and_unknown_collapse(client):
    r = client.post(
        "/chat", json={"message": "Hello Atlas!"}, headers={"X-Tenant": "logistics-ops"}
    )
    assert r.status_code == 200
    r2 = client.post("/chat", json={"message": "Hello Atlas!"}, headers={"X-Tenant": "marketing"})
    assert r2.status_code == 200
    spans = client.exporter.get_finished_spans()
    tenants = {s.attributes.get("atlas.tenant") for s in spans if s.name.startswith("invoke_agent")}
    assert tenants == {"ops", "other"}


def test_session_memory_via_header_and_body(client):
    r1 = client.post(
        "/chat",
        json={"message": "How many days of annual leave do I get?"},
        headers={**HDR, "X-Session": "abc"},
    )
    assert r1.json()["session_id"] == "abc"
    r2 = client.post(
        "/chat", json={"message": "And how do I request it?", "session_id": "abc"}, headers=HDR
    )
    assert r2.status_code == 200 and r2.json()["session_id"] == "abc"
    assert len(client.app.state.sessions) == 1
    hist = client.app.state.sessions.get("abc")
    assert hist[0]["role"] == "user" and any(m["role"] == "tool" for m in hist)


def test_feedback_recorded_in_store_and_metrics(client):
    r = client.post("/chat", json={"message": "When is payroll paid?"}, headers=HDR)
    tid = r.json()["trace_id"]
    fb = client.post(
        "/feedback",
        json={"trace_id": tid, "score": -1, "reason": "unhelpful", "comment": "too vague"},
        headers=HDR,
    )
    assert fb.status_code == 200 and fb.json()["value"] == 0.0 and fb.json()["langfuse"] is False
    scores = client.app_store.scores(name="user_feedback")
    assert len(scores) == 1 and scores[0].trace_id == tid and "unhelpful" in scores[0].comment
    assert (
        client.post("/feedback", json={"trace_id": tid, "score": 7}, headers=HDR).status_code == 422
    )
    metrics = client.get("/metrics").text
    assert 'atlas_feedback_total{outcome="negative",tenant="hr"}' in metrics


def test_metrics_endpoint_low_cardinality(client):
    client.post("/chat", json={"message": "How do I connect to the VPN?"}, headers=HDR)
    text = client.get("/metrics").text
    assert (
        "atlas_requests_total" in text
        and "atlas_cost_usd_total" in text
        and "atlas_request_latency_seconds_bucket" in text
    )
    assert (
        "atlas_tool_calls_total" in text
        and "atlas_tokens_total" in text
        and "atlas_ttft_seconds" in text
    )
    assert "user_id" not in text and "NW-40213" not in text and "session_id" not in text


def test_budget_endpoint(client):
    r = client.get("/budget")
    assert r.status_code == 200 and {b["tenant"] for b in r.json()} >= {
        "ops",
        "finance",
        "hr",
        "eng",
    }


def test_hard_cap_refuses_with_429(app_settings):
    from fastapi.testclient import TestClient

    from app.server import create_app
    from northwind.budget import BudgetGuard
    from telemetry.local_store import LocalSpanStore

    guard = BudgetGuard.from_caps(["hr", "other"], soft=0.001, hard=0.004)
    with TestClient(
        create_app(app_settings, store=LocalSpanStore(":memory:"), budget_guard=guard)
    ) as c:
        first = c.post("/chat", json={"message": "When is payroll paid?"}, headers=HDR)
        assert first.status_code == 200 and first.json()["budget_decision"] == "allow"
        for _ in range(40):
            last = c.post("/chat", json={"message": "When is payroll paid?"}, headers=HDR)
            if last.status_code == 429:
                break
        assert last.status_code == 429 and last.json()["detail"]["outcome"] == "refused"
        assert c.get("/budget").json()[0]["decision"] in {"degrade", "refuse", "allow"}
        assert 'decision="refuse"' in c.get("/metrics").text


def test_scenario_injection_via_body(client):
    r = client.post(
        "/chat", json={"message": "When is payroll paid?", "scenario": "slow_provider"}, headers=HDR
    )
    assert r.status_code == 200 and r.json()["latency_ms"] > 4000


def test_import_app_module():
    import app.server

    assert app.server.app.title == "Atlas helpdesk agent"


@pytest.mark.parametrize("path", ["/healthz", "/budget", "/metrics"])
def test_get_endpoints_exist(client, path):
    assert client.get(path).status_code == 200


def test_metrics_answers_without_redirect(client):
    for path in ("/metrics", "/metrics/"):
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 200 and "atlas_requests_total" in r.text, path


def test_feedback_comment_is_redacted(client):
    r = client.post("/chat", json={"message": "When is payroll paid?"}, headers=HDR)
    tid = r.json()["trace_id"]
    client.post(
        "/feedback",
        json={"trace_id": tid, "score": -1, "comment": "I am NW-40213, mail me at a.b@northwind.example"},
        headers=HDR,
    )
    comment = client.app_store.scores(name="user_feedback")[0].comment
    assert "NW-40213" not in comment and "a.b@northwind.example" not in comment
    assert "<EMPLOYEE_ID:" in comment and "<EMAIL:" in comment
