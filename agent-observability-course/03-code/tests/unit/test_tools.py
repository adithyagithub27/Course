import json

import pytest

from app.tools import (
    TOOL_NAMES,
    TOOL_SCHEMAS,
    TicketStore,
    ToolContext,
    UnknownToolError,
    check_shipment,
    create_ticket,
    default_context,
    execute_tool,
    lookup_ticket,
    reset_password,
    search_knowledge_base,
)


def test_schemas_match_tool_names():
    names = [t["function"]["name"] for t in TOOL_SCHEMAS]
    assert tuple(names) == TOOL_NAMES
    for t in TOOL_SCHEMAS:
        assert t["type"] == "function" and "parameters" in t["function"]


def test_ticket_store_seeded_and_deterministic():
    a, b = TicketStore(), TicketStore()
    assert len(a) == 40 and a.ids() == b.ids()
    assert a.get("TCK-100001").as_dict() == b.get("TCK-100001").as_dict()
    assert a.get("tck-100001") is not None


def test_lookup_ticket_paths():
    ctx = default_context()
    assert lookup_ticket(ctx, "TCK-100001").ok
    assert lookup_ticket(ctx, "TCK-999999").data["error"] == "not_found"
    assert lookup_ticket(ctx, "banana").data["error"] == "invalid_ticket_id"


def test_lookup_ticket_loop_and_flaky_scenarios():
    ctx = default_context(scenario="loop")
    r = lookup_ticket(ctx, "TCK-100001")
    assert not r.ok and r.data["retry"] is True
    ctx = default_context(scenario="ticket_flaky")
    results = [lookup_ticket(ctx, "TCK-100001").ok for _ in range(6)]
    assert results == [False, False, True, False, False, True]


def test_create_ticket_assigns_sequential_ids_and_defaults():
    ctx = default_context(tenant="eng", user_id="NW-11111")
    t1 = create_ticket(ctx, "screen flickering", "Hardware")
    t2 = create_ticket(ctx, "weird", "NotACategory", priority="P9")
    assert t1.data["ticket_id"] == "TCK-100041" and t2.data["ticket_id"] == "TCK-100042"
    assert t2.data["category"] == "Other" and t2.data["priority"] == "P3"
    assert t1.data["requester"] == "NW-11111" and t1.data["tenant"] == "eng"
    assert ctx.tickets.get("TCK-100041").status == "open"


def test_reset_password_requires_verification():
    ctx = default_context()
    r = reset_password(ctx, "NW-12345", verified=False)
    assert r.ok and r.data["status"] == "verification_required"
    r = reset_password(ctx, "NW-12345", verified=True)
    assert r.data["status"] == "reset" and r.data["must_change_at_login"] is True
    assert "password" not in json.dumps(r.data).lower().replace("password has", "").replace(
        "temporary password", ""
    )
    assert not reset_password(ctx, "12345", True).ok


def test_check_shipment_deterministic():
    ctx = default_context()
    a, b = check_shipment(ctx, "SHP-123456"), check_shipment(ctx, "shp-123456")
    assert (
        a.ok
        and a.data == b.data
        and a.data["status"]
        in {"created", "in_transit", "at_hub", "out_for_delivery", "delivered", "exception"}
    )
    assert not check_shipment(ctx, "SHP-12").ok


def test_search_knowledge_base_returns_chunks_and_bloat_mode():
    ctx = default_context(top_k=4)
    r = search_knowledge_base(ctx, "hotel limit expenses")
    assert r.ok and r.data["count"] >= 1 and all("content" in x for x in r.data["results"])
    bloat = search_knowledge_base(
        default_context(top_k=12, scenario="context_bloat"), "hotel limit expenses"
    )
    assert bloat.data["count"] > r.data["count"] and len(bloat.content) > len(r.content)


def test_execute_tool_dispatch_and_errors():
    ctx = default_context()
    assert execute_tool("lookup_ticket", '{"ticket_id": "TCK-100002"}', ctx).ok
    assert execute_tool("lookup_ticket", "{not json", ctx).data["error"] == "invalid_arguments"
    assert execute_tool("lookup_ticket", {"wrong": 1}, ctx).data["error"] == "bad_arguments"
    with pytest.raises(UnknownToolError):
        execute_tool("launch_rocket", {}, ctx)


def test_tool_context_defaults():
    ctx = ToolContext(kb=default_context().kb, tickets=TicketStore())
    assert ctx.tenant == "unknown" and ctx.top_k == 4 and ctx.min_score == 0.5
