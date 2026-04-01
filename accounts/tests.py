# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.test import TestCase
from accounts.models import User
from django.contrib.auth.models import Group

class AuthViewTests(TestCase):
    def setUp(self):
        self.email = "testemail@gmail.com"
        self.password = "password123"
        self.wrong_password = "wrongpassword"
        self.user = User.objects.create_user(
            email=self.email, 
            password=self.password,
            first_name="Test1",
            last_name="User1"
        )
        

    def test_login_page_loads_correctly(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_with_invalid_credentials_stays_on_login(self):
        response = self.client.post("/accounts/login/", {"email": self.email, "password": self.wrong_password})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_with_valid_credentials(self):
        response = self.client.post("/accounts/login/", {"email": self.email, "password": self.password})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/profile/")

    def test_logout_view(self):
        # Log in first so this test follows the real logout flow.
        response = self.client.post("/accounts/login/", {"email": self.email, "password": self.password})
        response = self.client.post("/accounts/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/")

    def test_profile_view_requires_login(self):
        response = self.client.get("/accounts/profile/")
        self.assertRedirects(response, "/accounts/login/?next=/accounts/profile/")

class UserRolePropertyTests(TestCase): 
    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.submitter_group = Group.objects.create(name="Submitter")
        self.support_staff_group = Group.objects.create(name="Support Staff")

        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password123",
        )
        self.submitter_user = User.objects.create_user(
            email="submitter@test.com",
            password="password123",
        )
        self.support_user = User.objects.create_user(
            email="support@test.com",
            password="password123",
        )
        self.no_role_user = User.objects.create_user(
            email="norole@test.com",
            password="password123",
        )
        self.admin_user.groups.add(self.admin_group)
        self.submitter_user.groups.add(self.submitter_group)
        self.support_user.groups.add(self.support_staff_group)


    def test_admin_role_property(self): 
        self.assertTrue(self.admin_user.is_admin_role)

    def test_submitter_role_property(self):
        self.assertTrue(self.submitter_user.is_submitter_role)

    def test_support_staff_role_property(self):
        self.assertTrue(self.support_user.is_support_staff_role)

    def test_display_role_returns_admin(self):
        self.assertEqual(self.admin_user.display_role, "Admin")

    def test_display_role_returns_submitter(self):
        self.assertEqual(self.submitter_user.display_role, "Submitter")

    def test_display_role_returns_support_staff(self):
        self.assertEqual(self.support_user.display_role, "Support Staff")

    def test_display_role_returns_no_role(self):
        self.assertEqual(self.no_role_user.display_role, "No Role Assigned")
