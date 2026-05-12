from pathlib import Path

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Ticket, TicketAttachment, TicketComment


# Forms for creating and updating tickets, comments, and attachments
class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "ticket_priority",
            "ticket_system",
            "ticket_type",
        ]


class TicketCommentForm(ModelForm):
    class Meta:
        model = TicketComment
        fields = ["body"]


class TicketAttachmentForm(ModelForm):
    max_file_size = 5 * 1024 * 1024
    allowed_extensions = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".txt",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
    }

    class Meta:
        model = TicketAttachment
        fields = ["file"]

    def clean_file(self):
        file = self.cleaned_data.get("file")
        extension = Path(file.name).suffix.lower()

        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"File type not allowed. Only {', '.join(self.allowed_extensions)} files are supported."
            )

        if file.size > self.max_file_size:
            raise ValidationError(
                f"File size must be less than {self.max_file_size} MB"
            )

        return file
