"""
MockOpenAI: a deterministic, offline stand-in for ``openai.OpenAI``.

It implements ``client.chat.completions.create(...)`` and returns real
``openai.types.chat.ChatCompletion`` objects, so the agents run unchanged.
Behaviour is scripted per agent in ``agents/mock_brains.py``: each "brain"
reads the system prompt, the conversation and the tool results so far and
decides the next step (tool calls or a final answer), the way a real model
would, but with fixed rules.

Determinism:
* temperature == 0          -> always the first phrasing.
* temperature None or > 0   -> one of several correct phrasings, picked by a
  seeded RNG from (prompt, call number). Same inputs in the same order give
  the same outputs on every machine, but repeated calls vary like a real model.
* usage = len(text) // 4 per message (close to tiktoken for English).
* latency is simulated and added to a virtual clock (see agents/llm.py).
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from openai.types.chat import ChatCompletion


@dataclass
class Ctx:
    """Everything a brain may look at for one call."""

    system: str
    messages: list[dict]
    tools: list[dict]
    temperature: float | None
    response_format: dict | None
    rng: random.Random
    model: str

    @property
    def tool_names(self) -> list[str]:
        return [t["function"]["name"] for t in self.tools or []]

    @property
    def user_messages(self) -> list[str]:
        return [m.get("content") or "" for m in self.messages if m.get("role") == "user"]

    @property
    def last_user(self) -> str:
        users = self.user_messages
        return users[-1] if users else ""

    @property
    def turn_tool_results(self) -> list[tuple[str, dict, str]]:
        """(tool, args, result) for tool calls made since the last user message."""
        idx = max(i for i, m in enumerate(self.messages) if m.get("role") in ("user", "system"))
        calls: dict[str, tuple[str, dict]] = {}
        out: list[tuple[str, dict, str]] = []
        for m in self.messages[idx + 1 :]:
            if m.get("role") == "assistant":
                for tc in m.get("tool_calls") or []:
                    fn = tc["function"]
                    calls[tc["id"]] = (fn["name"], json.loads(fn["arguments"] or "{}"))
            elif m.get("role") == "tool":
                name, args = calls.get(m.get("tool_call_id"), ("?", {}))
                out.append((name, args, m.get("content") or ""))
        return out

    def say(self, *variants: str) -> str:
        """Pick a phrasing: the first at temperature 0, else a seeded choice."""
        if self.temperature == 0 or len(variants) == 1:
            return variants[0]
        return self.rng.choice(variants)


@dataclass
class Step:
    """A brain's decision: tool calls, or final text."""

    text: str | None = None
    tool_calls: list[tuple[str, dict]] = field(default_factory=list)


def tool(name: str, **args: Any) -> Step:
    return Step(tool_calls=[(name, args)])


def tools(*calls: tuple[str, dict]) -> Step:
    return Step(tool_calls=list(calls))


def final(text: str) -> Step:
    return Step(text=text)


def _normalise(messages: list[Any]) -> list[dict]:
    out = []
    for m in messages:
        if hasattr(m, "model_dump"):
            m = m.model_dump(exclude_none=True)
        out.append(dict(m))
    return out


def _tokens(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


class _Completions:
    def __init__(self, owner: MockOpenAI) -> None:
        self._owner = owner

    def create(self, *, model: str, messages: list[Any], **kwargs: Any) -> ChatCompletion:
        return self._owner._create(model=model, messages=messages, **kwargs)


class _Chat:
    def __init__(self, owner: MockOpenAI) -> None:
        self.completions = _Completions(owner)


class MockOpenAI:
    """Drop-in for ``openai.OpenAI`` with scripted, deterministic answers."""

    def __init__(self, clock: Any = None, seed: int = 7) -> None:
        self.chat = _Chat(self)
        self.clock = clock
        self.seed = seed
        self.calls: list[dict] = []  # every request, for tests and demos
        self._per_prompt: dict[str, int] = defaultdict(int)

    # ---- internals --------------------------------------------------------
    def _create(
        self,
        *,
        model: str,
        messages: list[Any],
        tools: list[dict] | None = None,
        temperature: float | None = None,
        response_format: dict | None = None,
        **_: Any,
    ) -> ChatCompletion:
        from agents.mock_brains import route

        msgs = _normalise(messages)
        system = next((m.get("content") or "" for m in msgs if m.get("role") == "system"), "")
        key = hashlib.sha256(json.dumps(msgs, sort_keys=True, default=str).encode()).hexdigest()
        n = self._per_prompt[key]
        self._per_prompt[key] += 1
        rng = random.Random(f"{self.seed}:{key}:{n}")
        ctx = Ctx(
            system=system,
            messages=msgs,
            tools=tools or [],
            temperature=temperature,
            response_format=response_format,
            rng=rng,
            model=model,
        )
        step = route(ctx)
        self.calls.append({"model": model, "messages": msgs, "tools": [t["function"]["name"] for t in tools or []], "step": step})

        prompt_text = json.dumps(msgs, default=str) + (json.dumps(tools) if tools else "")
        prompt_tokens = _tokens(prompt_text)
        if step.tool_calls:
            tc = [
                {
                    "id": f"call_{hashlib.md5(f'{key}{n}{i}'.encode()).hexdigest()[:12]}",
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(args)},
                }
                for i, (name, args) in enumerate(step.tool_calls)
            ]
            message = {"role": "assistant", "content": None, "tool_calls": tc}
            finish = "tool_calls"
            completion_tokens = _tokens(json.dumps(tc))
        else:
            message = {"role": "assistant", "content": step.text or ""}
            finish = "stop"
            completion_tokens = _tokens(step.text or "")

        if self.clock is not None:
            jitter = int(key[:4], 16) / 0xFFFF * 0.25
            self.clock.advance(0.30 + prompt_tokens * 0.00002 + completion_tokens * 0.012 + jitter)

        return ChatCompletion.model_validate(
            {
                "id": f"chatcmpl-mock-{key[:10]}-{n}",
                "object": "chat.completion",
                "created": 1_790_000_000,
                "model": model,
                "choices": [{"index": 0, "message": message, "finish_reason": finish, "logprobs": None}],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
        )


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
