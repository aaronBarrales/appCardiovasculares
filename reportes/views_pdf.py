import os
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from xhtml2pdf import pisa

from clinica.models import CitaMedica
from clinica.views.citas import SoloMedicoMixin

from reportes.services.features import features_desde_cita
from reportes.services import modelo as modelo_service
from reportes.services.plots import plot_shap_waterfall
from reportes.services.cita_context import datos_cita_es


def _link_callback(uri, rel):
    """
    xhtml2pdf necesita resolver src/href a paths físicos.
    Soporta /media/... y /static/... en desarrollo.
    """
    # MEDIA
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, "").lstrip("/\\"))
        return path

    # STATIC
    if uri.startswith(settings.STATIC_URL):
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root:
            path = os.path.join(static_root, uri.replace(settings.STATIC_URL, "").lstrip("/\\"))
            return path

        if getattr(settings, "STATICFILES_DIRS", None):
            path = os.path.join(settings.STATICFILES_DIRS[0], uri.replace(settings.STATIC_URL, "").lstrip("/\\"))
            return path

    return uri


class ReporteCitaPDFView(LoginRequiredMixin, SoloMedicoMixin, View):
    """
    PDF:
      /reportes/cita/<pk>/pdf/              -> inline (previsualizar)
      /reportes/cita/<pk>/pdf/?download=1   -> descarga
    """

    def get(self, request, pk):
        cita = (
            CitaMedica.objects
            .select_related("paciente", "doctor", "rango_colesterol", "rango_glucosa")
            .get(pk=pk, doctor=request.user)
        )

        # Features + predicción
        X = features_desde_cita(cita)
        _, background, _ = modelo_service.cargar_bundle()
        X = X.reindex(columns=background.columns, fill_value=0)
        resultado = modelo_service.predecir_y_explicar(X, top_k=8)

        # Genera imagen waterfall en MEDIA
        out_dir = os.path.join(settings.MEDIA_ROOT, "reportes", f"cita_{cita.pk}")
        os.makedirs(out_dir, exist_ok=True)
        shap_png_path = os.path.join(out_dir, "shap_waterfall.png")
        plot_shap_waterfall(resultado["shap_explanation"], shap_png_path, max_display=8)

        # URL para incrustar en PDF (xhtml2pdf la resolverá con link_callback)
        shap_png_url = f"{settings.MEDIA_URL}reportes/cita_{cita.pk}/shap_waterfall.png"

        # Semáforo de riesgo
        p = float(resultado["proba_riesgo"])
        if p >= 0.66:
            nivel = "ALTO"
            color = "#dc3545"  # rojo
        elif p >= 0.33:
            nivel = "MODERADO"
            color = "#ffc107"  # amarillo
        else:
            nivel = "BAJO"
            color = "#28a745"  # verde

        ctx = {
            "cita": cita,
            "resultado": resultado,
            "nivel_riesgo": nivel,
            "color_riesgo": color,
            "shap_img_url": shap_png_url,
            "datos_cita": datos_cita_es(cita),  # <-- secciones
            "is_pdf": True,
        }

        # ✅ OJO: ahora renderiza el template correcto para PDF
        template = get_template("reportes/reporte_cita_pdf.html")

        html = template.render(ctx)

        pdf_io = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html,
            dest=pdf_io,
            link_callback=_link_callback,
            encoding="utf-8",
        )

        if pisa_status.err:
            return HttpResponse(
                "Error generando PDF. Revisa el HTML/CSS del template.",
                status=500
            )

        filename = f"reporte_cita_{cita.pk}.pdf"
        download = request.GET.get("download") == "1"

        resp = HttpResponse(pdf_io.getvalue(), content_type="application/pdf")
        resp["Content-Disposition"] = f'{"attachment" if download else "inline"}; filename="{filename}"'
        return resp
