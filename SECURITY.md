# SmartResolve Security Controls

## Implemented controls

- Django authentication with explicit Admin, Support Staff and Submitter role checks.
- Object-level checks protect submitter tickets and attachment downloads.
- Failed logins, rate-limited logins, access denials, blocked uploads and important
  ticket changes are recorded in the audit log.
- Login throttling uses a SHA-256 cache key derived from the normalised email and
  direct client address. Raw client addresses are not stored in the cache key.
- Attachment uploads enforce an extension allowlist, a 5 MB size limit and basic
  file-content checks. Rejected files are not stored.
- CSRF middleware and Django password validation are enabled.

## Login throttle configuration

Set these environment variables to positive integers:

```env
LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_SECONDS=900
LOGIN_RATE_LIMIT_BLOCK_SECONDS=900
```

Development uses Django's local-memory cache. Production should use a shared cache
such as Redis when more than one application process or instance is deployed.

## Deferred infrastructure controls

- Configure trusted proxy headers before using forwarded client addresses.
- Add reverse-proxy or platform-level request throttling.
- Add antivirus or malware scanning for uploaded files.
- Add central log collection, alerting and retention policies.
- Add a security dashboard if operational monitoring requires one.

## Verification

```text
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate
.venv/bin/pytest accounts/tests.py tickets/tests.py admin_portal/tests/test_views.py
.venv/bin/pytest
.venv/bin/python manage.py check --deploy
```

The deployment check is expected to report development-setting warnings until the
production configuration work tracked separately from security issue #24 is done.
