---
id: KB-001
title: VPN access and troubleshooting
owner: IT Service Desk
tags: [vpn, remote, network, globalprotect]
updated: 2026-08-12
---
# VPN access and troubleshooting

Northwind uses **GlobalProtect** for remote access. All employees with a managed
laptop can connect; contractors need a sponsor to request access through a ticket.

## Connecting
1. Open GlobalProtect from the system tray and enter portal `vpn.northwind.example`.
2. Sign in with your Northwind account and approve the push notification in Okta Verify.
3. The icon turns green when connected. Internal sites such as `hr.northwind.example` are then reachable.

## Common problems
- **"Gateway unreachable"**: check that your home router allows UDP 4501; switch to a phone hotspot to test.
- **Stuck at "Connecting"**: sign out of GlobalProtect, restart the laptop, try again. If it fails twice, open a ticket with category *Network / VPN*.
- **Slow VPN**: only intranet traffic goes through the tunnel (split tunnelling). Video calls should not use VPN.
- **MFA loop**: your Okta Verify device may be out of date; re-enrol at `okta.northwind.example/enroll`.

## Contractor access
Sponsors request access in ServiceHub → *Request contractor VPN*. Access expires after 90 days and can be renewed once.

## Requirements and supported platforms
GlobalProtect 6.x is pre-installed on all managed Windows and macOS laptops and updates through the
Company Portal. Managed iPhones and Android devices can install it from the corporate app store, but
mobile VPN is limited to e-mail, chat and the intranet. Personal devices are not supported: use the
managed browser (Island) for e-mail and chat instead. The client needs outbound UDP 4501 (preferred)
or TCP 443 (fallback) to `vpn.northwind.example`; hotel and airport networks that block UDP fall back
automatically but are noticeably slower.

## Step-by-step first connection
1. Sign in to the laptop with your Northwind account while on any internet connection.
2. Click the GlobalProtect globe in the system tray (Windows) or menu bar (macOS) and enter the portal
   `vpn.northwind.example`. The portal only needs to be typed once.
3. Enter your Northwind username (firstname.lastname) and password.
4. Approve the Okta Verify push on your phone. If you do not have Okta Verify yet, enrol first at
   `okta.northwind.example/enroll`; the VPN will not accept SMS codes.
5. Wait for the globe to turn green (up to 30 seconds on first connection while the gateway list loads).
6. Test with `https://hr.northwind.example`. If the page loads, you are connected.

## Frequently asked questions
- **Do I need the VPN for Microsoft 365, Slack or Zoom?** No. Those services are reachable directly and
  are excluded from the tunnel (split tunnelling). Connecting to the VPN for video calls makes them worse.
- **The client asks for a "gateway" and lists Rotterdam, Hamburg and Warsaw. Which one?** Choose *Best
  available*. Manual selection is only for troubleshooting with the service desk.
- **Can I stay connected all day?** Yes. Idle sessions disconnect after 12 hours and reconnect on the
  next use. There is no data cap.
- **Why does the VPN drop every ten minutes on my home network?** Usually the router's UDP timeout is
  too short. Enable "keep-alive" in the GlobalProtect settings or switch the router to TCP fallback.
  If it persists on a phone hotspot too, open a P3 ticket with category *Network / VPN* and attach the
  client logs (GlobalProtect menu → *Collect logs*).
- **Does the VPN work from China, Russia or Iran?** No. Traffic from sanctioned or restricted regions
  is blocked by policy. Travel to those countries requires a loaner laptop and a travel briefing from
  Information Security at least two weeks before departure.
- **I see "Your device does not meet compliance requirements".** The laptop is missing an update or the
  disk is not encrypted. Open the Company Portal, install pending updates, restart and try again.

## Contractors and partners
Contractors get VPN access only with a named Northwind sponsor. The sponsor submits *Request contractor
VPN* in ServiceHub with the contractor's company e-mail, the systems they need and the end date. Access
is granted for a maximum of 90 days and can be renewed once by the sponsor. Partner companies that need
permanent connectivity (for example carrier TMS integrations) are connected through a site-to-site
tunnel managed by Network Engineering, not through GlobalProtect.

## Contacts
Service desk: ServiceHub or extension 4000. Network Engineering (site-to-site, gateway capacity):
`network-eng@northwind.example`. Security questions about VPN logs: extension 4444.
