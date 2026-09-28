# Incident labs (Section 11)

Each folder is a self-contained dataset you can load into the Ops Console or query directly:

```bash
python - <<'PY'
from telemetry.local_store import LocalSpanStore
store = LocalSpanStore.from_jsonl("incidents/incident-01-cost-spike/spans.jsonl", "incidents/incident-01-cost-spike/scores.jsonl")
print(store.count(), "spans")
PY
python console/ops_console.py --text --store :memory: --seed -1   # or load the JSONL in your own script
```

Quicker: `make incident N=1` imports the JSONL into a temporary store and opens the text console.

| Folder | Read first | Reveal in lecture |
|---|---|---|
| `incident-01-cost-spike/` | `brief.md` | 11.2 (`solution.md`) |
| `incident-02-latency-regression/` | `brief.md` | 11.3 (`solution.md`) |
| `incident-03-quality-drift/` | `brief.md` | 11.4 (`solution.md`) |
| `incident-04-project/` | `brief.md` | never in video; `solution.md` is for instructors grading Project 2 |

Regenerate with `python incidents/generate.py` (deterministic; CI checks the files are unchanged).
