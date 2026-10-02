"""Lecture 13.2 - Governance audit trail: who evaluated, red-teamed and approved
which agent version, with a hash chain that exposes tampering.

    uv run python demos/m13_governance_audit.py
"""
from _common import banner

import json

from monitoring.governance import AuditTrail, release_allowed
from reports.experiments import RESULTS

banner("Lecture 13.2 - governance audit trail")
path = RESULTS / "audit_demo.jsonl"
path.unlink(missing_ok=True)
trail = AuditTrail(path)
trail.log("evaluation", "github-actions", "v1.3", {"pass_rate": 1.0, "averages": {"Faithfulness": 1.0, "Answer Relevancy": 1.0}}, ts="2026-09-28T10:02:00+00:00")
trail.log("redteam", "github-actions", "v1.3", {"total": 10, "findings": 0}, ts="2026-09-28T10:09:00+00:00")
trail.log("approval", "maria.lopez@techcorp.com", "v1.3", {"role": "QA lead"}, ts="2026-09-28T14:30:00+00:00")
print(release_allowed(trail, "v1.3"))
trail.log("approval", "sam.chen@techcorp.com", "v1.3", {"role": "Product owner"}, ts="2026-09-29T09:15:00+00:00")
trail.log("deployment", "release-bot", "v1.3", {"environment": "production"}, ts="2026-09-29T09:40:00+00:00")
for r in trail.records():
    print(f"#{r['seq']} {r['ts']} {r['event']:<11} {r['actor']:<26} {json.dumps(r['data'])[:50]}  hash {r['hash'][:10]}")
print(f"\nRelease allowed for v1.3: {release_allowed(trail, 'v1.3')}")
print(f"Chain intact: {trail.verify()}")
lines = path.read_text().splitlines()
lines[0] = lines[0].replace('"pass_rate": 1.0', '"pass_rate": 0.6')
path.write_text("\n".join(lines) + "\n")
print(f"After someone edits record #1 by hand -> chain intact: {trail.verify()}")
