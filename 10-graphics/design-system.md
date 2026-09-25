# Visual Design System

## AI Agent Testing & Evaluation — Udemy Course

> Single source of truth for all visual assets, slide templates, and production standards.
> Every lecture, thumbnail, and marketing graphic must conform to this system.

---

## 1. Color Palette

| Color Name     | Hex       | RGB              | Usage                                      |
| -------------- | --------- | ---------------- | ------------------------------------------ |
| Deep Navy      | `#0A1628` | `10, 22, 40`     | Backgrounds, slide canvas, code editor bg  |
| Electric Teal  | `#00D4AA` | `0, 212, 170`    | Primary accent, pass/success, CTA buttons  |
| Alert Red      | `#FF4B4B` | `255, 75, 75`    | Fail/error states, security threats, flags |
| Warm Amber     | `#FFB020` | `255, 176, 32`   | Warning/caution, thresholds, partial pass  |
| Cool Gray      | `#94A3B8` | `148, 163, 184`  | Secondary text, labels, muted elements     |
| White          | `#FFFFFF` | `255, 255, 255`  | Primary text on dark backgrounds           |

### Extended Palette (Derived)

| Color Name        | Hex       | Usage                                |
| ----------------- | --------- | ------------------------------------ |
| Navy Light        | `#1A2742` | Card surfaces, elevated panels       |
| Navy Mid          | `#0F1E35` | Secondary background, sidebar        |
| Teal Dim          | `#00A885` | Hover/active state for teal          |
| Teal Glow         | `#00D4AA33` | Glow effects, soft highlights (20% opacity) |
| Red Dim           | `#CC3C3C` | Hover/active state for red           |
| Amber Dim         | `#CC8D1A` | Hover/active state for amber         |
| Gray Dark         | `#64748B` | Disabled text, borders               |
| Gray Light        | `#CBD5E1` | Subheadings, secondary labels        |

### Color Rules

- **Never** use pure black (`#000000`) — always use Deep Navy (`#0A1628`).
- **Never** place teal text on white background — it fails WCAG contrast.
- Alert Red is **only** for failures, errors, and security threats — never decorative.
- Warm Amber is **only** for warnings and caution states — never decorative.
- All text on Dark Navy must meet WCAG AA contrast ratio (4.5:1 minimum).

---

## 2. Typography

### Font Stack

| Role       | Font             | Weight    | Size Range     | Usage                              |
| ---------- | ---------------- | --------- | -------------- | ---------------------------------- |
| Headings   | Inter            | Bold (700)| 32–48px        | Slide titles, section headers      |
| Subheads   | Inter            | SemiBold (600) | 24–32px   | Subtitles, category labels         |
| Body       | Inter            | Regular (400) | 18–24px    | Explanatory text, bullets          |
| Code       | JetBrains Mono   | Regular (400) | 16–20px    | All code snippets, terminal output |
| Callout    | Inter            | Medium (500) | 20–28px     | Key takeaways, highlighted stats   |

### Typography Rules

- **Maximum 12 words per slide** — if you need more, split into two slides.
- Slide titles: 5–8 words maximum.
- Bullet points: 3–5 per slide, each under 10 words.
- Code blocks: maximum 15 lines visible at once; highlight the key 3–5 lines.
- Never use more than 2 font sizes on a single slide.
- Line height: 1.5x for body text, 1.2x for headings.
- Letter spacing: 0 for body, +0.5px for all-caps labels.

---

## 3. Diagram Style Guide

### General Principles

- **Dark background** (`#0A1628`) with neon accent lines.
- **Node-and-edge** style for all architecture diagrams.
- Rounded rectangles for nodes (8px border radius).
- 2px stroke width for connections; 3px for highlighted/active paths.
- Animated arrows for flow direction (in video); static arrows with chevrons for stills.
- Drop shadow: none. Use subtle glow (`#00D4AA33`) for emphasis.

### Color Coding

| State/Type      | Color           | Usage                                  |
| --------------- | --------------- | -------------------------------------- |
| Pass / Success  | Electric Teal   | Passing tests, healthy metrics         |
| Fail / Error    | Alert Red       | Failed tests, broken pipelines         |
| Warning         | Warm Amber      | Threshold breaches, degraded quality   |
| Primary / Active| Electric Teal   | Active flow paths, current step        |
| Inactive        | Cool Gray       | Dormant paths, disabled components     |
| Data Flow       | White (60%)     | Data movement arrows                   |

### Standard Iconography

Every diagram must use consistent icons for the following components:

| Component        | Icon Style           | Color        | Description                          |
| ---------------- | -------------------- | ------------ | ------------------------------------ |
| Agent            | Robot head (rounded) | Teal         | The AI agent under test              |
| Tool             | Wrench / gear        | White        | External tools the agent calls       |
| LLM              | Brain / neural net   | Teal         | Language model (GPT, Claude, etc.)   |
| Database         | Cylinder             | Cool Gray    | Vector stores, knowledge bases       |
| User             | Person silhouette    | White        | End user / human-in-the-loop        |
| Evaluator        | Clipboard + check    | Teal         | Evaluation framework (DeepEval etc.) |
| Security Shield  | Shield icon          | Alert Red    | Security testing, red teaming        |
| Trace            | Timeline / waterfall | Warm Amber   | Observability spans, Langfuse traces |
| CI/CD Pipeline   | Infinity loop        | Electric Teal| GitHub Actions, automation           |
| Metric           | Bar chart            | Teal/Red     | Quality scores, thresholds           |

### Diagram Templates

1. **Agent Loop** — User → Agent → LLM → Tool → Response → User (circular flow)
2. **Eval Pipeline** — Input → Agent → Output → Evaluator → Score → Report
3. **CI/CD Flow** — Git Push → GitHub Actions → Test Suite → Eval Gate → Deploy/Block
4. **RAG Pipeline** — Query → Retriever → Context → LLM → Answer → Eval
5. **Red Team Flow** — Attack Prompts → Agent → Response → Security Evaluator → Report
6. **Observability Stack** — Agent → Langfuse/OTEL → Traces → Dashboard → Alerts
7. **Quality Platform** — All components integrated into single architecture

---

## 4. Visual Content Types

### 4.1 Architecture Diagrams

- **Usage:** Explain system structure, component relationships, data flow.
- **Style:** Node-and-edge on dark background, color-coded by component type.
- **Animation:** Arrows animate sequentially to show flow direction (in video).
- **Examples:** Agent evaluation loop, RAG pipeline, CI/CD integration, quality platform architecture.
- **Tool:** Excalidraw (dark theme) or Figma.

### 4.2 Code Highlights

- **Usage:** Show Python code with syntax highlighting on dark background.
- **Style:** JetBrains Mono font, VS Code Dark+ color scheme adapted to our palette.
- **Key lines:** Highlighted with a teal left-border glow or background stripe (`#00D4AA15`).
- **Max visible lines:** 15 per screen. Use `# ...` to collapse irrelevant sections.
- **File labels:** Top-left corner shows filename in Cool Gray (`tests/test_agent.py`).
- **Syntax colors:** Strings in teal, keywords in white bold, comments in Cool Gray, functions in amber.

### 4.3 Terminal Recordings

- **Usage:** Show real tool output — pytest, deepeval, promptfoo, ragas.
- **Style:** Dark terminal theme matching Deep Navy. Prompt in teal. Output in white.
- **Tool:** asciinema or OBS with terminal zoom.
- **Annotations:** Overlay arrows/boxes highlighting key output lines (pass/fail counts, scores).
- **Speed:** Real-time for short commands; 2x for installations/long output.

### 4.4 Trace Visualizations

- **Usage:** Demonstrate Langfuse span waterfalls, trace timelines.
- **Style:** Screenshot of Langfuse UI with annotation overlays.
- **Annotations:** Teal boxes around key spans, amber callouts for latency, red for errors.
- **Context:** Always show the full trace first, then zoom into the relevant span.

### 4.5 Dashboard Screenshots

- **Usage:** Show Streamlit quality dashboard, monitoring panels.
- **Style:** Dashboard styled to match our color palette (dark theme Streamlit).
- **Annotations:** Callout boxes explaining each metric panel.
- **Progression:** Show dashboard evolving as we add metrics throughout the course.

### 4.6 Before/After Comparisons

- **Usage:** Show agent output improvements after applying evaluation and fixes.
- **Style:** Split-screen — left (before) has red accent/border, right (after) has teal accent/border.
- **Labels:** "BEFORE" in Alert Red, "AFTER" in Electric Teal, both in Inter Bold.
- **Content:** Actual agent outputs with key differences highlighted.

### 4.7 Failure Demos

- **Usage:** Intentionally demonstrate incorrect agent behavior, hallucinations, security failures.
- **Style:** Red-tinted overlay or red border around the failing output.
- **Annotations:** Red callout boxes pointing to the specific failure.
- **Purpose:** Make failures visceral and memorable — students should *feel* why testing matters.

### 4.8 Metric Visualizations

- **Usage:** Show quality scores, threshold comparisons, trend lines.
- **Style:** Bar charts with teal bars (pass), red bars (fail), amber threshold line.
- **Background:** Dark Navy. Grid lines in Cool Gray at 20% opacity.
- **Labels:** White text, Inter Regular. Axis labels in Cool Gray.
- **Tool:** Matplotlib with custom dark theme or Streamlit charts.

---

## 5. Scene Kits — 7 Visual Templates

Every lecture follows a consistent visual rhythm using these 7 scene templates.

### K1: Hook Scene

> **Purpose:** Grab attention in the first 15 seconds with a compelling problem visual.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Alert Red (`#FF4B4B`)                          |
| Content         | Problem statement visual — failure screenshot, error log, or shocking stat |
| Text            | 1 bold sentence (max 8 words) in White         |
| Subtext         | Problem context in Cool Gray (max 12 words)    |
| Animation       | Fade in, slight zoom on problem element        |
| Duration        | 10–15 seconds                                  |
| Example         | Screenshot of hallucinated agent output with red highlight: "Your agent just made this up." |

### K2: Title Card

> **Purpose:** Establish what this lecture covers and what the student will achieve.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Electric Teal (`#00D4AA`)                      |
| Content         | Lecture title (Inter Bold, 40px) + learning outcome (Inter Regular, 24px) |
| Layout          | Title centered top-third, outcome below with teal left border |
| Section badge   | Top-right corner — section number and name in Cool Gray |
| Duration        | 5–8 seconds                                    |
| Example         | "Building Your First Evaluation Suite" / "You'll write 5 test cases using DeepEval and pytest" |

### K3: Teaching Slide

> **Purpose:** Deliver a single concept with a supporting diagram or visual.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Electric Teal (`#00D4AA`)                      |
| Content         | **Max 12 words** of text + one diagram/visual  |
| Layout          | Text on left (40%), diagram on right (60%) — OR full-width diagram with text overlay |
| Bullets         | Max 3–5 per slide, revealed progressively      |
| Duration        | 15–30 seconds per slide                        |
| Rule            | One concept per slide. If you need more words, you need another slide. |

### K4: Architecture Diagram

> **Purpose:** Show system structure, component relationships, and data flow.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Multi-color (per diagram color coding)         |
| Content         | Full-width architecture diagram                |
| Layout          | Diagram centered with 5% padding on all sides  |
| Animation       | Components appear sequentially, arrows animate flow direction |
| Labels          | Component names in White, descriptions in Cool Gray |
| Duration        | 30–60 seconds (walk through each component)    |
| Callouts        | Numbered circles (teal) linking to narrator explanation |

### K5: Code/Demo Screen

> **Purpose:** Show live code, terminal output, or tool UI during hands-on segments.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | IDE/terminal dark theme (close to Deep Navy)    |
| Accent          | Teal line highlights for key code              |
| Content         | Python code or terminal output                 |
| Font            | JetBrains Mono, 18–20px                        |
| Layout          | Full-screen code editor or split (code + output) |
| Highlights      | Teal left-border glow on key lines             |
| File label      | Filename in top-left, Cool Gray                |
| Duration        | Variable — match narration pace                |
| Rule            | Max 15 visible lines. Collapse irrelevant code with `# ...` |

### K6: Recap Card

> **Purpose:** Summarize key takeaways at the end of each lecture.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Electric Teal (`#00D4AA`)                      |
| Content         | 3 bullet points summarizing key takeaways      |
| Layout          | Teal checkmark icon + bullet text, stacked vertically, centered |
| Text style      | Inter SemiBold, 24px, White                    |
| Animation       | Bullets appear one at a time (1 second apart)  |
| Duration        | 10–15 seconds                                  |
| Example         | "✓ DeepEval integrates directly with pytest" / "✓ Threshold-based assertions catch regressions" / "✓ Golden datasets make tests reproducible" |

### K7: Bridge / Next-Up Card

> **Purpose:** Tease the next lecture and maintain momentum.

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Background      | Deep Navy (`#0A1628`)                          |
| Accent          | Electric Teal (`#00D4AA`)                      |
| Content         | "Next up:" label (Cool Gray) + next lecture title (White, Inter Bold) + one-line teaser (Cool Gray) |
| Layout          | Right-arrow icon (teal) + text, centered       |
| Duration        | 5–8 seconds                                    |
| CTA             | "See you in the next lecture." (voiceover)      |
| Example         | "Next up: Red Teaming Your Agent" / "We'll try to break your agent with prompt injection attacks." |

---

## 6. Production Rules

### Visual Pacing

| Rule                                              | Requirement                    |
| ------------------------------------------------- | ------------------------------ |
| Max time without visual change                    | 60 seconds (hard limit)        |
| Target visual change interval                     | Every 15–30 seconds            |
| Avatar continuous talking without visual support   | Never more than 60 seconds     |
| Minimum visuals per 10-minute lecture              | 15–20 visual changes           |

### Consistency Standards

| Element          | Standard                                        |
| ---------------- | ----------------------------------------------- |
| Avatar           | Same AI avatar across ALL lectures              |
| Voice            | Same voice profile across ALL lectures          |
| Colors           | Strictly this palette — no exceptions            |
| Fonts            | Inter + JetBrains Mono only — no exceptions      |
| Slide template   | Scene Kits K1–K7 only — no freestyle slides      |
| Code theme       | Dark theme matching Deep Navy — consistent across all demos |

### Audio Standards

| Property          | Value                        |
| ----------------- | ---------------------------- |
| Loudness target   | -16 LUFS (integrated)        |
| True peak         | -1 dBTP maximum              |
| Noise floor       | Below -60 dB                 |
| Format            | AAC 256kbps or WAV           |
| Sample rate       | 48 kHz                       |

### Video Standards

| Property          | Value                        |
| ----------------- | ---------------------------- |
| Resolution        | 1920 × 1080 (16:9)          |
| Frame rate        | 30 fps minimum               |
| Codec             | H.264 (Main Profile)        |
| Bitrate           | 8–12 Mbps (variable)        |
| Export format     | MP4                          |
| Color space       | sRGB                         |

### Content Rules

- **No captions/subtitles as primary visual** — visuals must stand on their own.
- **No stock photos** — every visual is purpose-built for this course.
- **No walls of text** — 12-word maximum per slide (code screens excepted).
- **Every diagram must have a title** — students should understand it at a glance.
- **Code always has context** — show filename, highlight key lines, explain purpose.
- **Failures are always red, successes are always teal** — no exceptions.

---

## 7. Asset Naming Convention

```
{section}-{lecture}-{type}-{descriptor}.{ext}

Types: arch, code, term, trace, dash, comp, fail, metric, hook, title, recap, bridge

Examples:
  S03-L02-arch-eval-pipeline.png
  S05-L04-code-deepeval-test.png
  S07-L01-term-pytest-output.png
  S09-L03-trace-langfuse-waterfall.png
  S11-L02-dash-quality-dashboard.png
  S04-L05-comp-before-after-hallucination.png
  S06-L01-fail-prompt-injection.png
  S08-L03-metric-rag-scores.png
```

---

## 8. Quality Checklist — Per Visual

Before any visual is used in a lecture, verify:

- [ ] Background is Deep Navy (`#0A1628`) — not black, not gray
- [ ] Text uses only Inter or JetBrains Mono
- [ ] Maximum 12 words on teaching slides
- [ ] Color coding follows the standard (teal=pass, red=fail, amber=warning)
- [ ] Icons match the standard iconography table
- [ ] Diagram has a title
- [ ] Code shows filename and highlights key lines
- [ ] Visual fits 1920×1080 without cropping
- [ ] Asset follows naming convention
- [ ] No orphaned visuals (every visual is referenced in the lecture script)

---

*Document version: 1.0*
*Last updated: 2025*
*Owner: Course Production Team*
