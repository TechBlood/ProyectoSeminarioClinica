import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils import timezone


def validar_dpi_guatemala(value):
    if not re.fullmatch(r'\d{13}', value or ''):
        raise ValidationError('El DPI debe contener exactamente 13 dígitos numéricos.')


def validar_nombre_apellido(value):
    if not re.fullmatch(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value or ''):
        raise ValidationError('El nombre y el apellido solo pueden contener letras y espacios.')


class Paciente(models.Model):
    dpi = models.CharField(max_length=20, unique=True, verbose_name='DPI', validators=[validar_dpi_guatemala])
    nombre = models.CharField(max_length=100, validators=[validar_nombre_apellido])
    apellido = models.CharField(max_length=100, validators=[validar_nombre_apellido])
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField()
    expediente = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='No. Expediente Interno',
        editable=False,
    )
    expediente_igss = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Expediente IGSS (opcional)',
    )

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.dpi})'

    def generar_expediente_interno(self):
        fecha = timezone.localtime(timezone.now()).date()
        prefijo = 'COEX'
        existentes = Paciente.objects.filter(expediente__isnull=False)
        contador = 0
        for paciente in existentes:
            if paciente.expediente:
                match = re.search(r'(\d+)$', paciente.expediente)
                if match:
                    contador = max(contador, int(match.group(1)))
        return f'CI-{fecha.year % 100:02d}-{contador + 1:04d}'

    def save(self, *args, **kwargs):
        if not self.expediente:
            self.expediente = self.generar_expediente_interno()
        super().save(*args, **kwargs)


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


class Ticket(models.Model):
    SERVICIO_COEX = 'coex'
    SERVICIO_PRIVADO = 'privado'
    SERVICIO_IGSS = 'igss'
    SERVICIO_EMERGENCIA = 'emergencia'

    SERVICIO_CHOICES = [
        (SERVICIO_COEX, 'COEX'),
        (SERVICIO_PRIVADO, 'Privado'),
        (SERVICIO_IGSS, 'IGSS'),
        (SERVICIO_EMERGENCIA, 'Emergencia'),
    ]

    PRIORIDAD_NORMAL = 1
    PRIORIDAD_ALTA = 2
    PRIORIDAD_EMERGENCIA = 3

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_NORMAL, 'Normal'),
        (PRIORIDAD_ALTA, 'Alta'),
        (PRIORIDAD_EMERGENCIA, 'Emergencia'),
    ]

    ESTADO_EN_ESPERA = 'en_espera'
    ESTADO_EN_PROCESO = 'en_proceso'
    ESTADO_REAGENDADO = 'reagendado'
    ESTADO_AUSENTE = 'ausente'
    ESTADO_COMPLETADO = 'completado'

    ESTADO_CHOICES = [
        (ESTADO_EN_ESPERA, 'En Espera'),
        (ESTADO_EN_PROCESO, 'En Proceso'),
        (ESTADO_REAGENDADO, 'Reagendado'),
        (ESTADO_AUSENTE, 'Ausente'),
        (ESTADO_COMPLETADO, 'Completado'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='tickets', null=True, blank=True)
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, related_name='tickets', null=True, blank=True)
    servicio = models.CharField(max_length=20, choices=SERVICIO_CHOICES)
    prioridad = models.PositiveSmallIntegerField(choices=PRIORIDAD_CHOICES, default=PRIORIDAD_NORMAL)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_EN_ESPERA)
    numero_diario = models.PositiveIntegerField(default=0, editable=False)
    turno = models.CharField(max_length=20, blank=True, editable=False)
    hora_llegada = models.DateTimeField(blank=True, null=True)
    hora_llamado = models.DateTimeField(blank=True, null=True)
    hora_inicio_estudio = models.DateTimeField(blank=True, null=True)
    hora_fin_estudio = models.DateTimeField(blank=True, null=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'
        ordering = ['-prioridad', 'hora_llegada']

    def __str__(self):
        return f'{self.turno} - {self.paciente or "Paciente desconocido"}'

    def save(self, *args, **kwargs):
        if not self.hora_llegada:
            self.hora_llegada = timezone.now()

        if self.numero_diario == 0:
            fecha = self.hora_llegada.date()
            ultimo = Ticket.objects.filter(servicio=self.servicio, hora_llegada__date=fecha).aggregate(max_num=Max('numero_diario'))
            self.numero_diario = (ultimo['max_num'] or 0) + 1

        if not self.turno:
            prefijo = {
                Ticket.SERVICIO_COEX: 'COEX',
                Ticket.SERVICIO_IGSS: 'IGSS',
                Ticket.SERVICIO_EMERGENCIA: 'EMERG',
            }.get(self.servicio, self.servicio.upper())
            self.turno = f'{prefijo}-{self.numero_diario:03d}'

        super().save(*args, **kwargs)

    @property
    def tiempo_espera(self):
        if self.hora_llamado and self.hora_llegada:
            return self.hora_llamado - self.hora_llegada
        return None

    @property
    def minutos_espera(self):
        espera = self.tiempo_espera
        return int(espera.total_seconds() // 60) if espera else None


class TicketCambioEstado(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='cambios_estado')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    prioridad_anterior = models.PositiveSmallIntegerField()
    prioridad_nueva = models.PositiveSmallIntegerField()
    razon = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tickets_cambios_estado'
        verbose_name = 'cambio de estado de ticket'
        verbose_name_plural = 'cambios de estado de ticket'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f'{self.ticket.turno}: {self.estado_anterior} -> {self.estado_nuevo} por {self.usuario}'
