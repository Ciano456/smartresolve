# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.db import models
from django.conf import settings
from django.utils import timezone

# Ticket Type look up model 
class TicketType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# Ticket System look up model
class TicketSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# Ticket Priority look up model   
class TicketPriority(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# Ticket Status look up model
class TicketStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
# Main Ticket model
class Ticket(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_tickets', on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, null=False)
    ticket_system = models.ForeignKey(TicketSystem, on_delete=models.PROTECT, null=False)
    ticket_priority = models.ForeignKey(TicketPriority, on_delete=models.PROTECT, null=False)
    ticket_status = models.ForeignKey(TicketStatus, on_delete=models.PROTECT, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Automatically set closed_at when status is changed to a closed status
        if self.ticket_status and self.ticket_status.is_closed and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.ticket_status and not self.ticket_status.is_closed and self.closed_at:
            self.closed_at = None

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new and not self.ticket_number:
            self.generate_ticket_number()
            super().save(update_fields=['ticket_number'])
        
    
    def generate_ticket_number(self):
        if self.id:  
            self.ticket_number =  f"TICKET-{self.id:06d}"
    
# Child model for comments on tickets
class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE ,related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.SET_NULL, related_name='ticket_comments', null=True, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_internal = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author} on {self.created_at}"

# Child model for attachments on tickets
class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.SET_NULL, related_name='ticket_attachments', null=True, blank=True)
    file = models.FileField(upload_to='ticket_attachments/')
    original_filename = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket} by {self.uploaded_by}"
    
# Model to track history of changes to tickets, including status changes, comments added, etc.
class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.PROTECT, related_name='ticket_changes')
    change_type = models.CharField(max_length=50)  # e.g., "Status Change", "Comment Added"
    field_name = models.CharField(max_length=100, blank=True)  # e.g., "ticket_status"
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.ticket} - {self.change_type} by {self.changed_by}"


