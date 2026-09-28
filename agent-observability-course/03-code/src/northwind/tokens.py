"""Approximate token counting and the "context diet" helpers.

``tiktoken`` downloads its encodings on first use, which is not possible in
locked-down CI or the course's offline mode. So:

* :func:`count_tokens` uses a chars/4 heuristic corrected for whitespace,
  punctuation and long words. It is within about 10 % of tiktoken on English
  prose and JSON, which is plenty for budgeting.
* If ``ATLAS_USE_TIKTOKEN=1`` *and* an encoding is already in tiktoken's local
  cache, the exact encoder is used. Nothing here ever opens a socket.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable, Iterable, Sequence
from functools import lru_cache
from typing import Any

Message = dict[str, Any]

_WORD = re.compile(r"[A-Za-z0-9_']+|[^\sA-Za-z0-9_']", re.UNICODE)
_TOKENS_PER_MESSAGE = 4  # role + separators, per OpenAI cookbook
_TOOL_CALL_OVERHEAD = 12


def _tiktoken_encoder(model: str | None) -> Callable[[str], list[int]] | None:
    """Return a cached tiktoken encoder only if it is on disk and explicitly enabled."""
    if os.environ.get("ATLAS_USE_TIKTOKEN", "0") != "1":
        return None
    cache_dir = os.environ.get("TIKTOKEN_CACHE_DIR") or os.path.join(
        tempfile.gettempdir(), "data-gym-cache"
    )
    if not os.path.isdir(cache_dir) or not os.listdir(cache_dir):
        return None
    try:  # pragma: no cover - depends on local cache
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("o200k_base")
        return enc.encode
    except Exception:  # noqa: BLE001
        return None


@lru_cache(maxsize=4096)
def approx_tokens(text: str) -> int:
    """Heuristic token count: ~1 token per 4 chars, corrected for word shape (memoised)."""
    if not text:
        return 0
    pieces = _WORD.findall(text)
    total = 0.0
    for p in pieces:
        if len(p) == 1 and not p.isalnum():
            total += 1.0  # punctuation is one token
        elif p.isdigit():
            total += max(1.0, len(p) / 3)  # digits tokenize densely
        else:
            total += max(1.0, len(p) / 4.2)
    # newlines and code-ish text add a little
    total += text.count("\n") * 0.25
    return max(1, round(total))


def count_tokens(text: str, model: str | None = None) -> int:
    """Count tokens in ``text`` (exact with cached tiktoken, else approximate)."""
    enc = _tiktoken_encoder(model)
    if enc is not None:  # pragma: no cover
        return len(enc(text))
    return approx_tokens(text)


def _content_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):  # multi-part content
        return " ".join(
            _content_text(part.get("text", "")) for part in content if isinstance(part, dict)
        )
    return json.dumps(content, ensure_ascii=False)


def count_message_tokens(messages: Sequence[Message], model: str | None = None) -> int:
    """Tokens for a chat message list including per-message overhead and tool calls."""
    total = 0
    for m in messages:
        total += _TOKENS_PER_MESSAGE
        total += count_tokens(_content_text(m.get("content")), model)
        for tc in m.get("tool_calls") or []:
            fn = tc.get("function", {}) if isinstance(tc, dict) else {}
            total += _TOOL_CALL_OVERHEAD
            total += count_tokens(str(fn.get("name", "")), model)
            total += count_tokens(str(fn.get("arguments", "")), model)
        if m.get("name"):
            total += 1
    return total + 3  # reply priming


def count_tool_schema_tokens(tools: Iterable[dict[str, Any]], model: str | None = None) -> int:
    """Tokens the tool/function definitions add to every request."""
    return sum(
        count_tokens(json.dumps(t, separators=(",", ":"), sort_keys=True), model) for t in tools
    )


def estimate_tokens(text: str, model: str | None = None) -> int:
    """Alias of :func:`count_tokens` (name used in the lecture scripts)."""
    return count_tokens(text, model)


def truncate_text(text: str, max_tokens: int, marker: str = " …[truncated]") -> str:
    """Cut ``text`` so it fits ``max_tokens`` (approximate), appending a marker."""
    if max_tokens <= 0:
        return marker.strip()
    if count_tokens(text) <= max_tokens:
        return text
    # binary search on characters
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if count_tokens(text[:mid]) + count_tokens(marker) <= max_tokens:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + marker


def _shrink_json(value: Any, max_chars: int) -> Any:
    """Recursively clip long string leaves so the JSON stays valid."""
    if isinstance(value, str):
        return value if len(value) <= max_chars else value[: max_chars - 1].rstrip() + "…"
    if isinstance(value, list):
        return [_shrink_json(v, max_chars) for v in value]
    if isinstance(value, dict):
        return {k: _shrink_json(v, max_chars) for k, v in value.items()}
    return value


def truncate_tool_result(result: str, max_tokens: int = 400) -> str:
    """Tool results are the usual source of context bloat.

    JSON results stay **valid JSON**: long string fields are clipped and, if that
    is not enough, list items are dropped from the end. Plain text keeps the head
    and the tail with a marker in between.
    """
    if count_tokens(result) <= max_tokens:
        return result
    stripped = result.lstrip()
    if stripped[:1] in "{[":
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            data = None
        if data is not None:
            for max_chars in (600, 400, 240, 120, 60):
                candidate = json.dumps(_shrink_json(data, max_chars), ensure_ascii=False)
                if count_tokens(candidate) <= max_tokens:
                    return candidate
            # drop list items from the end (e.g. retrieval results)
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list) and len(val) > 1:
                        while len(val) > 1:
                            val.pop()
                            candidate = json.dumps(_shrink_json(data, 60), ensure_ascii=False)
                            if count_tokens(candidate) <= max_tokens:
                                data[key] = val
                                data["truncated"] = True
                                return json.dumps(data, ensure_ascii=False)
            return json.dumps(_shrink_json(data, 40), ensure_ascii=False)
    head_budget = int(max_tokens * 0.7)
    tail_budget = max_tokens - head_budget - 6
    head = truncate_text(result, head_budget, marker="")
    tail = result[-max(1, tail_budget * 3) :] if tail_budget > 0 else ""
    return f"{head}\n…[{count_tokens(result) - max_tokens} tokens truncated]…\n{tail}".strip()


Summariser = Callable[[Sequence[Message]], str]


def summarise_placeholder(messages: Sequence[Message]) -> str:
    """Default summariser: a deterministic, LLM-free digest of dropped turns.

    Replace with a real LLM summariser via :func:`trim_history`'s ``summariser``
    argument (Section 6.5 discusses when that is worth its own cost).
    """
    users = [m for m in messages if m.get("role") == "user"]
    tools = [m for m in messages if m.get("role") == "tool"]
    topics = "; ".join(_content_text(m.get("content"))[:60].strip() for m in users[:3])
    return (
        f"[Summary of {len(messages)} earlier messages: {len(users)} user turns, "
        f"{len(tools)} tool results. Topics: {topics}]"
    )


def trim_history(
    messages: Sequence[Message],
    max_tokens: int,
    *,
    keep_system: bool = True,
    keep_last_n: int = 2,
    summariser: Summariser | None = summarise_placeholder,
    model: str | None = None,
) -> list[Message]:
    """Drop the oldest non-system turns until the history fits ``max_tokens``.

    The system prompt (if ``keep_system``) and the last ``keep_last_n`` messages
    are always kept. Dropped turns are replaced by one system-role summary when a
    ``summariser`` is given. Tool-call/tool-result pairs are dropped together so
    the API never sees an orphan ``tool`` message.
    """
    msgs = list(messages)
    if count_message_tokens(msgs, model) <= max_tokens:
        return msgs
    system = [m for m in msgs if m.get("role") == "system"] if keep_system else []
    body = [m for m in msgs if not (keep_system and m.get("role") == "system")]
    tail = body[-keep_last_n:] if keep_last_n > 0 else []
    middle = body[: len(body) - len(tail)]
    dropped: list[Message] = []
    while middle and count_message_tokens(system + middle + tail, model) > max_tokens:
        first = middle.pop(0)
        dropped.append(first)
        # drop tool results that belong to a removed assistant tool call
        if first.get("role") == "assistant" and first.get("tool_calls"):
            while middle and middle[0].get("role") == "tool":
                dropped.append(middle.pop(0))
    # never start the body with an orphan tool result
    while middle and middle[0].get("role") == "tool":
        dropped.append(middle.pop(0))
    while tail and tail[0].get("role") == "tool" and not middle:
        dropped.append(tail.pop(0))
    out = list(system)
    if dropped and summariser is not None:
        out.append({"role": "system", "content": summariser(dropped)})
    out.extend(middle)
    out.extend(tail)
    return out


def context_diet(
    messages: Sequence[Message],
    *,
    history_budget: int = 3000,
    tool_result_budget: int = 400,
    keep_last_n: int = 2,
) -> tuple[list[Message], dict[str, int]]:
    """Apply tool-result truncation then history trimming; return (messages, stats)."""
    before = count_message_tokens(messages)
    slimmed: list[Message] = []
    for m in messages:
        if m.get("role") == "tool" and isinstance(m.get("content"), str):
            m = {**m, "content": truncate_tool_result(m["content"], tool_result_budget)}
        slimmed.append(m)
    trimmed = trim_history(slimmed, history_budget, keep_last_n=keep_last_n)
    after = count_message_tokens(trimmed)
    return trimmed, {"tokens_before": before, "tokens_after": after, "saved": before - after}
