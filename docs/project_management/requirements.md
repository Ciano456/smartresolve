# Requirements

## Functional Requirements

| ID | Requirement | Status |
| --- | --- | --- |
| FR-01 | Users must be able to register, log in, and log out securely. | [~] Login/logout complete; accounts are admin-created rather than self-registered. |
| FR-02 | System must support user, support staff, and admin roles. | [x] |
| FR-03 | Users must be able to submit a ticket with category, urgency, and description. | [x] Implemented as type, system, priority, title, and description. |
| FR-04 | Users must be able to view ticket history and updates. | [x] Submitter updates and staff history views implemented. |
| FR-05 | Support staff must update ticket status, comments, and assignments. | [x] Includes priority, notes, resolution, cancellation, filtering, and history. |
| FR-06 | Admin can manage users, roles, categories, and urgency levels. | [x] User, role, lookup, and all-ticket management implemented. |
| FR-07 | System sends email notifications via Microsoft Graph API. | [x] Service, templates, event log, Graph client, and ticket triggers implemented. |
| FR-08 | Managers can view KPIs such as volume, response time, and trends. | [x] KPIs, breakdown charts, workload, trend, and average resolution time implemented. |
| FR-09 | System must export reports as CSV or PDF. | [x] Authorised CSV export implemented; PDF is an optional later enhancement. |
| FR-10 | System automatically categorises tickets using ML. | [ ] |
| FR-11 | System measures AI performance using test metrics. | [ ] |
| FR-12 | System suggests basic responses based on category. | [ ] |

## Non-Functional Requirements

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-01 | Passwords must use Django secure hashing and sessions. | [x] |
| NFR-02 | System must use CSRF protection and input validation. | [x] CSRF, form validation, upload allowlist/size/content checks, and tests exist. |
| NFR-03 | Unauthorized users cannot access restricted views. | [x] Role and object-level enforcement is covered by tests. |
| NFR-04 | Dashboard must load within acceptable time. | [ ] Needs performance target and test. |
| NFR-05 | AI classifier must achieve about 75-85 percent accuracy. | [ ] |
| NFR-06 | System logs ticket actions and login events. | [x] Ticket/admin, failed login, throttle, denied access, and blocked upload events exist. |
| NFR-07 | System must minimise stored personal data. | [~] Needs explicit report section and review. |

## Use Cases

| ID | Use Case | Status |
| --- | --- | --- |
| UC-01 | User logs in/out. | [x] |
| UC-02 | Admin assigns user roles. | [x] |
| UC-03 | User submits ticket. | [x] |
| UC-04 | User views ticket. | [x] |
| UC-05 | Staff triages ticket. | [x] |
| UC-06 | Staff resolves ticket. | [x] |
| UC-07 | System sends notification. | [x] |
| UC-08 | Manager views dashboard. | [x] |
| UC-09 | Export report. | [x] CSV |
| UC-10 | System classifies ticket. | [ ] |
