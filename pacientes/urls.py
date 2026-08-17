from django.urls import path

from . import views
from .models import Cita

urlpatterns = [
    path('estudios/nuevo/', views.crear_estudio, name='crear_estudio'),
    path('pacientes/buscar-por-dpi/', views.buscar_paciente_por_dpi, name='buscar_paciente_por_dpi'),
    path(
        'pacientes/completar-datos/<int:paciente_id>/',
        views.completar_datos_paciente,
        name='completar_datos_paciente',
    ),
    path('estudios/radiologos-por-estudio/', views.radiologos_por_estudio, name='radiologos_por_estudio'),
    path('pacientes/historial/', views.historial_pacientes, name='historial_pacientes'),
    path('pacientes/historial/<int:paciente_id>/', views.historial_paciente, name='historial_paciente'),
    path(
        'pacientes/historial/estudio/<int:cita_id>/',
        views.ver_estudio_historial,
        name='ver_estudio_historial',
    ),
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
    path(
        'citas/procesar/coex/',
        views.procesar_citas,
        {'convenio': Cita.CONVENIO_COEX},
        name='procesar_citas_coex',
    ),
    path(
        'citas/procesar/coex/<int:cita_id>/llegada/',
        views.marcar_llegada,
        {'convenio': Cita.CONVENIO_COEX},
        name='marcar_llegada_coex',
    ),
    path(
        'citas/procesar/coex/<int:cita_id>/orden/',
        views.generar_orden,
        {'convenio': Cita.CONVENIO_COEX},
        name='generar_orden_coex',
    ),
    path(
        'citas/procesar/coex/<int:cita_id>/ausente/',
        views.marcar_ausente,
        {'convenio': Cita.CONVENIO_COEX},
        name='marcar_ausente_coex',
    ),
    path(
        'citas/procesar/coex/<int:cita_id>/reagendar/',
        views.confirmar_reagenda,
        {'convenio': Cita.CONVENIO_COEX},
        name='confirmar_reagenda_coex',
    ),
    path('citas/solicitudes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('citas/solicitudes/<int:cita_id>/revisar/', views.revisar_solicitud, name='revisar_solicitud'),
    path('ordenes/pendientes/', views.ordenes_pendientes, name='ordenes_pendientes'),
    path('ordenes/pendientes/<int:orden_id>/imagenes/', views.adjuntar_imagenes, name='adjuntar_imagenes'),
    path('citas/procesadas/', views.citas_procesadas, name='citas_procesadas'),
    path('citas/procesadas/<int:cita_id>/informe/', views.adjuntar_informe, name='adjuntar_informe'),
    path('emergencia/tickets/nuevo/', views.registrar_ticket_emergencia, name='registrar_ticket_emergencia'),
    path('emergencia/tickets/', views.pantalla_turnos_emergencia, name='pantalla_turnos_emergencia'),
    path(
        'emergencia/tickets/<int:ticket_id>/procesar/',
        views.procesar_ticket_emergencia,
        name='procesar_ticket_emergencia',
    ),
    path('notificaciones/pendientes/', views.notificaciones_pendientes, name='notificaciones_pendientes'),
    path(
        'notificaciones/<int:notificacion_id>/marcar-leida/',
        views.marcar_notificacion_leida,
        name='marcar_notificacion_leida',
    ),
    path(
        'notificaciones/marcar-todas-leidas/',
        views.marcar_notificaciones_leidas,
        name='marcar_notificaciones_leidas',
    ),
]
