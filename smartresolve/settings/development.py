# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import os

from .base import *  # noqa: F403
from .base import BASE_DIR, env_list

# The fallback secret key below is clearly marked as insecure and is only
# ever used locally, production.py refuses to start at all without a
# real DJANGO_SECRET_KEY set through the environment.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-only-change-before-deployment",
)
DEBUG = os.getenv("DJANGO_DEBUG", "True").strip().lower() == "true"
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver")

# SQLite is fine for local development, no separate database server
# needed to just run the app and try things out. Production uses
# PostgreSQL instead, see production.py.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "smartresolve-development",
    }
}

MEDIA_ROOT = BASE_DIR / "media"
