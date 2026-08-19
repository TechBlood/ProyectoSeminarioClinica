import datetime

from django.utils import timezone

HORA_INICIO = 7
HORA_FIN = 17  # la última cita del día inicia a las 16:00
LIMITE_DIAS_ADELANTE = 21  # no se puede agendar más de 3 semanas después de hoy

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']


def horas_disponibles():
    return list(range(HORA_INICIO, HORA_FIN))


def inicio_semana(fecha):
    return fecha - datetime.timedelta(days=fecha.weekday())


def en_el_pasado(fecha, hora):
    momento = timezone.make_aware(datetime.datetime.combine(fecha, hora))
    return momento < timezone.now()


def fuera_de_ventana(fecha):
    return fecha > datetime.date.today() + datetime.timedelta(days=LIMITE_DIAS_ADELANTE)
