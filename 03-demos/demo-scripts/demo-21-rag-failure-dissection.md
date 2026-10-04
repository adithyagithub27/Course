# Demo 21 — RAG Failure Dissection

**Used in:** Lecture 5.1 (The RAG Quality Problem)
**Lecture type:** Screen beat in a diagram lecture (A5)
**Duration:** ~2 minutes of screen recording
**Purpose:** Trace a wrong RAG answer to the retriever and fix it there, with RAGAS scores before and after.
**Demo file(s):** `demos/m05_rag_failure_dissection.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m05_rag_failure_dissection.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Before (50 s)

Retrieved `vacation-001, itsec-001, travel-002`; the answer lives in `travel-001`. All four RAGAS scores 0.0.

### Scene 2: After (50 s)

Stop words removed: `travel-001` retrieved; correct answer with citation; faithfulness 1.0, recall 1.0, precision 0.5. Cut to `retrieve_context()` (bible §8.10).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m05_rag_failure_dissection.py
BEFORE: naive keyword retriever
  retrieved: ['vacation-001', 'itsec-001', 'travel-002']  (the answer lives in travel-001)
  answer   : The policy documents provided don't cover that question. Please contact HR or the IT Service Desk for help.
  RAGAS    : {'faithfulness': 0.0, 'answer_relevancy': 0.0, 'context_precision': 0.0, 'context_recall': 0.0}
  diagnosis: both
AFTER: stop words removed
  retrieved: ['itsec-001', 'travel-001', 'vacation-001']  (the answer lives in travel-001)
  answer   : Economy class is required for flights under 6 hours; premium economy is allowed for flights of 6 hours or more. (Source: Travel Booking (Section 7.2))
  RAGAS    : {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 0.5, 'context_recall': 1.0}
  diagnosis: retrieval
```

## Verify Before Recording

- [ ] The diagnosis label for BEFORE is "both" (all four scores are 0): explain that empty retrieval also starves the generator
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D9 build 2
- BEFORE in red tint, AFTER in teal
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
