# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.urls import path
from . import views

# "mine/" routes are the submitter facing pages (their own tickets only).
# Everything else here is staff and admin facing, guarded by
# admin_or_support_staff_required in the views themselves.
urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("ticket/<int:id>/", views.ticket_detail, name="ticket_detail"),
    path(
        "ticket/<int:ticket_id>/category-override/",
        views.TicketCategoryOverrideView.as_view(),
        name="ticket_category_override",
    ),
    path("ticket/create/", views.ticket_create, name="ticket_create"),
    path("ticket/<int:ticket_id>/comments/", views.comment_list, name="comment_list"),
    path(
        "ticket/<int:ticket_id>/comments/create/",
        views.staff_comment_create,
        name="staff_comment_create",
    ),
    path(
        "ticket/<int:ticket_id>/assignment/",
        views.ticket_assignment_update,
        name="ticket_assignment_update",
    ),
    path(
        "ticket/<int:ticket_id>/priority/",
        views.ticket_priority_update,
        name="ticket_priority_update",
    ),
    path(
        "ticket/<int:ticket_id>/resolve/",
        views.ticket_resolve,
        name="ticket_resolve",
    ),
    path(
        "ticket/<int:ticket_id>/cancel/",
        views.ticket_cancel,
        name="ticket_cancel",
    ),
    path(
        "ticket/<int:ticket_id>/resolution-notes/create/",
        views.ticket_resolution_note_create,
        name="ticket_resolution_note_create",
    ),
    path(
        "ticket/<int:ticket_id>/attachments/",
        views.attachment_list,
        name="attachment_list",
    ),
    path(
        "attachments/<int:attachment_id>/download/",
        views.attachment_download,
        name="attachment_download",
    ),
    path(
        "mine/<int:ticket_id>/comments/create/",
        views.comment_create,
        name="comment_create",
    ),
    path(
        "mine/<int:ticket_id>/attachments/create/",
        views.attachment_create,
        name="attachment_create",
    ),
    path("mine/", views.my_tickets, name="my_tickets"),
    path("mine/<int:id>/", views.my_ticket_detail, name="my_ticket_detail"),
]
