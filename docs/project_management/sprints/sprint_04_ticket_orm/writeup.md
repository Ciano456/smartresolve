# Sprint 4 Write-Up

Sprint 4 focused on building the full ticket database layer for SmartResolve. The goal of this sprint was to create a stable ORM foundation before moving into user-facing ticket workflows. This included designing ticket-related models, defining relationships, introducing ticket number generation, registering models in Django admin, seeding lookup data, and validating the data layer with tests.

The first part of the sprint was the design and implementation of the ticket master data models. Four lookup models were created: `TicketType`, `TicketSystem`, `TicketPriority`, and `TicketStatus`. These models support stable reference data across the application and include fields such as `name`, `code`, `description`, `is_active`, and `sort_order`. `TicketStatus` also includes an `is_closed` flag to support ticket lifecycle logic.

The central `Ticket` model was then implemented. It stores core ticket information including `ticket_number`, `title`, `description`, `submitter`, `assigned_to`, `ticket_type`, `ticket_system`, `ticket_priority`, `ticket_status`, `created_at`, `updated_at`, and `closed_at`. Lookup relationships and submitter use `PROTECT` to preserve business record integrity, while `assigned_to` uses `SET_NULL` so tickets remain valid if a support user is removed. Logic was added to automatically generate ticket numbers and update `closed_at` when a ticket moves into or out of a closed status.

Three supporting child models were added: `TicketComment`, `TicketAttachment`, and `TicketHistory`. These extend the ticket record with conversation, file uploads, and change tracking.

Django admin registration was completed for all ticket-related models, providing a back-office view of the ticket ORM. A data migration seeds baseline ticket types, systems, priorities, and statuses, ensuring each environment starts with required reference data.

Model tests verify ticket creation, ticket number generation, status transitions, closure handling, assignment, deletion behavior, and child-record cascade behavior.

## Deliverable

By the end of Sprint 4, SmartResolve had a stable ticket ORM, seeded master data, working migrations, admin visibility, and passing model-level tests.
