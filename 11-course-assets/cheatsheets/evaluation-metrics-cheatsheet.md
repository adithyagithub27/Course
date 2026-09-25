# Evaluation Metrics Cheatsheet

## Quick Reference — Which Metric When?

### Decision Tree

```
What are you testing?
│
├── LLM output quality?
│   ├── Is the answer relevant? → AnswerRelevancyMetric
│   ├── Is it grounded in context? → FaithfulnessMetric
│   ├── Does it hallucinate? → HallucinationMetric
│   └── Is it well-structured? → CoherenceMetric
│
├── RAG pipeline?
│   ├── Is retrieved context relevant? → ContextualPrecisionMetric
│   ├── Does context cover the answer? → ContextualRecallMetric
│   ├── Is answer grounded in docs? → FaithfulnessMetric (RAGAS)
│   └── Is answer relevant to query? → AnswerRelevancyMetric (RAGAS)
│
├── Agent behavior?
│   ├── Did it complete the task? → TaskCompletionMetric
│   ├── Did it use right tools? → ToolCorrectnessMetric
│   └── Custom business logic? → GEval (custom criteria)
│
├── Security?
│   ├── Prompt injection? → promptfoo red team
│   ├── Jailbreak? → promptfoo red team
│   ├── PII leakage? → GEval (PII Safety)
│   └── Unauthorized actions? → Custom assertion
│
└── Performance?
    ├── Latency? → benchmark.py (time.perf_counter)
    ├── Token cost? → benchmark.py (token counting)
    └── LLM call count? → benchmark.py (call counting)
```

### Metric Priority Matrix

| Priority | Category | Metrics | Run When |
|----------|----------|---------|----------|
| P0 (Critical) | Security | Injection resistance, PII leakage | Every PR |
| P0 (Critical) | Functional | Task completion, tool correctness | Every PR |
| P1 (Important) | LLM Quality | Relevancy, faithfulness, hallucination | Every PR |
| P1 (Important) | RAG Quality | Context precision, recall | Every PR |
| P2 (Periodic) | Performance | Latency, cost, throughput | Weekly / release |
| P2 (Periodic) | Reliability | Consistency, failure rate | Weekly / release |

### Threshold Quick Reference

| Metric | Default | Strict | Relaxed |
|--------|---------|--------|---------|
| Answer Relevancy | 0.7 | 0.85 | 0.5 |
| Faithfulness | 0.8 | 0.9 | 0.6 |
| Hallucination | 0.3 | 0.1 | 0.5 |
| Context Precision | 0.7 | 0.85 | 0.5 |
| Context Recall | 0.7 | 0.85 | 0.5 |
| Injection Resistance | 0.9 | 0.95 | 0.8 |
| PII Leakage | 0.05 | 0.01 | 0.1 |
| Task Completion | 0.8 | 0.9 | 0.6 |

### Remember
- **Inverted metrics** (lower = better): Hallucination, PII Leakage, Failure Rate
- **Context is required** for: Faithfulness, Hallucination, Context Precision/Recall
- **Expected output is optional** but improves accuracy for: Correctness, Context Recall
- **Run security tests on every PR** — they're fast and catch critical issues
