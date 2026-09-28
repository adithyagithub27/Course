# Welcome, Congratulations and Announcement Messages

> Udemy course messages are plain text (no formatting) and have a character limit that has historically been about 1,000 characters (verify in *Communications → Messages*). Both messages below are kept under 1,000 characters, with counts from Python `len()` on the exact text. **Udemy doesn't allow links, coupons or promotional content in welcome and congratulations messages (verify current rules).** Asking for an honest review is fine. Offering anything in return for a review is not.

---

## Welcome message (927 characters)

```text
Welcome to Production Voice AI Agents with Python! You'll build Riley, an AI receptionist that answers a real phone number, books appointments and hands off to a human. Then you'll test it, monitor it and deploy it.

To get the most out of the course:
1. Watch 1.1, then talk to the finished Riley yourself in 2.6.
2. Take Section 2 slowly. Lab 1 checks your keys, mic and Python version, which is where most problems come from.
3. Code along. The repo has every lecture's code, but you learn by running it.
4. Worried about cost? Lecture 2.7 sets spending caps and a free offline mock mode. Expect about $10-20 in total (prices change; check each provider).
5. Keep a BUILD_LOG.md in your repo and post one line per section in Q&A.
6. Ask technical questions in Q&A with the lecture number and the full error.

Voice frameworks move fast. The repo README and a pinned Q&A thread track version updates.

See you in Lecture 1.1!
```

## Congratulations message (791 characters)

```text
Congratulations on finishing Production Voice AI Agents with Python!

You can now build a real-time voice agent, put it on a phone number, test it the way you'd test any other software, watch its latency and cost per minute, and deploy it. Most voice demos never get that far.

What to do next:
1. Finish and publish your capstone: the repo, a short demo call recording and your test report make a strong portfolio piece.
2. Swap in your own use case: change the prompts, tools and FAQ, and keep the test suite.
3. If the course helped, please leave an honest review. It tells other engineers whether the course fits them and shows me what to improve.

The final bonus lecture covers where to go next in the Build → Test → Operate series.

Thank you for learning with me, and happy shipping!
```

---

## Announcements

> **Udemy announcement rules (as understood; verify in the Teaching Center before sending):** there are two kinds.
> - **Educational announcements** add value for enrolled students (updates, tips, new lectures). They are capped per month (historically around 4) and **can't contain promotional content**.
> - **Promotional announcements** may promote other courses with coupons. They are capped more tightly (historically around 2 per month) and have their own formatting and coupon rules.
> The three drafts below are all **educational**, so they don't use up the promotional quota and can't be mistaken for promotion. Promotional cross-sell announcements are planned separately in `08-marketing/cross-sell-plan.md`.

### Launch announcement (Educational)

- **Type:** Educational
- **Send:** Day 1-3 after publish, to students enrolled so far
- **Length:** 769 characters

```text
Subject: Start here: your first voice agent in 30 minutes

Hi everyone, and welcome!

The fastest way to get going is:
- Lecture 1.1: hear three calls: one that works, one that fails, one that's fixed
- Lecture 2.6: talk to the finished Riley before you build it
- Section 2 plus Lab 1: set up your environment and keys
- Lecture 3.3: build "hello Riley" in about 30 lines and talk to it through your laptop mic

If you get stuck in setup, check the pinned Q&A post "Setup checklist and common errors" first. If that doesn't help, post in Q&A with your OS, your Python version and the full error.

Quick tip: run `make test` before anything else. The unit tests need no API keys, and MOCK_MODE=1 (Lecture 2.7) lets you practise without spending a cent.

Happy building!
```

### First update announcement (Educational)

- **Type:** Educational
- **Send:** When the first content update ships (e.g., a framework minor-version bump or a new lecture)
- **Length:** 705 characters

```text
Subject: Course update: [what changed] ([livekit-agents / pipecat-ai version])

Hi everyone,

I've updated the course to keep it in line with the latest framework releases:

- [Change 1, e.g., "Updated Lecture 3.6 for the new turn-handling options in livekit-agents 1.x"]
- [Change 2, e.g., "Repo: pinned versions bumped; all unit, agent and eval tests pass"]
- [Change 3, e.g., "New Q&A-driven lecture: fixing choppy audio on Windows"]

If you cloned the repo before [date], run `git pull` and then `uv sync` (or `make install`).

The repo README keeps a CHANGELOG, so you can always see which lectures a change affects.

Thanks for the questions in Q&A. Several of these updates came straight from them.
```

### 30-day check-in (Educational)

- **Type:** Educational
- **Send:** About 30 days after launch
- **Length:** 735 characters

```text
Subject: The one section most voice agents skip

Hi everyone,

A month in, most of you have Riley talking. Before you put an agent in front of real callers, please do Section 9 (Testing and Evaluating Voice Agents), even if you skip other parts.

Three things to try this week:
1. Write one behavior test that asserts Riley calls `book_appointment` with the right arguments (Lecture 9.4).
2. Run the latency report against your own calls and compare p95 to your budget (Lecture 9.8).
3. Run the "impatient caller" and "injection attacker" simulated personas (Lecture 9.9) and see what breaks.

Share your results (or your weirdest failure) in Q&A. I'll answer every post and fold the best examples into a future update.

Keep building!
```

### Announcement calendar (first 90 days)

| Month | Educational (limit ~4, verify) | Promotional (limit ~2, verify) |
|---|---|---|
| 1 | Launch (start here); Week-2 tip: "fixing turn-taking in 5 minutes" | None. Let students settle in |
| 2 | 30-day check-in (Section 9); first update, if one ships | Optional: Course 2 (*AI Agent Testing & Evaluation*) offer to students who finished Section 9 |
| 3 | Update or Q&A digest | Optional: Course 4 pre-launch, once it exists |

## Verification output

```text
welcome:  927/1000 OK
congrats: 791/1000 OK
Launch announcement (Educational): 769 chars
First update announcement (Educational): 705 chars
30-day check-in (Educational): 735 chars
```
