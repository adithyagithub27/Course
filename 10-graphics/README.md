# Course 2 graphics: AI Agent Testing & Evaluation

Master diagrams for Course 2 (fix-plan decision A7) and, once the scripts exist, generated slide decks. Course 2 has no slide-deck outline yet (T9), so the D-numbers are defined here; the outline should reuse them. Sources: the "Visual Requirements" tables in `../01-curriculum/full-curriculum.md`, with the frozen taxonomies T2 (six failure modes), T3 (five quality dimensions) and T4 (five-layer agent eval pyramid), the TechCorp support agent (T1, five tools: `lookup_customer`, `search_knowledge_base`, `create_ticket`, `send_email`, `escalate_to_human`) and A8 models (gpt-4.1-mini agent, gpt-4.1 judge). Style: `design-system.md` in this folder.

## Diagrams (`diagrams/`)

| ID | File | Diagram | Used in | Build steps (`D{n}-step{k}.svg`) |
|---|---|---|---|---|
| D1 | `D1-six-failure-modes.svg` | The six ways agents fail | 1.4, 0.1, 2.3 | 1 hallucination; 2 wrong tool selection; 3 incorrect tool arguments; 4 reasoning errors; 5 goal drift; 6 infinite loops |
| D2 | `D2-deterministic-vs-non-deterministic.svg` | Same input, different outputs | 2.1 | 1 deterministic; 2 non-deterministic |
| D3 | `D3-agent-loop.svg` | Chatbot vs agent: the loop | 1.2, 1.3 | 1 chatbot; 2 agent loop |
| D4 | `D4-agent-eval-pyramid.svg` | Test pyramid vs agent eval pyramid | 2.3, 2.1, 12.1, 14.2 | 1 unit; 2 unit evals; 3 component evals; 4 trajectory evals; 5 end-to-end evals; 6 cost and speed |
| D5 | `D5-five-dimensions-radar.svg` | Five dimensions of agent quality | 2.2, 13.3 | 1 the axes; 2 agent a; 3 agent b |
| D6 | `D6-test-strategy-matrix.svg` | Test strategy matrix | 2.3, 14.1 | 1 llm; 2 tools; 3 memory; 4 planning |
| D7 | `D7-metric-taxonomy.svg` | Agent quality metrics | 4.1, 4.2 | 1 root; 2 llm quality; 3 agent behaviour |
| D8 | `D8-llm-as-judge.svg` | LLM-as-judge | 4.3, 4.4 | 1 inputs; 2 judge; 3 structured scores; 4 calibration |
| D9 | `D9-rag-retrieval-vs-generation.svg` | RAG: retrieval or generation? | 5.1, 5.2, 5.3 | 1 the pipeline; 2 which half failed? |
| D10 | `D10-tool-call-risk-pyramid.svg` | Tool calling risk | 6.1, 6.2 | 1 wrong tool selection; 2 wrong arguments; 3 unauthorized actions |
| D11 | `D11-multi-agent-failure-cascade.svg` | How one agent's failure spreads | 7.1, 7.3 | 1 agent c fails; 2 agent b; 3 agent a; 4 user; 5 where to test |
| D12 | `D12-agent-threat-model.svg` | The AI agent threat model | 8.1, 8.2, 8.3 | 1 the agent; 2 direct injection; 3 indirect injection; 4 jailbreak; 5 pii leakage; 6 data exfiltration; 7 unauthorized actions |
| D13 | `D13-trace-anatomy.svg` | Anatomy of an agent trace | 9.1, 9.2, 9.3 | 1 trace; 2 spans; 3 root cause |
| D14 | `D14-ci-quality-gate.svg` | The CI quality gate | 12.1, 12.2, 11.2, 14.4 | 1 the pipeline; 2 pass or block |
| D15 | `D15-production-monitoring-loop.svg` | Production monitoring loop | 13.1, 13.3 | 1 production agent; 2 sample requests; 3 online evaluator; 4 score store; 5 dashboard + alerts; 6 close the loop |
| D16 | `D16-capstone-architecture.svg` | The agent quality platform | 14.1, 14.2, 14.3, 14.4, 14.5 | 1 agent under test; 2 evaluation pipeline; 3 results and dashboard; 4 CI/CD and alerting |

Interpretations: D1 severity ratings are qualitative (critical / high / medium) and are this folder's call; adjust if the curriculum assigns others. D5 compares two illustrative agent profiles (Teal and White; Amber is reserved for warnings). D6 cells are suggested test types per component and dimension, matching the test-strategy template idea; the template itself lives in `11-course-assets/templates/`. D10 draws the curriculum's tool-call risk pyramid as three stacked bands (unauthorized actions / wrong arguments / wrong tool selection). D13 durations, tokens and cost are illustrative and footnoted. Not drawn yet from the curriculum list: course roadmap, tokenization flow, context window, DeepEval architecture, test-case anatomy, RAGAS 2x2 map, MCP architecture, multi-agent topologies, kill chain, cost treemaps, governance hierarchy, scorecard and career visuals; most are better as screenshots or K3 tables.

## Slide decks (`slides/section-NN.pptx`)

`02-course-content/` (T5) does not exist yet, so no Course 2 decks are built. Once it does:

## Regenerate

Set up once (any venv):

```bash
pip install -r voice-ai-agents-course/09-production/tools/requirements.txt
# Playwright needs a Chromium; it uses PLAYWRIGHT_BROWSERS_PATH if set (no 'playwright install' needed there).
# Install the Inter and JetBrains Mono fonts locally so previews and PowerPoint render the real type.
```

Diagrams (writes the SVGs, `index.json` and PNG previews in `diagrams/_preview/`, which git ignores):

```bash
python 10-graphics/diagrams/_src/build_diagrams.py            # add --no-render to skip the PNGs
```

Slide decks (one PPTX per section from the `[SLIDE n: title]` cues; rerun after any script edit):

```bash
python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content
python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content --section 06   # one section
```

What the builder does: a K2 title card per lecture (title + "One idea" or first learning objective), one slide per cue (bullets max 5 per slide, longer lists continue; markdown and `Table: a | b` tables become real PPTX tables with a Teal header; fenced code in JetBrains Mono, max 15 lines; backticked identifiers in mono), K6 cards from `[SLIDE n: Recap]` cues, a "You can now" card, and a K7 next-up card from the transition. Speaker notes hold the narration that follows each cue (other visual cues are kept so the editor sees the cut). Every slide carries a lecture-ID footer. A cue whose title or "Diagram:" text matches a diagram in `diagrams/index.json` (keywords + the lectures listed below, or an explicit `D3` / `D3 build 2`) embeds the rendered PNG, picking the matching build step; any other "Diagram:" description is drawn as an amber dashed box labelled DIAGRAM TO BUILD. Decks are committed so they open without tooling; regenerate rather than hand-edit them.

Editing a diagram: change `diagrams/_src/build_diagrams.py` (layout is hand-placed; styling comes from `voice-ai-agents-course/09-production/tools/diagram_kit.py`, which follows `10-graphics/design-system.md`), rebuild, and look at the PNG in `_preview/` before committing. Master files show every build group (`<g id="build-n">`); `D{n}-step{k}.svg` files show what is visible at build k.
