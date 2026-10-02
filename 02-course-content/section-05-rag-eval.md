# Section 5: RAG Agent Evaluation

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 05 (curriculum `01-curriculum/full-curriculum.md`, Module 05)
> **Section runtime:** 30 minutes (4 lectures)
> **Running example:** the TechCorp Policy Assistant, `agents/rag_agent.py`: 14 internal policy documents in three domains (HR, IT security, travel and expense), a keyword retriever that stands in for vector search, and a `gpt-4.1-mini` generator.
> **Source of truth:** `14-quality-review/course2-bible.md` (taxonomies, versions, demo outputs) and the code in `04-code-examples/agent-eval-framework/`. If this script and the code disagree, the code wins.
> **Production format:** HeyGen avatar for `[AVATAR]` blocks; OBS screen recording for `[SCREEN]`, `[CODE]` and `[DEMO]`; slides built from `[SLIDE]` cues by `slide_builder.py`. Diagrams are Course 2 masters in `10-graphics/diagrams/` (D-numbers).
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "Verified: openai 2.54.0 | ragas 0.4.3 | deepeval 4.2.7. Offline mode: mock LLM + mock judge."
> **Numbers:** every score in this section comes from offline mode (`OFFLINE=1`, deterministic mock LLM and mock judge). They are stable teaching numbers, not live `gpt-4.1` scores. Where a live run is intended, the speaker notes say "re-capture live before recording".
> **Word counts** are spoken words only (narration, recap and transition). Build-along lectures run below 140 words per minute to leave room for commands, output and on-screen reading.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 5.1 | The RAG Quality Problem: Retrieval vs. Generation | Diagram | 7:00 | 873 |
| 5.2 | RAGAS Metrics: Context Precision, Recall, Faithfulness | Demo | 8:00 | 787 |
| 5.3 | Evaluating Retrieval and Generation Separately | Build-along | 8:00 | 783 |
| 5.4 | [PROJECT 2] Evaluate an Enterprise RAG Agent | Build-along | 7:00 | 706 |
| | **Total** | | **30:00** | **3,149** |

**Cue legend**

| Cue | Meaning |
|---|---|
| [AVATAR] | HeyGen avatar on camera. Each block stays under about 60 seconds of speech. |
| [SLIDE n: title] | Full-screen slide. The bullets or `Diagram:` line underneath are the slide content; the prose after it is voice-over. |
| [SCREEN: ...] | OBS screen recording of the editor, terminal or browser. |
| [CODE: ...] | Code shown on screen. The fenced block is the exact code from the named file. |
| [DEMO: ...] | Real command output. The fenced block is pasted from an actual run (trimmed where marked). |
| [B-ROLL: ...] | Cutaway animation or footage. |
| [PAUSE] | One-beat pause (about 1 second). |

**Code names used in this section (matched to `04-code-examples/agent-eval-framework/`):** `retrieve_context`, `generate_answer`, `run_rag_agent`, `POLICY_DOCUMENTS` in `agents/rag_agent.py`; `to_sample`, `build_dataset`, `make_metrics`, `ascore_sample`, `evaluate_dataset`, `aggregate`, `diagnose`, `RAG_THRESHOLDS` in `evaluators/ragas_suite.py`; dataset `datasets/golden_rag.json` (RAG-HR-01 to RAG-TE-05); RAGAS classes `SingleTurnSample`, `EvaluationDataset`, `Faithfulness`, `AnswerRelevancy`, `ContextPrecision`, `ContextRecall` (from `ragas.metrics.collections`), `llm_factory`, `embedding_factory`.

---

## Lecture 5.1 — The RAG Quality Problem: Retrieval vs. Generation

| Field | Value |
|---|---|
| ID | 5.1 |
| Title | The RAG Quality Problem: Retrieval vs. Generation |
| Type | Diagram (slides + avatar, one terminal demo) |
| Target duration | 7:00 (about 873 spoken words, 6:14 of talking at 140 wpm) |
| Learning objectives | 1. Draw the RAG pipeline and name its two components, the retriever and the generator. 2. Classify a RAG failure as a retrieval problem (precision or recall) or a generation problem (faithfulness or relevance). 3. Use the two-question decision tree to decide which component to fix first. |
| Prerequisites | Module 4 (faithfulness and answer relevancy as DeepEval metrics); Lecture 2.3 (the five-layer agent eval pyramid) |
| Files used | `agents/rag_agent.py` (`retrieve_context`); `evaluators/ragas_suite.py` (`diagnose`, `RAG_THRESHOLDS`); `demos/m05_rag_failure_dissection.py`; diagram D9 (`10-graphics/diagrams/D9-rag-retrieval-vs-generation.svg`, builds 1 and 2) |
| Version banner | `Verified: openai 2.54.0 | ragas 0.4.3` (printed by the demo) |

### Script

[AVATAR]
An employee asks TechCorp's policy assistant a simple question. "What class can I fly on a long flight?" The assistant answers: "The policy documents provided don't cover that question." [PAUSE] But they do. Section 7.2 of the travel policy says premium economy for flights of six hours or more. So who got it wrong? The model, or the search? If you guess, you can spend a week tuning the wrong half.

By the end of this lecture, you'll be able to split any RAG failure into a retrieval problem or a generation problem, and point to the numbers that prove which one.

[SLIDE 1: Meet the TechCorp Policy Assistant]
- 14 internal policy documents, three domains
- HR, IT security, travel and expense
- Retriever returns the top 3 documents
- `gpt-4.1-mini` answers only from those 3
- Every answer cites its policy section
Footer: Verified: openai 2.54.0 | ragas 0.4.3. Offline mode: mock LLM + mock judge.

Here's the agent you'll evaluate all through this module. It's an internal assistant for TechCorp employees. Fourteen policy documents in three domains. HR covers vacation, remote work and benefits. IT security covers passwords, devices and phishing. Travel and expense covers flights, meals and mileage.

Where does this sit in your test strategy? In the five-layer pyramid from Module 2, everything in this section is layer two: component evals. Instead of grading the agent as one black box, you grade its parts.

[SLIDE 2: RAG: retrieval or generation?]
Diagram: D9 build 1 (the pipeline). Question goes into the retriever, the retriever returns the top-3 chunks, the generator reads them, the answer comes out. Retrieval path in blue, generation path in green.

A RAG agent has two jobs. First, the retriever searches the documents and picks the three that look most relevant. Second, the generator, our language model, writes an answer using only those three.

Think of a research assistant and a writer. The assistant pulls folders from the filing cabinet. The writer drafts the memo from whatever lands on the desk. If the memo is wrong, was it the wrong folders, or a bad writer?

[SLIDE 3: Four ways RAG goes wrong]
- Retriever returns noise: a precision problem
- Retriever misses the answer: a recall problem
- Generator ignores the context it was given
- Generator adds facts the context doesn't contain

There are four classic failures, two per half. The retriever can return noise: three documents, but only one is useful. That's a precision problem. Or it can miss the right document entirely. That's a recall problem.

The generator can ignore good context and answer from memory. Or it can embellish, adding facts that aren't in the documents. Both are the hallucination failure mode from Module 1, just with a clearer culprit.

So which of the four do you think hit our flight question? [PAUSE] Hold that thought. The data will tell us in a minute.

[SLIDE 4: Two questions find the broken half]
Diagram: D9 build 2 (which half failed?). Wrong answer, then "Were the right documents retrieved?" No leads to "Retrieval failure: precision or recall". Yes leads to "Generation failure: faithfulness or relevance".

Here's the whole diagnosis in two questions. Question one: were the right documents retrieved? If no, stop. Fix retrieval first, because no prompt can rescue a writer who never got the right folder. If yes, ask question two: did the generator use them faithfully, and did it answer what was asked? If no, it's a generation problem.

[SLIDE 5: One metric per failure]
- Context precision: are useful chunks ranked first?
- Context recall: did retrieval find everything needed?
- Faithfulness: is every claim backed by context?
- Answer relevancy: does it answer the question?

Each question maps to metrics. Context precision and context recall grade the retriever. Faithfulness and answer relevancy grade the generator. You'll compute all four with RAGAS in the next lecture.

One trap. Why would a perfectly faithful answer still be wrong? Because faithfulness only checks the answer against what was retrieved. If the retriever hands over the vacation policy for a travel question, the generator can be one hundred percent faithful to the wrong document. That's why you never read faithfulness alone.

[CODE: `agents/rag_agent.py`, `retrieve_context`, lines with the score formula highlighted]
```python
def retrieve_context(
    query: str,
    top_k: int = 3,
    include_noise: bool = False,
    remove_stopwords: bool = False,
) -> list[dict]:
    """
    Keyword retrieval standing in for vector search.

    Score = 3 x (query words in the title) + (query words in the content).
    With remove_stopwords=False (the shipped default) words like "the" and
    "for" also count, which is the retrieval weakness Module 5 diagnoses.
    """
    docs = POLICY_DOCUMENTS + (NOISE_DOCUMENTS if include_noise else [])
    q = _words(query, remove_stopwords)
    scored = []
    for i, doc in enumerate(docs):
        score = 3 * len(q & _words(doc["title"], remove_stopwords)) + len(
            q & _words(doc["content"], remove_stopwords)
        )
        scored.append((score, -i, doc))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [doc for _score, _i, doc in scored[:top_k]]
```

Here's the retriever. It's a keyword scorer standing in for a vector database, so you can see every decision it makes. A match in the title counts three times. A match in the body counts once. And by default, little words like "can", "on" and "a" count too. Can you see the problem coming?

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`. Type the command, run it, then zoom on the BEFORE block, then the AFTER block.]

```bash
uv run python demos/m05_rag_failure_dissection.py
```

[DEMO: Output (banner trimmed)]
```text
BEFORE: naive keyword retriever
  retrieved: ['vacation-001', 'itsec-001', 'travel-002']  (the answer lives in travel-001)
  answer   : The policy documents provided don't cover that question. Please contact HR or the IT Service Desk for help.
  RAGAS    : {'faithfulness': 0.0, 'answer_relevancy': 0.0, 'context_precision': 0.0, 'context_recall': 0.0}
  diagnosis: both

AFTER: stop words removed
  retrieved: ['itsec-001', 'travel-001', 'vacation-001']  (the answer lives in travel-001)
  answer   : Economy class is required for flights under 6 hours; premium economy is allowed for flights of 6 hours or more. (Source: Travel Booking (Section 7.2))
  RAGAS    : {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 0.5, 'context_recall': 1.0}
  diagnosis: retrieval
```

Look at BEFORE. The retriever returned the vacation policy, the password policy and the meals policy. Travel booking, the one document with the answer, isn't there. Context recall is zero. Question one already has its answer: wrong documents.

The generation scores are zero too, which is why the diagnosis says "both". But notice what the generator actually did. With no useful context, it said it didn't know. That's honest behavior. The real cause sits upstream.

[SCREEN: Same terminal, zoom on the AFTER block; highlight `travel-001` in the retrieved list and "(Section 7.2)" in the answer.]

Now AFTER. One change, in the retriever only: stop words no longer count. Travel booking comes back, the answer is right, and it cites Section 7.2. Faithfulness, relevancy and recall all hit 1.0. Not one word of the prompt changed.

But the diagnosis still says "retrieval". Why? Context precision is 0.5. The right document came back second, behind the password policy. That's below our 0.7 threshold. The answer is right today, but a ranking that weak will bite you on the next question.

[CODE: `evaluators/ragas_suite.py`, `diagnose`]
```python
def diagnose(scores: dict[str, float]) -> str:
    """Module 5 rule of thumb: which component to fix."""
    retrieval_bad = scores.get("context_recall", 1) < RAG_THRESHOLDS["context_recall"] or scores.get("context_precision", 1) < RAG_THRESHOLDS["context_precision"]
    generation_bad = scores.get("faithfulness", 1) < RAG_THRESHOLDS["faithfulness"] or scores.get("answer_relevancy", 1) < RAG_THRESHOLDS["answer_relevancy"]
```

That diagnosis is just the decision tree in code. Recall or precision under 0.7 flags retrieval. Faithfulness under 0.8, or relevancy under 0.7, flags generation. Both flags, and you fix retrieval first.

[AVATAR]
Here's the habit to take away. When a RAG answer is wrong, don't open the prompt first. Open the list of retrieved documents. It takes ten seconds, and in the flight example it would have saved the whole investigation. Then score the two halves separately. That's the plan for the next three lectures: the four metrics in 5.2, isolated component tests in 5.3, and a full diagnostic report in 5.4.

[SLIDE 6: Recap]
- RAG has two halves: retrieval, then generation
- First ask: were the right documents retrieved?
- Fix the half the metrics point to

### Recap

A RAG agent fails in two places. Ask first whether the right documents came back, using context precision and recall, and only then judge the generator with faithfulness and answer relevancy. Our flight question looked like a model problem and turned out to be a retriever that counted stop words.

### Transition

In Lecture 5.2, you'll compute those four RAGAS metrics yourself on five policy questions, using the current RAGAS 0.4 API.

### Speaker notes: common student mistakes / Q&A

- **Offline numbers.** All scores here come from the deterministic mock judge (`OFFLINE=1`). The retrieval results (`retrieved` lists) are real code behaviour and identical live, because the retriever is a keyword scorer. The RAGAS scores are re-capture live before recording if you want `gpt-4.1` judge numbers on screen.
- **"Why does the diagnosis say 'both' in BEFORE?"** When recall is zero, the generator has nothing to work with, so generation metrics collapse too. The decision tree says: fix retrieval first, then re-measure generation.
- **"Context precision 0.5 with the right answer?"** Precision is rank-aware: one useful chunk at rank 2 of 3 scores 0.5. A correct answer does not mean a healthy retriever.
- **"Is a keyword retriever realistic?"** It stands in for vector search so that every retrieval decision is visible. The diagnosis method is identical for embeddings; Project 2's extension idea swaps in a real vector store.
- Do not say "70% of RAG failures are retrieval failures" or similar; there is no source in the repo (A6).

---

## Lecture 5.2 — RAGAS Metrics: Context Precision, Recall, Faithfulness

| Field | Value |
|---|---|
| ID | 5.2 |
| Title | RAGAS Metrics: Context Precision, Recall, Faithfulness |
| Type | Demo |
| Target duration | 8:00 (about 787 spoken words, 5:37 of talking at 140 wpm; the rest is code and output on screen) |
| Learning objectives | 1. Build RAGAS 0.4 `SingleTurnSample` and `EvaluationDataset` objects with the `reference` field. 2. Create the four metric classes from `ragas.metrics.collections` with an LLM from `llm_factory` and score them with `ascore`. 3. Read per-question and aggregate scores and explain why an average can hide a broken row. |
| Prerequisites | 5.1 |
| Files used | `evaluators/ragas_suite.py` (`to_sample`, `make_metrics`, `ascore_sample`, `aggregate`); `demos/m05_ragas_metrics.py`; `datasets/golden_rag.json` |
| Version banner | `Verified: openai 2.54.0 | ragas 0.4.3` |

### Script

[AVATAR]
Five policy questions. Four metrics. Four rows of perfect scores, and one row of zeros. In that broken row, the right document came back at rank one, and the answer was still wrong. [PAUSE] Which metrics catch that? And which ones stay at a perfect 1.0? By the end of this lecture, you'll be able to score a RAG agent with RAGAS 0.4 and read every number it gives you.

[SLIDE 1: RAGAS 0.4 in three objects]
- `SingleTurnSample`: one question, answer, contexts, reference
- `EvaluationDataset`: a list of samples
- Metric classes from `ragas.metrics.collections`
- `await metric.ascore(...)` returns `.value`
Footer: Verified: openai 2.54.0 | ragas 0.4.3. Offline mode: mock LLM + mock judge.

RAGAS is an open-source library built for exactly this job: scoring RAG pipelines. You need three objects. A single-turn sample holds one question, the agent's answer, the retrieved contexts and a reference answer. An evaluation dataset is a list of samples. And each metric is a class you score asynchronously.

[SLIDE 2: Old tutorials, old API]
- Old: `from ragas.metrics import faithfulness`
- Old: `evaluate(Dataset.from_dict(...))`
- Old field name: `ground_truth`
- Now: metric classes, `ascore`, and `reference`

A warning before you search the web. Most RAGAS tutorials show the older API: lowercase metric objects, a Hugging Face dataset and a column called ground truth. In RAGAS 0.4.3, those lowercase imports are gone from `ragas.metrics`, and the ground-truth field is called reference. If you copy an old blog post, it won't run.

[CODE: `evaluators/ragas_suite.py`, `to_sample`]
```python
def to_sample(question: str, rag_result: dict, reference: str | None = None) -> SingleTurnSample:
    return SingleTurnSample(
        user_input=question,
        response=rag_result["answer"],
        retrieved_contexts=rag_result["retrieved_contexts"],
        reference=reference,
    )
```

Here's how one agent run becomes a sample. The user input is the employee's question. The response is the agent's answer. Retrieved contexts are the three document texts the retriever returned. And reference? Who writes that? A human does. It's the correct answer, from the golden dataset. Fifteen of those references live in `golden_rag.json`.

[CODE: `evaluators/ragas_suite.py`, `make_metrics` and the live LLM factory]
```python
# live: llm_factory("gpt-4.1", client=AsyncOpenAI())
#       embedding_factory("openai", model="text-embedding-3-small", client=AsyncOpenAI())

def make_metrics() -> dict[str, Any]:
    llm, emb = ragas_llm(), ragas_embeddings()
    return {
        "faithfulness": Faithfulness(llm=llm),
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=emb, strictness=1 if is_offline() else 3),
        "context_precision": ContextPrecision(llm=llm),
        "context_recall": ContextRecall(llm=llm),
    }
```

Every metric needs a judge model. Live, that's `gpt-4.1` through RAGAS's `llm_factory`. Answer relevancy also needs embeddings, so it gets `text-embedding-3-small`. Offline, the course swaps in a mock judge that implements RAGAS's own base classes, so the real metric code still runs. That's why you'll get my exact numbers without an API key.

So what does each metric actually do? Let's take them one at a time.

[SLIDE 3: How each metric scores]
- Faithfulness: answer claims supported by contexts
- Answer relevancy: questions regenerated from the answer
- Context precision: useful chunks ranked above useless ones
- Context recall: reference claims found in contexts

Faithfulness splits the answer into individual claims and asks the judge whether each one can be inferred from the retrieved contexts. Five claims, four supported, gives 0.8.

Answer relevancy works backwards. The judge reads the answer and writes the questions it seems to answer, three of them when running live. Those are compared with the real question using embeddings. A vague or non-committal answer scores near zero.

Context precision asks, for each retrieved chunk, was this useful for reaching the reference? Useful chunks ranked first score high. Context recall breaks the reference into claims and checks how many appear in the retrieved contexts. Which two of these need a reference answer? [PAUSE] Precision and recall. Faithfulness and relevancy don't.

[CODE: `evaluators/ragas_suite.py`, `ascore_sample` (each metric gets only the fields it reads)]
```python
async def ascore_sample(sample: SingleTurnSample, metrics: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for name, metric in metrics.items():
        if name == "faithfulness":
            r = await metric.ascore(user_input=sample.user_input, response=sample.response, retrieved_contexts=sample.retrieved_contexts)
        elif name == "answer_relevancy":
            r = await metric.ascore(user_input=sample.user_input, response=sample.response)
        elif name == "context_precision":
            r = await metric.ascore(user_input=sample.user_input, reference=sample.reference, retrieved_contexts=sample.retrieved_contexts)
        else:  # context_recall
            r = await metric.ascore(user_input=sample.user_input, retrieved_contexts=sample.retrieved_contexts, reference=sample.reference)
        v = float(r.value)
        out[name] = 0.0 if math.isnan(v) else round(v, 3)
    return out
```

And here's the scoring loop. Each metric's `ascore` takes only the fields it reads, which is a nice way to remember the slide. It returns a metric result, and `.value` is the score between zero and one. One defensive line: if a judge call fails and RAGAS returns not-a-number, we record zero, so a broken judge can never look like a pass.

[SCREEN: Terminal. Run the demo; zoom on the table, then the Aggregate line.]

```bash
uv run python demos/m05_ragas_metrics.py
```

[DEMO: Output (banner trimmed)]
```text
EvaluationDataset with 5 SingleTurnSamples (user_input, response, retrieved_contexts, reference)

id         faithfulness  answer_relevancy  context_precision  context_recall
---------  ------------  ----------------  -----------------  --------------
RAG-HR-01  1.0           1.0               1.0                1.0
RAG-HR-04  1.0           1.0               1.0                1.0
RAG-IT-03  1.0           1.0               1.0                1.0
RAG-TE-02  1.0           1.0               1.0                1.0
RAG-TE-05  0.0           0.0               1.0                1.0

Aggregate: {'faithfulness': 0.8, 'answer_relevancy': 0.8, 'context_precision': 1.0, 'context_recall': 1.0}
```

Five questions: vacation days, sick notes, lost laptops, receipts, and mileage. Four are perfect. Now RAG-TE-05: "What is the mileage reimbursement rate for using my own car?"

Read the right two columns first. Precision 1.0, recall 1.0. The retriever did its job; the mileage policy came back. Now the left two. Faithfulness zero, relevancy zero. The generator answered that the documents don't cover it, which the context it was given contradicts. RAGAS also scores a non-committal answer as irrelevant. That's a generation failure, pinned down without reading a single trace.

[SLIDE 4: Averages hide broken rows]
- Faithfulness average: 0.8
- Faithfulness threshold: 0.8
- Aggregate passes; RAG-TE-05 scored zero

Now the aggregate line. Faithfulness averages 0.8, exactly our threshold. If your gate only checks averages, this run passes, with one employee told the mileage policy doesn't exist. Would you ship that? Gate on the per-question rows as well as the average.

[SLIDE 5: The course's RAG thresholds]
- Faithfulness: 0.8
- Answer relevancy: 0.7
- Context precision: 0.7
- Context recall: 0.7
- Source: `RAG_THRESHOLDS` and `config/eval_config.yaml`

Where do those thresholds come from? They live in two places in the repo: `RAG_THRESHOLDS` in the RAGAS suite, and the faithfulness and relevance dimensions in `eval_config.yaml`. Faithfulness gets the strictest bar, 0.8, because an unsupported claim about a policy is the costliest mistake. Treat these as starting points. Once you have a few weeks of human-reviewed results, move them to match what your reviewers call acceptable.

[AVATAR]
One cost note before you run this live. Every metric is at least one judge call per sample, so five samples and four metrics means twenty or more `gpt-4.1` calls. That's cheap for five questions and real money for five thousand, so check current pricing and sample wisely.

[SLIDE 6: Recap]
- RAGAS 0.4: samples, datasets, metric classes
- Precision and recall grade the retriever
- Read rows, not just averages

### Recap

RAGAS 0.4 scores a RAG agent from samples that carry the question, answer, retrieved contexts and a reference. Context precision and recall grade the retriever, faithfulness and answer relevancy grade the generator, and a healthy average can still hide a row of zeros.

### Transition

RAG-TE-05 says "generation", but that's still an end-to-end guess. In Lecture 5.3, you'll prove it by testing the retriever and the generator separately.

### Speaker notes: common student mistakes / Q&A

- **Offline numbers.** The 1.0 and 0.0 scores come from the mock judge. RAG-TE-05 is a deliberate offline generation miss (see `tests/component/test_rag_components.py::test_known_generation_failure_is_reported`); live, `gpt-4.1-mini` may answer it correctly. Re-capture live before recording if you show live scores, and say "in offline mode" if you keep these.
- **`ImportError: cannot import name 'faithfulness'`**: an old tutorial. Use `from ragas.metrics.collections import Faithfulness` (class, capital F).
- **NaN scores**: usually a missing `reference` (precision and recall need it) or a failed judge call. The course code turns NaN into 0.0 so it fails loudly.
- **"Twenty or more judge calls"** is a floor, not an exact count: some metrics make more than one call per sample. Prices: `gpt-4.1` $2.00 in / $8.00 out per million tokens (verify current pricing).
- **`datasets` shadowing**: the repo's data folder is not a Python package, because a package named `datasets` would shadow Hugging Face `datasets`, which RAGAS imports.

---

## Lecture 5.3 — Evaluating Retrieval and Generation Separately

| Field | Value |
|---|---|
| ID | 5.3 |
| Title | Evaluating Retrieval and Generation Separately |
| Type | Build-along |
| Target duration | 8:00 (about 783 spoken words, 5:36 of talking at 140 wpm; the rest is typing, test runs and output) |
| Learning objectives | 1. Test the retriever alone with a hit-at-3 and rank check that needs no LLM. 2. Test the generator alone by giving it the perfect context. 3. Use the two results to decide whether to fix chunking and ranking or the prompt and model. |
| Prerequisites | 5.2 |
| Files used | `agents/rag_agent.py` (`retrieve_context`, `generate_answer`); `demos/m05_component_isolation.py`; `tests/component/test_rag_components.py`; `evaluators/heuristics.py` (`correctness`) |
| Version banner | `Verified: openai 2.54.0 | ragas 0.4.3` |

### Script

[AVATAR]
RAG-TE-05 failed end to end. You could spend a day tuning chunk sizes and re-indexing. Or you could spend ten seconds on two tests that tell you the retriever is fine and the generator isn't. [PAUSE] By the end of this lecture, you'll be able to test each half of a RAG agent on its own and know exactly which one to fix.

[SLIDE 1: Component isolation]
- Retriever alone: did the right document come back?
- Generator alone: given perfect context, is it right?
- Each test isolates exactly one component
Footer: Verified: openai 2.54.0 | ragas 0.4.3. Offline mode: mock LLM + mock judge.

It's the oldest idea in testing: isolate the component. An end-to-end score blends two parts. So you test the retriever with no generator at all, and the generator with a perfect retriever. Where would a mechanic start with a car that won't start: the whole car, or the battery? [PAUSE] The battery. One part at a time.

[SLIDE 2: Two halves, two levers]
- Retriever test: query in, top-3 IDs out
- Score the retriever by hit and rank
- Generator test: perfect chunks in, answer out
- Score the generator against the reference

Here's why that matters. The two halves have different fixes. A retriever problem is fixed with chunking, ranking, metadata filters or better embeddings. A generator problem is fixed with the prompt or the model. Fixing the wrong one costs you days and changes nothing.

[CODE: `agents/rag_agent.py`, the two entry points]
```python
retrieve_context(question)            -> list[dict]
generate_answer(question, contexts)   -> dict
run_rag_agent(question)               -> both, end to end
```

The policy assistant was built for this. Retrieval and generation are separate functions. `run_rag_agent` just calls one, then the other. If your own RAG code hides both steps inside one call, that's your first refactor: you can't test what you can't call.

[CODE: `demos/m05_component_isolation.py`, the isolation loop]
```python
docs = {d["id"]: d for d in POLICY_DOCUMENTS}
rows = []
for c in load("golden_rag")[10:]:
    got = [d["id"] for d in retrieve_context(c["question"])]
    hit = c["reference_context_ids"][0] in got
    gen = generate_answer(c["question"], [docs[i] for i in c["reference_context_ids"]])  # perfect context
    correct = h.correctness(gen["answer"], c["reference"])
```

Let's build it. Take the five travel and expense questions from the golden set. Each golden case knows which document holds its answer, in `reference_context_ids`.

For the retriever, call `retrieve_context` and check two things. Hit at 3: is the right document anywhere in the top three? And rank: where? No model is involved, so this test is free, instant and deterministic. You can run it on every commit.

For the generator, skip retrieval entirely. Look up the reference documents by ID and hand them straight to `generate_answer`. That's the perfect context. Then score the answer against the reference. What does it mean if the generator fails even here? [PAUSE] It means no retriever upgrade will ever fix it.

[SLIDE 3: Reading the two results]
- Hit and correct: healthy
- Hit but wrong: fix the generator
- Miss: fix the retriever first
- Miss and wrong: retriever first, then re-test

Four combinations, four actions. Retriever hits and the generator is correct: healthy. Retriever hits but the generator is wrong even with perfect context: fix the prompt or the model. Retriever misses: fix retrieval, whatever the generator did. And if both fail, retrieval first, then re-test the generator.

[SCREEN: Terminal. Run the demo; highlight the RAG-TE-05 row.]

```bash
uv run python demos/m05_component_isolation.py
```

[DEMO: Output (banner trimmed)]
```text
id         retriever_hit@3  rank  generator_correct(perfect ctx)  fix
---------  ---------------  ----  ------------------------------  ---------
RAG-TE-01  yes              1     1.00                            -
RAG-TE-02  yes              1     1.00                            -
RAG-TE-03  yes              1     1.00                            -
RAG-TE-04  yes              1     1.00                            -
RAG-TE-05  yes              1     0.00                            generator

Retriever misses -> fix chunking/ranking. Generator wrong with perfect context -> fix the prompt or model.
```

All five retriever checks hit, every one at rank one. Four generator checks score 1.00. And RAG-TE-05, the mileage question: the retriever found the mileage policy at rank one, yet even with that perfect context the generator scores zero. Verdict: generator.

Why would it miss? The employee asks for the mileage rate "for using my own car". The policy says "personal car use for business is reimbursed at seventy cents per mile". Same meaning, different words, and this generator didn't connect them. That's a prompt-and-model problem. Retrieval is innocent.

[SLIDE 4: Retriever scores you get for free]
- Hit at 3: answer document in the top three?
- Rank: one is solid, three is fragile
- No model calls: run on every commit
- Generator test: one model call per case

Why track rank if the hit already passed? Because a document at rank three survives today, but one more similar document in the index pushes it out of the top three. So track rank over time, not just hits. And look at cost. The retriever test makes zero model calls. The generator test makes one call per case, so fifteen calls of `gpt-4.1-mini` live, a fraction of a cent at current prices (verify current pricing). Both are cheap enough to sit in the component layer of the pyramid.

[SCREEN: VS Code, `tests/component/test_rag_components.py`. Scroll through the three test functions named below.]

[CODE: `tests/component/test_rag_components.py` (three of the tests)]
```python
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_retriever_hit_at_3(case):
    assert case["reference_context_ids"][0] in [d["id"] for d in retrieve_context(case["question"])]


def test_stopword_fix_repairs_the_flight_question():
    q = "What class can I fly on a long flight?"
    assert "travel-001" not in [d["id"] for d in retrieve_context(q)]
    assert "travel-001" in [d["id"] for d in retrieve_context(q, remove_stopwords=True)]


@pytest.mark.parametrize("case", [c for c in CASES if c["id"] != "RAG-TE-05"], ids=lambda c: c["id"])
def test_generator_with_perfect_context(case):
    gen = generate_answer(case["question"], [DOCS[i] for i in case["reference_context_ids"]])
    assert h.faithfulness(gen["answer"], DOCS[case["reference_context_ids"][0]]["content"]) == 1.0
```

A demo is nice. A test is better. The same checks live in the component layer of the test suite. The retriever test runs once for each of the 15 golden cases. There's a regression test for the flight question from 5.1, pinning both the bug and the fix. And the generator test runs every case except RAG-TE-05, which has its own test that asserts the failure is reported.

[SCREEN: Terminal. Run the component tests.]

```bash
uv run pytest -q tests/component/test_rag_components.py
```

[DEMO: Output (trimmed)]
```text
....................................                                     [100%]
36 passed in 1.57s
```

Thirty-six tests in under two seconds, and not one API call. That's the point of component tests: they're cheap enough to run on every commit, so retrieval regressions never sneak in behind a prompt change.

[AVATAR]
So when do you reach for which test? Retriever tests run on every commit, and always after you change chunking, the index or the embedding model. Generator tests run whenever the prompt or the model changes. And the end-to-end RAGAS run from 5.2 runs on pull requests, to confirm the two halves still work together. Three tests, three triggers, and no more guessing which half broke.

[SLIDE 5: Recap]
- Test the retriever alone: hit and rank
- Test the generator with perfect context
- Fix only the half that fails

### Recap

Component isolation tests the retriever with a free hit-at-3 and rank check, and the generator with the perfect context. RAG-TE-05's retriever hit at rank one, its generator failed anyway, so the fix belongs in the prompt or the model, not in chunking.

### Transition

You now have every piece. In Lecture 5.4, Project 2, you'll run the full 15-question evaluation across all three policy domains and write the diagnostic report.

### Speaker notes: common student mistakes / Q&A

- **Offline numbers.** The generator scores use `evaluators/heuristics.correctness` (word overlap and number matching) so they run free and offline. Live, you would use the GEval correctness metric from Module 4 with `gpt-4.1`. RAG-TE-05 is a deliberate offline miss; re-capture live before recording if you want live generator scores.
- **"Why `[10:]`?"** The golden file is ordered HR, IT, travel; the slice picks the five travel and expense cases (RAG-TE-01 to 05). All 15 run in the test file.
- **"My retriever returns chunks, not whole documents."** Map chunks to their source document ID and check the ID, or store a `reference_context_ids` per chunk. Hit-at-k works the same.
- **Timing** (`36 passed in 1.57s`) varies by machine; the count is stable.
- Noise documents exist (`include_noise=True`) for a harder retriever test; Project 2's extension uses them.

---

## Lecture 5.4 — [PROJECT 2] Evaluate an Enterprise RAG Agent

| Field | Value |
|---|---|
| ID | 5.4 |
| Title | [PROJECT 2] Evaluate an Enterprise RAG Agent |
| Type | Build-along (project brief + walkthrough) |
| Target duration | 7:00 (about 706 spoken words, 5:03 of talking at 140 wpm; the rest is output on screen) |
| Learning objectives | 1. Run a 15-case RAGAS evaluation across three policy domains. 2. Produce a per-question and per-domain diagnostic that labels each failure retrieval or generation. 3. Write remediation advice, and flag rows that need human review instead of blindly trusting the judge. |
| Prerequisites | 5.1 to 5.3; Project 1 |
| Files used | `demos/m05_project2_rag_eval.py`; `datasets/golden_rag.json`; `agents/rag_agent.py`; `evaluators/ragas_suite.py`; output `reports/results/project2_report.md` (generated, git-ignored); brief `08-projects/project-2-rag-eval/README.md` |
| Version banner | `Verified: openai 2.54.0 | ragas 0.4.3` |

### Script

[AVATAR]
TechCorp's VP of People Operations has one question for you. "Our policy assistant gets things wrong. Do I fund a search upgrade, or a better model?" [PAUSE] Fifteen questions, three departments, and one report will answer that. By the end of this project, you'll have that report, with a verdict for every question and a recommendation the VP can act on.

[SLIDE 1: Project 2 brief]
- Agent: TechCorp Policy Assistant, 14 documents
- Golden set: 15 questions, 5 per domain
- Metrics: the four RAGAS metrics
- Output: per-question and per-domain diagnosis
- Deliverable: report plus your remediation advice
Footer: Verified: openai 2.54.0 | ragas 0.4.3. Offline mode: mock LLM + mock judge.

Here's the brief. The agent is the policy assistant you've used all module. The golden set has fifteen questions, five each for HR, IT security, and travel and expense. Each has a human-written reference answer and the ID of the document that holds it. You'll score every question with the four RAGAS metrics, diagnose each one, roll them up by domain, and add your own recommendations. Then write at least three questions of your own, so the golden set covers something the course didn't think of.

[CODE: `demos/m05_project2_rag_eval.py`, the core]
```python
cases = load("golden_rag")
rows = evaluate_dataset(build_dataset([to_sample(c["question"], run_rag_agent(c["question"]), c["reference"]) for c in cases]))
table([{"id": c["id"], **r, "diagnosis": diagnose(r)} for c, r in zip(cases, rows, strict=True)])
for dom in ("hr", "it_security", "travel_expense"):
    agg = aggregate([r for c, r in zip(cases, rows, strict=True) if c["domain"] == dom])
```

The pipeline is everything from this module in five lines. Load the cases. Run the agent on each question. Turn each run into a RAGAS sample. Score the dataset. Then diagnose every row, and aggregate by domain. Can you name the function that turns four scores into one word? [PAUSE] It's `diagnose`, the decision tree from 5.1.

[SCREEN: Terminal. Run the project; scroll slowly through the per-question table, then the domain table.]

```bash
uv run python demos/m05_project2_rag_eval.py
```

[DEMO: Output (banner trimmed)]
```text
id         faithfulness  answer_relevancy  context_precision  context_recall  diagnosis
---------  ------------  ----------------  -----------------  --------------  ----------
RAG-HR-01  1.0           1.0               1.0                1.0             ok
...
RAG-IT-02  1.0           0.0               1.0                1.0             generation
...
RAG-TE-01  1.0           1.0               0.833              1.0             ok
...
RAG-TE-04  1.0           1.0               0.833              1.0             ok
RAG-TE-05  0.0           0.0               1.0                1.0             generation

# Project 2 - RAG diagnostic report

| Domain | faithfulness | answer_relevancy | context_precision | context_recall | diagnosis |
|---|---|---|---|---|---|
| hr | 1.0 | 1.0 | 1.0 | 1.0 | ok |
| it_security | 1.0 | 0.8 | 1.0 | 1.0 | ok |
| travel_expense | 0.8 | 0.8 | 0.933 | 1.0 | ok |

Overall: {'faithfulness': 0.933, 'answer_relevancy': 0.867, 'context_precision': 0.978, 'context_recall': 1.0}
```

Thirteen of fifteen rows are "ok". Two say "generation". Start with the column that answers the VP's question: context recall is 1.0 in every domain. The retriever found the needed document every single time. So the search upgrade can wait.

RAG-TE-05 you already know: the mileage paraphrase gap. Two rows show context precision of 0.833. That means the judge found two useful chunks with an irrelevant one ranked between them. It's a ranking nit, not a failure.

[SCREEN: Zoom on the domain table; draw a box around each number below 1.0 and an arrow to the row that causes it.]

Now trace every domain number back to a row. HR is perfect. IT security relevancy is 0.8: that's one zero from RAG-IT-02, averaged over five questions. Travel faithfulness is 0.8: that's RAG-TE-05. Travel precision is 0.933: the two 0.833 rows. Every average below 1.0 has a single row behind it. Which is why your report always shows both levels.

[SCREEN: Terminal. Show the full RAG-IT-02 answer with `uv run python -m agents.rag_agent "Can I use SMS codes for multi-factor authentication?"`; highlight the last sentence.]

```text
Multi-factor authentication (MFA) is mandatory for email, VPN and all production systems. Approved MFA methods are the Okta Verify app or a hardware security key; SMS codes are not allowed. (Source: Password and MFA Standard (Section IT-1))
```

Now the interesting one. RAG-IT-02: "Can I use SMS codes for multi-factor authentication?" Relevancy zero. But read the answer. "SMS codes are not allowed." That's correct. It just opens with a sentence about where MFA is mandatory, and the judge reconstructed the wrong question from that opening.

So is this a bug? [PAUSE] It's a judge disagreement. In your report, it goes in a third bucket: needs human review. A flagged row is a lead, not a verdict. The engineers who earn trust are the ones who read the row before they file the ticket.

[SLIDE 2: Your report has four parts]
- Scores: per question and per domain
- Diagnosis: retrieval, generation, or human review
- Evidence: the question, answer and retrieved IDs
- Recommendation: one concrete fix per finding

Here's the shape of the report. Scores, a diagnosis per finding, evidence, and one concrete recommendation each. For this run: no retrieval spend needed, recall is perfect. One generator fix: teach the prompt that "my own car" means mileage, then re-test RAG-TE-05. And one human review item. The domain averages all read "ok", yet two real issues sit underneath them. That's the 5.2 lesson again.

[SLIDE 3: Stretch goals]
- Turn on noise documents: `include_noise=True`
- Swap the keyword retriever for embeddings
- Re-run live with the `gpt-4.1` judge

When you're done, push it. Turn on the two noise documents and watch precision fall. Swap the keyword retriever for real embeddings. Or run it live with the `gpt-4.1` judge and compare its verdict on RAG-IT-02 with the mock judge's.

[AVATAR]
How will you know your report is good? Give it to someone who hasn't seen the code. If they can tell, in under a minute, which half to fix and why, you're done. And keep it: in a job interview, "I diagnosed a policy assistant's failures to retrieval or generation, with evidence for each" is a far stronger answer than "I ran RAGAS". One more thing. Commit the golden set and the report together, so the next run has a baseline to compare against. You'll put that baseline to work in Module 11.

[SLIDE 4: Recap]
- Fifteen questions, three domains, four metrics
- Recall 1.0 everywhere: retrieval is healthy
- Read flagged rows before filing fixes

### Recap

Project 2 scores fifteen golden questions with four RAGAS metrics, diagnoses each one and rolls them up by domain. Here, perfect recall says the retriever is healthy, RAG-TE-05 is a generator fix, and RAG-IT-02 is a judge disagreement that needs a human.

[SLIDE 5: You can now]
- Split RAG failures into retrieval or generation
- Score RAG agents with RAGAS 0.4
- Write a per-domain RAG diagnostic report

### Transition

Retrieval answers questions. Tools take actions. In Lecture 6.1, you'll see why tool calling is the highest-risk part of any agent, starting with an agent that refunds a customer who only asked a question.

### Speaker notes: common student mistakes / Q&A

- **Offline numbers.** All scores are mock-judge scores. RAG-IT-02's relevancy of 0.0 is an offline judge artefact (the mock regenerates a question from the answer's first sentence); a live `gpt-4.1` judge may score it differently. That is the teaching point: read flagged rows. Re-capture live before recording if you want live scores on screen.
- **Conflicts with `08-projects/project-2-rag-eval/README.md` (follow the code; reported to T-DOCS):** the README describes an HR-only corpus of 8 documents (`datasets/hr_policies.json`, 20 vacation days), a 10-question dataset (`datasets/rag_eval_dataset.json`), the legacy RAGAS `evaluate(...)` API with `ground_truth`, `pytest tests/project2/...` commands and an older OpenAI model (not the A8 default `gpt-4.1-mini`). The code ships 14 documents in three domains, 15 cases in `datasets/golden_rag.json` (vacation is 15 days), RAGAS 0.4 classes with `reference`, and `demos/m05_project2_rag_eval.py`. The curriculum's 15-case, three-domain brief matches the code.
- **"Where is the report file?"** `reports/results/project2_report.md`, regenerated on every run and git-ignored.
- **The DeepEval layer** the curriculum mentions (HallucinationMetric, GEval) is optional here; Module 4's metrics plug in via `evaluators/deepeval_suite.to_test_case`, which already fills `retrieval_context`.
