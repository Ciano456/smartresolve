# Railway Setup

This runbook starts after the deployment-preparation PR has merged into `develop`.

## 1. Create The Project

1. Create a Railway Hobby project in the nearest suitable European region.
2. Add a PostgreSQL service.
3. Add a Redis service.
4. Add an application service from `Ciano456/smartresolve`.
5. Select `develop` for the initial UAT deployment.

Do not expose PostgreSQL or Redis with public domains.

## 2. Configure The Application

1. Add the variables listed in `environment_variables.md`.
2. Reference Railway's PostgreSQL URL as `DATABASE_URL`.
3. Reference Railway's Redis URL as `REDIS_URL`.
4. Generate a long random `DJANGO_SECRET_KEY`.
5. Set `DJANGO_SETTINGS_MODULE=smartresolve.settings.production`.
6. Generate a Railway public domain.
7. Confirm `RAILWAY_PUBLIC_DOMAIN` is available to the service.

The committed `railway.json` defines the build, migration, Gunicorn, health-check,
and restart commands.

## 3. Attach Persistent Media Storage

1. Add a volume to the application service.
2. Mount it at `/app/media`.
3. Keep `MEDIA_ROOT=/app/media` or use the production default.
4. Use one application replica; Railway volumes cannot be shared across replicas.

Uploads outside this mount are ephemeral and must not be treated as persistent.

## 4. Deploy

The deployment sequence is:

1. Railpack installs Python and Node dependencies.
2. `build.sh` compiles Tailwind and runs `collectstatic`.
3. The pre-deploy command runs `python manage.py migrate --noinput`.
4. Gunicorn starts and binds to Railway's `PORT`.
5. Railway requests `/health/` and only routes traffic after it returns `200`.

## 5. Create The First Administrator

Open a Railway application shell and run:

```text
python manage.py createsuperuser
```

Use the admin portal to assign application roles and create synthetic UAT accounts.
Never use real employee or customer records for assessment evidence.

## 6. Verify External Integrations

1. Confirm the Graph application has permission to send mail.
2. Submit a synthetic ticket.
3. Inspect the notification event without exposing secrets.
4. Confirm a test message reaches the configured support inbox.
5. Record any tenant-policy failure as a known limitation rather than weakening auth.

## 7. Capture Evidence

- successful Railway deployment
- `/health/` returning `200`
- migration log without credentials
- static dashboard assets loading
- PostgreSQL-backed ticket surviving redeployment
- attachment surviving redeployment
- sanitised notification event
- Railway log output with no secrets
