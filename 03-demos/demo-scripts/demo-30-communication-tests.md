# Demo 30 — Testing Agent Hand-offs

**Used in:** Lecture 7.2 (Testing Agent Communication, Delegation & Coordination)
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Validate every message between the supervisor and its two workers with five communication checks.
**Demo file(s):** `demos/m07_communication_tests.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m07_communication_tests.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Messages (40 s)

The four hand-off messages with sender, receiver and `valid=True`. Show `Message` and `is_valid()` (bible §8.15).

### Scene 2: Checks (40 s)

Five PASS lines: order, checksums, topology, writer used findings, step budget.

### Scene 3: Final reply (20 s)

The reply built from KB-101.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m07_communication_tests.py
id  from        to          content                                                       valid
--  ----------  ----------  ------------------------------------------------------------  -----
1   supervisor  research    Find the facts needed to answer: Customer asks: what are you  True 
2   research    supervisor  FINDINGS: KB-101 (Plans and pricing): TechCorp offers three   True 
3   supervisor  writer      FINDINGS: KB-101 (Plans and pricing): TechCorp offers three   True 
4   writer      supervisor  Hi there, thanks for reaching out. TechCorp offers three pla  True 
[PASS] research is called before the writer
[PASS] every message passes its checksum
[PASS] workers only talk to the supervisor
[PASS] writer used the research findings
[PASS] finished within the step budget
Final reply: Hi there, thanks for reaching out. TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), and Enterprise (custom pricing). All plans include core features. Pro adds priority support and advanced analytics. Let us know if there's anything else we can help with. Best regards, TechCorp Support
```

## Verify Before Recording

- [ ] Uses `agents/multi_agent.py` and `tests/trajectory/test_multi_agent.py`
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Animate the four messages as arrows between three boxes
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
