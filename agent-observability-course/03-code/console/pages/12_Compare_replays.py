"""Compare replays (6.8, 14.2): the same day replayed into different stores, side by side.

make replay STORE=.atlas/base.sqlite
make replay STORE=.atlas/levers.sqlite CACHE=1 DIET=1 ROUTER=1
"""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console.data import compare  # noqa: E402

st.set_page_config(page_title="Atlas Ops Console: Compare replays", layout="wide")
st.title("Compare replays")
found = sorted(str(p) for p in Path(".atlas").glob("*.sqlite"))
chosen = st.multiselect("Stores (first one is the baseline)", found, default=found[:2])
if len(chosen) >= 1:
    rows = compare(chosen)
    st.dataframe(rows, hide_index=True)
    st.bar_chart(rows, x="store", y="cost_usd")
