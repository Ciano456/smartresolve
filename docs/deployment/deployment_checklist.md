# Deployment Checklist

## Before Railway

- [ ] Deployment-preparation PR merged and CI green.
- [ ] Full local tests pass.
- [ ] Production deployment check reviewed.
- [ ] No missing migrations.
- [ ] No secrets tracked by Git.
- [ ] Microsoft Graph test tenant/mailbox details available.

## Railway Services

- [ ] Hobby project created.
- [ ] PostgreSQL service created and private.
- [ ] Redis service created and private.
- [ ] GitHub application service connected to `develop`.
- [ ] Persistent volume mounted at `/app/media`.
- [ ] Application restricted to one replica while using the volume.

## Configuration

- [ ] Production settings module configured.
- [ ] Strong secret key configured.
- [ ] Database and Redis references configured.
- [ ] Railway domain allowed.
- [ ] CSRF trusted origin uses HTTPS.
- [ ] Graph variables configured without exposing values.
- [ ] Support inbox configured.
- [ ] Login-throttle values reviewed.

## First Deployment

- [ ] Build succeeds.
- [ ] Tailwind compilation succeeds.
- [ ] Static collection succeeds.
- [ ] Migrations succeed.
- [ ] Gunicorn starts.
- [ ] Health check succeeds.
- [ ] Administrator created.
- [ ] Smoke test completed.
- [ ] Evidence captured and sanitised.
