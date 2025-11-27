# clinica/views/__init__.py

# 👇 IMPORTA TUS DASHBOARDS COMO LOS TENÍAS ANTES
# Si tus dashboards están en clinica/views/dashboard.py:
from .dashboard import (
    DoctorDashboardView,
    PacienteDashboardView,
    AdminDashboardView,
    DashboardGenericoView,
)

# 👇 IMPORTA TAMBIÉN LAS VISTAS DE PACIENTES QUE ACABAMOS DE CREAR
from .pacientes import (
    PacienteListView,
    PacienteCreateView,
    PacienteUpdateView,
    PacienteDeleteView,
)


from .citas import (
    CitaMedicaListView,
    CitaMedicaCreateView,
)
