# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

import csv
from datetime import date
from datetime import timedelta
from io import StringIO
from typing import Any

from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    QuerySet,
    Q,
)
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone

from tickets.models import Ticket

# Spreadsheet programs like Excel treat a cell starting with one of these
# characters as a formula, not plain text. If a ticket title started with
# "=" for example, opening the exported CSV in Excel could run it as a
# formula. This is the well known CSV injection issue, and
# _sanitize_csv_value below is what actually defends against it.
CSV_DANGEROUS_PREFIXES = ("=", "+", "-", "@")
CSV_EXPORT_FIELDNAMES = [
    "ticket_number",
    "title",
    "type",
    "system",
    "priority",
    "status",
    "submitter",
    "assignee",
    "created",
    "updated",
    "closed",
]
CSV_EXPORT_FILENAME = "dashboard-report.csv"


def _ticket_percentage(count: int, total: int) -> int:
    if total == 0:
        return 0
    return round((count / total) * 100)


def _format_duration(duration: timedelta | None) -> str | None:
    if duration is None:
        return None

    total_seconds = int(duration.total_seconds())
    if total_seconds < 0:
        return None

    days, remainder = divmod(total_seconds, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes = remainder // 60

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if not parts and minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append("0m")
    return " ".join(parts)


def _month_sequence(months: int = 6) -> list[date]:
    # Builds the last six months as a fixed list, including any month
    # with zero closed tickets. Without this, a month with no activity
    # would just be missing from the chart instead of showing as a flat
    # zero, which would be a bit misleading.
    current = timezone.localdate().replace(day=1)
    sequence: list[date] = []

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


def _build_breakdown(
    queryset: QuerySet[Ticket],
    field_name: str,
) -> dict[str, list[Any]]:
    # Shared by the status, priority, type and system charts. field_name
    # is whichever lookup relation is being grouped by, so this one
    # function replaces four almost identical ones.
    rows = (
        queryset.values(
            f"{field_name}__name",
        )
        .annotate(ticket_count=Count("id"))
        .order_by(f"{field_name}__sort_order", f"{field_name}__name")
    )
    return {
        "labels": [row[f"{field_name}__name"] for row in rows],
        "counts": [row["ticket_count"] for row in rows],
    }


def _build_assigned_workload(queryset: QuerySet[Ticket]) -> dict[str, list[Any]]:
    rows = (
        queryset.filter(assigned_to__isnull=False)
        .values(
            "assigned_to__first_name",
            "assigned_to__last_name",
            "assigned_to__email",
        )
        .annotate(ticket_count=Count("id"))
        .order_by("-ticket_count", "assigned_to__first_name", "assigned_to__last_name")
    )

    labels = []
    counts = []
    for row in rows:
        full_name = " ".join(
            part
            for part in [row["assigned_to__first_name"], row["assigned_to__last_name"]]
            if part
        ).strip()
        labels.append(full_name or row["assigned_to__email"])
        counts.append(row["ticket_count"])

    return {"labels": labels, "counts": counts}


def _build_resolution_trend(queryset: QuerySet[Ticket]) -> dict[str, list[Any]]:
    months = _month_sequence()
    rows = (
        queryset.filter(closed_at__isnull=False)
        .annotate(closed_month=TruncMonth("closed_at"))
        .values("closed_month")
        .annotate(ticket_count=Count("id"))
    )
    trend_map = {}
    for row in rows:
        closed_month = row["closed_month"]
        if closed_month is None:
            continue
        trend_map[closed_month.date()] = row["ticket_count"]

    return {
        "labels": [month.strftime("%b %Y") for month in months],
        "counts": [trend_map.get(month, 0) for month in months],
    }


def _sanitize_csv_value(value: str) -> str:
    # Prefixing with a single quote tells spreadsheet software to treat
    # the value as plain text instead of trying to evaluate it as a
    # formula. This runs on every field pulled from user input before it
    # goes into the export.
    stripped_value = value.lstrip()
    if stripped_value and stripped_value[0] in CSV_DANGEROUS_PREFIXES:
        return f"'{value}"
    return value


def _ticket_export_rows(queryset: QuerySet[Ticket]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ticket in queryset.select_related(
        "ticket_type",
        "ticket_system",
        "ticket_priority",
        "ticket_status",
        "submitter",
        "assigned_to",
    ).order_by("-updated_at"):
        rows.append(
            {
                "ticket_number": _sanitize_csv_value(ticket.ticket_number),
                "title": _sanitize_csv_value(ticket.title),
                "type": _sanitize_csv_value(ticket.ticket_type.name),
                "system": _sanitize_csv_value(ticket.ticket_system.name),
                "priority": _sanitize_csv_value(ticket.ticket_priority.name),
                "status": _sanitize_csv_value(ticket.ticket_status.name),
                "submitter": _sanitize_csv_value(ticket.submitter.email),
                "assignee": (
                    _sanitize_csv_value(ticket.assigned_to.email)
                    if ticket.assigned_to
                    else ""
                ),
                "created": ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "closed": (
                    ticket.closed_at.strftime("%Y-%m-%d %H:%M:%S")
                    if ticket.closed_at
                    else ""
                ),
            }
        )
    return rows


def build_dashboard_export_response() -> HttpResponse:
    tickets = Ticket.objects.select_related(
        "ticket_status",
        "ticket_priority",
        "ticket_type",
        "ticket_system",
        "assigned_to",
        "submitter",
    )
    export_rows = _ticket_export_rows(tickets)

    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=CSV_EXPORT_FIELDNAMES,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(export_rows)

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{CSV_EXPORT_FILENAME}"'
    return response


def build_dashboard_context() -> dict[str, Any]:
    # Everything the dashboard template needs in one place: the top line
    # numbers, the five most recently updated tickets, and the data for
    # every chart. Keeping it all in one function means the view stays
    # thin and just renders whatever this returns.
    tickets = Ticket.objects.select_related(
        "ticket_status",
        "ticket_priority",
        "ticket_type",
        "ticket_system",
        "assigned_to",
        "submitter",
    )

    dashboard_stats = tickets.aggregate(
        total_tickets=Count("id"),
        open_tickets=Count("id", filter=Q(ticket_status__is_closed=False)),
        resolved_tickets=Count("id", filter=Q(ticket_status__is_closed=True)),
        average_resolution_time=Avg(
            ExpressionWrapper(
                F("closed_at") - F("created_at"),
                output_field=DurationField(),
            ),
            filter=Q(closed_at__isnull=False),
        ),
    )

    total_tickets = dashboard_stats["total_tickets"]
    dashboard_stats["open_percentage"] = _ticket_percentage(
        dashboard_stats["open_tickets"], total_tickets
    )
    dashboard_stats["resolved_percentage"] = _ticket_percentage(
        dashboard_stats["resolved_tickets"], total_tickets
    )
    dashboard_stats["average_resolution_time_display"] = _format_duration(
        dashboard_stats["average_resolution_time"]
    )

    recent_tickets = tickets.order_by("-updated_at")[:5]

    return {
        "dashboard_stats": dashboard_stats,
        "recent_tickets": recent_tickets,
        "chart_data": {
            "status": _build_breakdown(tickets, "ticket_status"),
            "priority": _build_breakdown(tickets, "ticket_priority"),
            "type": _build_breakdown(tickets, "ticket_type"),
            "system": _build_breakdown(tickets, "ticket_system"),
            "workload": _build_assigned_workload(tickets),
            "trend": _build_resolution_trend(tickets),
        },
    }
