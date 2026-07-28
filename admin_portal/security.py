# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import ipaddress

from django.conf import settings
from django.http import HttpRequest

from admin_portal.models import AuditLog

CRITICAL_KEYWORDS = {"breach", "compromised", "credential theft", "ransomware"}
HIGH_KEYWORDS = {
    "fraud",
    "lost device",
    "malware",
    "phishing",
    "scam",
    "spoofing",
    "stolen device",
    "unauthorised access",
    "virus",
}

AUDIT_EVENT_DEFAULTS = {
    AuditLog.ACTION_LOGIN_FAILED: (AuditLog.SEVERITY_LOW, False),
    AuditLog.ACTION_LOGIN_RATE_LIMITED: (AuditLog.SEVERITY_HIGH, True),
    AuditLog.ACTION_ACCESS_DENIED: (AuditLog.SEVERITY_MEDIUM, True),
    AuditLog.ACTION_UPLOAD_BLOCKED: (AuditLog.SEVERITY_HIGH, True),
    AuditLog.ACTION_SECURITY_TICKET_FLAGGED: (AuditLog.SEVERITY_MEDIUM, True),
}


def _valid_ip_address(value: str) -> str | None:
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def get_client_ip(request: HttpRequest | None) -> str | None:
    """Return a validated client address using the configured proxy policy."""
    if request is None:
        return None
    if settings.TRUST_PROXY_HEADERS:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        for candidate in forwarded_for.split(","):
            address = _valid_ip_address(candidate)
            if address:
                return address
    return _valid_ip_address(request.META.get("REMOTE_ADDR", ""))


def audit_event_defaults(action: str) -> tuple[str, bool]:
    return AUDIT_EVENT_DEFAULTS.get(action, (AuditLog.SEVERITY_LOW, False))


def security_ticket_severity(
    matched_keywords: str,
    security_confidence: float | None,
) -> str:
    keywords = {
        keyword.strip().casefold()
        for keyword in matched_keywords.split(",")
        if keyword.strip()
    }
    if keywords & CRITICAL_KEYWORDS:
        return AuditLog.SEVERITY_CRITICAL
    if keywords & HIGH_KEYWORDS:
        return AuditLog.SEVERITY_HIGH
    if security_confidence is not None and security_confidence >= 0.85:
        return AuditLog.SEVERITY_HIGH
    return AuditLog.SEVERITY_MEDIUM
