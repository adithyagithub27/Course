# Demo 06 — Quality Dashboard

**Used in:** Lecture 12.3 (Experiment Tracking & Quality Dashboards)
**Duration:** ~2 minutes of screen recording
**Purpose:** Show the Streamlit quality dashboard with real evaluation results

## Setup

```bash
# Run the evaluation suite first to generate results
cd agent-eval-framework
pytest tests/ -v --junitxml=reports/results/all.xml
# Then launch the dashboard
streamlit run reports/quality_dashboard.py
```

## Recording Script

### Scene 1: Launch Dashboard (15s)
```bash
streamlit run reports/quality_dashboard.py
```
Browser opens → show the dashboard loading.

### Scene 2: Overview Metrics (30s)
Show three top-level metrics:
- Overall Quality Score: 84.2%
- Categories Evaluated: 5
- Gate Status: PASS

Narration: "One number tells the VP of Engineering whether this agent is ready for production. 84.2% across all categories. The gate is PASS."

### Scene 3: Category Breakdown (45s)
Expand each category:
- Functional: 9/10 passed (90%)
- LLM Quality: 5/6 passed (83%)
- RAG Quality: 4/4 passed (100%)
- Security: 7/8 passed (87.5%)
- Performance: latency P95 = 3.2s, cost avg = $0.003/task

Click into a failing test case → show the input, actual output, score, and reason.

### Scene 4: Decision Point (30s)
Narration: "The security category shows one failure — a delimiter injection attack succeeded. Score: 0.4 against a 0.9 threshold. The agent needs a guardrail fix before production."

Show: highlight the failing row in the table.

## Post-Production Notes
- Record at 1920x1080
- Use the course color scheme in Streamlit (dark theme if possible)
- Zoom into the failing test case for detail
- This demo shows the capstone-quality output students will build
