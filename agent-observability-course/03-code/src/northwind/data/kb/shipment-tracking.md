---
id: KB-011
title: Internal shipment tracking and delivery exceptions
owner: Logistics Operations
tags: [shipment, tracking, delivery, exception, tms, customer]
updated: 2026-09-05
---
# Internal shipment tracking and delivery exceptions

Employees can check the status of any shipment by its tracking ID (format `SHP-` followed by
6 to 8 digits) through Atlas or the TMS. Statuses:

| Status | Meaning |
|---|---|
| created | Order booked, not yet collected |
| in_transit | Collected and moving between hubs |
| at_hub | Waiting at a sorting hub |
| out_for_delivery | On the last-mile vehicle |
| delivered | Proof of delivery captured |
| exception | Customs hold, damaged, address issue or refused |

## Exceptions
Customer-facing staff should not promise a new delivery date until the exception owner (the
hub listed on the record) updates the ETA. Damaged goods require photos in the TMS within 24 hours.

## Escalation
Shipments in *exception* for more than 48 hours are escalated automatically to the regional
operations lead. Urgent customer complaints go to the duty manager (extension 5100).

## Where tracking data comes from
Statuses are updated by hub scans, driver apps and carrier feeds. A shipment normally moves *created →
in_transit → at_hub → out_for_delivery → delivered* within one to three business days in Western Europe
and three to five days for Eastern Europe and cross-border. A status older than 12 hours during a working
day usually means a missed scan rather than a lost shipment; the hub team can confirm on request.

## Exception reasons and owners
| Reason | Meaning | Owner | Typical resolution |
|---|---|---|---|
| customs_hold | Documents missing or inspection | Customs desk at the border hub | 1-3 business days after documents are provided |
| address_issue | Address incomplete or recipient unknown | Last-mile hub | Customer service confirms the address with the customer |
| damaged | Damage found at a hub | Hub quality team | Photos in the TMS within 24 hours, claim opened |
| refused | Recipient refused delivery | Customer service | Return or redelivery per customer instruction |
| weather / strike | Regional disruption | Regional operations lead | Bulletins on the intranet |

## What customer-facing staff may say
Give the current status, the owning hub and the ETA shown in the TMS. Do not promise a new date for an
exception until the owner updates the ETA. Do not share other customers' shipment details or driver names.
For complaints about repeated delays, open a *Customer escalation* in the TMS so the account manager is
informed.

## Escalation ladder
1. Hub team for the owning hub (contact in the TMS record).
2. Regional operations lead after 48 hours in exception (automatic).
3. Duty manager on extension 5100 for urgent customer complaints outside office hours.
4. Account manager for contractual questions or claims.

## Frequently asked questions
- **The tracking id has seven digits; is that valid?** Yes, SHP ids have six to eight digits.
- **The customer says it was delivered but the status is out_for_delivery.** Driver apps sync when back
  in coverage; wait two hours, then ask the hub to confirm proof of delivery.
- **Can Atlas open a ticket for a shipment exception?** Yes, category *Other* with the tracking id in the
  summary; the hub is notified through the ticket integration.
