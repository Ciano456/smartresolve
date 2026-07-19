# Production Environment Variables

Never commit production values. Configure them in the Railway web-service Variables
tab and use Railway service references for PostgreSQL and Redis.

## Required Application Variables

| Variable | Source | Purpose |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Manual | Set to `smartresolve.settings.production`. |
| `DJANGO_SECRET_KEY` | Manual generated value | Django signing key; at least 50 characters. |
| `DJANGO_ALLOWED_HOSTS` | Manual when needed | Extra comma-separated hostnames without schemes. Railway's generated domain is added automatically. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Manual when needed | Extra comma-separated HTTPS origins. Railway's generated HTTPS origin is added automatically. |
| `DATABASE_URL` | Railway Postgres reference | PostgreSQL connection URL. |
| `REDIS_URL` | Railway Redis reference | Shared login-throttle cache. |
| `IT_SUPPORT_EMAIL` | Manual | Support inbox receiving ticket notifications. |

Railway normally supplies `RAILWAY_PUBLIC_DOMAIN` and `PORT`. Production settings
automatically add `RAILWAY_PUBLIC_DOMAIN` to allowed hosts and trusted HTTPS origins.

## Microsoft Graph Variables

| Variable | Purpose |
| --- | --- |
| `GRAPH_TENANT_ID` | Microsoft Entra tenant identifier. |
| `GRAPH_CLIENT_ID` | Registered application/client identifier. |
| `GRAPH_CLIENT_SECRET` | Client credential stored only in Railway. |
| `GRAPH_SENDER_USER` | Licensed mailbox/user used to send notifications. |

If these are absent, ticket operations continue but notification delivery is skipped
or recorded as failed according to the existing notification service behaviour.

## Optional Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MEDIA_ROOT` | `/app/media` | Railway volume mount used for attachments. |
| `WEB_CONCURRENCY` | `2` | Gunicorn worker count. Keep modest on Hobby resources. |
| `DJANGO_LOG_LEVEL` | `INFO` | Root console logging level. |
| `DJANGO_SECURE_HSTS_SECONDS` | `31536000` | HSTS duration in seconds. |
| `LOGIN_RATE_LIMIT_ATTEMPTS` | `5` | Failures before a temporary login block. |
| `LOGIN_RATE_LIMIT_WINDOW_SECONDS` | `900` | Failure counting window. |
| `LOGIN_RATE_LIMIT_BLOCK_SECONDS` | `900` | Temporary block duration. |
| `AI_CATEGORY_MODEL_PATH` | `ml/artifacts/category_model.joblib` | Optional category artifact override. |
| `AI_SECURITY_MODEL_PATH` | `ml/artifacts/security_model.joblib` | Optional security artifact override. |
| `AI_SECURITY_THRESHOLD` | Trained artifact value | Optional security review threshold override; must be between 0 and 1. |

The model paths and threshold are operational configuration rather than secrets.
Leave the paths and threshold unset to use the build-generated artifacts and their
validation-selected threshold. Staff correct individual predictions in the
application; global model configuration remains environment-only.

## Railway References

Use Railway's variable-reference UI rather than copying database credentials between
services. Link the application variables to the values exposed by the PostgreSQL and
Redis services. Confirm the resulting `DATABASE_URL` and `REDIS_URL` variables exist
without printing their values into screenshots or logs.
