"""The swarm: personas, a day of traffic with incident injectors, a live load driver and an offline replay."""

import sys as _sys
from pathlib import Path as _Path

_SRC = _Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in _sys.path:  # allow running from a checkout without `pip install -e .`
    _sys.path.insert(0, str(_SRC))
