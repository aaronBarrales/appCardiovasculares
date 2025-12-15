import pandas as pd

def features_desde_cita(cita) -> pd.DataFrame:
    """
    Regresa DataFrame con UNA fila.
    Ajusta los nombres a los que tu modelo espera (los del background.columns).
    """
    # OJO: aquí debes mapear EXACTAMENTE a las columnas del modelo.
    data = {
        # Ejemplo: adapta a tus columnas reales
        "age": calcular_edad(cita.paciente.fecha_nacimiento),
        "gender": map_genero(cita.paciente.genero),  # si tu modelo usa 1/2
        "height": float(cita.estatura) if cita.estatura is not None else 0.0,
        "weight": float(cita.peso) if cita.peso is not None else 0.0,
        "ap_hi": float(cita.presion_sistolica) if cita.presion_sistolica is not None else 0.0,
        "ap_lo": float(cita.presion_diastolica) if cita.presion_diastolica is not None else 0.0,
        "cholesterol": float(cita.colesterol_total) if cita.colesterol_total is not None else 0.0,
        "gluc": float(cita.glucosa) if cita.glucosa is not None else 0.0,
        "smoke": int(bool(cita.fumador)),
        "alco": int(bool(cita.alcohol)),
        "active": int(bool(cita.actividad_fisica)),
    }
    return pd.DataFrame([data])

def calcular_edad(fecha_nacimiento):
    from datetime import date
    if not fecha_nacimiento:
        return 0
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def map_genero(genero_obj):
    """
    Ajusta a tu codificación (ej: Hombre=1, Mujer=2) o lo que use tu modelo.
    """
    if not genero_obj:
        return 0
    g = str(genero_obj).strip().lower()
    if g.startswith("h"):
        return 1
    if g.startswith("m"):
        return 2
    return 0
