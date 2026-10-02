"""
RAGAS 0.4 evaluation for the TechCorp Policy Assistant (Module 5, Project 2).

Uses the current RAGAS API (ragas 0.4.3):

    from ragas import EvaluationDataset, SingleTurnSample
    from ragas.llms import llm_factory
    from ragas.metrics.collections import Faithfulness, ContextPrecision, ContextRecall, AnswerRelevancy

    llm = llm_factory("gpt-4.1", client=AsyncOpenAI())
    result = await Faithfulness(llm=llm).ascore(user_input=..., response=..., retrieved_contexts=[...])
    result.value  # 0.0 - 1.0

Sample fields (SingleTurnSample): user_input, response, retrieved_contexts,
reference (the ground-truth answer; older RAGAS called it ground_truth).

Offline, ``MockRagasLLM`` and ``MockEmbeddings`` stand in for the OpenAI LLM
and embeddings: they implement RAGAS's own base classes and answer its prompts
with the deterministic rules in evaluators/heuristics.py.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
from typing import Any

from ragas import EvaluationDataset, SingleTurnSample
from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms.base import InstructorBaseRagasLLM
from ragas.metrics.collections import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness

from config.settings import embedding_model, is_offline, judge_model
from evaluators import heuristics as h

RAG_THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.7,
    "context_precision": 0.7,
    "context_recall": 0.7,
}


# ---------------------------------------------------------------------------
# Offline stand-ins
# ---------------------------------------------------------------------------

class MockRagasLLM(InstructorBaseRagasLLM):
    """Deterministic RAGAS LLM: reads the prompt's `input:` JSON and fills the response model.

    For AnswerRelevancy it "regenerates" the user's question when the answer is
    on-topic (as a good LLM would): it remembers the question it saw for each
    answer in the Faithfulness prompts. Off-topic answers produce a question
    built from the answer's own words, which scores low.
    """

    def __init__(self) -> None:
        self._questions: dict[str, str] = {}

    def generate(self, prompt: str, response_model: Any) -> Any:
        m = re.search(r"input: (\{.*\})\s*Output:\s*$", prompt, flags=re.DOTALL)
        data = json.loads(m.group(1)) if m else {}
        name = response_model.__name__
        if name == "StatementGeneratorOutput":
            self._questions[data.get("answer", "")] = data.get("question", "")
            return response_model(statements=h.sentences(data.get("answer", "")))
        if name == "NLIStatementOutput":
            ctx = data.get("context", "")
            return response_model(statements=[
                {"statement": s, "reason": "supported by context" if h.supported(s, ctx) else "not in context",
                 "verdict": int(h.supported(s, ctx) or h.is_refusal(s))}
                for s in data.get("statements", [])
            ])
        if name == "ContextPrecisionOutput":
            useful = h.overlap(data.get("answer", ""), data.get("context", "")) >= 0.3
            return response_model(reason="overlaps the reference" if useful else "unrelated to the reference", verdict=int(useful))
        if name == "ContextRecallOutput":
            ctx = data.get("context", "")
            return response_model(classifications=[
                {"statement": s, "reason": "found in context" if h.supported(s, ctx) else "missing from context",
                 "attributed": int(h.supported(s, ctx))}
                for s in h.sentences(data.get("answer", ""))
            ])
        if name == "AnswerRelevanceOutput":
            resp = data.get("response", "")
            vague = h.is_refusal(resp) or "don't cover" in resp.lower()
            seen = self._questions.get(resp, "")
            first = (h.sentences(resp) or [resp])[0]
            question = seen if seen and h.overlap(seen, first) >= 0.4 else first
            return response_model(question=question, noncommittal=int(vague))
        fields = {k: ("" if f.annotation is str else 0) for k, f in response_model.model_fields.items()}
        return response_model(**fields)

    async def agenerate(self, prompt: str, response_model: Any) -> Any:
        return self.generate(prompt, response_model)


class MockEmbeddings(BaseRagasEmbedding):
    """Bag-of-content-words embeddings over a hashed 512-dim space (deterministic)."""

    DIM = 512

    def embed_text(self, text: str, **kwargs: Any) -> list[float]:
        vec = [0.0] * self.DIM
        for w in h.words(text):
            vec[sum(map(ord, w)) * 2654435761 % self.DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    async def aembed_text(self, text: str, **kwargs: Any) -> list[float]:
        return self.embed_text(text)


def ragas_llm() -> InstructorBaseRagasLLM:
    if is_offline():
        return MockRagasLLM()
    from openai import AsyncOpenAI
    from ragas.llms import llm_factory

    return llm_factory(judge_model(), client=AsyncOpenAI())


def ragas_embeddings() -> BaseRagasEmbedding:
    if is_offline():
        return MockEmbeddings()
    from openai import AsyncOpenAI
    from ragas.embeddings import embedding_factory

    return embedding_factory("openai", model=embedding_model(), client=AsyncOpenAI())


# ---------------------------------------------------------------------------
# Building samples and scoring
# ---------------------------------------------------------------------------

def to_sample(question: str, rag_result: dict, reference: str | None = None) -> SingleTurnSample:
    return SingleTurnSample(
        user_input=question,
        response=rag_result["answer"],
        retrieved_contexts=rag_result["retrieved_contexts"],
        reference=reference,
    )


def build_dataset(samples: list[SingleTurnSample]) -> EvaluationDataset:
    return EvaluationDataset(samples=samples)


def make_metrics() -> dict[str, Any]:
    llm, emb = ragas_llm(), ragas_embeddings()
    return {
        "faithfulness": Faithfulness(llm=llm),
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=emb, strictness=1 if is_offline() else 3),
        "context_precision": ContextPrecision(llm=llm),
        "context_recall": ContextRecall(llm=llm),
    }


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


def evaluate_dataset(dataset: EvaluationDataset, metrics: dict[str, Any] | None = None) -> list[dict[str, float]]:
    """Score every sample in an EvaluationDataset with the four RAGAS metrics."""
    metrics = metrics or make_metrics()

    async def _run() -> list[dict[str, float]]:
        return [await ascore_sample(s, metrics) for s in dataset.samples]

    return asyncio.run(_run())


def aggregate(rows: list[dict[str, float]]) -> dict[str, float]:
    keys = rows[0].keys() if rows else []
    return {k: round(sum(r[k] for r in rows) / len(rows), 3) for k in keys}


def check_thresholds(scores: dict, thresholds: dict | None = None) -> dict:
    thresholds = thresholds or RAG_THRESHOLDS
    results = {m: {"score": scores.get(m, 0.0), "threshold": t, "passed": scores.get(m, 0.0) >= t} for m, t in thresholds.items()}
    results["overall_passed"] = all(r["passed"] for r in results.values() if isinstance(r, dict))
    return results


def diagnose(scores: dict[str, float]) -> str:
    """Module 5 rule of thumb: which component to fix."""
    retrieval_bad = scores.get("context_recall", 1) < RAG_THRESHOLDS["context_recall"] or scores.get("context_precision", 1) < RAG_THRESHOLDS["context_precision"]
    generation_bad = scores.get("faithfulness", 1) < RAG_THRESHOLDS["faithfulness"] or scores.get("answer_relevancy", 1) < RAG_THRESHOLDS["answer_relevancy"]
    if retrieval_bad and generation_bad:
        return "both"
    if retrieval_bad:
        return "retrieval"
    if generation_bad:
        return "generation"
    return "ok"
