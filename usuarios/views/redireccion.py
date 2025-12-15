from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redireccion_por_rol(request):
    user = request.user 

    if getattr(user, 'es_admin', False):
        return redirect('admin_dashboard')

    if getattr(user, 'es_medico', False):  
        return redirect('doctor_dashboard')

    if getattr(user, 'es_paciente', False):
        return redirect('paciente_dashboard')

    return redirect('dashboard_generico')
