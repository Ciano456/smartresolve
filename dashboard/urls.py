# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.urls import path

from dashboard.views import dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
]
