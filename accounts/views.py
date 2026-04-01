# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == "POST":
        # Email is the username field for this project, so it is passed into authenticate().
        user = authenticate(request, username=request.POST["email"], password=request.POST["password"])
        if user: 
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("profile")  
        else:
                messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")

def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect("login")
    return redirect("profile")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")
