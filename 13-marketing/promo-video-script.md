# Promotional Video Script

**Duration:** 60–90 seconds
**Purpose:** Udemy course preview / landing page video
**Format:** HeyGen avatar + failure demo footage + architecture diagrams + code clips

---

## Script

```
[SCENE 1 — FAILURE HOOK] (0:00–0:12)
VISUAL: Screen recording of `demos/m00_agent_failure.py`: the agent answers "14-day money-back guarantee" with no tool call; "Faithfulness 0.00 -> FAIL: block this deploy" in red.
SCRIPT:
One line deleted from a prompt.
Now your AI agent invents your refund policy... and every unit test still passes.
So how would you have caught it?

[SCENE 2 — THE PROBLEM] (0:12–0:25)
VISUAL: Animated split — left side: "Traditional Test: assertEqual('Paris', response)" with a green check. Right side: agent producing different outputs each run.
SCRIPT:
Traditional testing doesn't work for AI agents.
They're non-deterministic. They use tools. They make decisions.
And when they fail... they fail in ways no unit test can catch.
Hallucinations. Wrong tool calls. Data leaks. Silent failures.

[SCENE 3 — THE SOLUTION] (0:25–0:40)
VISUAL: Course title card → quick montage of code, eval results, dashboards, traces.
SCRIPT:
This course teaches you to systematically test, evaluate, and monitor AI agents
the way enterprise teams actually do it.
You'll build real evaluation pipelines... not watch slides.

[SCENE 4 — WHAT YOU'LL BUILD] (0:40–0:60)
VISUAL: Quick cuts of real course output — DeepEval results table, RAGAS scores, promptfoo red-team table, SecureBank finding BRT-10, Langfuse trace, the failing PR comment, the Streamlit dashboard, the capstone "Decision: SHIP".
SCRIPT:
You'll use DeepEval to write AI tests that run like pytest.
You'll use RAGAS to evaluate your RAG pipeline.
You'll red-team agents with promptfoo, Garak and PyRIT.
You'll trace every agent step with Langfuse and OpenTelemetry.
And you'll wire it all into GitHub Actions... so a bad pull request gets blocked, not shipped.
Fifty-five lectures. Five projects. One quality platform you can use at work.
And every lab runs free, without an API key.

[SCENE 5 — CTA] (0:60–0:70)
VISUAL: Course title + "55 lectures · 6 h 40 min · 5 projects" + "Enroll Now" (add a star rating only once real reviews exist)
SCRIPT:
If you build AI agents... you need to know how to test them.
Enroll now. I'll see you in the first lecture.
```

---

## Production Notes

- **Total duration target:** 65–75 seconds
- **Tone:** Urgent, confident, practical — not salesy
- **Music:** Subtle electronic underscore, rises at CTA
- **Visuals change every 5–8 seconds** — no static frames
- **No greeting** — opens immediately on the failure
- **Avatar appears in scenes 2, 3, and 5** — scenes 1 and 4 are mostly screen footage with voiceover
