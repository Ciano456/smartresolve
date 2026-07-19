# Sprint 10 Plan: Security Event Flagging

## Goal

Complete FR-11 by turning configured suspicious activity into structured and
reportable security events. Audit records will capture a validated client address,
severity, and flagged state while remaining non-blocking for the original user action.

## Scope

- Add IP address, severity, and flagged fields to `AuditLog`.
- Add indexes for flagged and severity reporting by date.
- Centralise trusted proxy handling and severity policy.
- Capture request IP data at all audit call sites.
- Flag rate limiting, access denials, blocked uploads, and AI security tickets.
- Keep routine actions unflagged at low severity.
- Add automated coverage for IP handling, severity, and event creation.

## Security Decisions

- `REMOTE_ADDR` is the default source.
- Forwarded addresses are trusted only when `TRUST_PROXY_HEADERS` is enabled.
- Passwords, tokens, uploaded content, and other secrets are not stored in messages.
- Security flags request administrator review and do not change ticket priority.
- Audit persistence failure must not interrupt the original action.

## Done Criteria

- [x] Additive migration created.
- [x] IP extraction validates IPv4 and IPv6.
- [x] Suspicious actions receive deterministic severity and flags.
- [x] AI security ticket predictions create related audit events.
- [x] Existing login throttling uses the same client IP helper.
- [x] Focused tests pass.
