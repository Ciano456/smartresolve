# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from accounts.models import User
from django.contrib.auth.models import Group
from admin_portal.forms import (
    AdminPortalUserCreateForm,
    AdminPortalUserEditForm,
    TicketPriorityLookupForm,
    TicketStatusLookupForm,
    TicketTypeLookupForm,
)
from tickets.models import TicketType


class AdminPortalFormTests(TestCase):

    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")
        self.email = "admin@test.com"
        self.first_name = "Admin"
        self.last_name = "User"
        self.password1 = "StrongPass123!"
        self.password2 = "StrongPass123!"

    def test_user_form_valid_data(self):
        self.assertTrue(
            AdminPortalUserCreateForm(
                data={
                    "email": self.email,
                    "first_name": self.first_name,
                    "last_name": self.last_name,
                    "password1": self.password1,
                    "password2": self.password2,
                    "role": "Admin",
                    "is_active": True,
                }
            ).is_valid()
        )

    def test_create_form_saves_user_with_selected_role(self):
        form = AdminPortalUserCreateForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "password1": self.password1,
                "password2": self.password2,
                "role": "Admin",
                "is_active": True,
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.groups.filter(name="Admin").exists())
        self.assertTrue(user.is_active)

    def test_create_form_rejects_duplicate_email(self):
        User.objects.create_user(
            email=self.email,
            password=self.password1,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        form = AdminPortalUserCreateForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "password1": self.password1,
                "password2": self.password2,
                "role": "Admin",
                "is_active": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_create_form_rejects_password_mismatch(self):
        form = AdminPortalUserCreateForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "password1": self.password1,
                "password2": "differentpassword",
                "role": "Admin",
                "is_active": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_create_form_rejects_missing_role_group(self):
        self.admin_group.delete()
        form = AdminPortalUserCreateForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "password1": self.password1,
                "password2": self.password2,
                "role": "Admin",
                "is_active": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_edit_form_sets_intial_role_for_admin(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password1,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        user.groups.add(self.admin_group)
        form = AdminPortalUserEditForm(instance=user)
        self.assertEqual(form.fields["role"].initial, "Admin")

    def test_edit_form_updates_user_role(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password1,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        user.groups.add(self.admin_group)
        form = AdminPortalUserEditForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "role": "Submitter",
                "is_active": True,
            },
            instance=user,
        )
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertTrue(updated_user.groups.filter(name="Submitter").exists())
        self.assertFalse(updated_user.groups.filter(name="Admin").exists())

    def test_edit_form_can_deactivate_user(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password1,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        user.groups.add(self.admin_group)
        form = AdminPortalUserEditForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "role": "Admin",
                "is_active": False,
            },
            instance=user,
        )
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertFalse(updated_user.is_active)

    def test_edit_form_rejects_missing_role_group(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password1,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        user.groups.add(self.admin_group)
        self.admin_group.delete()
        form = AdminPortalUserEditForm(
            data={
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "role": "Admin",
                "is_active": True,
            },
            instance=user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_edit_form_sets_initial_role_for_support_staff(self):
        user = User.objects.create_user(
            email="support@test.com",
            password=self.password1,
            first_name="Support",
            last_name="User",
        )
        user.groups.add(self.support_staff_group)
        form = AdminPortalUserEditForm(instance=user)
        self.assertEqual(form.fields["role"].initial, "Support Staff")

    def test_ticket_type_lookup_form_valid_data(self):
        form = TicketTypeLookupForm(
            data={
                "name": "Change Request",
                "code": "CHANGE",
                "description": "Request to change a system or service.",
                "is_active": True,
                "sort_order": 10,
            }
        )

        self.assertTrue(form.is_valid())

    def test_ticket_type_lookup_form_rejects_duplicate_code(self):
        existing_type = TicketType.objects.get(code="INCIDENT")
        form = TicketTypeLookupForm(
            data={
                "name": "Duplicate Incident",
                "code": existing_type.code,
                "description": "Duplicate lookup code.",
                "is_active": True,
                "sort_order": 10,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_ticket_status_lookup_form_includes_closed_flag(self):
        form = TicketStatusLookupForm(
            data={
                "name": "Resolved",
                "code": "RESOLVED",
                "description": "Ticket work is resolved.",
                "is_active": True,
                "sort_order": 4,
                "is_closed": True,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertIn("is_closed", form.fields)

    def test_ticket_priority_lookup_form_can_save_inactive_value(self):
        form = TicketPriorityLookupForm(
            data={
                "name": "Emergency",
                "code": "EMERGENCY",
                "description": "Emergency priority.",
                "is_active": False,
                "sort_order": 99,
            }
        )

        self.assertTrue(form.is_valid())
        priority = form.save()
        self.assertFalse(priority.is_active)
