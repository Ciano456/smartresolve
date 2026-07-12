# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import logging
from collections.abc import Iterable

from django.conf import settings

from notifications.models import NotificationEvent
from notifications.services import NotificationService
from .models import Ticket

logger = logging.getLogger(__name__)

SUBJECT_TEMPLATE = "notifications/emails/subject.txt"
TEXT_TEMPLATE = "notifications/emails/body.txt"
HTML_TEMPLATE = "notifications/emails/generic_notification.html"


def _recipient_name(email: str, label: str | None = None) -> str:
    if label:
        return label
    local_part = email.split("@", maxsplit=1)[0]
    return local_part.replace(".", " ").replace("_", " ").title()


def _user_display_label(user) -> str:
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.email


def _unique_emails(emails: Iterable[str | None]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for email in emails:
        cleaned_email = (email or "").strip()
        if not cleaned_email or cleaned_email in seen:
            continue
        seen.add(cleaned_email)
        unique.append(cleaned_email)
    return unique


def _support_inbox() -> str:
    return settings.IT_SUPPORT_EMAIL.strip()


def _send_to_support_inbox(ticket: Ticket, *, event_type: str, subject: str, body: str, created_by_id: int | None) -> None:
    support_inbox = _support_inbox()
    if not support_inbox:
        logger.warning(
            "IT support inbox is not configured; skipping %s email.",
            event_type.lower().replace("_", " "),
        )
        return

    _send_ticket_notification(
        event_type=event_type,
        recipient_email=support_inbox,
        recipient_label="IT Support",
        subject=subject,
        body=body,
        created_by_id=created_by_id,
        ticket=ticket,
    )


def _send_ticket_notification(
    *,
    event_type: str,
    recipient_email: str,
    recipient_label: str | None,
    subject: str,
    body: str,
    created_by_id: int | None,
    ticket,
) -> None:
    NotificationService().send_notification(
        event_type=event_type,
        recipient_email=recipient_email,
        subject_template=SUBJECT_TEMPLATE,
        text_template=TEXT_TEMPLATE,
        html_template=HTML_TEMPLATE,
        context={
            "subject": subject,
            "recipient_name": _recipient_name(recipient_email, recipient_label),
            "body": body,
            "ticket_number": ticket.ticket_number,
            "ticket_title": ticket.title,
            "ticket_status": ticket.ticket_status.name,
            "ticket_priority": ticket.ticket_priority.name,
            "ticket_type": ticket.ticket_type.name,
        },
        created_by_id=created_by_id,
    )


def notify_ticket_created(ticket, *, created_by_id: int | None = None) -> None:
    support_inbox = _support_inbox()
    recipients = _unique_emails(
        [ticket.assigned_to.email if ticket.assigned_to_id else None, support_inbox]
    )
    if not recipients:
        logger.warning(
            "Ticket created notification skipped because no recipients were available."
        )
        return

    subject = f"New ticket created: {ticket.ticket_number}"
    body = (
        "A new ticket has been logged in SmartResolve. "
        "Open the ticket to review the initial request and take ownership."
    )
    for recipient_email in recipients:
        label = "IT Support" if recipient_email == support_inbox else None
        _send_ticket_notification(
            event_type=NotificationEvent.EventType.TICKET_CREATED,
            recipient_email=recipient_email,
            recipient_label=label,
            subject=subject,
            body=body,
            created_by_id=created_by_id,
            ticket=ticket,
        )


def notify_ticket_assigned(ticket, *, created_by_id: int | None = None) -> None:
    if not ticket.assigned_to_id:
        return

    _send_ticket_notification(
        event_type=NotificationEvent.EventType.TICKET_ASSIGNED,
        recipient_email=ticket.assigned_to.email,
        recipient_label=_user_display_label(ticket.assigned_to),
        subject=f"Ticket assigned: {ticket.ticket_number}",
        body="A ticket has been assigned to you. Open it in SmartResolve to review the details.",
        created_by_id=created_by_id,
        ticket=ticket,
    )


def notify_ticket_status_changed(
    ticket,
    *,
    previous_status_name: str,
    created_by_id: int | None = None,
) -> None:
    if ticket.ticket_status.is_closed:
        return

    _send_ticket_notification(
        event_type=NotificationEvent.EventType.TICKET_UPDATED,
        recipient_email=ticket.submitter.email,
        recipient_label=_user_display_label(ticket.submitter),
        subject=f"Ticket updated: {ticket.ticket_number}",
        body=(
            f"Your ticket status changed from {previous_status_name} to "
            f"{ticket.ticket_status.name}."
        ),
        created_by_id=created_by_id,
        ticket=ticket,
    )


def notify_public_comment(
    ticket,
    *,
    comment,
    created_by_id: int | None = None,
) -> None:
    recipients = _unique_emails(
        [
            ticket.submitter.email if comment.author_id != ticket.submitter_id else None,
            (
                ticket.assigned_to.email
                if ticket.assigned_to_id and comment.author_id != ticket.assigned_to_id
                else None
            ),
        ]
    )
    if not recipients:
        return

    subject = f"New comment on ticket: {ticket.ticket_number}"
    body = (
        "A new public comment has been added to your ticket. "
        "Open SmartResolve to review it."
    )
    for recipient_email in recipients:
        _send_ticket_notification(
            event_type=NotificationEvent.EventType.TICKET_COMMENTED,
            recipient_email=recipient_email,
            recipient_label=None,
            subject=subject,
            body=body,
            created_by_id=created_by_id,
            ticket=ticket,
        )


def notify_ticket_resolved(ticket, *, created_by_id: int | None = None) -> None:
    _send_to_support_inbox(
        ticket,
        event_type=NotificationEvent.EventType.TICKET_RESOLVED,
        subject=f"Ticket resolved: {ticket.ticket_number}",
        body=(
            "A ticket has been resolved. Open SmartResolve to review the "
            "resolution summary."
        ),
        created_by_id=created_by_id,
    )


def notify_ticket_cancelled(ticket, *, created_by_id: int | None = None) -> None:
    _send_to_support_inbox(
        ticket,
        event_type=NotificationEvent.EventType.TICKET_CANCELLED,
        subject=f"Ticket cancelled: {ticket.ticket_number}",
        body=(
            "A ticket has been cancelled. Open SmartResolve to review the "
            "cancellation reason."
        ),
        created_by_id=created_by_id,
    )
