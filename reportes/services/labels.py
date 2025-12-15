# reportes/services/labels.py

FEATURE_LABELS_ES = {
    "age": "Edad (años)",
    "gender": "Sexo",
    "height": "Estatura (cm)",
    "weight": "Peso (kg)",
    "ap_hi": "Presión sistólica (mmHg)",
    "ap_lo": "Presión diastólica (mmHg)",
    "cholesterol": "Colesterol (categoría)",
    "gluc": "Glucosa (categoría)",
    "smoke": "Tabaquismo",
    "alco": "Consumo de alcohol",
    "active": "Actividad física",
}

# Para binarios 0/1 si quieres texto clínico:
BOOL_TEXT_ES = {
    "smoke": {0: "No", 1: "Sí"},
    "alco":  {0: "No", 1: "Sí"},
    "active":{0: "No", 1: "Sí"},
}

# Sexo en tu dataset cardio: normalmente 1=femenino 2=masculino (si aplica)
GENDER_TEXT_ES = {1: "Femenino", 2: "Masculino"}
