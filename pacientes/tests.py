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


