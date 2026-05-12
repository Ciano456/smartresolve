# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.urls import path
from . import views 

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('ticket/<int:id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/create/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:ticket_id>/comments/', views.comment_list, name='comment_list'),
    path('ticket/<int:ticket_id>/attachments/', views.attachment_list, name='attachment_list'),
    path('mine/<int:ticket_id>/comments/create/', views.comment_create, name='comment_create'),
    path('mine/<int:ticket_id>/attachments/create/', views.attachment_create, name='attachment_create'),
    path('mine/', views.my_tickets, name='my_tickets'),
    path('mine/<int:id>/', views.my_ticket_detail, name='my_ticket_detail'),
]
