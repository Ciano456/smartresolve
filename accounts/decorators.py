# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

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
        # Redirect anonymous users back to login before checking their role.
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
