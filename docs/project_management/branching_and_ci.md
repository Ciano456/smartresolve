# Branching And CI

## Branch Strategy

- `main` - stable code only
- `develop` - integration branch
- `feature/<name>` - feature work
- `hotfix/<name>` - emergency fixes

Example branches:

- `feature/custom-user-model`
- `feature/admin-user-management`
- `feature/ticket-models`
- `feature/ticket-create-form`
- `feature/staff-ticket-queue`
- `feature/email-notifications`

## GitHub Settings

Configure immediately:

- default branch is `develop`
- protect `main`
- require pull request before merging to `main`
- require status checks before merging to `main`

Configure later:

- staging environment
- production environment
- protected-branch deployment controls
- production approval rules

## CI Workflow

First CI workflow:

- trigger on push to `develop` and `main`
- trigger on pull requests into `develop` and `main`
- install dependencies
- run Django checks
- check for missing migrations
- run tests

Recommended commands:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## PR Quality Workflow

Add later:

- Ruff
- Black
- import sorting
- coverage

## Deploy Workflow

Do not automate deployment yet.

Current deployment approach:

1. Work on a feature branch.
2. Merge to `develop`.
3. Test locally or on staging.
4. Merge stable work to `main`.
5. Deploy manually to internal app server.
6. Smoke test live system.

Later:

- add staging deploy workflow
- add production deploy with approval
- consider a self-hosted runner if internal network access is needed
