# Rollback And Restore

## Application Rollback

1. Stop further changes and record the failing deployment identifier.
2. Review Railway deployment and application logs without publishing secrets.
3. Use Railway's rollback/redeploy control for the last known-good deployment.
4. Verify `/health/`, login, ticket access, static assets, and protected media.
5. Create a GitHub fix issue and document the root cause.

Application rollback does not automatically reverse database migrations.

## PostgreSQL Backup And Restore

Before risky releases, create a Railway PostgreSQL backup or an encrypted `pg_dump`
stored outside the repository. Record the database service, timestamp, schema version,
and restoration owner.

For restoration:

1. restrict application access
2. confirm the selected backup and target database
3. restore using Railway's supported backup mechanism or `pg_restore`
4. run `python manage.py showmigrations`
5. run the smoke test before reopening access

Never commit dumps; they may contain emails, ticket content, and audit history.

## Media Backup And Restore

The `/app/media` volume stores ticket attachments separately from PostgreSQL. Back up
the volume before storage changes and restore it to the same mount path. Validate a
sample of protected attachment downloads after restoration. Database and media backups
must be taken as close together as practical to reduce broken attachment references.
