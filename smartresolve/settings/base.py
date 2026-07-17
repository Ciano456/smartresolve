# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def positive_env_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID", "").strip()
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID", "").strip()
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET", "").strip()
GRAPH_SENDER_USER = os.getenv("GRAPH_SENDER_USER", "").strip()
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_TOKEN_URL = (
    f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
    if GRAPH_TENANT_ID
    else ""
)
GRAPH_SEND_MAIL_URL = (
    f"https://graph.microsoft.com/v1.0/users/{GRAPH_SENDER_USER}/sendMail"
    if GRAPH_SENDER_USER
    else ""
)
IT_SUPPORT_EMAIL = os.getenv("IT_SUPPORT_EMAIL", "").strip()

LOGIN_RATE_LIMIT_ATTEMPTS = positive_env_int("LOGIN_RATE_LIMIT_ATTEMPTS", 5)
LOGIN_RATE_LIMIT_WINDOW_SECONDS = positive_env_int(
    "LOGIN_RATE_LIMIT_WINDOW_SECONDS",
    900,
)
LOGIN_RATE_LIMIT_BLOCK_SECONDS = positive_env_int(
    "LOGIN_RATE_LIMIT_BLOCK_SECONDS",
    900,
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "admin_portal",
    "ml",
    "notifications",
    "tickets",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smartresolve.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "smartresolve.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Dublin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
