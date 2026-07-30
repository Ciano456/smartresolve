# SmartResolve

SmartResolve is a secure internal IT support portal for managing incidents, service
requests, change requests, access requests, and report/data requests.

## Status

All eleven functional requirements are implemented, tested, and deployed. The
application runs live on Railway with PostgreSQL, Redis, persistent attachment
storage, and Microsoft Graph email delivery.

| | |
|---|---|
| Automated tests | 244 passing |
| Coverage | 84% overall, branch-aware (86% statement, 73% branch) |
| Deployment | Live on Railway, health check verified |
| CI | Django checks, migration check, Tailwind build, tests, production `check --deploy` |

Implemented and tested:

- email-based Django authentication and Submitter, Support Staff, and Admin roles
- admin user, role, lookup, and ticket management
- submitter ticket creation, comments, attachments, and protected downloads
- staff assignment, priority/status updates, notes, filtering, history, resolution,
  and cancellation
- Microsoft Graph notification service, templates, event records, and ticket triggers
- dashboard KPIs, Chart.js reporting datasets, and authorised CSV export
- AI-assisted ticket categorisation and security triage with staff override, keyword
  fallback, and graceful degradation when no trained model is present
- audit logging, security event flagging, and an admin security metrics dashboard
- upload hardening, object permissions, and configurable login throttling
- GitHub Actions checks for Django, migrations, tests, and production settings

Known limitations, carried into future work:

- classifiers are trained on a generated dataset rather than real ticket history
- security-triage recall is 66.7% on the final holdout set, so the model produces a
  staff review signal rather than an automatic incident decision
- no session inactivity timeout, malware scanning, load testing, or external user
  acceptance testing

## Stack

- Python 3.12
- Django 6
- SQLite for local development and Railway PostgreSQL in production
- Redis for login throttling and caching
- Django templates and Tailwind CSS
- Chart.js
- Microsoft Graph
- scikit-learn (TF-IDF with Logistic Regression and Multinomial Naive Bayes)
- pytest and pytest-django

## Project Structure

- `accounts/` authentication, roles, and login security
- `admin_portal/` internal administration and audit activity
- `tickets/` ticket domain and workflows
- `notifications/` Microsoft Graph delivery and notification records
- `dashboard/` KPI reporting, charts, and CSV export
- `ml/` TF-IDF ticket category and security triage classifiers, training command,
  dataset generation, and prediction records

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

## Machine Learning

The ticket category and security triage classifiers are trained from a generated,
hash-verified dataset. Model binaries are regenerable and are not committed.

```bash
python ml/data/generate_dataset.py
python manage.py train_classifiers
```

Training performs grouped five-fold cross-validation, compares Logistic Regression
against Multinomial Naive Bayes on macro F1, selects a recall-weighted decision
threshold for the security model, and writes full metrics to `ml/artifacts/metrics.json`.
If no trained model is present the application degrades gracefully and ticket creation
is unaffected.

## Checks And Tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
coverage run -m pytest && coverage report
```

## Branch Strategy

- `main` contains stable releases.
- `develop` is the integration branch and GitHub default.
- `feature/<name>` contains scoped feature work merged through pull requests.
- `hotfix/<name>` is reserved for urgent stable-release fixes.

See [security controls](SECURITY.md) for further detail on the security measures
implemented in the application.
