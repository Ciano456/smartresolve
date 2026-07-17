# Testing And Evaluation

## Automated Test Status

The final local issue #24 verification on 17 July 2026 completed with 186 passing
tests. The suite uses pytest, pytest-django, Django `TestCase`, the Django test
client, and targeted mocking at the Microsoft Graph boundary.

Implemented functional coverage includes:

- authentication, logout, role checks, and login throttling
- admin user, role, lookup, activation, and ticket management
- ticket creation, object-level visibility, comments, and attachments
- staff assignment, status, priority, notes, filtering, and pagination
- resolution and cancellation workflows
- protected attachment downloads and rejected upload validation
- Microsoft Graph client, notification service, event records, and ticket triggers
- dashboard permissions, KPIs, chart datasets, and CSV export
- audit events for login failures, throttling, access denials, uploads, and ticket actions

## Security Testing

Automated security tests confirm:

- wrong-role and anonymous users cannot access restricted areas
- submitters cannot access another submitter's tickets or attachments
- submitters cannot use staff status, assignment, priority, resolution, or note endpoints
- internal notes are hidden from submitter-facing views
- blocked, oversized, binary-text, and signature-mismatched uploads are rejected
- rejected suspicious uploads are audited and not stored
- repeated failed logins are rate limited using configurable thresholds
- malformed login requests fail safely
- CSV formula-like values are neutralised on export

Infrastructure controls deferred to deployment are documented in `SECURITY.md`.

## Performance Testing

The code uses pagination and `select_related`/`prefetch_related` on important list,
detail, dashboard, and export querysets. Functional tests cover pagination and
aggregates. Formal response-time targets, query-count budgets, load testing, and a
realistic production-sized dataset remain outstanding.

## AI Evaluation

AI classification and response suggestions are not implemented. No accuracy,
precision, recall, F1, or confusion-matrix evidence should be claimed until the AI
scope is implemented and evaluated against a labelled synthetic dataset.

## User Acceptance Testing

UAT remains outstanding. It must collect genuine feedback from at least three users
covering login, ticket submission, ticket tracking, staff workflow, dashboard use,
and overall clarity. Names should be anonymised in assessment evidence where needed.

## Remaining Evidence Pack

- GitHub CI result for the final security PR
- screenshots of key submitter, staff, admin, dashboard, and audit workflows
- sanitised notification event/log evidence
- sample CSV export
- deployment and smoke-test evidence after issue #25
- feedback from three UAT participants
- final demo script and known-limitations section
