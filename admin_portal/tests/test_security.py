# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth.models import Group
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from accounts.models import User
from admin_portal.models import AuditLog
from admin_portal.security_dashboard import build_security_dashboard_context
from ml.models import TicketCategoryPrediction
from tickets.models import (
    Ticket,
    TicketPriority,
    TicketStatus,
    TicketSystem,
    TicketType,
)

class SecurityDashboardTests(TestCase):
    # Covers FR10: who can reach the security dashboard, and whether the
    # numbers and records it shows actually match what is in the
    # database.
    def setUp(self) -> None:
        admin_group = Group.objects.create(name="Admin")
        support_group = Group.objects.create(name="Support Staff")
        submitter_group = Group.objects.create(name="Submitter")
        self.admin = User.objects.create_user("security-admin@example.com", "Pass123!")
        self.admin.groups.add(admin_group)
        self.support = User.objects.create_user("security-staff@example.com", "Pass123!")
        self.support.groups.add(support_group)
        self.submitter = User.objects.create_user("security-user@example.com", "Pass123!")
        self.submitter.groups.add(submitter_group)

        self.ticket = Ticket.objects.create(
            title="Suspicious attachment",
            description="A phishing attachment was opened.",
            submitter=self.submitter,
            ticket_type=TicketType.objects.get(code="INCIDENT"),
            ticket_system=TicketSystem.objects.get(code="SOFTWARE"),
            ticket_priority=TicketPriority.objects.get(code="HIGH"),
            ticket_status=TicketStatus.objects.get(code="OPEN"),
        )
        TicketCategoryPrediction.objects.create(
            ticket=self.ticket,
            predicted_category="software",
            confidence=0.8,
            category_model_name="LogisticRegression",
            category_model_version="a" * 64,
            is_security_flagged=True,
            security_confidence=0.9,
            security_threshold=0.55,
            matched_keywords="phishing, malware",
        )
        AuditLog.objects.create(
            action=AuditLog.ACTION_SECURITY_TICKET_FLAGGED,
            target_type="Ticket",
            target_id=self.ticket.id,
            target_repr=self.ticket.ticket_number,
            message="Security review requested.",
            severity=AuditLog.SEVERITY_HIGH,
            flagged=True,
            ip_address="192.0.2.30",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("security_dashboard"))
        self.assertRedirects(response, reverse("login"))

    def test_submitter_receives_forbidden_response(self):
        self.client.force_login(self.submitter)
        response = self.client.get(reverse("security_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_support_staff_receives_forbidden_response(self):
        self.client.force_login(self.support)
        response = self.client.get(reverse("security_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_admin_sees_flagged_metrics_and_records(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("security_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ticket.ticket_number)
        self.assertContains(response, "192.0.2.30")
        self.assertEqual(response.context["security_stats"]["flagged_tickets"], 1)
        self.assertEqual(response.context["security_stats"]["high"], 1)

    def test_keyword_breakdown_counts_each_signal(self):
        context = build_security_dashboard_context()
        self.assertEqual(
            context["keyword_breakdown"],
            [{"label": "phishing", "count": 1}, {"label": "malware", "count": 1}],
        )

    def test_keyword_breakdown_is_limited_to_recent_predictions(self):
        older_ticket = Ticket.objects.create(
            title="Older security signal",
            description="A ransomware alert was reported.",
            submitter=self.submitter,
            ticket_type=TicketType.objects.get(code="INCIDENT"),
            ticket_system=TicketSystem.objects.get(code="SOFTWARE"),
            ticket_priority=TicketPriority.objects.get(code="HIGH"),
            ticket_status=TicketStatus.objects.get(code="OPEN"),
        )
        TicketCategoryPrediction.objects.create(
            ticket=older_ticket,
            predicted_category="software",
            confidence=0.8,
            category_model_name="LogisticRegression",
            category_model_version="b" * 64,
            is_security_flagged=True,
            security_confidence=0.9,
            security_threshold=0.55,
            matched_keywords="ransomware",
        )

        with patch("admin_portal.security_dashboard.KEYWORD_BREAKDOWN_LIMIT", 1):
            context = build_security_dashboard_context()

        self.assertEqual(
            context["keyword_breakdown"],
            [{"label": "ransomware", "count": 1}],
        )

    def test_severity_filter_limits_recent_events(self):
        AuditLog.objects.create(
            action=AuditLog.ACTION_ACCESS_DENIED,
            target_type="Request",
            target_repr="/restricted/",
            message="Access denied.",
            severity=AuditLog.SEVERITY_MEDIUM,
            flagged=True,
        )
        context = build_security_dashboard_context(AuditLog.SEVERITY_HIGH)
        events = list(context["recent_security_events"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].severity, AuditLog.SEVERITY_HIGH)

    def test_dashboard_service_uses_bounded_queries(self):
        with CaptureQueriesContext(connection) as queries:
            context = build_security_dashboard_context()
            list(context["recent_flagged_tickets"])
            list(context["recent_security_events"])
        self.assertLessEqual(len(queries), 7)

    def test_empty_dashboard_renders_zero_values(self):
        TicketCategoryPrediction.objects.all().delete()
        AuditLog.objects.all().delete()
        self.client.force_login(self.admin)
        response = self.client.get(reverse("security_dashboard"))
        self.assertEqual(response.context["security_stats"]["flagged_tickets"], 0)
        self.assertContains(response, "No tickets currently require security review")
