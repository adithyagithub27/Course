# Course 3 graphics: Production Voice AI Agents

Master diagrams and generated slide decks (fix-plan decision A7). Specs: `../09-production/slide-deck-outline.md` (Master diagram list D1-D16). Canvas 1920x1080, Deep Navy, Inter / JetBrains Mono, palette and scene kits from `../../10-graphics/design-system.md`.

## Diagrams (`diagrams/`)

| ID | File | Diagram | Used in | Build steps (`D{n}-step{k}.svg`) |
|---|---|---|---|---|
| D1 | `D1-voice-pipeline.svg` | The voice pipeline | 1.2, 3.1, 13.1 | 1 the components; 2 where each fails |
| D2 | `D2-cascaded-vs-s2s-vs-hybrid.svg` | Three architectures | 1.3, 6.1, 6.3, 6.4 | 1 cascaded; 2 speech-to-speech; 3 half-cascade; 4 trade-offs; 5 6.1 zoom: speech-to-speech with transcript side channel |
| D3 | `D3-latency-budget-waterfall.svg` | Where the time goes | 1.4, 9.8, 10.1, 13.5 | 1 the axis; 2 the stages; 3 the target; 4 slow turn (p95) |
| D4 | `D4-turn-taking-timeline.svg` | One turn, on a timeline | 3.6, 3.7, 4.4 | 1 caller speech and VAD; 2 turn detection and end-of-utterance delay; 3 Riley answers; 4 interruptions; 5 preemptive generation |
| D5 | `D5-livekit-mental-model.svg` | Rooms, participants, tracks, dispatch | 3.1, 12.1 | 1 SFU, room and participants; 2 tracks; 3 dispatch; 4 the job is the agent participant |
| D6 | `D6-sip-call-flow.svg` | The call path | 8.1, 8.2, 8.4, 8.5 | 1 inbound; 2 transfer; 3 outbound |
| D7 | `D7-handoff-graph.svg` | Riley's team | 7.4, 7.5, 7.6 | 1 the agents; 2 shared userdata; 3 Lab 5: InsuranceAgent |
| D8 | `D8-voice-testing-pyramid.svg` | The voice testing pyramid | 9.2, 13.4 | 1 unit tests; 2 behavior tests; 3 evals; 4 simulated calls; 5 production monitoring; 6 13.4 overlay: all layers pass |
| D9 | `D9-failure-test-map.svg` | Failure → test map | 9.1, 11.1 | 1 mishearing; 2 wrong turn-taking; 3 talking over callers; 4 hallucinated availability; 5 wrong tool arguments; 6 missed escalation; 7 latency spikes; 8 prompt injection |
| D10 | `D10-observability-dashboard.svg` | The five numbers | 10.5, 10.6, 13.5 | 1 p95 latency; 2 cost/min; 3 transfers; 4 contained; 5 tool failures; 6 alert |
| D11 | `D11-trace-anatomy.svg` | One call, as a trace | 10.3 | 1 session and turns; 2 one turn expanded; 3 slowest span |
| D12 | `D12-threat-model.svg` | Five threats, layered defences | 11.1 | 1 spoken injection; 2 social engineering; 3 exfiltration via tools; 4 toll fraud; 5 voice cloning; 6 defences |
| D13 | `D13-agent-server-scaling.svg` | The agent server | 12.1, 12.4 | 1 jobs and warm processes; 2 load threshold; 3 memory warning; 4 draining on deploy |
| D14 | `D14-capstone-architecture.svg` | Riley in production | 13.1, 13.2 | 1 callers; 2 agent server; 3 agents and tools; 4 telemetry; 5 CI |
| D15 | `D15-pipecat-frame-pipeline.svg` | Frames through a pipeline | 14.1, 14.2 | 1 processors; 2 frames; 3 containers |
| D16 | `D16-build-vs-buy-matrix.svg` | Build vs buy | 14.3 | 1 time to first call; 2 pipeline control; 3 cost at low volume; 4 cost at high volume; 5 compliance control; 6 lock-in; 7 testing depth |

Interpretations of the spec: D2's "Cost" row is labelled "Cost visibility" (●●● = per-stage cost transparency, from `10-resources/architecture-decision-matrix.md`); D2 step 5 is the 6.1 zoom (speech-to-speech row alone with the transcription side channel). D5 draws the three participants inside the Room as well as their devices outside it. D8's speed and cost badges are ordinal words ("fastest" ... "live", "$" ... "$$$"), not numbers. D11 timings are illustrative and to scale on a 15-second axis. D10 and D3 values are the spec's illustrative numbers, footnoted as such.

## Slide decks (`slides/section-NN.pptx`)

Generated from `../02-lecture-scripts/section-*.md`.

## Regenerate

Set up once (any venv):

```bash
pip install -r voice-ai-agents-course/09-production/tools/requirements.txt
# Playwright needs a Chromium; it uses PLAYWRIGHT_BROWSERS_PATH if set (no 'playwright install' needed there).
# Install the Inter and JetBrains Mono fonts locally so previews and PowerPoint render the real type.
```

Diagrams (writes the SVGs, `index.json` and PNG previews in `diagrams/_preview/`, which git ignores):

```bash
python voice-ai-agents-course/10-graphics/diagrams/_src/build_diagrams.py            # add --no-render to skip the PNGs
```

Slide decks (one PPTX per section from the `[SLIDE n: title]` cues; rerun after any script edit):

```bash
python voice-ai-agents-course/09-production/tools/slide_builder.py --course voice-ai-agents-course 
python voice-ai-agents-course/09-production/tools/slide_builder.py --course voice-ai-agents-course  --section 06   # one section
```

What the builder does: a K2 title card per lecture (title + "One idea" or first learning objective), one slide per cue (bullets max 5 per slide, longer lists continue; markdown and `Table: a | b` tables become real PPTX tables with a Teal header; fenced code in JetBrains Mono, max 15 lines; backticked identifiers in mono), K6 cards from `[SLIDE n: Recap]` cues, a "You can now" card, and a K7 next-up card from the transition. Speaker notes hold the narration that follows each cue (other visual cues are kept so the editor sees the cut). Every slide carries a lecture-ID footer. A cue whose title or "Diagram:" text matches a diagram in `diagrams/index.json` (keywords + the lectures listed below, or an explicit `D3` / `D3 build 2`) embeds the rendered PNG, picking the matching build step; any other "Diagram:" description is drawn as an amber dashed box labelled DIAGRAM TO BUILD. Decks are committed so they open without tooling; regenerate rather than hand-edit them.

Editing a diagram: change `diagrams/_src/build_diagrams.py` (layout is hand-placed; styling comes from `voice-ai-agents-course/09-production/tools/diagram_kit.py`, which follows `10-graphics/design-system.md`), rebuild, and look at the PNG in `_preview/` before committing. Master files show every build group (`<g id="build-n">`); `D{n}-step{k}.svg` files show what is visible at build k.
