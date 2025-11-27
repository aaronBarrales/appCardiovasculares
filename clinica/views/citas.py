from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from datetime import date

from clinica.models import CitaMedica
from clinica.forms import CitaMedicaForm


class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return getattr(user, 'es_doctor', False)

    permission_denied_message = "Solo los usuarios con rol Médico pueden gestionar citas."
    raise_exception = True


class CitaMedicaListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    """
    Lista únicamente las citas donde el usuario logueado es el doctor.
    """
    model = CitaMedica
    template_name = 'citas/lista.html'
    context_object_name = 'citas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(doctor=self.request.user).select_related(
            'paciente',
            'rango_colesterol',
            'rango_glucosa',
            'rango_imc',
            'rango_presion_sanguinea',
        )


class CitaMedicaCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
    """
    Permite a un médico crear una cita con cualquier paciente.
    """
    model = CitaMedica
    form_class = CitaMedicaForm
    template_name = 'citas/form.html'
    success_url = reverse_lazy('citas:lista')

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get('paciente')
        if paciente_id:
            initial['paciente'] = paciente_id
        return initial


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = self.request.user   # se pasa al form
        return kwargs

    def form_valid(self, form):
        cita = form.save(commit=False)
        cita.doctor = self.request.user
        # opcional: fecha_creacion automática si la quieres manejar aquí
        if cita.fecha_creacion is None:
            cita.fecha_creacion = date.today()
        cita.estado = cita.estado or "ACTIVO"
        cita.save()
        return super().form_valid(form)
