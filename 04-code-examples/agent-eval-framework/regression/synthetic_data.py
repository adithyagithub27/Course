"""
Synthetic test data with the DeepEval Synthesizer (Module 11.3, Lab 11.1).

    from deepeval.synthesizer import Synthesizer
    synth = Synthesizer(model=get_judge(), styling_config=StylingConfig(...))
    goldens = synth.generate_goldens_from_goldens(seed_goldens, max_goldens_per_golden=4)
    goldens = synth.generate_goldens_from_contexts(contexts=[[kb_text], ...], max_goldens_per_context=2)

Live, the judge is gpt-4.1 and the inputs are LLM-written and evolved.
Offline, MockJudge answers the Synthesizer's prompts with templates, so the
pipeline runs end to end but the questions are formulaic.

    python -m regression.synthetic_data --per-seed 4 --out reports/results/synthetic_goldens.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.synthesizer import Synthesizer
from deepeval.synthesizer.config import StylingConfig

from agents.rag_agent import POLICY_DOCUMENTS
from agents.support_agent import KNOWLEDGE_BASE
from evaluators import heuristics as h
from evaluators.golden import load
from evaluators.judge import get_judge

STYLING = StylingConfig(
    scenario="Customers of TechCorp, a SaaS company, contacting support by chat",
    task="Answer questions about plans, billing, refunds, passwords and the API",
    input_format="Short, informal customer messages in English",
    expected_output_format="One to three sentences, grounded in the knowledge base",
)


def make_synthesizer() -> Synthesizer:
    return Synthesizer(model=get_judge(), async_mode=False, styling_config=STYLING)


def seed_goldens() -> list[Golden]:
    return [Golden(**s) for s in load("synthetic_seeds")]


def from_seeds(per_seed: int = 4) -> list[Golden]:
    """Expand the 5 seed goldens: 5 x per_seed new goldens (per_seed=20 gives 100)."""
    return make_synthesizer().generate_goldens_from_goldens(seed_goldens(), max_goldens_per_golden=per_seed)


def from_knowledge_base(per_context: int = 2) -> list[Golden]:
    contexts = [[a["text"]] for a in KNOWLEDGE_BASE]
    return make_synthesizer().generate_goldens_from_contexts(contexts=contexts, max_goldens_per_context=per_context)


def from_policies(per_context: int = 2) -> list[Golden]:
    """Lab 11.1: synthetic questions from the company policy documents."""
    contexts = [[d["content"]] for d in POLICY_DOCUMENTS]
    return make_synthesizer().generate_goldens_from_contexts(contexts=contexts, max_goldens_per_context=per_context)


def quality_report(goldens: list[Golden]) -> dict:
    """Cheap checks on synthetic data: duplicates, diversity, length."""
    inputs = [g.input for g in goldens]
    vocab = set().union(*(h.words(i) for i in inputs)) if inputs else set()
    return {
        "count": len(inputs),
        "unique": len(set(inputs)),
        "duplicate_rate": round(1 - len(set(inputs)) / len(inputs), 3) if inputs else 0.0,
        "avg_words": round(sum(len(i.split()) for i in inputs) / len(inputs), 1) if inputs else 0.0,
        "distinct_content_words": len(vocab),
        "with_expected_output": sum(1 for g in goldens if g.expected_output),
    }


def save(goldens: list[Golden], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"input": g.input, "expected_output": g.expected_output, "context": g.context} for g in goldens]
    p.write_text(json.dumps(rows, indent=2))
    return p


def as_dataset(goldens: list[Golden]) -> EvaluationDataset:
    return EvaluationDataset(goldens=goldens)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-seed", type=int, default=4)
    ap.add_argument("--out", default="reports/results/synthetic_goldens.json")
    a = ap.parse_args()
    g = from_seeds(a.per_seed)
    print(json.dumps(quality_report(g), indent=2))
    print(f"saved {save(g, a.out)}")
