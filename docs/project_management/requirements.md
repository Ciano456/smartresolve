# Requirements

## Functional Requirements

| ID | Requirement | Status |
| --- | --- | --- |
| FR-01 | Users must be able to authenticate securely. | [x] Login, logout, password reset, throttling, and audit evidence implemented. |
| FR-02 | Users must be able to submit support tickets. | [x] Implemented with type, system, priority, title, description, and attachments. |
| FR-03 | Users must be able to track and view their tickets and updates. | [x] Submitter visibility, comments, history, and attachments implemented. |
| FR-04 | Support staff must be able to manage tickets. | [x] Includes assignment, status, priority, notes, resolution, cancellation, and filtering. |
| FR-05 | The system must enforce role-based access control. | [x] User, support staff, and administrator roles enforced at view and object level. |
| FR-06 | The system must send ticket email notifications. | [x] Microsoft Graph service, templates, event log, client, and triggers implemented. |
| FR-07 | Authorised users must be able to view dashboards and reports. | [x] KPIs, charts, workload trends, resolution metrics, and authorised CSV export implemented. |
| FR-08 | The system must provide AI-assisted ticket categorisation. | [x] Four-category suggestion, staff override, security triage, and manual fallback implemented. |
| FR-09 | The system must record configured actions in an audit log. | [x] Authentication, denial, upload, ticket, and administrator events implemented. |
| FR-10 | Administrators must be able to view security metrics and trends. | [x] Admin-only flagged-ticket, severity, keyword, recent-event, and six-month trend dashboard implemented. |
| FR-11 | The system must flag configured suspicious security events. | [x] IP-aware audit severity, configured event flags, and AI-assisted ticket security events implemented. |

## Non-Functional Requirements

| ID | Requirement | Status |
| --- | --- | --- |
| NFR-01 | Passwords must use Django secure hashing and sessions. | [x] |
| NFR-02 | System must use CSRF protection and input validation. | [x] CSRF, form validation, upload allowlist/size/content checks, and tests exist. |
| NFR-03 | Unauthorized users cannot access restricted views. | [x] Role and object-level enforcement is covered by tests. |
| NFR-04 | Dashboard must load within acceptable time. | [ ] Needs performance target and test. |
| NFR-05 | AI classifier must achieve about 75-85 percent accuracy. | [x] Mean grouped cross-validation accuracy is 82.5%; frozen holdout accuracy is 91.7%; full evidence is recorded in `ml/artifacts/metrics.json`. |
| NFR-06 | System logs ticket actions and login events. | [x] Ticket/admin, failed login, throttle, denied access, and blocked upload events exist. |
| NFR-07 | System must minimise stored personal data. | [~] Needs explicit report section and review. |

## Use Cases

| ID | Use Case | Status |
| --- | --- | --- |
| FR-01 | User authenticates. | [x] |
| FR-02 | User submits a ticket. | [x] |
| FR-03 | User tracks and views a ticket. | [x] |
| FR-04 | Support staff manages a ticket. | [x] |
| FR-05 | System enforces role-based access. | [x] |
| FR-06 | System sends a notification. | [x] |
| FR-07 | Authorised user views dashboards and reports. | [x] |
| FR-08 | System suggests a ticket category. | [x] |
| FR-09 | System records an auditable action. | [x] |
| FR-10 | Administrator views the security dashboard. | [x] |
| FR-11 | System flags a suspicious security event. | [x] |
