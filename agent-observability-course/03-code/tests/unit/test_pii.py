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


def test_hash_is_keyed_hmac(monkeypatch):
    """Section 10.2: the pseudonym is HMAC-SHA256 keyed with ATLAS_PII_HASH_KEY, same format."""
    import hashlib
    import hmac

    from northwind.pii import DEMO_PII_HASH_KEY

    demo = short_hash("NW-12345")
    assert demo == hmac.new(
        DEMO_PII_HASH_KEY.encode(), b"northwind:NW-12345", hashlib.sha256
    ).hexdigest()[:8]
    assert demo != hashlib.sha256(b"northwind:NW-12345").hexdigest()[:8]  # not the old salted hash
    monkeypatch.setenv("ATLAS_PII_HASH_KEY", "s3cret")
    keyed = short_hash("NW-12345")
    assert keyed != demo and len(keyed) == 8
    masked = mask_text("id NW-12345", hash_ids=True)
    assert masked == f"id <EMPLOYEE_ID:{keyed}>"  # same placeholder shape, new key (no stale cache)


def test_demo_key_warns_outside_offline(monkeypatch, caplog):
    import northwind.pii as pii

    monkeypatch.delenv("ATLAS_PII_HASH_KEY", raising=False)
    monkeypatch.setattr(pii, "_warned_demo_key", False)
    monkeypatch.setenv("OFFLINE", "1")
    with caplog.at_level("WARNING", logger="atlas.pii"):
        pii.short_hash("x")
    assert not caplog.records
    monkeypatch.setenv("OFFLINE", "0")
    with caplog.at_level("WARNING", logger="atlas.pii"):
        pii.short_hash("x")
        pii.short_hash("y")
    assert len(caplog.records) == 1 and "ATLAS_PII_HASH_KEY" in caplog.records[0].getMessage()


def test_contains_pii_skips_documented_format_examples():
    """The KB and prompt print 'employee ID (format NW-12345)'; repeating it is not a leak."""
    assert not contains_pii("Reply with the code and your employee ID (NW-12345).")
    assert not contains_pii("check the employee ID format NW-12345.")
    assert contains_pii("Employee NW-40213 is locked out.")
    assert contains_pii("NW-12345 or NW-40213")  # a real id next to the example still counts
    assert "<EMPLOYEE_ID>" in mask_text("format NW-12345")  # telemetry still masks it


def test_contains_pii_skips_values_published_in_the_kb():
    from northwind.pii import published_values

    pub = published_values()
    assert {"NW-12345", "helpdesk@northwind.example", "0800-555-0199"} <= pub
    assert not contains_pii("Call the EAP on 0800-555-0199 or mail helpdesk@northwind.example.")
    assert contains_pii("Call me on 0800-555-0198.")  # one digit off: a real number
    assert contains_pii("mail anna.devries@northwind.example")
    assert contains_pii("helpdesk@northwind.example.attacker.io")  # not the published mailbox
