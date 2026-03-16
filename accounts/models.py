from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Import the custom user manager
from .manager import UserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Use the custom user manager
    objects = UserManager()

    def __str__(self):
        return self.email