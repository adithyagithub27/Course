# Garak scan of the TechCorp support agent (Lecture 8.5)

Garak (NVIDIA, `garak` 0.17.0 on PyPI, checked 2026-10-01) is a vulnerability
scanner: it fires hundreds of canned probes (DAN jailbreaks, prompt injection,
encoding tricks, data leakage) and scores replies with detectors.

Garak needs torch and pins `datasets<4`, which conflicts with RAGAS, so install
it as an isolated tool, not into this project:

```bash
uv tool install garak==0.17.0          # or: pipx install garak==0.17.0
```

Run (two terminals):

```bash
# 1. serve the real agent over HTTP (offline mock LLM, no key needed)
OFFLINE=1 uv run python -m security.agent_http --port 8765

# 2. scan it with Garak's REST generator
garak --target_type rest --generator_option_file security/garak/rest_generator.json \
      --spec probes.promptinject,probes.dan.DanInTheWild,probes.encoding.InjectBase64,probes.sysprompt_extraction \
      --generations 1 --report_prefix techcorp
```

`make garak` prints these commands (and runs them if `garak` is on PATH).
Reports land in `~/.local/share/garak/garak_runs/techcorp.report.html`.
Flags verified against the garak 0.17.0 source: `--target_type` (old name
`--model_type`, deprecated), `--generator_option_file` (`-G`), and `--spec`
(replaces the deprecated `--probes`). The scan itself was NOT run while building
the course repo (garak pulls torch, ~2 GB); do a dry run before recording.
Probe names change between releases: run `garak --list_probes` first.
