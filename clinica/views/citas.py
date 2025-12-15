from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from datetime import date
from django.utils import timezone
from clinica.models import CitaMedica
from clinica.forms import CitaMedicaForm
from django.db.models import Q
from datetime import datetime


class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return getattr(user, 'es_medico', False)

    permission_denied_message = "Solo los usuarios con rol Médico pueden gestionar citas."
    raise_exception = True



class CitaMedicaListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = CitaMedica
    template_name = 'citas/lista.html'
    context_object_name = 'citas'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .filter(doctor=self.request.user)
            .select_related('paciente', 'doctor', 'rango_colesterol', 'rango_glucosa', 'prediccion')
        )

        q = self.request.GET.get('q', '').strip()
        fecha_ini = self.request.GET.get('fecha_ini', '').strip()
        fecha_fin = self.request.GET.get('fecha_fin', '').strip()

        if q:
            qs = qs.filter(
                Q(paciente__nombre__icontains=q) |
                Q(paciente__apellido1__icontains=q) |
                Q(paciente__apellido2__icontains=q) |
                Q(paciente__correo__icontains=q)
            )

        # fechas en formato YYYY-MM-DD
        if fecha_ini:
            qs = qs.filter(fecha_cita__gte=fecha_ini)
        if fecha_fin:
            qs = qs.filter(fecha_cita__lte=fecha_fin)

        return qs.order_by('-fecha_cita', '-id_cita')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['fecha_ini'] = self.request.GET.get('fecha_ini', '')
        ctx['fecha_fin'] = self.request.GET.get('fecha_fin', '')
        return ctx


from django.utils import timezone

class CitaMedicaCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
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
        kwargs['doctor'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        form.instance.estado = form.instance.estado or "ACTIVO"
        form.instance.fecha_actualizacion = timezone.now()
        # fecha_creacion ya tiene default=timezone.now en el modelo
        return super().form_valid(form)


class CitaMedicaUpdateView(LoginRequiredMixin, SoloMedicoMixin, UpdateView):
    """
    Permite a un médico editar SOLO sus propias citas.
    """
    model = CitaMedica
    form_class = CitaMedicaForm
    template_name = 'citas/form.html'
    success_url = reverse_lazy('citas:lista')

    def get_queryset(self):
        # 🔒 Seguridad: no editar citas de otros doctores
        return CitaMedica.objects.filter(doctor=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = self.request.user
        return kwargs

    def form_valid(self, form):
        cita = form.save(commit=False)
        cita.doctor = self.request.user
        cita.fecha_actualizacion = timezone.now()  # ✅ evita nulos y mantiene auditoría
        cita.save()
        return super().form_valid(form)


class CitaMedicaReporteView(LoginRequiredMixin, SoloMedicoMixin, DetailView):
    model = CitaMedica
    template_name = "citas/reporte.html"
    context_object_name = "cita"

    def get_queryset(self):
        # Seguridad: el médico solo ve reportes de SUS citas
        return CitaMedica.objects.filter(doctor=self.request.user)