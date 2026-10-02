"""Golden datasets and loaders.

The JSON files live in ``datasets/`` (a plain data folder, deliberately not a
Python package: a package named ``datasets`` would shadow Hugging Face
``datasets``, which RAGAS imports).

    golden_support.json   10 cases, 4 categories (faq 3, account 3, escalation 2, security 2)  Modules 3, 11, 12
    golden_capstone.json  20 cases, same 4 categories, 5 each (superset of the 10)             Module 14
    golden_rag.json       15 cases, 5 per policy domain (hr, it_security, travel_expense)      Module 5, Project 2
    redteam_support.json  10 attacks on the support agent                                      Module 8
    redteam_banking.json  16 attacks on SecureBank (Project 4 attack matrix)                   Project 4
    synthetic_seeds.json  5 seed goldens for the DeepEval Synthesizer                          Module 11
"""

from __future__ import annotations

import json
from pathlib import Path

DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"

# One set of golden-dataset categories, used everywhere (Module 3 onwards).
SUPPORT_CATEGORIES = ["faq", "account", "escalation", "security"]


def load(name: str) -> list[dict]:
    """Load datasets/<name>.json, e.g. load("golden_support")."""
    return json.loads((DATASETS_DIR / f"{name}.json").read_text())
