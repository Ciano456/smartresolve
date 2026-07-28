# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env_list, positive_env_int


def required_env(name: str) -> str:
    # Unlike the development settings, production has no safe fallback
    # for things like the secret key or database URL, so a missing
    # setting stops the app from starting at all rather than quietly
    # running with something insecure.
    value = os.getenv(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} must be set in production.")
    return value


SECRET_KEY = required_env("DJANGO_SECRET_KEY")
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be at least 50 characters and securely generated."
    )

DEBUG = False
# Whitenoise serves the static files (CSS, images) directly, so there's
# no need for a separate static file server in production.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

# Railway sets this automatically for the app's public URL, so it's added
# to the allowed hosts and trusted origins without needing to hardcode
# the domain anywhere.
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS or RAILWAY_PUBLIC_DOMAIN must be set in production."
    )

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
if railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{railway_domain}")
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))
if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        "DJANGO_CSRF_TRUSTED_ORIGINS or RAILWAY_PUBLIC_DOMAIN must be set "
        "in production."
    )

DATABASES = {
    "default": dj_database_url.parse(
        required_env("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": required_env("REDIS_URL"),
        "OPTIONS": {
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        },
    }
}

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "/app/media"))

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": MEDIA_ROOT},
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# A block of standard Django security headers and settings for running
# behind HTTPS, forcing secure cookies, and stopping the site being
# loaded in an iframe on another site (clickjacking protection).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# Railway's internal health checker reaches the container over HTTP even
# though public traffic is terminated at HTTPS by Railway's proxy.
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = positive_env_int("DJANGO_SECURE_HSTS_SECONDS", 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "railway": {
            "format": "{asctime} level={levelname} logger={name} message={message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "railway",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO").upper(),
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
