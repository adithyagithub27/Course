"""Deterministic offline LLM that returns real ``openai`` response objects.

Why a mock and not a stub: the agent loop, the streaming/TTFT code, the token
accounting and the cost math all run unchanged against it, so every lab has an
offline path with realistic numbers.

Scenario hooks (``scenario=`` at construction or per call):

* ``loop``             — keeps re-calling ``lookup_ticket`` after a tool error (step limit demo)
* ``context_bloat``    — long-winded answers; tools return whole articles (see ``app.tools``)
* ``retry_storm``      — the first N attempts of every call time out (``APITimeoutError``)
* ``slow_provider``    — TTFT x3.5, tokens/s halved
* ``prompt_regression``— answers drop citations and next steps (also triggered by the v2 prompt)

Latency is *simulated*: the response carries ``simulated_ttft_ms`` and
``simulated_latency_ms``; with ``latency_scale > 0`` the mock also sleeps that
fraction of it so streaming demos feel real.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx
import openai
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageFunctionToolCall,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.chat.chat_completion_message_function_tool_call import Function
from openai.types.completion_usage import (
    CompletionTokensDetails,
    CompletionUsage,
    PromptTokensDetails,
)

from app.prompts import V2_MARKER
from app.tools import EMPLOYEE_RE, SHIPMENT_RE, TICKET_RE
from northwind.tokens import approx_tokens, count_message_tokens, count_tool_schema_tokens

#: Per-model simulated latency: TTFT base (ms) and time per output token (ms).
LATENCY_PROFILE: dict[str, tuple[float, float]] = {
    "gpt-4.1-nano": (220.0, 5.0),
    "gpt-4.1-mini": (380.0, 7.5),
    "gpt-4.1": (650.0, 14.0),
    "gpt-5-mini": (900.0, 12.0),
    "gpt-4o-mini": (350.0, 8.0),
}
CACHE_MIN_PREFIX = 1024  # OpenAI caches prefixes of at least 1024 tokens, in 128-token blocks

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "injection": (
        "ignore previous instructions",
        "ignore all previous",
        "system prompt",
        "reveal your instructions",
        "you are now",
        "developer mode",
    ),
    "escalation": (
        "grievance",
        "harassment",
        "disciplinary",
        "legal",
        "lawyer",
        "immigration",
        "visa",
        "discrimination",
        "bullying",
    ),
    "password_reset": (
        "reset my password",
        "password reset",
        "locked out",
        "forgot my password",
        "reset password",
        "account locked",
    ),
    "ticket_status": (
        "status of my ticket",
        "ticket status",
        "my ticket",
        "update on tck",
        "what happened to tck",
    ),
    "create_ticket": (
        "open a ticket",
        "create a ticket",
        "raise a ticket",
        "log a ticket",
        "file a ticket",
        "broken",
        "not working",
        "flickering",
        "won't turn on",
    ),
    "shipment": (
        "shipment",
        "tracking",
        "shp-",
        "delivery status",
        "where is my parcel",
        "where is the package",
    ),
    "vpn": ("vpn", "globalprotect", "remote access", "gateway unreachable"),
    "leave": (
        "annual leave",
        "vacation",
        "holiday",
        "sick leave",
        "day off",
        "pto",
        "leave balance",
        "carry over",
        "bereavement",
    ),
    "expenses": ("expense", "reimburse", "receipt", "per diem", "concur", "mileage", "hotel limit"),
    "payroll": (
        "payslip",
        "payroll",
        "salary",
        "paid on",
        "bonus",
        "tax statement",
        "bank details",
    ),
    "laptop": (
        "laptop",
        "hardware",
        "monitor",
        "dock",
        "headset",
        "replacement",
        "lost my",
        "stolen",
    ),
    "onboarding": ("onboarding", "new joiner", "first day", "new hire", "starter"),
    "benefits": (
        "pension",
        "health insurance",
        "benefit",
        "commut",
        "bike",
        "learning budget",
        "counselling",
    ),
    "software": ("licence", "license", "install", "software", "tableau", "adobe", "admin rights"),
    "security": (
        "phishing",
        "suspicious email",
        "malware",
        "security incident",
        "clicked a link",
        "badge",
    ),
    "remote_work": ("work from home", "remote work", "hybrid", "abroad", "home office"),
    "safety": ("forklift", "safety", "ppe", "near miss", "injur", "cold store"),
    "smalltalk": ("hello", "hi atlas", "thank you", "thanks", "good morning", "who are you"),
}


#: Features (the finance-facing grouping) that intents roll up into.
FEATURES: tuple[str, ...] = (
    "policy_question",
    "ticket_lookup",
    "create_ticket",
    "password_reset",
    "shipment_status",
    "escalation",
    "other",
)
_INTENT_TO_FEATURE: dict[str, str] = {
    "ticket_status": "ticket_lookup",
    "create_ticket": "create_ticket",
    "password_reset": "password_reset",
    "shipment": "shipment_status",
    "escalation": "escalation",
    "smalltalk": "other",
    "injection": "other",
}


def feature_for_intent(intent: str) -> str:
    """Map a fine-grained intent to one of :data:`FEATURES` (policy questions are the default)."""
    return _INTENT_TO_FEATURE.get(intent, "policy_question")


#: Intents cheap enough for the small model when routing is on (Section 6.6).
SIMPLE_INTENTS: frozenset[str] = frozenset(
    {"smalltalk", "ticket_status", "shipment", "create_ticket"}
)


def classify_intent(text: str) -> str:
    """Keyword intent classifier shared by the mock LLM, the simulator and the judge."""
    t = text.lower()
    if TICKET_RE.search(text) and "create" not in t and "open a" not in t:
        return "ticket_status"
    if SHIPMENT_RE.search(text):
        return "shipment"
    for intent, kws in INTENT_KEYWORDS.items():
        if any(k in t for k in kws):
            return intent
    return "general"


_INJECTION_RE = re.compile(
    r"(ignore (all |the )?(previous|prior|above) instructions|reveal (your|the) (system )?(prompt|instructions)|"
    r"you are now (dan|in developer mode)|print (all|every) (password|employee)|"
    r"disregard (your|all) (rules|instructions))",
    re.IGNORECASE,
)


def looks_like_injection(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))


@dataclass
class MockStats:
    calls: int = 0
    stream_calls: int = 0
    failures_raised: int = 0
    tool_calls: int = 0
    per_model: dict[str, int] = field(default_factory=dict)


def _rng(*parts: Any) -> random.Random:
    key = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return random.Random(int(key[:16], 16))


def _content(m: dict[str, Any]) -> str:
    c = m.get("content")
    if isinstance(c, list):
        return " ".join(str(p.get("text", "")) for p in c if isinstance(p, dict))
    return c or ""


def _last_user(messages: list[dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return _content(m)
    return ""


def _system_text(messages: list[dict[str, Any]]) -> str:
    return "\n".join(_content(m) for m in messages if m.get("role") == "system")


def _tool_name_for(messages: list[dict[str, Any]], tool_call_id: str | None) -> str | None:
    for m in reversed(messages):
        if m.get("role") == "assistant":
            for tc in m.get("tool_calls") or []:
                if tool_call_id is None or tc.get("id") == tool_call_id:
                    return tc.get("function", {}).get("name")
    return None


class MockLLM:
    """OpenAI-compatible ``chat`` method with deterministic behaviour per seed."""

    def __init__(
        self,
        *,
        seed: int = 0,
        scenario: str | None = None,
        latency_scale: float = 0.0,
        retry_storm_failures: int = 2,
    ) -> None:
        self.seed = seed
        self.scenario = scenario
        self.latency_scale = latency_scale
        self.retry_storm_failures = retry_storm_failures
        self.stats = MockStats()
        self._seen_cache_keys: set[str] = set()
        self._attempts: dict[str, int] = {}
        self._call_counter = 0

    # ------------------------------------------------------------------ decisions
    def _degraded(self, messages: list[dict[str, Any]], scenario: str | None) -> bool:
        return scenario == "prompt_regression" or V2_MARKER in _system_text(messages)

    def _decide(
        self, messages: list[dict[str, Any]], model: str, scenario: str | None, rng: random.Random
    ) -> tuple[str | None, list[tuple[str, dict[str, Any]]]]:
        """Return (content, tool_calls). Exactly one of them is non-empty."""
        last = messages[-1]
        user_text = _last_user(messages)
        intent = classify_intent(user_text)
        degraded = self._degraded(messages, scenario)
        verbose = scenario == "context_bloat"

        if last.get("role") == "tool":
            name = _tool_name_for(messages, last.get("tool_call_id"))
            try:
                data = json.loads(_content(last) or "{}")
            except json.JSONDecodeError:
                data = {}
            return self._after_tool(
                name, data, intent, user_text, degraded, verbose, scenario, rng
            ), []

        if intent == "injection":
            return (
                "I can't help with that request. I can help with IT access, hardware, HR policy, "
                "tickets and shipment status.",
                [],
            )
        if intent == "smalltalk":
            return (
                "Hello! I'm Atlas, the Northwind IT and HR helpdesk assistant. How can I help you today?",
                [],
            )
        if intent == "escalation":
            if model in {"gpt-4.1", "gpt-5-mini"}:
                return self._escalation_answer(user_text, degraded), []
            return "[ESCALATE] This needs careful handling by a person.", []
        if intent == "ticket_status":
            m = TICKET_RE.search(user_text)
            if m is None:
                ask = "I can check that for you. Which ticket do you mean? Please send the ticket id (format TCK-123456)."
                if not degraded:
                    ask += " Next step: reply with the id and I'll look it up (Source: How IT and HR tickets work)."
                return ask, []
            return None, [("lookup_ticket", {"ticket_id": m.group(0)})]
        if intent == "create_ticket":
            cat = (
                "Hardware"
                if any(k in user_text.lower() for k in ("laptop", "screen", "monitor", "dock"))
                else "Other"
            )
            return None, [
                ("create_ticket", {"summary": user_text[:120], "category": cat, "priority": "P3"})
            ]
        if intent == "password_reset":
            m = EMPLOYEE_RE.search(user_text)
            verified = (
                bool(re.search(r"\b(code|verified|confirm(ed)?)\b", user_text, re.I))
                and m is not None
            )
            return None, [
                (
                    "reset_password",
                    {"employee_id": m.group(0) if m else "NW-00000", "verified": verified},
                )
            ]
        if intent == "shipment":
            m = SHIPMENT_RE.search(user_text)
            if m is None:
                ask = "I can look that up. Which shipment? Please send the tracking id (format SHP-123456)."
                if not degraded:
                    ask += " Next step: reply with the id and I'll check the TMS (Source: Internal shipment tracking and delivery exceptions)."
                return ask, []
            return None, [("check_shipment", {"tracking_id": m.group(0)})]
        args: dict[str, Any] = {"query": user_text[:200]}
        if verbose:
            args["top_k"] = (
                20  # context_bloat: the model asks for everything; otherwise the tool's configured top_k applies
            )
        return None, [("search_knowledge_base", args)]

    def _after_tool(
        self,
        name: str | None,
        data: dict[str, Any],
        intent: str,
        user_text: str,
        degraded: bool,
        verbose: bool,
        scenario: str | None,
        rng: random.Random,
    ) -> str | list[tuple[str, dict[str, Any]]] | None:
        if name == "lookup_ticket":
            if data.get("error"):
                if data.get("retry"):
                    return (
                        None  # the tool said "retry": a naive model obliges (loop / ticket_flaky)
                    )
                return (
                    f"I couldn't find ticket {data.get('ticket_id', '')}. Please double-check the id "
                    "(format TCK-123456)."
                    + (
                        ""
                        if degraded
                        else " Next step: reply with the correct id and I'll look again."
                    )
                )
            s = data.get("status", "unknown").replace("_", " ")
            base = f'Ticket {data.get("ticket_id")} ("{data.get("summary")}") is **{s}**, priority {data.get("priority")}.'
            if degraded:
                return base
            return base + (
                " Waiting-on-user tickets close after 5 business days without a reply (Source: How IT and HR tickets work). "
                "Next step: reply on the ticket if you have new information, or tell me if you'd like me to add a note."
            )
        if name == "create_ticket":
            base = f"I've created ticket {data.get('ticket_id')} ({data.get('category')}, {data.get('priority')})."
            if degraded:
                return base
            return (
                base
                + " The service desk responds within the SLA for that priority (Source: How IT and HR tickets work). Next step: watch for the confirmation e-mail; reply here with the ticket id for updates."
            )
        if name == "reset_password":
            if data.get("status") == "verification_required":
                base = "Before I can reset your password I need to verify your identity."
                if degraded:
                    return base
                return (
                    base
                    + " I've sent a one-time code to your registered phone. Next step: reply with the code and your employee ID (NW-12345) (Source: Password reset and account lockout)."
                )
            if data.get("status") == "reset":
                base = "Your password has been reset; a temporary password was sent by SMS."
                if degraded:
                    return base
                return (
                    base
                    + " You must change it at next login (Source: Password reset and account lockout). Next step: sign in at okta.northwind.example and set a new 14+ character password."
                )
            return (
                "I couldn't reset the password: "
                + str(data.get("error", "unknown error"))
                + ("" if degraded else " Next step: check the employee ID format NW-12345.")
            )
        if name == "check_shipment":
            if data.get("error"):
                return f"I couldn't look that up: {data['error']}." + (
                    "" if degraded else " Next step: send the tracking id in the form SHP-123456."
                )
            status = str(data.get("status", "")).replace("_", " ")
            base = f"Shipment {data.get('tracking_id')} is **{status}** at the {data.get('hub')} hub, ETA {data.get('eta')}."
            if data.get("exception_reason"):
                base += f" Exception reason: {data['exception_reason'].replace('_', ' ')}."
            if degraded:
                return base
            return (
                base
                + " (Source: Internal shipment tracking and delivery exceptions). Next step: "
                + (
                    "the hub owner will update the ETA; escalate to the duty manager (ext. 5100) if the customer is waiting."
                    if data.get("exception_reason")
                    else "no action needed; I can check again later."
                )
            )
        if name == "search_knowledge_base":
            results = data.get("results") or []
            if not results:
                return "I couldn't find a policy article for that." + (
                    ""
                    if degraded
                    else " Next step: I can open a ticket with the service desk so a person can help."
                )
            top = results[0]
            passage = str(top.get("content") or top.get("snippet", ""))
            passage = re.sub(r"\s+", " ", passage.replace("#", "")).strip()
            snippet = str(top.get("snippet") or passage)[:400]
            if degraded:
                return f"{snippet.split('. ')[0]}."
            answer = (
                f"Here's what the policy says: {snippet} "
                f"In more detail: {passage[:520]} (Source: {top['title']})."
            )
            if verbose:
                extra = " ".join(str(r.get("snippet", ""))[:300] for r in results[1:6])
                answer += " For completeness, related guidance: " + extra
                answer += (
                    " I've also included the full text of the relevant articles above for reference. "
                    * 3
                )
            return answer + " Next step: " + self._next_step(intent)
        return "Done." if degraded else "Done. Next step: let me know if you need anything else."

    @staticmethod
    def _next_step(intent: str) -> str:
        return {
            "vpn": "try the steps above; if it still fails twice, tell me and I'll open a Network/VPN ticket.",
            "leave": "submit the request in Workday; your manager approves within five working days.",
            "expenses": "submit the claim in Concur within 30 days with itemised receipts.",
            "payroll": "check Workday two days before the 25th; open an HR/Payroll ticket if something is wrong.",
            "laptop": "open a Hardware ticket with your asset tag (NWL-######) if you need a replacement.",
        }.get(intent, "tell me if you'd like me to open a ticket for this.")

    @staticmethod
    def _escalation_answer(user_text: str, degraded: bool) -> str:
        base = (
            "I understand this is a sensitive matter and I want to make sure it is handled properly by a person. "
            "Northwind's HR Business Partners handle grievances, harassment, disciplinary and immigration questions "
            "confidentially."
        )
        if degraded:
            return base
        return base + (
            " (Source: How IT and HR tickets work). Next step: I can create a confidential HR ticket (P2) so an HR "
            "Business Partner contacts you within one business day; reply 'yes' and I'll raise it."
        )

    # ------------------------------------------------------------------ usage/latency
    def _usage(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        model: str,
        output_text: str,
        prompt_cache_key: str | None,
    ) -> CompletionUsage:
        tool_tokens = count_tool_schema_tokens(tools) if tools else 0
        prompt = count_message_tokens(messages) + tool_tokens
        prefix = (
            sum(approx_tokens(_content(m)) for m in messages if m.get("role") == "system")
            + tool_tokens
        )
        cached = 0
        if prompt_cache_key:
            if prompt_cache_key in self._seen_cache_keys and prefix >= CACHE_MIN_PREFIX:
                cached = (prefix // 128) * 128
            self._seen_cache_keys.add(prompt_cache_key)
        completion = approx_tokens(output_text) + 4
        reasoning = completion * 2 if model.startswith("gpt-5") else 0
        completion += reasoning
        return CompletionUsage(
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=prompt + completion,
            prompt_tokens_details=PromptTokensDetails(cached_tokens=cached),
            completion_tokens_details=CompletionTokensDetails(reasoning_tokens=reasoning),
        )

    def _latency(
        self, model: str, usage: CompletionUsage, scenario: str | None, rng: random.Random
    ) -> tuple[float, float]:
        base_ttft, tpot = LATENCY_PROFILE.get(model, (500.0, 15.0))
        ttft = (
            base_ttft * (0.75 + 0.5 * rng.random()) + usage.prompt_tokens * 0.02
        )  # long prompts: slower TTFT
        per_tok = tpot * (0.9 + 0.2 * rng.random())
        if scenario == "slow_provider":
            ttft *= 3.5
            per_tok *= 2.0
        total = ttft + usage.completion_tokens * per_tok
        return round(ttft, 1), round(total, 1)

    def _maybe_fail(self, messages: list[dict[str, Any]], scenario: str | None, model: str) -> None:
        if scenario != "retry_storm":
            return
        key = hashlib.sha256(
            (_last_user(messages) + str(len(messages)) + model).encode()
        ).hexdigest()
        n = self._attempts.get(key, 0)
        self._attempts[key] = n + 1
        if n < self.retry_storm_failures:
            self.stats.failures_raised += 1
            req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            raise openai.APITimeoutError(request=req)

    # ------------------------------------------------------------------ public API
    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
        prompt_cache_key: str | None = None,
        scenario: str | None = None,
        **_ignored: Any,
    ) -> ChatCompletion | Iterator[ChatCompletionChunk]:
        """Mimics ``client.chat.completions.create``. Extra kwargs are ignored."""
        scenario = scenario or self.scenario
        self.stats.calls += 1
        self.stats.per_model[model] = self.stats.per_model.get(model, 0) + 1
        self._call_counter += 1
        rng = _rng(self.seed, model, _last_user(messages), len(messages))
        self._maybe_fail(messages, scenario, model)
        content, tool_calls = self._decide(messages, model, scenario, rng)
        if content is None and not tool_calls:
            # loop scenario: re-issue the last tool call verbatim
            name = _tool_name_for(messages, messages[-1].get("tool_call_id"))
            m = TICKET_RE.search(_last_user(messages))
            tool_calls = [
                (name or "lookup_ticket", {"ticket_id": m.group(0) if m else "TCK-000000"})
            ]
        output_text = content or json.dumps([{"name": n, "arguments": a} for n, a in tool_calls])
        usage = self._usage(messages, tools, model, output_text, prompt_cache_key)
        ttft_ms, total_ms = self._latency(model, usage, scenario, rng)
        completion_id = f"chatcmpl-mock-{self._call_counter:06d}"
        tc_objs = [
            ChatCompletionMessageFunctionToolCall(
                id=f"call_{hashlib.sha1(f'{completion_id}{i}'.encode()).hexdigest()[:10]}",
                type="function",
                function=Function(name=n, arguments=json.dumps(a)),
            )
            for i, (n, a) in enumerate(tool_calls)
        ]
        self.stats.tool_calls += len(tc_objs)
        finish = "tool_calls" if tc_objs else "stop"
        if stream:
            self.stats.stream_calls += 1
            return self._stream(
                completion_id, model, content, tc_objs, usage, finish, ttft_ms, total_ms
            )
        if self.latency_scale > 0:
            time.sleep(total_ms / 1000.0 * self.latency_scale)
        msg = ChatCompletionMessage(role="assistant", content=content, tool_calls=tc_objs or None)
        return ChatCompletion(
            id=completion_id,
            created=1_758_000_000 + self._call_counter,
            model=f"{model}-2025-04-14" if model.startswith("gpt-4.1") else model,
            object="chat.completion",
            choices=[Choice(index=0, finish_reason=finish, message=msg)],
            usage=usage,
            simulated_ttft_ms=ttft_ms,
            simulated_latency_ms=total_ms,
        )

    def _stream(
        self,
        completion_id: str,
        model: str,
        content: str | None,
        tool_calls: list[ChatCompletionMessageFunctionToolCall],
        usage: CompletionUsage,
        finish: str,
        ttft_ms: float,
        total_ms: float,
    ) -> Iterator[ChatCompletionChunk]:
        resp_model = f"{model}-2025-04-14" if model.startswith("gpt-4.1") else model
        created = 1_758_000_000 + self._call_counter

        def chunk(
            delta: ChoiceDelta, finish_reason: str | None = None, with_usage: bool = False
        ) -> ChatCompletionChunk:
            return ChatCompletionChunk(
                id=completion_id,
                created=created,
                model=resp_model,
                object="chat.completion.chunk",
                choices=[ChunkChoice(index=0, delta=delta, finish_reason=finish_reason)],
                usage=usage if with_usage else None,
                simulated_ttft_ms=ttft_ms,
                simulated_latency_ms=total_ms,
            )

        if self.latency_scale > 0:
            time.sleep(ttft_ms / 1000.0 * self.latency_scale)
        if tool_calls:
            deltas = [
                {
                    "index": i,
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for i, tc in enumerate(tool_calls)
            ]
            yield chunk(ChoiceDelta(role="assistant", tool_calls=deltas))  # type: ignore[arg-type]
        else:
            words = (content or "").split(" ")
            yield chunk(ChoiceDelta(role="assistant", content=""))
            pieces = [" ".join(words[i : i + 4]) for i in range(0, len(words), 4)]
            per_piece = (total_ms - ttft_ms) / max(len(pieces), 1) / 1000.0 * self.latency_scale
            for i, piece in enumerate(pieces):
                if per_piece > 0:
                    time.sleep(per_piece)
                yield chunk(ChoiceDelta(content=(" " if i else "") + piece))
        yield chunk(ChoiceDelta(), finish_reason=finish)
        yield chunk(ChoiceDelta(), with_usage=True)


def make_rate_limit_error() -> openai.RateLimitError:
    """Helper for tests and chaos demos."""
    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    resp = httpx.Response(429, request=req, headers={"retry-after": "1"})
    return openai.RateLimitError("Rate limit exceeded", response=resp, body=None)
