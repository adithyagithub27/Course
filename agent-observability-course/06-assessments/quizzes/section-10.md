# Quiz: Governance (Section 10)

| Field | Value |
|---|---|
| Udemy lecture | 10.5 Quiz: Governance |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 10.1 to 10.4 |

---

### Q1. Lecture 10.1 calls traces "a data breach waiting to happen". Which list correctly names where personal data enters Atlas's telemetry?

*Related lecture: 10.1 Your traces are a data breach waiting to happen*

- **A.** In the user's prompt (names, employee ids, health or payroll details typed into the question), in tool results (`lookup_ticket` returns records, `reset_password` returns contact details), in the model's answer, and in every copy of these that the judge, the dataset and the export receive.
  - *Explanation:* Correct. The threat model is that telemetry duplicates the most sensitive path of the application into a system with broader access, longer retention and more consumers (analysts, judges, vendors). Masking at the source is the only control that covers every consumer.
- **B.** Only in tool results; prompts are anonymous.
  - *Explanation:* Incorrect. Employees routinely type their own and others' identifiers into questions.
- **C.** Nowhere, because Langfuse stores only token counts.
  - *Explanation:* Incorrect. Langfuse stores inputs and outputs by default; that is what makes traces useful and dangerous.
- **D.** Only in the `user_id` field.
  - *Explanation:* Incorrect. `user_id` is one field; the free text is the bigger exposure.

**Correct answer: A**

---

### Q2. Atlas masks PII in the Langfuse SDK (`mask=`) **and** in the OpenTelemetry Collector (the `attributes/redact` processor). Which statement correctly describes the roles?

*Related lecture: 10.2 Code-along: masking in the SDK and the collector*

- **A.** The SDK mask is redundant once the collector redacts.
  - *Explanation:* Incorrect for the same reason: the SDK is the only layer that guarantees raw values never leave the process.
- **B.** The SDK mask is the primary control because it runs before data leaves the process and covers every exporter; the collector is defence in depth that enforces policy centrally, including for services you do not control: `attributes/redact` deletes message bodies, tool results and Langfuse input/output attributes and hashes tool arguments, `user.id` and `enduser.id` before anything reaches a backend.
  - *Explanation:* Correct. Two layers with different failure modes; the near one is primary.
- **C.** Both are unnecessary if the Langfuse project is private.
  - *Explanation:* Incorrect. Access control limits who can log in; it does nothing about what analysts, judges or exports can read.
- **D.** The collector is the primary control; the SDK mask is a convenience.
  - *Explanation:* Incorrect. Anything that bypasses the collector (the console or file exporter, a direct SDK exporter, a debug log) would see raw data; the collector cannot be the only line.

**Correct answer: B**

---

### Q3. With `hash_ids=True`, `mask_text` replaces `NW-10433` with `<EMPLOYEE_ID:731ea41e>` (a short HMAC-SHA256 keyed with `ATLAS_PII_HASH_KEY`) rather than plain `<EMPLOYEE_ID>`. What does this buy and what does it cost?

*Related lecture: 10.2 Code-along: masking in the SDK and the collector*

- **A.** It lets Langfuse display the real name on hover.
  - *Explanation:* Incorrect. The whole purpose is that the real value is not available to the backend.
- **B.** It buys nothing; a hash is as identifying as the id.
  - *Explanation:* Incorrect as stated: a keyed short hash cannot be recomputed, or matched against a dictionary of ids, without the key, and it is not the id.
- **C.** It keeps joins: an analyst can still count sessions per person, correlate a trace with a ticket by hashed id, or see that the same employee hit the same failure five times, without ever seeing the identity; the cost is that it is pseudonymisation, not anonymisation, so the key must be kept secret (anyone with it can hash every employee id and match), and the data still counts as personal data under most regimes.
  - *Explanation:* Correct. Lecture 10.2's "keep hashes for joins" and lecture 10.4's caution: pseudonymised data is still regulated. Coding exercise CE4 implements the same `hash_ids` switch.
- **D.** It makes the trace smaller.
  - *Explanation:* Incorrect. Size is unchanged in any meaningful way; the point is analytical utility.

**Correct answer: C**

---

### Q4. Northwind wants dev, staging and production telemetry kept apart, and HR data kept from being visible to the engineering team's analysts. Which arrangement follows lecture 10.3?

*Related lecture: 10.3 Retention, access and tenant separation*

- **A.** Separate Langfuse accounts per employee.
  - *Explanation:* Incorrect. Unmanageable and unnecessary; the boundary is teams and environments, not individuals.
- **B.** Keep everything forever so audits are possible.
  - *Explanation:* Incorrect. Indefinite retention of PII-bearing traces is itself a compliance failure; retain aggregates long and raw traces short, per policy.
- **C.** One Langfuse project for everything, distinguished by tags; everyone gets viewer access.
  - *Explanation:* Incorrect. Tags filter views but do not restrict access; anyone who can see the project can remove the filter.
- **D.** A Langfuse project per environment (dev, staging, prod), with `environment` set on traces for cross-checks; tenants as tags inside a project when analysts may see all departments, or a separate project per tenant when access must be restricted (the HR case); retention windows set per project (shorter for prod PII-bearing data, longer for aggregated metrics) and role-based access per project.
  - *Explanation:* Correct. Projects are the access and retention boundary; tags are a convenience inside a boundary. Choose per tenant based on who must *not* see what.

**Correct answer: D**

---

### Q5. Lecture 10.4 discusses record-keeping obligations such as those the EU AI Act places on high-risk AI systems. What is the course's guidance, and what does it explicitly not do?

*Related lecture: 10.4 Regulatory logging obligations (not legal advice)*

- **A.** Design telemetry so that, if a system is classified high-risk, you can produce an audit trail of what the agent did (timestamps, versions of prompt and model, tool calls, decisions and their basis) for the required retention period, while minimising personal data in that trail; and confirm classification, retention periods and content with counsel, because the obligations depend on the system's classification and are still being interpreted.
  - *Explanation:* Correct. The engineering takeaway is that the trace with release, prompt version and masked tool calls *is* the audit trail if you keep it appropriately; the legal takeaway is to verify with counsel. The governance checklist in `10-resources/` lists the questions to bring.
- **B.** Internal helpdesk agents are exempt from all regulation, so nothing applies.
  - *Explanation:* Incorrect. Classification is a legal determination (an HR agent touching employment decisions may not be low-risk), and other regimes (GDPR, sector rules) apply regardless.
- **C.** Delete all logs after 24 hours to minimise liability.
  - *Explanation:* Incorrect. Deleting evidence you may be obliged to keep is the opposite failure.
- **D.** The course gives legal advice: log everything, including prompts and outputs, for ten years.
  - *Explanation:* Incorrect on both counts: the course explicitly flags it is not legal advice, and "log everything forever" conflicts with data-minimisation duties.

**Correct answer: A**

---

### Q6. A judge model reads sampled traces to score groundedness. Which governance consequence does lecture 10.1 draw from this?

*Related lecture: 10.1 Your traces are a data breach waiting to happen*

- **A.** The judge must run on-premises.
  - *Explanation:* Incorrect as a rule. Location is a choice; the requirement is about what the judge sees.
- **B.** Whatever the judge receives must already be masked (it reads the same masked spans, never raw application data), its calls are themselves traced and costed, and sending traces to an external judge is a data transfer that the governance checklist must cover.
  - *Explanation:* Correct. "Judges see everything" is one of the three exposure paths in the threat model; masking at the SDK is what makes judging on production traffic defensible.
- **C.** The judge should be given raw data so its scores are accurate, with masking applied afterwards.
  - *Explanation:* Incorrect. Once sent, the data has left; masking afterwards protects nothing. Judge criteria are written to work on masked text (an `<EMAIL>` token does not change groundedness).
- **D.** None; the judge is part of the system.
  - *Explanation:* Incorrect. The judge is another consumer, often a third-party API, that receives the trace content.

**Correct answer: B**
