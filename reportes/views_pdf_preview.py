from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from clinica.models import CitaMedica
from clinica.views.citas import SoloMedicoMixin


class ReporteCitaPDFPreviewView(LoginRequiredMixin, SoloMedicoMixin, DetailView):
    model = CitaMedica
    template_name = "reportes/reporte_cita_pdf_preview.html"
    context_object_name = "cita"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return CitaMedica.objects.filter(doctor=self.request.user).select_related("paciente", "doctor")
