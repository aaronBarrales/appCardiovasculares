from django.urls import path
from .views.usuarios import (
    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioBloquearView,
    UsuarioDesbloquearView,
)

app_name = 'usuarios'

urlpatterns = [
    path('', UsuarioListView.as_view(), name='lista'),
    path('crear/', UsuarioCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', UsuarioUpdateView.as_view(), name='editar'),
    path('<int:pk>/bloquear/', UsuarioBloquearView.as_view(), name='bloquear'),
    path('<int:pk>/desbloquear/', UsuarioDesbloquearView.as_view(), name='desbloquear'),
]
