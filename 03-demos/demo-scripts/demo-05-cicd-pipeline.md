# Demo 05 — The CI Quality Gate on a Pull Request

**Used in:** Lecture 12.2 (GitHub Actions Pipeline: Eval on Every PR); the gate logic is introduced in 12.1; also Lab 12.1
**Duration:** ~3–4 minutes of screen recording
**Purpose:** Show the quality gate pass a good change and block a bad one, locally and on a real GitHub pull request with a PR comment.
**Demo files:** `.github/workflows/agent-eval.yml`, `reports/run_eval.py`, `reports/quality_gate.py`, `demos/m12_quality_gate.py`
**Commands:** `uv run python demos/m12_quality_gate.py`; on GitHub: two pull requests
**Verified:** workflow as committed (2026-10-02); local commands offline

## Setup

- A GitHub repository with the course repo at its root (or `working-directory` set in the workflow), Actions enabled
- Optional `OPENAI_API_KEY` repository secret (without it the PR job evaluates offline)
- Two branches prepared: `good-change` (reword "Be helpful, concise, and professional" without changing meaning) and `bad-change` (delete "- Only state prices, limits and policies that appear in a knowledge base result" from `SYSTEM_PROMPT`)

## Recording Script

### Scene 1: The workflow (45 s)

`.github/workflows/agent-eval.yml`. Walk the jobs: `tests` (every push: offline suite + smoke eval), `quality-gate` (PRs: `reports.run_eval` live if the secret exists, `reports.quality_gate --baseline support_v1`, `gh pr comment`, fail step), `redteam` (promptfoo), `nightly` (capstone). Highlight `set +e` and `echo "exit=$?" >> "$GITHUB_OUTPUT"`: the comment posts even when the gate fails.

### Scene 2: Both outcomes locally (45 s)

```bash
uv run python demos/m12_quality_gate.py
```

Real offline output, the two summaries:

```
## Agent quality gate: PASSED
**Pass rate:** 10/10 (100%)
...
## Agent quality gate: FAILED
**Pass rate:** 7/10 (70%)
| Metric | Average |
|---|---|
| Answer Correctness | 0.74 |
| Answer Relevancy | 1.00 |
| Faithfulness | 0.25 |
**Blocking issues:**
- pass rate 70% < 80%
- Faithfulness average 0.25 < 0.70
- regression vs baseline: Answer Correctness, Faithfulness, GS-01, GS-02, GS-03
```

### Scene 3: The good PR (40 s)

Open the PR from `good-change`. Checks: `Offline tests + smoke eval` green, `Golden-dataset quality gate` green. The bot comment "Agent quality gate: PASSED".

### Scene 4: The bad PR (60 s)

Open the PR from `bad-change`. `Golden-dataset quality gate` red. Scroll the PR comment: pass rate 7/10, Faithfulness 0.25, the three blocking issues, the failing cases (GS-01 pricing, GS-02 refund policy, GS-03 API limits: "tools []"), and the regression deltas. Show the merge button blocked (branch protection requires the check; verify GitHub's current UI before recording).

Narration point: "One deleted line. The gate caught it before a customer did."

## Verify Before Recording

- [ ] Run both PRs once before the take; Actions minutes and (if live) API cost are real (verify current pricing)
- [ ] Offline vs live: if the secret is set, the PR numbers are live gpt-4.1 judge scores; re-capture the comment text you show
- [ ] No secrets in logs; the workflow only references `${{ secrets.OPENAI_API_KEY }}`

## Post-Production Notes

- Red border on the failing check and the blocking-issues list; teal on the passing PR
- Lower third on Scene 4: "Gate: pass rate ≥ 80%, critical metrics ≥ 0.7, ≤ 5 points below baseline"
