# clinica/views/pacientes.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Exists, OuterRef

from usuarios.models import Usuario,Rol,UserRol
from clinica.models import CitaMedica
from clinica.forms import PacienteUsuarioForm
from django.db.models import Q


def queryset_pacientes_basico():
    """Usuarios que tienen el rol 'Paciente'."""
    return Usuario.objects.filter(
        roles__rol__rol__iexact='Paciente'
    ).distinct()


class SoloMedicoMixin(UserPassesTestMixin):
    """Restringe acceso a usuarios con rol Médico."""

    def test_func(self):
        user = self.request.user
        return getattr(user, "es_medico", False)

    permission_denied_message = "Solo los usuarios con rol Médico pueden gestionar pacientes."
    raise_exception = True  # devuelve 403 si no es médico


class PacienteListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = Usuario
    template_name = 'pacientes/lista.html'
    context_object_name = 'pacientes'
    paginate_by = 20

    def get_queryset(self):
        # 🔹 Todos los usuarios con rol "Paciente"
        qs = Usuario.objects.filter(
            roles__rol__rol__iexact='Paciente'
        ).distinct()

        # 🔹 Búsqueda opcional por nombre/correo
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(apellido1__icontains=q) |
                Q(apellido2__icontains=q) |
                Q(correo__icontains=q)
            )

        return qs

class PacienteCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
    model = Usuario
    form_class = PacienteUsuarioForm
    template_name = 'pacientes/form.html'
    success_url = reverse_lazy('pacientes:lista')




class PacienteUpdateView(LoginRequiredMixin, SoloMedicoMixin, UpdateView):
    model = Usuario
    form_class = PacienteUsuarioForm
    template_name = 'pacientes/form.html'
    success_url = reverse_lazy('pacientes:lista')

    def get_queryset(self):
        """
        Cualquier médico puede editar a cualquier usuario que tenga rol 'Paciente'.
        """
        return queryset_pacientes_basico()


class PacienteDeleteView(LoginRequiredMixin, SoloMedicoMixin, DeleteView):
    model = Usuario
    template_name = 'pacientes/confirmar_eliminar.html'
    success_url = reverse_lazy('pacientes:lista')

    def get_queryset(self):
        """
        Cualquier médico puede eliminar a cualquier usuario que tenga rol 'Paciente'.
        """
        return queryset_pacientes_basico()
