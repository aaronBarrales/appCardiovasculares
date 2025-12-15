from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Rol, UserRol
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False,
        help_text="Obligatoria solo al crear el usuario."
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
            # 'estado',  ← IMPORTANTE: NO lo incluimos
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si es creación, la contraseña es obligatoria
        if not self.instance.pk:
            self.fields['password'].required = True

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Manejo de contraseña
        raw_password = self.cleaned_data.get('password')
        if raw_password:
            usuario.set_password(raw_password)

        # Si es nuevo usuario, por defecto queda ACTIVO
        if not usuario.pk and not usuario.estado:
            usuario.estado = "ACTIVO"

        if commit:
            usuario.save()
            # aquí puedes manejar roles si corresponde
        return usuario




class UsuarioPasswordResetForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")

    def get_users(self, email):
        """
        Devuelve los usuarios activos que tienen ese correo.
        Usamos 'correo' y 'estado' de tu modelo.
        """
        return Usuario.objects.filter(
            correo__iexact=email,
        ).filter(
            models.Q(estado__isnull=True) | models.Q(estado__iexact="ACTIVO")
        )

    def save(
        self,
        domain_override=None,
        subject_template_name='auth/password_reset_subject.txt',
        email_template_name='auth/password_reset_email.html',
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        email = self.cleaned_data["email"]
        from_email = from_email or 'no-reply@cardioapp.local'

        for user in self.get_users(email):
            if not user.password:
                continue  # usuario sin password usable

            context = {
                'email': user.correo,
                'domain': domain_override or request.get_host(),
                'site_name': 'CardioApp',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context:
                context.update(extra_email_context)

            subject = render_to_string(subject_template_name, context).strip()
            body = render_to_string(email_template_name, context)

            send_mail(subject, body, from_email, [user.correo])



from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
