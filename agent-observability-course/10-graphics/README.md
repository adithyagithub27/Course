# Course 4 graphics: AI Agent Observability & Cost Control

Master diagrams and generated slide decks (fix-plan decision A7). Specs: `../09-production/slide-deck-outline.md` (Master diagram list D1-D12), reconciled with the code and the frozen decisions. Canvas 1920x1080, Deep Navy, Inter / JetBrains Mono, palette and scene kits from `../../10-graphics/design-system.md`.

## Diagrams (`diagrams/`)

| ID | File | Diagram | Used in | Build steps (`D{n}-step{k}.svg`) |
|---|---|---|---|---|
| D1 | `D1-three-pillars.svg` | Three pillars, one foundation | 1.2, 15.1 | 1 traces; 2 quality in production; 3 cost; 4 where classic APM stops |
| D2 | `D2-architecture.svg` | The observability stack | 1.3, 13.4, 14.1, 13.2 | 1 the stack; 2 alternatives |
| D3 | `D3-trace-waterfall.svg` | One agent run, as a trace | 3.1, 5.1, 5.2, 5.6, 11.1, 1.1 | 1 happy path; 2 the loop (context bloat); 3 incident ruler |
| D4 | `D4-langfuse-on-otel.svg` | Langfuse on OpenTelemetry | 4.1, 12.1 | 1 OTel span to Langfuse observation; 2 what is not portable |
| D5 | `D5-token-anatomy.svg` | Token anatomy of one request | 6.1, 6.4, 6.5 | 1 one request; 2 caching: the cached share grows; 3 context diet: input shrinks |
| D6 | `D6-cost-rollup-tree.svg` | Rolling cost up | 6.3, 6.9, 14.4, 14.2 | 1 generations; 2 requests; 3 sessions; 4 users; 5 tenants; 6 Northwind total; 7 the feature cut |
| D7 | `D7-latency-budget.svg` | Latency budget of one request | 7.1, 7.2, 7.4, 7.6, 5.4 | 1 per-step budgets; 2 p50 vs p95; 3 fallback when the provider times out |
| D8 | `D8-slo-error-budget-burn.svg` | SLO, error budget, burn rate | 9.1, 9.5, 11.3 | 1 SLI and SLO; 2 error budget; 3 fast and slow burn |
| D9 | `D9-incident-timeline.svg` | Reading an incident timeline | 11.1, 11.2, 11.3, 11.4, 11.5 | 1 the timeline; 2 blast radius |
| D10 | `D10-telemetry-threat-model.svg` | Where PII leaks in telemetry | 10.1, 10.2 | 1 the flow and the leaks; 2 shields |
| D11 | `D11-ops-dashboard.svg` | Atlas Ops dashboard | 9.3, 14.3 | 1 p95 latency; 2 cost per resolved session; 3 task success; 4 tool error rate; 5 judge score; 6 budget remaining |
| D12 | `D12-backend-decision-matrix.svg` | Choosing a backend | 12.5, 1.3 | 1 control / self-host; 2 compliance control; 3 agent features; 4 cost model; 5 lock-in |

Interpretations of the spec (code and fix plan win): tenants are `ops`, `finance`, `hr`, `eng` (O7), not the outline's hr/it/ops/logistics; span names in D3 are the code's (`invoke_agent atlas`, `chat gpt-4.1-mini`, `execute_tool lookup_ticket`, `guardrail injection_check`, `step n`) with the Langfuse observation type in the right margin; D2's Collector shows the processors in `deploy/otel-collector.yaml` and Prometheus is fed both by the `/metrics` scrape and by Collector spanmetrics; D5 draws output and reasoning in White, not Amber, because the design system reserves Amber for warnings and thresholds; D6 features are the code's `feature_for_intent` values; D7 and D8 print no numbers except "SLO 95%" / "SLO 4 s" from `deploy/alerts.yml`; burn-rate multipliers are deliberately left off D8 because scripts and `alerts.yml` disagree today (O6 is pending). D3 master is build 1; build 2 (the loop) and build 3 (incident ruler) replace it rather than add to it. D10 master is build 2 (shields); build 1 shows the leaks.

## Slide decks (`slides/section-NN.pptx`)

Generated from `../02-lecture-scripts/section-*.md`. Recap / "You can now" cards appear once the `[SLIDE n: Recap]` cues (fix A1/A2) are in the scripts; rerun the builder after script edits.

## Regenerate

Set up once (any venv):

```bash
pip install -r voice-ai-agents-course/09-production/tools/requirements.txt
# Playwright needs a Chromium; it uses PLAYWRIGHT_BROWSERS_PATH if set (no 'playwright install' needed there).
# Install the Inter and JetBrains Mono fonts locally so previews and PowerPoint render the real type.
```

Diagrams (writes the SVGs, `index.json` and PNG previews in `diagrams/_preview/`, which git ignores):

```bash
python agent-observability-course/10-graphics/diagrams/_src/build_diagrams.py            # add --no-render to skip the PNGs
```

Slide decks (one PPTX per section from the `[SLIDE n: title]` cues; rerun after any script edit):

```bash
python voice-ai-agents-course/09-production/tools/slide_builder.py --course agent-observability-course 
python voice-ai-agents-course/09-production/tools/slide_builder.py --course agent-observability-course  --section 06   # one section
```

What the builder does: a K2 title card per lecture (title + "One idea" or first learning objective), one slide per cue (bullets max 5 per slide, longer lists continue; markdown and `Table: a | b` tables become real PPTX tables with a Teal header; fenced code in JetBrains Mono, max 15 lines; backticked identifiers in mono), K6 cards from `[SLIDE n: Recap]` cues, a "You can now" card, and a K7 next-up card from the transition. Speaker notes hold the narration that follows each cue (other visual cues are kept so the editor sees the cut). Every slide carries a lecture-ID footer. A cue whose title or "Diagram:" text matches a diagram in `diagrams/index.json` (keywords + the lectures listed below, or an explicit `D3` / `D3 build 2`) embeds the rendered PNG, picking the matching build step; any other "Diagram:" description is drawn as an amber dashed box labelled DIAGRAM TO BUILD. Decks are committed so they open without tooling; regenerate rather than hand-edit them.

Editing a diagram: change `diagrams/_src/build_diagrams.py` (layout is hand-placed; styling comes from `voice-ai-agents-course/09-production/tools/diagram_kit.py`, which follows `10-graphics/design-system.md`), rebuild, and look at the PNG in `_preview/` before committing. Master files show every build group (`<g id="build-n">`); `D{n}-step{k}.svg` files show what is visible at build k.
