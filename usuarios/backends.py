from django.contrib.auth.backends import BaseBackend
from usuarios.models import Usuario  # importa tu modelo

class EmailBackend(BaseBackend):
    """
    Backend que autentica contra el modelo Usuario usando el campo 'correo'.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # username aquí es el correo que viene del formulario
        correo = username or kwargs.get('email')

        if correo is None or password is None:
            return None

        try:
            user = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
