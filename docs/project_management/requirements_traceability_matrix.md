# Requirements Traceability Matrix

Status reflects implementation and automated evidence in the repository. Manual
screenshots, performance measurements, UAT, and deployment evidence remain open.

| Req ID | Requirement | Use Case | Implementation Reference | Automated Evidence | Manual Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| FR-01 | Authentication | UC-01 | `accounts/views.py`, `accounts/security.py` | `accounts/tests.py` | Login screenshot pending | [x] |
| FR-02 | Roles | UC-02 | `accounts/models.py`, `accounts/decorators.py` | Role and restricted-view tests | Role UI screenshot pending | [x] |
| FR-03 | Submit ticket | UC-03 | `tickets/views.py`, `tickets/forms.py` | Ticket creation tests | Workflow screenshot pending | [x] |
| FR-04 | View tickets and updates | UC-04 | `tickets/views.py`, ticket templates | Visibility, comment, history, and attachment tests | Workflow screenshot pending | [x] |
| FR-05 | Staff ticket management | UC-05/06 | `tickets/views.py`, `tickets/forms.py` | Assignment, status, priority, note, filter, resolve, and cancel tests | Staff workflow screenshot pending | [x] |
| FR-06 | Admin configuration | UC-02 | `admin_portal/views.py`, `admin_portal/forms.py` | Admin view and form tests | Admin screenshots pending | [x] |
| FR-07 | Email notifications | UC-07 | `notifications/`, `tickets/notifications.py` | Graph client, service, event, and trigger tests | Sanitised event/log screenshot pending | [x] |
| FR-08 | Dashboard reporting | UC-08 | `dashboard/services.py`, dashboard template | KPI, access, chart-data, and aggregate tests | Dashboard screenshot pending | [x] |
| FR-09 | Export reports | UC-09 | `dashboard/services.py`, `dashboard/views.py` | Permission, content, and CSV-injection tests | Sample CSV pending | [x] CSV |
| FR-10 | AI classification | UC-10 | `ml/` placeholder only | None | Accuracy report pending | [ ] |
| FR-11 | AI evaluation pipeline | UC-10 | Not implemented | None | Metrics output pending | [ ] |
| FR-12 | Response suggestions | UC-05 | Not implemented | None | Suggested-response screenshot pending | [ ] |
| NFR-01 | Secure authentication | UC-01 | Django auth, `accounts.models.User` | Auth and password-flow tests | Security notes in `SECURITY.md` | [x] |
| NFR-02 | Security protections | UC-ALL | Middleware, forms, `accounts/security.py` | CSRF defaults, upload validation, throttle, and malformed-input tests | Audit screenshot pending | [x] |
| NFR-03 | Access enforcement | UC-ALL | Role decorators and object-filtered views | Anonymous, wrong-role, cross-user, and attachment tests | Permission evidence pending | [x] |
| NFR-04 | Performance | UC-08 | Optimised querysets and pagination | Functional pagination/aggregate tests | Targets and load measurements pending | [~] |
| NFR-05 | AI accuracy | UC-10 | Not implemented | None | Metrics output pending | [ ] |
| NFR-06 | Audit logging | UC-ALL | `admin_portal.models.AuditLog`, `admin_portal/audit.py`, `TicketHistory` | Login, denial, upload, admin, and ticket audit tests | Audit-log screenshot pending | [x] |
| NFR-07 | GDPR/data minimisation | UC-ALL | Object permissions, hashed throttle identifiers, protected files | Access and security tests | Formal GDPR review pending | [~] |
| NFR-08 | Deployment security and recoverability | UC-ALL | Production settings, `railway.json`, `build.sh`, deployment runbooks | Settings/health tests and deployment check | Live Railway, backup, restore, and smoke evidence pending | [~] |

## Latest Automated Test Evidence

- Local pre-deployment suite on 17 July 2026: `196 passed`.
- Migration consistency: no changes detected.
- Django system check: no issues.
- GitHub CI evidence will be linked from the issue #24 pull request.
