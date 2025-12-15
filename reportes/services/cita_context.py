# reportes/services/cita_context.py
from datetime import date, datetime
from typing import Optional

from clinica.models import RangoColesterol, RangoGlucosa


def _si_no(value: bool) -> str:
    return "Sí" if bool(value) else "No"


def _fmt_fecha(v):
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    return v if v else "—"


def _fmt_num(v, dec=1):
    if v is None or v == "":
        return "—"
    try:
        return f"{float(v):.{dec}f}".replace(".", ",")
    except Exception:
        return str(v)


def _fmt_rango(rango) -> str:
    if not rango:
        return "—"
    desc = getattr(rango, "descripcion", None) or "Sin descripción"
    rmin = getattr(rango, "min", None)
    rmax = getattr(rango, "max", None)
    if rmin is not None and rmax is not None:
        return f"{desc} ({rmin:g}–{rmax:g})"
    return desc


def calcular_imc(peso: Optional[float], estatura_cm: Optional[float]) -> Optional[float]:
    """
    Calcula IMC = peso (kg) / estatura^2 (m)
    """
    if peso is None or estatura_cm is None:
        return None
    try:
        estatura_cm = float(estatura_cm)
        peso = float(peso)
    except Exception:
        return None

    if estatura_cm <= 0:
        return None

    estatura_m = estatura_cm / 100.0
    imc = peso / (estatura_m ** 2)
    return round(imc, 1)


def calcular_rango_colesterol(valor: Optional[float], version_modelo: str = "v1"):
    if valor is None:
        return None
    try:
        valor = float(valor)
    except Exception:
        return None

    return (
        RangoColesterol.objects
        .filter(min__lte=valor, max__gte=valor, version_modelo=version_modelo)
        .order_by("min")
        .first()
    )


def calcular_rango_glucosa(valor: Optional[float], version_modelo: str = "v1"):
    if valor is None:
        return None
    try:
        valor = float(valor)
    except Exception:
        return None

    return (
        RangoGlucosa.objects
        .filter(min__lte=valor, max__gte=valor, version_modelo=version_modelo)
        .order_by("min")
        .first()
    )


def datos_cita_es(cita, version_modelo: str = "v1"):
    """
    Regresa secciones para render:
    [
      {"titulo":"...", "items":[{"label":"...", "value":"..."}]}
    ]
    """
    # --- Cálculos / rangos dinámicos (si no vienen guardados)
    imc_calc = calcular_imc(getattr(cita, "peso", None), getattr(cita, "estatura", None))

    rango_col = getattr(cita, "rango_colesterol", None)
    if rango_col is None:
        rango_col = calcular_rango_colesterol(getattr(cita, "colesterol_total", None), version_modelo=version_modelo)

    rango_glu = getattr(cita, "rango_glucosa", None)
    if rango_glu is None:
        rango_glu = calcular_rango_glucosa(getattr(cita, "glucosa", None), version_modelo=version_modelo)

    secciones = []

    # --- Identificación
    secciones.append({
        "titulo": "Identificación de la cita",
        "items": [
            {"label": "ID de cita", "value": str(getattr(cita, "id_cita", "—"))},
            {"label": "Fecha de cita", "value": _fmt_fecha(getattr(cita, "fecha_cita", None))},
        ]
    })

    # --- Antropometría
    secciones.append({
        "titulo": "Antropometría",
        "items": [
            {"label": "Peso", "value": f"{_fmt_num(getattr(cita, 'peso', None), 1)} kg"},
            {"label": "Estatura", "value": f"{_fmt_num(getattr(cita, 'estatura', None), 1)} cm"},
            {"label": "IMC", "value": _fmt_num(imc_calc, 1) if imc_calc is not None else "—"},
        ]
    })

    # --- Signos vitales
    secciones.append({
        "titulo": "Signos vitales",
        "items": [
            {"label": "Presión sistólica", "value": f"{_fmt_num(getattr(cita, 'presion_sistolica', None), 0)} mmHg"},
            {"label": "Presión diastólica", "value": f"{_fmt_num(getattr(cita, 'presion_diastolica', None), 0)} mmHg"},
        ]
    })

    # --- Laboratorio / bioquímica
    secciones.append({
        "titulo": "Laboratorio",
        "items": [
            {"label": "Colesterol total", "value": f"{_fmt_num(getattr(cita, 'colesterol_total', None), 1)} mg/dL"},
            {"label": "Glucosa", "value": f"{_fmt_num(getattr(cita, 'glucosa', None), 1)} mg/dL"},
            {"label": "Rango de colesterol", "value": _fmt_rango(rango_col)},
            {"label": "Rango de glucosa", "value": _fmt_rango(rango_glu)},
        ]
    })

    # --- Hábitos
    secciones.append({
        "titulo": "Hábitos",
        "items": [
            {"label": "Tabaquismo", "value": _si_no(getattr(cita, "fumador", False))},
            {"label": "Consumo de alcohol", "value": _si_no(getattr(cita, "alcohol", False))},
            {"label": "Consumo de drogas", "value": _si_no(getattr(cita, "drogas", False))},
            {"label": "Actividad física", "value": _si_no(getattr(cita, "actividad_fisica", False))},
        ]
    })

    # --- Notas clínicas
    notas = getattr(cita, "notas", None)
    secciones.append({
        "titulo": "Notas clínicas",
        "items": [
            {"label": "Observaciones", "value": notas if notas else "(Sin notas)"},
        ]
    })

    return secciones
