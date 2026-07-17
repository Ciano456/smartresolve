# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import hashlib

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest


def _login_attempt_key(request: HttpRequest, email: str) -> str:
    client_ip = request.META.get("REMOTE_ADDR", "unknown")
    identifier = f"{email.strip().lower()}|{client_ip}"
    digest = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
    return f"login-attempt:{digest}"


def _login_block_key(request: HttpRequest, email: str) -> str:
    return f"{_login_attempt_key(request, email)}:blocked"


def is_login_blocked(request: HttpRequest, email: str) -> bool:
    return bool(cache.get(_login_block_key(request, email), False))


def record_failed_login(request: HttpRequest, email: str) -> bool:
    attempt_key = _login_attempt_key(request, email)
    block_key = _login_block_key(request, email)

    if cache.get(block_key, False):
        return True

    if cache.add(attempt_key, 1, timeout=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS):
        attempt_count = 1
    else:
        try:
            attempt_count = cache.incr(attempt_key)
        except ValueError:
            cache.set(
                attempt_key,
                1,
                timeout=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
            )
            attempt_count = 1

    if attempt_count < settings.LOGIN_RATE_LIMIT_ATTEMPTS:
        return False

    cache.set(
        block_key,
        True,
        timeout=settings.LOGIN_RATE_LIMIT_BLOCK_SECONDS,
    )
    cache.delete(attempt_key)
    return True


def clear_failed_logins(request: HttpRequest, email: str) -> None:
    cache.delete_many(
        [
            _login_attempt_key(request, email),
            _login_block_key(request, email),
        ]
    )
