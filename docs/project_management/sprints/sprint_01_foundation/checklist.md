# Sprint 1 Checklist

## A. Project Starts Cleanly

- [x] Confirm the project can run without import errors.
- [x] Check that included app URL files contain `urlpatterns`.
- [x] Remove or postpone app URL includes that are not ready yet.
- [x] Confirm the root URL structure is intentional.
- [x] Confirm `/admin/` works.
- [~] Confirm there is a sensible temporary home route if needed.

## B. Settings Cleanup

- [x] Review `INSTALLED_APPS`.
- [x] Confirm middleware is standard and sufficient.
- [x] Move secret values out of code and into env vars.
- [x] Define `SECRET_KEY` from environment.
- [x] Define `DEBUG` from environment.
- [x] Review `ALLOWED_HOSTS`.
- [x] Confirm timezone and locale choices.
- [x] Fix static settings.
- [x] Add media settings.
- [x] Add project-level templates directory.
- [ ] Add auth redirect settings.
- [x] Keep database config simple for now.

## C. Custom User Model

- [x] Confirm user fields are final enough for MVP.
- [x] Confirm email is the login identifier.
- [x] Confirm `USERNAME_FIELD` is correct.
- [x] Confirm manager methods support user and superuser creation.
- [x] Confirm admin integration supports the custom model.
- [x] Confirm user forms exist for admin usage.

## D. Migrations

- [x] Create initial migrations for `accounts`.
- [x] Confirm migration dependencies are clean.
- [x] Apply migrations locally.
- [x] Check the database builds from scratch cleanly.
- [x] Check for missing migrations.

## E. Static, Media, And Templates Structure

- [x] Decide where global templates live.
- [x] Keep app templates inside apps.
- [x] Create static file structure.
- [x] Create uploaded file structure.
- [x] Decide media URL and local path.

## F. App Boundaries

- [x] `accounts`: identity and authentication.
- [x] `tickets`: ticket domain models and workflow.
- [x] `admin_portal`: internal admin UI beyond Django admin.
- [x] `dashboard`: reporting and KPIs.
- [x] `notifications`: email and notification logic.
- [x] `ml`: future AI features.
- [~] Placeholder apps kept intentionally.

## G. Environment Setup

- [x] Fill in `.env.example`.
- [x] Include needed variables.
- [x] Make sure `.env` is ignored.
- [~] Confirm project can be set up from scratch by following docs.

## H. README

- [x] Add project purpose.
- [x] Add stack summary.
- [x] Add setup steps.
- [x] Add dependency install step.
- [x] Add migrate step.
- [x] Add runserver step.
- [x] Add superuser creation step.
- [x] Add test command.
- [x] Add roadmap/status note.

## I. CI

- [x] Add `.github/workflows/ci.yml`.
- [x] Trigger on push to `develop` and `main`.
- [x] Trigger on PRs into `develop` and `main`.
- [x] Install dependencies.
- [x] Run Django checks.
- [x] Check missing migrations.
- [x] Run tests.

## J. GitHub Branch Setup

- [x] Set default branch to `develop`.
- [?] Protect `main`.
- [?] Require PRs into `main`.
- [?] Require status checks before merge to `main`.
- [x] Use `feature/...` branch naming strategy.

## K. Foundation Validation

- [x] Project starts.
- [x] Migrations apply.
- [x] Superuser can be created.
- [x] Admin opens.
- [x] Custom user works in admin.
- [x] No missing migration warning.
- [x] CI file exists.
- [x] README exists.
- [x] `.env.example` exists.
