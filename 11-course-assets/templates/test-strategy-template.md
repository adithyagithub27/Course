# AI Agent Test Strategy Template

## Agent Under Test

| Field | Value |
|-------|-------|
| Agent Name | |
| Purpose | |
| LLM Model | |
| Tools/APIs | |
| Deployment Target | |
| Risk Level | Low / Medium / High / Critical |

## Testing Layers

### Layer 1 — Prompt Tests (Unit)
**What:** Test individual prompts for correctness and robustness
**When:** Every code change
**Tools:** DeepEval, pytest

| Test | Metric | Threshold | Priority |
|------|--------|-----------|----------|
| Answer relevancy | AnswerRelevancyMetric | 0.7 | P0 |
| Faithfulness | FaithfulnessMetric | 0.8 | P0 |
| Hallucination | HallucinationMetric | 0.3 | P0 |
| Custom: _________ | GEval | _____ | P1 |

### Layer 2 — Component Tests
**What:** Test individual components (tools, retrieval, generation)
**When:** Every PR
**Tools:** DeepEval, RAGAS

| Component | Tests | Metric | Threshold |
|-----------|-------|--------|-----------|
| Tool calling | Selection accuracy | ToolCorrectnessMetric | 0.85 |
| Tool calling | Argument correctness | Custom assertion | 100% |
| RAG retrieval | Context precision | ContextualPrecisionMetric | 0.7 |
| RAG retrieval | Context recall | ContextualRecallMetric | 0.7 |
| RAG generation | Faithfulness to docs | FaithfulnessMetric | 0.8 |

### Layer 3 — Agent-Level Evals (Integration)
**What:** End-to-end agent behavior on realistic scenarios
**When:** Every PR, full suite weekly
**Tools:** DeepEval, golden datasets

| Scenario Category | Test Cases | Metric | Threshold |
|-------------------|-----------|--------|-----------|
| Happy path | _____ cases | Task completion | 0.8 |
| Edge cases | _____ cases | Correctness (GEval) | 0.7 |
| Error handling | _____ cases | Recovery behavior | 0.7 |

### Layer 4 — Security (Overlay)
**What:** Adversarial testing for injection, jailbreak, data leakage
**When:** Every PR (fast scan), weekly (full scan)
**Tools:** promptfoo, DeepEval

| Attack Vector | Test Count | Threshold | Priority |
|---------------|-----------|-----------|----------|
| Prompt injection | _____ | 0.9 resistance | P0 |
| Jailbreak | _____ | 0.9 resistance | P0 |
| PII leakage | _____ | <0.05 rate | P0 |
| Unauthorized actions | _____ | <0.02 rate | P0 |
| Data exfiltration | _____ | 0.95 resistance | P1 |

## Performance Baselines

| Metric | Target | Current |
|--------|--------|---------|
| P95 Latency | _____ s | _____ s |
| Avg Cost/Task | $_____ | $_____ |
| LLM Calls/Task | _____ | _____ |
| Failure Rate | <_____% | _____% |

## Quality Gate

| Gate | Criteria | Blocks Deploy? |
|------|----------|---------------|
| Functional | >80% pass rate on golden dataset | Yes |
| Security | >90% resistance on all attack vectors | Yes |
| Performance | P95 latency < target | No (warning) |
| Regression | No score drop >10% from baseline | Yes |

## Monitoring (Post-Deploy)

| Signal | Check | Alert Threshold |
|--------|-------|----------------|
| Quality drift | Weekly eval run | >15% score drop |
| Cost trend | Daily cost tracking | >20% increase |
| Error rate | Real-time monitoring | >5% error rate |
| User feedback | Feedback collection | <3.5/5 avg rating |

## Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| QA Lead | | | [ ] |
| Engineering Manager | | | [ ] |
| Security | | | [ ] |
| Product Owner | | | [ ] |
