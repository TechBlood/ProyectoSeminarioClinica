import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Usuario
from pacientes.models import Cita, Paciente, TipoEstudio, Ticket
from pacientes.views import crear_ticket_emergencia


class CrearTicketEmergenciaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='recepcionista-test',
            password='password123',
            rol=Usuario.ROL_RECEPCIONISTA,
        )
        self.paciente = Paciente.objects.create(
            dpi='1234567890123',
            nombre='Ana',
            apellido='López',
            fecha_nacimiento=datetime.date(1990, 1, 1),
        )
        self.tipo_estudio = TipoEstudio.objects.create(nombre='TAC')

    def test_no_crea_ticket_para_citas_coex(self):
        cita = Cita.objects.create(
            paciente=self.paciente,
            tipo_estudio=self.tipo_estudio,
            convenio=Cita.CONVENIO_COEX,
            fecha=datetime.date.today(),
            hora=datetime.time(10, 0),
            creada_por=self.usuario,
        )

        ticket = crear_ticket_emergencia(self.paciente, cita, Ticket.PRIORIDAD_EMERGENCIA)

        self.assertIsNone(ticket)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_crea_ticket_para_citas_emergencia_igss(self):
        cita = Cita.objects.create(
            paciente=self.paciente,
            tipo_estudio=self.tipo_estudio,
            convenio=Cita.CONVENIO_EMERGENCIA_IGSS,
            fecha=datetime.date.today(),
            hora=datetime.time(10, 0),
            creada_por=self.usuario,
        )

        ticket = crear_ticket_emergencia(self.paciente, cita, Ticket.PRIORIDAD_EMERGENCIA)

        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.servicio, Ticket.SERVICIO_EMERGENCIA)
        self.assertEqual(ticket.prioridad, Ticket.PRIORIDAD_EMERGENCIA)
        self.assertEqual(ticket.cita, cita)
        self.assertEqual(Ticket.objects.count(), 1)
