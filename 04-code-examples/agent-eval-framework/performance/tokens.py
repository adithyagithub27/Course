"""
Token counting (Module 1.1, Module 10).

``count_tokens`` uses tiktoken (o200k_base, the gpt-4.1 family encoding). The
encoding file is downloaded once from openaipublic.blob.core.windows.net and
cached; if that download is impossible (air-gapped machine) we fall back to
len(text)/4 and say so, so nothing crashes offline.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _encoding():
    try:
        import tiktoken

        return tiktoken.get_encoding("o200k_base")
    except Exception:  # noqa: BLE001 - no network or no cache
        return None


def tokenizer_name() -> str:
    return "tiktoken o200k_base" if _encoding() is not None else "approximate (len/4; tiktoken encoding unavailable)"


def tokenize(text: str) -> list[str]:
    enc = _encoding()
    if enc is None:
        import re

        return re.findall(r"\w+|[^\w\s]", text)
    return [enc.decode([t]) for t in enc.encode(text)]


def count_tokens(text: str) -> int:
    enc = _encoding()
    return len(enc.encode(text)) if enc is not None else max(1, len(text) // 4)
