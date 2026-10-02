# Lab 12.1: CI/CD Eval Pipeline with GitHub Actions

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 12.1 (file `lab-11-github-actions.md`) |
| **Module** | Module 12 — CI/CD for Agent Evaluation |
| **Lectures** | 12.1–12.3 |
| **Duration** | 60 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Put the golden-dataset evaluation behind a GitHub Actions quality gate: offline tests and a smoke eval on every push, a full evaluation with a PR comment on pull requests, and a failed check when the pass rate drops below 80%, a critical metric drops below 0.7, or a metric regresses more than 5 points. Prove it with one good and one bad pull request. |
| **Reference solution** | `.github/workflows/agent-eval.yml`, `reports/run_eval.py`, `reports/quality_gate.py`, `demos/m12_quality_gate.py` |
| **Verified on** | GitHub-hosted `ubuntu-latest`, `astral-sh/setup-uv@v6`, Python 3.11 (workflow as committed 2026-10-02; the local commands below verified offline) |

---

## Prerequisites

- Completed **Lab 3.1** and **Lab 11.1** (golden datasets, baselines)
- A GitHub account and your own repository containing the course repo (fork or push a copy)
- Optional: an `OPENAI_API_KEY` repository secret. Without it, the pull-request job runs the evaluation offline, so the gate still works.

---

## Setup Instructions

### 1. Run the pipeline locally first

Everything the workflow does can run on your machine:

```bash
cd 04-code-examples/agent-eval-framework
make test                       # what the "tests" job runs (offline)
make smoke                      # 3-case smoke eval: GS-01, GS-05, GS-10
make eval-offline               # golden eval + gate with --baseline support_v1
```

### 2. See a gate fail locally

```bash
uv run python -m reports.run_eval --prompt-variant regressed --out reports/results/eval_regressed.json
uv run python -m reports.quality_gate reports/results/eval_regressed.json --baseline support_v1; echo "exit code: $?"
```

`--prompt-variant regressed` runs the agent with the grounding rule deleted (Module 11). The gate prints the Markdown that becomes the PR comment and exits with code 1.

---

## Step-by-Step Instructions

### Step 1 — Read the workflow

Open `.github/workflows/agent-eval.yml`. Four jobs:

| Job | Trigger | What it does |
|---|---|---|
| `tests` | every push | `uv sync --locked`, `uv run pytest -q` (offline), smoke eval |
| `quality-gate` | pull request to main, manual | `reports.run_eval` (live if the `OPENAI_API_KEY` secret exists, else offline) → `reports.quality_gate --baseline support_v1` → PR comment via `gh pr comment` → fail the job if the gate failed |
| `redteam` | pull request, schedule, manual | Node 22 + `npx promptfoo@0.123.1 eval -c promptfooconfig.yaml` against the real agent |
| `nightly` | cron `17 3 * * *` | the full capstone pipeline |

### Step 2 — Write the gate job yourself

In your repository, create `.github/workflows/my-agent-eval.yml` with a `tests` job (copy it from the reference) and this quality-gate job. Write it, don't paste it: each step is one decision.

```yaml
name: My Agent Evaluation

on:
  push:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write          # needed to post the PR comment

jobs:
  quality-gate:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.11"
      - run: uv sync --locked
      - name: Run evaluation (live when the secret is set)
        run: |
          if [ -n "$OPENAI_API_KEY" ]; then export OFFLINE=0; else export OFFLINE=1; fi
          uv run python -m reports.run_eval --out reports/results/eval.json
      - name: Apply the quality gate
        id: gate
        run: |
          set +e
          uv run python -m reports.quality_gate reports/results/eval.json \
            --summary reports/results/summary.md --baseline support_v1
          echo "exit=$?" >> "$GITHUB_OUTPUT"
      - name: Comment on the pull request
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh pr comment ${{ github.event.pull_request.number }} --body-file reports/results/summary.md
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: eval-${{ github.sha }}
          path: reports/results/
      - name: Fail if the gate failed
        if: steps.gate.outputs.exit != '0'
        run: exit 1
```

Why `set +e` and a separate "Fail" step? So the PR comment and the artifact are posted **even when the gate fails**; the job still ends red.

If your repository root is above `04-code-examples/agent-eval-framework`, add `defaults: run: working-directory: 04-code-examples/agent-eval-framework` to the job and adjust the artifact path.

### Step 3 — A good pull request

Create a branch, make a harmless change (for example, reword the "Be helpful, concise, and professional" rule without changing its meaning), push, open a PR. Watch the checks: `tests` green, `quality-gate` green, and a comment "Agent quality gate: PASSED".

### Step 4 — A bad pull request

On another branch, delete the line `- Only state prices, limits and policies that appear in a knowledge base result` from `SYSTEM_PROMPT` in `agents/support_agent.py`. Push and open a PR. The gate fails and the comment lists the blocking issues and the failing cases.

### Step 5 — Make the check required

In the repository settings, add a branch protection rule (or ruleset) for `main` that requires the `quality-gate` check to pass before merging. GitHub's settings UI changes; verify the current steps in GitHub's docs. Now the bad PR cannot be merged.

### Step 6 — Track the experiment

```bash
uv run python demos/m12_experiment_comparison.py
uv run python demos/m12_quality_dashboard.py && make dashboard
```

`reports/experiments.py` appends every run to `reports/results/experiments.jsonl`, so you can compare versions and see trends on the dashboard.

---

## Expected Output

The gate on the regressed prompt (offline; also what the bad PR's comment says):

```
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
<details><summary>Failing cases</summary>
- `GS-01` 'What are your pricing plans?': lowest Faithfulness = 0.0, tools []
- `GS-02` 'What is your refund policy?': lowest Faithfulness = 0.0, tools []
- `GS-03` 'What are the API rate limits for the Pro plan?': lowest Faithfulness = 0.0, tools []
</details>
**Regression vs baseline:** YES
- Answer Correctness: 0.98 -> 0.74 (-0.24)
- Answer Relevancy: 1.00 -> 1.00 (+0.00)
- Faithfulness: 1.00 -> 0.25 (-0.75)
```

The good PR:

```
## Agent quality gate: PASSED
**Pass rate:** 10/10 (100%)
```

---

## Verification Checklist

- [ ] The pipeline runs locally (`make test`, `make smoke`, `make eval-offline`)
- [ ] Your workflow posts a PR comment and uploads `reports/results/` even when the gate fails
- [ ] The good PR passes; the bad PR fails with the three blocking issues shown above
- [ ] The `quality-gate` check is required on `main`
- [ ] No API key appears in the workflow file or in the logs (only `${{ secrets.OPENAI_API_KEY }}`)

---

## Common Pitfalls

1. **`gh pr comment` fails with a permissions error.** Add `permissions: pull-requests: write` to the workflow and pass `GH_TOKEN: ${{ github.token }}`.
2. **The workflow can't find the code.** If the student repo is a subfolder of your repository, set `working-directory` on the job.
3. **Gate failures vs infrastructure failures.** A timeout or rate limit from the API is not a quality failure. Retry, then mark the run inconclusive for a human; don't let a flaky provider block every merge.
4. **Live cost creep.** The PR job runs the full golden set on every push to the PR. Keep the live dataset small and the judge model chosen on purpose (verify current pricing).

---

## Extension Challenge

1. Add the `redteam` job (Node 22, promptfoo static suite) and make it required too.
2. Add a path filter so the quality gate only runs when `agents/`, `config/`, `datasets/` or `evaluators/` change.
3. Add a soft gate that warns (but does not fail) when the average LLM calls per task rise above the baseline.
