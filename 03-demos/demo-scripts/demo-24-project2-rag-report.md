# Demo 24 — Project 2 RAG Diagnostic Report

**Used in:** Lecture 5.4 ([PROJECT 2] Evaluate an Enterprise RAG Agent)
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Run the 15-question RAG evaluation with a per-question diagnosis and per-domain report.
**Demo file(s):** `demos/m05_project2_rag_eval.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m05_project2_rag_eval.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Per question (50 s)

Run the demo; 15 rows; RAG-IT-02 and RAG-TE-05 diagnosed "generation".

### Scene 2: Per domain (40 s)

The report table: hr, it_security, travel_expense; overall averages. Callout: a domain can read "ok" while one question in it fails.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m05_project2_rag_eval.py
id         faithfulness  answer_relevancy  context_precision  context_recall  diagnosis 
---------  ------------  ----------------  -----------------  --------------  ----------
RAG-HR-01  1.0           1.0               1.0                1.0             ok        
RAG-HR-02  1.0           1.0               1.0                1.0             ok        
RAG-HR-03  1.0           1.0               1.0                1.0             ok        
RAG-HR-04  1.0           1.0               1.0                1.0             ok        
RAG-HR-05  1.0           1.0               1.0                1.0             ok        
RAG-IT-01  1.0           1.0               1.0                1.0             ok        
RAG-IT-02  1.0           0.0               1.0                1.0             generation
RAG-IT-03  1.0           1.0               1.0                1.0             ok        
RAG-IT-04  1.0           1.0               1.0                1.0             ok        
RAG-IT-05  1.0           1.0               1.0                1.0             ok        
RAG-TE-01  1.0           1.0               0.833              1.0             ok        
RAG-TE-02  1.0           1.0               1.0                1.0             ok        
RAG-TE-03  1.0           1.0               1.0                1.0             ok        
RAG-TE-04  1.0           1.0               0.833              1.0             ok        
RAG-TE-05  0.0           0.0               1.0                1.0             generation
# Project 2 - RAG diagnostic report
| Domain | faithfulness | answer_relevancy | context_precision | context_recall | diagnosis |
|---|---|---|---|---|---|
| hr | 1.0 | 1.0 | 1.0 | 1.0 | ok |
| it_security | 1.0 | 0.8 | 1.0 | 1.0 | ok |
| travel_expense | 0.8 | 0.8 | 0.933 | 1.0 | ok |
Overall: {'faithfulness': 0.933, 'answer_relevancy': 0.867, 'context_precision': 0.978, 'context_recall': 1.0}
```

## Verify Before Recording

- [ ] 14 documents in 3 domains, 15 cases (the old brief's 8 HR docs and 10 questions are retired)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Open `reports/results/project2_report.md` in Markdown preview at the end
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
