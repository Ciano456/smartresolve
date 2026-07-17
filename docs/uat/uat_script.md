# User Acceptance Test Script

Use synthetic accounts and tickets. Record pass/fail, comments, date, tester code, and
an evidence reference. Do not place real passwords or personal data in this document.

## Submitter Scenario

1. Sign in with the supplied synthetic Submitter account.
2. Create a ticket with type, system, priority, title, and description.
3. Find the ticket in My Tickets.
4. Add a public comment and permitted attachment.
5. Confirm current status and public updates are understandable.
6. Attempt an unsupported upload and confirm it is rejected clearly.
7. Sign out.

Expected result: the Submitter can manage their own conversation and attachments but
cannot access staff/admin functions or another submitter's ticket.

## Support Staff Scenario

1. Sign in as Support Staff.
2. Find the new ticket using queue filters.
3. Assign it, change priority/status, and add an internal note.
4. Add a public response.
5. Resolve it with a resolution summary.
6. Review ticket history and export the dashboard CSV.
7. Sign out.

Expected result: the complete staff workflow succeeds, history is understandable, and
internal notes remain staff-only.

## Administrator Scenario

1. Sign in as Admin.
2. Review dashboard KPIs and charts.
3. Create or edit a synthetic user and role.
4. Review lookup management without changing required workflow codes.
5. Review all tickets and the audit log.
6. Confirm denied login/upload events are visible.
7. Sign out.

Expected result: administrative operations are restricted, auditable, and clear.

## Completion

Each of at least three participants completes the relevant scenario and the feedback
form. A failed step becomes a defect or known limitation; it must not be silently
marked as passed.
