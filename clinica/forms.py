from django import forms
from usuarios.models import Usuario, Rol, UserRol
from clinica.models import CitaMedica, RangoColesterol, RangoGlucosa


# =========================================================
# Formulario para crear/editar pacientes (usuario)
# =========================================================
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
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Password obligatorio solo al crear
        self.fields['password'].required = not bool(self.instance and self.instance.pk)

    def save(self, commit=True):
        usuario = super().save(commit=False)

        raw_password = self.cleaned_data.get('password')
        if raw_password:
            usuario.set_password(raw_password)

        if commit:
            usuario.save()

            # Asegurar rol 'paciente' (OJO: en tu BD lo insertaste en minúsculas)
            rol_paciente, _ = Rol.objects.get_or_create(rol='paciente')
            UserRol.objects.get_or_create(usuario=usuario, rol=rol_paciente)

        return usuario


# =========================================================
# Formulario de Cita Médica (captura de variables crudas)
# =========================================================
class CitaMedicaForm(forms.ModelForm):
    class Meta:
        model = CitaMedica
        fields = [
            'paciente',
            

            # Crudos para el modelo / captura clínica
            'peso',
            'estatura',
            'colesterol_total',
            'glucosa',
            'presion_sistolica',
            'presion_diastolica',
    


            # Estilo de vida
            'alcohol',
            'drogas',
            'actividad_fisica',
            'fumador',

            'notas',
        ]
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-control',
            }),

            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg (ej. 72.5)',
                'step': '0.01',
                'min': '0'
            }),
            'estatura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estatura en centímetros (ej. 170)',
                'step': '1',
                'min': '0'
            }),
            'colesterol_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Colesterol total (mg/dL)',
                'step': '0.01',
                'min': '0'
            }),
            'glucosa': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Glucosa (mg/dL)',
                'step': '0.01',
                'min': '0'
            }),
            'presion_sistolica': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Presión sistólica (mmHg)',
                'step': '1',
                'min': '0'
            }),
            'presion_diastolica': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Presión diastólica (mmHg)',
                'step': '1',
                'min': '0'
            }),

            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones clínicas relevantes',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        # El doctor logueado viene de la vista
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        # Pacientes = usuarios con rol "paciente"
        self.fields['paciente'].queryset = Usuario.objects.filter(
            roles__rol__rol__iexact='paciente'
        ).distinct()

        # Rangos derivados (opcionales). Si luego filtras por version_modelo, se hace aquí.
        if 'rango_colesterol' in self.fields:
            self.fields['rango_colesterol'].queryset = RangoColesterol.objects.all()
        if 'rango_glucosa' in self.fields:
            self.fields['rango_glucosa'].queryset = RangoGlucosa.objects.all()

    def save(self, commit=True):
        cita = super().save(commit=False)

        # Asignar doctor automáticamente si viene de la vista
        if self.doctor is not None:
            cita.doctor = self.doctor

        if commit:
            cita.save()

        return cita
