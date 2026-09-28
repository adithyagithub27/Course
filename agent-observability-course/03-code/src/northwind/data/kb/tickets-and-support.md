---
id: KB-012
title: How IT and HR tickets work (priorities and SLAs)
owner: IT Service Desk
tags: [ticket, sla, priority, servicehub, support hours]
updated: 2026-04-22
---
# How IT and HR tickets work

Tickets are created in ServiceHub, by e-mail to `helpdesk@northwind.example`, or by asking Atlas.
Ticket IDs look like `TCK-` followed by 6 digits.

## Priorities and response times
| Priority | Example | First response | Resolution target |
|---|---|---|---|
| P1 | Site down, security breach | 15 min | 4 h |
| P2 | Team blocked, payroll error | 1 h | 1 business day |
| P3 | One person blocked | 4 h | 3 business days |
| P4 | Question, request | 1 business day | 5 business days |

Support hours are 07:00-19:00 CET Monday to Friday. P1 incidents are handled 24/7 through the
on-call rota; call extension 4000.

## Status meanings
*open* → *in_progress* → *waiting_on_user* → *resolved* → *closed*. A ticket in *waiting_on_user*
for 5 business days closes automatically.

## Ways to open a ticket
- **ServiceHub** (preferred): choose a category and answer the guided questions; attachments up to 25 MB.
- **Atlas**: ask in chat; Atlas creates the ticket with the category and priority and gives you the id.
- **E-mail** to `helpdesk@northwind.example`: creates a P4 ticket; the subject becomes the summary.
- **Phone** extension 4000: for P1 and P2 issues, or when you cannot sign in at all.

## Categories
Hardware, Software, Network, Access, HR, Payroll, Security, Other. HR and Payroll tickets are only visible
to the HR team and the requester. Security tickets are visible to the security team only.

## How priority is set
The requester proposes a priority; the service desk may change it using the impact and urgency matrix.
Site-wide outages, security incidents and payroll runs at risk are P1. A whole team unable to work is P2.
One person blocked is P3. Questions, requests and improvements are P4. Raising a priority artificially
delays other tickets; use P1 and P2 only when the definitions apply.

## Ticket lifecycle
*open* (waiting for the desk) → *in_progress* (an engineer is working on it) → *waiting_on_user* (we need
information from you; auto-closes after 5 business days without a reply) → *resolved* (fix applied; reply
within 3 business days if it did not help) → *closed*. Reopen a closed ticket by replying to it within 14
days; after that, open a new one and reference the old id.

## Service levels
| Priority | First response | Resolution target | Hours |
|---|---|---|---|
| P1 | 15 minutes | 4 hours | 24/7 |
| P2 | 1 hour | 1 business day | 07:00-19:00 CET, on-call outside |
| P3 | 4 hours | 3 business days | 07:00-19:00 CET |
| P4 | 1 business day | 5 business days | 07:00-19:00 CET |

## Frequently asked questions
- **Can I see my colleague's ticket?** Only if they added you as a watcher.
- **How do I escalate?** Reply on the ticket with "escalate"; the queue lead reviews within 4 business hours.
  For P1 and P2 call extension 4000.
- **Can I open a ticket for someone else?** Yes; set them as the *affected user* in ServiceHub.
