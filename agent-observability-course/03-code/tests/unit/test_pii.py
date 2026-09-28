import pytest

from northwind.pii import (
    contains_pii,
    langfuse_mask,
    make_mask,
    mask_fn,
    mask_text,
    mask_value,
    mask_with_stats,
    short_hash,
    stable_hash,
)


@pytest.mark.parametrize(
    "text,tag",
    [
        ("contact anna.devries@northwind.example please", "<EMAIL>"),
        ("call +49 30 1234567 now", "<PHONE>"),
        ("call (555) 123-4567", "<PHONE>"),
        ("my id is NW-12345", "<EMPLOYEE_ID>"),
        ("card 4111 1111 1111 1111", "<CARD>"),
        ("card 4111-1111-1111-1111", "<CARD>"),
    ],
)
def test_masks_each_kind(text, tag):
    assert tag in mask_text(text)


def test_mask_text_returns_string_and_stats_variant():
    out, stats = mask_with_stats("a@b.io and NW-11111")
    assert (
        out == "<EMAIL> and <EMPLOYEE_ID>"
        and stats.emails == 1
        and stats.employee_ids == 1
        and stats.total == 2
    )
    assert isinstance(mask_text("a@b.io"), str)


def test_safe_ids_survive():
    out = mask_text("ticket TCK-100001 and shipment SHP-123456 and asset NWL-123456")
    assert "TCK-100001" in out and "SHP-123456" in out and "NWL-123456" in out


def test_card_requires_luhn():
    assert "<CARD>" not in mask_text("order 1234 5678 9012 3456")  # fails Luhn
    assert "<CARD>" in mask_text("4111111111111111")


def test_short_numbers_not_phones():
    assert (
        mask_text("28 days and 2026-09-14 and extension 4000")
        == "28 days and 2026-09-14 and extension 4000"
    )


def test_hash_ids_deterministic_and_joinable():
    a = mask_text("bob@northwind.example", hash_ids=True)
    b = mask_text("BOB@northwind.example", hash_ids=True)
    assert a == b and a.startswith("<EMAIL:") and len(a) == len("<EMAIL:>") + 8
    assert short_hash("x") == stable_hash("x") and short_hash("x", salt="s") != short_hash("x")


def test_mask_value_recursive():
    data = {"user": "NW-12345", "msgs": [{"content": "mail a@b.io"}], "n": 3, "t": ("NW-00001",)}
    out = mask_value(data)
    assert (
        out["user"] == "<EMPLOYEE_ID>"
        and out["msgs"][0]["content"] == "mail <EMAIL>"
        and out["n"] == 3
        and out["t"] == ("<EMPLOYEE_ID>",)
    )


def test_langfuse_mask_signature():
    out = langfuse_mask(data={"input": "NW-12345"})
    assert out["input"].startswith("<EMPLOYEE_ID:")
    assert mask_fn is langfuse_mask
    plain = make_mask(hash_ids=False)(data="NW-12345")
    assert plain == "<EMPLOYEE_ID>"


def test_contains_pii():
    assert contains_pii("write to hr@northwind.example")
    assert not contains_pii("Your ticket TCK-100001 is open.")


def test_empty_text():
    assert mask_text("") == ""
