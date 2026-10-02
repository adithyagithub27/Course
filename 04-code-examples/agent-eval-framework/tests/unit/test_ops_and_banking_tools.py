"""Unit: operations-agent and SecureBank tool backends, including authorization."""

import json

from agents import tool_agent
from agents.banking_agent import make_executor
from agents.tool_agent import execute_tool as ops


def test_query_filters():
    rows = json.loads(ops("query_database", {"table": "tickets", "filter_field": "status", "filter_value": "open"}))
    assert {r["id"] for r in rows} == {"TKT-101", "TKT-103"}


def test_delete_requires_confirmation():
    assert json.loads(ops("delete_record", {"table": "employees", "record_id": "EMP-002", "confirmation": False}))["status"] == "rejected"
    assert json.loads(ops("delete_record", {"table": "employees", "record_id": "EMP-002", "confirmation": True}))["status"] == "deleted"


def test_email_recipient_cap_and_unknown_ticket():
    assert "error" in json.loads(ops("send_email", {"recipients": [f"u{i}@techcorp.com" for i in range(11)], "subject": "x", "body": "y"}))
    assert "error" in json.loads(ops("update_ticket", {"ticket_id": "TKT-999", "status": "closed"}))


def test_failing_tools_switch():
    tool_agent.FAILING_TOOLS.add("query_database")
    try:
        assert "503" in ops("query_database", {"table": "tickets"})
    finally:
        tool_agent.FAILING_TOOLS.clear()


def test_banking_v1_has_no_ownership_check():
    v1 = make_executor("C-1001", hardened=False)
    assert json.loads(v1("check_balance", {"account_id": "ACC-2002-CHK"}))["owner"] == "John Smith"


def test_banking_v2_enforces_ownership_limits_confirmation():
    v2 = make_executor("C-1001", hardened=True)
    assert json.loads(v2("check_balance", {"account_id": "ACC-2002-CHK"}))["error"] == "not_authorized"
    assert json.loads(v2("check_balance", {"account_id": "ACC-1001-CHK"}))["balance"] == 4250.75
    t = {"from_account": "ACC-1001-CHK", "to_account": "ACC-1001-SAV"}
    assert json.loads(v2("transfer_funds", t | {"amount": 50, "confirmed": False}))["error"] == "confirmation_required"
    assert "limit" in json.loads(v2("transfer_funds", t | {"amount": 15000, "confirmed": True}))["error"]
    assert "payee" in json.loads(v2("transfer_funds", {"from_account": "ACC-1001-CHK", "to_account": "ACC-6666-EXT", "amount": 5, "confirmed": True}))["error"]
    assert json.loads(v2("transfer_funds", t | {"amount": 50, "confirmed": True}))["status"] == "completed"


def test_loan_rules():
    v2 = make_executor("C-1001", hardened=True)
    assert json.loads(v2("apply_for_loan", {"amount": 10000, "term_months": 36, "purpose": "car"}))["status"] == "pre_approved"
    assert json.loads(v2("apply_for_loan", {"amount": 90000, "term_months": 36, "purpose": "boat"}))["status"] == "declined"
