# Testing And Evaluation

## Automated Test Status

The latest local verification on 19 July 2026 completed with 226 passing
tests. The suite uses pytest, pytest-django, Django `TestCase`, the Django test client,
and targeted mocking at the Microsoft Graph boundary.

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
- production settings validation and database-aware health checks

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

FR8 AI-assisted categorisation and security triage are implemented as advisory
features with staff override and graceful manual fallback. The deterministic
development dataset contains 720 unique, balanced synthetic tickets across
Hardware, Software, Network, and Access. Its 60 independently written source
templates are evaluated with grouped five-fold cross-validation, so variations of
the same source template never appear in both training and validation. The 60-ticket
set used during refinement is retained as `tickets_evaluation.csv`. A second frozen
60-ticket holdout contains 15 newly authored examples per category and was hashed
before its initial frozen evaluation.

When category inference is unavailable, staff can create a manual category from the
ticket detail page. Keyword and security-model triage run independently, so a category
artifact outage does not suppress security review flags.

Logistic Regression and Multinomial Naive Bayes were compared using mean macro F1
across the same five folds. Logistic Regression was selected with 82.5% mean
cross-validation accuracy (standard deviation 6.9 percentage points) and 0.815 mean
macro F1 (standard deviation 0.076). Its aggregate out-of-fold Access recall was
85.0%, resolving the earlier Access/Software failure caused by insufficient template
variety. After model selection, it was refitted on all development data. It achieved
95.0% accuracy on the iterative evaluation set. On the separately frozen final
holdout it achieved 91.7% accuracy and 0.917 macro F1. Its five errors crossed
Hardware/Network, Hardware/Software, Network/Software, and Access/Hardware boundaries,
supporting the human-in-the-loop design.

The binary security classifier threshold was selected from out-of-fold development
probabilities to favour recall. It achieved 98.3% accuracy and 91.7% security recall
on the iterative evaluation set. On the frozen final holdout, the unchanged 0.55
threshold achieved 90.0% accuracy, 80.0% security precision, 66.7% security recall,
0.727 security F1, and 0.981 ROC-AUC. The existing narrow keyword rules did not recover
the four missed security cases. This is a remaining limitation rather than a reason
to tune against the final set. Full fold-level and aggregate metrics, confusion
matrices, errors, threshold candidates, dataset and artifact hashes, and dependency
versions are stored in `ml/artifacts/metrics.json`.

The approved hashes are also stored in `ml/data/dataset_hashes.json`. Training stops
before fitting or inference if any development, iterative evaluation, or final holdout
file differs from that manifest. Iterative and frozen metrics use separate keys in the
metrics report so post-refinement evidence cannot be mistaken for final evidence.

Limitations: both datasets remain synthetic. Fold accuracy ranges from 75.0% to
95.1%, and aggregate Hardware recall is 65.0%, showing that performance still varies
by unseen wording. The final holdout is independent but still contains only 60 tickets,
and its security recall is below the development objective. These figures do not
establish production performance; future work should improve security-language
coverage using new development data and then evaluate on another untouched set of
consented, anonymised organisational tickets.

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

## Deployment Configuration Testing

Automated tests load production settings in isolated subprocesses. They confirm that
valid Railway-style configuration imports successfully and that missing PostgreSQL,
Redis, or a strong signing key causes a clear startup failure. Health tests cover the
healthy database path, generic unavailable response, and rejection of POST requests.
