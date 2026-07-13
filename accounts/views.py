# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from accounts.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _get_post_login_redirect(user: User) -> str:
    if user.is_admin_role or user.is_support_staff_role:
        return "dashboard"
    return "profile"


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # Email is the username field for this project, so it is passed into authenticate().
        user = authenticate(
            request, username=request.POST["email"], password=request.POST["password"]
        )
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect(_get_post_login_redirect(user))
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
