# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    # One row per action worth keeping a record of. This backs the audit
    # trail described in the security requirements: failed logins, access
    # denials, admin actions on users and tickets, and AI category
    # overrides all end up here through record_audit_log() in audit.py.
    ACTION_LOGIN_FAILED = "LOGIN_FAILED"
    ACTION_LOGIN_RATE_LIMITED = "LOGIN_RATE_LIMITED"
    ACTION_ACCESS_DENIED = "ACCESS_DENIED"
    ACTION_UPLOAD_BLOCKED = "UPLOAD_BLOCKED"
    ACTION_USER_CREATED = "USER_CREATED"
    ACTION_USER_UPDATED = "USER_UPDATED"
    ACTION_USER_DEACTIVATED = "USER_DEACTIVATED"
    ACTION_USER_REACTIVATED = "USER_REACTIVATED"
    ACTION_TICKET_CREATED = "TICKET_CREATED"
    ACTION_TICKET_STATUS_CHANGED = "TICKET_STATUS_CHANGED"
    ACTION_TICKET_ASSIGNED = "TICKET_ASSIGNED"
    ACTION_TICKET_PRIORITY_CHANGED = "TICKET_PRIORITY_CHANGED"
    ACTION_TICKET_RESOLVED = "TICKET_RESOLVED"
    ACTION_TICKET_CANCELLED = "TICKET_CANCELLED"
    ACTION_TICKET_COMMENT_ADDED = "TICKET_COMMENT_ADDED"
    ACTION_RESOLUTION_NOTE_ADDED = "RESOLUTION_NOTE_ADDED"
    ACTION_AI_CATEGORY_OVERRIDDEN = "AI_CATEGORY_OVERRIDDEN"
    ACTION_SECURITY_TICKET_FLAGGED = "SECURITY_TICKET_FLAGGED"

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    ACTION_CHOICES = [
        (ACTION_LOGIN_FAILED, "Login failed"),
        (ACTION_LOGIN_RATE_LIMITED, "Login rate limited"),
        (ACTION_ACCESS_DENIED, "Access denied"),
        (ACTION_UPLOAD_BLOCKED, "Upload blocked"),
        (ACTION_USER_CREATED, "User created"),
        (ACTION_USER_UPDATED, "User updated"),
        (ACTION_USER_DEACTIVATED, "User deactivated"),
        (ACTION_USER_REACTIVATED, "User reactivated"),
        (ACTION_TICKET_CREATED, "Ticket created"),
        (ACTION_TICKET_STATUS_CHANGED, "Ticket status changed"),
        (ACTION_TICKET_ASSIGNED, "Ticket assigned"),
        (ACTION_TICKET_PRIORITY_CHANGED, "Ticket priority changed"),
        (ACTION_TICKET_RESOLVED, "Ticket resolved"),
        (ACTION_TICKET_CANCELLED, "Ticket cancelled"),
        (ACTION_TICKET_COMMENT_ADDED, "Ticket comment added"),
        (ACTION_RESOLUTION_NOTE_ADDED, "Resolution note added"),
        (ACTION_AI_CATEGORY_OVERRIDDEN, "AI category overridden"),
        (ACTION_SECURITY_TICKET_FLAGGED, "Security ticket flagged"),
    ]

    # Null and blank because some events, like a failed login for an
    # email that doesn't even belong to a real account, don't have a
    # logged in user to attach as the actor.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="admin_audit_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=100)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_repr = models.CharField(max_length=255)
    message = models.TextField()
    # ip_address, severity and flagged are what the FR10 security
    # dashboard is built on top of. ip_address is nullable because not
    # every event has a request behind it, for example a system generated
    # entry. severity and flagged are worked out by admin_portal/security.py
    # at the time the entry is written, using audit_event_defaults and
    # security_ticket_severity, rather than being decided later.
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_LOW,
    )
    flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        # Both the dashboard and the audit log page filter on flagged and
        # severity a lot, so these indexes keep those queries fast as the
        # table grows.
        indexes = [
            models.Index(fields=["flagged", "-created_at"]),
            models.Index(fields=["severity", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.target_repr}"
