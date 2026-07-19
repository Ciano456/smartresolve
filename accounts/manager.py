# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    # Django expects a user manager whenever the username field is
    # changed away from the default, so this is what lets User.objects.create_user()
    # and createsuperuser work with an email address instead of a username.
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # set_password hashes the password before it gets anywhere near
        # the database. The plain text version never gets saved.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # A superuser should always keep the built-in Django admin flags.
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
