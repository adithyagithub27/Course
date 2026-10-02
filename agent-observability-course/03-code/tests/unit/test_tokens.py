import json

import pytest

from northwind.tokens import (
    approx_tokens,
    context_diet,
    count_message_tokens,
    count_tokens,
    count_tool_schema_tokens,
    estimate_tokens,
    summarise_placeholder,
    trim_history,
    truncate_text,
    truncate_tool_result,
)


def test_empty_is_zero():
    assert count_tokens("") == 0


@pytest.mark.parametrize(
    "text,lo,hi",
    [
        ("Hello world", 2, 4),
        ("The quick brown fox jumps over the lazy dog.", 8, 13),
        ("a" * 400, 80, 110),
        ('{"ticket_id": "TCK-100001", "status": "open"}', 12, 26),
    ],
)
def test_approximation_in_plausible_range(text, lo, hi):
    assert lo <= approx_tokens(text) <= hi


def test_estimate_alias():
    assert estimate_tokens("hello there") == count_tokens("hello there")


def test_message_tokens_include_overhead_and_tool_calls():
    msgs = [{"role": "system", "content": "You are Atlas."}, {"role": "user", "content": "hi"}]
    base = count_message_tokens(msgs)
    with_tc = count_message_tokens(
        msgs
        + [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"function": {"name": "lookup_ticket", "arguments": '{"ticket_id":"TCK-1"}'}}
                ],
            }
        ]
    )
    assert with_tc > base + 10


def test_tool_schema_tokens_positive():
    from app.tools import TOOL_SCHEMAS

    assert 400 < count_tool_schema_tokens(TOOL_SCHEMAS) < 1200


def test_truncate_text_fits_budget():
    text = "word " * 500
    out = truncate_text(text, 50)
    assert count_tokens(out) <= 50 and out.endswith("[truncated]")


def test_truncate_text_noop_when_short():
    assert truncate_text("short", 100) == "short"


def test_truncate_tool_result_keeps_json_valid():
    big = json.dumps(
        {"results": [{"id": f"KB-{i}", "content": "lorem ipsum " * 200} for i in range(6)]}
    )
    out = truncate_tool_result(big, 300)
    data = json.loads(out)
    assert "results" in data and count_tokens(out) <= 300


def test_truncate_tool_result_plain_text_marker():
    out = truncate_tool_result("alpha beta gamma " * 300, 60)
    assert "tokens truncated" in out and count_tokens(out) < 120


def test_trim_history_keeps_system_and_tail():
    msgs = [{"role": "system", "content": "sys"}] + [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"turn {i} " + "blah " * 60}
        for i in range(12)
    ]
    out = trim_history(msgs, 300, keep_last_n=2)
    assert out[0]["role"] == "system"
    assert out[-2:] == msgs[-2:]
    assert count_message_tokens(out) <= 300 + 60  # summary line adds a little
    assert any(m["content"].startswith("[Summary") for m in out)


def test_trim_history_drops_tool_pairs_together():
    msgs = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "q1"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "c1", "function": {"name": "x", "arguments": "{}"}}],
        },
        {"role": "tool", "tool_call_id": "c1", "content": "result " * 200},
        {"role": "assistant", "content": "a1"},
        {"role": "user", "content": "q2"},
        {"role": "assistant", "content": "a2"},
    ]
    out = trim_history(msgs, 80, keep_last_n=2, summariser=None)
    roles = [m["role"] for m in out]
    assert "tool" not in roles or roles[roles.index("tool") - 1] == "assistant"


def test_trim_history_noop_when_fits():
    msgs = [{"role": "user", "content": "hi"}]
    assert trim_history(msgs, 1000) == msgs


def test_summarise_placeholder_mentions_counts():
    s = summarise_placeholder(
        [{"role": "user", "content": "vpn broken"}, {"role": "tool", "content": "{}"}]
    )
    assert "1 user turns" in s and "1 tool results" in s and "vpn broken" in s


def test_context_diet_reports_savings():
    msgs = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "c", "function": {"name": "s", "arguments": "{}"}}],
        },
        {"role": "tool", "tool_call_id": "c", "content": "x " * 3000},
        {"role": "user", "content": "follow up"},
    ]
    out, stats = context_diet(msgs, history_budget=5000, tool_result_budget=100)
    assert stats["saved"] > 0 and stats["tokens_after"] < stats["tokens_before"]
    assert count_tokens(out[3]["content"]) <= 130


def test_context_diet_bounds_tokens():
    """Incident 1 action item: 3 turns x 12 whole articles stay near history_token_budget."""
    import json

    from app.knowledge import get_kb
    from northwind.config import Settings
    from northwind.tokens import context_diet, count_message_tokens

    s = Settings.from_env({})
    kb = get_kb()
    article = " ".join(a.body for a in kb.articles)[:20000]
    msgs = [{"role": "system", "content": "You are Atlas."}]
    for turn in range(3):
        msgs.append({"role": "user", "content": f"question {turn}"})
        msgs.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"c{turn}",
                        "type": "function",
                        "function": {"name": "search_knowledge_base", "arguments": "{}"},
                    }
                ],
            }
        )
        msgs.append(
            {
                "role": "tool",
                "tool_call_id": f"c{turn}",
                "content": json.dumps({"results": [article] * 12}),
            }
        )
    raw = count_message_tokens(msgs)
    slim, stats = context_diet(
        msgs, history_budget=s.history_token_budget, tool_result_budget=s.tool_result_token_budget
    )
    assert raw > 10 * s.history_token_budget
    assert count_message_tokens(slim) <= s.history_token_budget + s.tool_result_token_budget
    assert stats["saved"] > 0
