# Final Demo Script

Target duration: 10-15 minutes. Use synthetic data prepared before the assessment.

1. **Purpose and architecture** — explain the spreadsheet/email problem, Django apps,
   PostgreSQL, Redis, Railway, Microsoft Graph, and persistent media storage.
2. **Authentication and roles** — demonstrate Submitter, Support Staff, and Admin
   navigation plus a denied-access audit event.
3. **Submitter workflow** — create a ticket, comment, upload, and show object-level
   isolation.
4. **Staff workflow** — filter, assign, prioritise, add internal/public notes, resolve,
   and show history.
5. **Admin workflow** — manage a synthetic user/lookup and review audit activity.
6. **Reporting** — show KPIs, charts, workload/trend data, and secure CSV export.
7. **Notifications** — show a sanitised event and test message delivered through Graph.
8. **Security** — explain CSRF, role/object checks, protected files, upload validation,
   login throttling, secure cookies, HSTS, audit events, and secret handling.
9. **Quality evidence** — show tests, CI, migration checks, `/health/`, and UAT summary.
10. **Limitations and future work** — cover deployment constraints, AI, SLA features,
    malware scanning, and monitoring without claiming unimplemented work.
