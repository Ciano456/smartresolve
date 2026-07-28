# Sprint 5 Write-Up

Sprint 5 focuses on the submitter-facing ticket workflow. The goal is for normal users to log into SmartResolve, create a ticket, view their own tickets, open ticket details, add comments, and upload supporting attachments.

The current working project already includes much of this flow. A `TicketForm` exists for creating tickets, and the submitter ticket create view sets the logged-in user as the submitter and assigns the initial `OPEN` status. Ticket creation also records a `TicketHistory` entry so that the first lifecycle event is captured.

Submitters can access a `my_tickets` list that filters tickets to the current user, and a `my_ticket_detail` view that uses object-level filtering to prevent users from opening tickets submitted by someone else. This is an important security control for the project because ticket data may contain sensitive business or personal information.

Comment and attachment flows are also present. Submitters can add comments to their own tickets and upload files. The attachment form validates file extensions and file size, supporting the project's secure file handling requirement.

Attachment handling was tightened after review. Attachment downloads now use protected application routes rather than exposing direct media URLs in the ticket detail pages. Access checks allow the ticket owner, support staff, and admins to download attachments while blocking unrelated submitters. The attachment size validation message was also corrected so it displays the human-readable `5 MB` limit instead of the raw byte value.

Testing was strengthened for this part of the sprint. The test suite now covers protected attachment download access for submitters, support staff, admins, anonymous users, and unrelated submitters. A regression test also confirms that oversized file uploads show the correct validation message.

Public versus internal comment visibility is fully enforced and covered by tests.
Submitter editing after ticket creation was intentionally left outside the MVP so the
record remains controlled through comments and the staff workflow.

## Current Deliverable Status

Sprint 5 is complete for the agreed submitter MVP. Ticket creation, submitter-only
visibility, comments, uploads, validation, and protected downloads are implemented
and tested.
