import json
import logging

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g

from northwind.config import Settings
from northwind.pricing import estimate_cost
from telemetry import genai_attrs as ga
from telemetry import metrics
from telemetry.local_store import LocalSpanStore, records_from_otel
from telemetry.logging_setup import JsonFormatter, configure_logging
from telemetry.otel_setup import (
    FailingSpanExporter,
    SafeSpanExporter,
    build_resource,
    configure_tracing,
    current_trace_id,
    exporter_health,
    get_tracer,
    setup_tracing,
    shutdown_tracing,
)


def _provider():
    exp = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exp))
    return tp, exp


def test_span_names_follow_semconv():
    assert ga.llm_span_name("gpt-4.1-mini") == "chat gpt-4.1-mini"
    assert ga.tool_span_name("lookup_ticket") == "execute_tool lookup_ticket"
    assert ga.agent_span_name() == "invoke_agent atlas"


def test_llm_attributes_and_langfuse_mirrors():
    tp, exp = _provider()
    with tp.get_tracer("t").start_as_current_span("chat x") as span:
        ga.set_llm_request(
            span, model="gpt-4.1-mini", conversation_id="s1", prompt_version="v1", temperature=0.2
        )
        ga.set_llm_usage(
            span,
            input_tokens=100,
            output_tokens=20,
            cached_tokens=64,
            reasoning_tokens=0,
            ttft_s=0.25,
            finish_reasons=["stop"],
        )
        ga.set_cost(span, estimate_cost("gpt-4.1-mini", 100, 20, cached_tokens=64))
    a = exp.get_finished_spans()[0].attributes
    assert (
        a[g.GEN_AI_OPERATION_NAME] == "chat"
        and a[g.GEN_AI_REQUEST_MODEL] == "gpt-4.1-mini"
        and a[g.GEN_AI_PROVIDER_NAME] == "openai"
    )
    assert (
        a[g.GEN_AI_USAGE_INPUT_TOKENS] == 100
        and a[g.GEN_AI_USAGE_OUTPUT_TOKENS] == 20
        and a[g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS] == 64
    )
    assert a[g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK] == 0.25 and a[ga.ATLAS_TTFT_MS] == 250.0
    assert (
        a[ga.LF_OBS_TYPE] == "generation"
        and json.loads(a[ga.LF_OBS_USAGE])["cache_read_input_tokens"] == 64
    )
    assert json.loads(a[ga.LF_OBS_COST])["total"] > 0 and a[ga.ATLAS_COST_USD] > 0


def test_tool_attributes_are_masked_and_clipped():
    tp, exp = _provider()
    with tp.get_tracer("t").start_as_current_span("execute_tool x") as span:
        ga.set_tool(
            span,
            name="reset_password",
            call_id="c1",
            arguments={"employee_id": "NW-12345"},
            result="x" * 10_000,
        )
    a = exp.get_finished_spans()[0].attributes
    assert a[g.GEN_AI_TOOL_NAME] == "reset_password" and a[g.GEN_AI_TOOL_CALL_ID] == "c1"
    assert (
        "NW-12345" not in a[g.GEN_AI_TOOL_CALL_ARGUMENTS]
        and "<EMPLOYEE_ID:" in a[g.GEN_AI_TOOL_CALL_ARGUMENTS]
    )
    assert len(a[g.GEN_AI_TOOL_CALL_RESULT]) <= ga.MAX_ATTR_CHARS


def test_agent_tenant_retrieval_guardrail_error():
    tp, exp = _provider()
    with tp.get_tracer("t").start_as_current_span("invoke_agent atlas") as span:
        ga.set_agent(span, conversation_id="s1")
        ga.set_tenant_context(span, tenant="ops", user_id="NW-1", session_id="s1", intent="vpn")
        ga.set_retrieval(span, query="vpn", top_k=4, hits=0)
        ga.set_guardrail(span, kind="prompt_injection", triggered=True)
        ga.set_error(span, ValueError("boom"))
        ga.add_event(span, "x", detail={"a": 1})
    s = exp.get_finished_spans()[0]
    a = s.attributes
    assert (
        a[g.GEN_AI_AGENT_NAME] == "atlas"
        and a[g.GEN_AI_CONVERSATION_ID] == "s1"
        and a[ga.LF_SESSION_ID] == "s1"
        and a[ga.LF_USER_ID] == "NW-1"
    )
    assert a[ga.ATLAS_RETRIEVAL_EMPTY] is True and a[ga.ATLAS_GUARDRAIL_TRIGGERED] is True
    assert (
        a["error.type"] == "ValueError"
        and s.status.status_code.name == "ERROR"
        and any(e.name == "x" for e in s.events)
    )


def test_script_aliases_exist():
    tp, exp = _provider()
    with tp.get_tracer("t").start_as_current_span("x") as span:
        ga.set_agent_attrs(span, name="atlas")
        ga.set_llm_attrs(span, model="gpt-4.1", input_tokens=1, output_tokens=1)
        ga.set_tool_attrs(span, name="t")
    a = exp.get_finished_spans()[0].attributes
    assert a[g.GEN_AI_TOOL_NAME] == "t" and a[g.GEN_AI_USAGE_INPUT_TOKENS] == 1


def test_records_from_otel_infers_kind_and_status():
    tp, exp = _provider()
    tr = tp.get_tracer("t")
    with tr.start_as_current_span("invoke_agent atlas") as root:
        ga.set_agent(root)
        with tr.start_as_current_span("chat m") as gen:
            gen.set_attribute("gen_ai.operation.name", "chat")
    recs = records_from_otel(exp.get_finished_spans())
    by_name = {r.name: r for r in recs}
    assert by_name["invoke_agent atlas"].kind == "agent" and by_name["chat m"].kind == "generation"
    assert (
        by_name["chat m"].parent_span_id == by_name["invoke_agent atlas"].span_id
        and by_name["chat m"].status == "OK"
    )


def test_resource_attributes():
    r = build_resource(
        Settings.from_env({"OTEL_SERVICE_NAME": "atlas-test", "DEPLOYMENT_ENVIRONMENT": "ci"})
    ).attributes
    assert (
        r["service.name"] == "atlas-test"
        and r["deployment.environment"] == "ci"
        and r["deployment.environment.name"] == "ci"
    )


def test_safe_exporter_swallows_failures():
    failing = FailingSpanExporter()
    safe = SafeSpanExporter(failing, name="dead")
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(safe))
    with tp.get_tracer("t").start_as_current_span("x"):
        pass
    assert failing.calls == 1 and safe.failures == 1 and safe.exported == 0
    assert safe.force_flush() is True
    safe.shutdown()


def test_configure_tracing_memory_and_store_mirror():
    store = LocalSpanStore(":memory:")
    s = Settings.from_env({"OTEL_EXPORTER": "memory"})
    tp = configure_tracing(s, store=store)
    with get_tracer().start_as_current_span("invoke_agent atlas") as span:
        ga.set_agent(span)
        assert current_trace_id() == f"{span.get_span_context().trace_id:032x}"
    assert store.count() == 1 and exporter_health()[0]["exported"] >= 1
    assert setup_tracing(s, store=store) is not tp
    shutdown_tracing()
    assert current_trace_id() is None


def test_configure_tracing_none_exporter():
    s = Settings.from_env({"OTEL_EXPORTER": "none", "ATLAS_LOCAL_STORE": ""})
    configure_tracing(s)
    with get_tracer().start_as_current_span("x"):
        pass
    shutdown_tracing()


def test_metrics_label_allowlist():
    names = metrics.label_names()
    assert names <= metrics.ALLOWED_LABELS
    assert not (names & metrics.FORBIDDEN_LABELS)
    metrics.record_generation(
        tenant="ops",
        model="m",
        feature="f",
        input_tokens=1,
        output_tokens=1,
        cached_tokens=1,
        reasoning_tokens=1,
        cost_usd=0.1,
        ttft_s=0.1,
    )
    metrics.record_request(tenant="ops", model="m", outcome="resolved", latency_s=0.5, steps=2)
    metrics.record_tool(tool="lookup_ticket", ok=False, latency_s=0.01)
    metrics.set_build_info(version="1", model="m", prompt_version="v1")
    assert (
        metrics.FIRST_TOKEN_SECONDS is metrics.TTFT
        and metrics.LLM_COST is metrics.COST
        and metrics.BUDGET_EVENTS is metrics.BUDGET_DECISIONS
        and metrics.GUARDRAIL_EVENTS is metrics.GUARDRAIL
    )


def test_json_logging_has_trace_id_and_masks_pii():
    import io

    buf = io.StringIO()
    logger = configure_logging("INFO", stream=buf)
    tp, _ = _provider()
    with tp.get_tracer("t").start_as_current_span("x"):
        logger.info("user NW-12345 asked %s", "vpn", extra={"tenant": "ops"})
    rec = json.loads(buf.getvalue().strip())
    assert (
        rec["level"] == "INFO"
        and rec["tenant"] == "ops"
        and "trace_id" in rec
        and "NW-12345" not in rec["message"]
    )
    assert isinstance(logging.getLogger("atlas").handlers[0].formatter, JsonFormatter)


def test_langfuse_helpers_noop_without_keys():
    from telemetry import langfuse_setup as lf

    assert lf.init_langfuse(Settings.from_env({})) is None and not lf.langfuse_enabled()
    assert lf.setup_langfuse(None, Settings.from_env({})) is None
    lf.score_current_trace("x", 1.0)
    assert lf.create_score("t", "x", 1.0) is False
    assert lf.get_prompt_text("atlas-system", fallback="fb") == ("fb", None)
    assert lf.push_prompts({"v1": "a"}) == 0
    with lf.trace_attributes(session_id="s", user_id="u", tags=["a"]):
        pass
    lf.flush()
    lf.shutdown()


def test_langsmith_and_openinference_guards():
    from telemetry import langsmith_setup as ls
    from telemetry import openinference_setup as oi

    assert not ls.langsmith_enabled()
    assert (
        ls.traced("x")(lambda: 1)() == 1
        and ls.wrap_openai_if_enabled("client") == "client"
        and ls.send_feedback("r", "k", 1.0) is False
    )
    tp, _ = _provider()
    assert oi.setup_openinference(tp) is oi.is_instrumented()
    oi.uninstrument_openai()
    assert not oi.is_instrumented()
