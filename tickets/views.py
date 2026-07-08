# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_or_support_staff_required, submitter_required

from .forms import TicketAttachmentForm, TicketCommentForm, TicketForm
from .models import Ticket, TicketAttachment, TicketComment, TicketHistory, TicketStatus


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
    comment_detail = TicketComment.objects.filter(ticket_id=id, author=request.user)
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
                    "comments": TicketComment.objects.filter(ticket_id=ticket_id),
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
                    "comments": TicketComment.objects.filter(ticket_id=ticket_id),
                    "attachments": TicketAttachment.objects.filter(ticket_id=ticket_id),
                },
            )


@login_required
@admin_or_support_staff_required
def ticket_list(request):
    tickets = Ticket.objects.select_related(
        "submitter",
        "assigned_to",
        "ticket_type",
        "ticket_system",
        "ticket_priority",
        "ticket_status",
    )
    return render(request, "tickets/ticket_list.html", {"tickets": tickets})


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
    status_options = TicketStatus.objects.filter(is_active=True).order_by("sort_order")
    comments = ticket_detail.comments.all().order_by("-created_at")
    attachments = ticket_detail.attachments.all().order_by("-created_at")

    if request.method == "POST":
        status_id = request.POST.get("ticket_status")
        new_status = status_options.filter(id=status_id).first()
        if new_status is None:
            return render(
                request,
                "tickets/ticket_detail.html",
                {
                    "ticket": ticket_detail,
                    "status_options": status_options,
                    "comments": comments,
                    "attachments": attachments,
                    "status_error": "Select a valid ticket status.",
                },
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
        return redirect("ticket_detail", id=ticket_detail.id)

    return render(
        request,
        "tickets/ticket_detail.html",
        {
            "ticket": ticket_detail,
            "status_options": status_options,
            "comments": comments,
            "attachments": attachments,
        },
    )


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
