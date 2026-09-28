# Welcome, Congratulations and Announcement Messages

> Udemy course messages are plain text (no formatting) and have a character limit that has historically been about 1,000 characters (verify in *Communications → Messages*). Both messages below are kept under 1,000 characters, with counts from Python `len()` on the exact text. **Udemy doesn't allow links, coupons or promotional content in welcome and congratulations messages (verify current rules).** Asking for an honest review is fine. Offering anything in return for a review is not.

---

## Welcome message (987 characters)

```text
Welcome to AI Agent Observability & Cost Control! You'll instrument Atlas, an IT and HR helpdesk agent, with OpenTelemetry and Langfuse, price every request, hold its latency, judge it on live traffic and solve incidents from traces.

To get the most out of the course:
1. Watch 1.1, then get your first trace on screen in 2.3.
2. Take Section 2 slowly. Lab 1 checks your keys, uv install and Langfuse project, which is where most problems come from.
3. Code along. The repo has every lecture's code, but you learn by running it.
4. Worried about cost? Lecture 2.1 sets a hard OpenAI cap, and OFFLINE=1 replays a full day of traffic for free. Expect about $5-15 in total (prices change; check each provider).
5. Keep a BUILD_LOG.md in your repo and post one line per section in Q&A.
6. Ask technical questions in Q&A with the lecture number and the full error, with keys removed.

The stack moves fast. The repo README and a pinned Q&A thread track version pins.

See you in Lecture 1.1!
```

## Congratulations message (913 characters)

```text
Congratulations on finishing AI Agent Observability & Cost Control!

You can now trace an agent step by step, attribute cost to every session and tenant, hold a latency budget under a provider outage, judge quality on live traffic, set SLOs and alerts, and find root cause from traces alone. Most teams running agents in production can't do all of that yet.

What to do next:
1. Finish and publish your capstone: the repo, dashboard screenshots, the weekly ops report and your postmortems make a strong portfolio piece.
2. Point the same stack at your own agent using the instrumentation template, and keep the CI budget gate.
3. If the course helped, please leave an honest review. It tells other engineers whether the course fits them and shows me what to improve.

The final bonus lecture covers where to go next in the Build, Test, Deploy, Operate series.

Thank you for learning with me, and happy operating!
```

---

## Announcements

> **Udemy announcement rules (as understood; verify in the Teaching Center before sending):** there are two kinds.
> - **Educational announcements** add value for enrolled students (updates, tips, new lectures). They are capped per month (historically around 4) and **can't contain promotional content**.
> - **Promotional announcements** may promote other courses with coupons. They are capped more tightly (historically around 2 per month) and have their own formatting and coupon rules.
> The three drafts below are all **educational**, so they don't use up the promotional quota and can't be mistaken for promotion. Promotional cross-sell announcements are planned separately in `08-marketing/cross-sell-plan.md`. Announcement length limits are not published in one place; these drafts are kept under ~850 characters so they fit comfortably (verify the field's limit when you paste).

### Launch announcement (Educational)

- **Type:** Educational
- **Send:** Day 1-3 after publish, to students enrolled so far
- **Length:** 767 characters

```text
Subject: Start here: your first trace in 10 minutes

Hi everyone, and welcome!

The fastest way to get going is:
- Lecture 1.1: watch an agent burn money in real time, then watch the fixed run
- Section 2 plus Lab 1: keys, spending cap, uv sync, make test green
- Lecture 2.3: one request, one trace. Open it in Langfuse and read the agent, retriever, generation and tool spans
- Lecture 2.4: OFFLINE=1 make replay gives you a full day of traffic for free

If you get stuck in setup, check the pinned Q&A post "Setup checklist and common errors" first. If that doesn't help, post in Q&A with your OS, your Python version and the full error (keys removed).

Quick tip: run make test before anything else. The unit tests need no API keys and no network.

Happy tracing!
```

### First update announcement (Educational)

- **Type:** Educational
- **Send:** When the first content update ships (e.g., a langfuse or semconv version bump, or a new lecture)
- **Length:** 813 characters (with placeholders; re-count after filling them in)

```text
Subject: Course update: [what changed] ([langfuse / opentelemetry version])

Hi everyone,

I've updated the course to keep it in line with the latest releases:

- [Change 1, e.g., "Updated Lecture 3.3 for renamed gen_ai.* attributes in semconv 0.6x"]
- [Change 2, e.g., "Repo: pinned versions bumped; all unit, integration and budget-gate tests pass"]
- [Change 3, e.g., "New Q&A-driven lecture: fixing the OTel Collector on Apple Silicon"]

If you cloned the repo before [date], run git pull and then uv sync (or make install).

The repo README keeps a CHANGELOG, so you can always see which lectures a change affects. The GenAI semantic conventions are still incubating, so attribute renames are the most likely kind of update.

Thanks for the questions in Q&A. Several of these updates came straight from them.
```

### 30-day check-in (Educational)

- **Type:** Educational
- **Send:** About 30 days after launch
- **Length:** 793 characters

```text
Subject: The section most teams skip: incidents

Hi everyone,

A month in, most of you have Atlas traced and costed. Before you trust your own agent in production, please do Section 11 (Incident Labs), even if you skip other parts. Reading a trace under pressure is a different skill from building one.

Three things to try this week:
1. Open incidents/incident-01-cost-spike, read the brief and write down your hypothesis before you watch the reveal (Lecture 11.2).
2. Run the weekly drift report against your replayed traffic and check which tenant moved most (Lecture 8.5).
3. Fill in the runbook template for one alert you actually have (Lecture 9.5).

Share your hypothesis for Incident 1 in the pinned "Incident labs" thread, marked as a spoiler. I'll answer every post.

Keep operating!
```

### Announcement calendar (first 90 days)

| Month | Educational (limit ~4, verify) | Promotional (limit ~2, verify) |
|---|---|---|
| 1 | Launch (start here); Week-2 tip: "read a trace waterfall in 5 minutes" (lecture 5.1 recap) | None. Let students settle in |
| 2 | 30-day check-in (Section 11); first update, if one ships | Optional: Course 2 (*AI Agent Testing & Evaluation*) offer to students who finished Section 8 (online evals → offline evals) |
| 3 | Update or Q&A digest (most-asked questions and answers) | Optional: Course 3 (*Production Voice AI Agents*) offer framed around the domain-swap project (14.6) |

## Verification output

```text
welcome:  987/1000 OK
congrats: 913/1000 OK
Launch announcement (Educational): 767 chars
First update announcement (Educational): 813 chars
30-day check-in (Educational): 793 chars
```

Re-check with `python3 -c "print(len(open('welcome.txt').read()))"` after pasting the exact text into a file.
