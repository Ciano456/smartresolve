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
- [ ] Security dashboard summary.
- [x] Configurable cache-backed repeated-login throttle.
- [ ] Backup/restore plan.
- [ ] GDPR/data minimisation review.

## Production Readiness

- [ ] Settings split for base/dev/prod.
- [ ] Production environment variable list.
- [ ] Static files deployment process.
- [ ] Media storage plan.
- [ ] Gunicorn/Uvicorn setup.
- [ ] Reverse proxy plan if used.
- [ ] `collectstatic` process.
- [ ] Logging configuration.
- [ ] Error reporting.
- [ ] Manual deployment checklist.
- [ ] Release checklist.

## UAT And Evidence

- [ ] UAT setup.
- [ ] Smoke test checklist.
- [ ] User feedback from three testers.
- [~] RTM implementation/test statuses updated; manual evidence remains.
- [ ] Final screenshot/log evidence pack.
