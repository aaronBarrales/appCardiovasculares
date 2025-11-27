from django.urls import path
from clinica.views import (
    CitaMedicaListView,
    CitaMedicaCreateView,
)

app_name = 'citas'

urlpatterns = [
    path('', CitaMedicaListView.as_view(), name='lista'),
    path('crear/', CitaMedicaCreateView.as_view(), name='crear'),
]
