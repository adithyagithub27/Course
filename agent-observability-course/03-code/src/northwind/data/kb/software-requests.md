---
id: KB-010
title: Software requests and licences
owner: IT Service Desk
tags: [software, licence, install, application, approval]
updated: 2026-08-05
---
# Software requests and licences

- Standard software (Office, Teams, Slack, Zoom, browsers, 7-Zip, VLC) installs from the **Company Portal** without a ticket.
- Licensed software (Adobe, Tableau, JetBrains, AutoCAD) requires a ticket with category *Software / Licence* and manager approval; provisioning takes 2 business days.
- Open-source developer tools are pre-approved from the list at `it.northwind.example/oss`.
- Software that stores customer data outside the EU must pass a security review (allow 2-3 weeks).
- Local admin rights are granted for 7 days at a time through the *Temporary Admin* self-service.

## Licence returns
When you leave a project, release licences in the Company Portal so the department is not charged.

## Categories and how to get them
| Category | Examples | How |
|---|---|---|
| Standard | Microsoft 365, Slack, Zoom, browsers, 7-Zip, VLC, Adobe Reader | Company Portal, self-service, immediate |
| Licensed | Adobe Creative Cloud, Tableau, JetBrains, AutoCAD, Visio, Project | *Software / Licence* ticket, manager approval, 2 business days |
| Developer tools | Docker Desktop, VS Code, Git, Python, Node.js, open-source libraries on the approved list | Company Portal (*Developer* section), immediate |
| SaaS / cloud | New web applications, AI tools, vendor portals that store company data | *Software / New vendor* ticket, security review 2-3 weeks |

## Security review for new software
Any software or SaaS that stores Northwind data outside Microsoft 365 or the TMS goes through a security and
data protection review: the vendor's security questionnaire, data location, single sign-on support and
the data processing agreement. Tools that process Confidential data must keep it in the EU. Free tiers of
SaaS products count as new vendors and need the same review.

## Local administrator rights
Temporary admin rights are granted for 7 days through the *Temporary Admin* self-service in the Company
Portal; a reason is required and the grant is logged. Permanent admin rights are limited to engineers with
a documented need and are reviewed quarterly. Installing software with admin rights does not make it
approved; unapproved software may be removed during compliance scans.

## Licence management
Licences are assigned to a person, not a device. When you change roles or leave a project, release the
licence in the Company Portal so the department stops paying. Unused licences (no login for 60 days) are
reclaimed automatically after a warning e-mail. Costs are charged to the cost centre of the user.

## Frequently asked questions
- **Can I use a browser extension?** Extensions from the approved list install without a ticket; others
  need a *Software / Licence* ticket.
- **Is a personal ChatGPT or Copilot account allowed for work?** No. Use the approved internal assistants
  or request the enterprise version through *Software / New vendor*.
- **My licence request has been open for a week.** Check whether your manager approved it in ServiceHub;
  most delays are pending approvals.
