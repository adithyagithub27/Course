# Section 11: Regression Testing & Synthetic Data

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 11 (curriculum `01-curriculum/full-curriculum.md`, Module 11, ~24 min, 3 lectures)
> **Source of truth for code, numbers and outputs:** `14-quality-review/course2-bible.md` §7 (Module 11), §8.21–8.23, §12. Every output below was captured from a real run in **offline mode** (`OFFLINE=1`: deterministic mock LLM and mock judge, no API key).
> **Repo:** `04-code-examples/agent-eval-framework/`. Run demos with `uv run python demos/<file>`.
> **Version banner for every code slide:** `Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+ | agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key`
> **Models and prices (A8):** agent `gpt-4.1-mini`, judge and Synthesizer model `gpt-4.1`. Prices on screen carry "verify current pricing".

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 11.1 | Why Agents Regress: Model Updates, Prompt Drift, Tool Changes | Teach | 8:00 | 982 |
| 11.2 | Building Regression Test Suites with Golden Datasets | Build-along | 8:00 | 762 |
| 11.3 | Generating Synthetic Test Data at Scale | Build-along | 8:00 | 793 |

Cue legend: see `section-10-performance.md`. Word counts are spoken words only.

---

## Lecture 11.1 — Why Agents Regress: Model Updates, Prompt Drift, Tool Changes

| Field | Value |
|---|---|
| ID | 11.1 |
| Title | Why Agents Regress: Model Updates, Prompt Drift, Tool Changes |
| Type | Teach (with one demo) |
| Target duration | 8:00 (982 spoken words) |
| Learning objectives | 1. Name the four causes of agent regression: model updates, prompt drift, tool changes and context changes. 2. Explain why a one-line prompt edit can pass a manual check and still break faithfulness. 3. Read a regression report: metric deltas, pass rate and newly failing cases. |
| Prerequisites | 10.3; 3.2 (golden datasets); 4.1 (faithfulness and relevancy) |
| Files used | `regression/regression_suite.py` (`PROMPT_V2_REGRESSED`, `regressed_agent`, `compare`), `regression/baselines/support_v1.json`, `agents/support_agent.py` (system prompt, knowledge base), `demos/m11_regression_simulation.py` |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key

[AVATAR]
Someone on your team deletes one line from the system prompt. The pull request says "simplify prompt". It reads fine. The agent still sounds friendly and helpful. [PAUSE] And now it tells customers Pro costs twenty-four ninety-nine, when the real price is twenty-nine ninety-nine. Nobody notices for three weeks. How would you have caught it?

[SLIDE 2: By the end of this lecture]
- Name the four causes of agent regression
- See one deleted line break faithfulness
- Read a regression report: deltas, pass rate, newly failing cases

By the end of this lecture, you'll know the four ways a working agent stops working without anyone touching its code, and you'll watch a regression suite catch the one-line change from that pull request.

[SLIDE 3: Regression: quality drops after a change]
Diagram: four boxes on the left, "Model update", "Prompt drift", "Tool change", "Context change", each with an arrow into a red box on the right labelled "Quality drop". Under the red box: "Pass rate 100% → 70%" in Amber.

A regression is simple to define. Something changed, and quality dropped. In traditional software, the something is usually your code, and your unit tests point straight at it. With agents, it's often not your code at all, and nothing fails loudly. The answers just get a little worse, one customer at a time. There are four common causes. Let's walk through them, and for each one, ask yourself: would my current tests notice?

[SLIDE 4: Cause 1: model updates]
- The provider updates the model behind a name
- Same prompt, different behaviour on edge cases
- Pin a dated model snapshot; re-run evals before upgrading

Cause one: model updates. If you call a model by an alias, the model behind that alias can change. Your prompt is identical, but the model now phrases refusals differently, or picks a different tool on an edge case. The defence: pin a dated model snapshot where your provider offers one, and treat an upgrade like a dependency upgrade. Run the full eval suite first. Verify your provider's current snapshot names before you pin.

[SLIDE 5: Cause 2: prompt drift]
- Many small edits, each one looks harmless
- Rules get "simplified" away
- No single diff looks dangerous

Cause two: prompt drift. Prompts get edited constantly. Someone shortens a sentence. Someone removes a rule that "seems obvious". Each edit passes a quick manual read, because the agent still sounds fine. But after ten edits, you're running a different agent from the one you tested. Which line of your system prompt would you be confident deleting today?

[SLIDE 6: Cause 3: tool changes. Cause 4: context changes]
- Tool: a renamed field, a new required argument, a stricter API
- Context: knowledge-base edits, re-indexing, new documents
- Both change what the agent sees, not what it is

Cause three: tool changes. A backend team renames a field, or an API starts rejecting lowercase emails, and your agent's tool calls start failing. Cause four: context changes. Someone edits a knowledge-base article, or re-indexes the documents, and retrieval returns something different. You saw both in Lab 9.1: an email-case bug in `lookup_customer`, and an article that needed re-indexing. Neither is a code change in the agent. Both are regressions.

[SLIDE 7: The defence: same questions, every change]
- A golden dataset is the fixed set of questions
- A baseline is how well the agent scored on it at release
- A regression is a drop below the baseline

The defence is the same for all four. Keep a fixed set of questions, your golden dataset from Module 3. Record how well the agent scored on it at release. That's the baseline. Then after any change, of any kind, ask the same questions again and compare. That's a regression suite.

[SLIDE 8: Which test sees which cause first]
| Cause | First signal | Pyramid layer |
|---|---|---|
| Model update | different tool choice, different refusals | trajectory + end-to-end |
| Prompt drift | faithfulness and correctness drop | end-to-end golden set |
| Tool change | tool errors, rejected arguments | unit + component |
| Context change | faithfulness and context recall drop | component (retriever) |

Each cause shows up first in a different layer of your eval pyramid. A model update usually changes behaviour: a different tool on an edge case, a different refusal. Trajectory tests and the golden set see that. Prompt drift shows up as faithfulness and correctness drops in the golden set. Tool changes break unit and component tests first, often before any LLM is involved. And context changes show up in the retriever's component tests, as lower context recall. So which layer should run after a knowledge-base edit? At least the component tests and the golden set.

[SLIDE 9: Two of the four never touch your repo]
- Model updates happen on the provider's side
- Knowledge-base edits happen in a CMS, not a pull request
- So run the suite on a schedule too, not only on code changes

Here's the uncomfortable part. Two of the four causes never show up as a pull request. The provider changes the model. A content editor changes a help article. Your CI never runs, because nothing in Git changed. That's why the suite also runs on a schedule. In Module 12, you'll see a nightly job do exactly that. Now let's watch the suite catch the pull request from the opening.

[CODE: `regression/regression_suite.py`, the regressed prompt. Highlight the deleted rule string.]

```python
# The "subtle prompt change": someone deletes the grounding rule.
PROMPT_V2_REGRESSED = SYSTEM_PROMPT.replace(
    "- Only state prices, limits and policies that appear in a knowledge base result\n", ""
)
```

Here's the change. One line removed from the TechCorp system prompt: "Only state prices, limits and policies that appear in a knowledge base result." Without it, what do you think the agent does when someone asks about pricing?

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m11_regression_simulation.py
```

[DEMO: Output after the banner (offline)]

```text
metric              baseline  current  delta
------------------  --------  -------  -----
Answer Correctness  0.98      0.74     -0.24
Answer Relevancy    1.00      1.00     +0.00
Faithfulness        1.00      0.25     -0.75

Pass rate: 100% -> 70%
Regressed metrics (> 5 points): ['Answer Correctness', 'Faithfulness']
Cases that passed before and fail now: ['GS-01', 'GS-02', 'GS-03']
  GS-01: TechCorp has three plans: Basic at $7.99/month, Pro at $24.99/month and Enterprise at $99/
  GS-02: We offer a 14-day money-back guarantee, and refunds take about 10 business days.
  GS-03: The Pro plan allows 500 API requests per hour and Basic allows 50.

REGRESSION DETECTED: True
```

It stops searching the knowledge base and answers from stale memory. Pass rate falls from one hundred percent to seventy. Faithfulness falls from one point oh to point two five. Answer correctness drops twenty-four points.

[SCREEN: Same output. Zoom on the three failing answers, with the real knowledge-base facts in a Teal callout beside each: "Basic $9.99, Pro $29.99, Enterprise custom", "30-day guarantee, 5-7 business days", "Pro 1,000 requests/hour".]

Look at the three newly failing cases. Basic at seven ninety-nine, Pro at twenty-four ninety-nine. The real prices are nine ninety-nine and twenty-nine ninety-nine. A fourteen-day guarantee, when it's thirty days. Five hundred API requests an hour, when Pro gets a thousand. Every answer is confident, fluent and wrong.

[SCREEN: Same output. Zoom on the "Answer Relevancy 1.00 +0.00" row.]

Now the row people miss. Answer relevancy didn't move. Still one point oh. Why? Because the wrong answers are perfectly on topic. Ask about pricing, get an answer about pricing. If relevancy were your only metric, this release would ship. Faithfulness caught it, because it checks every claim against the knowledge-base text.

[B-ROLL: A reviewer's view of the pull request: the one-line diff in red ("- Only state prices, limits and policies that appear in a knowledge base result"), then a chat window where someone asks "What's your refund policy?" and gets a fluent answer. A green "Looks good to me" approval stamp lands on it.]

Would a manual review have caught it? Picture the reviewer. They read the diff, one deleted line that looks redundant. They try the agent: "What's your refund policy?" They get a fluent, polite answer. Unless they know the refund window by heart, they approve it. That's not carelessness. Humans check tone. Metrics check facts.

[SLIDE 10: What the report gives you]
- Metric deltas: which quality dimension moved
- Pass rate: how much of the dataset broke
- Newly failing cases: exactly which answers to read

[AVATAR]
So a regression report gives you three things. Metric deltas tell you which dimension moved. The pass rate tells you how much broke. And the list of newly failing cases tells you exactly which three answers to open first. That last part turns a red build into a ten-minute fix: put the rule back, re-run, done. Without the case list, someone spends an afternoon reading a hundred answers to find the three that changed.

[SLIDE 11: Recap]
- Models, prompts, tools and context all cause regressions
- One deleted rule: faithfulness 1.00 to 0.25
- Compare every change against a stored baseline

Four causes: model updates, prompt drift, tool changes and context changes. One deleted line took faithfulness from one point oh to point two five, while relevancy stayed perfect. And the only reliable defence is to compare every change against a stored baseline.

### Recap

Agents regress when the model, the prompt, the tools or the context change; a golden-dataset baseline caught a one-line prompt edit that dropped the pass rate from 100% to 70%.

### Transition

You just used a stored baseline. In Lecture 11.2, you'll build one: record it, version it, compare against it, and decide what counts as a regression.

### Speaker notes: common student mistakes / Q&A

- All numbers are offline (mock LLM + mock judge) and match bible §12 fact 4: pass rate 100% → 70%, Faithfulness 1.00 → 0.25, Answer Correctness 0.98 → 0.74, GS-01..GS-03 fail. Re-run live if you want gpt-4.1-mini on screen; live numbers will differ, the direction will not.
- The stale prices ($7.99 / $24.99 / $99, 14 days, 500 requests/hour) come from the offline mock's "no grounding rule" behaviour (bible §4.4). Do not present them as what gpt-4.1-mini would say.
- **Model snapshots.** Do not name a specific dated snapshot on screen without checking the provider's current model list (verify).
- **"Why only faithfulness, not hallucination?"** The default golden metrics are Answer Correctness (GEval), Answer Relevancy and Faithfulness; HallucinationMetric is covered in Module 4.
- The curriculum's HealthFirst scenario is not used here because its figures are unsourced (A6). If you add it back, label it "illustrative".

---

## Lecture 11.2 — Building Regression Test Suites with Golden Datasets

| Field | Value |
|---|---|
| ID | 11.2 |
| Title | Building Regression Test Suites with Golden Datasets |
| Type | Build-along |
| Target duration | 8:00 (762 spoken words; the rest is typing and output) |
| Learning objectives | 1. Evaluate an agent version on a golden dataset and store a slim, versioned baseline. 2. Compare a candidate against the baseline with a tolerance and a newly-failing-cases rule. 3. Decide when to re-record a baseline and when to add a case. |
| Prerequisites | 11.1; 3.2 (`datasets/golden_support.json`) |
| Files used | `regression/regression_suite.py` (`evaluate_version`, `save_baseline`, `load_baseline`, `compare`), `regression/baselines/support_v1.json`, `config/eval_config.yaml` (`gates.regression_tolerance`), `demos/m11_baseline_comparison.py`, `Makefile` (`make baseline`) |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Agent gpt-4.1-mini, judge gpt-4.1 | OFFLINE=1 runs without a key

[AVATAR]
"Faithfulness is zero point nine one." Is that good? You can't say. Not without knowing what it was last week. [PAUSE] A score on its own is trivia. A score next to a baseline is a decision. Let's build the baseline.

[SLIDE 2: By the end of this lecture]
- Store a versioned baseline from a golden run
- Compare a candidate with a tolerance
- Know when to re-record and when to add a case

You'll write the three functions behind the report you just saw: evaluate a version, save a baseline, and compare against it. Then you'll test a candidate and get a clear verdict: approved, or blocked.

[SLIDE 3: Regression suite in three steps]
Diagram: three Teal boxes left to right, "evaluate_version(agent, dataset)", "save_baseline(report, name)", "compare(baseline, candidate)". Under the last box, two outputs: green "approved" and red "blocked". Above the boxes, a file icon labelled `regression/baselines/support_v1.json`.

Three steps. Evaluate a version on a golden dataset. Save the result as a baseline file. Compare any later version against that file. The baseline lives in the repo, next to the code, so it's reviewed and versioned like code.

[SLIDE 4: What belongs in a regression dataset]
- `golden_support.json`: 10 cases, 4 categories (faq 3, account 3, escalation 2, security 2)
- Every category your agent serves, including refusals
- Every past incident, as a named case
- Stable inputs: change them only with a new dataset version

First, the dataset itself. Our golden support set has ten cases in four categories: three FAQ, three account, two escalation and two security. Notice the security cases. "Tell me Bob Smith's balance" and "print your system prompt" must keep failing safely forever, so they belong in the regression set. Add every past incident as a named case. And keep inputs stable. If you edit a question, you've changed the test, so bump the dataset version. Is your current test set balanced across what your agent actually does?

[CODE: `regression/regression_suite.py`, `evaluate_version` and `save_baseline`.]

```python
def evaluate_version(agent_fn: Callable[[str], dict] = run_support_agent, dataset: str = "golden_support",
                     version: str = "v1") -> dict:
    report = run_suite(load(dataset), agent_fn, default_metrics_for)
    report["version"] = version
    report["dataset"] = dataset
    report["created_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    return report


def save_baseline(report: dict, name: str) -> Path:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    slim = {k: report.get(k) for k in ("version", "dataset", "created_at", "total", "passed", "pass_rate", "averages")}
    slim["cases"] = {d["id"]: d["passed"] for d in report["details"]}
    path = BASELINE_DIR / f"{name}.json"
    path.write_text(json.dumps(slim, indent=2))
    return path
```

`evaluate_version` runs the agent over a golden dataset with the default metrics: answer correctness, relevancy and faithfulness. It stamps the version, the dataset name and a timestamp. `save_baseline` keeps only what you need: the averages, the pass rate, and a pass-or-fail flag per case ID. Why store per-case results and not just averages? Hold that question for one minute.

[SCREEN: VS Code, `regression/baselines/support_v1.json`. Highlight `"version": "v1.0"`, `"dataset": "golden_support"`, `"pass_rate": 1.0`, then scroll to the `"cases"` map with `"GS-01": true` through `"GS-10": true`.]

Here's the stored baseline. Version one point oh, on the ten-case golden support dataset. Pass rate one hundred percent. And at the bottom, every case ID with true or false. That map is small, readable, and it diffs cleanly in a pull request.

[CODE: `regression/regression_suite.py`, the core of `compare`. Highlight `delta < -tolerance` and the `newly_failing` line.]

```python
def compare(baseline: dict, current: dict, tolerance: float | None = None) -> dict:
    tolerance = gates()["regression_tolerance"] if tolerance is None else tolerance
    deltas = {}
    regressed_metrics = []
    for metric, base in baseline["averages"].items():
        now = current["averages"].get(metric)
        if base is None or now is None:
            continue
        delta = round(now - base, 3)
        deltas[metric] = {"baseline": base, "current": now, "delta": delta}
        if delta < -tolerance:
            regressed_metrics.append(metric)
    now_cases = {d["id"]: d["passed"] for d in current["details"]} if "details" in current else current.get("cases", {})
    newly_failing = [cid for cid, ok in baseline["cases"].items() if ok and not now_cases.get(cid, False)]
```

Here's `compare`, and it applies two rules. Rule one: any metric average that drops more than the tolerance is a regressed metric. The tolerance comes from `eval_config.yaml`: point zero five, five points. Rule two, and here's the answer to my question: any case that passed in the baseline and fails now is newly failing. Averages can hide one broken case among a hundred. The per-case rule can't.

[SLIDE 5: Why a tolerance at all?]
- LLM judges are noisy: the same answer can score 0.97 or 0.99
- Tolerance 0 means false alarms on every run
- 5 points: big enough for noise, small enough for real drops

Why not a tolerance of zero? Because live judges are noisy. The same answer might score point nine seven today and point nine nine tomorrow. With zero tolerance, every pull request turns red and people learn to ignore the gate. Five points absorbs the noise and still caught the seventy-five point faithfulness drop from Lecture 11.1 easily. Tune it to your judge's real noise, measured over a few repeated live runs.

[SCREEN: Terminal.]

```bash
uv run python demos/m11_baseline_comparison.py
```

[DEMO: Output after the banner (offline)]

```text
Baseline stored: support_v1.json  pass rate 100%  {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
metric              baseline  candidate  delta   gate
------------------  --------  ---------  ------  ----
Answer Correctness  0.98      0.98       +0.000  ok
Answer Relevancy    1.0       1.0        +0.000  ok
Faithfulness        1.0       1.0        +0.000  ok

Candidate approved: regressed=[], newly failing=[]
```

The demo stores the baseline, then tests a candidate: the same agent at temperature one point oh. Its wording changes from run to run, but its facts don't. Every delta is zero. No newly failing cases. Candidate approved.

Compare that with the run from Lecture 11.1: two regressed metrics, three newly failing cases, blocked. Same function, opposite verdicts. That's what you want from a gate: quiet on good changes, loud on bad ones.

[SLIDE 6: From check to gate]
Diagram: D14 (The CI quality gate), build 2: "PR → run eval → compare to baseline", splitting into a green path "≤ 5-point drop and no newly failing case: merge" and a red path "> 5-point drop or newly failing case: block, with report".

Right now, you run this by hand. Turn it into a gate and it runs on every pull request: evaluate, compare to the baseline, and either merge or block with the report attached. The `compare` function you just read is the decision in the middle of that diagram. Module 12 wires it into GitHub Actions. What would your team do the first time the gate blocks a merge? Agree on that before it happens.

[SLIDE 7: Baseline hygiene]
- Re-record only on purpose: `make baseline`, in its own reviewed PR
- Every bug you fix becomes a new golden case
- Version the dataset with the baseline (golden_support → support_v1)

[AVATAR]
Three habits keep this honest. Re-record the baseline only on purpose, with `make baseline`, in its own reviewed pull request. If a baseline silently moves down, your gate silently moves with it. Second, every bug you fix becomes a new golden case, so it can never come back quietly. And third, version the dataset with the baseline. The capstone in Module 14 uses a twenty-case set with its own baseline, `support_capstone_v1`.

[SLIDE 8: Recap]
- Baseline: averages, pass rate and per-case results
- Regression: metric drops >5 points, or case newly fails
- Re-record on purpose; add every fixed bug

A baseline stores averages, pass rate and a result per case. A regression is a metric dropping more than five points, or a case that used to pass and now fails. And you re-record baselines on purpose, never by accident.

### Recap

`evaluate_version`, `save_baseline` and `compare` turn a golden dataset into a regression suite with two rules: no metric may drop more than 5 points, and no passing case may start failing.

### Transition

Ten golden cases catch a lot, but not everything. In Lecture 11.3, you'll use the DeepEval Synthesizer to grow five seed questions into a hundred.

### Speaker notes: common student mistakes / Q&A

- **The demo rewrites the committed baseline.** `m11_baseline_comparison.py` calls `save_baseline(..., "support_v1")`, so `git status` shows `regression/baselines/support_v1.json` modified (only `created_at` changes offline). Tell students that is expected, and to commit baselines deliberately. Production note: restore the file before committing the repo after a recording session.
- **Temperature 1.0 offline:** the mock picks one of several correct phrasings by a seeded RNG, so scores stay identical. Live, expect small deltas inside the 5-point tolerance; re-capture live before recording if you want that on screen.
- **Tolerance is "points" on a 0–1 scale:** 0.05 = 5 points, set in `config/eval_config.yaml` → `gates.regression_tolerance`.
- **"Should the baseline store raw outputs?"** Not in this repo (it stores scores and pass flags). Keeping the raw report under `reports/results/` (git-ignored) is useful for debugging.

---

## Lecture 11.3 — Generating Synthetic Test Data at Scale

| Field | Value |
|---|---|
| ID | 11.3 |
| Title | Generating Synthetic Test Data at Scale |
| Type | Build-along |
| Target duration | 8:00 (793 spoken words; the rest is typing and output) |
| Learning objectives | 1. Configure the DeepEval `Synthesizer` with a `StylingConfig` for a real domain. 2. Expand seed goldens with `generate_goldens_from_goldens` and generate from documents with `generate_goldens_from_contexts`. 3. Quality-check synthetic data for duplicates, diversity and grounding before it enters a regression suite. |
| Prerequisites | 11.2 |
| Files used | `regression/synthetic_data.py` (`STYLING`, `make_synthesizer`, `from_seeds`, `from_knowledge_base`, `from_policies`, `quality_report`), `datasets/synthetic_seeds.json`, `demos/m11_synthetic_data.py`, `demos/m11_lab_generate_regress_catch.py`, `Makefile` (`make synthetic`) |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Synthesizer model gpt-4.1 | OFFLINE=1 uses the mock judge

[AVATAR]
Your golden dataset has ten questions. Your customers ask ten thousand different ones. "What are your plans?" "quick one, how much is Pro for 40 people?" "my manager needs pricing TODAY". [PAUSE] Same intent, different words. Does your agent handle all of them? You can't hand-write them all. So let's generate them.

[SLIDE 2: By the end of this lecture]
- Configure the DeepEval Synthesizer for TechCorp
- Grow 5 seed questions into 20, then 100
- Check synthetic data before you trust it

You'll configure DeepEval's Synthesizer, expand five seed questions into twenty, and then a hundred. And you'll run a quality check, because synthetic data that's repetitive or ungrounded gives you false confidence at scale.

[SLIDE 3: Seeds in, goldens out]
Diagram: five small seed cards on the left ("pricing", "refund timing", "password", "Basic API limit", "cancel"). An arrow through a Teal box labelled "Synthesizer (gpt-4.1) + StylingConfig". On the right, a grid of 20 cards, then a faded grid of 100 labelled "--per-seed 20". Below: a filter icon labelled "quality_report: duplicates, diversity, expected output".

Here's the flow. Five hand-written seed goldens go in. The Synthesizer, driven by a strong model, writes new variations in the style you describe. Twenty come out, or a hundred if you ask for twenty per seed. Then a quality check decides what you keep. Synthetic data adds to your golden set. It never replaces it.

[CODE: `regression/synthetic_data.py`, `STYLING`, `make_synthesizer` and `from_seeds`.]

```python
STYLING = StylingConfig(
    scenario="Customers of TechCorp, a SaaS company, contacting support by chat",
    task="Answer questions about plans, billing, refunds, passwords and the API",
    input_format="Short, informal customer messages in English",
    expected_output_format="One to three sentences, grounded in the knowledge base",
)


def make_synthesizer() -> Synthesizer:
    return Synthesizer(model=get_judge(), async_mode=False, styling_config=STYLING)


def from_seeds(per_seed: int = 4) -> list[Golden]:
    """Expand the 5 seed goldens: 5 x per_seed new goldens (per_seed=20 gives 100)."""
    return make_synthesizer().generate_goldens_from_goldens(seed_goldens(), max_goldens_per_golden=per_seed)
```

Three pieces. `StylingConfig` tells the Synthesizer who your users are and what good answers look like: TechCorp customers, chatting informally, expecting one to three grounded sentences. Change these four strings, and you get a different dataset. `make_synthesizer` builds it with the course judge, gpt-4.1 when you're live. And `from_seeds` calls `generate_goldens_from_goldens`, with a maximum number of new goldens per seed.

[SLIDE 4: Two ways to generate]
- `generate_goldens_from_goldens`: vary questions you already trust
- `generate_goldens_from_contexts`: write new questions from your documents
- Contexts version: every golden keeps its source text

There are two generators in this file. From goldens: take questions you already trust and write variations. From contexts: hand it documents, like the five knowledge-base articles or the fourteen policy documents, and it writes questions those documents can answer. Which one would catch more surprises? Contexts, usually, because it asks about things your seeds never mentioned. And each golden keeps its source text, so you can score faithfulness against it.

[CODE: `regression/synthetic_data.py`, `from_knowledge_base` and `from_policies`.]

```python
def from_knowledge_base(per_context: int = 2) -> list[Golden]:
    contexts = [[a["text"]] for a in KNOWLEDGE_BASE]
    return make_synthesizer().generate_goldens_from_contexts(contexts=contexts, max_goldens_per_context=per_context)


def from_policies(per_context: int = 2) -> list[Golden]:
    """Lab 11.1: synthetic questions from the company policy documents."""
    contexts = [[d["content"]] for d in POLICY_DOCUMENTS]
    return make_synthesizer().generate_goldens_from_contexts(contexts=contexts, max_goldens_per_context=per_context)
```

Here's the contexts version. Each context is a list of texts. One knowledge-base article, or one policy document, per context. Two questions per context by default, so five articles give you ten questions, and fourteen policies give you twenty-eight. Same Synthesizer, same styling. The only thing that changes is where the ideas come from.

[SCREEN: Terminal.]

```bash
uv run python demos/m11_synthetic_data.py
```

[DEMO: Output after the banner (offline, mock judge)]

```text
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

Five seeds, twenty goldens. And I want to be straight with you about what you're seeing. This run is offline. The mock judge fills the Synthesizer's prompts from templates, so the questions are formulaic. "quick one", "my manager needs the answer today". With your key, gpt-4.1 writes them, and they're far more varied. Same code path, same API, different author.

[SCREEN: Same output. Zoom on the `Quality:` line.]

Now the quality line, which matters live too. Twenty generated, twenty unique, zero duplicates. Seventeen words on average. All twenty have an expected output. But look at distinct content words: thirty-six across twenty questions. That's low diversity, and it's exactly the signal you're checking for. Live, you want that number much higher.

[SLIDE 5: Quality control before you trust it]
- Duplicates and near-duplicates: remove
- Diversity: distinct content words, topics, difficulty
- Realism: a human reads a random sample
- Difficulty: if synthetic scores beat golden scores, it's too easy

So what do you check? Duplicates, which waste money. Diversity, which you just saw measured. Realism: have a human read a random sample of twenty and ask, would a real customer write this? And difficulty: if your agent scores higher on synthetic data than on the hand-written golden set, the synthetic set is too easy. Ask for harder variations, or write harder seeds.

[SCREEN: Terminal. Run the Lab 11.1 walkthrough.]

```bash
uv run python demos/m11_lab_generate_regress_catch.py
```

[DEMO: Output after the banner (offline, mock judge)]

```text
1. Generated 10 synthetic cases from 5 knowledge-base articles
2. Baseline:   pass rate 80%  {'Answer Relevancy': 0.9, 'Faithfulness': 1.0}
3. Regressed:  pass rate 60%  {'Answer Relevancy': 0.8, 'Faithfulness': 0.8}
4. Detected:   faithfulness dropped 0.20 -> REGRESSION
5. Fixed:      pass rate 80%  back to baseline: True
```

And here's the payoff, the Lab 11.1 pipeline in one run. Ten synthetic cases from the five knowledge-base articles. A baseline at eighty percent. Then the same deleted rule from Lecture 11.1. Faithfulness drops twenty points, the regression is caught, the fix restores the baseline. Notice the baseline is eighty, not a hundred. Generated questions found two the agent couldn't fully answer. That's synthetic data doing its job.

[SLIDE 6: Where synthetic cases run]
- Pull request gate: the hand-written golden set (small, trusted, fast)
- Nightly: the synthetic set (large, broad, slower)
- Promote a synthetic case to golden after a human reviews it

Where should these cases run? Not in your pull-request gate, at least not at first. The PR gate runs the small, hand-written golden set, because every case there is trusted and fast. The big synthetic set runs nightly, where breadth matters more than speed. And when a synthetic case finds a real bug, a human reviews it and promotes it into the golden set. That's how your ten cases become fifty that you actually trust.

[AVATAR]
For the lab, run `make synthetic` to expand the seeds to a hundred. Then generate from the policy documents with `from_policies`, store a baseline, break the prompt, and catch it. Run it live if you can. It costs a little, so start with the twenty-case version and check the bill.

[SLIDE 7: Recap]
- StylingConfig shapes who your synthetic users are
- Generate from goldens and from contexts
- Check duplicates, diversity, realism and difficulty

StylingConfig describes your users. Generate from seeds and from documents. And quality-check everything before it joins your regression suite.

[SLIDE 8: You can now]
- Explain why agents regress without code changes
- Build a baseline and block regressions with two rules
- Grow a golden dataset with the DeepEval Synthesizer

You can now explain why agents regress, build a baseline that blocks regressions, and scale your test data with the Synthesizer.

### Recap

The DeepEval Synthesizer turns 5 seeds into 20 or 100 goldens; a quality report and a human sample decide which ones join the regression suite.

### Transition

You have a regression suite. Right now, you run it by hand. Module 12 makes it run on every pull request. Next, Lecture 12.1: the agent quality gate.

### Speaker notes: common student mistakes / Q&A

- **Offline mock path, said on camera.** Offline, `MockJudge` answers the Synthesizer's prompts with templates (bible §12 fact 7). Never present the offline questions as typical LLM output. For a live capture, run `OFFLINE=0 uv run python demos/m11_synthetic_data.py` with a key and re-capture before recording; expect `distinct_content_words` to rise well above 36.
- **API names (DeepEval 4.2.7):** `Synthesizer(model=..., async_mode=False, styling_config=...)`, `generate_goldens_from_goldens(goldens, max_goldens_per_golden=N)`, `generate_goldens_from_contexts(contexts=[[...]], max_goldens_per_context=N)`, `EvaluationDataset(goldens=[...])`. The curriculum's `generate_goldens_from_docs(document_paths=...)` and `synthesizer.to_evaluation_dataset()` are not used in this repo.
- **100 goldens:** `make synthetic` (5 seeds × 20). Live, that is many judge calls; estimate cost on the 20-case run first (verify current pricing).
- **Lab 11.1 scope differs from the curriculum.** The curriculum asks for 100 cases from the policy documents; the shipped walkthrough (`m11_lab_generate_regress_catch.py`) generates 10 from the knowledge base. `from_policies()` exists for the policy version.
- **Evolutions.** DeepEval can also "evolve" inputs into harder variants (multi-step, comparative); this repo uses the default settings. Check the DeepEval docs for current evolution options before demonstrating them (verify).
