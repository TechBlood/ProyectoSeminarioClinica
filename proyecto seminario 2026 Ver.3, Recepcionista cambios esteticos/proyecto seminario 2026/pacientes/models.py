from django.conf import settings
from django.db import models


class Paciente(models.Model):
    dpi = models.CharField(max_length=20, unique=True, verbose_name='DPI')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField()
    expediente = models.CharField(max_length=30, blank=True, null=True, verbose_name='Número de expediente')

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.dpi})'


class TipoEstudio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tipos_estudio'
        verbose_name = 'tipo de estudio'
        verbose_name_plural = 'tipos de estudio'

    def __str__(self):
        return self.nombre


class Cita(models.Model):
    CONVENIO_COEX = 'coex'
    CONVENIO_PRIVADO = 'privado'
    CONVENIO_EMERGENCIA_IGSS = 'emergencia_igss'

    CONVENIO_CHOICES = [
        (CONVENIO_COEX, 'COEX'),
        (CONVENIO_PRIVADO, 'Privado'),
        (CONVENIO_EMERGENCIA_IGSS, 'Emergencia IGSS'),
    ]

    ESTADO_AGENDADA = 'agendada'
    ESTADO_PROCESADA = 'procesada'
    ESTADO_CANCELADA = 'cancelada'

    ESTADO_CHOICES = [
        (ESTADO_AGENDADA, 'Agendada'),
        (ESTADO_PROCESADA, 'Procesada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='citas')
    tipo_estudio = models.ForeignKey(TipoEstudio, on_delete=models.PROTECT, related_name='citas')
    convenio = models.CharField(max_length=20, choices=CONVENIO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_AGENDADA)
    fecha = models.DateField()
    hora = models.TimeField()
    notas = models.TextField(blank=True)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citas_creadas'
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'citas'
        verbose_name = 'cita'
        verbose_name_plural = 'citas'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f'{self.paciente} - {self.fecha} {self.hora}'


class CambioCita(models.Model):
    ACCION_CANCELAR = 'cancelar'
    ACCION_REPROGRAMAR = 'reprogramar'

    ACCION_CHOICES = [
        (ACCION_CANCELAR, 'Cancelar'),
        (ACCION_REPROGRAMAR, 'Reprogramar'),
    ]

    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='cambios')
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    motivo = models.TextField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cambios_cita'
        verbose_name = 'cambio de cita'
        verbose_name_plural = 'cambios de cita'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f'{self.get_accion_display()} para {self.cita} por {self.usuario} en {self.fecha_cambio}'
