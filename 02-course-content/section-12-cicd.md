# Section 12: CI/CD for Agent Evaluation

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 12 (curriculum `01-curriculum/full-curriculum.md`, Module 12, ~21 min, 3 lectures)
> **Source of truth for code, numbers and outputs:** `14-quality-review/course2-bible.md` §7 (Module 12), §8.24, §10. Every output below was captured from a real run in **offline mode** (`OFFLINE=1`: deterministic mock LLM and mock judge, no API key).
> **Repo:** `04-code-examples/agent-eval-framework/`. The workflow is `.github/workflows/agent-eval.yml`. Run demos with `uv run python demos/<file>`.
> **Version banner for every code slide:** `Verified: openai 2.54.0 | deepeval 4.2.7 | streamlit 1.64.0 | Python 3.11+ | agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key`
> **Third-party UI (verify before recording):** GitHub branch-protection and Actions screens change often. Re-capture every GitHub screen live before recording.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 12.1 | The Agent Quality Gate: Evals That Block Bad Deploys | Teach + diagram | 7:00 | 905 |
| 12.2 | GitHub Actions Pipeline: Eval on Every PR | Build-along | 7:00 | 760 |
| 12.3 | Experiment Tracking & Quality Dashboards | Build-along | 7:00 | 735 |

Cue legend: see `section-10-performance.md`. Word counts are spoken words only.

---

## Lecture 12.1 — The Agent Quality Gate: Evals That Block Bad Deploys

| Field | Value |
|---|---|
| ID | 12.1 |
| Title | The Agent Quality Gate: Evals That Block Bad Deploys |
| Type | Teach + diagram |
| Target duration | 7:00 (905 spoken words) |
| Learning objectives | 1. Define a quality gate: which dataset, which metrics, which thresholds, and what happens on failure. 2. Choose between hard, soft and advisory gates. 3. Design a tiered evaluation strategy (every push, every PR, nightly) that balances cost, speed and coverage. |
| Prerequisites | 11.2 (baselines and `compare`) |
| Files used | `reports/quality_gate.py` (`evaluate_gate`), `config/eval_config.yaml` (`gates`), `reports/run_eval.py` (`SMOKE_IDS`), `.github/workflows/agent-eval.yml` (job list), `demos/m12_quality_gate.py`; diagrams D14 and D4 |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key

[AVATAR]
Two pull requests land on a Friday afternoon. One fixes typos. One "simplifies" the system prompt. Both have green unit tests. Both get approved. [PAUSE] Only one of them makes your agent invent refund terms. Which one would your pipeline stop?

[SLIDE 2: By the end of this lecture]
- Define a quality gate in four decisions
- Pick hard, soft or advisory for each check
- Tier your evals: every push, every PR, nightly

By the end of this lecture, you'll design a quality gate for an agent: what it checks, what it blocks, and how often it runs. You'll see it make that Friday decision in about a minute, offline, at zero cost.

[SLIDE 3: The quality gate]
Diagram: D14 (The CI quality gate), build 1 then build 2. "Code change → PR → GitHub Actions → eval run → compare to thresholds and baseline", then the split: green "merge" and red "block, with report in the PR".

A quality gate is an evaluation that can say no. A developer opens a pull request. CI runs the agent on the golden dataset, scores it, compares the scores to thresholds and to the baseline, and then either lets the merge happen or blocks it, with a report explaining why. You built every piece of this already. The gate just puts them in the merge path.

[SLIDE 4: A gate is four decisions]
- Dataset: which questions? (golden_support, 10 cases)
- Metrics: which scores? (correctness, relevancy, faithfulness)
- Thresholds: what is good enough? (from `eval_config.yaml`)
- Action: what happens on failure? (block, warn or report)

Every gate is four decisions. Which dataset: for us, the ten-case golden support set. Which metrics: answer correctness, answer relevancy and faithfulness. Which thresholds: they live in `eval_config.yaml`, not in the CI file, so the policy is reviewed like code. And which action: block, warn or just report. Who on your team should own each of those four decisions?

[CODE: `config/eval_config.yaml`, the `gates` block.]

```yaml
gates:
  smoke_pass_rate: 1.0            # every push (Module 12)
  pr_pass_rate: 0.8               # pull requests: >= 80% of golden cases pass
  critical_metric_min: 0.7        # no critical metric average may drop below this
  regression_tolerance: 0.05      # fail if a metric drops more than 5 points vs baseline
```

Here are our numbers. Smoke tests on every push must pass one hundred percent. On a pull request, at least eighty percent of golden cases must pass. No critical metric average may fall below point seven. And no metric may drop more than five points below the baseline. That last rule is the `compare` function from Lecture 11.2.

[CODE: `reports/quality_gate.py`, `evaluate_gate`.]

```python
def evaluate_gate(report: dict, min_pass_rate: float | None = None, critical_min: float | None = None) -> tuple[bool, list[str]]:
    g = gates()
    min_pass_rate = g["pr_pass_rate"] if min_pass_rate is None else min_pass_rate
    critical_min = g["critical_metric_min"] if critical_min is None else critical_min
    reasons = []
    if report["pass_rate"] < min_pass_rate:
        reasons.append(f"pass rate {report['pass_rate']:.0%} < {min_pass_rate:.0%}")
    for m in CRITICAL:
        v = report["averages"].get(m)
        if v is not None and v < critical_min:
            reasons.append(f"{m} average {v:.2f} < {critical_min:.2f}")
    return (not reasons, reasons)
```

And here's the gate in code. It returns two things: a yes or no, and a list of reasons. The reasons matter as much as the verdict. A gate that says "failed" with no explanation gets bypassed within a week. A gate that says "Faithfulness average point two five, below point seven" gets fixed.

[SLIDE 5: Where the numbers come from]
- Start from your baseline: 100% pass, metrics 0.98 to 1.00
- Leave room for judge noise: 80% pass, 0.7 per metric
- Tighten later, once live runs show your real variance

Where do eighty percent and point seven come from? Not from a textbook. Start from your baseline. Our agent passes every case and scores between point nine eight and one point oh. Then leave room for noise, because live judges wobble a few points from run to run. Eighty and point seven are deliberately loose starting values. After a few weeks of live runs, you'll see your real variance, and you can tighten them. What would happen if you started strict and the gate failed on noise every other day?

[SLIDE 6: Hard, soft, advisory]
- Hard gate: blocks the merge (pass rate, critical metrics, regression)
- Soft gate: warns but allows (cost per task up, latency up)
- Advisory: reports only (new metrics you are still calibrating)

Not every check should block. A hard gate blocks the merge. Use it for things you'd roll back a release over: pass rate, critical metrics, regressions. A soft gate warns but allows, which suits cost and latency creep. And advisory checks only report, which is where a new metric lives while you calibrate it against human judgment, like the GEval metrics from Module 4. Promote a check to hard only when you trust it.

[SLIDE 7: Tiered evaluation]
Diagram: D4 (agent eval pyramid) on the left. On the right, three stacked bands mapped to the workflow's jobs: bottom "every push: offline tests + 3-case smoke eval, ~1 min, $0"; middle "every PR: 10-case golden gate + PR comment + promptfoo suite, live if the secret is set (a few cents, verify current pricing)"; top "nightly: full capstone pipeline".

Running every metric on every commit is slow and costs money. So you tier it. On every push, the workflow runs the offline test suite plus a three-case smoke eval: one FAQ, one account action, one attack. About a minute, zero dollars. On every pull request, the full ten-case golden gate runs, live if the API key secret is set, plus the promptfoo red-team suite. That costs a few cents a run; verify with your first live run. And every night, the full capstone pipeline runs. Cheap and fast at the bottom. Broad and thorough at the top.

[SLIDE 8: Spend the eval budget where it matters]
- Skip the live gate when no agent file changed (path filters)
- Run the agent once, score with every metric
- Cheaper judge for PRs, strongest judge nightly

Three more ways to keep the bill small. First, a pull request that only touches the README doesn't need a live agent eval. GitHub Actions path filters can skip it. Our workflow runs on everything to keep it simple, so that's an easy upgrade. Second, run the agent once per case and score that one answer with every metric. Third, consider gpt-4.1-mini as the judge on pull requests, and keep gpt-4.1 for the nightly run, once you've checked the cheaper judge agrees with it.

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m12_quality_gate.py
```

[DEMO: Output after the banner (offline), the two decision lines and the blocking reasons only]

```text
10/10 passed (100%); averages {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}; wrote reports/results/eval_v1.json

===== PR #41: copy edits (good change): MERGE ALLOWED =====
...
7/10 passed (70%); averages {'Answer Correctness': 0.74, 'Answer Relevancy': 1.0, 'Faithfulness': 0.25}; wrote reports/results/eval_regressed.json

===== PR #42: 'simplify' the system prompt (bad change): MERGE BLOCKED =====
...
**Blocking issues:**
- pass rate 70% < 80%
- Faithfulness average 0.25 < 0.70
- regression vs baseline: Answer Correctness, Faithfulness, GS-01, GS-02, GS-03
```

Here's the Friday afternoon, replayed. Pull request forty-one, the copy edits: ten out of ten, merge allowed. Pull request forty-two, the simplified prompt: seven out of ten, merge blocked.

[SCREEN: Same output. Zoom on the three "Blocking issues" lines, one at a time.]

And look how many rules caught it. The pass rate is below eighty percent. Faithfulness is below point seven. And it regressed against the baseline, with the three exact case IDs. Three independent reasons. Even if someone loosened one threshold, the other two would still block it.

[SLIDE 9: When the evaluation itself fails]
- Agent failed the gate: red gate step, PR comment lists reasons
- Eval infrastructure failed (API outage, rate limit): red eval step, no comment
- Re-run infrastructure failures; never "fix" them by lowering thresholds

[AVATAR]
One more design question. What if the evaluation itself breaks? An API outage, a rate limit, an expired key. In our workflow, that's a failed "run evaluation" step, and no PR comment appears. A real quality failure fails the gate step and posts its reasons. So the PR comment tells you which kind you have. Re-run infrastructure failures. Never fix them by lowering thresholds.

[SLIDE 10: Recap]
- A gate: dataset, metrics, thresholds, action
- Hard gates block; soft gates warn
- Tier it: push, pull request, nightly

A gate is four decisions: dataset, metrics, thresholds and action. Hard gates block, soft gates warn, advisory checks report. And you tier it, so every push is cheap and every night is thorough.

### Recap

A quality gate turns a golden-dataset run into a merge decision with reasons; on our support agent it allowed the copy edits and blocked the prompt change for three independent reasons.

### Transition

So far the gate ran in your terminal. In Lecture 12.2, you'll put it in GitHub Actions, on every pull request, with the results posted as a PR comment.

### Speaker notes: common student mistakes / Q&A

- **Real tiers vs the curriculum's.** The curriculum's "$0.10 / $0.50 / $5" tier prices are not sourced; the workflow's own comments say push = ~1 min, $0 (offline) and PR = "a few cents" live. Quote those, and verify against a real live run.
- **Smoke set:** `SMOKE_IDS = ["GS-01", "GS-05", "GS-10"]` in `reports/run_eval.py`.
- **Critical metrics** in `evaluate_gate` are Faithfulness, Answer Correctness and Answer Relevancy (bible §10).
- **The regression line** in the demo comes from `compare(load_baseline("support_v1"), report)` in `demos/m12_quality_gate.py`; in CI the same check runs inside `reports.quality_gate --baseline support_v1`.
- All numbers are offline. The PR numbers (#41, #42) are labels in the demo, not real GitHub PRs.

---

## Lecture 12.2 — GitHub Actions Pipeline: Eval on Every PR

| Field | Value |
|---|---|
| ID | 12.2 |
| Title | GitHub Actions Pipeline: Eval on Every PR |
| Type | Build-along |
| Target duration | 7:00 (760 spoken words; the rest is reading YAML and output) |
| Learning objectives | 1. Read and adapt the course workflow: jobs, triggers, permissions and the offline fallback. 2. Keep the API key in a repository secret and make forks safe. 3. Post the gate's Markdown summary as a single, updating PR comment and fail the job only after the comment is posted. |
| Prerequisites | 12.1 |
| Files used | `.github/workflows/agent-eval.yml`, `reports/run_eval.py`, `reports/quality_gate.py`, `demos/m12_quality_gate.py` |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+ | uv
- GitHub Actions: checkout@v4, setup-uv@v6, upload-artifact@v4

[AVATAR]
A gate that only runs on your laptop is a suggestion. Someone forgets to run it, or runs it on the wrong branch, and the bad prompt ships anyway. [PAUSE] So let's make GitHub run it on every pull request, and post the verdict where the reviewer can't miss it.

[SLIDE 2: By the end of this lecture]
- Read the four jobs in `agent-eval.yml`
- Store the API key as a secret, with an offline fallback
- Post the gate summary as a PR comment

You'll walk through the course's real workflow file, job by job. Then you'll see the exact comment it posts on a pull request, for a good change and a bad one.

[SCREEN: VS Code, `.github/workflows/agent-eval.yml`, top of the file: the `on:` block, `permissions:` and the job names `tests`, `quality-gate`, `redteam`, `nightly`.]

```yaml
on:
  push:
  pull_request:
    branches: [main]
  schedule:
    - cron: "17 3 * * *"
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write
```

Four triggers: every push, pull requests into main, a nightly schedule at three seventeen in the morning, and a manual button. And look at permissions. Read the code, write pull-request comments. Nothing more. Always give a workflow the smallest permissions it needs. Why seventeen minutes past? Because lots of scheduled jobs start on the hour, and runners are busiest then.

[SLIDE 3: Four jobs]
| Job | Trigger | What it does |
|---|---|---|
| `tests` | every push | `uv sync --locked`, offline pytest, 3-case smoke eval |
| `quality-gate` | PR to main, manual | golden eval → gate → PR comment → fail if gate failed |
| `redteam` | PR, schedule, manual | promptfoo 0.123.1 suite against the real agent |
| `nightly` | schedule | full capstone pipeline |

Four jobs. `tests` runs on every push: install with the lock file, run the offline test suite, run the smoke eval. `quality-gate` runs on pull requests, after `tests` passes. `redteam` runs the promptfoo suite from Module 8 against the real agent. And `nightly` runs the whole capstone pipeline you'll build in Module 14.

[CODE: `.github/workflows/agent-eval.yml`, the `tests` job steps.]

```yaml
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: "3.11"
      - run: uv sync --locked
      - run: uv run pytest -q --junitxml=reports/results/pytest.xml
      - run: uv run python -m reports.run_eval --smoke --out reports/results/smoke.json
```

The `tests` job is short on purpose. `uv sync locked` installs exactly the versions in the lock file, so CI tests what you tested. Then the offline test suite, all five layers of the pyramid, in seconds. Then the smoke eval on three golden cases. No API key, no cost. If this job fails, nothing else even starts, because the gate job says `needs: tests`. Why pay for a live eval on code that doesn't install?

[CODE: `.github/workflows/agent-eval.yml`, the `quality-gate` job's evaluation and gate steps.]

```yaml
      - name: Run evaluation (live when the secret is set)
        run: |
          if [ -n "$OPENAI_API_KEY" ]; then export OFFLINE=0; else export OFFLINE=1; fi
          echo "OFFLINE=$OFFLINE"
          uv run python -m reports.run_eval --out reports/results/eval.json
      - name: Apply the quality gate
        id: gate
        run: |
          set +e
          uv run python -m reports.quality_gate reports/results/eval.json \
            --summary reports/results/summary.md --baseline support_v1
          echo "exit=$?" >> "$GITHUB_OUTPUT"
```

Now the heart of it. Step one runs the evaluation. If the `OPENAI_API_KEY` secret exists, it runs live. If not, it runs offline. That fallback matters for forks: GitHub doesn't give secrets to pull requests from forks, so a contributor's PR still gets a gate, just an offline one. The job also prints which mode it used, so nobody mistakes an offline pass for a live one.

Step two applies the gate. Notice `set plus e`. It tells the shell not to stop on failure. The gate's exit code is saved as a step output instead. Why would you want a failing gate to keep going?

[CODE: `.github/workflows/agent-eval.yml`, the comment, artifact and final steps.]

```yaml
      - name: Comment on the pull request
        if: github.event_name == 'pull_request'
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh pr comment ${{ github.event.pull_request.number }} --body-file reports/results/summary.md --edit-last || gh pr comment ${{ github.event.pull_request.number }} --body-file reports/results/summary.md
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: eval-${{ github.sha }}
          path: reports/results/
          retention-days: 30
      - name: Fail if the gate failed
        if: steps.gate.outputs.exit != '0'
        run: exit 1
```

Here's why. Step three posts the summary as a PR comment, using the GitHub CLI. `edit last` updates the bot's previous comment instead of adding a new one on every push, and the fallback after the two bars creates the first one. Step four uploads the full results as an artifact, kept for thirty days, even when things fail. And only then, step five fails the job. Comment first, fail last. A blocked PR always explains itself.

[SLIDE 4: Secrets and safety]
- Add `OPENAI_API_KEY` under Settings → Secrets and variables → Actions (verify current UI)
- Use a separate key with a spending limit for CI (verify current UI)
- Make "Golden-dataset quality gate" a required check in branch protection

Three setup steps on GitHub, and verify the screens, because GitHub moves them. Add the key as a repository secret. Use a separate key for CI, with a spending limit, so a runaway loop can't drain your main account. And mark the quality-gate check as required in branch protection. Without that last step, the gate turns red, and the merge button still works.

[SCREEN: Terminal. Run the same commands CI runs, through the demo.]

```bash
uv run python demos/m12_quality_gate.py
```

[DEMO: The PR comment Markdown for the bad change, exactly as `gh pr comment` posts it (offline)]

```text
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

This Markdown is exactly what lands on the pull request. A verdict. A score table. The blocking reasons. A collapsible list of failing cases. And look at the failing cases: tools, empty brackets. The agent didn't even search the knowledge base. A reviewer can see the root cause without opening a terminal.

[SCREEN: GitHub pull request page, "Conversation" tab: the same comment rendered by GitHub, with the red failed check "Golden-dataset quality gate" and the disabled merge button. Re-capture live before recording.]

And here it is rendered on GitHub, next to the red required check. The good change from PR forty-one gets the same comment format with "PASSED" and a green check.

[SLIDE 5: Recap]
- Four jobs: tests, quality gate, red team, nightly
- Secret for live runs, offline fallback for forks
- Comment first, fail last

Four jobs, tiered by trigger. A secret for live runs, with an offline fallback so forks still get a gate. And comment first, fail last, so every blocked PR explains itself.

### Recap

`agent-eval.yml` runs the golden-dataset gate on every pull request, posts the Markdown summary as an updating PR comment, uploads the results, and fails the job only after the comment is posted.

### Transition

Every PR now leaves a result behind. In Lecture 12.3, you'll collect those results, compare versions side by side, and put them on a dashboard.

### Speaker notes: common student mistakes / Q&A

- **GitHub screens must be captured live.** This build environment has no GitHub PR; the comment shown in the DEMO cue is the real Markdown the gate writes. Re-capture the rendered PR page, the Actions run and the branch-protection screen live before recording, and verify current menu names.
- **Forks:** GitHub withholds repository secrets from fork PRs by default, so the job falls back to offline mode; the `echo "OFFLINE=$OFFLINE"` line shows which mode ran. Do not suggest `pull_request_target` to get secrets into fork runs without a security review.
- **`--edit-last`** edits the last comment made by the same user (the Actions bot); if none exists it errors and the `||` fallback creates one.
- **Cost:** a live PR run is "a few cents" per the workflow comment; measure on your first live run (verify current pricing).
- **The curriculum's workflow** (pip + `actions/github-script` comment, `tests/eval_full.py`) is superseded by this file; there is no `eval_smoke.py` (use `reports.run_eval --smoke`).

---

## Lecture 12.3 — Experiment Tracking & Quality Dashboards

| Field | Value |
|---|---|
| ID | 12.3 |
| Title | Experiment Tracking & Quality Dashboards |
| Type | Build-along |
| Target duration | 7:00 (735 spoken words; the rest is the dashboard walk-through) |
| Learning objectives | 1. Log every evaluation run as a versioned experiment and compare two runs metric by metric. 2. Read a quality dashboard: gate status, pass rate, category breakdown, trend and case details. 3. Decide what a team view and a leadership view each need. |
| Prerequisites | 12.2 |
| Files used | `reports/experiments.py` (`log_run`, `runs`, `compare_runs`), `reports/quality_dashboard.py`, `demos/m12_experiment_comparison.py`, `demos/m12_quality_dashboard.py`, `Makefile` (`make dashboard`) |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | streamlit 1.64.0
- Python 3.11+ | OFFLINE=1 runs without a key

[AVATAR]
Your manager asks: "Is version one point three better than one point two?" You open two CI logs in two tabs and start squinting at numbers. [PAUSE] There's a better answer, and it takes one function call. Then let's give your manager a page they can open without asking you at all.

[SLIDE 2: By the end of this lecture]
- Log every eval run as an experiment
- Compare two versions metric by metric
- Read a quality dashboard in 30 seconds

You'll log evaluation runs as experiments, compare two versions side by side, and open a Streamlit quality dashboard built from the same files.

[CODE: `reports/experiments.py`, the `row` built inside `log_run`.]

```python
row = {"version": version, "ts": datetime.now(UTC).isoformat(timespec="seconds"), "notes": notes,
       "pass_rate": report["pass_rate"], "averages": report["averages"], "total": report["total"],
       "categories": _by_category(report)}
```

An experiment is one line in a file. `log_run` appends a row to `reports/results/experiments.jsonl`: the version, a timestamp, your notes, the pass rate, the metric averages, and the pass rate per category. One JSON object per line. It's boring on purpose. You can grep it, diff it, or load it into anything.

[SLIDE 3: Tag runs so you can find them]
- Version: what changed (v1.3, or v1.3 plus a short commit SHA)
- Notes: why ("grounding rule restored")
- Dataset: what was asked (golden_support)

Tag every run so you can find it later. The version says what changed. In CI, add the short commit SHA to the version string. The notes say why. And the report already records the dataset. Six months from now, "v1.3, grounding rule restored" will save you an afternoon.

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m12_experiment_comparison.py
```

[DEMO: Output after the banner (offline)]

```text
Pass rate: v1.2 70% -> v1.3 100% (+30%)
  Answer Correctness   +0.240
  Answer Relevancy     +0.000
  Faithfulness         +0.750
Improved: ['Answer Correctness', 'Faithfulness']  Regressed: []
```

The demo logs two runs. Version one point two is the shorter prompt from Module 11. Version one point three restores the grounding rule. `compare_runs` answers the manager's question in five lines. Pass rate up thirty points. Faithfulness up point seven five. Correctness up point two four. Nothing regressed. Which line would you paste into the release notes?

[SLIDE 4: Two audiences, two views]
- Team view: every metric, every case, the trend across versions
- Leadership view: one status, one trend, one cost (Module 13.3)
- Same data underneath; different questions on top

Before the dashboard, a design rule. Your team and your leadership ask different questions. The team asks: which case broke, and since when? Leadership asks: is it safe to ship, and is it getting better? Same data underneath, different pages on top. Today you build the team view. In Lecture 13.3, you'll build the leadership scorecard.

[SCREEN: Terminal.]

```bash
uv run python demos/m12_quality_dashboard.py
```

[DEMO: Output after the banner (offline)]

```text
10/10 passed (100%); averages {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}; wrote reports/results/eval.json
Quality gate: PASS   pass rate 100% (10/10)
  Answer Correctness   0.98
  Answer Relevancy     1.00
  Faithfulness         1.00
  faq          3/3
  account      3/3
  escalation   2/2
  security     2/2
History: v1.0=100%

Launch the app: uv run streamlit run reports/quality_dashboard.py  (or: make dashboard)
```

This demo writes a fresh evaluation, then prints the dashboard's numbers as text: gate status, pass rate, three metric averages, and all four categories green. Now open the real app.

[SCREEN: Browser at `localhost:8501` after `make dashboard`. Pan top to bottom: the title "TechCorp Agent Quality Dashboard"; four metric tiles ("Quality gate PASS", "Pass rate 100%", "Faithfulness 1.00", "Answer relevancy 1.00"); the "By category" table; the "Trend across versions" line chart; the "Case details" table with per-metric scores; the caption about offline mode. Re-capture live before recording.]

```bash
make dashboard
```

Here's the Streamlit dashboard. Four tiles across the top: the gate, the pass rate, faithfulness and relevancy. Below, the category table. Then the trend line across every version you've logged, which is where a slow slide becomes visible. And at the bottom, every case with its scores, so a red tile is two clicks from the answer that caused it.

[SLIDE 5: What the trend shows that the gate can't]
Diagram: a line chart of faithfulness across six versions, v1.0 to v1.5: 1.00, 0.97, 0.94, 0.91, 0.88, 0.85, each step labelled "−0.03, gate: pass". A dashed Teal line at the v1.0 baseline. Footnote: "illustrative".

Why bother with the trend chart when the gate already blocks regressions? Here's an illustrative case. Each release drops faithfulness by three points. Three is under the five-point tolerance, so every single release passes the gate. After five releases, you've lost fifteen points. The gate compares one step. The trend shows the whole staircase. If you see this pattern, re-baseline on purpose or tighten the tolerance. Have you seen a staircase like this in any metric you track?

[CODE: `reports/quality_dashboard.py`, the four tiles.]

```python
c1, c2, c3, c4 = st.columns(4)
c1.metric("Quality gate", gate_status(r))
c2.metric("Pass rate", f"{r['pass_rate']:.0%}", help=f"{r['passed']}/{r['total']} golden cases")
c3.metric("Faithfulness", f"{r['averages'].get('Faithfulness', 0):.2f}")
c4.metric("Answer relevancy", f"{r['averages'].get('Answer Relevancy', 0):.2f}")
```

The whole app is about a hundred lines. It reads the files the pipeline already writes. No database, no server. And the gate tile calls the same `evaluate_gate` function CI uses, so the dashboard can never disagree with the build.

[AVATAR]
Prefer a hosted dashboard? DeepEval's Confident AI platform and the Langfuse scores from Module 9 can both show this kind of history. The principle doesn't change: one source of results, and every view reads from it.

[SLIDE 6: Recap]
- Log every run: version, notes, scores
- Compare versions with one function call
- One results source; dashboards only read it

Log every run with a version and notes. Compare versions with one call instead of two browser tabs. And keep one source of results, with every dashboard reading from it.

[SLIDE 7: You can now]
- Design a tiered agent quality gate
- Run it on every PR with a PR comment
- Track experiments and show them on a dashboard

You can now design a quality gate, run it in GitHub Actions on every pull request, and track every result on a dashboard.

### Recap

`log_run` and `compare_runs` turn CI results into experiments (v1.2 → v1.3: pass rate +30 points, faithfulness +0.75), and the Streamlit dashboard reads the same files CI writes.

### Transition

Your gate protects every release. But what happens after release, when real users arrive? Module 13 watches production. Next, Lecture 13.1: drift, degradation and alerts.

### Speaker notes: common student mistakes / Q&A

- **History accumulates.** `reports/results/experiments.jsonl` grows every time `log_run` runs (the capstone appends too), so "History:" may show more versions on your machine. Delete `reports/results/` for a clean recording; it is git-ignored.
- **The Streamlit screen must be captured live** with `make dashboard` (port 8501 by default; verify). The text demo is the offline proof of the numbers.
- **Commit SHA:** `log_run` has no SHA field; put it in `version` or `notes` (for example `version=f"v1.3-{sha[:7]}"`).
- **Confident AI** is DeepEval's hosted platform; features and pricing change (verify). The course does not require an account.
- The curriculum's `ExperimentTracker` class is superseded by `reports/experiments.py`.
