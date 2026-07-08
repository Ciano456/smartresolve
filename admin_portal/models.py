# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_USER_CREATED = "USER_CREATED"
    ACTION_USER_UPDATED = "USER_UPDATED"
    ACTION_USER_DEACTIVATED = "USER_DEACTIVATED"
    ACTION_USER_REACTIVATED = "USER_REACTIVATED"

    ACTION_CHOICES = [
        (ACTION_USER_CREATED, "User created"),
        (ACTION_USER_UPDATED, "User updated"),
        (ACTION_USER_DEACTIVATED, "User deactivated"),
        (ACTION_USER_REACTIVATED, "User reactivated"),
    ]

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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} - {self.target_repr}"
