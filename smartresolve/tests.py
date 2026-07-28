# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

BASE_DIR = Path(__file__).resolve().parent.parent


# Covers the health check endpoint and a few project level checks, for
# example that manage.py commands like collectstatic actually run
# cleanly.
class HealthCheckViewTests(TestCase):
    def test_health_check_returns_success_when_database_is_available(self) -> None:
        # Railway must only route traffic after Django can query its database.
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    @patch("smartresolve.views.connections")
    def test_health_check_hides_database_failure_details(
        self,
        mocked_connections,
    ) -> None:
        # Database failures must return a generic status without leaking internals.
        mocked_connections.__getitem__.return_value.cursor.side_effect = (
            OperationalError("sensitive database detail")
        )

        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertNotContains(
            response,
            "sensitive database detail",
            status_code=503,
        )

    def test_health_check_rejects_post_requests(self) -> None:
        # The public health route is read-only and must reject state-changing methods.
        response = self.client.post(reverse("health_check"))

        self.assertEqual(response.status_code, 405)


class ProductionSettingsTests(SimpleTestCase):
    def _run_production_import(
        self,
        code: str = "import smartresolve.settings.production",
        **overrides: str,
    ) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SECRET_KEY": "secure-production-test-key-" + ("x" * 50),
                "DJANGO_ALLOWED_HOSTS": "example.up.railway.app",
                "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.up.railway.app",
                "DATABASE_URL": "postgresql://user:password@localhost:5432/testdb",
                "REDIS_URL": "redis://localhost:6379/0",
                "MEDIA_ROOT": "/app/media",
            }
        )
        environment.update(overrides)
        return subprocess.run(
            [
                sys.executable,
                "-c",
                code,
            ],
            cwd=BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_production_settings_load_with_required_environment(self) -> None:
        # A complete Railway-like environment must load without contacting services.
        result = self._run_production_import(
            code=(
                "from smartresolve.settings import production as settings; "
                "assert settings.DEBUG is False; "
                "assert settings.SECURE_SSL_REDIRECT is True; "
                "assert settings.SESSION_COOKIE_SECURE is True; "
                "assert settings.CSRF_COOKIE_SECURE is True; "
                "assert settings.MEDIA_ROOT.as_posix() == '/app/media'; "
                "assert settings.DATABASES['default']['ENGINE'] == "
                "'django.db.backends.postgresql'"
            )
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_settings_require_database_url(self) -> None:
        # Production must never silently fall back to SQLite when PostgreSQL is absent.
        result = self._run_production_import(DATABASE_URL="")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL must be set", result.stderr)

    def test_production_settings_require_redis_url(self) -> None:
        # Shared throttling state is mandatory rather than silently becoming per-process.
        result = self._run_production_import(REDIS_URL="")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REDIS_URL must be set", result.stderr)

    def test_production_settings_reject_weak_secret_key(self) -> None:
        # Production must reject development-style or short signing keys at startup.
        result = self._run_production_import(DJANGO_SECRET_KEY="too-short")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be at least 50 characters", result.stderr)

    def test_production_settings_require_an_allowed_host(self) -> None:
        # Production must not accept arbitrary Host headers through a wildcard fallback.
        result = self._run_production_import(
            DJANGO_ALLOWED_HOSTS="",
            RAILWAY_PUBLIC_DOMAIN="",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_ALLOWED_HOSTS or RAILWAY_PUBLIC_DOMAIN", result.stderr)

    def test_railway_domain_is_added_to_hosts_and_csrf_origins(self) -> None:
        # Railway's generated domain must be accepted as a host and trusted HTTPS origin.
        result = self._run_production_import(
            code=(
                "from smartresolve.settings import production as settings; "
                "assert 'generated.up.railway.app' in settings.ALLOWED_HOSTS; "
                "assert 'https://generated.up.railway.app' in "
                "settings.CSRF_TRUSTED_ORIGINS"
            ),
            DJANGO_ALLOWED_HOSTS="",
            DJANGO_CSRF_TRUSTED_ORIGINS="",
            RAILWAY_PUBLIC_DOMAIN="generated.up.railway.app",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_settings_require_a_trusted_csrf_origin(self) -> None:
        # Production form submissions must never rely on an undefined trusted origin.
        result = self._run_production_import(
            DJANGO_CSRF_TRUSTED_ORIGINS="",
            RAILWAY_PUBLIC_DOMAIN="",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "DJANGO_CSRF_TRUSTED_ORIGINS or RAILWAY_PUBLIC_DOMAIN",
            result.stderr,
        )
