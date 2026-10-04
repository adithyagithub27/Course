# Demo 45 — Hash-Chained Audit Trail and Release Gate

**Used in:** Lecture 13.2 (Enterprise AI Governance)
**Lecture type:** Screen beat in a teach lecture (A5)
**Duration:** ~2 minutes of screen recording
**Purpose:** Show a release blocked by a missing approval, the full audit trail, the release allowed, and tamper detection.
**Demo file(s):** `demos/m13_governance_audit.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m13_governance_audit.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Blocked (20 s)

`(False, ['missing approval: Product owner'])`.

### Scene 2: The trail (50 s)

Five records: evaluation, red team, two approvals, deployment; each with a hash. Show `AuditTrail.log()` (bible §8.26).

### Scene 3: Tamper (30 s)

Release allowed for v1.3; after editing record #1 by hand, chain intact: False.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m13_governance_audit.py
(False, ['missing approval: Product owner'])
#1 2026-09-28T10:02:00+00:00 evaluation  github-actions             {"pass_rate": 1.0, "averages": {"Faithfulness": 1.  hash 3cde262af4
#2 2026-09-28T10:09:00+00:00 redteam     github-actions             {"total": 10, "findings": 0}  hash 01962c2bbf
#3 2026-09-28T14:30:00+00:00 approval    maria.lopez@techcorp.com   {"role": "QA lead"}  hash 427222e35d
#4 2026-09-29T09:15:00+00:00 approval    sam.chen@techcorp.com      {"role": "Product owner"}  hash 1890e1649d
#5 2026-09-29T09:40:00+00:00 deployment  release-bot                {"environment": "production"}  hash 4d5b3ad7f5
Release allowed for v1.3: (True, [])
Chain intact: True
After someone edits record #1 by hand -> chain intact: False
```

## Verify Before Recording

- [ ] Names and emails in the trail are fictional
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Animate the hash chain links
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
