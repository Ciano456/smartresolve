# Release Checklist

- [ ] Target commit and PR are identified.
- [ ] CI and local test suite pass.
- [ ] Migration plan reviewed for destructive operations.
- [ ] PostgreSQL backup completed before schema changes.
- [ ] Media backup completed before storage changes.
- [ ] Environment variables reviewed without copying secrets into the issue or PR.
- [ ] Deployment window and expected brief volume-related downtime recorded.
- [ ] Deployment logs monitored.
- [ ] `/health/` returns `200` after deployment.
- [ ] Authentication and each role tested.
- [ ] Ticket create, update, resolve, cancel, dashboard, and CSV export tested.
- [ ] Upload and protected download tested.
- [ ] Notification event and delivery tested.
- [ ] Rollback commit/deployment identified.
- [ ] Known limitations updated.
- [ ] Release evidence linked to the RTM.
