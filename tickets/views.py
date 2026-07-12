# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from accounts.decorators import admin_or_support_staff_required, submitter_required
from . import notifications as ticket_notifications

from .forms import (
    StaffTicketCancelForm,
    StaffTicketAssignmentForm,
    StaffTicketCommentForm,
    StaffTicketPriorityForm,
    StaffTicketResolveForm,
    StaffTicketResolutionNoteForm,
    TicketAttachmentForm,
    TicketCommentForm,
    TicketForm,
)
from .models import (
    Ticket,
    TicketAttachment,
    TicketComment,
    TicketHistory,
    TicketPriority,
    TicketStatus,
    TicketSystem,
    TicketType,
)

TICKET_LIST_PAGE_SIZE = 25


def _can_download_attachment(user, attachment: TicketAttachment) -> bool:
    if user.is_admin_role or user.is_support_staff_role:
        return True
    return user.is_submitter_role and attachment.ticket.submitter_id == user.id


def _ticket_history_entries(ticket: Ticket) -> QuerySet[TicketHistory]:
    return ticket.history.select_related("changed_by").order_by("-created_at")


def _valid_filter_id(raw_value: str | None, queryset: QuerySet) -> int | None:
    if not raw_value or not raw_value.isdigit():
        return None
    value = int(raw_value)
    if queryset.filter(id=value).exists():
        return value
    return None


def _paginate_queryset(request: HttpRequest, queryset: QuerySet[object]) -> Page:
    paginator = Paginator(queryset, TICKET_LIST_PAGE_SIZE)
    return paginator.get_page(request.GET.get("page"))


def _staff_ticket_detail_context(
    ticket: Ticket,
    comment_form: StaffTicketCommentForm | None = None,
    assignment_form: StaffTicketAssignmentForm | None = None,
    priority_form: StaffTicketPriorityForm | None = None,
    resolution_note_form: StaffTicketResolutionNoteForm | None = None,
    resolve_form: StaffTicketResolveForm | None = None,
    cancel_form: StaffTicketCancelForm | None = None,
    status_error: str = "",
) -> dict:
    return {
        "ticket": ticket,
        "status_options": TicketStatus.objects.filter(
            is_active=True,
            is_closed=False,
        ).order_by("sort_order"),
        "comments": ticket.comments.select_related("author").order_by("-created_at"),
        "attachments": ticket.attachments.select_related("uploaded_by").order_by(
            "-created_at"
        ),
        "history_entries": _ticket_history_entries(ticket),
        "status_error": status_error,
        "comment_form": comment_form or StaffTicketCommentForm(),
        "assignment_form": assignment_form or StaffTicketAssignmentForm(instance=ticket),
        "priority_form": priority_form or StaffTicketPriorityForm(instance=ticket),
        "resolution_note_form": resolution_note_form or StaffTicketResolutionNoteForm(),
        "resolve_form": resolve_form or StaffTicketResolveForm(instance=ticket),
        "cancel_form": cancel_form or StaffTicketCancelForm(instance=ticket),
    }


@login_required
@submitter_required
def my_tickets(request):
    tickets = Ticket.objects.filter(submitter=request.user).select_related(
        "ticket_type",
        "ticket_system",
        "ticket_priority",
        "ticket_status",
        "assigned_to",
    )
    return render(request, "tickets/my_tickets.html", {"tickets": tickets})


@login_required
@submitter_required
def my_ticket_detail(request, id):
    ticket_detail = get_object_or_404(Ticket, id=id, submitter=request.user)
    comment_detail = (
        TicketComment.objects.filter(
            ticket_id=id,
            is_internal=False,
        )
        .select_related("author")
        .order_by("-created_at")
    )
    attachment_detail = TicketAttachment.objects.filter(
        ticket_id=id, uploaded_by=request.user
    )
    return render(
        request,
        "tickets/my_ticket_detail.html",
        {
            "ticket": ticket_detail,
            "comments": comment_detail,
            "attachments": attachment_detail,
            "comment_form": TicketCommentForm(),
            "attachment_form": TicketAttachmentForm(),
        },
    )


@login_required
@submitter_required
def ticket_create(request):
    if request.method == "GET":
        form = TicketForm()
        return render(request, "tickets/ticket_form.html", {"form": form})
    elif request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.submitter = request.user
            open_status = TicketStatus.objects.get(code="OPEN")
            ticket.ticket_status = open_status
            ticket.save()
            ticket_history = TicketHistory(
                ticket=ticket,
                changed_by=request.user,
                change_type="CREATED",
                field_name="ALL",
                old_value="",
                new_value=f"Ticket created with title: {ticket.title}",
            )
            ticket_history.save()
            ticket_notifications.notify_ticket_created(
                ticket,
                created_by_id=request.user.id,
            )
            return redirect("my_ticket_detail", id=ticket.id)
        else:
            return render(request, "tickets/ticket_form.html", {"form": form})


@login_required
@submitter_required
def comment_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, submitter=request.user)
    if request.method == "POST":
        comment_form = TicketCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            return redirect("my_ticket_detail", id=ticket_id)
        else:
            return render(
                request,
                "tickets/my_ticket_detail.html",
                {
                    "ticket": ticket,
                    "comment_form": comment_form,
                    "attachment_form": TicketAttachmentForm(),
                    "comments": TicketComment.objects.filter(
                        ticket_id=ticket_id,
                        is_internal=False,
                    ).select_related("author"),
                    "attachments": TicketAttachment.objects.filter(ticket_id=ticket_id),
                },
            )


@login_required
@submitter_required
def attachment_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, submitter=request.user)
    if request.method == "POST":
        attachment_form = TicketAttachmentForm(request.POST, request.FILES)
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.ticket_id = ticket_id
            attachment.uploaded_by = request.user
            attachment.original_filename = attachment.file.name
            attachment.save()
            return redirect("my_ticket_detail", id=ticket_id)
        else:
            return render(
                request,
                "tickets/my_ticket_detail.html",
                {
                    "ticket": ticket,
                    "comment_form": TicketCommentForm(),
                    "attachment_form": attachment_form,
                    "comments": TicketComment.objects.filter(
                        ticket_id=ticket_id,
                        is_internal=False,
                    ).select_related("author"),
                    "attachments": TicketAttachment.objects.filter(ticket_id=ticket_id),
                },
            )


@login_required
@admin_or_support_staff_required
def ticket_list(request):
    status_options = TicketStatus.objects.filter(is_active=True).order_by("sort_order")
    priority_options = TicketPriority.objects.filter(is_active=True).order_by(
        "sort_order"
    )
    type_options = TicketType.objects.filter(is_active=True).order_by("sort_order")
    system_options = TicketSystem.objects.filter(is_active=True).order_by("sort_order")
    User = get_user_model()
    submitter_options = (
        User.objects.filter(submitted_tickets__isnull=False)
        .distinct()
        .order_by("email")
    )
    assignee_options = (
        User.objects.filter(groups__name="Support Staff")
        .distinct()
        .order_by("email")
    )
    active_filters = {
        "status": request.GET.get("status", ""),
        "priority": request.GET.get("priority", ""),
        "type": request.GET.get("type", ""),
        "system": request.GET.get("system", ""),
        "submitter": request.GET.get("submitter", ""),
        "assigned_to": request.GET.get("assigned_to", ""),
        "created_from": request.GET.get("created_from", ""),
        "created_to": request.GET.get("created_to", ""),
    }
    tickets = Ticket.objects.select_related(
        "submitter",
        "assigned_to",
        "ticket_type",
        "ticket_system",
        "ticket_priority",
        "ticket_status",
    )

    status_id = _valid_filter_id(active_filters["status"], status_options)
    if status_id:
        tickets = tickets.filter(ticket_status_id=status_id)

    priority_id = _valid_filter_id(active_filters["priority"], priority_options)
    if priority_id:
        tickets = tickets.filter(ticket_priority_id=priority_id)

    type_id = _valid_filter_id(active_filters["type"], type_options)
    if type_id:
        tickets = tickets.filter(ticket_type_id=type_id)

    system_id = _valid_filter_id(active_filters["system"], system_options)
    if system_id:
        tickets = tickets.filter(ticket_system_id=system_id)

    submitter_id = _valid_filter_id(active_filters["submitter"], submitter_options)
    if submitter_id:
        tickets = tickets.filter(submitter_id=submitter_id)

    assignee_id = _valid_filter_id(active_filters["assigned_to"], assignee_options)
    if assignee_id:
        tickets = tickets.filter(assigned_to_id=assignee_id)

    created_from = parse_date(active_filters["created_from"])
    if created_from:
        tickets = tickets.filter(created_at__date__gte=created_from)

    created_to = parse_date(active_filters["created_to"])
    if created_to:
        tickets = tickets.filter(created_at__date__lte=created_to)

    tickets = tickets.order_by("-created_at")
    page_obj = _paginate_queryset(request, tickets)
    filter_query = request.GET.copy()
    filter_query.pop("page", None)
    return render(
        request,
        "tickets/ticket_list.html",
        {
            "tickets": page_obj,
            "page_obj": page_obj,
            "filter_query": filter_query.urlencode(),
            "status_options": status_options,
            "priority_options": priority_options,
            "type_options": type_options,
            "system_options": system_options,
            "submitter_options": submitter_options,
            "assignee_options": assignee_options,
            "active_filters": active_filters,
        },
    )


@login_required
@admin_or_support_staff_required
def ticket_detail(request, id):
    ticket_detail = get_object_or_404(
        Ticket.objects.select_related(
            "submitter",
            "assigned_to",
            "ticket_type",
            "ticket_system",
            "ticket_priority",
            "ticket_status",
        ).prefetch_related(
            "comments__author",
            "attachments__uploaded_by",
        ),
        id=id,
    )
    status_options = TicketStatus.objects.filter(
        is_active=True,
        is_closed=False,
    ).order_by("sort_order")

    if request.method == "POST":
        status_id = request.POST.get("ticket_status")
        new_status = status_options.filter(id=status_id).first()
        if new_status is None:
            return render(
                request,
                "tickets/ticket_detail.html",
                _staff_ticket_detail_context(
                    ticket_detail,
                    status_error="Select a valid ticket status.",
                ),
                status=400,
            )
        if new_status.is_closed:
            return render(
                request,
                "tickets/ticket_detail.html",
                _staff_ticket_detail_context(
                    ticket_detail,
                    status_error=(
                        "Use Resolve Ticket or Cancel Ticket to close this ticket "
                        "with the required note."
                    ),
                ),
                status=400,
            )

        old_status = ticket_detail.ticket_status
        if old_status.id != new_status.id:
            ticket_detail.ticket_status = new_status
            ticket_detail.save()
            TicketHistory.objects.create(
                ticket=ticket_detail,
                changed_by=request.user,
                change_type="STATUS_CHANGED",
                field_name="ticket_status",
                old_value=old_status.name,
                new_value=new_status.name,
            )
            ticket_notifications.notify_ticket_status_changed(
                ticket_detail,
                previous_status_name=old_status.name,
                created_by_id=request.user.id,
            )
        return redirect("ticket_detail", id=ticket_detail.id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket_detail),
    )


@login_required
@admin_or_support_staff_required
def ticket_assignment_update(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("assigned_to"),
        id=ticket_id,
    )
    if request.method != "POST":
        return redirect("ticket_detail", id=ticket_id)

    old_assignee = ticket.assigned_to
    form = StaffTicketAssignmentForm(request.POST, instance=ticket)
    if form.is_valid():
        updated_ticket = form.save(commit=False)
        new_assignee = updated_ticket.assigned_to
        if old_assignee != new_assignee:
            updated_ticket.save(update_fields=["assigned_to", "updated_at"])
            TicketHistory.objects.create(
                ticket=updated_ticket,
                changed_by=request.user,
                change_type="ASSIGNMENT_CHANGED",
                field_name="assigned_to",
                old_value=str(old_assignee) if old_assignee else "Unassigned",
                new_value=str(new_assignee) if new_assignee else "Unassigned",
            )
            ticket_notifications.notify_ticket_assigned(
                updated_ticket,
                created_by_id=request.user.id,
            )
        return redirect("ticket_detail", id=ticket_id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket, assignment_form=form),
        status=400,
    )


@login_required
@admin_or_support_staff_required
def ticket_priority_update(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("ticket_priority"),
        id=ticket_id,
    )
    if request.method != "POST":
        return redirect("ticket_detail", id=ticket_id)

    old_priority = ticket.ticket_priority
    form = StaffTicketPriorityForm(request.POST, instance=ticket)
    if form.is_valid():
        updated_ticket = form.save(commit=False)
        new_priority = updated_ticket.ticket_priority
        if old_priority != new_priority:
            updated_ticket.save(update_fields=["ticket_priority", "updated_at"])
            TicketHistory.objects.create(
                ticket=updated_ticket,
                changed_by=request.user,
                change_type="PRIORITY_CHANGED",
                field_name="ticket_priority",
                old_value=old_priority.name,
                new_value=new_priority.name,
            )
        return redirect("ticket_detail", id=ticket_id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket, priority_form=form),
        status=400,
    )


@login_required
@admin_or_support_staff_required
def ticket_resolve(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("ticket_status"),
        id=ticket_id,
    )
    if request.method != "POST":
        return redirect("ticket_detail", id=ticket_id)

    form = StaffTicketResolveForm(request.POST, instance=ticket)
    if ticket.ticket_status.is_closed:
        form.add_error(
            None,
            "Closed or cancelled tickets cannot be resolved again.",
        )
    if form.is_valid():
        closed_status = TicketStatus.objects.get(code="CLOSED")
        old_status = ticket.ticket_status
        updated_ticket = form.save(commit=False)
        updated_ticket.ticket_status = closed_status
        updated_ticket.cancellation_reason = ""
        updated_ticket.save(
            update_fields=[
                "resolution_summary",
                "cancellation_reason",
                "ticket_status",
                "closed_at",
                "updated_at",
            ]
        )
        TicketHistory.objects.create(
            ticket=updated_ticket,
            changed_by=request.user,
            change_type="RESOLVED",
            field_name="ticket_status",
                old_value=old_status.name,
                new_value=closed_status.name,
            )
        ticket_notifications.notify_ticket_resolved(
            updated_ticket,
            created_by_id=request.user.id,
        )
        return redirect("ticket_detail", id=ticket_id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket, resolve_form=form),
        status=400,
    )


@login_required
@admin_or_support_staff_required
def ticket_cancel(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("ticket_status"),
        id=ticket_id,
    )
    if request.method != "POST":
        return redirect("ticket_detail", id=ticket_id)

    form = StaffTicketCancelForm(request.POST, instance=ticket)
    if ticket.ticket_status.is_closed:
        form.add_error(
            None,
            "Closed or cancelled tickets cannot be cancelled again.",
        )
    if form.is_valid():
        cancelled_status = TicketStatus.objects.get(code="CANCELLED")
        old_status = ticket.ticket_status
        updated_ticket = form.save(commit=False)
        updated_ticket.ticket_status = cancelled_status
        updated_ticket.resolution_summary = ""
        updated_ticket.save(
            update_fields=[
                "resolution_summary",
                "cancellation_reason",
                "ticket_status",
                "closed_at",
                "updated_at",
            ]
        )
        TicketHistory.objects.create(
            ticket=updated_ticket,
            changed_by=request.user,
            change_type="CANCELLED",
            field_name="ticket_status",
                old_value=old_status.name,
                new_value=cancelled_status.name,
            )
        ticket_notifications.notify_ticket_cancelled(
            updated_ticket,
            created_by_id=request.user.id,
        )
        return redirect("ticket_detail", id=ticket_id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket, cancel_form=form),
        status=400,
    )


@login_required
@admin_or_support_staff_required
def ticket_resolution_note_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method != "POST":
        return redirect("ticket_detail", id=ticket_id)

    resolution_note_form = StaffTicketResolutionNoteForm(request.POST)
    if resolution_note_form.is_valid():
        resolution_note = resolution_note_form.save(commit=False)
        resolution_note.ticket = ticket
        resolution_note.author = request.user
        resolution_note.is_internal = False
        resolution_note.save()
        ticket_notifications.notify_public_comment(
            ticket,
            comment=resolution_note,
            created_by_id=request.user.id,
        )
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=request.user,
            change_type="RESOLUTION_NOTE_ADDED",
            field_name="comments",
            old_value="",
            new_value="Resolution note added",
        )
        return redirect("ticket_detail", id=ticket_id)

    return render(
        request,
        "tickets/ticket_detail.html",
        _staff_ticket_detail_context(ticket, resolution_note_form=resolution_note_form),
        status=400,
    )


@login_required
@admin_or_support_staff_required
def staff_comment_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        comment_form = StaffTicketCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            if not comment.is_internal:
                ticket_notifications.notify_public_comment(
                    ticket,
                    comment=comment,
                    created_by_id=request.user.id,
                )
            return redirect("ticket_detail", id=ticket_id)

        return render(
            request,
            "tickets/ticket_detail.html",
            _staff_ticket_detail_context(ticket, comment_form=comment_form),
            status=400,
        )

    return redirect("ticket_detail", id=ticket_id)


@login_required
@admin_or_support_staff_required
def comment_list(request, ticket_id):
    comments = TicketComment.objects.filter(ticket_id=ticket_id)
    return render(request, "tickets/comment_list.html", {"comments": comments})


@login_required
@admin_or_support_staff_required
def attachment_list(request, ticket_id):
    attachments = TicketAttachment.objects.filter(ticket_id=ticket_id)
    return render(request, "tickets/attachment_list.html", {"attachments": attachments})


@login_required
def attachment_download(request, attachment_id):
    attachment = get_object_or_404(
        TicketAttachment.objects.select_related("ticket__submitter"),
        id=attachment_id,
    )
    if not _can_download_attachment(request.user, attachment):
        return redirect("profile")

    return FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.original_filename,
    )
