# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
Builds the data shown on the FR10 security metrics dashboard. Kept as one
context builder function rather than putting all this logic straight
into the view, the same pattern dashboard/services.py uses for the main
dashboard, so the view stays thin and this can be tested on its own.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from admin_portal.models import AuditLog
from ml.models import TicketCategoryPrediction

# How many recent flagged predictions get scanned when building the
# keyword breakdown chart. Capped rather than scanning every flagged
# ticket ever, since the dashboard only needs a sense of recent activity,
# not the full history.
KEYWORD_BREAKDOWN_LIMIT = 500


def _month_sequence(months: int = 6) -> list[date]:
    # Builds a list of the first day of each of the last six months,
    # oldest first, so the trend chart always has a full six month axis
    # even for months with zero flagged events, instead of only showing
    # bars for months that happen to have data.
    current = timezone.localdate().replace(day=1)
    sequence = []
    year = current.year
    month = current.month
    for _ in range(months):
        sequence.append(date(year, month, 1))
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    return list(reversed(sequence))


def build_security_dashboard_context(selected_severity: str = "") -> dict[str, Any]:
    # Two separate sources feed the dashboard. flagged_predictions comes
    # from the FR8 AI triage on tickets, and flagged_events comes from
    # the general audit log (failed logins, blocked uploads, access
    # denials, and so on). They cover different kinds of security signal
    # so both get shown rather than picking just one.
    flagged_predictions = TicketCategoryPrediction.objects.filter(
        is_security_flagged=True
    )
    flagged_events = AuditLog.objects.filter(flagged=True)
    # An unexpected value in the severity filter, for example someone
    # editing the URL by hand, is just ignored rather than causing an
    # error, and the dashboard falls back to showing everything.
    valid_severities = {value for value, _label in AuditLog.SEVERITY_CHOICES}
    if selected_severity not in valid_severities:
        selected_severity = ""
    recent_events = flagged_events
    if selected_severity:
        recent_events = recent_events.filter(severity=selected_severity)
    severity_rows = flagged_events.values("severity").annotate(total=Count("id"))
    # Every severity level starts at zero and gets filled in from the
    # query results, so the chart always shows all four levels even if
    # one of them currently has no events at all.
    severity_counts = {
        choice: 0 for choice, _label in AuditLog.SEVERITY_CHOICES
    }
    severity_counts.update({row["severity"]: row["total"] for row in severity_rows})

    # Counts how often each keyword shows up across recent flagged
    # tickets, so the dashboard can show which security concerns are
    # actually coming up most, phishing versus malware versus stolen
    # devices, for example.
    keyword_counts: Counter[str] = Counter()
    recent_keyword_signals = flagged_predictions.exclude(
        matched_keywords=""
    ).order_by("-created_at")[:KEYWORD_BREAKDOWN_LIMIT]
    for matched_keywords in recent_keyword_signals.values_list(
        "matched_keywords",
        flat=True,
    ):
        keyword_counts.update(
            keyword.strip()
            for keyword in matched_keywords.split(",")
            if keyword.strip()
        )

    months = _month_sequence()
    trend_rows = (
        flagged_events.annotate(event_month=TruncMonth("created_at"))
        .values("event_month")
        .annotate(total=Count("id"))
    )
    trend_map = {
        row["event_month"].date(): row["total"]
        for row in trend_rows
        if row["event_month"] is not None
    }

    return {
        "security_stats": {
            "flagged_tickets": flagged_predictions.count(),
            "flagged_events": flagged_events.count(),
            **severity_counts,
        },
        "recent_flagged_tickets": flagged_predictions.select_related(
            "ticket",
            "ticket__submitter",
            "ticket__ticket_status",
            "ticket__ticket_priority",
        ).order_by("-created_at")[:10],
        "recent_security_events": recent_events.select_related("actor").order_by(
            "-created_at"
        )[:20],
        "selected_severity": selected_severity,
        "severity_choices": AuditLog.SEVERITY_CHOICES,
        "keyword_breakdown": [
            {"label": label, "count": count}
            for label, count in keyword_counts.most_common()
        ],
        "security_chart_data": {
            "severity": {
                "labels": [label for _value, label in AuditLog.SEVERITY_CHOICES],
                "counts": [
                    severity_counts[value]
                    for value, _label in AuditLog.SEVERITY_CHOICES
                ],
            },
            "trend": {
                "labels": [month.strftime("%b %Y") for month in months],
                "counts": [trend_map.get(month, 0) for month in months],
            },
        },
    }
