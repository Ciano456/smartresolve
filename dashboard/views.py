# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from accounts.decorators import admin_or_support_staff_required

from dashboard.services import build_dashboard_context, build_dashboard_export_response


# Both views are kept deliberately thin. All the real work of pulling
# stats and building chart data lives in dashboard/services.py, these
# just wire that up to a template or an HTTP response and enforce that
# only admins and support staff can see it.
@method_decorator(admin_or_support_staff_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard_context())
        return context


@method_decorator(admin_or_support_staff_required, name="dispatch")
class DashboardExportView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return build_dashboard_export_response()


dashboard_view = DashboardView.as_view()
dashboard_export_view = DashboardExportView.as_view()
