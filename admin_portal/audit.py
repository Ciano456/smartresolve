# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import logging

from accounts.models import User

from admin_portal.models import AuditLog

logger = logging.getLogger(__name__)


def record_audit_log(
    *,
    actor: User | None,
    action: str,
    target_type: str,
    target_id: int | None,
    target_repr: str,
    message: str,
) -> None:
    # The one place in the whole app that writes to the audit log, so
    # every caller (decorators, views, the AI override flow) goes through
    # the same function instead of creating AuditLog rows directly.
    try:
        AuditLog.objects.create(
            actor=actor,
            action=action,
            target_type=target_type[:100],
            target_id=target_id,
            target_repr=target_repr[:255],
            message=message,
        )
    except Exception:
        # Writing the audit log should never be the reason a real user
        # action fails. If saving the log entry itself goes wrong, that
        # gets logged for debugging but the original action still
        # succeeds.
        logger.exception("Failed to record audit log entry.")
