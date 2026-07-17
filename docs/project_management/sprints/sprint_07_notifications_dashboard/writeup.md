# Sprint 7 Write-Up

Sprint 7 made SmartResolve operationally useful through Microsoft Graph email
notifications, richer dashboard reporting, and authorised CSV export.

The `notifications` app provides a central `NotificationService`, a Graph client,
reusable text and HTML templates, and a `NotificationEvent` record for sent, failed,
or skipped delivery attempts. Graph-specific configuration and failures are isolated
from the ticket workflow, and tests mock the external HTTP boundary.

Ticket triggers now cover creation, assignment, status changes, public comments,
resolution, and cancellation. Recipient selection avoids duplicate delivery and
does not send public-comment notifications back to the comment author. Internal
comments do not trigger public notifications.

The staff/admin dashboard now reports total, open, and resolved tickets, percentages,
average resolution time, recent tickets, status/priority/type/system breakdowns,
assigned workload, and a six-month resolution trend. Chart.js renders the datasets
provided by the dashboard service. Access is restricted to admins and support staff.

Authorised staff and admins can export ticket report data as CSV. The export includes
ticket number, title, type, system, priority, status, submitter, assignee, creation,
update, and closure fields. Formula-like spreadsheet values are neutralised to reduce
CSV injection risk. Permission, headers, content, and sanitisation are tested.

## Deliverable Status

Sprint 7 is complete and merged. Microsoft Graph notification foundations and ticket
triggers, notification event records, dashboard KPIs/charts, and CSV export all have
automated coverage. PDF export remains an optional later enhancement.
