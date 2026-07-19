# Requirements Traceability Matrix

Status reflects implementation and automated evidence in the repository. Manual
screenshots, performance measurements, UAT, and deployment evidence remain open.

| Req ID | Requirement | Use Case | Implementation Reference | Automated Evidence | Manual Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| FR-01 | User authentication | FR-01 | `accounts/views.py`, `accounts/security.py` | Authentication, password-flow, throttle, and audit tests | Login screenshot pending | [x] |
| FR-02 | Ticket submission | FR-02 | `tickets/views.py`, `tickets/forms.py` | Ticket creation and validation tests | Submission screenshot pending | [x] |
| FR-03 | Ticket tracking and viewing | FR-03 | `tickets/views.py`, ticket templates | Visibility, comment, history, and attachment tests | User workflow screenshot pending | [x] |
| FR-04 | Ticket management by support staff | FR-04 | `tickets/views.py`, `tickets/forms.py` | Assignment, status, priority, note, filter, resolve, and cancel tests | Staff workflow screenshot pending | [x] |
| FR-05 | Role-based access control | FR-05 | `accounts/models.py`, `accounts/decorators.py`, object-filtered views | Role, restricted-view, and cross-user access tests | Role UI screenshot pending | [x] |
| FR-06 | Email notifications | FR-06 | `notifications/`, `tickets/notifications.py` | Graph client, service, event, and trigger tests | Sanitised event/log screenshot pending | [x] |
| FR-07 | Dashboard and reporting | FR-07 | `dashboard/services.py`, `dashboard/views.py`, dashboard templates | KPI, access, chart-data, aggregate, export-permission, and CSV-injection tests | Dashboard screenshot and sample CSV pending | [x] |
| FR-08 | AI-assisted ticket categorisation | FR-08 | `ml/`, ticket creation/detail/list integration | ML, fallback, permission, override, audit, and filter tests | Staff workflow screenshot pending | [x] |
| FR-09 | Audit logging | FR-09 | `admin_portal.models.AuditLog`, `admin_portal/audit.py`, `TicketHistory` | Login, denial, upload, admin, and ticket audit tests | Audit-log screenshot pending | [x] |
| FR-10 | Security metrics dashboard | FR-10 | `admin_portal.security_dashboard.build_security_dashboard_context`, `security_dashboard`, security dashboard template | Admin-only access, metric, filter, empty-state, keyword, and query-bound tests | Security dashboard screenshot pending | [x] |
| FR-11 | Security event flagging | FR-11 | `AuditLog`, `admin_portal/audit.py`, `admin_portal/security.py`, account and ticket flows | Direct/proxy IP, severity mapping, login, denial, upload, and AI ticket-event tests | Flagged-event dashboard screenshot pending | [x] |
| NFR-01 | Secure authentication | UC-01 | Django auth, `accounts.models.User` | Auth and password-flow tests | Security notes in `SECURITY.md` | [x] |
| NFR-02 | Security protections | UC-ALL | Middleware, forms, `accounts/security.py` | CSRF defaults, upload validation, throttle, and malformed-input tests | Audit screenshot pending | [x] |
| NFR-03 | Access enforcement | UC-ALL | Role decorators and object-filtered views | Anonymous, wrong-role, cross-user, and attachment tests | Permission evidence pending | [x] |
| NFR-04 | Performance | FR-07 | Optimised querysets and pagination | Functional pagination/aggregate tests | Targets and load measurements pending | [~] |
| NFR-05 | AI accuracy | FR-08 | `train_classifiers`, grouped dataset, frozen independent holdout | 82.5% mean grouped cross-validation accuracy and 91.7% frozen holdout accuracy; full metrics and hashes in `ml/artifacts/metrics.json` | Evaluation write-up complete | [x] |
| NFR-06 | Audit logging | UC-ALL | `admin_portal.models.AuditLog`, `admin_portal/audit.py`, `TicketHistory` | Login, denial, upload, admin, and ticket audit tests | Audit-log screenshot pending | [x] |
| NFR-07 | GDPR/data minimisation | UC-ALL | Object permissions, hashed throttle identifiers, protected files | Access and security tests | Formal GDPR review pending | [~] |
| NFR-08 | Deployment security and recoverability | UC-ALL | Production settings, `railway.json`, `build.sh`, deployment runbooks | Settings/health tests and deployment check | Live Railway, backup, restore, and smoke evidence pending | [~] |

## Latest Automated Test Evidence

- Local suite on 19 July 2026: `243 passed`.
- Migration consistency: no changes detected.
- Django system check: no issues.
- GitHub CI evidence will be linked from the issue #24 pull request.
