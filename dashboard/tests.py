# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from datetime import timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from tickets.models import (
    Ticket,
    TicketPriority,
    TicketStatus,
    TicketSystem,
    TicketType,
)


class DashboardViewTests(TestCase):
    def setUp(self) -> None:
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_group = Group.objects.create(name="Support Staff")
        self.admin_group = Group.objects.create(name="Admin")

        self.submitter = User.objects.create_user(
            email="submitter@test.com",
            password="password123",
        )
        self.submitter.groups.add(self.submitter_group)

        self.support_user = User.objects.create_user(
            email="support@test.com",
            password="password123",
        )
        self.support_user.groups.add(self.support_group)

        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password123",
        )
        self.admin_user.groups.add(self.admin_group)

        self.ticket_type_incident = TicketType.objects.get(code="INCIDENT")
        self.ticket_type_request = TicketType.objects.get(code="SERVICE")
        self.ticket_system_network = TicketSystem.objects.get(code="NETWORK")
        self.ticket_system_software = TicketSystem.objects.get(code="SOFTWARE")
        self.ticket_priority_high = TicketPriority.objects.get(code="HIGH")
        self.ticket_priority_low = TicketPriority.objects.get(code="LOW")
        self.status_open = TicketStatus.objects.get(code="OPEN")
        self.status_in_progress = TicketStatus.objects.get(code="IN_PROGRESS")
        self.status_closed = TicketStatus.objects.get(code="CLOSED")

        self.assignee_one = User.objects.create_user(
            email="staff.one@test.com",
            password="password123",
        )
        self.assignee_one.groups.add(self.support_group)

        self.assignee_two = User.objects.create_user(
            email="staff.two@test.com",
            password="password123",
        )
        self.assignee_two.groups.add(self.support_group)

    def _create_ticket(
        self,
        *,
        title: str,
        submitter: User,
        status: TicketStatus,
        priority: TicketPriority,
        ticket_type: TicketType,
        system: TicketSystem,
        assigned_to: User | None = None,
        created_at_offset_days: int = 0,
        closed_at_offset_days: int | None = None,
    ) -> Ticket:
        ticket = Ticket.objects.create(
            title=title,
            description=f"{title} description",
            submitter=submitter,
            assigned_to=assigned_to,
            ticket_type=ticket_type,
            ticket_system=system,
            ticket_priority=priority,
            ticket_status=status,
        )

        created_at = timezone.now() - timedelta(days=created_at_offset_days)
        Ticket.objects.filter(pk=ticket.pk).update(created_at=created_at)

        if closed_at_offset_days is not None:
            Ticket.objects.filter(pk=ticket.pk).update(
                closed_at=timezone.now() - timedelta(days=closed_at_offset_days)
            )

        ticket.refresh_from_db()
        return ticket

    def test_dashboard_requires_login(self) -> None:
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/accounts/login/")

    def test_submitter_is_redirected_to_profile(self) -> None:
        self.client.force_login(self.submitter)
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/accounts/profile/")

    def test_support_staff_can_view_dashboard_metrics(self) -> None:
        open_ticket = self._create_ticket(
            title="Open ticket",
            submitter=self.submitter,
            status=self.status_open,
            priority=self.ticket_priority_high,
            ticket_type=self.ticket_type_incident,
            system=self.ticket_system_network,
            assigned_to=self.assignee_one,
            created_at_offset_days=4,
        )
        in_progress_ticket = self._create_ticket(
            title="In progress ticket",
            submitter=self.submitter,
            status=self.status_in_progress,
            priority=self.ticket_priority_low,
            ticket_type=self.ticket_type_request,
            system=self.ticket_system_software,
            assigned_to=self.assignee_two,
            created_at_offset_days=3,
        )
        closed_ticket = self._create_ticket(
            title="Closed ticket",
            submitter=self.submitter,
            status=self.status_closed,
            priority=self.ticket_priority_high,
            ticket_type=self.ticket_type_incident,
            system=self.ticket_system_network,
            assigned_to=self.assignee_one,
            created_at_offset_days=6,
            closed_at_offset_days=2,
        )

        self.client.force_login(self.support_user)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")
        self.assertEqual(response.context["dashboard_stats"]["total_tickets"], 3)
        self.assertEqual(response.context["dashboard_stats"]["open_tickets"], 2)
        self.assertEqual(response.context["dashboard_stats"]["resolved_tickets"], 1)
        self.assertEqual(response.context["dashboard_stats"]["open_percentage"], 67)
        self.assertEqual(response.context["dashboard_stats"]["resolved_percentage"], 33)
        self.assertIsNotNone(
            response.context["dashboard_stats"]["average_resolution_time_display"]
        )
        self.assertEqual(
            response.context["chart_data"]["status"]["labels"],
            ["Open", "In Progress", "Closed"],
        )
        self.assertEqual(response.context["chart_data"]["status"]["counts"], [1, 1, 1])
        self.assertEqual(response.context["chart_data"]["priority"]["counts"], [1, 2])
        self.assertEqual(response.context["chart_data"]["type"]["counts"], [2, 1])
        self.assertEqual(response.context["chart_data"]["system"]["counts"], [1, 2])
        self.assertEqual(response.context["chart_data"]["workload"]["counts"], [2, 1])
        self.assertEqual(len(response.context["chart_data"]["trend"]["labels"]), 6)
        self.assertContains(response, "Chart")
        self.assertContains(response, open_ticket.ticket_number)
        self.assertContains(response, in_progress_ticket.ticket_number)
        self.assertContains(response, closed_ticket.ticket_number)

    def test_admin_can_view_dashboard(self) -> None:
        self._create_ticket(
            title="Admin ticket",
            submitter=self.submitter,
            status=self.status_open,
            priority=self.ticket_priority_high,
            ticket_type=self.ticket_type_incident,
            system=self.ticket_system_network,
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")
