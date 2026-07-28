# Sprint 8 Checklist

## Security Hardening

- [x] CSRF middleware enabled.
- [x] File upload allowlist, size, and basic content validation exist.
- [x] Role decorators exist.
- [x] Object-level ticket and attachment access exists for submitter views.
- [x] Permission review across sensitive views.
- [x] Failed and rate-limited login logging.
- [x] Access denial logging.
- [x] Audit log extended for important security and ticket events.
- [x] Security dashboard summary delivered in Sprint 11.
- [x] Configurable cache-backed repeated-login throttle.
- [ ] Backup/restore plan.
- [ ] GDPR/data minimisation review.

## Production Readiness

- [x] Settings split for base/development/production.
- [x] Production environment variable list.
- [x] WhiteNoise static deployment process.
- [x] Railway persistent media-volume plan.
- [x] Gunicorn setup.
- [x] Railway proxy/TLS handling configured.
- [x] `collectstatic` build process.
- [x] Console logging configuration.
- [~] Railway log review prepared; live error evidence pending.
- [x] Manual deployment checklist.
- [x] Release and rollback checklists.

## UAT And Evidence

- [x] UAT script and feedback form prepared.
- [x] Smoke test checklist prepared.
- [ ] User feedback from three testers.
- [~] RTM implementation/test statuses updated; manual evidence remains.
- [ ] Final screenshot/log evidence pack.
