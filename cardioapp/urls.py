from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from usuarios.forms import EmailAuthenticationForm
from usuarios.views.redireccion import redireccion_por_rol
from clinica.views import (
    DoctorDashboardView,
    PacienteDashboardView,
    AdminDashboardView,
    DashboardGenericoView,
)
from usuarios.forms import UsuarioPasswordResetForm
from usuarios.views.password_reset import UsuarioPasswordResetConfirmView

from django.conf import settings
from django.conf.urls.static import static


from django.shortcuts import redirect

def home_redirect(request):
    return redirect("doctor_dashboard")  # o redir_por_rol


urlpatterns = [

    path("", home_redirect, name="home"),
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        authentication_form=EmailAuthenticationForm
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('paciente/dashboard/', PacienteDashboardView.as_view(), name='paciente_dashboard'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),

    path('dashboard/', DashboardGenericoView.as_view(), name='dashboard_generico'),
    path('redir/', redireccion_por_rol, name='redir_por_rol'),

    path('usuarios/', include('usuarios.urls')),
    path('pacientes/', include('clinica.urls_pacientes')),
    path('citas/', include('clinica.urls_citas')),


    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='auth/password_reset_form.html',
            form_class=UsuarioPasswordResetForm,
            email_template_name='auth/password_reset_email.html',
            subject_template_name='auth/password_reset_subject.txt',
            success_url='/password_reset/done/',
        ),
        name='password_reset',
    ),

    # Mensaje de "te enviamos un correo"
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    # Link con token (desde el correo)
    path(
        'reset/<uidb64>/<token>/',
        UsuarioPasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            success_url='/reset/done/',
        ),
        name='password_reset_confirm',
    ),

    # Mensaje de "contraseña cambiada"
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),


    path('admin/', admin.site.urls),
    path("reportes/", include("reportes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)