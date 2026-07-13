# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from accounts.decorators import admin_or_support_staff_required

from dashboard.services import build_dashboard_context


@method_decorator(admin_or_support_staff_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard_context())
        return context


dashboard_view = DashboardView.as_view()
