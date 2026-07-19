# SmartResolve Security Controls

## Implemented controls

- Django authentication with explicit Admin, Support Staff and Submitter role checks.
- Object-level checks protect submitter tickets and attachment downloads.
- Failed logins, rate-limited logins, access denials, blocked uploads and important
  ticket changes are recorded with severity, flagged state, and a validated client
  address where available.
- Login throttling uses a SHA-256 cache key derived from the normalised email and
  direct client address. Raw client addresses are not stored in the cache key.
- Attachment uploads enforce an extension allowlist, a 5 MB size limit and basic
  file-content checks. Rejected files are not stored.
- CSRF middleware and Django password validation are enabled.
- Administrators have a read-only security dashboard for flagged tickets, event
  severity, keyword signals, and recent trends.

## Security event reporting

Configured suspicious events are classified as low, medium, high, or critical.
Rate limiting, access denials, blocked uploads, and AI security-ticket signals are
flagged for administrator review. Security flags do not automatically change ticket
priority or replace a human decision.

`REMOTE_ADDR` is used for audit and throttle identification by default. Set
`TRUST_PROXY_HEADERS=True` only behind Railway or another trusted reverse proxy that
controls `X-Forwarded-For`. The first valid forwarded address is then treated as the
original client address.

## Login throttle configuration

Set these environment variables to positive integers:

```env
LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_SECONDS=900
LOGIN_RATE_LIMIT_BLOCK_SECONDS=900
```

Development uses Django's local-memory cache. Production requires Railway Redis so
all Gunicorn workers share the same throttle state.

Production settings also enforce HTTPS redirection, secure session/CSRF cookies,
HSTS, explicit allowed hosts and trusted CSRF origins, PostgreSQL SSL, and a strong
environment-provided secret key.

## Deferred infrastructure controls

- Add reverse-proxy or platform-level request throttling.
- Add antivirus or malware scanning for uploaded files.
- Add central log collection, alerting and retention policies.

## Verification

```text
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate
.venv/bin/pytest accounts/tests.py tickets/tests.py admin_portal/tests
.venv/bin/pytest
.venv/bin/python manage.py check --deploy
```

The production deployment check intentionally leaves HSTS browser-preload submission
disabled because SmartResolve does not control the parent `railway.app` domain.
