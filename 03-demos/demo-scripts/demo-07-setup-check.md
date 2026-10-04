# Demo 07 — Environment Smoke Test

**Used in:** Lecture 0.2 (Course Roadmap & Environment Setup); Lab 1.1 setup
**Lecture type:** Setup demo
**Duration:** ~2 minutes of screen recording
**Purpose:** Install the locked environment, run the offline test suite, and prove every library, the agent and one DeepEval metric work, with no API key.
**Demo file(s):** `demos/m00_verify_setup.py`, `demos/m00_hello_eval.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m00_verify_setup.py`; `uv run python demos/m00_hello_eval.py`; `make install`; `make test`; `uv run deepeval test run demos/m00_hello_eval.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Install (30 s)

Terminal in `04-code-examples/agent-eval-framework`: `make install` (uv sync --locked; speed up 4x in post). Callout: "`uv.lock` is committed: everyone gets the same versions."

### Scene 2: 204 tests, no key (30 s)

`make test`. Show the last line: `204 passed, 5 skipped` in about 8–10 s. Callout: "5 live tests skip without a key."

### Scene 3: Verify setup (40 s)

`uv run python demos/m00_verify_setup.py` (output below). Highlight the version column and the two `[--]` lines: an API key and Langfuse keys are optional.

### Scene 4: Hello eval (20 s)

`uv run deepeval test run demos/m00_hello_eval.py`: one DeepEval test passes. Narration: "That's the loop you'll use for the rest of the course."

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m00_verify_setup.py
[OK] openai                                 2.54.0
[OK] deepeval                               4.2.7
[OK] ragas                                  0.4.3
[OK] langfuse                               4.16.0
[OK] mcp                                    2.2.0
[OK] opentelemetry-sdk                      1.45.0
[OK] opentelemetry-semantic-conventions     0.66b0
[OK] streamlit                              1.64.0
[OK] pytest                                 9.1.1
[--] OPENAI_API_KEY set                     optional offline
[--] LANGFUSE keys set                      optional until Module 9
[OK] support agent answers                  2 LLM calls, tools ['search_knowledge_base']
[OK] DeepEval metric runs                   AnswerRelevancy = 1.00
Setup complete. You're ready for Module 1.
```

```
$ uv run python demos/m00_hello_eval.py
hello eval PASSED
```

## Verify Before Recording

- [ ] Versions on screen match `uv.lock` (bible §2.1); re-capture if the lock file changed
- [ ] No API key in `.env` on screen
- [ ] Windows: show `uv run` (works in PowerShell) rather than `source .venv/bin/activate`
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Speed up installation 4x; keep test output real time
- Lower third: "No API key? Everything runs offline with a deterministic mock model and judge."
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
