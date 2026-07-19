# Sprint 11 Plan: Security Metrics Dashboard

## Goal

Complete FR-10 with a read-only administrator dashboard backed by the structured
events created in Sprint 10 and the existing AI ticket predictions.

## Scope

- Add an admin-only `/admin_portal/security/` route.
- Show flagged ticket and audit-event totals.
- Show low, medium, high, and critical event counts.
- List recent flagged tickets and recent flagged audit events.
- Filter recent events by severity.
- Show keyword counts and a six-month event trend.
- Add admin navigation and responsive Tailwind presentation.
- Add access, aggregation, empty-state, filter, and query-bound tests.

## Design

The page follows the existing SmartResolve shell and dashboard grid. A dark review
header separates security reporting from operational ticket reporting, while rose,
orange, amber, and slate communicate severity consistently. The page uses semantic
sections, tables, labelled controls, accessible empty states, and safe JSON chart data.

## Done Criteria

- [x] Admin-only view and URL exist.
- [x] Non-admin authenticated users receive HTTP 403.
- [x] Metrics and recent lists are query optimised.
- [x] Severity and trend charts render from service data.
- [x] Keyword and severity filtering are implemented.
- [x] Automated dashboard tests pass.
- [ ] Screenshot captured from an authenticated local or deployed session.
