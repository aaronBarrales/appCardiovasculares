# clinica/forms.py
from django import forms
from usuarios.models import Usuario, Rol, UserRol

class PacienteUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False,
        help_text="Obligatoria solo al crear el paciente."
    )

    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido1',
            'apellido2',
            'genero',
            'fecha_nacimiento',
            'correo',
            'estado',
            'password',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True
        else:
            self.fields['password'].required = False

    def save(self, commit=True):
        usuario = super().save(commit=False)

        raw_password = self.cleaned_data.get('password')
        if raw_password:
            usuario.set_password(raw_password)

        if commit:
            usuario.save()

            # Asegurar que tenga rol 'Paciente'
            rol_paciente, _ = Rol.objects.get_or_create(rol='Paciente')
            UserRol.objects.get_or_create(usuario=usuario, rol=rol_paciente)

        return usuario


# clinica/forms.py
from django import forms
from usuarios.models import Usuario
from clinica.models import (
    CitaMedica,
    RangoColesterol,
    RangoGlucosa,
    RangoIMC,
    RangoPresionSanguinea,
)


class CitaMedicaForm(forms.ModelForm):
    class Meta:
        model = CitaMedica
        
        fields = [
            'paciente',
            'fecha_cita',
            'peso',
            'estatura',
            'rango_colesterol',
            'rango_glucosa',
            'rango_imc',
            'rango_presion_sanguinea',
            'alcohol',
            'drogas',
            'actividad_fisica',
            'fumador',
            'notas',
        ]
        widgets = {
            'fecha_cita': forms.DateInput(attrs={'type': 'date'}),
            'peso': forms.NumberInput(attrs={'step': '0.01'}),
            'estatura': forms.NumberInput(attrs={'step': '0.01'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # el doctor logueado viene de la vista
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        # Pacientes = usuarios con rol "Paciente"
        self.fields['paciente'].queryset = Usuario.objects.filter(
            roles__rol__rol__iexact='Paciente'
        ).distinct()

        # Rangos: por ahora todos, si más adelante quieres
        # filtrar por versión_modelo, se hace aquí
        self.fields['rango_colesterol'].queryset = RangoColesterol.objects.all()
        self.fields['rango_glucosa'].queryset = RangoGlucosa.objects.all()
        self.fields['rango_imc'].queryset = RangoIMC.objects.all()
        self.fields['rango_presion_sanguinea'].queryset = RangoPresionSanguinea.objects.all()
