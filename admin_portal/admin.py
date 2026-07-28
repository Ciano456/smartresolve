# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib import admin

from admin_portal.models import AuditLog


# Lets audit log entries be browsed in the plain Django admin site as
# well as the app's own audit log page. Everything is read only here,
# audit records should never be editable once created.
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "severity",
        "flagged",
        "actor",
        "ip_address",
        "target_type",
        "target_repr",
    )
    list_filter = ("flagged", "severity", "action", "target_type", "created_at")
    search_fields = ("actor__email", "ip_address", "target_repr", "message")
    readonly_fields = (
        "actor",
        "action",
        "target_type",
        "target_id",
        "target_repr",
        "message",
        "ip_address",
        "severity",
        "flagged",
        "created_at",
    )
