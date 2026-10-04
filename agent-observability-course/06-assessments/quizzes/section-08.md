# Quiz: Online Evaluation (Section 8)

| Field | Value |
|---|---|
| Udemy lecture | 8.8 Quiz: Online evaluation |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 8.1 to 8.7 |

---

### Q1. Atlas's judge runs on a 10% head sample plus a tail of traces that are always judged. Which traces belong in the tail, and which sample does the headline quality number come from?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** The tail is a random extra 10%; the headline uses head and tail together for a bigger n.
  - *Explanation:* Incorrect. The tail is chosen by content, so mixing it into the mean biases quality downwards. This is the most common bug the lecture warns about.
- **B.** The tail is the traces that matter for investigation (errors, step limits, escalations, thumbs-down); the headline quality estimate uses the head sample only, because the tail is biased toward bad traces by design.
  - *Explanation:* Correct. Head gives you an unbiased estimate; tail gives you the failures. Keep the two separable when you compute the quality tiles: the head sample (`head_sample(trace_id, rate)`) is deterministic per trace id, so you can always tell which judged traces it picked.
- **C.** The tail is the most expensive traces; the headline uses the tail because cost and quality go together.
  - *Explanation:* Incorrect. Cost is one tail rule a team might add, but the headline still comes from the head sample.
- **D.** There is no tail; judge 100% of traces so the estimate is exact.
  - *Explanation:* Incorrect. Judging everything on gpt-4.1 would cost about $109 a day, almost six times serving after Section 6; sampling is what keeps the judge affordable.

**Correct answer: B**

---

### Q2. The judge uses 3 criteria, each one call of about 1,200 input and 150 output tokens on gpt-4.1-mini ($0.40 / $1.60 per million tokens; verify current pricing), so $0.00072 per call. Atlas serves 10,000 traces a day and the head sample is 10%. What is the judge's daily bill for the head sample?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** $0.72: 1,000 traces × $0.00072.
  - *Explanation:* Incorrect. That counts one call per trace; each judged trace is three calls, one per criterion.
- **B.** $21.60: 10,000 traces × 3 × $0.00072.
  - *Explanation:* Incorrect. That judges every trace; the head sample is 10%.
- **C.** $2.16: 1,000 traces × 3 criteria × $0.00072 (the tail adds a little on top).
  - *Explanation:* Correct. $0.00216 per judged trace, about $2.16 a day: roughly 4% of the $56.28 baseline day and about 11% of the $19.07 day after Section 6's levers. Report it as a line item and cap it with `JUDGE_MAX_CALLS`.
- **D.** $0.216: the judge's tokens are billed at the cached rate.
  - *Explanation:* Incorrect. Each judge prompt contains a different trace, so there is no long shared prefix to cache.

**Correct answer: C**

---

### Q3. A teammate writes the `resolved` criterion as "Did the agent give a good answer?". Scores cluster between 0.7 and 0.9 whatever the answer, and two runs of the same trace disagree. What should the criterion add?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** A higher threshold, so fewer answers pass.
  - *Explanation:* Incorrect. The threshold moves the pass line but does nothing about a vague scale; the scores would still cluster.
- **B.** A bigger judge model; vagueness is a capability problem.
  - *Explanation:* Incorrect. A larger model is just as generous with an undefined criterion, at five times the price.
- **C.** Few words: the shorter the criterion, the more consistent the judge.
  - *Explanation:* Incorrect. Short criteria are exactly what produce the generous, noisy scores in the question.
- **D.** What a zero looks like, spelled out for a helpdesk agent: for example, "the employee got what they asked for and a next step; an answer that only says 'contact HR', asks for information it already has, or doesn't address the question scores 0".
  - *Explanation:* Correct. A judge is generous unless you tell it exactly what failure is. Atlas's `CRITERIA` name the failure cases for `resolved`, `grounded` and `safe_escalation`.

**Correct answer: D**

---

### Q4. The `grounded` criterion currently reads "The answer is accurate." Which addition makes a zero unambiguous for Atlas?

*Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** "Every policy statement is backed by a cited knowledge-base article or a quoted tool result; any number, entitlement or deadline that appears in neither scores 0."
  - *Explanation:* Correct. It defines what counts as support and names the failure (an invented number or entitlement). If you also pass the retrieved passages as `retrieval_context`, the judge can check the citation instead of trusting it.
- **B.** "Be strict."
  - *Explanation:* Incorrect. Strictness without a definition of failure just shifts the noise.
- **C.** "Score 1 if the answer sounds confident."
  - *Explanation:* Incorrect. Confidence is the signature of a hallucination, not of grounding.
- **D.** "Compare against the expected answer."
  - *Explanation:* Incorrect. Production traces have no expected answer; that is an offline-eval construction.

**Correct answer: A**

---

### Q5. On the replayed day, `make feedback` prints `joined_with_judge=363 agreement=80% judge|👍=0.91 judge|👎=0.91`. The disagreement table shows 81 traces where user and judge disagree, 71 of them thumbs-down that the judge rated fine. How should you read this?

*Related lecture: 8.3 Capturing user feedback that means something*

- **A.** The judge is broken and should be replaced by the thumbs.
  - *Explanation:* Incorrect. 12.7% of requests carry a vote; the judge covers a defined sample. Neither replaces the other.
- **B.** The judge's mean is the same for thumbs-up and thumbs-down, so on this day the votes carry almost no information about answer quality (the simulator draws them independently of the answer); the 81 disagreements are the week's reading list, because each one is either a judge error or a user who wanted something the policy forbids.
  - *Explanation:* Correct. Agreement is a calibration check, not a quality score. Click through the disagreements: they are where the judge's criteria or the product are wrong.
- **C.** 80% agreement means quality is 80%.
  - *Explanation:* Incorrect. Agreement measures whether two signals match, not how good the answers are.
- **D.** Thumbs-down should be weighted double because negative feedback is rarer.
  - *Explanation:* Incorrect. Arbitrary weights do not fix a noisy or biased signal; they add a second bias.

**Correct answer: B**

---

### Q6. A manager wants to report "quality = 79% positive feedback". Feedback covers 12.7% of requests, and on real traffic the per-answer feedback rate falls in long sessions. Which bias does this hide, and what does lecture 8.3 do about it?

*Related lecture: 8.3 Capturing user feedback that means something*

- **A.** No bias: 79% of users are happy.
  - *Explanation:* Incorrect. It is 79% of the votes, from the minority who clicked; a reader will hear "79% of users".
- **B.** Recency bias; fix by weighting recent votes more.
  - *Explanation:* Incorrect. The problem is who votes, not when.
- **C.** Survivorship: the users who give up leave instead of voting, so the people who remain to click are not representative. Report the rate next to the score ("79% of 12.7%"), track abandonment as its own metric (no final answer viewed, or the same question re-asked within 2 minutes), and judge the complaints with the tail rule.
  - *Explanation:* Correct. Feedback is a targeting signal and a calibration set, not a population estimate. The headline quality comes from the judge's head sample.
- **D.** Selection bias in the judge; fix by judging only voted traces.
  - *Explanation:* Incorrect. That would import the feedback bias into the judge.

**Correct answer: C**

---

### Q7. A drift report row reads: `judge_grounded  mean 0.91 → 0.89 (−2.2%)  PSI 0.18`. Using `DriftThresholds` (PSI 0.10 watch, 0.25 alert; mean −15% alert), what is the status and the next step?

*Related lecture: 8.5 Drift detection: compare this week to last week*

- **A.** OK: the mean barely moved.
  - *Explanation:* Incorrect. The mean can stay nearly flat while the distribution changes shape, for example when part of the traffic gets worse. That is what PSI catches.
- **B.** Watch: PSI is between 0.10 and 0.25 even though the mean moved only 2%, so part of the distribution shifted; open the low cluster and slice by `prompt_version` to name the change.
  - *Explanation:* Correct. A small mean delta with a sizeable PSI is a distribution that split. The split by prompt version is what turns "quality fell" into "prompt v2 did it".
- **C.** Alert: any PSI above 0.1 pages someone.
  - *Explanation:* Incorrect. 0.10 to 0.25 is watch; alert starts at 0.25 or a mean drop of 15%.
- **D.** PSI cannot be applied to judge scores because they are bounded in 0 to 1.
  - *Explanation:* Incorrect. PSI works on any binned distribution; bounded scores bin perfectly well.

**Correct answer: B**

---

### Q8. `make drift` on the two-week store (Lab 5) shows: `judge_grounded` alert, 0.943 → 0.720, PSI 2.013; `judge_resolved` alert, PSI 3.678; `latency_ms` watch, mean −25.9% (improved); `steps` ok. What does this combination say?

*Related lecture: 8.5 Drift detection: compare this week to last week*

- **A.** An infrastructure incident: latency moved, so the provider changed.
  - *Explanation:* Incorrect. Latency *improved*; the drift report flags the shape change but never alerts on an improvement.
- **B.** Nothing actionable: two metrics alert every week.
  - *Explanation:* Incorrect. A PSI around 2 is far beyond the 0.25 alert line; this is a real change.
- **C.** The judge drifted, not Atlas; recalibrate the judge.
  - *Explanation:* Incorrect as the first step. Check what changed in Atlas in the window before blaming the judge; feedback moving the same way (79% → 74% positive on the drift day) corroborates a real regression.
- **D.** The output got worse while the operation got cheaper and faster: shorter, vaguer answers. That is the signature of a prompt or model change, not infrastructure; the Quality page's split by prompt version (v1 grounded 0.941 vs v2 0.586) names the release, and moving the `production` label back to v1 is the fix.
  - *Explanation:* Correct. This is Incident 3's signature. A cost-only or latency-only view would have rewarded the regression.

**Correct answer: D**
