# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    # Custom user model so people log in with their email instead of a
    # separate username. Roles (Admin, Submitter, Support Staff) are just
    # Django groups rather than extra boolean fields on this model, so
    # the group system that already ships with Django can be reused for
    # permissions instead of building something new.
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_admin_role(self):
        return self.groups.filter(name="Admin").exists()

    @property
    def is_submitter_role(self):
        return self.groups.filter(name="Submitter").exists()

    @property
    def is_support_staff_role(self):
        return self.groups.filter(name="Support Staff").exists()
    
    @property
    def display_role(self):
        # Show the highest-priority app role when a user has more than one group.
        if self.is_admin_role:
            return "Admin"
        elif self.is_support_staff_role:
            return "Support Staff"
        elif self.is_submitter_role:
            return "Submitter"
        else:
            return "No Role Assigned"

    def __str__(self):
        return self.email
