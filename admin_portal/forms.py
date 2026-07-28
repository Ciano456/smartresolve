# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import Group

from accounts.models import User
from tickets.models import TicketPriority, TicketStatus, TicketSystem, TicketType

# These forms are for admins managing users and the lookup tables
# (ticket types, systems, priorities, statuses) from the admin portal,
# separate from the plain Django admin site.
ROLE_CHOICES = [
    ("Admin", "Admin"),
    ("Support Staff", "Support Staff"),
    ("Submitter", "Submitter"),
]


def validate_role_group(role_name: str) -> str:
    # Groups have to already exist for a role to be assignable, so this
    # gives a clear error instead of letting a typo silently create a
    # user with no role at all.
    if not Group.objects.filter(name=role_name).exists():
        raise forms.ValidationError(
            f"The {role_name} role is not configured. Create the group before assigning it."
        )
    return role_name


class AdminPortalUserCreateForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_active",
        ]

    def clean_role(self):
        return validate_role_group(self.cleaned_data["role"])

    def save(self, commit=True):
        user = super().save(commit=False)
        role_name = self.cleaned_data["role"]
        group = Group.objects.get(name=role_name)
        if commit:
            user.save()
            # The UI allows one business role at a time, so we replace the managed groups.
            user.groups.set([group])
        return user


class AdminPortalUserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Prefill the custom role field from the user's current group assignment.
            current_groups = self.instance.groups.values_list("name", flat=True)
            if "Admin" in current_groups:
                self.fields["role"].initial = "Admin"
            elif "Support Staff" in current_groups:
                self.fields["role"].initial = "Support Staff"
            elif "Submitter" in current_groups:
                self.fields["role"].initial = "Submitter"

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_active",
        ]

    def clean_role(self):
        return validate_role_group(self.cleaned_data["role"])

    def save(self, commit=True):
        user = super().save(commit=False)
        role_name = self.cleaned_data["role"]
        group = Group.objects.get(name=role_name)
        if commit:
            user.save()
            # Editing follows the same single-role rule as user creation.
            user.groups.set([group])
        return user


# The four lookup tables (ticket type, system, priority, status) all get
# managed with near identical forms, so this base class holds the shared
# styling and the rule that a lookup's code can't be changed once it
# exists, since other parts of the app may depend on that code.
class BaseLookupForm(forms.ModelForm):
    text_input_class = (
        "w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-base "
        "font-semibold text-slate-800 shadow-sm focus:border-[#0756f8] "
        "focus:outline-none focus:ring-2 focus:ring-[#0756f8]/20"
    )
    checkbox_class = "h-5 w-5 rounded border-slate-300 text-[#0756f8]"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": self.checkbox_class})
            else:
                field.widget.attrs.update({"class": self.text_input_class})
        if self.instance and self.instance.pk:
            self.fields["code"].disabled = True
            self.fields["code"].help_text = (
                "Codes are locked after creation because workflow logic may depend on them."
            )

    class Meta:
        fields = [
            "name",
            "code",
            "description",
            "is_active",
            "sort_order",
        ]


class TicketTypeLookupForm(BaseLookupForm):
    class Meta(BaseLookupForm.Meta):
        model = TicketType


class TicketSystemLookupForm(BaseLookupForm):
    class Meta(BaseLookupForm.Meta):
        model = TicketSystem


class TicketPriorityLookupForm(BaseLookupForm):
    class Meta(BaseLookupForm.Meta):
        model = TicketPriority


class TicketStatusLookupForm(BaseLookupForm):
    class Meta(BaseLookupForm.Meta):
        model = TicketStatus
        fields = [
            "name",
            "code",
            "description",
            "is_active",
            "sort_order",
            "is_closed",
        ]
