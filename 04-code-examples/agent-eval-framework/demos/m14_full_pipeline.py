"""Lecture 14.2-14.5 / Project 5 - Run the full capstone pipeline end to end.

    uv run python demos/m14_full_pipeline.py      # same as: make capstone
"""
from _common import banner

import sys

from capstone.run_capstone import main

banner("Project 5 - full pipeline run", ["openai", "deepeval", "ragas", "langfuse"])
sys.exit(main([]))
