# Demo 43 — DeepEval Synthesizer at Scale

**Used in:** Lecture 11.3 (Generating Synthetic Test Data at Scale); Lab 11.1
**Lecture type:** Build-along
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Expand 5 seed goldens with DeepEval's Synthesizer, check quality, then run the Lab 11.1 generate-baseline-regress-catch loop.
**Demo file(s):** `demos/m11_synthetic_data.py`, `demos/m11_lab_generate_regress_catch.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m11_synthetic_data.py`; `uv run python demos/m11_lab_generate_regress_catch.py`; `make synthetic   # 5 seeds x 20 = 100 goldens`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The synthesizer (40 s)

`regression/synthetic_data.py`: `StylingConfig` and `generate_goldens_from_goldens(..., max_goldens_per_golden=per_seed)` (bible §8.23).

### Scene 2: Generated goldens (40 s)

Run `m11_synthetic_data.py`: 20 goldens, quality report (unique 20/20, duplicate rate 0.0).

### Scene 3: The lab loop (50 s)

Run `m11_lab_generate_regress_catch.py`: 10 cases from the KB articles, baseline 80%, regressed 60%, caught, fixed back to baseline.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m11_synthetic_data.py
Seeds:
  - What are your pricing plans?
  - How long do refunds take?
  - How do I reset my password?
  - What is the API rate limit on Basic?
  - How do I cancel my subscription?
Generated 20 goldens (generate_goldens_from_goldens, max_goldens_per_golden=4):
  - I'm confused about the plans and pricing. Can you help? My manager needs the answer today. thanks!
  - quick one: where can I read the plans and pricing? We have 40 users on our account.
  - quick one: can you tell me about the plans and pricing? We have 40 users on our account.
  - Can you explain the plans and pricing for my team? We have 40 users on our account.
  - Can you explain the refund policy for my team? My manager needs the answer today. thanks!
  - quick one: i'm confused about the refund policy. Can you help? My manager needs the answer today.
  - Where can I read the refund policy? I signed up last week.
  - quick one: can you tell me about the refund policy? I'm on the Pro plan, if that matters.
  ...
Quality: {'count': 20, 'unique': 20, 'duplicate_rate': 0.0, 'avg_words': 17.1, 'distinct_content_words': 36, 'with_expected_output': 20}
Saved to reports/results/synthetic_goldens.json
Offline the mock judge fills the Synthesizer's templates, so wording is formulaic; live gpt-4.1 writes varied inputs.
```

```
$ uv run python demos/m11_lab_generate_regress_catch.py
1. Generated 10 synthetic cases from 5 knowledge-base articles
2. Baseline:   pass rate 80%  {'Answer Relevancy': 0.9, 'Faithfulness': 1.0}
3. Regressed:  pass rate 60%  {'Answer Relevancy': 0.8, 'Faithfulness': 0.8}
4. Detected:   faithfulness dropped 0.20 -> REGRESSION
5. Fixed:      pass rate 80%  back to baseline: True
```

## Verify Before Recording

- [ ] **Say it:** offline the mock fills the templates, so questions are formulaic; live gpt-4.1 writes varied ones. Don't present offline questions as typical LLM output (bible §12.7)
- [ ] API names: `generate_goldens_from_goldens` / `generate_goldens_from_contexts` (not `generate_goldens_from_docs`)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Show three generated questions full-screen, labelled "offline"
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
