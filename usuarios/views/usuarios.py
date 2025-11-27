# usuarios/views/usuarios.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from usuarios.models import Usuario, Rol
from usuarios.forms import UsuarioForm   # <-- tu formulario
from .base import AuthenticatedView      # por si luego quieres usarlo
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.urls import reverse_lazy
from datetime import date

from usuarios.models import Usuario

class SoloAdminMixin(UserPassesTestMixin):
    """Restringe el acceso a usuarios con rol de Administrador."""

    def test_func(self):
        user = self.request.user
        return getattr(user, "es_admin", False)

    permission_denied_message = "No tienes permisos para administrar usuarios."
    raise_exception = True  # lanza 403 si no es admin



class UsuarioBloquearView(LoginRequiredMixin, SoloAdminMixin, View):
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.estado = "INACTIVO"
        usuario.fecha_eliminacion = date.today()  # reutilizamos este campo como 'fechaBloqueo'
        usuario.save()
        return redirect('usuarios:lista')


class UsuarioDesbloquearView(LoginRequiredMixin, SoloAdminMixin, View):
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.estado = "ACTIVO"
        # opcional: limpiar fecha_eliminacion
        usuario.fecha_eliminacion = None
        usuario.save()
        return redirect('usuarios:lista')


class UsuarioListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('genero')

        rol_id = self.request.GET.get('rol')
        estado = self.request.GET.get('estado')
        q = self.request.GET.get('q')

        if rol_id:
            qs = qs.filter(roles__rol_id=rol_id)

        if estado:
            qs = qs.filter(estado__iexact=estado)

        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(apellido1__icontains=q) |
                Q(apellido2__icontains=q) |
                Q(correo__icontains=q)
            ).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles_disponibles'] = Rol.objects.all()
        context['estado_seleccionado'] = self.request.GET.get('estado', '')
        context['rol_seleccionado'] = self.request.GET.get('rol', '')
        context['q'] = self.request.GET.get('q', '')
        return context


class UsuarioCreateView(LoginRequiredMixin, SoloAdminMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')


class UsuarioUpdateView(LoginRequiredMixin, SoloAdminMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')


class UsuarioDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_eliminar.html'
    success_url = reverse_lazy('usuarios:lista')
