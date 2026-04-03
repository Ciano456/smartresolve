# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from accounts.models import User
from django.contrib.auth.models import Group
from django.urls import reverse

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
    
    def test_admin_dashboard_view_requires_login(self):
        response = self.client.get("/admin_portal/")
        self.assertRedirects(response, "/accounts/login/")
    
    def test_admin_dashboard_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get("/admin_portal/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/admin_dashboard.html")
    
    def test_user_list_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get("/admin_portal/users/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_list.html")

    def test_user_detail_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.get(f"/admin_portal/users/{self.user.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_portal/user_detail.html")

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
    
    def test_user_deactivate_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.post(f"/admin_portal/users/{self.user.id}/deactivate/")
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_user_reactivate_view_accessible_by_admin(self):
        self._login_admin_user()
        response = self.client.post(f"/admin_portal/users/{self.user.id}/deactivate/")
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        response = self.client.post(f"/admin_portal/users/{self.user.id}/reactivate/")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertEqual(response.status_code, 302)

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

    def test_user_edit_view_updates_user(self):
        self._login_admin_user()
        response = self.client.post(
            reverse("user_edit", args=[self.user.id]),
            {
                "email": self.email,
                "first_name": "Updated",
                "last_name": "Name",
                "role": "Submitter",
                "is_active": False,
            },
        )
        self.assertRedirects(response, reverse("user_detail", args=[self.user.id]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertFalse(self.user.is_active)
        self.assertTrue(self.user.groups.filter(name="Submitter").exists())
    
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
