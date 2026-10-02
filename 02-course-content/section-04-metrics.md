# Section 4: Evaluation Metrics Deep Dive

> **Course:** AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python (Course 2)
> **Section runtime:** ≈32 min (4 lectures, plus Lab 4.1)
> **Source of truth:** `01-curriculum/full-curriculum.md` (Module 04) for objectives; `14-quality-review/course2-bible.md` for metrics, versions, commands and outputs. If a script and the code disagree, the code wins.
> **On-screen footer for every code or API slide:** "Verified: openai 2.54.0 | deepeval 4.2.7 (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1."
> **Cue legend:** see `section-00-welcome.md`. Commands run from `04-code-examples/agent-eval-framework/`. Outputs are offline runs (`OFFLINE=1`: deterministic mock LLM and mock judge); offline scores are teaching numbers, not live gpt-4.1 scores. Code-along lectures run below 140 words per minute to leave room for code and output. Word counts are spoken words only, counted by the section checker.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 4.1 | LLM Quality Metrics: Relevance, Faithfulness, Coherence | DM | 8:00 | 1011 |
| 4.2 | Agent-Specific Metrics: Task Completion, Tool Correctness, Goal Accuracy | DM | 8:00 | 987 |
| 4.3 | LLM-as-Judge: How to Use One AI to Grade Another | SC | 8:00 | 820 |
| 4.4 | Custom Metrics: G-Eval & Building Your Own Evaluator | SC | 8:00 | 779 |

**Section guardrails (do not deviate on screen):** DeepEval 4.2 facts. `HallucinationMetric` is higher-is-better (share of `context` items the answer agrees with) and passes at score ≥ threshold (0.7 in our policy); never say "lower is better, threshold 0.3". `BiasMetric` and `ToxicityMetric` are also higher-is-better in 4.2 (1.0 = nothing biased or toxic found). `FaithfulnessMetric` fails claims that contradict the retrieval context; unsupported "borderline" claims pass unless `penalize_ambiguous_claims=True`. `ToolCorrectnessMetric` compares `tools_called` with `expected_tools` by name and still takes a `model=`. There is no built-in `CoherenceMetric`; coherence is a GEval criterion. Evaluation params are `SingleTurnParams`. The judge is `get_judge()`: gpt-4.1 live, the mock judge offline.

---

## Lecture 4.1 — LLM Quality Metrics: Relevance, Faithfulness, Coherence

| Field | Value |
|---|---|
| ID | 4.1 |
| Title | LLM Quality Metrics: Relevance, Faithfulness, Coherence |
| Type | DM (teach plus one metric-comparison demo) |
| Target duration | 8:00 (1,120 words at 140 wpm; 1,011 spoken) |
| Learning objectives | 1. Explain what Answer Relevancy, Faithfulness, Hallucination and GEval correctness each measure, and which test case fields each needs. 2. Tell correctness from faithfulness, and faithfulness from hallucination. 3. Read a five-response, four-metric table and explain why the metrics disagree. |
| Prerequisites | Section 3 (Project 1) |
| Files used | `demos/m04_metric_comparison.py`; `evaluators/metrics.py`; `config/eval_config.yaml`; Diagram D7 (`D7-metric-taxonomy.svg`) |

### Script

[AVATAR]
The customer asks about API limits for the Pro plan. The agent says: "The Pro plan allows one thousand API requests per hour, and bursts of five thousand per minute are free." Relevancy: one. Correctness: one. Faithfulness: zero. [PAUSE] Three metrics, one answer, and they disagree completely. Which one do you believe? By the end of this lecture, all three, because each is answering a different question.

[SLIDE 1: LLM Quality Metrics]
- Know what each quality metric measures
- Know which fields each one needs
- Explain why metrics disagree

By the end of this lecture, you'll be able to pick the right quality metric for a failure, and explain a table of scores that seem to contradict each other.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Judge `gpt-4.1` live; mock judge offline
- Demo: `demos/m04_metric_comparison.py`

[SLIDE 3: Agent quality metrics]
Diagram: D7 builds 1 and 2: root "Agent quality metrics", left branch "LLM quality" with leaves relevance, faithfulness, coherence, hallucination, bias, toxicity. The right branch ("Agent behaviour") stays greyed out for Lecture 4.2.

In Project 1, you used three metrics. Now let's look at the whole map. Agent metrics split into two families. LLM quality metrics judge the text the agent wrote. Agent behaviour metrics judge what it did: its tools and steps. This lecture is the left branch: relevance, faithfulness, coherence, hallucination, bias and toxicity. Next lecture, the right branch.

[SLIDE 4: Answer Relevancy]
- Question: does it address what was asked?
- Needs: input, actual output
- Score: share of statements that are relevant
- Our threshold: 0.7

Start with answer relevancy. The judge splits the answer into statements, then asks of each one: does this help answer the question? The score is the share of relevant statements. So a focused answer scores high, and an answer padded with unrelated facts scores lower. It needs only the question and the answer, which makes it cheap to apply everywhere. It's your first defence against goal drift and non-answers. So what does a vague answer score? Somewhere in the middle, and you'll see exactly where in the demo.

[SLIDE 5: Faithfulness]
- Question: is every claim backed by what it retrieved?
- Needs: actual output, retrieval context
- Score: share of claims not contradicted
- Our threshold: 0.8

Faithfulness checks grounding. The judge pulls the factual claims out of the answer, then checks each one against the retrieval context, the text the agent's tools actually returned. The score is the share of claims that hold up.

One detail that matters in DeepEval four point two. By default, a claim fails only if the context contradicts it. A claim the context simply doesn't mention counts as borderline and passes. Want unsupported extras to fail too? Set `penalize_ambiguous_claims` to true. For a policy bot, that's often the right call. Why? Because "bursts of five thousand are free" isn't contradicted by the docs. It's just invented.

[SLIDE 6: Hallucination vs faithfulness]
- Faithfulness: answer vs what the agent retrieved
- Hallucination: answer vs ground-truth context you supply
- 4.2: higher is better; our threshold 0.7

The hallucination metric sounds like the same thing, so what's different? Its reference. Faithfulness compares the answer with the retrieval context, whatever the agent found. Hallucination compares it with the context field, the ground truth you wrote into the test case. The score is the share of those context passages the answer agrees with.

Careful with old tutorials. In DeepEval four point two, hallucination is higher-is-better, and it passes at or above the threshold. Our policy uses zero point seven. Older docs describe it the other way round.

[SLIDE 7: Correctness vs faithfulness]
- Correctness: matches the expert's expected answer
- Faithfulness: matches the agent's own sources
- Outdated document: faithful but incorrect
- Correct from memory: correct but unfaithful

Then there's correctness, our GEval metric from Project 1. It compares the answer with the expected answer an expert wrote. This is the distinction most people get wrong in interviews. Correctness asks, "is it true?" Faithfulness asks, "did it come from the sources?" Quote an outdated document word for word, and you're faithful but incorrect. State today's price from memory, and you're correct but unfaithful, and one price change away from wrong.

[SLIDE 8: Coherence, bias, toxicity]
- Coherence: no built-in metric; write a GEval criterion
- Bias and Toxicity: built in, higher is better
- 1.0 means nothing biased or toxic found

Coherence asks whether the answer is well structured and logically consistent. DeepEval four point two doesn't ship a coherence metric. You write it as a GEval criterion, in plain English, which you'll do in Lecture 4.4. Bias and toxicity are built in. In four point two they're higher-is-better too: one point zero means the judge found no biased or toxic statements. For a support agent, they're a safety net rather than a daily metric.

[CODE: `demos/m04_metric_comparison.py`, the scoring loop]
```python
q = "What are the API rate limits for the Pro plan?"
exp = "The Pro plan allows 1,000 API requests per hour."
for name, out in responses.items():
    tc = LLMTestCase(input=q, actual_output=out, expected_output=exp, context=ctx, retrieval_context=ctx)
    row = {"response": name}
    for label, metric in (("relevancy", M.answer_relevancy()), ("faithfulness", M.faithfulness()),
                          ("hallucination*", M.hallucination()), ("correctness", M.correctness())):
        metric.measure(tc)
        row[label] = f"{metric.score:.2f}"
```

Here's the demo. One question about Pro API limits. One expected answer: a thousand requests per hour. The knowledge-base article KB-104 as both context and retrieval context. Five candidate answers, each measured by four metrics. Notice `metric.measure`: you don't need `assert_test` to get a score. Measure, then read `score` and `reason`.

[SCREEN: Terminal. Run the comparison. Highlight one cell per row as the narration reaches it.]

```bash
uv run python demos/m04_metric_comparison.py
```

[DEMO: Output (banner and blank lines trimmed)]
```text
response        relevancy  faithfulness  hallucination*  correctness
--------------  ---------  ------------  --------------  -----------
1 correct       1.00       1.00          1.00            1.00
2 wrong number  1.00       1.00          1.00            0.50
3 off-topic     0.00       1.00          1.00            0.10
4 vague         0.50       1.00          1.00            0.20
5 extra claim   1.00       0.00          0.00            1.00

*DeepEval 4.2 HallucinationMetric: share of contexts the answer agrees with (higher is better).
```

Row one, the correct answer: ones everywhere. Good. That's your control row. If the correct answer didn't score well, you'd fix the test before reading anything else.

Row three, off-topic: "Our refund policy gives you thirty days." Relevancy zero, correctness zero point one. But faithfulness? One. Nothing in the answer contradicts the API docs, so it's perfectly grounded and perfectly useless. Faithfulness alone would wave it through.

Row four, vague: "Rate limits depend on your plan. Check the documentation." Relevancy zero point five, correctness zero point two. Not wrong, just not an answer.

Row five is our hook. Relevant, correct on the key fact, and an invented claim about free bursts. Faithfulness and hallucination both drop to zero. Here, offline, the mock judge treats an unsupported number as a failure.

[SLIDE 9: The row that teaches the most]
- Row 2: "500 requests per hour", the wrong number
- Relevancy, faithfulness, hallucination: all passed offline
- Correctness caught it: 0.50 vs expert answer

And row two, the wrong number: five hundred instead of a thousand. Only correctness caught it, at zero point five. Offline, the mock judge missed the contradiction. A live `gpt-4.1` judge usually flags it, but "usually" is the point. Every judge has blind spots, and that's why you stack metrics, and why Lecture 4.3 is about checking the judge itself. So which single metric would you trust alone? None of them.

[SLIDE 10: A default set for a support agent]
- Answer Relevancy 0.7 on every case
- Faithfulness 0.8 where there's retrieved text
- GEval correctness 0.7 where an expert answer exists
- Bias and toxicity as a safety net

So what do you run day to day? For a support agent, the Project 1 set is a strong default. Relevancy on everything. Faithfulness wherever the agent retrieved text, with ambiguous claims penalized for policy answers. Correctness wherever an expert wrote the answer. Add bias and toxicity as a safety net. Then add behaviour metrics, which is next.

Why is faithfulness at zero point eight while the others sit at zero point seven? Because a wrong policy costs more than a slightly unfocused answer. Thresholds encode risk. Start from the policy file's values, then move them only with evidence, like the calibration you'll do in Lecture 4.3.

[SLIDE 11: Recap]
- Relevancy, faithfulness, correctness answer different questions
- Faithfulness checks sources; correctness checks truth
- Stack metrics; every judge has blind spots

Three things to keep. Relevancy, faithfulness and correctness each answer a different question, so they disagree, and that's useful. Faithfulness checks the sources; correctness checks the truth. And no single metric catches everything, so you stack them.

[AVATAR]
Everything today judged the words. But an agent can write a lovely answer after calling the wrong tool. Next, the metrics that judge what the agent did: task completion, tool correctness and goal accuracy.

### Recap

Answer Relevancy (statements relevant to the question, 0.7), Faithfulness (claims not contradicted by the retrieval context, 0.8; `penalize_ambiguous_claims=True` makes unsupported extras fail), Hallucination (agreement with ground-truth context, higher is better in DeepEval 4.2, 0.7) and GEval correctness (vs the expert answer, 0.7) answer different questions; on five answers to one question they disagree (an off-topic answer is fully faithful; a wrong number passes everything but correctness), so you stack metrics.

### Transition

Next: Lecture 4.2 — Agent-Specific Metrics: Task Completion, Tool Correctness, Goal Accuracy.

### Speaker notes: common student mistakes / Q&A

- All five rows are offline (mock judge: word overlap and number matching). Row 2 is the mock's blind spot: it doesn't treat "500" vs "1000/hr" as a contradiction. Re-capture live (`OFFLINE=0`) before recording; gpt-4.1 will likely give row 2 a faithfulness below 1.0, and row 5's faithfulness may be above 0 (by default DeepEval 4.2 counts unsupported claims as borderline and passes them). If the live numbers differ, keep the narration's lesson and read the live numbers.
- The curriculum asked for "0.9 relevancy vs 0.3 faithfulness"; row 5 (1.00 vs 0.00 offline) is the real example.
- "Where's the CoherenceMetric?" There isn't one in DeepEval 4.2.7; the legacy curriculum listed it. Lecture 4.4 builds criteria-based metrics with GEval.
- `HallucinationMetric` reads `context`; `FaithfulnessMetric` reads `retrieval_context`. Mixing them up gives "cannot be None" errors (Lecture 3.2).
- Bias/Toxicity direction: in DeepEval 4.2.7 both score the share of opinions judged not biased / not toxic and pass at score ≥ threshold (checked in the installed source). Older articles describe them as lower-is-better.

---

## Lecture 4.2 — Agent-Specific Metrics: Task Completion, Tool Correctness, Goal Accuracy

| Field | Value |
|---|---|
| ID | 4.2 |
| Title | Agent-Specific Metrics: Task Completion, Tool Correctness, Goal Accuracy |
| Type | DM (teach plus one agent-metrics demo) |
| Target duration | 8:00 (1,120 words at 140 wpm; 987 spoken) |
| Learning objectives | 1. Measure tool selection with `ToolCorrectnessMetric` (`tools_called` vs `expected_tools`) and task completion with `TaskCompletionMetric`. 2. Check tool arguments, goal accuracy and trajectory efficiency with the course's checks and budgets. 3. Read a ToolCorrectness reason and turn it into a fix. |
| Prerequisites | 4.1 |
| Files used | `demos/m04_agent_metrics.py`; `evaluators/metrics.py` (`tool_correctness`, `task_completion`); `evaluators/deepeval_suite.py` (`to_test_case`, `tools_called`); `evaluators/tool_metrics.py` (`check_arguments`); `config/eval_config.yaml`; Diagram D7 |

### Script

[AVATAR]
"How do I reset my password?" The agent replies: "I've opened a ticket for your password reset." Polite. On topic. Relevancy would pass it. [PAUSE] But the answer was one knowledge-base article away: Settings, Security, Reset Password. The agent took the wrong action, and a text metric can't see actions. So how do you measure what an agent did?

[SLIDE 1: Agent-Specific Metrics]
- Score what the agent did, not just said
- Tool correctness and task completion in DeepEval
- Arguments, goals and efficiency with simple checks

By the end of this lecture, you'll be able to score an agent's actions: which tools it chose, whether it finished the task, and how efficiently it got there.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Judge `gpt-4.1` live; mock judge offline
- Demo: `demos/m04_agent_metrics.py`

[SLIDE 3: The agent behaviour branch]
Diagram: D7 build 3: the right branch "Agent behaviour" with leaves task completion, tool selection, tool arguments, goal accuracy, trajectory efficiency (the left branch from 4.1 dims).

Last lecture was the left side of the map: metrics that judge text. Now the right side. Five behaviour metrics: task completion, tool selection, tool arguments, goal accuracy and trajectory efficiency. Remember the six failure modes? Wrong tool selection, incorrect arguments and infinite loops are invisible to text metrics. This branch is how you catch them.

[SLIDE 4: Tool correctness]
- Compares `tools_called` with `expected_tools`
- By name; options for order and exact match
- Our threshold: 0.85
- DeepEval 4.2 still needs a `model=`

Start with tool selection. DeepEval's tool correctness metric compares two lists on the test case: the tools the agent called, and the tools it should have called. By default it matches by name. You can ask it to care about order, or to require an exact match with nothing extra.

What does order mean here? For the cancellation case, the agent must look up the customer before it creates a ticket on their account. Same tools in the wrong order is a different trajectory.

Where do the two lists come from? You built them in Lecture 3.2. `to_test_case` turns the agent's tool log into `tools_called`, and the golden case's expected tools into `expected_tools`. Our policy threshold is zero point eight five.

[CODE: `evaluators/deepeval_suite.py`, `tools_called`]
```python
def tools_called(result: dict) -> list[ToolCall]:
    return [
        ToolCall(name=tc["tool"], input_parameters=tc.get("arguments", {}), output=tc.get("result"))
        for tc in result.get("tool_calls", [])
    ]
```

Each logged step becomes a DeepEval `ToolCall`: the name, the arguments as input parameters, and the result as output. So the arguments and results travel with the test case, ready for stricter checks later.

[SLIDE 5: Task completion]
- Did the agent achieve the user's goal?
- Judge reads input, output and tools called
- Score 0 to 1; our threshold: 0.8

Next, task completion. Did the agent actually do what the user wanted? The judge reads the request, the answer and the tools the agent called, works out what the task was and what the agent achieved, and scores how well they match. It's a judged metric, so it needs no expected answer. That makes it useful on real traffic too, where nobody wrote one. Our policy sets it at zero point eight. Can a judge really tell whether opening a ticket was the right outcome? Often, yes, because the request says what the customer wanted. When it can't, you fall back on expected tools.

[CODE: `demos/m04_agent_metrics.py`, scoring real runs and one recorded bad run]
```python
for case in [c for c in load("golden_support") if c["id"] in ("GS-03", "GS-05", "GS-06", "GS-07")]:
    tc = to_test_case(run_support_agent(case["input"]), case)
    tool_m, task_m = M.tool_correctness(), M.task_completion()
    tool_m.measure(tc)
    task_m.measure(tc)

# A recorded bad run: ticket instead of a knowledge-base answer.
bad = LLMTestCase(input="How do I reset my password?", actual_output="I've opened a ticket for your password reset.",
                  tools_called=[ToolCall(name="create_ticket")], expected_tools=[ToolCall(name="search_knowledge_base")])
m = M.tool_correctness()
m.measure(bad)
```

Here's the demo. Four real agent runs from the golden set, from a one-tool lookup to the three-tool cancellation. Each gets tool correctness and task completion. Then the recorded bad run from our hook, built by hand: called `create_ticket`, expected `search_knowledge_base`.

[SCREEN: Terminal. Run the agent-metrics demo; highlight the `recorded-bad` row, then the reason block.]

```bash
uv run python demos/m04_agent_metrics.py
```

[DEMO: Output (banner and blank lines trimmed)]
```text
id            expected tools                                    called                                            tool_correct  task_complete
------------  ------------------------------------------------  ------------------------------------------------  ------------  -------------
GS-03         search_knowledge_base                             search_knowledge_base                             1.00          1.00
GS-05         lookup_customer,create_ticket                     lookup_customer,create_ticket                     1.00          1.00
GS-06         lookup_customer,search_knowledge_base,create_tic  lookup_customer,search_knowledge_base,create_tic  1.00          1.00
GS-07         escalate_to_human                                 escalate_to_human                                 1.00          1.00
recorded-bad  search_knowledge_base                             create_ticket                                     0.00          -

ToolCorrectness reason for the bad run: [
	 Tool Calling Reason: Incomplete tool usage: missing tools [ToolCall(
    name="search_knowledge_base",
    type="FUNCTION"
)]; expected ['search_knowledge_base'], called ['create_ticket']. See more details above.
	 Tool Selection Reason: No available tools were provided to assess tool selection criteria
]
```

The four real runs score one on both metrics. The double charge, the cancellation with three tools in order, the urgent escalation: all as expected. The recorded bad run scores zero on tool correctness.

Should you be suspicious of all those ones? A little. Offline, the mock model follows the system prompt faithfully, so the golden cases come out clean. Live, `gpt-4.1-mini` occasionally takes a different path, and that's exactly when these metrics earn their place.

[SCREEN: Same terminal, zoom on the `ToolCorrectness reason` block; underline "missing tools" and "No available tools were provided".]

Now read the reason, because it tells you two things. First: missing tool, `search_knowledge_base`; called `create_ticket` instead. That's your bug report. Second: "no available tools were provided". If you also pass the list of tools the agent could have used, DeepEval adds a judged score for whether the choice was sensible. Name matching tells you that it chose wrong. The judged part helps explain why. So what would you fix first? The prompt rule that sends how-to questions to the knowledge base.

[SLIDE 6: Tool arguments]
- Right tool, wrong values
- Deterministic check: `check_arguments` in our repo
- DeepEval 4.2 also has `ArgumentCorrectnessMetric`

Third behaviour metric: arguments. Right tool, wrong values, like looking up "Alice" instead of alice@example.com. You saw our deterministic check catch that in Lecture 1.4: it compares each argument with the expected value and reports what's missing or wrong. No judge, no cost. DeepEval four point two also ships an argument correctness metric that uses a judge, which helps when the right value is a matter of judgement, like a ticket subject. Prefer the deterministic check whenever you can write down the expected value. Module 6 goes deep on this.

[SLIDE 7: Goal accuracy]
- Did the final outcome match the intended outcome?
- Single turn: expected tools plus expected answer
- Multi-turn: DeepEval's `GoalAccuracyMetric`

Fourth: goal accuracy. Task completion asks whether the agent finished something. Goal accuracy asks whether it finished the right thing. Opening a ticket completes a task. But if the customer only wanted the password steps, the goal was missed. For single-turn cases, you measure goal accuracy with what you already have: the expected tools plus GEval correctness against the expert answer. That's exactly what the Project 1 suite does. For multi-turn conversations, DeepEval's goal accuracy metric works on whole conversations.

[SLIDE 8: Trajectory efficiency]
- Count model calls: our budget is 6
- GS-05: 3 calls; GS-06: 4 calls
- Loop detector: 3 identical steps in a row

Fifth: trajectory efficiency. Did the agent take a reasonable number of steps? The simplest measure is a count. Our quality policy allows at most six model calls per task. The double-charge case uses three; the cancellation, our longest, uses four. Add the loop detector, three identical steps in a row, and you catch the runaway agent from Lecture 1.4 for free. DeepEval also has a step efficiency metric that reads a traced run. You'll meet tracing in Module 9.

[SCREEN: VS Code, `config/eval_config.yaml`. Highlight `task_completion: 0.8`, `tool_correctness: 0.85` under correctness and `max_llm_calls: 6` under reliability.]

All three thresholds live in the policy file. Notice where they sit. Task completion and tool correctness are part of correctness: the action is part of the answer. The step budget is part of reliability. Same five dimensions, now covering behaviour.

[SLIDE 9: Recap]
- Text metrics can't see actions; behaviour metrics can
- Tool correctness compares called and expected tools
- Arguments and efficiency: cheap deterministic checks first

Three takeaways. Text metrics can't see actions, so agents need behaviour metrics too. Tool correctness compares the tools called with the tools expected, and its reason reads like a bug report. And for arguments and efficiency, start with cheap deterministic checks before reaching for a judge. Which of these would have caught the password ticket? Tool correctness, at zero.

[AVATAR]
Most of these metrics lean on a judge model. Task completion, faithfulness, relevancy: another model is grading yours. So who grades the grader? Next, you'll build an LLM judge from scratch, and check it against human labels.

### Recap

`ToolCorrectnessMetric` compares `tools_called` with `expected_tools` by name (0.85) and `TaskCompletionMetric` judges whether the request was achieved (0.8); four real TechCorp runs score 1.00 on both and a recorded ticket-instead-of-search run scores 0.00 with a reason naming the missing tool; arguments use the deterministic `check_arguments`, goal accuracy uses expected tools plus GEval correctness (DeepEval's `GoalAccuracyMetric` is for conversations), and efficiency uses a 6-call budget plus the loop detector.

### Transition

Next: Lecture 4.3 — LLM-as-Judge: How to Use One AI to Grade Another.

### Speaker notes: common student mistakes / Q&A

- Offline scores (1.00 / 0.00) come from the mock judge for TaskCompletion; ToolCorrectness by name is deterministic either way. Re-capture live before recording if you show TaskCompletion live: gpt-4.1 usually scores these four runs high but not always 1.00.
- The `recorded-bad` row is hand-built (no agent run), so `task_complete` is "-". Don't present it as a live agent failure.
- `ToolCorrectnessMetric(...)` in 4.2 needs a `model=` even for name matching (it's used only when `available_tools` is passed). That's why `evaluators/metrics.py` passes `get_judge()`.
- Options on `ToolCorrectnessMetric` (from the 4.2.7 signature): `should_consider_ordering`, `should_exact_match`, `evaluation_params` (to compare `ToolCallParams` such as input parameters), `available_tools`.
- DeepEval 4.2.7 also has `ArgumentCorrectnessMetric` (needs `input` and `tools_called`), `StepEfficiencyMetric` and `PlanAdherenceMetric` (read a DeepEval trace), and `GoalAccuracyMetric` (a conversational metric). The course doesn't use them; mention only as signposts.
- GS-05 = 3 LLM calls (Lecture 1.2 demo); GS-06 = 4 LLM calls (bible §4.4). Both offline; live counts usually match because the trajectories are short.

---

## Lecture 4.3 — LLM-as-Judge: How to Use One AI to Grade Another

| Field | Value |
|---|---|
| ID | 4.3 |
| Title | LLM-as-Judge: How to Use One AI to Grade Another |
| Type | SC (build-along: judge prompt, judge function, calibration) |
| Target duration | 8:00 (1,120 words at 140 wpm; 820 spoken, the rest is code and output on screen) |
| Learning objectives | 1. Write a judge prompt with an anchored rubric, the context, and JSON output. 2. Call the judge with a stronger model at temperature 0 and parse its score and reasoning. 3. Name three judge biases and calibrate a judge against human labels. |
| Prerequisites | 4.1, 4.2 |
| Files used | `evaluators/llm_as_judge.py` (`JUDGE_PROMPT`, `judge`, `agreement`); `demos/m04_llm_as_judge.py`; `config/settings.py` (`judge_model`, `PRICES_PER_1M`); Diagram D8 (`D8-llm-as-judge.svg`) |

### Script

[AVATAR]
Every score you've seen in this module came from one model grading another. Relevancy, faithfulness, task completion: a judge decided. [PAUSE] So here's an uncomfortable question. How do you know the judge is right? Today you'll build a judge from scratch, in about twenty lines, and then check it against human graders.

[SLIDE 1: LLM-as-Judge]
- Build a judge prompt and function
- Know the biases judges bring
- Calibrate a judge against human labels

By the end of this lecture, you'll be able to build your own LLM judge, and prove whether you can trust it.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Judge `gpt-4.1` grades agent `gpt-4.1-mini`
- File: `evaluators/llm_as_judge.py`

[SLIDE 3: How a judge works]
Diagram: D8 builds 1 to 3: inputs (agent output, rubric, context) → "Judge LLM: gpt-4.1" → score (0.0 to 1.0, vs threshold) and reasoning ("why it scored that").

Why build a judge when DeepEval has dozens of metrics? Because DeepEval's metrics are judges with good prompts. Building one yourself shows you what's inside, and when you'd want your own. The shape is simple. Three inputs: the agent's answer, a rubric, and the context the answer should match. One judge model. Two outputs: a score and a reason.

[CODE: `evaluators/llm_as_judge.py`, `JUDGE_PROMPT`]
```python
JUDGE_PROMPT = """You are an impartial judge grading a customer-support answer.

Score the answer from 1 to 5:
5 = fully correct, complete, and supported by the context
4 = correct with a minor omission
3 = partly correct or partly unsupported
2 = mostly wrong or unsupported
1 = wrong, harmful, or ignores the question

Return JSON: {{"score": <1-5>, "reasoning": "<one sentence>"}}

Question: {question}
Context: {context}
Answer: {answer}
"""
```

Here's the prompt. Four design choices, and each one is there for a reason.

One: a role. "An impartial judge grading a customer-support answer." It sets the standard.

Two: an anchored rubric. Every score from one to five has a definition. What happens without anchors? One judge's four is another's three, and your scores drift.

Three: the context. The judge sees the knowledge-base text, so it grades against your policy, not against whatever it remembers. That's called reference-based judging, and it removes a whole class of judge errors.

Four: JSON output. A score you can parse, plus one sentence of reasoning. Notice the double braces: the prompt is a Python format string, so literal braces are escaped.

[CODE: `evaluators/llm_as_judge.py`, `judge`]
```python
def judge(question: str, answer: str, context: str = "(none)", model: str | None = None) -> dict:
    prompt = JUDGE_PROMPT.format(question=question, context=context or "(none)", answer=answer)
    resp = get_client().chat.completions.create(
        model=model or judge_model(),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content or "{}")
    return {"score": int(data.get("score", 1)), "reasoning": data.get("reasoning", "")}
```

Now the function. Fill in the prompt. Call the judge model, `gpt-4.1` by default. Temperature zero, because you want the same grade for the same answer. JSON mode, so the reply always parses. Then return the score and the reasoning.

Why `gpt-4.1` judging `gpt-4.1-mini`? A grader should be at least as capable as the student. It costs more: about five times the price per token of the agent model, so verify current pricing before you judge thousands of answers. And if the judge fails to return a score, the code defaults to one, the lowest. A broken judge should fail loudly, not pass quietly.

[SCREEN: Terminal. Run the judge demo. Let the printed prompt sit for a beat, then highlight the judge and human columns.]

```bash
uv run python demos/m04_llm_as_judge.py
```

[DEMO: Output (banner and printed prompt trimmed)]
```text
answer                                                        judge  human  reasoning
------------------------------------------------------------  -----  -----  ------------------------------------------------------------
TechCorp has a 30-day money-back guarantee, and refunds take  5      5      100% of statements supported by the context; covers 100% of
You can get a refund within 30 days.                          4      4      100% of statements supported by the context; covers 50% of t
Refunds are possible for 14 days and take 10 business days.   1      1      0% of statements supported by the context; covers 50% of the
I can't help with refunds.                                    1      1      Refuses a question the context answers.

Calibration vs human labels: {'n': 4, 'agreement': 1.0, 'mae': 0.0}
```

Our judge grades one answer at a time. That's called pointwise grading. The other style, pairwise, shows the judge two answers and asks which is better. It's handy for comparing two prompt versions, and it's where one of the biases you're about to see bites hardest.

Four answers to "What is your refund policy?", each graded by the judge and, separately, by a human. The full answer: five and five. The short one, thirty days but no processing time: four and four, a minor omission. The invented fourteen-day policy: one. The refusal: one, because the context answers the question. Judge and human agree on all four.

[SLIDE 4: Three biases every judge has]
- Position: prefers the first of two options
- Verbosity: rewards longer answers
- Self-preference: favours its own model family

Now, the catch. Judges have well-documented biases (verify: Zheng et al., 2023, "Judging LLM-as-a-Judge"). Position bias: when comparing two answers, judges tend to prefer the first one shown. Verbosity bias: longer answers look more thorough, so they score higher, even when they're padded. And self-preference: a model may rate text from its own family more kindly. Notice that our agent and judge share a family. Why does that matter? Because every one of these biases is a quiet, systematic error, the kind that never shows up as a crash.

[SLIDE 5: Mitigations]
- Give the judge the context and an expert answer
- Anchor every score level in the rubric
- Temperature 0 and JSON output
- Swap order when comparing two answers
- Calibrate against human labels before trusting it

The fixes. Ground the judge: give it the context and, when you have one, the expert answer. Anchor every score level. Run at temperature zero with JSON output. When comparing two answers, run both orders and average. Use a judge from a different provider when you can afford it. And above all: calibrate.

[CODE: `evaluators/llm_as_judge.py`, `agreement`]
```python
def agreement(judge_scores: list[float], human_scores: list[float], tolerance: float = 1.0) -> dict:
    """Share of items where judge and human agree within `tolerance`, plus mean absolute error."""
    pairs = list(zip(judge_scores, human_scores, strict=True))
    within = sum(abs(j - h) <= tolerance for j, h in pairs)
    mae = sum(abs(j - h) for j, h in pairs) / len(pairs) if pairs else 0.0
    return {"n": len(pairs), "agreement": round(within / len(pairs), 3) if pairs else 0.0, "mae": round(mae, 3)}
```

Calibration in code is this small. Pair each judge score with a human score. Count how often they agree within one point, and the average gap. In our demo: four items, agreement one point zero, average gap zero.

[SLIDE 6: How to calibrate a judge]
- Collect 50 to 100 human-scored answers
- Include clear passes, clear fails, borderline cases
- Target: at least 0.9 agreement before it gates
- Re-check after changing the prompt or judge model

Four items is a demo, not a calibration. For real use, have people score fifty to a hundred answers, with clear passes, clear fails, and the borderline ones that matter most. Run the judge on the same set. If it agrees at least ninety percent of the time, let it gate releases. If not, read the disagreements, fix the rubric, and run it again. And every time you change the prompt or the judge model, calibrate again. What would you do if humans disagree with each other? Then fix the criterion first. A judge can't be clearer than its instructions.

[SLIDE 7: Recap]
- Judge = role, anchored rubric, context, JSON
- Judges have biases: position, verbosity, self-preference
- Calibrate against humans before a judge gates

Three takeaways. A good judge prompt has a role, an anchored rubric, the context, and JSON output, run at temperature zero on a stronger model. Judges have biases: position, verbosity and self-preference. And no judge gates a release until it agrees with human labels.

[AVATAR]
Your hand-built judge works, but every new criterion means a new prompt and new parsing. Next, G-Eval: DeepEval's way to turn a criterion in plain English into a reusable, calibrated metric. You'll build one for customer empathy.

### Recap

An LLM judge is a role, an anchored 1-to-5 rubric, the reference context and JSON output, called on a stronger model (gpt-4.1 judging gpt-4.1-mini) at temperature 0; judges carry position, verbosity and self-preference biases, so they are grounded, anchored and calibrated against human labels (target at least 0.9 agreement) before they gate anything.

### Transition

Next: Lecture 4.4 — Custom Metrics: G-Eval & Building Your Own Evaluator.

### Speaker notes: common student mistakes / Q&A

- Offline, the mock LLM answers the judge prompt with word-overlap scoring, which is why the reasoning column reads "100% of statements supported by the context". Re-capture live (`OFFLINE=0`) before recording: gpt-4.1 writes real one-sentence reasons, and agreement may drop below 1.0 on four items. That's a good on-camera moment if it happens.
- "About five times the price per token": gpt-4.1 $2.00 / $8.00 vs gpt-4.1-mini $0.40 / $1.60 per 1M input/output tokens, `config/settings.py`, checked 2026-10-01. Verify current pricing.
- The bias citation is flagged for verification. If it can't be confirmed, keep the three biases (they're widely reported) and drop the attribution.
- "Same family" caveat: our agent and judge are both OpenAI gpt-4.1 models. The course keeps it that way for one key and simple setup; a cross-provider judge is a good exercise.
- `agreement` default tolerance is 1 point on a 1-to-5 scale. Lab 4.1 uses `tolerance=0` on pass/fail labels.
- The 50 to 100 examples and the 0.9 target are the course's working rule (the 0.9 matches `m04_lab_regulatory_geval.py`), not an industry standard.

---

## Lecture 4.4 — Custom Metrics: G-Eval & Building Your Own Evaluator

| Field | Value |
|---|---|
| ID | 4.4 |
| Title | Custom Metrics: G-Eval & Building Your Own Evaluator |
| Type | SC (build-along: a Customer Empathy GEval metric, then calibration) |
| Target duration | 8:00 (1,120 words at 140 wpm; 779 spoken, the rest is code and output on screen) |
| Learning objectives | 1. Build a GEval metric from a name, criteria, evaluation steps and evaluation params. 2. Explain how GEval turns steps into a 0-to-1 score. 3. Calibrate a custom metric against labelled examples before it gates anything (Lab 4.1). |
| Prerequisites | 4.3 |
| Files used | `evaluators/custom_metrics.py` (`customer_empathy`, `regulatory_compliance`); `demos/m04_geval_empathy.py`; `demos/m04_lab_regulatory_geval.py`; `datasets/regulatory_calibration.json`; Diagram D8 (build 4: calibration) |

### Script

[AVATAR]
Your support lead reads the transcripts and says: "The agent is always correct, and it sounds like a vending machine." [PAUSE] Which built-in metric measures that? None of them. Relevancy, faithfulness, correctness: all high. The problem is tone. When your business cares about something no library measures, you build the metric yourself. Let's build one.

[SLIDE 1: Custom Metrics with G-Eval]
- Turn a plain-English criterion into a metric
- Write evaluation steps the judge follows
- Calibrate it before it gates anything

By the end of this lecture, you'll be able to build a custom GEval metric for any business criterion, and check it against human judgement.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Judge `gpt-4.1` live; mock judge offline
- File: `evaluators/custom_metrics.py`

[SLIDE 3: What GEval does]
Diagram: D8 builds 1 to 3, relabelled: criteria + evaluation steps (rubric) → judge LLM → score 0.0 to 1.0 and reason. A small callout on the judge box: "scores 0 to 10, normalised to 0 to 1".

Last lecture, you built a judge by hand: a prompt, a call, some parsing. GEval packages that pattern. You give it a criterion in plain English and, ideally, the steps a careful grader would follow. It asks the judge to work through those steps, score from zero to ten, and normalizes the result to zero to one. When the judge model exposes token probabilities, GEval also weighs the likely scores rather than taking one number at face value, which makes scores steadier.

You've already used one GEval metric: Answer Correctness in Project 1. Now you'll write one from scratch.

[CODE: `evaluators/custom_metrics.py`, `customer_empathy`]
```python
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams as P

from evaluators.judge import get_judge


def customer_empathy(threshold: float = 0.7) -> GEval:
    """Module 4.4 build-along: criteria plus explicit evaluation steps."""
    return GEval(
        name="Customer Empathy",
        criteria="Does the response show empathy for the customer's situation while still solving the problem?",
        evaluation_steps=[
            "Criteria: empathy - does the response acknowledge the customer's feelings?",
            "Check whether the response acknowledges the customer's feelings in the first sentence.",
            "Check whether the response offers a concrete next step, not just sympathy.",
            "Penalize blame, sarcasm, or rude language heavily.",
        ],
        evaluation_params=[P.INPUT, P.ACTUAL_OUTPUT],
        threshold=threshold, model=get_judge(), async_mode=False,
    )
```

Let's build it piece by piece.

The name: Customer Empathy. It shows up in every report, so make it readable.

The criteria: one sentence. "Does the response show empathy for the customer's situation while still solving the problem?" Notice the second half. Without "while still solving the problem", a reply that only says sorry would score well.

[SLIDE 4: Writing evaluation steps]
- One check per step, in grading order
- Observable: "in the first sentence", not "warm"
- Include what to penalize
- Steps make scores consistent and explainable

Now the evaluation steps. This is where most custom metrics succeed or fail. If you leave them out, GEval writes its own from the criteria, and they can change between runs. Writing them yourself makes the metric consistent and explainable.

Look at ours. Step two: does it acknowledge the customer's feelings in the first sentence? That's observable; "is it warm?" isn't. Step three: does it offer a concrete next step, not just sympathy? And step four says what to punish: blame, sarcasm, rudeness, heavily. Good steps read like instructions to a new grader on day one. How many steps? Keep it short: ours has four. If you need ten, you probably have two metrics hiding in one.

[CODE: Same file, highlight the last two lines of `customer_empathy`: the `evaluation_params` list (input and actual output) and the `threshold`, `model` and `async_mode` arguments.]

Then evaluation params: the judge sees the customer's message and the reply. Empathy depends on what the customer said, so the input matters. And the threshold, zero point seven, plus our usual judge.

[SCREEN: Terminal. Run the empathy demo. Highlight the three scores, then each reason.]

```bash
uv run python demos/m04_geval_empathy.py
```

[DEMO: Output (banner trimmed)]
```text
Criteria: Does the response show empathy for the customer's situation while still solving the problem?
Evaluation steps:
  - Criteria: empathy - does the response acknowledge the customer's feelings?
  - Check whether the response acknowledges the customer's feelings in the first sentence.
  - Check whether the response offers a concrete next step, not just sympathy.
  - Penalize blame, sarcasm, or rude language heavily.

empathetic  score 0.90 PASS  I'm sorry for the frustration, and thank you for flagging it. I've opened a high-priority ticket so billing can refund the duplicate charge.
            reason: Professional and acknowledges the customer.

flat        score 0.60 FAIL  A ticket has been created for the duplicate charge.
            reason: Polite but does not acknowledge the customer's frustration.

rude        score 0.00 FAIL  Stop shouting. Read the docs yourself, you idiot.
            reason: Uses insulting language.
```

The customer wrote: "This is ridiculous! I was charged twice and nobody answers my emails!" Three replies.

The empathetic one acknowledges the frustration first, then opens a high-priority ticket. Zero point nine, pass. The flat one: "A ticket has been created." Correct, useful, and zero point six, a fail, because it never acknowledges the customer. That's the vending machine from our hook, now measurable. And the rude one scores zero.

What would correctness have said about the flat reply? It would pass. That's the point of a custom metric: it measures the thing your business cares about that nothing else does.

[SLIDE 5: Before a custom metric gates anything]
Diagram: D8 build 4: the amber calibration loop from "Score" back to "Rubric", labelled "calibrate against human labels".

But don't wire it into CI yet. A new metric is a hypothesis. You test it the same way you tested your judge: against human labels. That's Lab 4.1.

[SCREEN: Terminal. Run the Lab 4.1 reference solution; highlight the agree column and the summary line.]

```bash
uv run python demos/m04_lab_regulatory_geval.py
```

[DEMO: Output (banner trimmed; first four rows shown)]
```text
output                                                                  score  metric  human  agree
----------------------------------------------------------------------  -----  ------  -----  -----
Index funds have historically returned about 7% a year, but past perfo  1.00   pass    pass   yes
Buy NVDA now, it will definitely double by next year.                   0.00   fail    fail   yes
A Roth IRA lets your investments grow tax-free. This is not financial   1.00   pass    pass   yes
This fund has guaranteed returns of 12% per year.                       0.00   fail    fail   yes
...
Agreement with human labels: {'n': 10, 'agreement': 1.0, 'mae': 0.0}
Target: >= 0.9 agreement before the metric gates anything.
```

In the lab, you build a Regulatory Compliance metric for a financial assistant: a disclaimer must be present, no promised returns, and regulations named specifically. Then you score ten answers that a human already labelled pass or fail, and compare. Here, the metric agrees on all ten. The target is at least zero point nine before the metric is allowed to gate anything.

[SLIDE 6: Raw judge or GEval?]
- Raw judge: quick experiments, custom output formats
- GEval: reusable, documented, plugs into `assert_test`
- Prototype with a judge; ship with GEval

So when do you use your hand-built judge, and when GEval? Prototype with the raw judge: it's quick, and you control the output. Ship with GEval: the criteria and steps document what the metric measures, it returns a normal DeepEval score and reason, and it plugs straight into `assert_test`, your reports and CI.

[SLIDE 7: Common mistakes]
- Several criteria crammed into one metric
- Vague words: "good", "helpful", "appropriate"
- Missing params, like context for grounding
- No calibration before gating

Four mistakes to avoid. Cramming several criteria into one metric: split them, so a failure tells you which one. Vague words like "good" or "appropriate": replace them with something a grader can observe. Forgetting a param: a policy metric needs the context, or the judge guesses. And skipping calibration. Which of these have you seen in a prompt at work?

[SLIDE 8: Recap]
- GEval: name, criteria, steps, params, threshold
- Write observable steps, including what to penalize
- Calibrate against human labels before gating

Three takeaways. A GEval metric is a name, a criterion, evaluation steps, the params the judge needs, and a threshold. Write steps a new grader could follow, including what to penalize. And calibrate against human labels before the metric gates a release.

[SLIDE 9: You can now]
- Choose quality and behaviour metrics for an agent
- Build and calibrate an LLM judge
- Create a custom GEval metric for a business rule

[AVATAR]
You can now choose the right mix of metrics, build and calibrate a judge, and turn any business rule into a metric. Next module, the agents that answer from documents. When a RAG agent gets it wrong, did retrieval fail, or generation? That's where we start.

### Recap

GEval turns a plain-English criterion plus evaluation steps into a 0-to-1 metric (judge scores 0 to 10, normalised); the Customer Empathy metric scores an empathetic reply 0.90 (pass), a flat but correct one 0.60 (fail) and a rude one 0.00, and Lab 4.1's Regulatory Compliance metric agrees with 10 human labels (target at least 0.9) before it may gate anything.

### Transition

Next: Lecture 5.1 — The RAG Quality Problem: Retrieval vs. Generation.

### Speaker notes: common student mistakes / Q&A

- Offline scores and reasons come from the mock judge (it recognises the empathy criteria and insulting language). Re-capture live (`OFFLINE=0`) before recording: gpt-4.1's scores will differ (the flat reply may land near the 0.7 line), and the reasons will be full sentences. If the flat reply passes live, say so and tighten step 2; that's the calibration lesson in action.
- GEval scoring facts (DeepEval 4.2.7 source): default score range 0 to 10 normalised to 0 to 1; `top_logprobs=20` with probability-weighted scoring when the judge model returns log-probabilities. Without `evaluation_steps`, GEval generates steps from `criteria`.
- The first "evaluation step" in our code starts with "Criteria: empathy - ..." to name the criterion inside the steps; it's harmless and kept so the screen matches the file.
- Lab 4.1 full output: 10 rows, all `agree = yes`, agreement 1.0, MAE 0.0, offline. Students' live runs will vary; the lab asks them to reach at least 0.9.
- Lab files: `datasets/regulatory_calibration.json` (10 answers with human pass/fail labels), `regulatory_compliance()` in `evaluators/custom_metrics.py`.
- The curriculum's "LegalBot cut partner review time by 40%" scenario is illustrative and not used in the script.
