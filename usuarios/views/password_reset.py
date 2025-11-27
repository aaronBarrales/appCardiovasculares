from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from usuarios.models import Usuario


class UsuarioPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Igual que la vista de Django, pero usando el modelo Usuario
    en lugar de get_user_model().
    """

    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None
        return user
