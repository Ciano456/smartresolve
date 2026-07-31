# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Loads variables from a local .env file (not committed to git) into the
# environment, so secrets like GRAPH_CLIENT_SECRET don't have to be
# hardcoded anywhere in the codebase.
load_dotenv(BASE_DIR / ".env")


def env_list(name: str, default: str = "") -> list[str]:
    # Reads a comma separated environment variable into a clean list, for
    # things like ALLOWED_HOSTS where more than one value might be
    # needed.
    return [
        item.strip() for item in os.getenv(name, default).split(",") if item.strip()
    ]


def positive_env_int(name: str, default: int) -> int:
    # Falls back to the default for anything that isn't a real positive
    # number, rather than letting a typo in an environment variable break
    # startup.
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def optional_probability_env_float(name: str) -> float | None:
    # Used for AI_SECURITY_THRESHOLD. Unlike the helpers above, this
    # raises rather than silently falling back, since a badly set
    # security threshold is worth failing loudly over rather than quietly
    # using some default the operator didn't intend.
    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        return None
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be a number between 0 and 1.") from exc
    if not 0.0 <= value <= 1.0:
        raise ImproperlyConfigured(f"{name} must be between 0 and 1.")
    return value


def boolean_env(name: str, default: bool = False) -> bool:
    # A simple helper for settings that are just on or off, like
    # TRUST_PROXY_HEADERS below. Accepts a few common ways of writing
    # true in an environment variable rather than requiring an exact
    # match, since these get set by hand in Railway or a .env file.
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# Microsoft Graph settings for sending email notifications through
# Microsoft 365 instead of a normal SMTP server. See
# notifications/graph_client.py for how these actually get used.
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

# Where the trained FR8 model files live. Defaults to the artifacts
# folder in the repo, but can be pointed elsewhere through the
# environment, for example on a deployment where the models are stored
# separately from the code.
AI_CATEGORY_MODEL_PATH = Path(
    os.getenv("AI_CATEGORY_MODEL_PATH", "").strip()
    or BASE_DIR / "ml/artifacts/category_model.joblib"
)
AI_SECURITY_MODEL_PATH = Path(
    os.getenv("AI_SECURITY_MODEL_PATH", "").strip()
    or BASE_DIR / "ml/artifacts/security_model.joblib"
)
# None here means "use whatever threshold the trained model itself was
# tuned to", see ml/predictor.py. Setting this explicitly overrides that
# without needing to retrain the model.
AI_SECURITY_THRESHOLD = optional_probability_env_float("AI_SECURITY_THRESHOLD")
# Whether to trust the X-Forwarded-For header when working out a
# request's real IP address for the audit log, see
# admin_portal/security.py. This should only be turned on when the app
# is actually running behind a proxy that sets this header honestly, for
# example on Railway, since otherwise anyone could fake their own IP by
# just sending the header themselves.
TRUST_PROXY_HEADERS = boolean_env("TRUST_PROXY_HEADERS")

# How the login throttle in accounts/security.py behaves: how many failed
# attempts are allowed, over what time window, and how long a block lasts
# once triggered.
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
    "accounts.middleware.AuthenticatedNoStoreMiddleware",
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
