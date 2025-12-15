from django.urls import path
from clinica.views.citas import (
    CitaMedicaListView,
    CitaMedicaCreateView,
    CitaMedicaUpdateView,      
    CitaMedicaReporteView
)

app_name = 'citas'

urlpatterns = [
    path('', CitaMedicaListView.as_view(), name='lista'),
    path('crear/', CitaMedicaCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', CitaMedicaUpdateView.as_view(), name='editar'),  
    path('<int:pk>/reporte/', CitaMedicaReporteView.as_view(), name='reporte')
]
