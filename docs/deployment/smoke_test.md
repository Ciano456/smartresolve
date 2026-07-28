# Production Smoke Test

Record the date, deployment identifier, tester, result, and evidence link for each step.

1. Open `/health/` and confirm `200` with `{"status": "healthy"}`.
2. Open the login page over HTTPS and confirm no redirect loop.
3. Confirm an invalid login shows the generic error and creates an audit event.
4. Log in as a synthetic Submitter and create a ticket.
5. Add a public comment and valid text attachment.
6. Confirm another Submitter cannot access the ticket or attachment.
7. Log in as Support Staff and assign, prioritise, comment, and resolve the ticket.
8. Confirm the submitter can see public updates but not internal notes.
9. Confirm Admin can manage users/lookups and view the audit log.
10. Open the dashboard and confirm charts and static assets load.
11. Export CSV and confirm headers/content are correct.
12. Confirm the expected notification event and test email delivery.
13. Redeploy without data changes.
14. Confirm the ticket, audit entries, and attachment persist.
15. Review Railway logs for errors or exposed credentials.
