# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.conf import settings
from django.db import models


class NotificationEvent(models.Model):
    class EventType(models.TextChoices):
        GENERIC = "GENERIC", "Generic"
        TICKET_CREATED = "TICKET_CREATED", "Ticket Created"
        TICKET_UPDATED = "TICKET_UPDATED", "Ticket Updated"
        TICKET_ASSIGNED = "TICKET_ASSIGNED", "Ticket Assigned"
        TICKET_COMMENTED = "TICKET_COMMENTED", "Ticket Commented"
        TICKET_RESOLVED = "TICKET_RESOLVED", "Ticket Resolved"
        TICKET_CANCELLED = "TICKET_CANCELLED", "Ticket Cancelled"

    class DeliveryStatus(models.TextChoices):
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"
        SKIPPED = "SKIPPED", "Skipped"

    event_type = models.CharField(max_length=50, choices=EventType.choices)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    text_body = models.TextField()
    html_body = models.TextField(blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.SKIPPED,
    )
    provider_message_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.event_type} to {self.recipient_email} ({self.delivery_status})"
