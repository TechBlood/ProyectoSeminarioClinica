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


