# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Redirect anonymous users back to login before checking their role.
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_admin_role:
            return redirect("profile")
        return view_func(request, *args, **kwargs)
    return wrapper

def submitter_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_submitter_role:
            return redirect("profile")
        return view_func(request, *args, **kwargs)
    return wrapper

def support_staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_support_staff_role:
            return redirect("profile")
        return view_func(request, *args, **kwargs)
    return wrapper
