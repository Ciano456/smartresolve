# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django import forms
from django.contrib.auth.models import Group

class AdminPortalUserCreateForm(UserCreationForm):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Support Staff", "Support Staff"),
        ("Submitter", "Submitter"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta: 
        model = User 
        fields = [
            "email", 
            "first_name", 
            "last_name", 
            "is_active",
            ]
    
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

    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Support Staff", "Support Staff"),
        ("Submitter", "Submitter"),
    ]

    role = forms.ChoiceField(choices=AdminPortalUserCreateForm.ROLE_CHOICES, label="Role")

    class Meta: 
        model = User 
        fields = [
            "email", 
            "first_name", 
            "last_name", 
            "is_active",
            ]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        role_name = self.cleaned_data["role"]
        group = Group.objects.get(name=role_name)
        if commit:
            user.save()
            # Editing follows the same single-role rule as user creation.
            user.groups.set([group])
        return user
    
