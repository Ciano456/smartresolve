# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Ticket, TicketAttachment, TicketComment, TicketPriority


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


class StaffTicketResolutionNoteForm(ModelForm):
    class Meta:
        model = TicketComment
        fields = ["body"]


class StaffTicketResolveForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["resolution_summary"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resolution_summary"].required = True
        self.fields["resolution_summary"].widget.attrs.update(
            {
                "class": (
                    "mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 "
                    "py-3 text-base font-semibold text-slate-800 shadow-sm "
                    "focus:border-[#0756f8] focus:outline-none "
                    "focus:ring-2 focus:ring-[#0756f8]/20"
                ),
                "rows": 4,
            }
        )


class StaffTicketCancelForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["cancellation_reason"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cancellation_reason"].required = True
        self.fields["cancellation_reason"].widget.attrs.update(
            {
                "class": (
                    "mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 "
                    "py-3 text-base font-semibold text-slate-800 shadow-sm "
                    "focus:border-[#0756f8] focus:outline-none "
                    "focus:ring-2 focus:ring-[#0756f8]/20"
                ),
                "rows": 4,
            }
        )


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


class StaffTicketPriorityForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["ticket_priority"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ticket_priority"].queryset = TicketPriority.objects.filter(
            is_active=True
        ).order_by("sort_order")
        self.fields["ticket_priority"].widget.attrs.update(
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
    binary_signatures = {
        ".pdf": (b"%PDF-",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".docx": (b"PK\x03\x04",),
        ".xlsx": (b"PK\x03\x04",),
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
            max_file_size_mb = self.max_file_size // (1024 * 1024)
            raise ValidationError(
                f"File size must be less than {max_file_size_mb} MB"
            )

        header = file.read(16)
        file.seek(0)
        expected_signatures = self.binary_signatures.get(extension)
        if expected_signatures and not header.startswith(expected_signatures):
            raise ValidationError("File content does not match its extension.")

        if extension in {".txt", ".csv"}:
            sample = file.read(4096)
            file.seek(0)
            try:
                sample.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValidationError("Text files must use UTF-8 encoding.") from exc
            if b"\x00" in sample:
                raise ValidationError("Text files cannot contain binary content.")

        return file
