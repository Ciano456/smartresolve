# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib import admin
from .models import TicketType, TicketSystem, TicketPriority, TicketStatus, Ticket, TicketComment, TicketAttachment, TicketHistory

# Register Ticket models in the admin site
admin.site.register(TicketType)
admin.site.register(TicketSystem)
admin.site.register(TicketPriority)
admin.site.register(TicketStatus)
admin.site.register(Ticket)
admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
admin.site.register(TicketHistory)
