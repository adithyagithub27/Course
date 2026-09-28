# Quiz: Online Evaluation (Section 8)

| Field | Value |
|---|---|
| Udemy lecture | 8.8 Quiz: Online evaluation |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 8.1 to 8.7 |

---

### Q1. Atlas passed a 300-case offline eval suite before launch. Three months later the HR business partner says answers have become vague. The suite still passes. What does lecture 8.1 say is going on?

*Related lecture: 8.1 Offline evals are not enough*

- **A.** Vagueness cannot be measured, so nothing can be done.
  - *Explanation:* Incorrect. A G-Eval criterion for groundedness and specificity measures it well enough to alert on, as Lab 5 shows.
- **B.** The business partner is wrong; passing evals prove quality.
  - *Explanation:* Incorrect. Offline evals prove quality on the cases you thought of, at the time you wrote them.
- **C.** Production has drifted from the eval set: new intents, new phrasing, a new prompt version or model snapshot, and a knowledge base that changed; the suite measures yesterday's distribution, so only evaluation on live traffic (sampled judge, feedback, drift detection) can see today's quality.
  - *Explanation:* Correct. "Quality in production" means measuring on the traffic you actually serve and comparing windows over time. Incident 3 is exactly a regression the suite could not see because the suite never contained the new prompt's failure modes.
- **D.** Offline evals expire after 30 days and must be re-run.
  - *Explanation:* Incorrect. Re-running the same suite on the same cases would still pass; the cases are the problem, not their age.

**Correct answer: C**

---

### Q2. A week of Atlas traffic has 15,660 requests, 187 errors and 312 thumbs-down. You can afford to judge about 10% of traces. Compare uniform sampling with the course's tail-sampling policy.

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** Tail sampling is cheaper because it judges fewer traces.
  - *Explanation:* Incorrect. It judges more (all the "always" traces on top of the base rate); the benefit is coverage of failures, not cost.
- **B.** Neither matters because the judge should score every trace.
  - *Explanation:* Incorrect. Judging 100% of a week costs about 7% of serving cost in Lab 5's numbers; sampling is what keeps the judge affordable.
- **C.** Uniform keeps all errors; tail sampling keeps a random 10%.
  - *Explanation:* Incorrect. Reversed: uniform sampling is blind to trace content, so it keeps about 10% of errors (19 of 187).
- **D.** Uniform keeps ~10% of everything including errors (about 19 of 187); tail sampling keeps 100% of traces matching `always` rules (errors, negative feedback, escalations, step limits) plus 10% of the rest, for about 29% more judge calls; but the tail sample is biased toward bad traces, so headline quality must be reported from the uniform slice only.
  - *Explanation:* Correct. Lab 5 shows 1,566 vs 2,014 judged traces. Investigation wants every bad trace; measurement wants an unbiased sample; the judge records `sample_reason` so the two can be separated.

**Correct answer: D**

---

### Q3. Which DeepEval construction correctly expresses the course's `grounded` criterion?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** `GEval(name="grounded", criteria="Every policy claim in the answer is supported by the retrieved knowledge base passages; invented numbers or entitlements score 0.", evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT], threshold=0.7, model="gpt-4.1-mini")` scored on `LLMTestCase(input=..., actual_output=..., retrieval_context=[...])`.
  - *Explanation:* Correct. Groundedness needs the retrieved passages, so `RETRIEVAL_CONTEXT` must be among the evaluation params and the test case must carry `retrieval_context`; the criteria text is agent-specific and the threshold turns the 0-1 score into pass/fail.
- **B.** `GEval(name="grounded", criteria="Is the answer good?", evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT])`
  - *Explanation:* Incorrect. Without input or retrieval context the judge cannot check grounding, and "good" is too vague to be reproducible (Lab 5's stretch goal measures judge agreement for this reason).
- **C.** `LLMTestCase(input=..., expected_output=...)` with an exact-match assertion.
  - *Explanation:* Incorrect. Production traces have no expected output, and exact match fails on every paraphrase; that is an offline test style, not an online judge.
- **D.** A regex that checks the answer contains a number.
  - *Explanation:* Incorrect. Containing a number is not the same as containing the *right* number from the knowledge base.

**Correct answer: A**

---

### Q4. Feedback data: sessions with thumbs-up have a judge `resolved` mean of 0.93, thumbs-down 0.61, and the 92% of sessions with no feedback score 0.87. A manager proposes reporting "quality = share of thumbs-up among feedback" (75%). What is wrong with that?

*Related lecture: 8.3 Capturing user feedback that means something*

- **A.** Nothing; feedback is the voice of the user.
  - *Explanation:* Incorrect. It is the voice of the 8% of users who clicked, who are not representative.
- **B.** Survivorship bias: people who bother to click are systematically happier (0.93) or angrier (0.61) than the silent majority (0.87), so any statistic over feedback alone misrepresents overall quality. Use the judge on a uniform sample for the headline, and use feedback to find *which* traces to read and to calibrate the judge (84% agreement in Lab 5).
  - *Explanation:* Correct. Feedback is a precious targeting signal and a calibration set, not a population estimate.
- **C.** Thumbs-down should be weighted double because negative feedback is rarer.
  - *Explanation:* Incorrect. Arbitrary weights do not fix a biased sample; they add a second bias.
- **D.** Feedback should be removed from the product because it is unreliable.
  - *Explanation:* Incorrect. It is reliable for what it is: a pointer to problem traces and a check on the judge. The reasons attached to thumbs-down are the fastest route to a dataset item.

**Correct answer: B**

---

### Q5. Lecture 8.4 turns injection attempts, refusals and PII-in-output into time series. Why metrics here rather than only trace attributes?

*Related lecture: 8.4 Guardrail and safety metrics*

- **A.** Because metrics can carry the full prompt text for review.
  - *Explanation:* Incorrect. Metrics must never carry high-cardinality or sensitive text; that is a cardinality and privacy violation.
- **B.** Because traces cannot store booleans.
  - *Explanation:* Incorrect. Traces store the per-request fact (the guardrail observation and its boolean score from Challenge 4.7).
- **C.** Because safety questions are about *rates over time* ("did injection attempts triple this week?", "is PII leaking after the release?"), which are cheap to answer from low-cardinality counters in Prometheus and expensive to answer by scanning every trace; the trace still holds the evidence for any individual case.
  - *Explanation:* Correct. Counters like `atlas_guardrail_blocks_total{tenant,kind}` and `atlas_pii_in_output_total{tenant}` give alertable trends; the trace gives the example when the alert fires.
- **D.** Because Langfuse deletes guardrail observations after a day.
  - *Explanation:* Incorrect. Retention is configurable and not the reason.

**Correct answer: C**

---

### Q6. The weekly drift report shows: judge `grounded` PSI 0.19, answer length PSI 0.31, cost PSI 0.03, latency PSI 0.02. Using the thresholds from lecture 8.5, what does this say?

*Related lecture: 8.5 Drift detection: compare this week to last week*

- **A.** Latency drifted the most because it has the smallest PSI.
  - *Explanation:* Incorrect. Smaller PSI means less shift.
- **B.** PSI cannot be applied to judge scores because they are bounded in 0-1.
  - *Explanation:* Incorrect. PSI works on any binned distribution; bounded scores bin perfectly well.
- **C.** Everything is stable; PSI under 0.5 is noise.
  - *Explanation:* Incorrect. The course's thresholds are < 0.1 stable, 0.1 to 0.25 moderate shift, > 0.25 significant shift.
- **D.** Cost and latency are stable; `grounded` shifted moderately and answer length shifted significantly, so the output distribution changed while operational metrics did not, which points at a prompt or model change rather than an infrastructure problem; slice by `prompt_version` next.
  - *Explanation:* Correct. This is the Incident 3 signature. PSI compares the distribution of a metric between two windows, so it catches shape changes that a mean would understate.

**Correct answer: D**

---

### Q7. `evals/to_dataset.py` promotes traces with `grounded < 0.4` to a Langfuse dataset with `source_trace_id`. What closes the loop back to Section 4 and to offline evals?

*Related lecture: 8.6 From bad trace to regression test*

- **A.** The dataset becomes the input to offline evals (Course 2 style) that run against every new prompt version *before* it is promoted to the `production` label, so the failures observed in production this week cannot recur silently next week; `source_trace_id` lets a reviewer open the original trace for context.
  - *Explanation:* Correct. Production → judge → dataset → offline eval → prompt label promotion is the full quality loop. Incident 3 happened because the promotion step skipped the eval.
- **B.** Langfuse automatically fixes the prompt based on dataset items.
  - *Explanation:* Incorrect. Langfuse stores and evaluates; humans (or your CI) change prompts.
- **C.** Dataset items replace the knowledge base entries that were wrong.
  - *Explanation:* Incorrect. Dataset items hold the question and the *expected* answer for testing; the knowledge base is a separate artefact.
- **D.** The dataset is emailed to the prompt author.
  - *Explanation:* Incorrect. There is no automated value in that; the loop is about running evals.

**Correct answer: A**

---

### Q8. Judging 10% of a week's traffic cost $1.67 against $246 of serving cost. A colleague argues observability should be free and wants the judge switched off. Which response reflects lecture 8.2 and Lab 5?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** Agree: 0.7% overhead is waste.
  - *Explanation:* Incorrect. 0.7% is the price of the only signal that detected Incident 3, whose "cost" was two wrong HR answers and a week of eroded trust.
- **B.** Keep it, and keep reporting its cost as a line item on the Quality page: the judge's cost is a known, tunable fraction (sample rate, model choice, criteria count) of serving cost, and making it visible is what keeps it justified in the next finance review.
  - *Explanation:* Correct. Observability that hides its own cost gets switched off; observability that shows its cost next to what it caught gets funded. Same argument applies to Langfuse ingestion and to tail sampling.
- **C.** Switch the judge to gpt-4.1 to make it more accurate, whatever the cost.
  - *Explanation:* Incorrect. A more expensive judge is a decision to be measured (agreement vs cost), not a default.
- **D.** Judge 100% of traffic so the estimate is exact.
  - *Explanation:* Incorrect. That is $16.70 a week (6.8%) for a marginal gain in precision; the uniform 10% slice already estimates weekly means well.

**Correct answer: B**
