"""
An LLM judge built from scratch (Module 4.3), before reaching for GEval.

    from evaluators.llm_as_judge import judge
    judge("What is your refund policy?", answer, context)  # {"score": 1-5, "reasoning": "..."}

Design choices the lecture explains:
* a rubric with anchored score levels (1 = wrong, 5 = fully correct and grounded)
* the judge sees the context, so it grades grounding, not its own knowledge
* JSON output (response_format) so the score is machine-readable
* temperature 0, and a different, stronger model than the agent (gpt-4.1 judges gpt-4.1-mini)

``agreement`` checks a judge against human labels (calibration).
"""

from __future__ import annotations

import json

from agents.llm import get_client
from config.settings import judge_model

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


def agreement(judge_scores: list[float], human_scores: list[float], tolerance: float = 1.0) -> dict:
    """Share of items where judge and human agree within `tolerance`, plus mean absolute error."""
    pairs = list(zip(judge_scores, human_scores, strict=True))
    within = sum(abs(j - h) <= tolerance for j, h in pairs)
    mae = sum(abs(j - h) for j, h in pairs) / len(pairs) if pairs else 0.0
    return {"n": len(pairs), "agreement": round(within / len(pairs), 3) if pairs else 0.0, "mae": round(mae, 3)}
