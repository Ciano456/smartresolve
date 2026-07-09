# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from accounts.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from admin_portal.models import AuditLog
from tickets.models import (
    Ticket,
    TicketHistory,
    TicketPriority,
    TicketStatus,
    TicketSystem,
    TicketType,
)


class AdminPortalViewTests(TestCase):
    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.email = "testemail@gmail.com"
        self.password = "password123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Test1",
            last_name="User1",
        )
        self.user.groups.add(self.admin_group)

    def _login_admin_user(self):
        self.client.force_login(self.user)

    def _login_non_admin_user(self):
        self.user.groups.clear()
        self.user.groups.add(self.submitter_group)
        self.client.force_login(self.user)

    def _create_managed_user(self):
        managed_user = User.objects.create_user(
            email="managed-user@test.com",
            password="password123",
            first_name="Managed",
            last_name="User",
        )
        managed_user.groups.add(self.submitter_group)
        return managed_user

    def _create_ticket(self, title, submitter=None):
        return Ticket.objects.create(
            title=title,
            description=f"{title} description.",
            submitter=submitter or self.user,
            ticket_type=TicketType.objects.get(code="INCIDENT"),
            ticket_system=TicketSystem.objects.get(code="NETWORK"),
            ticket_priority=TicketPriority.objects.get(code="HIGH"),
            ticket_status=TicketStatus.objects.get(code="OPEN"),
        )

    def test_admin_dashboard_view_requires_login(self):
        response = self.client.get("/admin_portal/")
        self.assertRedirects(response, "/accounts/login/")

    def test_admin_dashboard_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get("/admin_portal/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/admin_dashboard.html")
        self.assertContains(response, "Audit Logs")

    def test_admin_dashboard_uses_live_ticket_counts(self):
        self._login_admin_user()
        ticket_type = TicketType.objects.get(code="INCIDENT")
        ticket_system = TicketSystem.objects.get(code="NETWORK")
        ticket_priority = TicketPriority.objects.get(code="HIGH")
        open_status = TicketStatus.objects.get(code="OPEN")
        closed_status = TicketStatus.objects.get(code="CLOSED")
        Ticket.objects.create(
            title="Open ticket",
            description="Open ticket description",
            submitter=self.user,
            ticket_type=ticket_type,
            ticket_system=ticket_system,
            ticket_priority=ticket_priority,
            ticket_status=open_status,
        )
        Ticket.objects.create(
            title="Closed ticket",
            description="Closed ticket description",
            submitter=self.user,
            ticket_type=ticket_type,
            ticket_system=ticket_system,
            ticket_priority=ticket_priority,
            ticket_status=closed_status,
        )

        response = self.client.get("/admin_portal/")

        self.assertEqual(response.context["ticket_stats"]["total_tickets"], 2)
        self.assertEqual(response.context["ticket_stats"]["open_tickets"], 1)
        self.assertEqual(response.context["ticket_stats"]["closed_tickets"], 1)

    def test_user_list_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get("/admin_portal/users/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_list.html")

    def test_audit_log_list_view_requires_login(self):
        response = self.client.get(reverse("audit_log_list"))

        self.assertRedirects(response, "/accounts/login/")

    def test_audit_log_list_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get(reverse("audit_log_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/audit_log_list.html")
        self.assertContains(response, "Recent Activity")

    def test_audit_log_list_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get(reverse("audit_log_list"))

        self.assertRedirects(response, "/accounts/profile/")

    def test_user_detail_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_detail.html")

    def test_user_detail_sidebar_uses_logged_in_admin_role(self):
        # Viewing a submitter account must not make the admin sidebar show submitter links.
        submitter_user = User.objects.create_user(
            email="managed-submitter@test.com",
            password="password123",
        )
        submitter_user.groups.add(self.submitter_group)

        self._login_admin_user()
        response = self.client.get(reverse("user_detail", args=[submitter_user.id]))

        self.assertContains(response, "All Tickets")
        self.assertContains(response, "User Management")
        self.assertNotContains(response, "My Tickets")
        self.assertNotContains(response, "Create Ticket")

    def test_user_create_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get("/admin_portal/users/create/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_form.html")

    def test_user_edit_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_form.html")

    def test_admin_ticket_list_view_accessible_by_admin(self):
        ticket = self._create_ticket("Admin visible ticket")

        self._login_admin_user()
        response = self.client.get(reverse("admin_ticket_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/ticket_list.html")
        self.assertContains(response, "Admin Tickets")
        self.assertContains(response, ticket.title)
        self.assertContains(response, ticket.ticket_number)

    def test_admin_ticket_list_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get(reverse("admin_ticket_list"))

        self.assertRedirects(response, "/accounts/profile/")

    def test_admin_ticket_list_shows_all_tickets(self):
        managed_user = self._create_managed_user()
        first_ticket = self._create_ticket("First admin list ticket")
        second_ticket = self._create_ticket(
            "Second admin list ticket",
            submitter=managed_user,
        )

        self._login_admin_user()
        response = self.client.get(reverse("admin_ticket_list"))
        content = response.content.decode()

        self.assertContains(response, first_ticket.title)
        self.assertContains(response, second_ticket.title)
        self.assertLess(
            content.index(second_ticket.title),
            content.index(first_ticket.title),
        )

    def test_admin_dashboard_links_to_admin_ticket_list(self):
        self._login_admin_user()
        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, reverse("admin_ticket_list"))
        self.assertContains(response, "View All Tickets")

    def test_lookup_list_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get(reverse("lookup_list", args=["types"]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/lookup_list.html")
        self.assertContains(response, "Ticket Types")
        self.assertContains(response, "Incident")

    def test_lookup_list_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get(reverse("lookup_list", args=["types"]))

        self.assertRedirects(response, "/accounts/profile/")

    def test_lookup_create_view_creates_lookup_value(self):
        self._login_admin_user()
        response = self.client.post(
            reverse("lookup_create", args=["types"]),
            {
                "name": "Change Request",
                "code": "CHANGE",
                "description": "Request to change a system or service.",
                "is_active": True,
                "sort_order": 10,
            },
        )

        self.assertRedirects(response, reverse("lookup_list", args=["types"]))
        self.assertTrue(TicketType.objects.filter(code="CHANGE").exists())

    def test_lookup_create_rejects_duplicate_code(self):
        self._login_admin_user()
        response = self.client.post(
            reverse("lookup_create", args=["types"]),
            {
                "name": "Duplicate Incident",
                "code": "INCIDENT",
                "description": "Duplicate lookup code.",
                "is_active": True,
                "sort_order": 10,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/lookup_form.html")
        self.assertContains(response, "Ticket type with this Code already exists.")

    def test_lookup_edit_view_updates_lookup_value(self):
        ticket_type = TicketType.objects.get(code="INCIDENT")

        self._login_admin_user()
        response = self.client.post(
            reverse("lookup_edit", args=["types", ticket_type.id]),
            {
                "name": "Incident Updated",
                "code": ticket_type.code,
                "description": ticket_type.description,
                "is_active": True,
                "sort_order": ticket_type.sort_order,
            },
        )

        self.assertRedirects(response, reverse("lookup_list", args=["types"]))
        ticket_type.refresh_from_db()
        self.assertEqual(ticket_type.name, "Incident Updated")

    def test_lookup_toggle_active_updates_lookup_value(self):
        ticket_type = TicketType.objects.get(code="INCIDENT")
        self.assertTrue(ticket_type.is_active)

        self._login_admin_user()
        response = self.client.post(
            reverse("lookup_toggle_active", args=["types", ticket_type.id])
        )

        self.assertRedirects(response, reverse("lookup_list", args=["types"]))
        ticket_type.refresh_from_db()
        self.assertFalse(ticket_type.is_active)

    def test_lookup_toggle_active_requires_post(self):
        ticket_type = TicketType.objects.get(code="INCIDENT")

        self._login_admin_user()
        response = self.client.get(
            reverse("lookup_toggle_active", args=["types", ticket_type.id])
        )

        self.assertEqual(response.status_code, 405)

    def test_invalid_lookup_slug_returns_404(self):
        self._login_admin_user()
        response = self.client.get(reverse("lookup_list", args=["unknown"]))

        self.assertEqual(response.status_code, 404)

    def test_user_deactivate_view_accessible_by_admin(self):
        managed_user = self._create_managed_user()
        self._login_admin_user()
        response = self.client.post(
            reverse("user_deactivate", args=[managed_user.id]),
        )

        self.assertEqual(response.status_code, 302)
        managed_user.refresh_from_db()
        self.assertFalse(managed_user.is_active)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.ACTION_USER_DEACTIVATED,
                target_id=managed_user.id,
            ).exists()
        )

    def test_admin_cannot_deactivate_own_account(self):
        self._login_admin_user()
        response = self.client.post(
            reverse("user_deactivate", args=[self.user.id]),
        )

        self.assertRedirects(response, reverse("user_detail", args=[self.user.id]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.ACTION_USER_DEACTIVATED,
                target_id=self.user.id,
            ).exists()
        )

    def test_user_reactivate_view_accessible_by_admin(self):
        managed_user = self._create_managed_user()
        self._login_admin_user()
        response = self.client.post(
            reverse("user_deactivate", args=[managed_user.id]),
        )
        self.assertEqual(response.status_code, 302)
        managed_user.refresh_from_db()
        self.assertFalse(managed_user.is_active)

        response = self.client.post(
            reverse("user_reactivate", args=[managed_user.id]),
        )
        managed_user.refresh_from_db()

        self.assertTrue(managed_user.is_active)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.ACTION_USER_REACTIVATED,
                target_id=managed_user.id,
            ).exists()
        )

    def test_user_create_view_creates_user(self):
        self._login_admin_user()
        response = self.client.post(
            reverse("user_create"),
            {
                "email": "newuser@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "Submitter",
                "is_active": True,
            },
        )
        self.assertRedirects(response, reverse("user_list"))
        created_user = User.objects.get(email="newuser@test.com")
        self.assertTrue(created_user.groups.filter(name="Submitter").exists())
        self.assertTrue(created_user.is_active)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.ACTION_USER_CREATED,
                target_id=created_user.id,
            ).exists()
        )

    def test_user_edit_view_updates_user(self):
        managed_user = self._create_managed_user()
        self._login_admin_user()
        response = self.client.post(
            reverse("user_edit", args=[managed_user.id]),
            {
                "email": managed_user.email,
                "first_name": "Updated",
                "last_name": "Name",
                "role": "Submitter",
                "is_active": False,
            },
        )
        self.assertRedirects(response, reverse("user_detail", args=[managed_user.id]))
        managed_user.refresh_from_db()
        self.assertEqual(managed_user.first_name, "Updated")
        self.assertEqual(managed_user.last_name, "Name")
        self.assertFalse(managed_user.is_active)
        self.assertTrue(managed_user.groups.filter(name="Submitter").exists())
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.ACTION_USER_UPDATED,
                target_id=managed_user.id,
            ).exists()
        )

    def test_audit_log_list_shows_admin_logs_and_ticket_history(self):
        self._login_admin_user()
        managed_user = self._create_managed_user()
        ticket_type = TicketType.objects.get(code="INCIDENT")
        ticket_system = TicketSystem.objects.get(code="NETWORK")
        ticket_priority = TicketPriority.objects.get(code="HIGH")
        open_status = TicketStatus.objects.get(code="OPEN")
        ticket = Ticket.objects.create(
            title="Audit ticket",
            description="Ticket history should appear in audit logs.",
            submitter=managed_user,
            ticket_type=ticket_type,
            ticket_system=ticket_system,
            ticket_priority=ticket_priority,
            ticket_status=open_status,
        )
        AuditLog.objects.create(
            actor=self.user,
            action=AuditLog.ACTION_USER_CREATED,
            target_type="User",
            target_id=managed_user.id,
            target_repr=managed_user.email,
            message=f"Created user {managed_user.email}.",
        )
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=self.user,
            change_type="STATUS_CHANGED",
            field_name="ticket_status",
            old_value="Open",
            new_value="In Progress",
        )

        response = self.client.get(reverse("audit_log_list"))

        self.assertContains(response, "User created")
        self.assertContains(response, managed_user.email)
        self.assertContains(response, "Status Changed")
        self.assertContains(response, ticket.ticket_number)

    def test_user_deactivate_rejects_get_request(self):
        self._login_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/deactivate/")
        self.assertEqual(response.status_code, 405)

    def test_user_reactivate_rejects_get_request(self):
        self._login_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/reactivate/")
        self.assertEqual(response.status_code, 405)

    def test_admin_dashboard_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get("/admin_portal/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_list_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get("/admin_portal/users/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_detail_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_create_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get("/admin_portal/users/create/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_edit_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/edit/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_deactivate_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.post(f"/admin_portal/users/{self.user.id}/deactivate/")
        self.assertRedirects(response, "/accounts/profile/")

    def test_user_reactivate_view_inaccessible_by_non_admin(self):
        self._login_non_admin_user()
        response = self.client.post(f"/admin_portal/users/{self.user.id}/reactivate/")
        self.assertRedirects(response, "/accounts/profile/")
