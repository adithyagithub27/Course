"""Component: DeepEval Synthesizer pipeline (Module 11.3) with the offline judge."""

from regression.synthetic_data import from_knowledge_base, from_seeds, quality_report


def test_from_seeds_expands_and_is_unique():
    goldens = from_seeds(per_seed=2)
    rep = quality_report(goldens)
    assert rep["count"] == 10 and rep["duplicate_rate"] == 0.0 and rep["with_expected_output"] == 10


def test_from_contexts():
    goldens = from_knowledge_base(per_context=1)
    assert len(goldens) == 5 and all(g.context for g in goldens)
