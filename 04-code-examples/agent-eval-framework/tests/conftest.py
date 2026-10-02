"""
Shared pytest setup.

* OFFLINE defaults to 1 for the test run, so `make test` never needs a key.
* Tests marked `live` run only with OFFLINE=0 and OPENAI_API_KEY set (`make eval`).
* Folders follow the five-layer agent eval pyramid (decision T4):
  unit -> component -> trajectory -> e2e -> production.
"""

import os

os.environ.setdefault("OFFLINE", "1")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

import pytest  # noqa: E402

from config.settings import is_offline  # noqa: E402


def pytest_collection_modifyitems(config, items):
    if not is_offline() and os.getenv("OPENAI_API_KEY"):
        return
    skip = pytest.mark.skip(reason="live test: set OFFLINE=0 and OPENAI_API_KEY (make eval)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def tmp_results(tmp_path):
    return tmp_path
