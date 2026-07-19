# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from admin_portal.views import (
    audit_log_list,
    admin_dashboard,
    admin_ticket_list,
    lookup_create,
    lookup_edit,
    lookup_list,
    lookup_toggle_active,
    user_list,
    user_detail,
    user_create,
    user_edit,
    user_deactivate,
    user_reactivate,
)
from django.urls import path

# All admin only routes: dashboard, audit log, ticket overview, lookup
# table management, and user management. The actual role check happens
# in the views themselves through the admin_required decorator, not here.
urlpatterns = [
    path("", admin_dashboard, name="admin_dashboard"),
    path("audit-logs/", audit_log_list, name="audit_log_list"),
    path("tickets/", admin_ticket_list, name="admin_ticket_list"),
    path("lookups/<str:lookup_slug>/", lookup_list, name="lookup_list"),
    path(
        "lookups/<str:lookup_slug>/create/",
        lookup_create,
        name="lookup_create",
    ),
    path(
        "lookups/<str:lookup_slug>/<int:lookup_id>/edit/",
        lookup_edit,
        name="lookup_edit",
    ),
    path(
        "lookups/<str:lookup_slug>/<int:lookup_id>/toggle-active/",
        lookup_toggle_active,
        name="lookup_toggle_active",
    ),
    path("users/", user_list, name="user_list"),
    path("users/<int:user_id>/", user_detail, name="user_detail"),
    path("users/create/", user_create, name="user_create"),
    path("users/<int:user_id>/edit/", user_edit, name="user_edit"),
    path("users/<int:user_id>/deactivate/", user_deactivate, name="user_deactivate"),
    path("users/<int:user_id>/reactivate/", user_reactivate, name="user_reactivate"),
]
