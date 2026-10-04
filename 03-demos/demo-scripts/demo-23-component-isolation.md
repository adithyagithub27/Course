# Demo 23 — Retriever vs Generator in Isolation

**Used in:** Lecture 5.3 (Evaluating Retrieval and Generation Separately)
**Lecture type:** Build-along
**Duration:** ~90 seconds of screen recording
**Purpose:** Test the retriever alone (hit@3) and the generator alone (perfect context) to decide which component to fix.
**Demo file(s):** `demos/m05_component_isolation.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m05_component_isolation.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Isolation table (60 s)

Run the demo: retriever hit@3 yes at rank 1 for all five travel questions; generator with perfect context fails RAG-TE-05 → fix the generator.

### Scene 2: The rule (20 s)

Zoom on the last line: retriever misses → chunking/ranking; generator wrong with perfect context → prompt or model.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m05_component_isolation.py
id         retriever_hit@3  rank  generator_correct(perfect ctx)  fix      
---------  ---------------  ----  ------------------------------  ---------
RAG-TE-01  yes              1     1.00                            -        
RAG-TE-02  yes              1     1.00                            -        
RAG-TE-03  yes              1     1.00                            -        
RAG-TE-04  yes              1     1.00                            -        
RAG-TE-05  yes              1     0.00                            generator
Retriever misses -> fix chunking/ranking. Generator wrong with perfect context -> fix the prompt or model.
```

## Verify Before Recording

- [ ] Uses `tests/component/test_rag_components.py` patterns; the same split is in the D9 build 2 decision tree
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Teal for hits, red for the generator miss
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
