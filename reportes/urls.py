from django.urls import path
from reportes.views import CitaMedicaReporteWebView
from reportes.views_pdf import ReporteCitaPDFView
from reportes.views_pdf_preview import ReporteCitaPDFPreviewView  
from reportes.views_async import ReporteCitaDataAjaxView


app_name = "reportes"

urlpatterns = [
    path("cita/<int:pk>/", CitaMedicaReporteWebView.as_view(), name="reporte_cita_web"),
    path("cita/<int:pk>/pdf/", ReporteCitaPDFView.as_view(), name="reporte_cita_pdf"),
    path("cita/<int:pk>/pdf/preview/", ReporteCitaPDFPreviewView.as_view(), name="reporte_cita_pdf_preview"),
    path("cita/<int:pk>/data/", ReporteCitaDataAjaxView.as_view(), name="reporte_cita_data"),
    
]
