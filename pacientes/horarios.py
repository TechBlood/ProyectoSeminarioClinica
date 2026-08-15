import datetime

HORA_INICIO = 7
HORA_FIN = 17  # la última cita del día inicia a las 16:00
CUPO_POR_HORA = 3

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']


def horas_disponibles():
    return list(range(HORA_INICIO, HORA_FIN))


def inicio_semana(fecha):
    return fecha - datetime.timedelta(days=fecha.weekday())
