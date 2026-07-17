# Proposal Context

Source proposal:

`docs/Updated_Project_Proposal_Secure_IT_Support_Portal.docx`

## Proposal Title

Secure IT Support Portal with Audit Logging, Security Monitoring and AI-Assisted Ticket Triage

## Core Proposal Summary

The project proposes a secure internal IT support portal for logging, tracking, and managing support requests. It goes beyond a basic helpdesk by including cyber security controls such as authentication, role-based access control, audit logging, secure file handling, suspicious activity monitoring, and AI-assisted triage.

## Key Proposal Themes

- Replace spreadsheets and shared inboxes with a centralised support portal.
- Improve visibility over ticket ownership, status, and history.
- Apply secure system design from the beginning.
- Record important user, admin, and ticket actions.
- Detect suspicious activity using rule-based monitoring.
- Use AI to assist with ticket classification and security triage.
- Use dashboards to show ticket and security metrics.
- Avoid using real sensitive data in the submitted project.

## Proposal Technical Approach

The proposal identifies Django as the main framework because it provides:

- MVT structure
- authentication
- ORM
- admin panel
- CSRF protection
- password hashing
- form validation support

Additional planned technologies:

- Chart.js for visual reporting
- Microsoft Graph for email notifications where possible
- scikit-learn for AI ticket classification
- SQLite during development
- MySQL or another production database later

## Proposal Security Features

Planned security features include:

- authentication
- role-based access control
- object-level permission checks
- secure form handling
- audit logging
- file upload validation
- suspicious activity detection
- security dashboard

Example security events:

- successful login
- failed login
- permission denied
- ticket creation
- ticket update
- assignment change
- priority change
- status change
- administrator action
- file upload
- blocked file upload
- security-related ticket flag

## Proposal Testing Areas

The proposal expects:

- unit testing
- integration testing
- system testing
- security testing
- suspicious activity simulation
- performance testing
- AI accuracy evaluation
- user testing

## GDPR And Ethics

The project should:

- minimise stored personal data
- restrict access by role
- hash passwords securely
- log only relevant security/system events
- avoid real customer, employee, or live organisational data in the final report/demo
- use synthetic ticket examples where needed
