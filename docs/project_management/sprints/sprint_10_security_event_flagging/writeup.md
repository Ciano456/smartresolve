# Sprint 10 Write-Up

Sprint 10 completed FR-11 by extending the existing audit trail into a structured
security-event source. `AuditLog` now records a nullable client IP address, a severity
of low, medium, high, or critical, and whether the event requires security review.
Existing records receive safe low and unflagged defaults.

Client IP extraction is shared by audit logging and login throttling. Direct request
addresses are used by default. Railway forwarding headers are considered only when
`TRUST_PROXY_HEADERS` is explicitly enabled, preventing an untrusted header from
silently replacing the direct address. Values are validated as IPv4 or IPv6 before
storage.

Severity policy is centralised in `admin_portal/security.py`. Ordinary failed logins
remain low and unflagged. Rate limiting and blocked uploads are high severity, while
role access denials are medium. AI security tickets create a related audit event after
prediction persistence. Ransomware, breach, compromised-account, and credential-theft
signals are critical; other strong security phrases are high; a model-only signal is
medium unless its confidence is at least 0.85.

The main challenge was preserving graceful behaviour. Audit logging remains an
observability feature and cannot be allowed to break login, ticket creation, or an
administrator action. The existing failure boundary was retained while adding IP and
severity metadata. Messages intentionally store only concise signal labels and never
passwords, tokens, attachment contents, or full ticket descriptions.

The resulting event data provides the foundation consumed by the Sprint 11 security
dashboard.

Verification completed with the integrated 243-test project suite, Ruff, Django
system checks, migration application, and migration consistency checks all passing.
