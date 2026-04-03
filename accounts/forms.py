# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

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
            ]
    
        
    
class CustomUserChangeForm(UserChangeForm):
    
    class Meta: 
        model = User 
        fields = [
            "email", 
            "first_name", 
            "last_name", 
            "password", 
            "is_active",
            "is_staff",
            "groups",
            "user_permissions"
            ]
    
class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
