from django.urls import path

from . import views
from .models import Cita

urlpatterns = [
    path(
        'citas/calendario/coex/',
        views.seleccionar_horario,
        {'convenio': Cita.CONVENIO_COEX},
        name='calendario_coex',
    ),
    path(
        'citas/calendario/privado/',
        views.seleccionar_horario,
        {'convenio': Cita.CONVENIO_PRIVADO},
        name='calendario_privado',
    ),
    path(
        'citas/calendario/emergencia-igss/',
        views.seleccionar_horario,
        {'convenio': Cita.CONVENIO_EMERGENCIA_IGSS},
        name='calendario_emergencia_igss',
    ),
    path(
        'citas/agendar/coex/',
        views.agendar_cita,
        {'convenio': Cita.CONVENIO_COEX},
        name='agendar_cita_coex',
    ),
    path(
        'citas/agendar/privado/',
        views.agendar_cita,
        {'convenio': Cita.CONVENIO_PRIVADO},
        name='agendar_cita_privado',
    ),
    path(
        'citas/agendar/emergencia-igss/',
        views.agendar_cita,
        {'convenio': Cita.CONVENIO_EMERGENCIA_IGSS},
        name='agendar_cita_emergencia_igss',
    ),
    # Nuevas rutas para pacientes
    path('pacientes/registrar/', views.registrar_paciente, name='registrar_paciente'),
    path('pacientes/buscar/', views.buscar_paciente, name='buscar_paciente'),
    path('pacientes/editar/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('citas/<int:cita_id>/cancelar/', views.cancelar_cita, name='cancelar_cita'),
]
