# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Login attempt throttling. This is what stops someone from just trying
password after password against one account. After too many failed
attempts from the same email and IP combination within a set window, any
further attempts get blocked for a while, even if the correct password is
eventually typed in.

Everything is stored in the Django cache rather than the database, since
this data is short lived and needs to be fast to check on every single
login attempt.
"""

from __future__ import annotations

import hashlib

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

from admin_portal.security import get_client_ip


def _login_attempt_key(request: HttpRequest, email: str) -> str:
    # Hashing the email and IP together means the cache key itself
    # doesn't store anyone's email address in plain text, and combining
    # both means the limit is per person per location, not just per
    # email on its own.
    client_ip = get_client_ip(request) or "unknown"
    identifier = f"{email.strip().lower()}|{client_ip}"
    digest = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
    return f"login-attempt:{digest}"


def _login_block_key(request: HttpRequest, email: str) -> str:
    return f"{_login_attempt_key(request, email)}:blocked"


def is_login_blocked(request: HttpRequest, email: str) -> bool:
    # Checked right at the start of the login view, before even looking
    # at the password, so a blocked attempt doesn't waste time checking
    # credentials that won't be accepted anyway.
    return bool(cache.get(_login_block_key(request, email), False))


def record_failed_login(request: HttpRequest, email: str) -> bool:
    """Call this after a login attempt fails. Returns True if this
    failure was the one that triggered a block."""
    attempt_key = _login_attempt_key(request, email)
    block_key = _login_block_key(request, email)

    if cache.get(block_key, False):
        return True

    # cache.add only sets the value if the key isn't already there, so
    # this is how the attempt counter gets started at 1 the first time,
    # and cache.incr bumps it up on every attempt after that.
    if cache.add(attempt_key, 1, timeout=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS):
        attempt_count = 1
    else:
        try:
            attempt_count = cache.incr(attempt_key)
        except ValueError:
            # The key could have expired in the moment between the add
            # check and the incr call, so this just restarts the count
            # rather than crashing the login attempt.
            cache.set(
                attempt_key,
                1,
                timeout=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
            )
            attempt_count = 1

    if attempt_count < settings.LOGIN_RATE_LIMIT_ATTEMPTS:
        return False

    # The limit has been hit, so block further attempts for a while and
    # reset the attempt counter, there's no need to keep counting once
    # the block itself is already in place.
    cache.set(
        block_key,
        True,
        timeout=settings.LOGIN_RATE_LIMIT_BLOCK_SECONDS,
    )
    cache.delete(attempt_key)
    return True


def clear_failed_logins(request: HttpRequest, email: str) -> None:
    # Called after a successful login, so a genuine login doesn't leave
    # old failed attempts sitting around counting towards a future block.
    cache.delete_many(
        [
            _login_attempt_key(request, email),
            _login_block_key(request, email),
        ]
    )
