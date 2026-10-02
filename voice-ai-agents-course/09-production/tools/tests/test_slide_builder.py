"""Unit tests for the slide_builder.py script parser and diagram matcher (no rendering, no PPTX)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from slide_builder import Slide, match_diagram, parse_script  # noqa: E402

C3_STYLE = """# Section 1: Welcome and How Voice Agents Work

## Lecture 1.2 — What a voice agent actually is

| Field | Value |
|---|---|
| ID | 1.2 |
| Learning objectives | 1. Distinguish a voice agent from an IVR. 2. Name the components. |

### Script

[AVATAR]
Press one for appointments. [PAUSE] You've been trapped in that menu.

[SLIDE 1: IVR vs chatbot vs voice agent]
- IVR: fixed menu tree
- **Chatbot**: text in, text out
- Voice agent: speaks in real time

An IVR is a decision tree.

A chatbot understands language.

[SLIDE 2: The voice pipeline, seven components]
Diagram, left to right: Caller → Transport → VAD → STT → LLM → TTS.
Each box has a one-line label:
- Transport: moves audio
- VAD: is someone speaking?

Let's walk the pipeline.

[SCREEN: terminal]

Still narrating over the screen.

[SLIDE 3: Every box adds a failure mode]
Table: Component | Typical failure | Where we fix it
- Transport | packet loss | S8
- VAD | noise triggers | S3
Footer: "Example numbers for illustration."

Every box adds time.

[SLIDE 4: Recap]
- A voice agent is a pipeline
- Each stage fails its own way
- Test each box

**Recap:** A voice agent is a real-time pipeline.

**Transition:** Next, cascaded versus speech-to-speech.

## Lecture 1.3: Cascaded vs speech-to-speech

[SLIDE 1: The config]

```python
session = AgentSession(stt="deepgram/nova-3")
```

[AVATAR]

Here is the code.

[SLIDE 2: You can now]
- run Riley · tune turn-taking · hear what's wrong
"""

C4_STYLE = """# Section 6: Cost Engineering

## Lecture 6.1: Where the money goes

| Field | Value |
|---|---|
| One idea | An agent's bill is made of six token streams. |

[SLIDE 2: One request, step by step]

| Step | Input tokens | Output tokens |
|---|---|---|
| 1 | 3,259 | 42 |
| 2 | 6,667 | 282 |

[AVATAR]

Step one sends the system prompt.

[SLIDE 3: Order matters]
> Stable first, per-request last.

### Recap

Six token streams; input dominates.

### Transition

Next, the price table.
"""


def c3():
    return parse_script(C3_STYLE, "02-lecture-scripts/section-01-welcome.md")


def test_section_and_lectures():
    sec = c3()
    assert sec.number == 1
    assert sec.title == "Welcome and How Voice Agents Work"
    assert [l.id for l in sec.lectures] == ["1.2", "1.3"]
    assert sec.lectures[1].title == "Cascaded vs speech-to-speech"


def test_objective_recap_transition():
    lec = c3().lectures[0]
    assert lec.objective.startswith("Distinguish a voice agent from an IVR")
    assert lec.recap == "A voice agent is a real-time pipeline."
    assert lec.transition.startswith("Next, cascaded")


def test_bullets_strip_bold_and_notes_follow_cue():
    s1 = c3().lectures[0].slides[0]
    assert s1.number == "1" and s1.title == "IVR vs chatbot vs voice agent"
    assert s1.bullets == ["IVR: fixed menu tree", "Chatbot: text in, text out", "Voice agent: speaks in real time"]
    assert "An IVR is a decision tree." in s1.notes and "A chatbot understands language." in s1.notes
    assert "[PAUSE]" not in s1.notes
    assert s1.kind == "teaching"


def test_diagram_description_with_labels_and_screen_cue_in_notes():
    s2 = c3().lectures[0].slides[1]
    assert s2.kind == "diagram"
    assert s2.diagram.startswith("Diagram, left to right: Caller")
    assert "Each box has a one-line label" in s2.diagram
    assert s2.bullets == ["Transport: moves audio", "VAD: is someone speaking?"]
    # narration runs to the next SLIDE cue and keeps other visual cues for the editor
    assert "Let's walk the pipeline." in s2.notes
    assert "[SCREEN: terminal]" in s2.notes and "Still narrating" in s2.notes


def test_table_colon_style_and_footer():
    s3 = c3().lectures[0].slides[2]
    assert s3.kind == "table"
    assert s3.table[0] == ["Component", "Typical failure", "Where we fix it"]
    assert s3.table[1] == ["Transport", "packet loss", "S8"]
    assert len(s3.table) == 3
    assert s3.footer == "Example numbers for illustration."


def test_recap_and_you_can_now_kinds():
    sec = c3()
    recap = sec.lectures[0].slides[3]
    assert recap.kind == "recap" and len(recap.bullets) == 3
    ycn = sec.lectures[1].slides[1]
    assert ycn.kind == "youcannow"


def test_code_fence_under_slide():
    code = c3().lectures[1].slides[0]
    assert code.kind == "code"
    assert code.code_lang == "python"
    assert 'AgentSession(stt="deepgram/nova-3")' in code.code
    assert code.notes == "Here is the code."


def test_markdown_table_blockquote_and_section_style_recap():
    sec = parse_script(C4_STYLE, "x/section-06-cost-engineering.md")
    lec = sec.lectures[0]
    assert sec.number == 6
    assert lec.objective == "An agent's bill is made of six token streams."
    t = lec.slides[0]
    assert t.table == [["Step", "Input tokens", "Output tokens"], ["1", "3,259", "42"], ["2", "6,667", "282"]]
    assert t.notes == "Step one sends the system prompt."
    q = lec.slides[1]
    assert q.text == ["Stable first, per-request last."]
    assert lec.recap.startswith("Six token streams")
    assert lec.transition == "Next, the price table."


def test_code_blocks_in_narration_are_not_slide_cues():
    text = "## Lecture 2.1 — X\n\n```text\n[SLIDE 9: not a cue]\n```\n\n[SLIDE 1: Real]\n- a\n"
    sec = parse_script(text, "section-02.md")
    assert [s.title for s in sec.lectures[0].slides] == ["Real"]


def _index(tmp_path: Path) -> tuple[dict, Path]:
    idx = {"diagrams": {
        "D1": {"file": "D1-voice-pipeline.svg", "lectures": ["1.2"], "keywords": ["voice pipeline"],
               "steps": {"1": {"file": "D1-step1.svg", "keywords": ["seven components"]},
                         "2": {"file": "D1-step2.svg", "keywords": ["where each fails"]}}},
        "D3": {"file": "D3-latency-budget-waterfall.svg", "lectures": ["1.4"], "keywords": ["where the time goes"],
               "steps": {"4": {"file": "D3-step4.svg", "keywords": ["p95"]}}},
    }}
    (tmp_path / "index.json").write_text(json.dumps(idx))
    return idx, tmp_path


def test_match_by_keyword_and_step(tmp_path):
    idx, d = _index(tmp_path)
    s = Slide(number="2", title="The voice pipeline, seven components", lecture_id="1.2",
              diagram="Diagram, left to right: Caller → Transport")
    ref = match_diagram(s, idx, d)
    assert ref.id == "D1" and ref.step == 1 and ref.svg.name == "D1-step1.svg"


def test_match_explicit_id_with_build(tmp_path):
    idx, d = _index(tmp_path)
    s = Slide(number="1", title="Latency (D3 build 4)", lecture_id="9.8")
    ref = match_diagram(s, idx, d)
    assert ref.id == "D3" and ref.svg.name == "D3-step4.svg"


def test_no_match_for_plain_bullets_or_other_lectures(tmp_path):
    idx, d = _index(tmp_path)
    assert match_diagram(Slide(number="1", title="Rooms", lecture_id="3.1", bullets=["a"]), idx, d) is None
    # keyword in title but not a lecture that uses the diagram and no diagram description
    assert match_diagram(Slide(number="1", title="The voice pipeline", lecture_id="7.1"), idx, d) is None
    # deliverable list items named "D1 ..." are not diagram references
    s = Slide(number="5", title="Deliverables", lecture_id="13.1", bullets=["D1 Repository with README"])
    assert match_diagram(s, idx, d) is None
