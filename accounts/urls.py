# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from accounts.views import login_view, logout_view, profile_view
from django.urls import path

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
