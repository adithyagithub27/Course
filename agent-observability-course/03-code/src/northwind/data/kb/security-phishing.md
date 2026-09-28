---
id: KB-006
title: Security: phishing, suspicious e-mail and incident reporting
owner: Information Security
tags: [security, phishing, incident, report, malware]
updated: 2026-09-10
---
# Security: phishing and incident reporting

## Suspicious e-mail
Use the **Report Phish** button in Outlook. Do not forward the message. The security team replies
within one business day. If you clicked a link or entered your password, call the security hotline
(extension 4444) immediately and change your password.

## Lost badge or device
Report within 24 hours through Atlas or the service desk so access can be revoked.

## Data handling
Customer shipment data is *Confidential*. Never paste shipment manifests, customer names or
addresses into external tools, including public AI assistants. Internal tools such as Atlas
mask personal data in their logs.

## Incident reporting
Any suspected breach (unusual login alerts, unknown devices in Okta, ransomware notes) is a
**P1** security incident: call 4444, then open a ticket with category *Security / Incident*.

## How to recognise phishing
Typical signs: urgency ("your account will be closed today"), requests for passwords or gift cards, sender
addresses that look almost right (`northwind-logistics.co` instead of `northwind.example`), unexpected
invoices or shipment notifications with attachments, and links whose preview does not match the text.
Northwind never sends password reset links by e-mail unless you requested one in the last 15 minutes, and
never asks for MFA codes.

## Reporting
Use *Report Phish* in Outlook (desktop, web and mobile). The message is moved to a quarantine folder and
the Security Operations team reviews it within one business day; you receive a short verdict. If you
clicked a link and entered credentials, change your password immediately at `okta.northwind.example/reset`
and call extension 4444; do not wait for the verdict. Suspicious phone calls or texts (smishing) are
reported by forwarding a screenshot to `security@northwind.example`.

## Devices, badges and clean desk
Lock your screen when you leave your desk (Windows key + L / Control-Command-Q). Report lost badges within
24 hours so they can be deactivated; a temporary badge is issued at reception. Visitors must be escorted in
warehouses and server rooms. Printed documents with customer data go into the locked shredding bins.

## Data classification
- **Public**: marketing material, published tariffs.
- **Internal**: policies, org charts, most e-mail.
- **Confidential**: customer shipment data, contracts, HR and payroll records, source code.
- **Restricted**: credentials, encryption keys, security incident details.
Confidential and Restricted data may only be stored in approved systems (Microsoft 365, the TMS, Workday,
the vault) and never in personal cloud storage or public AI tools.

## Incident severity and response
| Severity | Examples | Action |
|---|---|---|
| P1 | Ransomware, confirmed data breach, compromised admin account | Call 4444 immediately, then ticket *Security / Incident* |
| P2 | Credentials entered on a phishing page, lost unencrypted device | Ticket within 1 hour, call if outside office hours |
| P3 | Suspicious e-mail not clicked, policy questions | Report Phish button or ticket |

## Frequently asked questions
- **I opened an attachment but nothing happened.** Still report it; malware often runs silently.
- **Can I use ChatGPT or similar tools for work?** Only the approved internal assistants (such as Atlas) for
  Confidential data; public tools may be used for Public and Internal information only.
