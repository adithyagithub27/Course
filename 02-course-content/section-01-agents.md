# Section 1: AI Agents: What You Need to Know for Testing

> **Course:** AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python (Course 2)
> **Section runtime:** ≈28 min (4 lectures, plus Lab 1.1)
> **Source of truth:** `01-curriculum/full-curriculum.md` (Module 01) for objectives; `14-quality-review/course2-bible.md` for agents, data, versions, commands and outputs. If a script and the code disagree, the code wins.
> **On-screen footer for every code or API slide:** "Verified: openai 2.54.0 | deepeval 4.2.7 | tiktoken 0.14.0 (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1."
> **Cue legend:** see `section-00-welcome.md`. Commands run from `04-code-examples/agent-eval-framework/`. Outputs are offline runs (`OFFLINE=1`) unless a note says otherwise. Word counts are spoken words only, counted by the section checker.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 1.1 | LLMs in 10 Minutes: Tokens, Context, Temperature | SL | 8:00 | 1002 |
| 1.2 | What Makes an Agent an Agent (Not a Chatbot) | DM | 7:00 | 891 |
| 1.3 | Agent Architecture: The Loop, Tools, Memory, Planning | SL | 7:00 | 903 |
| 1.4 | The 6 Ways AI Agents Fail (And Why Testing Is Hard) | DM | 6:00 | 734 |

**Section guardrails (do not deviate on screen):** one agent, TechCorp support (`agents/support_agent.py`), a SaaS company with plans, invoices and a knowledge base (KB-101 to KB-105). No orders, no inventory, no `lookup_order`, no TechGear, no LangChain agent code. The six failure modes are exactly: hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops. Prices on screen carry "verify current pricing".

---

## Lecture 1.1 — LLMs in 10 Minutes: Tokens, Context, Temperature

| Field | Value |
|---|---|
| ID | 1.1 |
| Title | LLMs in 10 Minutes: Tokens, Context, Temperature |
| Type | SL (slides with two short terminal demos) |
| Target duration | 8:00 (1,120 words at 140 wpm; 1,002 spoken) |
| Learning objectives | 1. Explain tokens and estimate what a test run costs from token counts. 2. Describe what fills a context window on an agent's first call and why long contexts change behaviour. 3. Explain how temperature makes the same question produce different, equally correct answers, and what that does to exact-match tests. |
| Prerequisites | Section 0 complete (`make install`) |
| Files used | `demos/m01_token_demo.py`; `demos/m01_temperature_demo.py`; `performance/tokens.py`; `config/settings.py` (`PRICES_PER_1M`); `agents/support_agent.py` (`SYSTEM_PROMPT`, `TOOLS`) |

### Script

[AVATAR]
This test just failed. The agent said, "Expect your refund within five to seven business days." The test expected, "Refunds are processed within five to seven business days." Same fact. Both correct. The test is red anyway. [PAUSE] Whose fault is that? Not the agent's. Three ideas about how language models work would have saved that test. Let's cover them.

[SLIDE 1: LLMs in 10 Minutes: Tokens, Context, Temperature]
- Tokens: what you pay for and what gets cut
- Context: everything the model sees at once
- Temperature: why the same question varies

By the end of this lecture, you'll be able to explain how tokens, context windows and temperature shape every test you write for an agent.

[SLIDE 2: Your testing cheat sheet]
- Not how transformers work
- Three ideas that change how you test
- Used in every module from 3 onward

This isn't a machine learning course. You don't need attention mechanisms or training math. You need three ideas, because every evaluation technique from Module 3 onward leans on them. Think of this as your tester's cheat sheet for language models.

[SLIDE 3: Tokens: the units a model reads]
Diagram: The customer query "Hi, I was charged twice for my Pro plan this month. Can you refund one charge?" splits into coloured blocks, one per token. A counter under it reads "78 characters → 19 tokens". A small note: "rule of thumb: 100 tokens ≈ 75 English words".

Language models don't read words. They read tokens. A token is a chunk of text: often a whole word, sometimes part of one, sometimes punctuation. A handy rule of thumb: a hundred tokens is roughly seventy-five English words.

Why should a tester care? Two reasons. Cost, and truncation. Every token in and out is billed. And when you cap a response with a maximum token count, you're cutting tokens, not words. A capped answer can stop mid-sentence, and your test has to notice.

[SCREEN: Terminal. Run the token demo; the version banner shows `openai 2.54.0 | tiktoken 0.14.0`.]

```bash
uv run python demos/m01_token_demo.py
```

[DEMO: Output (banner trimmed)]
```text
Tokenizer: approximate (len/4; tiktoken encoding unavailable)

Customer query (78 characters) -> 19 tokens
Hi | , | I | was | charged | twice | for | my | Pro | plan | this | month | . | Can | you | refund | one | charge | ?

What the model actually receives on the first call:
  system prompt     255 tokens
  tool schemas      481 tokens
  customer query     19 tokens
  total input       755 tokens
  gpt-4.1-mini  one call ~ $0.000398; 1M calls ~ $398  (verify current pricing)
  gpt-4.1       one call ~ $0.001990; 1M calls ~ $1,990  (verify current pricing)

Context window 1,000,000 tokens: roughly 12,648 turns of this size before it is full.
```

Here's a real customer message for our TechCorp agent. Nineteen tokens. But look at what the model actually receives on the first call. The system prompt is two hundred fifty-five tokens. The five tool definitions are four hundred eighty-one. The customer's words are the smallest part: nineteen out of seven hundred fifty-five.

That surprises most testers. The fixed overhead, the prompt and the tool schemas, is paid again on every single call. And an agent makes several calls per question. So when someone adds a sixth tool or a longer rule to the prompt, every test case gets more expensive, and every conversation fills its context a little faster.

[SLIDE 4: Tokens are your test budget]
- 755 input tokens before the agent does anything
- `gpt-4.1-mini`: about $0.0004 per call (verify pricing)
- Judge calls on `gpt-4.1` cost about 5x more
- 500 cases × 2,000 tokens = 1M tokens per run

So what does that cost? On `gpt-4.1-mini`, about four hundredths of a cent per call. Tiny. Now scale it. A suite of five hundred test cases at two thousand tokens each is a million tokens per run. Your judge model, `gpt-4.1`, is about five times the price of the agent model. Run that suite ten times a day and you can see the bill. Tokens are your testing budget, and that's why this course runs offline by default.

[SLIDE 5: Context window: the model's desk]
Diagram: A horizontal bar labelled "context window". Segments from left: system prompt (255), tool schemas (481), conversation history (grows every turn), retrieved knowledge-base text (varies), customer query (19), and "space for the answer" at the right. A red arrow at the right edge: "overflow: something gets dropped".

The context window is everything the model can see at once. Think of it as a desk. The system prompt, the tool definitions, the conversation so far, any documents the agent retrieved, the new question, and room for the answer: all of it has to fit on the desk.

The `gpt-4.1` family has a window of about one million tokens. Our demo says that's over twelve thousand turns of this size. Sounds endless, right?

It isn't, for two reasons. Real turns carry more than a short question: every tool result the agent reads lands on the desk too, and a single knowledge-base article can be longer than the whole customer message. And the window is a hard limit only at the very edge. Long before it's full, quality can slip.

[SLIDE 6: Big windows still fail]
- History grows with every turn
- Retrieval can add thousands of tokens per call
- Details in the middle get less attention
- Test short and long conversations, both

Here's the catch. Size isn't the problem; attention is. Research on long contexts found that models use information at the start and end of the context better than information buried in the middle. It's often called "lost in the middle" (verify: Liu et al., 2023). For you, that means an agent can answer perfectly in a three-turn test and forget the customer's account ID by turn thirty. Your test suite needs both lengths.

[SLIDE 7: Temperature: the variation dial]
Diagram: A slider from 0.0 to 2.0. At 0.0: one answer repeated ("same wording every run"). At 1.0: several different sentences fanning out ("same facts, different words"). At 2.0, greyed out: "rarely used: often incoherent".

Third idea: temperature. Every time a model picks the next token, it chooses from a list of likely options. Temperature controls how adventurous that choice is. At zero, it nearly always takes the most likely token, so the wording barely changes. At one, it samples more widely. Same facts, different words. Push it toward two, and answers get strange.

Which setting would you rather test against? Here's an analogy. Ask ten people to finish "the capital of France is", and they all say Paris. That's temperature zero. Ask them to "name a city in France", and you get Paris, Lyon, Nice. All correct, all different. That's temperature one.

[SCREEN: Terminal. Run the temperature demo. Highlight the five identical lines, then the three different phrasings.]

```bash
uv run python demos/m01_temperature_demo.py
```

[DEMO: Output (banner trimmed)]
```text
temperature=0.0: 1 distinct answer(s) out of 5
  1. Refunds are processed within 5-7 business days.
  2. Refunds are processed within 5-7 business days.
  3. Refunds are processed within 5-7 business days.
  4. Refunds are processed within 5-7 business days.
  5. Refunds are processed within 5-7 business days.

temperature=1.0: 3 distinct answer(s) out of 5
  1. It takes 5-7 business days for a refund to be processed.
  2. Expect your refund within 5-7 business days.
  3. Once approved, a refund takes 5-7 business days to process.
  4. Expect your refund within 5-7 business days.
  5. Expect your refund within 5-7 business days.

Same facts, different words: an exact-match assertion would fail on the 1.0 runs.
```

Same question, "How long do refunds take?", five times at each setting. At zero: one distinct answer out of five. At one: three distinct answers out of five. Every one says five to seven business days. Every one is correct. And an exact-match assertion fails on every run that isn't word-for-word the expected sentence. That's the test from the start of this lecture.

[SLIDE 8: What this means for your tests]
- Low temperature reduces variation; it doesn't remove it
- Our agent uses the API's default temperature
- Check meaning, not exact wording

Can you just set temperature to zero for testing? It helps, but it's not a guarantee. Providers update models, and long contexts shift outputs, so even at zero you'll see some drift. And you want to test the agent the way it runs in production. Our TechCorp agent doesn't set a temperature, so it uses the API default. The fix isn't to freeze the model. It's to check meaning instead of exact words. That's exactly what you'll build in Module 3.

[SLIDE 9: One run proves very little]
- Same case, several runs
- Measure how often it behaves the same
- Course threshold: consistency of at least 0.7

There's a second habit worth starting now. When the output can vary, one run proves very little. So how many runs do you need? In Module 10 you'll run the same case several times and measure consistency: how often the agent takes the same path of tools. Our quality policy asks for at least zero point seven.

[SLIDE 10: Recap]
- Tokens set your cost and truncation risk
- Context windows fill fast; the middle fades
- Temperature varies wording; test meaning instead

Three fundamentals. Tokens are your cost currency: seven hundred fifty-five tokens before the agent even acts, and judge calls cost more. Context windows fill with prompts, tools and history, and details in the middle fade. And temperature changes the wording from run to run, so exact-match assertions break and semantic checks win.

[AVATAR]
Now you know the engine. Next, you'll see what makes an agent different from a chatbot. Spoiler: it isn't the model. It's the loop. Agents don't just answer; they act, look at the result, and act again. That changes what you have to test.

### Recap

Tokens drive cost and truncation (755 input tokens on the agent's first call, about $0.0004 on gpt-4.1-mini, verify current pricing); context windows fill with system prompt, tools and history, and models attend less to the middle; temperature makes correct answers vary in wording (3 distinct answers out of 5 at 1.0), so tests must check meaning, not exact text.

### Transition

Next: Lecture 1.2 — What Makes an Agent an Agent (Not a Chatbot).

### Speaker notes: common student mistakes / Q&A

- Re-capture the token demo on the recording machine. In our build sandbox the tiktoken `o200k_base` file could not download, so the demo fell back to `len/4` and printed "approximate"; on a normal laptop it uses the real tokenizer and the token list, the 19 and the 755 will change. Update the narration numbers to match the new run.
- Prices come from `config/settings.py` (gpt-4.1-mini $0.40 / $1.60 per 1M input/output; gpt-4.1 $2.00 / $8.00), checked 2026-10-01. Verify current pricing before recording; "about five times" follows from those two rows.
- The temperature demo is offline: the mock LLM returns the first phrasing at 0.0 and a seeded choice of phrasings above 0. Live gpt-4.1-mini at 0.0 usually, but not always, repeats itself. If you want a live clip, re-capture with `OFFLINE=0` before recording and keep the narration ("one distinct answer" may become two).
- "Lost in the middle": the citation is flagged for verification. If it can't be confirmed, keep the advice ("test short and long conversations") and drop the attribution.
- The 1,000,000-token window for the gpt-4.1 family is from the demo constant; verify against current model docs.

---

## Lecture 1.2 — What Makes an Agent an Agent (Not a Chatbot)

| Field | Value |
|---|---|
| ID | 1.2 |
| Title | What Makes an Agent an Agent (Not a Chatbot) |
| Type | DM (diagram plus one terminal demo and a code walk-through) |
| Target duration | 7:00 (980 words at 140 wpm; 891 spoken) |
| Learning objectives | 1. Distinguish a chatbot (one call, text in, text out) from an agent (LLM plus tools in a loop). 2. Read an agent trace step by step: tool choice, arguments, tool result, final answer. 3. Explain why agents must be tested on their trajectory, not just the final answer. |
| Prerequisites | 1.1 |
| Files used | `demos/m01_agent_vs_chatbot.py`; `agents/support_agent.py` (`run_support_agent`, the loop); Diagram D3 (`D3-agent-loop.svg`) |

### Script

[AVATAR]
Same message, two systems. A customer writes: "I've been charged twice this month. My email is alice@example.com. Please create a ticket." The chatbot apologizes and says it can't see your account. The agent looks up Alice, finds the account, and opens a high-priority ticket. [PAUSE] One talks. The other acts. Which one do you think is harder to test?

[SLIDE 1: What Makes an Agent an Agent (Not a Chatbot)]
- Tell a chatbot from an agent in one look
- Read an agent's trace step by step
- Know why the path matters, not just the answer

By the end of this lecture, you'll be able to look at any AI system, say whether it's a chatbot or an agent, and explain why agents need a different kind of test.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Agent `gpt-4.1-mini`; offline mock in the demos
- File: `agents/support_agent.py`

Last lecture was about the engine: tokens, context and temperature. Now let's look at the machine built around it. People say "agent" when they mean "chatbot" all the time. If you mix them up, you'll test the wrong things.

[SLIDE 3: A chatbot: text in, text out]
Diagram: D3 build 1. A person icon sends "Request" to one LLM box; one arrow back labelled "Response". Caption: "one call, no tools, no loop".

A chatbot is the simplest thing you can build with a language model. A message goes in, one model call happens, and text comes out. No tools. No database. No second step. It can't check your account, because it has no way to reach your account.

Testing a chatbot is fairly direct. Send a prompt, judge the response. You still need to check meaning rather than exact words, as you saw last lecture, but there's one input and one output. One thing to check.

Now, what happens when you give that same model hands?

[SLIDE 4: An agent: a loop with tools]
Diagram: D3 build 2. The loop Observe → Think → Act, with "gpt-4.1-mini" in the centre and a Tools box below listing `lookup_customer, create_ticket, …`. Label: "repeat until done".

An agent runs in a loop. It observes the conversation and any tool results. It thinks: what should I do next? It acts: either it calls a tool, or it writes the final answer. If it called a tool, the result goes back into the conversation, and the loop runs again.

That's the whole difference. The same model, but now it decides which tool to call, with which arguments, how many times, and when to stop. Every one of those decisions can be wrong.

[SCREEN: Terminal. Run the side-by-side demo. Pause on the chatbot paragraph, then step through the agent's three lines.]

```bash
uv run python demos/m01_agent_vs_chatbot.py
```

[DEMO: Output (banner trimmed)]
```text
CHATBOT (one LLM call, no tools):
  I'm sorry about the trouble. I don't have access to your account or TechCorp's billing system, so I can't check the charges or open a ticket. Please contact TechCorp support with your account email.

AGENT (LLM + tools in a loop):
  step 1: lookup_customer({'identifier': 'alice@example.com'})
          -> Customer found: {"id": "CUST-001", "name": "Alice Johnson", "email": "alice@exam
  step 2: create_ticket({'customer_id': 'CUST-001', 'priority': 'high'})
          -> Ticket TKT-5001 created: Duplicate charge on Pro plan (Priority: high)
  final : Thanks, Alice. I've opened high-priority ticket TKT-5001 so our billing team can investigate the double charge and get back to you.

3 LLM calls, 2 tool calls, 2994 tokens
```

Here's the real thing. The chatbot gets one model call and no tools, so it does the honest thing: it says it can't reach the account. Polite, correct, and useless to Alice. Notice that a chatbot test would probably pass this answer. It's relevant and it's safe. It just doesn't do the job.

The agent goes to work. Step one: it calls `lookup_customer` with the email. The tool returns Alice Johnson, customer one. Step two: it calls `create_ticket` for that customer ID, with priority high. The tool returns ticket five thousand and one. Then the model writes the final answer. Three model calls, two tool calls, just under three thousand tokens.

[SLIDE 5: Five things you can check in one run]
- Did it pick the right tools?
- Did it pass the right arguments?
- Did it use the tool results correctly?
- Did it stop at the right time?
- Is the final answer right and grounded?

Now count what you could test in that one run. Was `lookup_customer` the right first tool? Was the email the right argument? Did the ticket use the customer ID the lookup returned, not a guess? Did the agent stop after the ticket, or wander on? And is the final answer correct and supported by what the tools said? A chatbot test checks one thing. This agent run gives you at least five.

[CODE: `agents/support_agent.py`, the loop inside `run_support_agent` (trimmed)]
```python
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **extra,
        )
        llm_calls += 1
        total_tokens += response.usage.total_tokens if response.usage else 0
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = run_tool(tool_call.function.name, args)
                tool_calls_log.append(
                    {"tool": tool_call.function.name, "arguments": args, "result": result}
                )
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": result}
                )
        else:
            return {
                "response": choice.message.content or "",
                "tool_calls": tool_calls_log,
                ...
            }
```

Here's that loop in our agent. It's plain OpenAI tool calling, no framework. Each pass calls the model with the conversation and the five tool definitions. If the model asks for tools, the code runs them, logs the tool name, the arguments and the result, and appends the result to the conversation. Otherwise, it returns the answer.

See the line that appends `choice.message`? The agent's own tool request goes into the conversation too, so on the next pass the model can see what it asked for and what came back. That's how the loop remembers.

Notice two more things. First, `max_iterations` is five. The loop can't run forever; you'll see why that matters in Lecture 1.4. Second, `tool_calls_log`. Every step is recorded. That log is what your trajectory tests will read.

[SLIDE 6: Four properties of an agent]
- Reasoning: decides what to do next
- Tools: acts on real systems
- Memory: carries context between steps and turns
- Goal pursuit: works until the task is done

Four properties separate agents from chatbots. Reasoning: it decides what to do next instead of just replying. Tools: it can change real systems, like opening a ticket or sending an email. Memory: it carries the conversation and tool results from step to step. And goal pursuit: it keeps going until the job is done, or it gives up and escalates.

A chatbot has none of these. Which ones does a basic retrieval bot have? Just one: a single tool, the search. A full agent has all four, and each is a separate thing to test. You'll take each one apart in the next lecture.

[SLIDE 7: Trajectory: the path, not just the destination]
- Trajectory: every step, tool and argument, in order
- Right answer, risky path: still a failure
- Wrong answer: the trajectory shows where

That brings us to the most important word in this course: trajectory. The trajectory is the full path: every tool call, every argument, every result, in order. Why does it matter? Because an agent can reach the right answer by a risky path, like reading an account it had no reason to open. And when the answer is wrong, the trajectory tells you which step went wrong. That's why our agent logs every step.

[SLIDE 8: Recap]
- Chatbots answer; agents act in a loop
- One run gives five things to check
- Test the trajectory, not just the answer

Three takeaways. Chatbots take text in and give text out. Agents run a loop of observe, think and act, with tools at every step. One short agent run already gives you five things to check. So you don't just test the final answer. You test the trajectory: every tool, every argument, every step.

[AVATAR]
You've seen that agents run a loop. So what's inside that loop? Next, you'll break an agent into its four building blocks: the model, the tools, memory and planning. And, more useful for you, where each one breaks.

### Recap

A chatbot makes one model call and returns text; an agent loops (observe, think, act) and calls tools, so one TechCorp run (`lookup_customer` → `create_ticket` → answer: 3 LLM calls, 2 tool calls) already has at least five checkable decisions, which is why agents are tested on their trajectory.

### Transition

Next: Lecture 1.3 — Agent Architecture: The Loop, Tools, Memory, Planning.

### Speaker notes: common student mistakes / Q&A

- The demo prints `create_ticket` with only `customer_id` and `priority` to keep the line short; the real call also has `subject` and `description` (the tool requires all four). Say so if a student asks.
- Ticket numbers (`TKT-5001`) count up per process; never quote a later ticket number as fixed.
- Offline run: the token count (2,994) uses `len/4` per message in the mock. Live counts differ; re-capture with `OFFLINE=0` if you show a live run, and keep "just under three thousand" only if it still holds.
- "Is this LangChain?" No. The course agents call the OpenAI SDK directly with tool calling, so every step is visible. The testing ideas apply to any framework.
- "Why does the chatbot refuse instead of making something up?" A bare call with no system prompt and no tools tends to admit it can't see accounts. Hallucinated answers appear when the model thinks it should know (Lecture 1.4).

---

## Lecture 1.3 — Agent Architecture: The Loop, Tools, Memory, Planning

| Field | Value |
|---|---|
| ID | 1.3 |
| Title | Agent Architecture: The Loop, Tools, Memory, Planning |
| Type | SL (animated diagram, with a code tour and one terminal demo) |
| Target duration | 7:00 (980 words at 140 wpm; 903 spoken) |
| Learning objectives | 1. Map any agent to four testable components: the LLM, tools, memory, planning. 2. Name the failure surfaces of each component, including the three per tool (selection, arguments, result use). 3. Locate each component in the TechCorp agent's code. |
| Prerequisites | 1.2 |
| Files used | `agents/support_agent.py` (`SYSTEM_PROMPT`, `TOOLS`, `KNOWLEDGE_BASE`, `run_support_agent`); `demos/m01_lab_run_agent.py`; `datasets/failure_gallery.json`; Diagrams D3, D6 |

### Script

[AVATAR]
A customer asks, "How do I reset my password?" The agent reads the question correctly, decides it needs help, and calls a tool. The wrong one. It opens a support ticket for a question the knowledge base answers in one line. [PAUSE] The reasoning was fine. The hands were wrong. To test agents well, you need to know which part failed. So which part was it?

[SLIDE 1: Agent Architecture: The Loop, Tools, Memory, Planning]
- Map any agent to four testable parts
- Know how each part breaks
- Find each part in real code

By the end of this lecture, you'll be able to take any agent and map it to four components you can test one at a time.

[SLIDE 2: The blueprint]
Diagram: Central circle "Agent core (the loop)" with four satellites: LLM brain (top), Tools (right), Memory (bottom), Planning (left). Each satellite carries a small test icon.

Every agent has the same four parts, whatever framework built it. A model that reasons. Tools that act. Memory that carries context. And planning, the strategy for getting from question to done. Each part breaks in its own way, so each needs its own tests. This blueprint is the map you'll use every time you design a test strategy.

[SLIDE 3: Part 1: the LLM brain]
- Reads system prompt, history, tool results
- Writes reasoning, tool calls and answers
- Risks: hallucination, reasoning errors, ignored rules

Part one is the model itself. In our agent, that's `gpt-4.1-mini`. It reads the system prompt, the conversation and every tool result, and it writes three kinds of output: reasoning, tool calls and the final answer.

Sound like anyone you've worked with? Think of it as a brilliant but unreliable consultant. It connects dots fast and writes beautifully. It also sometimes invents facts, sometimes draws the wrong conclusion from the right facts, and sometimes forgets a rule from the brief.

[SCREEN: VS Code, `agents/support_agent.py`, scroll `SYSTEM_PROMPT`. Highlight "Only state prices, limits and policies that appear in a knowledge base result" and the four escalation rules.]

Here's the brief our agent gets. Five responsibilities, six rules, four escalation rules. Every rule is a test waiting to be written. "Only state prices, limits and policies that appear in a knowledge base result." That's the line from Lecture 0.1. Delete it, and the brain starts inventing prices.

[SLIDE 4: Part 2: tools, the agent's hands]
Diagram: Five tool cards in a row: `lookup_customer`, `search_knowledge_base`, `create_ticket`, `send_email`, `escalate_to_human`. Under each, three small check boxes: selection, arguments, result use. Two cards (`create_ticket`, `send_email`) carry a red "side effect" tag.

Part two: tools. These are the agent's hands. Our agent has five: look up a customer, search the knowledge base, create a ticket, send an email, and escalate to a human.

[SCREEN: VS Code, `agents/support_agent.py`, collapse `TOOLS` to show the five `"name":` lines, then expand `create_ticket` to show its four required parameters and the `priority` enum (`low`, `medium`, `high`, `critical`).]

Here's why tools carry the most risk. A bad sentence is embarrassing. A bad tool call opens the wrong ticket, emails the wrong person, or reads the wrong customer's account. Tools have side effects.

Every tool has three failure surfaces. Selection: did it pick the right tool? Arguments: did it pass the right values? And result use: did it read the result correctly? Five tools, three surfaces each. That's fifteen things to test before you even look at the answer. Which of the five worries you most? Look at the ones that change something: `create_ticket`, `send_email` and `escalate_to_human`. A wrong search wastes a call. A wrong email can't be unsent.

[SCREEN: Terminal. Run the Lab 1.1 demo and zoom on the third query, the unknown email.]

```bash
uv run python demos/m01_lab_run_agent.py
```

[DEMO: Output (third query only)]
```text
Q: Look up my account. My email is unknown@notreal.com
   tool lookup_customer({'identifier': 'unknown@notreal.com'}) -> Customer not found.
   A: I'm sorry, I couldn't find any account matching unknown@notreal.com. Please check the address, or give me your account ID.
```

Here's result use done right. The tool says "Customer not found." The agent tells the customer exactly that and asks for another identifier. A weaker agent might treat an empty result as success and invent an account. That's a test case: feed a tool an unknown value, check the answer admits it.

[SLIDE 5: Part 3: memory]
- Short-term: the conversation history
- Working: messages and tool results in this run
- Long-term: knowledge base and customer records
- Risks: forgotten facts, wrong retrieval, overflow

Part three: memory. Three layers. Short-term memory is the conversation history; in our code, that's the `conversation_history` argument. Working memory is the message list inside one run: every tool call and result so far. Long-term memory is what the agent can look up: five knowledge-base articles and three customer records here, often a vector database in bigger systems.

What breaks? Retrieval can return the wrong article. History can grow until early details get dropped. A customer gives their email in message two; by message thirty, the agent asks for it again. Testing memory means testing at several conversation lengths. Few teams ever write that test. Will yours?

[SLIDE 6: Part 4: planning]
Diagram: "Cancel my subscription and refund me. I signed up 3 weeks ago." Plan: 1 `lookup_customer` → 2 `search_knowledge_base` (refund policy) → 3 `create_ticket` → answer. A "reflect" diamond after each step: "did that work? adjust the plan?" A side branch at step 2: "21 days < 30 days: eligible".

Part four: planning. How does the agent break a task into steps, and when does it stop? Take one of our hardest golden cases: cancel my subscription and refund me, I signed up three weeks ago. The agent looks up the customer, searches the refund policy, then creates a ticket. Four model calls, three tools, in that order.

Planning failures are the hardest to test, because the right plan depends on what each step returns. You can't always hard-code the expected steps. Sometimes you check the order. Sometimes you check that the plan was sensible given what the agent knew. That's trajectory evaluation, and you'll build it in Module 6.

[SCREEN: VS Code, `run_support_agent` signature. Highlight `conversation_history: list | None = None` and `max_iterations: int = 5`.]

In code, our agent's planning is the loop itself, plus the system prompt's rules, plus one guard: at most five model calls. Hit the cap, and it apologizes and escalates. Is five the right number? For this agent, yes: its longest golden case needs four calls. Your agent might need a different cap, and testing tells you which.

[SLIDE 7: Your testing map]
Diagram: D6 (test strategy matrix), rows LLM, Tools, Memory, Planning; columns the five quality dimensions. Build rows 1 to 4 in sync with the narration.

Let's put it together. What does each part do, and how does it fail? The LLM reasons and writes; it can hallucinate, reason badly or drift from the brief. Tools act; they can be the wrong tool, get the wrong arguments, or have their results misread. Memory stores and retrieves; it can retrieve the wrong thing or forget. Planning sequences the steps; it can choose a bad plan or never stop. Every test you write targets one of these rows.

[SLIDE 8: Recap]
- Four parts: brain, tools, memory, planning
- Tools carry the most risk: side effects
- Each part fails differently; test each

Lock in the blueprint. Every agent has four testable parts: the model, the tools, memory and planning. Tools carry the most risk, because they change real systems. And each part fails in its own way, so each gets its own tests.

[AVATAR]
You know the four parts. Next, the six specific ways they fail: hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift and infinite loops. You'll see a real recorded example of every one.

### Recap

Every agent has four testable components (the LLM, tools, memory, planning); in TechCorp that is gpt-4.1-mini with `SYSTEM_PROMPT`, five tools with three failure surfaces each, conversation history plus five KB articles and three customer records, and a loop capped at five model calls.

### Transition

Next: Lecture 1.4 — The 6 Ways AI Agents Fail (And Why Testing Is Hard).

### Speaker notes: common student mistakes / Q&A

- The hook is a recorded run from `datasets/failure_gallery.json` (`wrong_tool_selection`), not a live failure; the shipped agent searches the knowledge base for password questions. Lecture 1.4 shows the recording on screen.
- GS-06 (cancel and refund) trajectory: `lookup_customer` → `search_knowledge_base` → `create_ticket`, 4 LLM calls offline (bible §4.4). Live runs should match the order; if a live run differs, that's a good Module 6 discussion, not a script change.
- "Where's the planner?" Many production agents have no separate planner; the model plans implicitly inside the loop. Frameworks with explicit planners add a fifth thing to test (the plan itself), covered in Module 7.
- Lab 1.1 uses `demos/m01_lab_run_agent.py`: five queries with traces and a worksheet (failure mode, component, test that would catch it).

---

## Lecture 1.4 — The 6 Ways AI Agents Fail (And Why Testing Is Hard)

| Field | Value |
|---|---|
| ID | 1.4 |
| Title | The 6 Ways AI Agents Fail (And Why Testing Is Hard) |
| Type | DM (teach plus recorded failure gallery) |
| Target duration | 6:00 (840 words at 140 wpm; 734 spoken) |
| Learning objectives | 1. Name the six failure modes: hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops. 2. Give a TechCorp example of each and the check that catches it. 3. Explain why step-level tests miss trajectory-level failures. |
| Prerequisites | 1.3 |
| Files used | `demos/m01_failure_gallery.py`; `datasets/failure_gallery.json`; `evaluators/tool_metrics.py` (`check_arguments`); `performance/reliability.py` (`detect_tool_loop`); `evaluators/metrics.py`; Diagram D1 |

### Script

[AVATAR]
A customer asks for TechCorp's pricing. The agent answers instantly: Basic at seven ninety-nine, Pro at twenty-four ninety-nine, Enterprise at ninety-nine a month. Confident. Friendly. Every price is wrong. The real plans are nine ninety-nine, twenty-nine ninety-nine, and custom pricing. [PAUSE] No error was raised. Would a unit test catch that? Not one that only checks the response isn't empty.

[SLIDE 1: The 6 Ways AI Agents Fail]
- Name all six failure modes
- See a real example of each
- Know which check catches which

By the end of this lecture, you'll be able to name the six ways agents fail, show an example of each, and say which check catches it.

[SLIDE 2: Verified for this lecture]
- `openai 2.54.0` and `deepeval 4.2.7`
- Six recorded runs from `failure_gallery.json`
- Checks run offline with the mock judge

Before you can test anything, you need to know what breaks. This is your field guide. Every technique from Module 3 onward maps back to one of these six.

[SLIDE 3: Failure 1: hallucination]
Diagram: D1 build 1 (hallucination panel with its one-line definition).

Failure one: hallucination. The agent states facts that aren't in its context, its tool results or the world. That pricing answer was hallucinated: it never searched the knowledge base, so it answered from memory. The check that catches it is faithfulness: compare every claim with the source.

[SLIDE 4: Failures 2 and 3: the hands]
Diagram: D1 builds 2 and 3 (wrong tool selection, incorrect tool arguments).

Failure two: wrong tool selection. The agent calls the wrong tool, or a tool when none was needed. That's the password question from last lecture: a ticket instead of a knowledge-base search. The check: expected tools versus called tools.

Failure three: incorrect tool arguments. Right tool, wrong values. The customer gives an email, and the agent looks up the first name instead. The tool finds nothing. The check: compare the arguments with what they should be.

Which component failed in each case? Hallucination is the brain. Wrong tool and wrong arguments are the hands: the tools layer from last lecture.

[SLIDE 5: Failure 4: reasoning errors]
Diagram: D1 build 4 (reasoning errors).

Failure four: reasoning errors. Correct inputs, correct tools, wrong conclusion. The agent reads the thirty-day refund policy, hears "three weeks", and says that's too late. Twenty-one days is less than thirty. The check: correctness against an expected answer.

[SLIDE 6: Failures 5 and 6: losing the plot]
Diagram: D1 builds 5 and 6 (goal drift, infinite loops); the full six-panel grid stays on screen at the end.

Failure five: goal drift. The agent wanders off the user's goal. Someone asks about a double charge, and the agent ends up explaining API rate limits. Prompt injection is goal drift on purpose, when an attacker hijacks the goal. The check: answer relevancy, and red teaming in Module 8.

Failure six: infinite loops. The agent repeats the same step without progress. Same search, same result, again and again. Every pass costs tokens, and the customer waits. The check: a loop detector, and a hard cap on steps.

And the components? Reasoning errors live in the brain. Goal drift and loops are planning failures: the agent lost track of where it was going. So where would you look first if your agent started looping?

[SCREEN: Terminal. Run the failure gallery. Scroll one case at a time; colour each "caught" line red.]

```bash
uv run python demos/m01_failure_gallery.py
```

[DEMO: Output (banner trimmed)]
```text
[hallucination] What are your pricing plans?
  tools : []
  reply : TechCorp has three plans: Basic at $7.99/month, Pro at $24.99/month and Enterprise at $99/month.
  why   : Answered from memory without searching the knowledge base; every price is wrong.
  caught: Faithfulness 0.00 (threshold 0.8)

[wrong_tool_selection] How do I reset my password?
  tools : ['create_ticket']
  reply : I've opened a ticket for your password reset.
  why   : A self-service FAQ became a ticket: the KB article answers it.
  caught: expected ['search_knowledge_base'], got ['create_ticket']

[incorrect_tool_arguments] Can you look up my account? My email is alice@example.com
  tools : ['lookup_customer']
  reply : I couldn't find an account for Alice.
  why   : Right tool, wrong argument: passed a first name instead of the email.
  caught: argument check: wrong={'identifier': ('alice@example.com', 'Alice')}

[reasoning_error] I signed up 3 weeks ago. Can I still get a full refund?
  tools : ['search_knowledge_base']
  reply : Unfortunately 3 weeks is outside our 30-day money-back guarantee, so a full refund isn't possible.
  why   : Retrieved the right policy, then drew the wrong conclusion (21 days < 30 days).
  caught: GEval correctness 0.30

[goal_drift] I was charged twice this month. Can you fix it?
  tools : ['search_knowledge_base']
  reply : Great question! The Pro plan includes 1,000 API requests per hour, and you can create API keys under
  why   : Started on billing, ended up explaining API limits; the double charge is never addressed.
  caught: Answer relevancy 0.00

[infinite_loop] What is the refund policy for annual enterprise contracts signed through a reseller?
  tools : ['search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base']
  reply : I apologize, but I'm having trouble processing your request. Let me escalate this to a human agent.
  why   : The same search 5 times in a row until the 5-iteration cap stopped it.
  caught: loop detector: 'search_knowledge_base' repeated 3 times in a row
```

Here are all six, one recorded run each, and each one caught by a different check. Hallucination: faithfulness zero against a threshold of zero point eight. Wrong tool: we expected a search and got a ticket. Wrong argument: the check shows exactly which value was wrong. Reasoning: correctness zero point three. Drift: relevancy zero. And the loop: the same search five times, until the five-step cap stopped it. The detector flagged it at three in a row.

Notice something? Six failures, and not one exception. Every run returned a polite answer. A monitoring alert on errors would have stayed green all day. And look at the reasoning case: the agent did search, and it found the right policy. A test that only checks "did it call the knowledge base?" passes. The mistake is in what it concluded.

[SLIDE 7: Why testing agents is hard]
- No crash: every failure returns a fluent answer
- Each step can look fine alone
- Failures compound across steps
- Different failures need different checks

So why is this hard? First, nothing crashes. Second, every single step can look reasonable on its own. The drifting agent's search was a sensible search. Third, failures compound: a wrong argument in step one means step two works on bad data. And fourth, there's no single check. Faithfulness misses the loop. A loop detector misses the hallucination. You need a set of checks, applied to the whole trajectory. Which of these six would hurt your users most?

[SLIDE 8: Recap]
- Six failure modes, each with its own check
- Agents fail politely, with no exceptions
- Test the whole trajectory, not single steps

Lock it in. Six failure modes: hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift and infinite loops. Agents fail politely, with no exceptions to catch. And because failures compound, you test the whole trajectory, with a different check for each mode.

[SLIDE 9: You can now]
- Explain tokens, context windows and temperature for testing
- Map any agent to brain, tools, memory, planning
- Name the six failure modes and their checks

[AVATAR]
You can now take any agent apart, and name the six ways it can fail. In Lab 1.1, you'll run the agent on five queries and fill in a failure worksheet. Then Module 2 tackles why your existing test toolkit, exact assertions, mocks and pass or fail, breaks on all of this.

### Recap

The six failure modes are hallucination (caught by Faithfulness), wrong tool selection (expected vs called tools), incorrect tool arguments (argument check), reasoning errors (GEval correctness), goal drift (answer relevancy, red teaming) and infinite loops (loop detector plus a step cap); none raises an exception, so agents need several checks applied to the whole trajectory.

### Transition

Next: Lecture 2.1 — Deterministic vs. Non-Deterministic: The Testing Paradigm Shift (after Lab 1.1).

### Speaker notes: common student mistakes / Q&A

- The gallery replays six recorded runs from `datasets/failure_gallery.json`; the checks (Faithfulness, GEval correctness, Answer Relevancy) run live code paths against the offline mock judge. With `OFFLINE=0` the metrics are scored by gpt-4.1; the faithfulness and relevancy zeros should hold, the correctness 0.30 may move. Re-capture live before recording if you show live scores.
- Do not use "grounding failure" or "boundary violation" as failure-mode names; they are retired. Data leaks and unauthorized actions are taught as attacks in Module 8.
- "Is prompt injection a seventh mode?" No. It's an attack that causes goal drift (and sometimes wrong tool use). Module 8 covers it.
- "Slow response time?" Not a failure mode; it's measured under the Reliability dimension (Lecture 2.2) and Module 10.
- The loop detector (`performance/reliability.py`) flags three identical consecutive actions; the agent's own cap is five model calls. Module 7.3 builds the detector.
