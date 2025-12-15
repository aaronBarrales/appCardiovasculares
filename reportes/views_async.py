# reportes/views_async.py
import os
import numpy as np

from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from clinica.models import CitaMedica
from clinica.views.citas import SoloMedicoMixin

from reportes.services.features import features_desde_cita
from reportes.services import modelo as modelo_service
from reportes.services.plots import plot_shap_waterfall


def _semaforo_riesgo(p: float):
    if p >= 0.66:
        return ("ALTO", "#dc3545")
    elif p >= 0.33:
        return ("MODERADO", "#ffc107")
    return ("BAJO", "#28a745")


def _json_safe(obj):
    """
    Convierte recursivamente tipos numpy/pandas a tipos nativos JSON-serializables.
    """
    # None, bool, str
    if obj is None or isinstance(obj, (bool, str)):
        return obj

    # numpy scalars
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)

    # números python
    if isinstance(obj, (int, float)):
        return obj

    # dict
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}

    # list/tuple
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]

    # fallback (por si llega algo raro)
    return str(obj)


class ReporteCitaDataAjaxView(LoginRequiredMixin, SoloMedicoMixin, View):
    """
    Devuelve JSON async con:
      - proba_riesgo
      - nivel_riesgo, color_riesgo
      - shap_img_url
      - top_contributions (tabla)
    Genera la imagen SHAP si no existe.
    """

    def get(self, request, pk):
        cita = CitaMedica.objects.select_related("paciente", "doctor").get(pk=pk, doctor=request.user)

        # 1) Features alineadas al background
        X = features_desde_cita(cita)
        _, background, _ = modelo_service.cargar_bundle()
        X = X.reindex(columns=background.columns, fill_value=0)

        # 2) Predicción + explicación
        # OJO: aquí tu servicio debe devolver proba_riesgo y shap_explanation (para la imagen)
        resultado = modelo_service.predecir_y_explicar(X, top_k=8)

        proba = float(resultado["proba_riesgo"])
        nivel, color = _semaforo_riesgo(proba)

        # 3) Generar/reusar PNG SHAP en MEDIA
        out_dir = os.path.join(settings.MEDIA_ROOT, "reportes", f"cita_{cita.pk}")
        os.makedirs(out_dir, exist_ok=True)

        shap_png_path = os.path.join(out_dir, "shap_waterfall.png")
        if not os.path.exists(shap_png_path):
            plot_shap_waterfall(resultado["shap_explanation"], shap_png_path, max_display=8)

        shap_img_url = f"{settings.MEDIA_URL}reportes/cita_{cita.pk}/shap_waterfall.png"

        payload = {
            "ok": True,
            "proba_riesgo": proba,
            "nivel_riesgo": nivel,
            "color_riesgo": color,
            "shap_img_url": shap_img_url,
            "top_contributions": resultado.get("top_contributions", []),
        }

        return JsonResponse(_json_safe(payload))
