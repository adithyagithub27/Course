# Demo 11 — Why Exact-Match Assertions Flake

**Used in:** Lecture 2.1 (Deterministic vs. Non-Deterministic)
**Lecture type:** Screen beat in a diagram lecture (A5)
**Duration:** ~90 seconds of screen recording
**Purpose:** Show a traditional assertion failing six correct answers out of ten, and a semantic check passing all ten.
**Demo file(s):** `demos/m02_assertion_flakiness.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m02_assertion_flakiness.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Ten runs (50 s)

Run the demo; let the ten lines scroll. Highlight the `exact=FAIL semantic=PASS` rows: every answer says 5-7 business days.

### Scene 2: The verdict (30 s)

Zoom on the last two lines: 4/10 vs 10/10. Narration: "The test is flaky. The agent isn't."

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m02_assertion_flakiness.py
run  1: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  2: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  3: exact=FAIL  semantic=PASS  Once approved, a refund takes 5-7 business days to process.
run  4: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  5: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  6: exact=FAIL  semantic=PASS  It takes 5-7 business days for a refund to be processed.
run  7: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.
run  8: exact=FAIL  semantic=PASS  Once approved, a refund takes 5-7 business days to process.
run  9: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.
run 10: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.
assert response == expected : 4/10 passed (flaky, though every answer is correct)
assert '5-7 business days' in : 10/10 passed
```

## Verify Before Recording

- [ ] Which runs fail depends on the seeded phrasing; the 4/10 total is stable offline. Live it will differ: re-capture if you record live
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- FAIL in red, PASS in teal
- Pair with D2 build 2
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
