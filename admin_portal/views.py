# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from accounts.models import User
from admin_portal.forms import (
    AdminPortalUserCreateForm,
    AdminPortalUserEditForm,
    TicketPriorityLookupForm,
    TicketStatusLookupForm,
    TicketSystemLookupForm,
    TicketTypeLookupForm,
)
from admin_portal.models import AuditLog
from tickets.models import (
    Ticket,
    TicketHistory,
    TicketPriority,
    TicketStatus,
    TicketSystem,
    TicketType,
)

AUDIT_LOG_LIMIT = 100
ADMIN_TICKET_LIST_PAGE_SIZE = 25

LOOKUP_CONFIG = {
    "types": {
        "model": TicketType,
        "form": TicketTypeLookupForm,
        "title": "Ticket Types",
        "singular": "Ticket Type",
        "description": "Manage the request categories users choose when creating tickets.",
    },
    "systems": {
        "model": TicketSystem,
        "form": TicketSystemLookupForm,
        "title": "Ticket Systems",
        "singular": "Ticket System",
        "description": "Manage the systems or technology areas tickets can be linked to.",
    },
    "priorities": {
        "model": TicketPriority,
        "form": TicketPriorityLookupForm,
        "title": "Ticket Priorities",
        "singular": "Ticket Priority",
        "description": "Manage the priority values used to triage support work.",
    },
    "statuses": {
        "model": TicketStatus,
        "form": TicketStatusLookupForm,
        "title": "Ticket Statuses",
        "singular": "Ticket Status",
        "description": "Manage ticket lifecycle statuses and closed-state behaviour.",
    },
}


def _lookup_config(lookup_slug: str) -> dict:
    try:
        return LOOKUP_CONFIG[lookup_slug]
    except KeyError as exc:
        raise Http404("Lookup type not found.") from exc


def _record_user_audit_log(
    *,
    actor: User,
    action: str,
    target_user: User,
    message: str,
) -> None:
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type="User",
        target_id=target_user.id,
        target_repr=target_user.email,
        message=message,
    )


def _build_audit_log_entries() -> list[dict]:
    audit_logs = AuditLog.objects.select_related("actor").order_by("-created_at")[
        :AUDIT_LOG_LIMIT
    ]
    ticket_history = TicketHistory.objects.select_related(
        "ticket",
        "changed_by",
    ).order_by("-created_at")[:AUDIT_LOG_LIMIT]

    entries = [
        {
            "created_at": log.created_at,
            "source": "Admin",
            "action": log.get_action_display(),
            "actor": log.actor,
            "target": log.target_repr,
            "message": log.message,
        }
        for log in audit_logs
    ]
    entries.extend(
        {
            "created_at": history.created_at,
            "source": "Ticket",
            "action": history.change_type.replace("_", " ").title(),
            "actor": history.changed_by,
            "target": history.ticket.ticket_number,
            "message": (
                f"{history.field_name}: {history.old_value} -> {history.new_value}"
                if history.field_name
                else history.new_value
            ),
        }
        for history in ticket_history
    )

    return sorted(
        entries,
        key=lambda entry: entry["created_at"],
        reverse=True,
    )[:AUDIT_LOG_LIMIT]


def _active_admin_count() -> int:
    return User.objects.filter(is_active=True, groups__name="Admin").distinct().count()


@admin_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    ticket_stats = Ticket.objects.aggregate(
        total_tickets=Count("id"),
        open_tickets=Count("id", filter=Q(ticket_status__is_closed=False)),
        closed_tickets=Count("id", filter=Q(ticket_status__is_closed=True)),
    )
    return render(
        request,
        "admin_portal/admin_dashboard.html",
        {"ticket_stats": ticket_stats},
    )


@admin_required
def audit_log_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "admin_portal/audit_log_list.html",
        {"audit_entries": _build_audit_log_entries()},
    )


@admin_required
def admin_ticket_list(request: HttpRequest) -> HttpResponse:
    tickets = Ticket.objects.select_related(
        "submitter",
        "assigned_to",
        "ticket_type",
        "ticket_system",
        "ticket_priority",
        "ticket_status",
    ).order_by("-created_at")
    paginator = Paginator(tickets, ADMIN_TICKET_LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "admin_portal/ticket_list.html",
        {
            "tickets": page_obj,
            "page_obj": page_obj,
        },
    )


@admin_required
def lookup_list(request: HttpRequest, lookup_slug: str) -> HttpResponse:
    config = _lookup_config(lookup_slug)
    lookup_values = config["model"].objects.order_by("sort_order", "name")
    return render(
        request,
        "admin_portal/lookup_list.html",
        {
            "lookup_slug": lookup_slug,
            "lookup_config": config,
            "lookup_values": lookup_values,
        },
    )


@admin_required
def lookup_create(request: HttpRequest, lookup_slug: str) -> HttpResponse:
    config = _lookup_config(lookup_slug)
    form_class = config["form"]
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lookup_list", lookup_slug=lookup_slug)
    else:
        form = form_class()

    return render(
        request,
        "admin_portal/lookup_form.html",
        {
            "lookup_slug": lookup_slug,
            "lookup_config": config,
            "form": form,
            "form_mode": "create",
            "submit_label": f"Create {config['singular']}",
        },
    )


@admin_required
def lookup_edit(
    request: HttpRequest,
    lookup_slug: str,
    lookup_id: int,
) -> HttpResponse:
    config = _lookup_config(lookup_slug)
    lookup_value = get_object_or_404(config["model"], id=lookup_id)
    form_class = config["form"]
    if request.method == "POST":
        form = form_class(request.POST, instance=lookup_value)
        if form.is_valid():
            form.save()
            return redirect("lookup_list", lookup_slug=lookup_slug)
    else:
        form = form_class(instance=lookup_value)

    return render(
        request,
        "admin_portal/lookup_form.html",
        {
            "lookup_slug": lookup_slug,
            "lookup_config": config,
            "lookup_value": lookup_value,
            "form": form,
            "form_mode": "edit",
            "submit_label": f"Save {config['singular']}",
        },
    )


@admin_required
@require_POST
def lookup_toggle_active(
    request: HttpRequest,
    lookup_slug: str,
    lookup_id: int,
) -> HttpResponse:
    config = _lookup_config(lookup_slug)
    lookup_value = get_object_or_404(config["model"], id=lookup_id)
    lookup_value.is_active = not lookup_value.is_active
    lookup_value.save(update_fields=["is_active"])
    return redirect("lookup_list", lookup_slug=lookup_slug)


@admin_required
def user_list(request):
    users = User.objects.prefetch_related("groups")
    return render(request, "admin_portal/user_list.html", {"users": users})


@admin_required
def user_detail(request, user_id):
    managed_user = get_object_or_404(User, id=user_id)
    return render(
        request,
        "admin_portal/user_detail.html",
        {"managed_user": managed_user},
    )


@admin_required
def user_create(request):
    if request.method == "POST":
        form = AdminPortalUserCreateForm(request.POST)
        if form.is_valid():
            created_user = form.save()
            _record_user_audit_log(
                actor=request.user,
                action=AuditLog.ACTION_USER_CREATED,
                target_user=created_user,
                message=f"Created user {created_user.email}.",
            )
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
    managed_user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AdminPortalUserEditForm(request.POST, instance=managed_user)
        if form.is_valid():
            updated_user = form.save()
            _record_user_audit_log(
                actor=request.user,
                action=AuditLog.ACTION_USER_UPDATED,
                target_user=updated_user,
                message=f"Updated user {updated_user.email}.",
            )
            return redirect("user_detail", user_id=managed_user.id)
    else:
        form = AdminPortalUserEditForm(instance=managed_user)

    return render(
        request,
        "admin_portal/user_form.html",
        {
            "form": form,
            "managed_user": managed_user,
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
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("user_detail", user_id=user.id)
    if user.is_admin_role and _active_admin_count() <= 1:
        messages.error(request, "You cannot deactivate the last active admin account.")
        return redirect("user_detail", user_id=user.id)
    user.is_active = False
    user.save()
    _record_user_audit_log(
        actor=request.user,
        action=AuditLog.ACTION_USER_DEACTIVATED,
        target_user=user,
        message=f"Deactivated user {user.email}.",
    )
    return redirect("user_detail", user_id=user.id)


@admin_required
@require_POST
def user_reactivate(request, user_id):
    # Reactivation mirrors deactivation and returns the admin to the user detail page.
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    _record_user_audit_log(
        actor=request.user,
        action=AuditLog.ACTION_USER_REACTIVATED,
        target_user=user,
        message=f"Reactivated user {user.email}.",
    )
    return redirect("user_detail", user_id=user.id)
