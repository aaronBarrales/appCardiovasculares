from django.shortcuts import render
from django.views.generic import TemplateView
from usuarios.views.base import AuthenticatedView  # tu mixin AuthenticatedView

class DoctorDashboardView(AuthenticatedView, TemplateView):
    template_name = "doctor/dashboard.html"


class PacienteDashboardView(AuthenticatedView, TemplateView):
    template_name = "paciente/dashboard.html"


class AdminDashboardView(AuthenticatedView, TemplateView):
    template_name = "admin/dashboard.html"


class DashboardGenericoView(AuthenticatedView, TemplateView):
    template_name = "dashboard_generico.html"

