import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import os
from django.conf import settings

def plot_top_contribuciones(top_contributions, out_path):
    feats = [d["feature"] for d in top_contributions][::-1]
    vals = [d["shap"] for d in top_contributions][::-1]

    plt.figure(figsize=(8, 4))
    plt.barh(feats, vals)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_riesgo(proba, out_path):
    plt.figure(figsize=(6, 1.6))
    plt.barh(["Riesgo"], [proba])
    plt.xlim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


import shap

def plot_shap_waterfall(shap_explanation, out_path: str, max_display=8):
    plt.close("all")
    plt.figure(figsize=(8, 4))  # Ajusta aquí tamaño
    shap.plots.waterfall(shap_explanation[0], max_display=max_display, show=False)
    plt.tight_layout(rect=[0.15, 0.05, 0.98, 0.95])
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close("all")
