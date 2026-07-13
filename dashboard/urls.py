# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.urls import path

from dashboard.views import dashboard_export_view, dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("export/", dashboard_export_view, name="dashboard_export"),
]
