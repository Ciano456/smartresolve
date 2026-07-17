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

- Full local pre-deployment suite: 196 tests passed on 17 July 2026.
- Django system check: no issues.
- Migration consistency check: no changes detected.
- Production deployment checks still report development-setting warnings; these are
  retained for issue #25 rather than falsely marked complete.

## Current Deliverable Status

Security hardening was completed and merged through PR #43. Live deployment, formal
UAT, manual screenshots, user feedback, and final demo evidence remain outstanding
under issues #25 and #26.

## Railway Preparation

The codebase now separates shared, development, and production settings. Production
requires PostgreSQL, Redis, a strong secret key, and an explicit Railway/allowed host.
It enables HTTPS redirect, secure cookies, HSTS, WhiteNoise static serving, persistent
media configuration, and structured console logging. `railway.json` defines build,
migration, Gunicorn, restart, and health-check behaviour.

Operational runbooks now cover Railway setup, environment variables, deployment,
release, rollback, backup/restore, and smoke testing. UAT scripts, feedback forms,
screenshot requirements, a demo script, and known limitations are prepared without
claiming results that require a live service.

Issue #25 must remain open until the Railway services are provisioned and live
PostgreSQL, Redis, HTTPS, media persistence, Graph delivery, backup, and smoke-test
evidence are captured. Issue #26 remains open until three genuine UAT participants
complete the prepared script.
