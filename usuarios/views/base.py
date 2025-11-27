from django.contrib.auth.mixins import LoginRequiredMixin

class AuthenticatedView(LoginRequiredMixin):
    login_url = 'login'
    redirect_field_name = 'next'
