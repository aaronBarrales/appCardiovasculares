import os
from django.views.generic import DetailView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from clinica.views.citas import SoloMedicoMixin  # o duplica el mixin si prefieres
from clinica.models import CitaMedica
from reportes.services.plots import plot_riesgo, plot_shap_waterfall
from reportes.services.features import features_desde_cita
from reportes.services.modelo import predecir_y_explicar, cargar_bundle
from reportes.services.plots import plot_top_contribuciones, plot_riesgo
from django.http import JsonResponse
from reportes.services.features import features_desde_cita
from reportes.services import modelo as modelo_service
from reportes.services.plots import plot_riesgo, plot_shap_waterfall
from django.views import View

# reportes/views.py
import os
from django.conf import settings
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from clinica.views.citas import SoloMedicoMixin
from clinica.models import CitaMedica

from reportes.services.features import features_desde_cita
from reportes.services import modelo as modelo_service
from reportes.services.plots import plot_shap_waterfall
from reportes.services.cita_context import datos_cita_es
import os
from django.conf import settings
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from clinica.views.citas import SoloMedicoMixin
from clinica.models import CitaMedica

from reportes.services.features import features_desde_cita
from reportes.services import modelo as modelo_service
from reportes.services.plots import plot_shap_waterfall
from reportes.services.cita_context import datos_cita_es


class CitaMedicaReporteWebView(LoginRequiredMixin, SoloMedicoMixin, DetailView):
    model = CitaMedica
    template_name = "reportes/reporte_cita_web.html"

    context_object_name = "cita"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return CitaMedica.objects.filter(doctor=self.request.user).select_related("paciente", "doctor")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cita = self.object

        # Features + predicción
        X = features_desde_cita(cita)
        _, background, _ = modelo_service.cargar_bundle()
        X = X.reindex(columns=background.columns, fill_value=0)
        resultado = modelo_service.predecir_y_explicar(X, top_k=8)

        # Waterfall en MEDIA
        out_dir = os.path.join(settings.MEDIA_ROOT, "reportes", f"cita_{cita.pk}")
        os.makedirs(out_dir, exist_ok=True)
        shap_png_path = os.path.join(out_dir, "shap_waterfall.png")
        plot_shap_waterfall(resultado["shap_explanation"], shap_png_path, max_display=8)

        shap_img_url = f"{settings.MEDIA_URL}reportes/cita_{cita.pk}/shap_waterfall.png"

        # Semáforo
        p = float(resultado["proba_riesgo"])
        if p >= 0.66:
            nivel, color = "ALTO", "#dc3545"
        elif p >= 0.33:
            nivel, color = "MODERADO", "#ffc107"
        else:
            nivel, color = "BAJO", "#28a745"

        ctx.update({
            "resultado": resultado,
            "datos_cita": datos_cita_es(cita),
            "nivel_riesgo": nivel,
            "color_riesgo": color,
            "shap_img_url": shap_img_url,
            "is_pdf": False,
        })
        return ctx

class CitaMedicaPlotsView(LoginRequiredMixin, SoloMedicoMixin, View):
    def get(self, request, pk):
        cita = CitaMedica.objects.select_related("paciente", "doctor").get(pk=pk, doctor=request.user)

        X = features_desde_cita(cita)
        _, background, _ = modelo_service.cargar_bundle()
        X = X.reindex(columns=background.columns, fill_value=0)

        resultado = modelo_service.predecir_y_explicar(X, top_k=10)

        out_dir = os.path.join(settings.MEDIA_ROOT, "reportes", f"cita_{cita.pk}")
        os.makedirs(out_dir, exist_ok=True)

        riesgo_png = os.path.join(out_dir, "riesgo.png")
        shap_png = os.path.join(out_dir, "shap_waterfall.png")

        plot_riesgo(resultado["proba_riesgo"], riesgo_png)
        plot_shap_waterfall(resultado["shap_explanation"], shap_png, max_display=10)

        return JsonResponse({
            "riesgo_img": f"{settings.MEDIA_URL}reportes/cita_{cita.pk}/riesgo.png",
            "shap_img":   f"{settings.MEDIA_URL}reportes/cita_{cita.pk}/shap_waterfall.png",
        })
    


class CitaMedicaReportePDFPreviewView(LoginRequiredMixin, SoloMedicoMixin, DetailView):
    model = CitaMedica
    template_name = "reportes/reporte_cita_pdf_preview.html"
    context_object_name = "cita"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return CitaMedica.objects.filter(doctor=self.request.user).select_related("paciente", "doctor")
