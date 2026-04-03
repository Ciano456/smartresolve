# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from admin_portal.views import (
    admin_dashboard,
    user_list,
    user_detail,
    user_create,
    user_edit,
    user_deactivate,
    user_reactivate,
)
from django.urls import path

urlpatterns = [
    path("", admin_dashboard, name="admin_dashboard"),
    path("users/", user_list, name="user_list"),
    path("users/<int:user_id>/", user_detail, name="user_detail"),
    path("users/create/", user_create, name="user_create"),
    path("users/<int:user_id>/edit/", user_edit, name="user_edit"),
    path("users/<int:user_id>/deactivate/", user_deactivate, name="user_deactivate"),
    path("users/<int:user_id>/reactivate/", user_reactivate, name="user_reactivate"),
]
