# Sprint 1 Write-Up

Sprint 1 focused on getting the project into a stable state that is safe to build on. The aim was not to deliver user-facing features yet, but to make sure the Django project structure, configuration, and custom identity layer were in place before moving into authentication and ticket workflow development.

The main outcome of Sprint 1 is that SmartResolve now has a working project foundation. The application settings were cleaned up, environment variable loading was added, static and media file configuration were set, the root URL configuration was simplified, and the project was brought to a state where it can run cleanly with Django admin as the primary active route at that stage.

A custom user model was established during this sprint. That included the user model itself, a custom user manager, admin integration, and supporting forms needed to manage users through Django admin. Initial migrations were created and applied successfully, and a superuser was created and tested through the admin interface. This gave the project a proper identity base to support later authentication and role work.

Project documentation and workflow setup were also improved. A usable `README.MD`
was added with setup instructions, local environment steps, and project context. A
tracked `.env.example` documents expected environment variables without containing
credentials. GitHub Actions CI now runs Django checks, migration consistency checks,
and tests for pushes and pull requests targeting `develop` and `main`.

## Completed Items

- cleaned project foundation
- simplified root URL configuration
- cleaned and updated Django settings
- added environment variable loading
- configured static and media settings
- set `AUTH_USER_MODEL`
- implemented custom user model
- implemented custom user manager
- configured custom admin/forms for user management
- created initial migrations
- applied migrations successfully
- created and validated superuser/admin access
- added `.env.example`
- wrote project README
- implemented initial CI workflow

## Deliverable

By the end of Sprint 1, SmartResolve was in a stable early-development state with a working Django base, custom user setup, migrations in place, admin access working, and the core repo/setup documentation started.

## Out Of Scope

Sprint 1 did not include the real authentication flow, groups and permissions, ticket models, dashboard features, or notifications.

## Next Step

Sprint 2 should begin with login, logout, groups, role setup, permission helpers, and a basic account/profile page.
