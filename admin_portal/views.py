# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.shortcuts import render, redirect
from accounts.decorators import admin_required
from accounts.models import User
from django.shortcuts import get_object_or_404
from admin_portal.forms import AdminPortalUserCreateForm, AdminPortalUserEditForm
from django.views.decorators.http import require_POST

# Landing page view for the admin portal
@admin_required
def admin_dashboard(request):
    return render(request, "admin_portal/admin_dashboard.html")

@admin_required
def user_list(request):
    users = User.objects.all()
    return render(request, "admin_portal/user_list.html", {"users": users})

@admin_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "admin_portal/user_detail.html", {"user": user})


@admin_required
def user_create(request):
    if request.method == "POST":
        form = AdminPortalUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_list")
    else:
        form = AdminPortalUserCreateForm()

    # Create and edit share the same template, with the mode-specific labels passed in here.
    return render(
        request,
        "admin_portal/user_form.html",
        {
            "form": form,
            "form_mode": "create",
            "page_title": "Create User",
            "form_heading": "New User Details",
            "hero_text": "Add a new SmartResolve user, set their initial role, and control whether the account is active from day one.",
            "flow_text": "Accounts are created by administrators and immediately available in the user list after save.",
            "submit_label": "Create User",
        },
    )

@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AdminPortalUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_detail", user_id=user.id)
    else:
        form = AdminPortalUserEditForm(instance=user)

    return render(
        request,
        "admin_portal/user_form.html",
        {
            "form": form,
            "user": user,
            "form_mode": "edit",
            "page_title": "Edit User",
            "form_heading": "Update User Details",
            "hero_text": "Update user account details, change the assigned role, and control whether the SmartResolve account remains active.",
            "flow_text": "Edits made here update the existing account and return you to the user detail view after save.",
            "submit_label": "Save Changes",
        },
    )

@admin_required
@require_POST
def user_deactivate(request, user_id):
    # Status changes are POST-only so they cannot be triggered by a simple link visit.
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect("user_detail", user_id=user.id)

@admin_required
@require_POST
def user_reactivate(request, user_id):
    # Reactivation mirrors deactivation and returns the admin to the user detail page.
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect("user_detail", user_id=user.id)
