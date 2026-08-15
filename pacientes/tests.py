import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from pacientes import horarios
from pacientes.forms import AgendarCitaForm, RegistrarTicketForm
from pacientes.models import Cita, ImagenEstudio, Notificacion, OrdenTrabajo, Paciente, Ticket, TipoEstudio

Usuario = get_user_model()


def crear_paciente(**kwargs):
    datos = dict(
        dpi='1234567890101',
        nombre='Juana',
        apellido='Pérez',
        sexo=Paciente.SEXO_FEMENINO,
        fecha_nacimiento=datetime.date(1990, 5, 20),
    )
    datos.update(kwargs)
    return Paciente.objects.create(**datos)


def crear_usuario(username='usuario', **kwargs):
    return Usuario.objects.create_user(username=username, password='clave-segura-123', **kwargs)


def crear_cita(usuario, paciente=None, tipo_estudio=None, **kwargs):
    paciente = paciente or crear_paciente()
    if tipo_estudio is None:
        tipo_estudio, _ = TipoEstudio.objects.get_or_create(nombre='Radiografía de tórax')
    datos = dict(
        paciente=paciente,
        tipo_estudio=tipo_estudio,
        convenio=Cita.CONVENIO_PRIVADO,
        estado=Cita.ESTADO_AGENDADA,
        fecha=timezone.localdate(),
        hora=datetime.time(9, 0),
        creada_por=usuario,
    )
    datos.update(kwargs)
    return Cita.objects.create(**datos)


class PacienteModelTests(TestCase):

    def test_edad_en_antes_de_su_cumpleanos_no_cuenta_el_anio_actual(self):
        paciente = crear_paciente(fecha_nacimiento=datetime.date(2000, 8, 20))
        self.assertEqual(paciente.edad_en(datetime.date(2026, 8, 7)), 25)

    def test_edad_en_el_dia_de_su_cumpleanos_ya_cuenta_el_anio(self):
        paciente = crear_paciente(fecha_nacimiento=datetime.date(2000, 8, 20))
        self.assertEqual(paciente.edad_en(datetime.date(2026, 8, 20)), 26)

    def test_str_incluye_nombre_apellido_y_dpi(self):
        paciente = crear_paciente(nombre='Juana', apellido='Pérez', dpi='1111222233330')
        self.assertEqual(str(paciente), 'Juana Pérez (1111222233330)')


class CitaModelTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario('recepcionista1')

    def test_esta_tarde_es_falso_si_aun_no_vence_la_tolerancia(self):
        ahora = timezone.localtime()
        cita = crear_cita(
            self.usuario,
            estado=Cita.ESTADO_AGENDADA,
            fecha=ahora.date(),
            hora=(ahora + datetime.timedelta(minutes=10)).time(),
        )
        self.assertFalse(cita.esta_tarde)

    def test_esta_tarde_es_verdadero_pasada_la_tolerancia_sin_llegada(self):
        ahora = timezone.localtime()
        hace_una_hora = (ahora - datetime.timedelta(hours=1))
        cita = crear_cita(
            self.usuario,
            estado=Cita.ESTADO_AGENDADA,
            fecha=hace_una_hora.date(),
            hora=hace_una_hora.time(),
        )
        self.assertTrue(cita.esta_tarde)

    def test_esta_tarde_es_falso_si_ya_marco_llegada(self):
        ahora = timezone.localtime()
        hace_una_hora = ahora - datetime.timedelta(hours=1)
        cita = crear_cita(
            self.usuario,
            estado=Cita.ESTADO_AGENDADA,
            fecha=hace_una_hora.date(),
            hora=hace_una_hora.time(),
            hora_llegada=ahora,
        )
        self.assertFalse(cita.esta_tarde)

    def test_esta_tarde_es_falso_si_el_estado_no_es_agendada(self):
        ahora = timezone.localtime()
        hace_una_hora = ahora - datetime.timedelta(hours=1)
        cita = crear_cita(
            self.usuario,
            estado=Cita.ESTADO_PROCESADA,
            fecha=hace_una_hora.date(),
            hora=hace_una_hora.time(),
        )
        self.assertFalse(cita.esta_tarde)

    def test_marcar_ausentes_vencidas_actualiza_citas_de_dias_anteriores(self):
        ayer = timezone.localdate() - datetime.timedelta(days=1)
        cita = crear_cita(self.usuario, estado=Cita.ESTADO_AGENDADA, fecha=ayer, hora=datetime.time(9, 0))

        actualizadas = Cita.marcar_ausentes_vencidas()

        cita.refresh_from_db()
        self.assertEqual(actualizadas, 1)
        self.assertEqual(cita.estado, Cita.ESTADO_AUSENTE)

    def test_marcar_ausentes_vencidas_no_toca_citas_ya_procesadas(self):
        ayer = timezone.localdate() - datetime.timedelta(days=1)
        cita = crear_cita(self.usuario, estado=Cita.ESTADO_PROCESADA, fecha=ayer, hora=datetime.time(9, 0))

        Cita.marcar_ausentes_vencidas()

        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.ESTADO_PROCESADA)

    def test_marcar_ausentes_vencidas_no_toca_citas_futuras(self):
        manana = timezone.localdate() + datetime.timedelta(days=1)
        cita = crear_cita(self.usuario, estado=Cita.ESTADO_AGENDADA, fecha=manana, hora=datetime.time(9, 0))

        Cita.marcar_ausentes_vencidas()

        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.ESTADO_AGENDADA)


class OrdenTrabajoModelTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario('tecnico1')
        self.cita = crear_cita(self.usuario, fecha=datetime.date(2026, 1, 10))

    def test_tiene_informe_es_falso_sin_texto_ni_archivo(self):
        orden = OrdenTrabajo.objects.create(cita=self.cita, motivo='Dolor torácico', creada_por=self.usuario)
        self.assertFalse(orden.tiene_informe)

    def test_tiene_informe_es_verdadero_con_texto(self):
        orden = OrdenTrabajo.objects.create(
            cita=self.cita, motivo='Dolor torácico', creada_por=self.usuario, informe_texto='Sin hallazgos.',
        )
        self.assertTrue(orden.tiene_informe)

    def test_tiene_imagenes_refleja_las_imagenes_asociadas(self):
        orden = OrdenTrabajo.objects.create(cita=self.cita, motivo='Control', creada_por=self.usuario)
        self.assertFalse(orden.tiene_imagenes)

        ImagenEstudio.objects.create(
            orden=orden,
            archivo=SimpleUploadedFile('rx.jpg', b'contenido-falso-de-imagen'),
            subida_por=self.usuario,
        )
        self.assertTrue(orden.tiene_imagenes)

    def test_edad_paciente_usa_la_fecha_de_la_cita_no_la_de_hoy(self):
        paciente = crear_paciente(dpi='9999888877776', fecha_nacimiento=datetime.date(2000, 6, 1))
        cita = crear_cita(self.usuario, paciente=paciente, fecha=datetime.date(2020, 1, 10))
        orden = OrdenTrabajo.objects.create(cita=cita, motivo='Control', creada_por=self.usuario)

        self.assertEqual(orden.edad_paciente, 19)




    def test_horas_disponibles_va_de_inicio_a_fin_sin_incluir_el_fin(self):
        self.assertEqual(horarios.horas_disponibles(), list(range(7, 17)))

    def test_inicio_semana_devuelve_el_lunes_de_esa_semana(self):
        miercoles = datetime.date(2026, 8, 12)  # miércoles
        self.assertEqual(horarios.inicio_semana(miercoles), datetime.date(2026, 8, 10))

    def test_en_el_pasado_es_verdadero_para_un_momento_ya_ocurrido(self):
        ayer = timezone.localdate() - datetime.timedelta(days=1)
        self.assertTrue(horarios.en_el_pasado(ayer, datetime.time(9, 0)))

    def test_en_el_pasado_es_falso_para_un_momento_futuro(self):
        manana = timezone.localdate() + datetime.timedelta(days=1)
        self.assertFalse(horarios.en_el_pasado(manana, datetime.time(9, 0)))

    def test_fuera_de_ventana_es_falso_dentro_del_limite(self):
        fecha = datetime.date.today() + datetime.timedelta(days=horarios.LIMITE_DIAS_ADELANTE)
        self.assertFalse(horarios.fuera_de_ventana(fecha))

    def test_fuera_de_ventana_es_verdadero_pasado_el_limite(self):
        fecha = datetime.date.today() + datetime.timedelta(days=horarios.LIMITE_DIAS_ADELANTE + 1)
        self.assertTrue(horarios.fuera_de_ventana(fecha))



    """HU: cada hand-off del flujo (cita asignada, orden pendiente, estudio
    listo para informar, estudio completado) genera una Notificacion para
    quien tiene que actuar, que la campanita del navegador usa para avisar
    con sonido."""

    def setUp(self):
        self.recepcionista = crear_usuario('recepcionista_notif', rol=Usuario.ROL_RECEPCIONISTA)
        self.tecnico = crear_usuario('tecnico_notif', rol=Usuario.ROL_TECNICO_IMAGENES)
        self.radiologo = crear_usuario('radiologo_notif', rol=Usuario.ROL_MEDICO_RADIOLOGO)
        self.tipo_estudio = TipoEstudio.objects.create(nombre='Radiografía de tórax')

    def test_agendar_cita_notifica_al_radiologo_asignado(self):
        self.client.force_login(self.recepcionista)
        manana = timezone.localdate() + datetime.timedelta(days=1)
        datos = {
            'dpi': '3030303030303',
            'nombre': 'Ana',
            'apellido': 'López',
            'sexo': Paciente.SEXO_FEMENINO,
            'telefono': '',
            'fecha_nacimiento': '1990-01-01',
            'tipo_estudio': self.tipo_estudio.id,
            'radiologo': self.radiologo.id,
            'fecha': manana,
            'hora': '10:00',
            'notas': '',
        }

        self.client.post(f"{reverse('agendar_cita_coex')}?fecha={manana}&hora=10:00", datos)

        cita = Cita.objects.get(paciente__dpi='3030303030303')
        notificacion = Notificacion.objects.get(destinatario=self.radiologo)
        self.assertEqual(notificacion.tipo, Notificacion.TIPO_CITA_ASIGNADA)
        self.assertEqual(notificacion.cita, cita)
        self.assertFalse(notificacion.leida)

    def test_generar_orden_notifica_a_todos_los_tecnicos(self):
        otro_tecnico = crear_usuario('tecnico_notif_2', rol=Usuario.ROL_TECNICO_IMAGENES)
        cita = crear_cita(
            self.recepcionista, radiologo=self.radiologo, convenio=Cita.CONVENIO_COEX,
            estado=Cita.ESTADO_AGENDADA, hora_llegada=timezone.now(),
            # Fecha en el futuro: AutoMarcarAusenteMiddleware pasaría a AUSENTE
            # cualquier cita AGENDADA de hoy si ya son las 18:00 (ver
            # Cita.marcar_ausentes_vencidas), lo que le ganaría la carrera al POST.
            fecha=timezone.localdate() + datetime.timedelta(days=1),
        )
        self.client.force_login(self.recepcionista)

        self.client.post(
            reverse('generar_orden_coex', args=[cita.id]),
            {'motivo': 'Dolor torácico.'},
        )

        for tecnico in (self.tecnico, otro_tecnico):
            notificacion = Notificacion.objects.get(destinatario=tecnico, cita=cita)
            self.assertEqual(notificacion.tipo, Notificacion.TIPO_ORDEN_PENDIENTE)

    def test_adjuntar_imagenes_notifica_al_radiologo_asignado_de_la_cita(self):
        cita = crear_cita(self.recepcionista, radiologo=self.radiologo, estado=Cita.ESTADO_EN_PROCESO)
        orden = OrdenTrabajo.objects.create(cita=cita, motivo='Control.', creada_por=self.recepcionista)
        self.client.force_login(self.tecnico)

        self.client.post(
            reverse('adjuntar_imagenes', args=[orden.id]),
            {'imagenes': [SimpleUploadedFile('foto.jpg', b'contenido', content_type='image/jpeg')]},
        )

        notificacion = Notificacion.objects.get(destinatario=self.radiologo, cita=cita)
        self.assertEqual(notificacion.tipo, Notificacion.TIPO_ESTUDIO_LISTO_INFORMAR)

    def test_adjuntar_imagenes_sin_radiologo_asignado_notifica_a_todos_los_radiologos(self):
        otro_radiologo = crear_usuario('radiologo_notif_2', rol=Usuario.ROL_MEDICO_RADIOLOGO)
        cita = crear_cita(self.recepcionista, radiologo=None, estado=Cita.ESTADO_EN_PROCESO)
        orden = OrdenTrabajo.objects.create(cita=cita, motivo='Control.', creada_por=self.recepcionista)
        self.client.force_login(self.tecnico)

        self.client.post(
            reverse('adjuntar_imagenes', args=[orden.id]),
            {'imagenes': [SimpleUploadedFile('foto.jpg', b'contenido', content_type='image/jpeg')]},
        )

        for radiologo in (self.radiologo, otro_radiologo):
            self.assertTrue(
                Notificacion.objects.filter(
                    destinatario=radiologo, cita=cita, tipo=Notificacion.TIPO_ESTUDIO_LISTO_INFORMAR,
                ).exists()
            )

    def test_adjuntar_informe_notifica_a_todos_los_recepcionistas(self):
        otro_recepcionista = crear_usuario('recepcionista_notif_2', rol=Usuario.ROL_RECEPCIONISTA)
        cita = crear_cita(self.recepcionista, radiologo=self.radiologo, estado=Cita.ESTADO_EN_PROCESO)
        orden = OrdenTrabajo.objects.create(cita=cita, motivo='Control.', creada_por=self.recepcionista)
        ImagenEstudio.objects.create(
            orden=orden,
            archivo=SimpleUploadedFile('foto.jpg', b'contenido', content_type='image/jpeg'),
            subida_por=self.tecnico,
        )
        self.client.force_login(self.radiologo)

        self.client.post(
            reverse('adjuntar_informe', args=[cita.id]),
            {'informe_texto': 'Sin hallazgos patológicos.'},
        )

        for recepcionista in (self.recepcionista, otro_recepcionista):
            notificacion = Notificacion.objects.get(destinatario=recepcionista, cita=cita)
            self.assertEqual(notificacion.tipo, Notificacion.TIPO_ESTUDIO_COMPLETADO)

    def test_procesar_ticket_emergencia_notifica_a_los_tecnicos(self):
        paciente = crear_paciente(dpi='4040404040404')
        ticket = Ticket.objects.create(
            paciente=paciente, servicio=Ticket.SERVICIO_EMERGENCIA_IGSS, registrado_por=self.recepcionista,
        )
        self.client.force_login(self.recepcionista)

        self.client.post(
            reverse('procesar_ticket_emergencia', args=[ticket.id]),
            {'tipo_estudio': self.tipo_estudio.id, 'motivo': 'Trauma.'},
        )

        self.assertTrue(
            Notificacion.objects.filter(
                destinatario=self.tecnico, tipo=Notificacion.TIPO_ORDEN_PENDIENTE,
            ).exists()
        )


