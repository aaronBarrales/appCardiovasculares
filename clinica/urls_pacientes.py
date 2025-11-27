from django.urls import path
from .views import (
    PacienteListView,
    PacienteCreateView,
    PacienteUpdateView,
    PacienteDeleteView,
)

app_name = 'pacientes'

urlpatterns = [
    path('', PacienteListView.as_view(), name='lista'),
    path('crear/', PacienteCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', PacienteUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', PacienteDeleteView.as_view(), name='eliminar'),
]
