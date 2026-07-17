# Sprint 8 Write-Up

Sprint 8 covers security hardening, production readiness, UAT, and final evidence.
The security-hardening work tracked in GitHub issue #24 is complete in the current
feature work and awaits CI/merge confirmation.

Sensitive account, admin, dashboard, ticket, comment, attachment, and workflow views
were reviewed for authentication, role enforcement, and object-level ticket access.
Tests cover anonymous users, incorrect roles, unrelated submitters, and protected
attachment access.

Audit coverage now includes failed and rate-limited login attempts, access denials,
blocked uploads, admin user changes, ticket creation, assignment, priority/status
changes, comments, resolution notes, resolution, and cancellation. Audit persistence
is isolated behind a helper so an audit-write failure is logged without masking the
underlying user operation.

Suspicious login activity is controlled by a cache-backed throttle keyed by a SHA-256
digest of normalised email and the direct client address. Attempt thresholds, the
failure window, and the block duration are configurable through environment variables.
A shared production cache and trusted proxy configuration are deferred to deployment.

Attachment validation now checks an extension allowlist, a 5 MB limit, basic binary
signatures, and UTF-8/null-byte rules for text files. Rejected suspicious uploads are
audited and are not stored. Antivirus scanning remains an infrastructure enhancement.

## Verification

- Full local suite: 186 tests passed on 17 July 2026.
- Django system check: no issues.
- Migration consistency check: no changes detected.
- Production deployment checks still report development-setting warnings; these are
  retained for issue #25 rather than falsely marked complete.

## Current Deliverable Status

Security hardening is complete subject to PR CI and merge. Production configuration,
deployment checklists, formal UAT, manual screenshots, user feedback, and final demo
evidence remain outstanding under issues #25 and #26.
