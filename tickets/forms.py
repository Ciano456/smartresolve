# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from pathlib import Path

from django.contrib.auth import get_user_model
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


class StaffTicketCommentForm(ModelForm):
    class Meta:
        model = TicketComment
        fields = ["body", "is_internal"]


class StaffTicketAssignmentForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields["assigned_to"].queryset = (
            User.objects.filter(groups__name="Support Staff")
            .distinct()
            .order_by("email")
        )
        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = "Unassigned"
        self.fields["assigned_to"].widget.attrs.update(
            {
                "class": (
                    "mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 "
                    "py-3 text-base font-semibold text-slate-800 shadow-sm "
                    "focus:border-[#0756f8] focus:outline-none "
                    "focus:ring-2 focus:ring-[#0756f8]/20"
                )
            }
        )


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
