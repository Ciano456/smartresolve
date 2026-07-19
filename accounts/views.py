# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from accounts.models import User
from accounts.security import (
    clear_failed_logins,
    is_login_blocked,
    record_failed_login,
)
from admin_portal.audit import record_audit_log
from admin_portal.models import AuditLog
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _get_post_login_redirect(user: User) -> str:
    # Staff and admins land on the dashboard since that's what they
    # actually need day to day. Everyone else just goes to their profile.
    if user.is_admin_role or user.is_support_staff_role:
        return "dashboard"
    return "profile"


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # Email is the username field for this project, so it gets
        # passed into authenticate() as the username.
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        if is_login_blocked(request, email):
            # Blocked before even checking the password, this account or
            # IP has already gone over the failed attempt limit recently.
            record_audit_log(
                actor=None,
                action=AuditLog.ACTION_LOGIN_RATE_LIMITED,
                target_type="User",
                target_id=None,
                target_repr=email or "<blank>",
                message="Login attempt blocked by the configured rate limit.",
            )
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)
        if user:
            clear_failed_logins(request, email)
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect(_get_post_login_redirect(user))
        # Login failed, so this gets logged and counted towards the rate
        # limit. The same generic error message is shown either way, so
        # nobody can tell from the response whether the email exists or
        # the password was just wrong.
        record_audit_log(
            actor=None,
            action=AuditLog.ACTION_LOGIN_FAILED,
            target_type="User",
            target_id=None,
            target_repr=email or "<blank>",
            message=f"Failed login attempt for {email or '<blank>'}.",
        )
        if record_failed_login(request, email):
            record_audit_log(
                actor=None,
                action=AuditLog.ACTION_LOGIN_RATE_LIMITED,
                target_type="User",
                target_id=None,
                target_repr=email or "<blank>",
                message="Login rate limit activated after repeated failures.",
            )
        messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect("login")
    return redirect("profile")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/profile.html")
