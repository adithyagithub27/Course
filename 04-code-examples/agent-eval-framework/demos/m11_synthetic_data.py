"""Lecture 11.3 - Synthetic test data with the DeepEval Synthesizer: expand 5
seed goldens into 20 (use --per-seed 20 for 100), then check quality.

    uv run python demos/m11_synthetic_data.py [--per-seed 4]
"""
from _common import banner

import sys

from regression.synthetic_data import from_seeds, quality_report, save, seed_goldens

banner("Lecture 11.3 - DeepEval Synthesizer", ["openai", "deepeval"])
per_seed = int(sys.argv[sys.argv.index("--per-seed") + 1]) if "--per-seed" in sys.argv else 4
print("Seeds:")
for g in seed_goldens():
    print(f"  - {g.input}")
goldens = from_seeds(per_seed)
print(f"\nGenerated {len(goldens)} goldens (generate_goldens_from_goldens, max_goldens_per_golden={per_seed}):")
for g in goldens[:8]:
    print(f"  - {g.input}")
print("  ...")
print(f"\nQuality: {quality_report(goldens)}")
print(f"Saved to {save(goldens, 'reports/results/synthetic_goldens.json')}")
print("Offline the mock judge fills the Synthesizer's templates, so wording is formulaic; live gpt-4.1 writes varied inputs.")
