import joblib
import pandas as pd
import shap
import numpy as np
from django.conf import settings

# Ruta al pkl (guárdalo en /modelo/ o similar)
BUNDLE_PATH = getattr(settings, "MODELO_PKL_PATH", None)
from reportes.services.labels import FEATURE_LABELS_ES, BOOL_TEXT_ES, GENDER_TEXT_ES

_bundle = None
_modelo = None
_background = None
_explainer_shap = None
def cargar_bundle():
    global _bundle, _modelo, _background, _explainer_shap

    if _bundle is None:
        bundle_path = getattr(settings, "MODELO_PKL_PATH", None)
        if not bundle_path:
            raise RuntimeError("MODELO_PKL_PATH no está configurado en settings.py")

        _bundle = joblib.load(bundle_path)
        _modelo = _bundle["pipeline"]
        _background = _bundle["background"]

        def predict_proba_clase1(X):
            X_df = to_df_alineado(X)
            return _modelo.predict_proba(X_df)[:, 1]

        masker = shap.maskers.Independent(_background)
        _explainer_shap = shap.Explainer(predict_proba_clase1, masker)

    return _modelo, _background, _explainer_shap

def to_df_alineado(X):
    _, background, _ = cargar_bundle()
    if isinstance(X, pd.DataFrame):
        X_df = X.copy()
    else:
        X_df = pd.DataFrame(X, columns=background.columns)
    return X_df[background.columns]

def _human_value(feature: str, value):
    """Convierte valores crudos a texto clínico cuando aplica."""
    try:
        if feature in BOOL_TEXT_ES:
            v = int(round(float(value)))
            return BOOL_TEXT_ES[feature].get(v, str(value))
        if feature == "gender":
            v = int(round(float(value)))
            return GENDER_TEXT_ES.get(v, str(value))
    except Exception:
        pass
    return value

def predecir_y_explicar(X_df: pd.DataFrame, top_k=10):
    modelo, background, explainer = cargar_bundle()
    X_df = X_df[background.columns]

    proba = float(modelo.predict_proba(X_df)[0, 1])

    sv = explainer(X_df)  # shap.Explanation
    contrib = sv.values[0]
    base_value = float(sv.base_values[0] if np.ndim(sv.base_values) else sv.base_values)

    # Top contribuciones
    idx = np.argsort(np.abs(contrib))[::-1][:top_k]
    top = []
    for i in idx:
        feat = background.columns[i]
        raw_val = X_df.iloc[0, i]
        top.append({
            "feature": feat,
            "feature_es": FEATURE_LABELS_ES.get(feat, feat),
            "value": float(raw_val) if isinstance(raw_val, (int, float, np.number)) else raw_val,
            "value_human": _human_value(feat, raw_val),
            "shap": float(contrib[i]),
        })

    # Traducción de nombres también para el gráfico waterfall (SHAP)
    # (esto hace que el waterfall salga con etiquetas en español)
    sv.feature_names = [FEATURE_LABELS_ES.get(f, f) for f in sv.feature_names]

    return {
        "proba_riesgo": proba,
        "base_value": base_value,
        "top_contributions": top,
        "shap_explanation": sv,  # para generar waterfall en servidor
    }