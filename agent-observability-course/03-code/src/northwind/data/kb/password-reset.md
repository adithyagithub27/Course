---
id: KB-002
title: Password reset and account lockout
owner: IT Service Desk
tags: [password, account, lockout, okta, mfa]
updated: 2026-09-01
---
# Password reset and account lockout

## Self-service reset
Go to `okta.northwind.example/reset` and follow the prompts. You need your registered
phone or Okta Verify to confirm identity. Passwords must have 14+ characters and cannot
reuse any of your last 10 passwords.

## Reset through Atlas or the service desk
Atlas can reset a password **only after identity verification**: it will ask for your
employee ID (format `NW-12345`) and send a one-time code to your registered manager
or phone. Atlas never reveals or e-mails a password; you receive a temporary password
by SMS and must change it at next login.

## Lockout
Accounts lock after 8 failed attempts for 30 minutes. Repeated lockouts are usually
caused by an old password saved in a mail client or mobile device; update those first.

## Shared and service accounts
Shared mailbox and service account passwords are managed by the owning team in the
vault (`vault.northwind.example`). The service desk cannot reset them.

## Password rules in detail
Passwords must be at least 14 characters and may not contain your username, the word "northwind" or a
password you used in the last 10 changes. There is no forced expiry as long as MFA is enrolled; accounts
without MFA must change their password every 90 days. Passphrases such as four unrelated words are
recommended and are accepted with spaces. Passwords are checked against a list of known breached
passwords and rejected if they appear on it.

## Multi-factor authentication
Okta Verify (push notification) is the standard factor. A hardware key (YubiKey) is available on request
for administrators and for employees who cannot use a smartphone at work, for example in the cold store.
SMS codes are a fallback for enrolment only. If you get a new phone, re-enrol Okta Verify from a laptop
that is already signed in before wiping the old phone; otherwise the service desk must reset your MFA,
which requires a video call with a photo ID.

## Step-by-step self-service reset
1. Go to `okta.northwind.example/reset` from any device.
2. Enter your Northwind username.
3. Choose *Send push* (Okta Verify) or *Text me* (only if SMS is enrolled).
4. Approve or enter the code, then set a new password that meets the rules above.
5. Sign out and back in on all devices; saved passwords in browsers and mail apps must be updated.

## Frequently asked questions
- **How long does a reset take to propagate?** Up to 15 minutes for Wi-Fi and the VPN; immediately for
  web applications.
- **Atlas reset my password but I did not receive an SMS.** Check that your phone number in Workday is
  current. The service desk can resend once identity is confirmed.
- **Can my manager reset my password?** No. Only you (self-service) or the service desk after verification.
- **My account locks again minutes after I unlock it.** An old password is cached somewhere: a phone
  mail client, a saved Wi-Fi profile, a scheduled task on a shared computer or a mapped network drive.
  Update or remove those first.
- **I am a new joiner and the activation link expired.** Ask your manager to request a new activation
  link in ServiceHub; links are valid for 7 days.

## What the service desk will never do
Nobody at Northwind will ask you for your password by e-mail, chat or phone. If you are asked, report it
with the *Report Phish* button and call extension 4444.
