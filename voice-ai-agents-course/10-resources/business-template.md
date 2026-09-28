# Business Template: Re-skin Riley for Any Business

**Used in:** 4.7 (Challenge: Riley for your business), 13.7 (Domain swap: restaurant, salon or law office)

> Fill this in for a real or realistic business you know. **Don't include real customer data, real phone numbers or confidential information.** Use fictional names and `555-01XX` numbers. Keep **style** and **output rules** from Riley. They're about voice, not the business.

---

## 1. Business facts

| Field | Your business | Maple Street Dental (example) |
|---|---|---|
| Business name | | Maple Street Dental (fictional) |
| Type | | Dental clinic |
| Agent name and role | | Riley, AI receptionist |
| Opening hours | | Mon-Fri 8 AM-6 PM, Sat 9 AM-1 PM |
| Location / parking | | 123 Maple Street, free lot behind the building |
| Services (3-8) | | Cleaning, check-up, filling, whitening, emergency visit |
| Appointment types + durations | | Cleaning 60 min, check-up 30 min, emergency 30 min |
| Policies (cancellation, deposits, late arrival) | | 24-hour cancellation notice |
| Languages to support | | English (Spanish, Hindi in 7.8) |
| Human handoff: when, and to which number | | Front desk, business hours: `+1 555 0100` (fictional) |
| Things the agent must **never** do | | Give medical advice; reveal appointments without identity verification |
| Industry sensitivities | | Health data (HIPAA) |

## 2. FAQ skeleton (becomes `data/faq.md`-style content)

Write answers **for the ear**: 1-2 sentences, no lists or URLs.

```markdown
## Hours
Q: When are you open?
A: [one or two spoken sentences]

## Location and parking
Q: Where are you and where do I park?
A:

## Services
Q: Do you offer [service]?
A:

## Prices / payment (if you'll answer these at all)
Q: How much is [service]?
A: [or: "I can't quote prices on the phone, but I can transfer you to the front desk."]

## Policies
Q: What's your cancellation policy?
A:

## [Industry-specific]
Q:
A:
```

Aim for 10-20 questions. Add an explicit "don't know" rule: anything not covered → offer a transfer.

## 3. Tool schema

Define the actions the agent can take. Keep business logic in pure Python (like `src/maple/scheduler.py`) and keep tools thin.

| Tool name | What it does | Arguments (name: type) | Returns (speakable) | Irreversible? (needs read-back) | Needs identity check? |
|---|---|---|---|---|---|
| `find_available_slots` | Lists open times | `service: str, preferred_day: str` | "Tuesday at 2 or 3:30" | No | No |
| `book_appointment` | Books a slot | `name: str, phone: str, service: str, time: str` | "Booked for Tuesday at 2" | **Yes** | No |
| `reschedule_appointment` | | | | Yes | Yes |
| `cancel_appointment` | | | | Yes | Yes |
| `lookup_info` | FAQ retrieval | `question: str` | Short answer or "not sure" | No | No |
| `transfer_to_human` | Warm/cold transfer | `reason: str` | "Connecting you now" | Yes | No |
| *(your tool)* | | | | | |

**Examples for 13.7**

| Business | Typical tools |
|---|---|
| Restaurant | `check_table_availability(party_size, date, time)`, `book_table(...)`, `lookup_menu_info(question)` (allergens → escalate if unsure) |
| Salon | `find_stylist_slots(service, stylist?, day)`, `book_service(...)`, `cancel_booking(...)` |
| Law office | `book_consultation(practice_area, day)`, `lookup_office_info(question)`. **Guardrail: never give legal advice**; route urgent matters to a human |

## 4. Prompt blocks (fill in; see `voice-prompting-cheatsheet.md`)

```text
IDENTITY: You are [agent name], the AI [role] for [business]. You are an AI assistant and say so at the start of the call.

GOAL: Help callers [primary tasks]. A successful call ends with [outcome].

STYLE: Warm and efficient. One or two short sentences per turn. One question at a time.   ← keep from Riley

OUTPUT RULES: Plain spoken text only. No markdown, lists, emojis or URLs. Say numbers, dates and prices as words.   ← keep from Riley

TOOLS POLICY: Never state availability without calling [availability tool]. Read back [confirmation fields] and get a clear yes before [irreversible tools].

GUARDRAILS: Never [industry-specific never-do list]. Don't reveal [sensitive info] until the caller is verified by [verification fields].

ESCALATION: Offer to transfer when the caller asks for a person, is upset, mentions [urgent triggers], or you can't help after two tries.
```

**Confirmation fields** (what gets read back): `[e.g., name, date, time, party size]`
**Verification fields** (identity check): `[e.g., name + phone on file + date of birth]`
**Urgent triggers** (immediate transfer): `[e.g., "emergency", "allergic reaction", "court date tomorrow"]`

## 5. Test checklist (adapt Riley's tests)

- [ ] **Greeting** says the business name and that it's an AI (`test_greeting.py` adapted)
- [ ] **Happy path**: the main booking flow calls the availability tool, then the booking tool with the right arguments (`test_booking_flows.py` adapted)
- [ ] **Read-back** happens before every irreversible tool
- [ ] **Correction**: "no, [different day]" leads to a corrected booking
- [ ] **No availability** path via `mock_tools`
- [ ] **Tool error** path via `mock_tools` (speakable error + retry or transfer)
- [ ] **Unknown question** → "not sure" + transfer offer (no invented facts)
- [ ] **Guardrail**: industry-specific refusal (medical/legal advice, allergens) passes a judge `intent`
- [ ] **Social engineering / injection** attempts fail (`test_safety.py` adapted)
- [ ] **Escalation**: urgent trigger → `transfer_to_human`
- [ ] **WER**: 10+ domain terms (menu items, stylist names, practice areas) in `stt_references`-style data
- [ ] **Latency**: p95 within your budget (`latency-budget-worksheet.md`)
- [ ] Transcript posted in Q&A (4.7) / repo README updated with a demo and test report (13.7)

## 6. Submission (4.7 / 13.7)

- 4.7: post **one console transcript** in Q&A with your business type and one thing you changed in the prompt.
- 13.7: repo branch or folder with FAQ, prompt, tools, adapted tests, a test report and a short demo recording (numbers masked). Check it against `voice-agent-readiness-scorecard.md`.
