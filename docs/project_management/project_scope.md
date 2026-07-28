# Project Scope

## Core Purpose

SmartResolve is an internal IT support platform for managing:

- incidents
- service requests
- change requests
- access requests
- report and data requests

The system should replace spreadsheet and email-based tracking with a centralised, secure ticket workflow.

## Final Product Scope

The final product should include:

- secure authentication
- role-based access control
- ticket tracking
- user and admin management
- ticket comments and attachments
- audit logging
- dashboard reporting
- email notifications
- secure file upload validation
- internal deployment readiness
- AI-assisted ticket categorisation
- AI-assisted response suggestions
- security monitoring for suspicious activity

## Security Focus

The project links directly to cyber security through:

- Django password hashing
- role checks before sensitive actions
- CSRF protection
- controlled file uploads
- audit logs for important actions
- suspicious activity monitoring
- GDPR-aware data minimisation
- synthetic data for demos and AI training where real data is not safe

## Current Implementation Snapshot

- Custom user model, login/logout/profile, and group-based roles are implemented.
- Admins can manage users, roles, lookup values, and all tickets from the portal.
- Submitters can create and follow their own tickets, comment, and use protected attachments.
- Staff can assign, prioritise, filter, comment, resolve, cancel, and review ticket history.
- Microsoft Graph notification delivery, templates, event records, and ticket triggers exist.
- Dashboard KPIs, charts, workload, trends, and authorised CSV export are implemented.
- Audit logging covers failed/rate-limited logins, denied access, blocked uploads,
  admin actions, and important ticket actions.
- Production deployment, formal UAT, final evidence, AI, and SLA rules remain future work.
