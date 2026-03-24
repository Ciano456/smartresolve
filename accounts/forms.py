from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):

    class Meta: 
        model = User 
        fields = [
            "email", 
            "first_name", 
            "last_name", 
            "password1", 
            "password2"
            ]
    
        
    
class CustomUserChangeForm(UserChangeForm):
    
    class Meta: 
        model = User 
        fields = [
            "email", 
            "first_name", 
            "last_name", 
            "password"
            ]
    
class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
