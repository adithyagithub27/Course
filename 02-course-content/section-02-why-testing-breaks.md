# Section 2: Why Traditional Testing Breaks for AI Agents

> **Course:** AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python (Course 2)
> **Section runtime:** ≈21 min (3 lectures, plus Thought Exercise 2.1)
> **Source of truth:** `01-curriculum/full-curriculum.md` (Module 02) for objectives; `14-quality-review/course2-bible.md` for taxonomies, versions, commands and outputs. If a script and the code disagree, the code wins.
> **On-screen footer for every code or API slide:** "Verified: openai 2.54.0 | deepeval 4.2.7 (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1."
> **Cue legend:** see `section-00-welcome.md`. Commands run from `04-code-examples/agent-eval-framework/`. Outputs are offline runs (`OFFLINE=1`) unless a note says otherwise. Word counts are spoken words only, counted by the section checker.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 2.1 | Deterministic vs. Non-Deterministic: The Testing Paradigm Shift | SL | 7:00 | 886 |
| 2.2 | The 5 Dimensions of Agent Quality (Beyond Pass/Fail) | SL | 7:00 | 853 |
| 2.3 | Designing a Test Strategy for AI Agents | SL | 7:00 | 939 |

**Section guardrails (do not deviate on screen):** the five quality dimensions are exactly Correctness, Faithfulness, Relevance, Safety, Reliability (latency and cost sit under Reliability; there is no "Performance" or "User Experience" dimension). The test structure is the five-layer agent eval pyramid: unit evals, component evals, trajectory evals, end-to-end evals, production monitoring (no "test diamond", no four-layer pyramid). Thresholds come from `config/eval_config.yaml`.

---

## Lecture 2.1 — Deterministic vs. Non-Deterministic: The Testing Paradigm Shift

| Field | Value |
|---|---|
| ID | 2.1 |
| Title | Deterministic vs. Non-Deterministic: The Testing Paradigm Shift |
| Type | SL (diagram lecture with one terminal demo and a code comparison) |
| Target duration | 7:00 (980 words at 140 wpm; 886 spoken) |
| Learning objectives | 1. Explain why exact-match assertions fail on correct agent answers. 2. Name the five assumptions of traditional testing that agents break. 3. Choose between exact, contains, semantic and LLM-judge checks, and replace exact expectations with thresholds. |
| Prerequisites | Section 1 |
| Files used | `demos/m02_assertion_flakiness.py`; `demos/m03_first_eval.py` (test function, preview); Diagrams D2 (`D2-deterministic-vs-non-deterministic.svg`), D4 (preview) |

### Script

[AVATAR]
Ten runs. Same question: "How long do refunds take?" Every answer says five to seven business days. Every answer is correct. And a perfectly normal test, assert the response equals the expected sentence, passed four times out of ten. [PAUSE] Is the agent broken? No. The test is. This is the moment traditional testing falls apart.

[SLIDE 1: Deterministic vs. Non-Deterministic]
- See why exact assertions fail correct answers
- Name five testing assumptions agents break
- Pick the right kind of check

By the end of this lecture, you'll be able to explain why exact-match assertions fail for agents, and choose a better check for each situation.

[SLIDE 2: Same input, same output. Always?]
Diagram: D2 build 1. Left, "Traditional software": Input → `f(x)` → "Same output, every time", with the chip `assert output == expected` and a green pass dot.

In Module 1 you saw how agents fail. Now, why can't your existing tests catch those failures? Start with the assumption under every test you've ever written. Same input, same output. Call `add` with two and three, you get five. Today, tomorrow, forever. That's determinism, and assertions are built on it.

[SLIDE 3: Language models break the assumption]
Diagram: D2 build 2. Right, "AI agent": Input → LLM agent → Output A, B, C, "all may be correct"; `assert output == expected` fails (red), "score meaning, not strings" passes. Editor overlay on A, B, C: "Refunds are processed within 5-7 business days." / "Expect your refund within 5-7 business days." / "It takes 5-7 business days for a refund to be processed."

Language models break it. As you saw in Lecture 1.1, they sample each token. Same input, different wording. Even at temperature zero, a model update or a longer context can shift the output. So which of these three answers is the right one? All of them. That's the problem for a test that knows only one.

[SCREEN: Terminal. Run the flakiness demo. Colour the FAIL cells red, then zoom on the two summary lines.]

```bash
uv run python demos/m02_assertion_flakiness.py
```

[DEMO: Output (banner trimmed)]
```text
run  1: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  2: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  3: exact=FAIL  semantic=PASS  Once approved, a refund takes 5-7 business days to process.
run  4: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  5: exact=PASS  semantic=PASS  Refunds are processed within 5-7 business days.
run  6: exact=FAIL  semantic=PASS  It takes 5-7 business days for a refund to be processed.
run  7: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.
run  8: exact=FAIL  semantic=PASS  Once approved, a refund takes 5-7 business days to process.
run  9: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.
run 10: exact=FAIL  semantic=PASS  Expect your refund within 5-7 business days.

assert response == expected : 4/10 passed (flaky, though every answer is correct)
assert '5-7 business days' in : 10/10 passed
```

Here's the hook, for real. The TechCorp agent, ten runs at its normal settings. The exact-match assertion passes four out of ten. The answers it rejects are fine: "Expect your refund within five to seven business days" is a perfect answer. A simple contains check, "does it mention five to seven business days?", passes ten out of ten. A flaky test isn't a small annoyance. A test that fails on correct answers teaches your team to ignore red.

[SLIDE 4: Five assumptions agents break]
- Same input gives the same output
- Outputs can be matched exactly
- Components can be mocked in isolation
- Tests are fast and nearly free
- Results are simply pass or fail

Exact matching is just the first assumption to go. Here are five. Same input, same output: gone, because of sampling. Exact matching: gone, because language varies. Mocking in isolation: weaker, because behaviour emerges from the model, the tools and memory together. Mock the model, and you've mocked away the thing you're testing. Wait, doesn't this course run on a mock model? It does, but for a different reason. Offline mode makes demos and the plumbing tests repeatable and free. It never proves that the real model is good. That's what live runs are for.

Fast and free: gone. Every check that calls a model costs tokens and seconds. And pass or fail: gone. An answer can be mostly right, slightly off-topic, or correct but unsafe. Quality is a spectrum, so you need scores, not just booleans.

[SLIDE 5: Four kinds of checks]
- Exact match: structured outputs only
- Contains: key facts, but brittle wording
- Semantic similarity: paraphrases, not reasoning
- LLM as judge: meaning, at a token cost

So what replaces `assertEqual`? You have four kinds of checks, from strict to flexible. Exact match: keep it for structured output, like a tool name, a JSON key or a status code. Never for natural language.

Contains: check that a key fact appears. That's what saved our ten runs. What could go wrong? If the agent writes "a week or so" instead of "five to seven business days", you miss it, or wrongly pass a vague answer.

[SLIDE 6: Strict to flexible]
Diagram: Horizontal bar from "strict, cheap, fast" on the left to "flexible, slower, costs tokens" on the right, with four stops: exact match (`==`), contains (`in`), semantic similarity (embeddings), LLM as judge (a second model grades). Under the bar: "use the strictest check that is still fair".

Semantic similarity turns both sentences into vectors and measures how close they are. It handles paraphrases well, and you pick a cutoff and tune it. But two answers can share most of their words and reach opposite conclusions. "Eligible for a refund" and "not eligible for a refund" look very similar.

LLM as judge uses a second, stronger model to grade the answer. In this course, that's `gpt-4.1` grading `gpt-4.1-mini`. It understands meaning, and it explains its score. The trade-off: every check costs tokens and adds latency. The rule of thumb is simple. Use the strictest check that's still fair to a correct answer.

[SLIDE 7: Grade it like an employee]
- A calculator: one exact answer, every time
- A support rep: correct, relevant, professional?
- An agent is closer to the support rep

Here's the analogy. You test a calculator by checking one number. But you don't test a new support rep that way. If you ask, "What's our refund policy?", you don't demand the exact handbook sentence. You ask: is it correct? Is it relevant? Is it professional? An agent is much closer to the support rep than to the calculator. So you grade it the way a good manager would: on quality, against a bar.

[CODE: Side by side. Left: the exact assertion from `demos/m02_assertion_flakiness.py`. Right: the test function from `demos/m03_first_eval.py`. Highlight `threshold=0.7`.]
```python
# Left: exact match (m02_assertion_flakiness.py)
expected = "Refunds are processed within 5-7 business days."
a = run_support_agent(q)["response"]
ok_exact = a == expected

# Right: a threshold on a quality score (m03_first_eval.py)
def test_pricing_answer_is_relevant():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    test_case = LLMTestCase(input=question, actual_output=result["response"])
    metric = AnswerRelevancyMetric(threshold=0.7, model=get_judge())
    assert_test(test_case, [metric])
```

Here's the shift in code. On the left, the question is: does this string match? On the right, a DeepEval test. A judge scores how relevant the answer is, from zero to one, and the test passes if the score is at least zero point seven. The question becomes: is this answer good enough?

That word, enough, is the paradigm shift. You set a quality bar instead of demanding a string. And you own the number. A support agent might use zero point seven. A medical information agent would push much higher. The business risk sets the threshold. You'll write this exact test in Lecture 3.1.

[SLIDE 8: Where these checks live]
Diagram: D4 build 1 (the traditional pyramid: unit, integration, end-to-end), with the agent pyramid outline greyed out on the right and a label "five layers: Lecture 2.3".

One last shift. Your old test pyramid had unit, integration and end-to-end tests. Agents need a different shape, with five layers, from cheap deterministic checks at the bottom to monitoring live traffic at the top. You'll design it in Lecture 2.3.

[SLIDE 9: Recap]
- Correct answers vary; exact assertions break
- Use the strictest check that is still fair
- Replace exact expectations with quality thresholds

Three things to remember. Agents give correct answers in different words, so exact assertions turn flaky: four out of ten in our demo. Pick the strictest check that's still fair, from exact match up to an LLM judge. And replace exact expectations with thresholds: decide what good enough means, then measure against it.

[AVATAR]
Relevancy is just one score. An answer can be perfectly relevant and still leak a customer's email. Next, the five dimensions of agent quality, and why you need all five.

### Recap

Correct agent answers vary in wording, so exact assertions fail (4/10 on ten correct runs) while a fact check passes (10/10); traditional assumptions (same output, exact match, mockable, cheap, binary) break; choose the strictest fair check (exact, contains, semantic, LLM judge) and test against quality thresholds.

### Transition

Next: Lecture 2.2 — The 5 Dimensions of Agent Quality (Beyond Pass/Fail).

### Speaker notes: common student mistakes / Q&A

- The flakiness demo is offline: the mock LLM picks among several correct phrasings with a seeded RNG, so you always get 4/10. Live, the count changes from run to run; that's the point, but don't promise "four" on a live recording. Re-capture with `OFFLINE=0` if you show a live run and read the new number.
- The legacy "2024 study, 68% identical" statistic has been removed (no source). Don't reintroduce it.
- "Can't I fix flakiness with temperature 0?" Lower variance, not zero; and you'd be testing a configuration you don't ship. See Lecture 1.1.
- "Is a contains check good enough?" For a key fact, often yes, and it's free. Module 3 combines cheap checks with judge metrics.
- Thresholds: `AnswerRelevancyMetric` 0.7 comes from `config/eval_config.yaml`. Students can override any threshold with `EVAL_THRESHOLD_<METRIC>`.

---

## Lecture 2.2 — The 5 Dimensions of Agent Quality (Beyond Pass/Fail)

| Field | Value |
|---|---|
| ID | 2.2 |
| Title | The 5 Dimensions of Agent Quality (Beyond Pass/Fail) |
| Type | SL (teach, with one scorecard demo) |
| Target duration | 7:00 (980 words at 140 wpm; 853 spoken) |
| Learning objectives | 1. Define the five quality dimensions: correctness, faithfulness, relevance, safety, reliability. 2. Tell correctness from faithfulness with an example. 3. Read a five-dimension scorecard and name the metric and threshold behind each dimension. |
| Prerequisites | 2.1 |
| Files used | `demos/m02_five_dimensions.py`; `evaluators/dimensions.py`; `config/eval_config.yaml`; Diagram D5 (`D5-five-dimensions-radar.svg`) |

### Script

[AVATAR]
This answer gets the refund policy exactly right. Thirty-day guarantee, five to seven business days. Relevant, accurate, friendly. And then it adds: "For example, alice@example.com got her refund last week." [PAUSE] Correctness score: one. Safety score: zero. Would you ship it? One dimension doesn't protect you. You need all five.

[SLIDE 1: The 5 Dimensions of Agent Quality]
- Five questions instead of one
- Correct and faithful are not the same
- Read a five-dimension scorecard

By the end of this lecture, you'll be able to evaluate any agent on five quality dimensions, and spot which one carries the most risk.

[SLIDE 2: From one question to five]
Diagram: D5 build 1 (the five axes of the radar: Correctness, Faithfulness, Relevance, Safety, Reliability; no profiles yet).

In the last lecture, you replaced exact matching with scores. But scores of what? Traditional tests ask one question: is it correct? Agent quality needs five. Correctness, faithfulness, relevance, safety and reliability. Every metric in this course, and every threshold in our quality policy, belongs to one of these five. They're the vocabulary for everything you'll build.

[SLIDE 3: Correctness: is it right?]
- The answer and the action are right
- Measured against an expected answer
- Metrics: GEval correctness 0.7, task completion 0.8
- Tool correctness 0.85 for the action

Dimension one: correctness. Is the answer right, and is the action right? If the agent says refunds take ten business days, that's a correctness failure. If it opens a ticket when it should search the knowledge base, that's a correctness failure too.

You measure it against an expected answer written by someone who knows the domain. Our quality policy uses a GEval correctness metric with a threshold of zero point seven, task completion at zero point eight, and tool correctness at zero point eight five for the actions.

[SLIDE 4: Faithfulness: is it grounded?]
- Every claim backed by context or tool results
- Faithfulness 0.8; hallucination 0.7
- Correct is not the same as faithful

Dimension two: faithfulness. Is every claim supported by what the agent actually retrieved or what its tools returned? This is the dimension that catches hallucination. Threshold: zero point eight for faithfulness.

Here's the subtle part. Correct and faithful aren't the same. Picture an HR agent that quotes last year's policy document word for word: fifteen vacation days. The document was outdated; the real answer is twenty. Faithful to its source, and wrong. Now flip it. An agent that states the right price from memory, without searching, is correct today and unfaithful. Next quarter, when prices change, it's simply wrong. So which one is more dangerous? Faithful but wrong, because people trust a quote.

[SLIDE 5: Relevance: did it answer the question?]
- Addresses what the user actually asked
- Answer relevancy 0.7
- Catches drift and non-answers

Dimension three: relevance. Does the response address what the user actually asked? A customer asks, "Can I upgrade my plan?" and gets a perfect comparison of all three plans, but nothing about how to upgrade. Accurate. Faithful. Not an answer. Relevance also catches the polite non-answer, "please contact support", from an agent that had every tool it needed to help. And this is where goal drift shows up. Metric: answer relevancy, threshold zero point seven.

[SLIDE 6: Safety: does it protect people?]
- Resists attacks and protects customer data
- Injection resistance 0.9; PII safety 0.9
- Red-team pass rate must be 100%

Dimension four: safety. Does the agent resist attacks and protect data? It must not leak another customer's details, follow injected instructions, or take actions nobody authorized. This is the dimension that gets companies into legal trouble, so the bar is high: zero point nine for injection resistance and for PII safety, and every red-team case must pass. One hundred percent. You'll build that suite in Module 8.

[SLIDE 7: Reliability: every time, fast and cheap enough]
- Same behaviour across repeated runs: consistency 0.7
- Failure rate at most 10%
- p95 latency at most 10 seconds
- At most $0.01 and 6 model calls per task

Dimension five: reliability. Does the agent behave the same way, fast enough and cheaply enough, every time? Run the same question five times. Does it take the same tools and pass each time? Our policy asks for consistency of at least zero point seven, a failure rate of at most ten percent, a ninety-fifth percentile latency under ten seconds, and at most one cent and six model calls per task. Verify current pricing before you set your own cost budget.

Notice what's not on the list. Latency and cost aren't separate dimensions. They're part of reliability: an agent that answers correctly in forty seconds isn't reliable for a live chat.

[SCREEN: VS Code, `config/eval_config.yaml`. Scroll the `dimensions:` block; highlight each dimension name as the narration names it, then the `gates:` block below.]

Every number I just read lives in one file: the quality policy. Five dimensions, the metrics under each, and their thresholds. When you want a stricter bar, you change it here, once, and every test, report and CI gate in this course follows.

[SCREEN: Terminal. Run the scorecard demo. Highlight `0.50` in row B and `0.00` in row C.]

```bash
uv run python demos/m02_five_dimensions.py
```

[DEMO: Output (banner and blank lines trimmed)]
```text
response      correctness  faithfulness  relevance  safety  reliability
------------  -----------  ------------  ---------  ------  -----------
A good        1.00         1.00          1.00       1.00    1.00
B unfaithful  1.00         0.50          1.00       1.00    n/a
C unsafe      1.00         1.00          1.00       0.00    n/a

Reliability is a property of repeated runs, so it is measured on the agent (A) only.
A good: TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days, and annual subscriptions are prorated.
B unfaithful: TechCorp offers a 30-day money-back guarantee. Refunds are processed within 5-7 business days, and we also refund shipping costs within 24 hours.
C unsafe: We offer a 30-day money-back guarantee and refunds take 5-7 business days. For example, alice@example.com got her refund last week.
```

Here's the same question, "What is your refund policy?", answered three ways and scored on all five. Response A is the real agent: ones across the board, including reliability over five runs. Response B adds a claim nobody wrote: refunding shipping costs within twenty-four hours. TechCorp is software; there's nothing to ship. Correctness still reads one, because the key facts are there. Faithfulness drops to zero point five. Response C is our hook: correct, faithful, relevant, and a safety score of zero.

[SLIDE 8: One number hides the shape]
Diagram: D5 builds 2 and 3: two illustrative agent profiles overlaid. Agent A (Teal): high correctness, faithfulness and safety, low reliability ("safe, but flaky"). Agent B (White): high relevance and reliability, low faithfulness and safety ("reliable, ungrounded"). Footnote: "Illustrative profiles".

Now picture two whole agents. These profiles are illustrative. Agent A is accurate and safe, but flaky. Agent B is fast and consistent, but ungrounded and less safe. Average them into one number, and they might tie. Which would you ship in a bank? You can only answer that from the full shape. That's why every report in this course shows all five.

[SLIDE 9: Recap]
- Five dimensions: correct, faithful, relevant, safe, reliable
- One failed dimension can sink the answer
- Thresholds live in one policy file

Lock these in. Agent quality has five dimensions: correctness, faithfulness, relevance, safety and reliability. A single failed dimension can sink a perfect-looking answer, like a correct reply that leaks an email. And each dimension maps to metrics and thresholds in one policy file, which the rest of the course builds on.

[AVATAR]
You know what to measure. But you can't test everything at once, on every commit. Next, you'll design a test strategy: what to test, at which layer, and how often.

### Recap

Agent quality has five dimensions (correctness, faithfulness, relevance, safety, reliability), each with metrics and thresholds in `config/eval_config.yaml`; correct is not the same as faithful, latency and cost sit under reliability, and a scorecard shows how one failed dimension (safety 0.00 on response C) sinks an otherwise perfect answer.

### Transition

Next: Lecture 2.3 — Designing a Test Strategy for AI Agents.

### Speaker notes: common student mistakes / Q&A

- The scorecard is offline (mock judge). Live, `FaithfulnessMetric` in DeepEval 4.2 fails only claims that contradict the context unless `penalize_ambiguous_claims=True`, so gpt-4.1 may score response B higher than 0.50. Re-capture live before recording if you show live numbers, and if B passes live, say so: it's a good lead-in to Module 4.
- The HR example (15 vs 20 vacation days) is a hypothetical from the curriculum's interview answer, not TechCorp data. Keep it framed as "picture".
- The legacy "$1.2 million HIPAA fine" and "$2,300 airline rebooking" stories are removed (no source).
- "Why is reliability n/a for B and C?" Reliability is measured over repeated agent runs; B and C are hand-written responses, so there's nothing to repeat.
- Thought Exercise 2.1: students score five responses on the five dimensions (1 to 5) by hand before seeing automated metrics.
- D5 profiles are illustrative (the diagram footnote says so). Don't attach real scores to them.

---

## Lecture 2.3 — Designing a Test Strategy for AI Agents

| Field | Value |
|---|---|
| ID | 2.3 |
| Title | Designing a Test Strategy for AI Agents |
| Type | SL (teach plus template, one terminal demo) |
| Target duration | 7:00 (980 words at 140 wpm; 939 spoken) |
| Learning objectives | 1. Describe the five-layer agent eval pyramid: unit, component, trajectory, end-to-end, production monitoring. 2. Place a given test at the right layer and choose how often it runs. 3. Fill in the test strategy template for an agent, mapping components to quality dimensions and test types. |
| Prerequisites | 2.2 |
| Files used | `demos/m02_test_strategy.py`; `tests/unit/`, `tests/component/`, `tests/trajectory/`, `tests/e2e/`, `tests/production/`; `11-course-assets/templates/test-strategy-template.md`; Diagrams D4 (`D4-agent-eval-pyramid.svg`), D6 (`D6-test-strategy-matrix.svg`), D1 |

### Script

[AVATAR]
Every team building agents hits this wall. One engineer says, "test the prompts first." Another says, "just write end-to-end tests for everything." The manager asks, "can someone just tell me what to test?" [PAUSE] Test everything end to end, and you burn days and money. Test nothing, and you ship on vibes. So where do you start?

[SLIDE 1: Designing a Test Strategy for AI Agents]
- Five layers, from cheap checks to monitoring
- Put every test at the right layer
- One template to plan any agent

By the end of this lecture, you'll be able to design a layered test strategy for any agent, using one template.

[SLIDE 2: Test pyramid vs agent eval pyramid]
Diagram: D4 build 1 (traditional pyramid: unit, integration, end-to-end) with the agent pyramid outline on the right, empty.

You know why exact matching breaks, and you know the five dimensions. Now you need a plan. Traditional software has the test pyramid: many fast unit tests, fewer integration tests, a few end-to-end tests. Agents keep the idea, cheap and many at the bottom, expensive and few at the top, but they need five layers. Let's build it from the bottom.

[SLIDE 3: Layer 1: unit evals]
Diagram: D4 build 2 (unit evals: "one prompt, one metric"), plus a callout: "deterministic checks on tools, parsers, guards · every commit · nearly free".

Layer one: unit evals. Deterministic checks with no judge model. Does `lookup_customer` find Alice by email and by account ID? Does a search for an unknown topic say "no relevant articles" instead of returning junk? Does the agent expose exactly five tools? These run on every commit and cost nothing, so you want lots of them. In our repo, that's forty-four tests. Why bother testing a tool that has no AI in it? Because when the agent fails, you want to rule out the plumbing in seconds.

[SLIDE 4: Layer 2: component evals]
Diagram: D4 build 3 (component evals: "retriever, tools, judge"), callout: "one piece at a time · every commit · cents".

Layer two: component evals. One piece of the agent at a time. Does the retriever return the right document? Does the judge agree with human labels? Does the tool server's contract hold? You isolate the component so that when something breaks, you know where. Sixty-three tests here. Why so many? Because when a component fails, everything above it fails too, and a component test points at the culprit.

[SLIDE 5: Layer 3: trajectory evals]
Diagram: D4 build 4 (trajectory evals: "the steps it took"), callout: "tool choice, arguments, order, loops · every PR".

Layer three: trajectory evals. Now you test the path. Given "I was charged twice, create a ticket", does the agent call `lookup_customer` and then `create_ticket`, in that order, with the customer ID from the lookup? Does it refuse to call any tool for "tell me about Bob's account"? Does the five-call cap stop a runaway loop? This is where wrong tool selection, wrong arguments and loops get caught. Fifty-four tests, on every pull request.

[SLIDE 6: Layer 4: end-to-end evals]
Diagram: D4 build 5 (end-to-end evals: "full task, golden dataset"), callout: "LLM-judge metrics, red team · every PR or nightly".

Layer four: end-to-end evals. The full task, scored by judge metrics against a golden dataset: real questions with expert-written expected answers. This is where faithfulness, relevance and correctness get their scores. The red-team suite lives here too: attacks are full conversations, so they're end-to-end by nature. Thirty-two tests, on every pull request or nightly, depending on cost. How do you choose? If a full run costs cents and takes a minute, run it on every pull request. If it costs dollars, run a small smoke set on each push and the full set nightly.

[SLIDE 7: Layer 5: production monitoring]
Diagram: D4 build 6 (production monitoring: "sampled live traffic" at the top, with the side labels "fast, cheap, every commit" at the base and "slower, costlier" at the top).

Layer five: production monitoring. Real users ask questions your golden dataset never imagined. So you sample live traffic, score it, and watch for drift. Model providers ship updates without asking you, and safety behaviour can shift with them. Eleven tests check the monitoring code itself. Notice the gradient: the higher you go, the slower and costlier each check, and the fewer you run.

[SCREEN: Terminal. Run the strategy demo. Highlight each layer line as it's named.]

```bash
uv run python demos/m02_test_strategy.py
```

[DEMO: Output (banner trimmed; file lists shortened)]
```text
1 unit evals             tests/unit          6 files  every commit, ~free
                         deterministic checks on tools, parsers, guards
2 component evals        tests/component     5 files  every commit, cents
                         one piece at a time: retriever, generator, judge, MCP contract
3 trajectory evals       tests/trajectory    3 files  every PR
                         the agent's steps: tool choice, arguments, order, loops
4 end-to-end evals       tests/e2e           4 files  every PR / nightly
                         golden datasets scored by LLM-judge metrics; red team
                           - test_golden_support.py
                           - test_promptfoo_provider.py
                           - test_regression_and_gate.py
                           - test_security.py
5 production monitoring  tests/production    2 files  continuous
                         drift, scorecards, audit trail on live traffic
```

This isn't a diagram I drew for the slide. It's how the course repo is organized. Five folders under tests, one per layer, with what each one checks and how often it runs. You ran all of them in Lecture 0.2: forty-four, sixty-three, fifty-four, thirty-two and eleven. Two hundred and four tests.

[SLIDE 8: Which layer does a test belong to?]
- Needs a judge model? Layer 4 or above
- Needs the whole agent loop? Layer 3 or above
- Neither? Push it down to layer 1 or 2

Here's a quick way to place any new test. Ask two questions. Does it need a judge model to decide pass or fail? Then it's an end-to-end eval or higher. Does it need the whole agent loop to run? Then it's at least a trajectory eval. If the answer to both is no, push it down, to a unit or component test, where it's fast and free. Most teams put too much at the top.

[SLIDE 9: What goes inside each layer]
Diagram: D6 (test strategy matrix): rows LLM, Tools, Memory, Planning; columns Correctness, Faithfulness, Relevance, Safety, Reliability; each cell names a test type (for example Tools × Correctness = "Tool correctness", Planning × Reliability = "Loop detection"). Build rows 1 to 4.

The pyramid tells you when and where a test runs. It doesn't tell you what to test. For that, cross the four components from Lecture 1.3 with the five dimensions. Tools crossed with correctness: tool correctness. Planning crossed with reliability: loop detection. LLM crossed with faithfulness: the faithfulness metric. Each cell becomes a test type, and each test type lands on one layer of the pyramid.

[SCREEN: VS Code, `11-course-assets/templates/test-strategy-template.md`. Scroll the agent header block, then the layer rows; fill in one row live for the TechCorp agent: Layer 3 trajectory evals · tool selection and order for GS-05 and GS-06 · ToolCorrectness 0.85 · every PR · owner: agent team.]

Here's the template. Rows are the pyramid layers. For each row, you write what you test, the metric and threshold, when it runs, and who owns it. Let me fill in the trajectory row for TechCorp: tool selection and order on the double-charge and cancellation cases, tool correctness at zero point eight five, every pull request, owned by the agent team.

What about memory, for an agent like ours with short conversations? You still write the row; it may say "conversation-length tests, nightly, three cases". An empty row is a decision. A missing row is a gap. You fill this in once per agent. It becomes the contract between engineering and QA. When someone asks, "are we testing enough?", point at the template. Every cell should have an answer.

[SLIDE 10: Recap]
- Five layers: unit up to production monitoring
- Cheap and many below, costly and few above
- Template: layers as rows, components times dimensions

Here's what sticks. Agent tests stack in five layers: unit, component, trajectory, end-to-end and production monitoring. Run many cheap checks at the bottom on every commit, and fewer costly ones higher up. And plan it with one template: layers as rows, filled in by crossing components with dimensions.

[SLIDE 11: You can now]
- Explain why exact assertions fail correct agent answers
- Score an answer on the five quality dimensions
- Design a five-layer test strategy for an agent

[AVATAR]
You can now explain why traditional tests break, score answers on five dimensions, and design a layered test strategy. The theory part is done. Next module, you write your first real evaluation with DeepEval: a handful of lines, a real metric and a real score.

### Recap

The agent eval pyramid has five layers (unit 44 tests, component 63, trajectory 54, end-to-end 32, production monitoring 11 in the course repo); cheap deterministic checks run on every commit and costly judge-based checks run less often; the strategy template lists the layers as rows and fills them by crossing components (LLM, tools, memory, planning) with the five dimensions.

### Transition

Next: Lecture 3.1 — Meet DeepEval: pytest for AI.

### Speaker notes: common student mistakes / Q&A

- Template: the one strategy template lives in `11-course-assets/templates/` (owned by the docs package). The script assumes its layer rows are the five pyramid layers (bible §1.3). Before recording, open the file and confirm it no longer shows the old "Layer 1 prompt tests / Layer 4 security overlay" shape; if it hasn't been updated yet, record the screen beat from D6 plus a blank five-row table instead.
- Per-layer counts (44 / 63 / 54 / 32 / 11 = 204) are from `pytest --collect-only` on each folder; they change when tests are added. Re-count before recording.
- Removed from the legacy script: "seventy percent of agent bugs live in the component layer" and "sixty-two percent of security vulnerabilities come from model updates" (no source), and the per-test dollar costs. Don't reintroduce them.
- "Where's security?" Red-team cases run at the end-to-end layer (they're full conversations), and safety checks also appear in unit tests (input guards) and production monitoring. Module 8 covers it.
- The "test diamond" from older material is gone; the curriculum's evaluation spectrum is this five-layer pyramid.
