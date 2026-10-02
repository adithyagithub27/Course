"""
AI governance: a tamper-evident audit trail and a release gate (Module 13.2).

Every event (evaluation run, approval, deployment) is appended to a JSONL log
with the SHA-256 of the previous record, so any edit breaks the chain.

    trail = AuditTrail("reports/results/audit.jsonl")
    trail.log("evaluation", actor="ci", agent_version="v1.3", data={"pass_rate": 0.9})
    trail.log("approval", actor="jane.doe@techcorp.com", agent_version="v1.3", data={"role": "QA lead"})
    release_allowed(trail, "v1.3", policy) -> (bool, reasons)
    trail.verify() -> True if no record was altered
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_POLICY = {
    "min_pass_rate": 0.8,
    "min_scores": {"Faithfulness": 0.8, "Answer Relevancy": 0.7},
    "redteam_must_pass": True,
    "required_approvals": ["QA lead", "Product owner"],
}


class AuditTrail:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def records(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]

    def log(self, event: str, actor: str, agent_version: str, data: dict | None = None, ts: str | None = None) -> dict:
        prev = self.records()
        rec = {
            "seq": len(prev) + 1,
            "ts": ts or datetime.now(UTC).isoformat(timespec="seconds"),
            "event": event, "actor": actor, "agent_version": agent_version, "data": data or {},
            "prev_hash": prev[-1]["hash"] if prev else "0" * 64,
        }
        rec["hash"] = hashlib.sha256(json.dumps({k: v for k, v in rec.items() if k != "hash"}, sort_keys=True).encode()).hexdigest()
        with self.path.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def verify(self) -> bool:
        prev_hash = "0" * 64
        for rec in self.records():
            body = {k: v for k, v in rec.items() if k != "hash"}
            if rec["prev_hash"] != prev_hash:
                return False
            if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != rec["hash"]:
                return False
            prev_hash = rec["hash"]
        return True

    def history(self, agent_version: str) -> list[dict]:
        return [r for r in self.records() if r["agent_version"] == agent_version]


def release_allowed(trail: AuditTrail, version: str, policy: dict | None = None) -> tuple[bool, list[str]]:
    policy = policy or DEFAULT_POLICY
    hist = trail.history(version)
    reasons = []
    evals = [r for r in hist if r["event"] == "evaluation"]
    if not evals:
        reasons.append("no evaluation run recorded")
    else:
        last = evals[-1]["data"]
        if last.get("pass_rate", 0) < policy["min_pass_rate"]:
            reasons.append(f"pass rate {last.get('pass_rate')} < {policy['min_pass_rate']}")
        for m, thr in policy["min_scores"].items():
            if last.get("averages", {}).get(m, 0) < thr:
                reasons.append(f"{m} {last.get('averages', {}).get(m)} < {thr}")
    if policy.get("redteam_must_pass"):
        rt = [r for r in hist if r["event"] == "redteam"]
        if not rt or rt[-1]["data"].get("findings", 1) > 0:
            reasons.append("red-team run missing or has open findings")
    roles = {r["data"].get("role") for r in hist if r["event"] == "approval"}
    for role in policy["required_approvals"]:
        if role not in roles:
            reasons.append(f"missing approval: {role}")
    if not trail.verify():
        reasons.append("audit trail integrity check failed")
    return (not reasons, reasons)
