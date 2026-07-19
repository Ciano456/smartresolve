# Sprint 11 Write-Up

Sprint 11 completed FR-10 with a dedicated read-only security dashboard for
administrators. It combines two evidence sources: AI ticket predictions requiring
security review and structured audit events flagged by the Sprint 10 policy.

The reporting service calculates flagged-ticket and event totals, severity counts,
recent records, security-keyword frequency, and a fixed six-month trend. Database
aggregation is used for counts and trends. Recent lists are bounded and load their
ticket, submitter, status, priority, and actor relationships with `select_related`.
Keyword parsing uses the 500 most recent flagged predictions, keeping the work
bounded as the audit history grows. Matched labels remain stored as concise text on
the prediction record.

The view remains thin and uses an extended `admin_required` decorator. Anonymous
users are redirected to login, authenticated support staff and submitters receive
HTTP 403, and administrators receive the dashboard. Existing admin routes retain
their previous redirect behaviour.

The interface continues the established SmartResolve visual system instead of adding
a separate theme. A dark review header and severity colours provide the primary
visual hierarchy. Responsive cards, charts, tables, a labelled severity filter, and
explicit empty states keep the page useful across desktop and smaller screens.

The dashboard does not claim to be automated monitoring. It gives administrators a
single place to review evidence, while central alert delivery, SIEM integration, and
formal retention policy remain future operational enhancements.

The final integrated project suite completed with 243 passing tests. Ruff, Django
system checks, migration application, migration consistency, and diff checks also
passed. Authenticated screenshot evidence remains pending. Safari opened the local
site, but macOS blocked automated keyboard control and Safari page scripting because
the required Accessibility and Apple Events permissions are disabled. Temporary
evidence records created for the attempt were removed afterward.
