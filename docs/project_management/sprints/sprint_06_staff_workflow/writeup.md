# Sprint 6 Write-Up

Sprint 6 is intended to turn SmartResolve from a submitter ticket form into a usable support workflow for technicians and administrators.

The current project now includes most of this workflow. Support staff and admins can access an all-ticket list, open ticket details, and update ticket status. Status changes are protected by role decorators, create a `TicketHistory` entry, and use the model-level `closed_at` behaviour when a closed status is selected. Tests confirm that support staff can update status, admins can close tickets, invalid status IDs are rejected, and submitters cannot use the staff update endpoint.

Assignment and priority management have also been implemented. Staff and admins can assign tickets to support staff, unassign tickets, and update ticket priority from the staff ticket detail page. Assignment and priority changes create history records only when the value actually changes, which avoids duplicate audit noise. Submitters are blocked from these staff endpoints, and invalid assignee or priority values are rejected.

The staff detail page now supports both public comments and internal notes in the same comments section. Internal notes are labelled on the staff view and remain hidden from submitters, while public comments remain visible in the normal ticket conversation. This keeps the current UI simple while still meeting the need for technician-only working notes.

Filtering was completed for the staff ticket queue. Staff can filter by status, priority, type, system, requester, assigned user, and created date range. Invalid filter values are ignored safely rather than causing errors. The queue is also paginated, with active filters preserved when moving between pages, so the staff view remains usable once the database contains more tickets.

Ticket history is visible on the staff detail page. Staff can see lifecycle and workflow changes such as status updates, assignment changes, and priority changes in newest-first order. Submitter-facing ticket detail pages do not show the staff history section.

A dedicated resolve and cancel workflow was then added to complete the operational flow. Staff and admins can resolve a ticket only by providing a required resolution summary. Resolving a ticket moves it to the closed status, stores the resolution summary on the ticket, creates a public ticket comment, records ticket history, and sets the close timestamp through the model lifecycle logic. The generic status dropdown no longer allows closed-status transitions, so closed tickets must go through the workflow that captures the required note.

Cancellation was also included in Sprint 6. A `Cancelled` ticket status is seeded through migration and is treated as a closed status. Staff and admins can cancel a ticket only by entering a cancellation reason. Cancelling stores the reason on the ticket, clears any resolution summary, creates a public cancellation comment, records ticket history, and sets the close timestamp. Submitters cannot use either the resolve or cancel endpoints.

A review cleanup pass was completed before moving further into Sprint 6. Lookup `code` values are now locked after creation in the admin portal because workflow logic depends on stable codes such as `OPEN`. The admin all-ticket list was paginated as well, and the attachment size validation message was corrected to show the proper `5 MB` limit. Regression tests were added for these fixes.

## Current Deliverable Status

Sprint 6 is complete and merged for the planned MVP workflow. Staff can triage,
assign, filter, update status and priority, add public and internal notes, resolve
tickets with a required summary, cancel tickets with a required reason, and review
history. Automated tests cover the happy paths, validation, and permission failures.
