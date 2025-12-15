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


from django.db.models import Q
from usuarios.models import Genero  # asegúrate de importar Genero

class PacienteListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = Usuario
    template_name = 'pacientes/lista.html'
    context_object_name = 'pacientes'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Usuario.objects
            .filter(roles__rol__rol__iexact='paciente')
            .select_related('genero')
            .distinct()
        )

        q = self.request.GET.get('q', '').strip()
        genero_id = self.request.GET.get('genero', '').strip()
        estado = self.request.GET.get('estado', '').strip()

        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(apellido1__icontains=q) |
                Q(apellido2__icontains=q) |
                Q(correo__icontains=q)
            )

        if genero_id:
            qs = qs.filter(genero_id=genero_id)

        if estado:
            qs = qs.filter(estado__iexact=estado)

        return qs.order_by('nombre', 'apellido1')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['genero_seleccionado'] = self.request.GET.get('genero', '')
        ctx['estado_seleccionado'] = self.request.GET.get('estado', '')
        ctx['generos_disponibles'] = Genero.objects.all()
        return ctx


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
