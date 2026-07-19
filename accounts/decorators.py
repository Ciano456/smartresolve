# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Role based access control for views. Each decorator below checks that the
logged in user has a particular role before letting the view run at all.
Anyone who isn't logged in gets sent to the login page, and anyone who is
logged in but doesn't have the right role gets sent back to their profile
page rather than seeing the page they tried to reach. Every denied
attempt is written to the audit log so there's a record of who tried to
access what.
"""

from functools import wraps

from django.shortcuts import redirect

from admin_portal.audit import record_audit_log
from admin_portal.models import AuditLog


def _log_access_denied(request, required_role: str) -> None:
    record_audit_log(
        actor=request.user if request.user.is_authenticated else None,
        action=AuditLog.ACTION_ACCESS_DENIED,
        target_type="Request",
        target_id=None,
        target_repr=request.path,
        message=f"Access denied to {request.path}. Required role: {required_role}.",
    )


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Anonymous users get sent to login rather than a permission
        # error, so it's clear what to do next instead of just hitting a
        # dead end.
        if not request.user.is_authenticated:
            _log_access_denied(request, "Admin")
            return redirect("login")
        if not request.user.is_admin_role:
            _log_access_denied(request, "Admin")
            return redirect("profile")
        return view_func(request, *args, **kwargs)

    return wrapper


def submitter_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            _log_access_denied(request, "Submitter")
            return redirect("login")
        if not request.user.is_submitter_role:
            _log_access_denied(request, "Submitter")
            return redirect("profile")
        return view_func(request, *args, **kwargs)

    return wrapper


def support_staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            _log_access_denied(request, "Support Staff")
            return redirect("login")
        if not request.user.is_support_staff_role:
            _log_access_denied(request, "Support Staff")
            return redirect("profile")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_or_support_staff_required(view_func):
    # Used on pages both roles are allowed to see, for example the
    # dashboard, where a plain submitter shouldn't get in but either
    # staff type should.
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            _log_access_denied(request, "Admin or Support Staff")
            return redirect("login")
        if not request.user.is_admin_role and not request.user.is_support_staff_role:
            _log_access_denied(request, "Admin or Support Staff")
            return redirect("profile")
        return view_func(request, *args, **kwargs)

    return wrapper
