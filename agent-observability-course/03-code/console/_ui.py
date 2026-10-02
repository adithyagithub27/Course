"""Shared Streamlit plumbing for the Ops Console pages (store picker, cached loading).

Every page starts with::

    from console._ui import page
    d, settings = page("Cost")

Pages live in ``console/pages/`` and are discovered by Streamlit automatically when the
console runs (``make console`` -> ``streamlit run console/ops_console.py``): add a file there
and it appears in the sidebar.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (ROOT, ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st  # noqa: E402

from console.data import StoreData, load_store  # noqa: E402
from northwind.config import Settings  # noqa: E402


@st.cache_resource(show_spinner="Reading the span store...", max_entries=4)
def _load(path: str, count: int, mtime: float) -> StoreData:  # noqa: ARG001 - cache keys
    return StoreData.load(load_store(path, seed=None))


def store_path() -> str:
    default = os.environ.get("ATLAS_LOCAL_STORE") or Settings.from_env().local_store_path
    if "store_path" not in st.session_state:
        st.session_state["store_path"] = default
    return st.sidebar.text_input("Span store", key="store_path")


def page(title: str, *, layout: str = "wide") -> tuple[StoreData, Settings]:
    st.set_page_config(page_title=f"Atlas Ops Console: {title}", layout=layout)
    st.title(title)
    path = store_path()
    store = load_store(path, seed=7)  # replays seed 7 into an empty store
    count = store.count()
    mtime = Path(path).stat().st_mtime if Path(path).exists() else 0.0
    store.close()
    if st.sidebar.button("Reload store"):
        _load.clear()
    return _load(path, count, mtime), Settings.from_env()


def money(x: float, digits: int = 2) -> str:
    return f"${x:,.{digits}f}"
