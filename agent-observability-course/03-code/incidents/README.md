# Incident labs (Section 11)

Each folder is a self-contained dataset (`spans.jsonl` + `scores.jsonl`, 300 sessions, deterministic seed) you can load into the Ops Console or query directly:

```bash
make incident N=1                                  # imports into .atlas/incident-01.sqlite and prints the text console
make console STORE=.atlas/incident-01.sqlite       # the same store in the Streamlit UI

python - <<'PY'                                    # or load the JSONL in your own script
from telemetry.local_store import LocalSpanStore
store = LocalSpanStore.from_jsonl("incidents/incident-01-cost-spike/spans.jsonl", "incidents/incident-01-cost-spike/scores.jsonl")
print(store.count(), "spans")
PY
```

| Folder | Seed / session ids | Requests | Cost | p95 | Read first | Reveal in lecture |
|---|---|---:|---:|---:|---|---|
| `incident-01-cost-spike/` | 11 / `s11-…` | 785 | $2.35 | 6,819 ms | `brief.md` | 11.2 (`solution.md`) |
| `incident-02-latency-regression/` | 22 / `s22-…` | 759 | $1.64 | 6,857 ms | `brief.md` | 11.3 (`solution.md`) |
| `incident-03-quality-drift/` | 33 / `s33-…` | 768 | $1.52 | 3,476 ms | `brief.md` | 11.4 (`solution.md`) |
| `incident-04-project/` | 44 / `s44-…` | 741 | $1.66 | 4,652 ms | `brief.md` | never in video; `solution.md` is for instructors grading Project 2 |

All four datasets are Monday 2026-09-14 (UTC). Incident 3 is the one where `scores.jsonl` (judge scores and user feedback) matters most; the other three sample the judge at 30–35%.

Regenerate with `python incidents/generate.py` (deterministic; CI regenerates into a temporary directory and fails if the committed files differ). The briefs and solutions quote figures from these files; if you change the simulator, regenerate and re-check them.
