# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.conf import settings
from django.db import models
from django.utils import timezone


# TicketType, TicketSystem, TicketPriority and TicketStatus are lookup
# tables rather than fixed choices on the Ticket model. This means admins
# can add, rename or deactivate values from the admin portal without a
# code change or a migration, which matters for something like ticket
# type where an organisation might want to add a new category later.
class TicketType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class TicketSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class TicketPriority(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class TicketStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    # Left blank here on purpose. The real value gets filled in by
    # generate_ticket_number() below, after the row has a database id to
    # build the number from.
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="submitted_tickets",
        on_delete=models.PROTECT,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, null=False)
    ticket_system = models.ForeignKey(TicketSystem, on_delete=models.PROTECT, null=False)
    ticket_priority = models.ForeignKey(TicketPriority, on_delete=models.PROTECT, null=False)
    ticket_status = models.ForeignKey(TicketStatus, on_delete=models.PROTECT, null=False)
    resolution_summary = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.ticket_number} - {self.title}"

    def save(self, *args, **kwargs) -> None:
        # closed_at gets set or cleared automatically based on whatever
        # status the ticket is on, rather than relying on every view that
        # changes status to remember to set it themselves. If a ticket
        # gets reopened, closed_at is cleared again so it doesn't still
        # look closed.
        if self.ticket_status and self.ticket_status.is_closed and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.ticket_status and not self.ticket_status.is_closed and self.closed_at:
            self.closed_at = None

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # The ticket number needs the database id, which doesn't exist
        # until after the first save, so this is a genuine two step save
        # for brand new tickets: save once to get an id, generate the
        # number, then save again just for that one field.
        if is_new and not self.ticket_number:
            self.generate_ticket_number()
            super().save(update_fields=["ticket_number"])

    def generate_ticket_number(self) -> None:
        if self.id:
            self.ticket_number = f"TICKET-{self.id:06d}"


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ticket_comments",
        null=True,
        blank=True,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Internal comments are only visible to staff and admins, for notes
    # about a ticket that shouldn't go back to the submitter. The
    # submitter facing views filter these out.
    is_internal = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.created_at}"


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ticket_attachments",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="ticket_attachments/")
    # Django renames uploaded files on disk to avoid clashes, so this
    # keeps the name the user actually uploaded, for showing in the UI
    # and for the download filename.
    original_filename = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Attachment for {self.ticket} by {self.uploaded_by}"


# A row per change made to a ticket (status, assignment, priority, and so
# on). This is what powers the ticket detail page's history timeline, and
# also feeds into the combined activity view in admin_portal.
class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ticket_changes",
    )
    change_type = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"History for {self.ticket} - {self.change_type} by {self.changed_by}"
