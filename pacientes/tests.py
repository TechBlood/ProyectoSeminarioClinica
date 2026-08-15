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


