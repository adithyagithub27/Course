# Instructor Bio Templates

> **Do not publish any placeholder text.** Replace every `[BRACKETED]` field with the instructor's real, verifiable credentials. Leave a field out if it doesn't apply. **Don't invent job titles, employers, years of experience, student counts, certifications, incidents you handled or project names.** Udemy's instructor profile has headline and biography fields with their own length limits (verify in *Profile → Udemy profile*). The headline in particular is short (historically about 60 characters).

---

## Headline options (profile headline field; keep ≤ 60 chars, verify)

- `[Role] | Production AI Agents: Build, Test, Deploy, Operate`
- `[Role] building, testing and operating AI agents in Python`
- `AI engineer and instructor: LLMOps, evals and voice agents`

Check the length with `python3 -c "print(len('your headline'))"`.

## Short bio (~60-80 words)

Use it on the course landing page, the promo lower third (first sentence only) and social profiles.

> I'm [FULL NAME], [CURRENT ROLE] [at COMPANY, if you can share it]. I build AI agents that have to work in production, not just in demos, and I care about the parts demos skip: what they cost, how they fail and how you find out. [ONE VERIFIABLE CREDENTIAL, e.g., years building software / domain / a shipped system you can name]. My courses follow a Build → Test → Deploy → Operate path, and every course is hands-on Python with code you can take to work.

## Long bio (~200-300 words)

Use it for the Udemy profile biography.

> **[FULL NAME]** is [CURRENT ROLE] [at COMPANY / independent consultant / etc.] who [ONE SENTENCE ON WHAT YOU BUILD: e.g., "designs and ships LLM-powered applications for ___"].
>
> [BACKGROUND PARAGRAPH: prior roles, domains (e.g., fintech, logistics, support, platform engineering), and the kind of systems you've shipped. Only include verifiable facts. Leave out numbers you can't back up.]
>
> [WHY OBSERVABILITY PARAGRAPH: your real connection to operations, SRE, monitoring, cost management or on-call work, e.g., "I started caring about observability when ___." If you have no professional SRE background, say so honestly and frame it as a builder's view: "I built Atlas, the course's helpdesk agent, and its traffic simulator end to end, instrumented it with OpenTelemetry and Langfuse, and wrote the three incident datasets from failure patterns I've seen or reproduced, not from any client's data."]
>
> [TEACHING PARAGRAPH: teaching approach. Suggested text you can keep: "My courses are built around one running project that grows lecture by lecture, with tests from the start and failures shown before fixes. I care about the parts demos skip: cost, latency, failure modes, and what happens on a Monday morning."]
>
> [SERIES PARAGRAPH: "My courses form a Build → Test → Deploy → Operate path: *Generative AI & AI Agents: Zero to Production* (build), *AI Agent Testing & Evaluation* (test), *Production Voice AI Agents with Python* (build, test and deploy for voice), and *AI Agent Observability & Cost Control* (operate)."]
>
> [OPTIONAL: public work you can point to without links in the bio (Udemy restricts links in bios; verify), e.g., open-source repos, talks, publications, certifications with issuer and year.]

## Credential worksheet (fill in privately first)

| Field | Your real answer | Verifiable? (link/proof kept on file) | Use in bio? |
|---|---|---|---|
| Current role and employer (if shareable) | | | |
| Years of relevant experience | | | |
| AI/LLM systems shipped (describe without confidential detail) | | | |
| Operations, SRE, on-call or monitoring experience | | | |
| Cost management / FinOps experience | | | |
| Testing/QA/evaluation experience | | | |
| Certifications (issuer, year) | | | |
| Talks, publications, open-source | | | |
| Teaching experience / Udemy students (from the dashboard only) | | | |

## Rules

- Write in first person on the landing page and third person in the profile biography (or pick one and stay consistent).
- No unverifiable superlatives ("world-class", "leading expert", "top 1%").
- **Never describe a real incident from a past employer or client as if it were yours to share.** The course's incidents are fictional and labelled as such; keep the bio consistent with that.
- No off-platform contact details or links in the bio unless Udemy's current profile rules allow them (verify). Social links go in the dedicated profile fields.
- If lectures use a HeyGen avatar of the instructor, the bio shouldn't imply the avatar is live footage (see `publish-checklist.md` §9).
