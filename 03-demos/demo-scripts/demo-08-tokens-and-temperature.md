# Demo 08 — Tokens, Cost per Call and Temperature

**Used in:** Lecture 1.1 (LLMs in 10 Minutes: Tokens, Context, Temperature)
**Lecture type:** Screen beat in a diagram lecture (A5)
**Duration:** ~2 minutes of screen recording
**Purpose:** Make tokens and temperature concrete on the course agent: what the model really receives on every call, what one call costs, and why the same question gives different words.
**Demo file(s):** `demos/m01_token_demo.py`, `demos/m01_temperature_demo.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m01_token_demo.py`; `uv run python demos/m01_temperature_demo.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: What the model receives (50 s)

Run `m01_token_demo.py`. Highlight: query 19 tokens vs system prompt 255 + tool schemas 481 = 755 input tokens on the first call. Then the two cost lines (gpt-4.1-mini vs gpt-4.1) with "verify current pricing".

### Scene 2: Same question, five times (50 s)

Run `m01_temperature_demo.py`. temperature=0.0: 1 distinct answer; 1.0: 3 distinct answers, same facts. Callout on the last line: "an exact-match assertion would fail".

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m01_token_demo.py
Tokenizer: approximate (len/4; tiktoken encoding unavailable)
Customer query (78 characters) -> 19 tokens
Hi | , | I | was | charged | twice | for | my | Pro | plan | this | month | . | Can | you | refund | one | charge | ?
What the model actually receives on the first call:
  system prompt     255 tokens
  tool schemas      481 tokens
  customer query     19 tokens
  total input       755 tokens
  gpt-4.1-mini  one call ~ $0.000398; 1M calls ~ $398  (verify current pricing)
  gpt-4.1       one call ~ $0.001990; 1M calls ~ $1,990  (verify current pricing)
Context window 1,000,000 tokens: roughly 12,648 turns of this size before it is full.
```

```
$ uv run python demos/m01_temperature_demo.py
temperature=0.0: 1 distinct answer(s) out of 5
  1. Refunds are processed within 5-7 business days.
  2. Refunds are processed within 5-7 business days.
  3. Refunds are processed within 5-7 business days.
  4. Refunds are processed within 5-7 business days.
  5. Refunds are processed within 5-7 business days.
temperature=1.0: 3 distinct answer(s) out of 5
  1. It takes 5-7 business days for a refund to be processed.
  2. Expect your refund within 5-7 business days.
  3. Once approved, a refund takes 5-7 business days to process.
  4. Expect your refund within 5-7 business days.
  5. Expect your refund within 5-7 business days.
Same facts, different words: an exact-match assertion would fail on the 1.0 runs.
```

## Verify Before Recording

- [ ] The token table depends on the tokenizer. In the build sandbox tiktoken's `o200k_base` file was unavailable, so the demo used `len/4` (first line says so). **Re-capture on the recording machine** where tiktoken downloads the real encoding, and use those numbers on screen and in the script
- [ ] Context window line (1,000,000 tokens for the gpt-4.1 family): verify
- [ ] Prices: verify current pricing
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Teal highlight on the 19-token query, amber on the 736 fixed-overhead tokens
- Split screen for the temperature runs: 0.0 left, 1.0 right
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
