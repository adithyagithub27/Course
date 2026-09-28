"""Atlas tools with OpenAI function schemas and an in-memory ticket store.

Every tool returns a JSON string (what the model sees) plus an ``ok`` flag via
:func:`execute_tool`. ``reset_password`` refuses to act unless ``verified`` is
true — the guardrail the course keeps coming back to.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.knowledge import KnowledgeBase, get_kb

TICKET_RE = re.compile(r"\bTCK-\d{6}\b")
SHIPMENT_RE = re.compile(r"\bSHP-\d{6,8}\b")
EMPLOYEE_RE = re.compile(r"\bNW-\d{5}\b")

TOOL_NAMES: tuple[str, ...] = (
    "search_knowledge_base",
    "lookup_ticket",
    "create_ticket",
    "reset_password",
    "check_shipment",
)

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search Northwind IT/HR policy articles. Use before answering any policy or how-to question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms"},
                    "top_k": {"type": "integer", "description": "Number of articles", "default": 4},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_ticket",
            "description": "Get the status of an existing helpdesk ticket by id (TCK-123456).",
            "parameters": {
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a helpdesk ticket for something Atlas cannot resolve directly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [
                            "Hardware",
                            "Software",
                            "Network",
                            "Access",
                            "HR",
                            "Payroll",
                            "Security",
                            "Other",
                        ],
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["P1", "P2", "P3", "P4"],
                        "default": "P3",
                    },
                },
                "required": ["summary", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_password",
            "description": "Reset an employee's password. Only call with verified=true after identity verification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Format NW-12345"},
                    "verified": {
                        "type": "boolean",
                        "description": "Identity verified via one-time code",
                    },
                },
                "required": ["employee_id", "verified"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_shipment",
            "description": "Check the status of an internal shipment by tracking id (SHP-123456).",
            "parameters": {
                "type": "object",
                "properties": {"tracking_id": {"type": "string"}},
                "required": ["tracking_id"],
            },
        },
    },
]

_STATUSES = ("open", "in_progress", "waiting_on_user", "resolved", "closed")
_CATEGORIES = ("Hardware", "Software", "Network", "Access", "HR", "Payroll", "Security", "Other")
_SHIPMENT_STATUSES = (
    "created",
    "in_transit",
    "at_hub",
    "out_for_delivery",
    "delivered",
    "exception",
)
_HUBS = ("Rotterdam", "Hamburg", "Lyon", "Milan", "Warsaw")


def _h(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest()[:8], 16)


@dataclass
class Ticket:
    ticket_id: str
    summary: str
    category: str
    priority: str
    status: str
    requester: str
    tenant: str
    created_at: str = "2026-09-14T08:00:00Z"
    updates: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "summary": self.summary,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "requester": self.requester,
            "tenant": self.tenant,
            "created_at": self.created_at,
            "updates": list(self.updates),
        }


class TicketStore:
    """In-memory tickets, pre-seeded deterministically so demos have data."""

    def __init__(self, seed_count: int = 40) -> None:
        self._tickets: dict[str, Ticket] = {}
        self._next = 100_001 + seed_count
        self.flaky_calls = 0  # used by the ``ticket_flaky`` scenario
        for i in range(seed_count):
            tid = f"TCK-{100_001 + i}"
            h = _h(tid)
            self._tickets[tid] = Ticket(
                ticket_id=tid,
                summary=[
                    "VPN drops every 10 minutes",
                    "Laptop screen flickering",
                    "Cannot open payslip in Workday",
                    "Need Tableau licence",
                    "Badge not working at Hamburg gate",
                    "Expense claim rejected without reason",
                    "Forklift licence renewal",
                    "Okta Verify not sending push",
                ][h % 8],
                category=_CATEGORIES[h % len(_CATEGORIES)],
                priority=f"P{1 + (h >> 3) % 4}",
                status=_STATUSES[(h >> 5) % len(_STATUSES)],
                requester=f"NW-{10_000 + (h >> 7) % 90_000:05d}",
                tenant=("ops", "finance", "hr", "eng")[(h >> 9) % 4],
            )

    def get(self, ticket_id: str) -> Ticket | None:
        return self._tickets.get(ticket_id.strip().upper())

    def create(
        self, *, summary: str, category: str, priority: str, requester: str, tenant: str
    ) -> Ticket:
        tid = f"TCK-{self._next}"
        self._next += 1
        t = Ticket(tid, summary, category, priority, "open", requester, tenant)
        self._tickets[tid] = t
        return t

    def __len__(self) -> int:
        return len(self._tickets)

    def ids(self) -> list[str]:
        return sorted(self._tickets)


@dataclass
class ToolContext:
    """Per-request context handed to tools."""

    kb: KnowledgeBase
    tickets: TicketStore
    tenant: str = "unknown"
    user_id: str = "anonymous"
    top_k: int = 4
    min_score: float = 0.5
    scenario: str | None = None
    full_text: bool = False  # return whole articles instead of snippets (context bloat!)


@dataclass(frozen=True)
class ToolResult:
    name: str
    ok: bool
    content: str  # JSON string for the model
    data: dict[str, Any]


def search_knowledge_base(ctx: ToolContext, query: str, top_k: int | None = None) -> ToolResult:
    k = int(top_k or ctx.top_k)
    # context_bloat: someone "improved recall" by dropping the relevance floor and raising top_k
    min_score = 0.0 if ctx.scenario == "context_bloat" else ctx.min_score
    hits = ctx.kb.search(query, top_k=k, min_score=min_score)
    items = []
    from app.knowledge import tokenize

    q_tokens = tokenize(query)
    for h in hits:
        d = h.as_dict()
        if ctx.full_text or ctx.scenario == "context_bloat":
            art = ctx.kb.get(h.doc_id)
            d["content"] = art.text if art else h.snippet
        else:
            d["content"] = ctx.kb.chunk(h.doc_id, q_tokens)  # ~500-token passage, like a RAG chunk
        items.append(d)
    data = {"query": query, "top_k": k, "results": items, "count": len(items)}
    return ToolResult("search_knowledge_base", True, json.dumps(data, ensure_ascii=False), data)


def lookup_ticket(ctx: ToolContext, ticket_id: str) -> ToolResult:
    if ctx.scenario == "loop":
        data = {"error": "ticket_service_unavailable", "ticket_id": ticket_id, "retry": True}
        return ToolResult("lookup_ticket", False, json.dumps(data), data)
    if ctx.scenario == "ticket_flaky":
        # two timeouts, then success: the retry-storm demo for tools
        ctx.tickets.flaky_calls += 1
        if ctx.tickets.flaky_calls % 3 != 0:
            data = {"error": "ticket_service_timeout", "ticket_id": ticket_id, "retry": True}
            return ToolResult("lookup_ticket", False, json.dumps(data), data)
    if not TICKET_RE.fullmatch(ticket_id.strip().upper()):
        data = {"error": "invalid_ticket_id", "ticket_id": ticket_id}
        return ToolResult("lookup_ticket", False, json.dumps(data), data)
    t = ctx.tickets.get(ticket_id)
    if t is None:
        data = {"error": "not_found", "ticket_id": ticket_id}
        return ToolResult("lookup_ticket", False, json.dumps(data), data)
    return ToolResult("lookup_ticket", True, json.dumps(t.as_dict()), t.as_dict())


def create_ticket(
    ctx: ToolContext, summary: str, category: str, priority: str = "P3"
) -> ToolResult:
    if category not in _CATEGORIES:
        category = "Other"
    if priority not in {"P1", "P2", "P3", "P4"}:
        priority = "P3"
    t = ctx.tickets.create(
        summary=summary[:200],
        category=category,
        priority=priority,
        requester=ctx.user_id,
        tenant=ctx.tenant,
    )
    data = {"created": True, **t.as_dict()}
    return ToolResult("create_ticket", True, json.dumps(data), data)


def reset_password(ctx: ToolContext, employee_id: str, verified: bool = False) -> ToolResult:
    if not EMPLOYEE_RE.fullmatch(employee_id.strip().upper()):
        data = {"error": "invalid_employee_id", "employee_id": employee_id}
        return ToolResult("reset_password", False, json.dumps(data), data)
    if not verified:
        data = {
            "status": "verification_required",
            "employee_id": employee_id,
            "message": "Send the one-time code to the registered phone and confirm before resetting.",
        }
        return ToolResult("reset_password", True, json.dumps(data), data)
    data = {
        "status": "reset",
        "employee_id": employee_id,
        "delivery": "temporary password sent by SMS to the registered phone",
        "must_change_at_login": True,
    }
    return ToolResult("reset_password", True, json.dumps(data), data)


def check_shipment(ctx: ToolContext, tracking_id: str) -> ToolResult:
    tid = tracking_id.strip().upper()
    if not SHIPMENT_RE.fullmatch(tid):
        data = {"error": "invalid_tracking_id", "tracking_id": tracking_id}
        return ToolResult("check_shipment", False, json.dumps(data), data)
    h = _h(tid)
    status = _SHIPMENT_STATUSES[h % len(_SHIPMENT_STATUSES)]
    data = {
        "tracking_id": tid,
        "status": status,
        "hub": _HUBS[(h >> 4) % len(_HUBS)],
        "eta": f"2026-09-{15 + (h >> 8) % 10:02d}",
        "exception_reason": ("customs_hold", "address_issue", "damaged")[(h >> 12) % 3]
        if status == "exception"
        else None,
    }
    return ToolResult("check_shipment", True, json.dumps(data), data)


_DISPATCH = {
    "search_knowledge_base": search_knowledge_base,
    "lookup_ticket": lookup_ticket,
    "create_ticket": create_ticket,
    "reset_password": reset_password,
    "check_shipment": check_shipment,
}


class UnknownToolError(KeyError):
    pass


def execute_tool(name: str, arguments: dict[str, Any] | str, ctx: ToolContext) -> ToolResult:
    """Dispatch by name; bad JSON or bad arguments become an error *result*, not an exception."""
    fn = _DISPATCH.get(name)
    if fn is None:
        raise UnknownToolError(name)
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            data = {"error": "invalid_arguments", "raw": arguments[:200]}
            return ToolResult(name, False, json.dumps(data), data)
    try:
        return fn(ctx, **arguments)  # type: ignore[arg-type]
    except TypeError as exc:
        data = {"error": "bad_arguments", "detail": str(exc)[:200]}
        return ToolResult(name, False, json.dumps(data), data)


def default_context(**overrides: Any) -> ToolContext:
    return ToolContext(kb=get_kb(), tickets=TicketStore(), **overrides)
