# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib import admin

from .models import NotificationEvent


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_type",
        "recipient_email",
        "delivery_status",
        "created_by",
        "created_at",
    )
    list_filter = ("event_type", "delivery_status", "created_at")
    search_fields = ("recipient_email", "subject", "error_message")
    ordering = ("-created_at",)
