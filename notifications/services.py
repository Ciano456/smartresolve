# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import logging
from typing import Any

from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from .exceptions import GraphConfigurationError, GraphDeliveryError
from .graph_client import GraphClient
from .models import NotificationEvent

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, client: GraphClient | None = None) -> None:
        self.client = client or GraphClient()

    def _render_templates(
        self,
        subject_template: str,
        text_template: str,
        html_template: str | None,
        render_context: dict[str, Any],
    ) -> tuple[str, str, str]:
        subject = render_to_string(subject_template, render_context).strip()
        text_body = render_to_string(text_template, render_context).strip()
        html_body = (
            render_to_string(html_template, render_context).strip()
            if html_template
            else ""
        )
        return subject, text_body, html_body

    def _create_event(
        self,
        *,
        event_type: str,
        recipient_email: str,
        created_by_id: int | None,
        subject: str,
        text_body: str,
        html_body: str,
        delivery_status: str,
        error_message: str = "",
    ) -> NotificationEvent:
        return NotificationEvent.objects.create(
            event_type=event_type,
            recipient_email=recipient_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            delivery_status=delivery_status,
            error_message=error_message,
            created_by_id=created_by_id,
        )

    def send_notification(
        self,
        *,
        event_type: str,
        recipient_email: str,
        subject_template: str,
        text_template: str,
        context: dict[str, Any] | None = None,
        html_template: str | None = None,
        created_by_id: int | None = None,
    ) -> NotificationEvent:
        render_context = context or {}

        try:
            subject, text_body, html_body = self._render_templates(
                subject_template,
                text_template,
                html_template,
                render_context,
            )
        except (TemplateDoesNotExist, ValueError) as exc:
            logger.exception(
                "Notification template rendering failed for %s", recipient_email
            )
            return self._create_event(
                event_type=event_type,
                recipient_email=recipient_email,
                created_by_id=created_by_id,
                subject="",
                text_body="",
                html_body="",
                delivery_status=NotificationEvent.DeliveryStatus.FAILED,
                error_message=str(exc),
            )

        notification_event = self._create_event(
            event_type=event_type,
            recipient_email=recipient_email,
            created_by_id=created_by_id,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            delivery_status=NotificationEvent.DeliveryStatus.SKIPPED,
        )

        try:
            result = self.client.send_mail(
                recipient_email=recipient_email,
                subject=subject,
                text_body=text_body,
                html_body=html_body,
            )
        except (GraphConfigurationError, GraphDeliveryError, ValueError) as exc:
            logger.exception("Notification delivery failed for %s", recipient_email)
            notification_event.delivery_status = NotificationEvent.DeliveryStatus.FAILED
            notification_event.error_message = str(exc)
            notification_event.save(
                update_fields=["delivery_status", "error_message", "updated_at"]
            )
            return notification_event

        notification_event.delivery_status = NotificationEvent.DeliveryStatus.SENT
        notification_event.provider_message_id = result.message_id
        notification_event.save(
            update_fields=[
                "delivery_status",
                "provider_message_id",
                "updated_at",
            ]
        )
        return notification_event
