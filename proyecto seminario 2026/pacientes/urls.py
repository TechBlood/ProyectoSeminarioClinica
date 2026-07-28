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
]
