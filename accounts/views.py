# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from tickets.models import Ticket


def _get_dashboard_tickets(request: HttpRequest) -> QuerySet[Ticket]:
    if request.user.is_admin_role or request.user.is_support_staff_role:
        return Ticket.objects.all()
    return Ticket.objects.filter(submitter=request.user)


def _ticket_percentage(count: int, total: int) -> int:
    if total == 0:
        return 0
    return round((count / total) * 100)


def login_view(request):
    if request.method == "POST":
        # Email is the username field for this project, so it is passed into authenticate().
        user = authenticate(request, username=request.POST["email"], password=request.POST["password"])
        if user: 
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard")
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
def dashboard_view(request: HttpRequest) -> HttpResponse:
    tickets = _get_dashboard_tickets(request)
    dashboard_stats = tickets.aggregate(
        total_tickets=Count("id"),
        current_tickets=Count("id", filter=Q(ticket_status__is_closed=False)),
        closed_tickets=Count("id", filter=Q(ticket_status__is_closed=True)),
    )
    total_tickets = dashboard_stats["total_tickets"]
    dashboard_stats["current_percentage"] = _ticket_percentage(
        dashboard_stats["current_tickets"], total_tickets
    )
    dashboard_stats["closed_percentage"] = _ticket_percentage(
        dashboard_stats["closed_tickets"], total_tickets
    )
    recent_tickets = tickets.select_related(
        "submitter",
        "ticket_priority",
        "ticket_status",
    ).order_by("-updated_at")[:5]

    return render(
        request,
        "accounts/dashboard.html",
        {
            "dashboard_stats": dashboard_stats,
            "recent_tickets": recent_tickets,
        },
    )


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")
