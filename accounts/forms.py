from django import forms
from .models import User

class UserCreationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    first_name = forms.CharField(label="First Name", max_length=30, required=False)
    last_name = forms.CharField(label="Last Name", max_length=30, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
    def save(self, commit=True):
        cleaned = self.cleaned_data
        return User.objects.create_user(
            email=cleaned["email"],
            password=cleaned["password1"],
            first_name=cleaned.get("first_name", ""),
            last_name=cleaned.get("last_name", "")
        )
        
    
class UserChangeForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    first_name = forms.CharField(label="First Name", max_length=30, required=False)
    last_name = forms.CharField(label="Last Name", max_length=30, required=False)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    
class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
