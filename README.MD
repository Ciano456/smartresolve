# SmartResolve

SmartResolve is a secure internal IT support portal for managing incidents, service
requests, change requests, access requests, and report/data requests.

## Current Status

Implemented and tested:

- email-based Django authentication and Submitter, Support Staff, and Admin roles
- admin user, role, lookup, and ticket management
- submitter ticket creation, comments, attachments, and protected downloads
- staff assignment, priority/status updates, notes, filtering, history, resolution,
  and cancellation
- Microsoft Graph notification service, templates, event records, and ticket triggers
- dashboard KPIs, Chart.js reporting datasets, and authorised CSV export
- audit logging, upload hardening, object permissions, and configurable login throttling
- GitHub Actions checks for Django, migrations, and tests

Outstanding release work:

- production settings and deployment checklist (issue #25)
- UAT, screenshots, final RTM evidence, and demo material (issue #26)
- AI classification and response suggestions remain future enhancements

## Stack

- Python 3.12
- Django 6
- SQLite for local development; PostgreSQL planned for production
- Django templates and Tailwind CSS
- Chart.js
- Microsoft Graph
- pytest and pytest-django

## Project Structure

- `accounts/` authentication, roles, and login security
- `admin_portal/` internal administration and audit activity
- `tickets/` ticket domain and workflows
- `notifications/` Microsoft Graph delivery and notification records
- `dashboard/` KPI reporting, charts, and CSV export
- `ml/` reserved for future AI functionality
- `docs/project_management/` plans, sprint records, RTM, and evidence notes

## Local Setup

```bash
git clone https://github.com/Ciano456/smartresolve.git
cd smartresolve
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the application or
`http://127.0.0.1:8000/admin/` for Django admin.

## Environment Variables

Use `.env.example` as the source list. Required or supported variables include:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-value
DJANGO_DEBUG=True
GRAPH_TENANT_ID=
GRAPH_CLIENT_ID=
GRAPH_CLIENT_SECRET=
GRAPH_SENDER_USER=
IT_SUPPORT_EMAIL=
LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_SECONDS=900
LOGIN_RATE_LIMIT_BLOCK_SECONDS=900
```

Never commit `.env` or real credentials.

## Checks And Tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
```

## Branch Strategy

- `main` contains stable releases.
- `develop` is the integration branch and GitHub default.
- `feature/<name>` contains scoped feature work merged through pull requests.
- `hotfix/<name>` is reserved for urgent stable-release fixes.

See [project management notes](docs/project_management/README.md) and
[security controls](SECURITY.md) for further detail.
