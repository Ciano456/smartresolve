# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import logging

from accounts.models import User
from django.http import HttpRequest

from admin_portal.models import AuditLog
from admin_portal.security import audit_event_defaults, get_client_ip

logger = logging.getLogger(__name__)


def record_audit_log(
    *,
    actor: User | None,
    action: str,
    target_type: str,
    target_id: int | None,
    target_repr: str,
    message: str,
    request: HttpRequest | None = None,
    severity: str | None = None,
    flagged: bool | None = None,
) -> None:
    # The one place in the whole app that writes to the audit log, so
    # every caller (decorators, views, the AI override flow) goes through
    # the same function instead of creating AuditLog rows directly.
    default_severity, default_flagged = audit_event_defaults(action)
    try:
        AuditLog.objects.create(
            actor=actor,
            action=action,
            target_type=target_type[:100],
            target_id=target_id,
            target_repr=target_repr[:255],
            message=message,
            ip_address=get_client_ip(request),
            severity=severity or default_severity,
            flagged=default_flagged if flagged is None else flagged,
        )
    except Exception:
        # Writing the audit log should never be the reason a real user
        # action fails. If saving the log entry itself goes wrong, that
        # gets logged for debugging but the original action still
        # succeeds.
        logger.exception("Failed to record audit log entry.")
