import datetime

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

MINUTOS_TOLERANCIA_LLEGADA = 15


class Paciente(models.Model):
    SEXO_MASCULINO = 'M'
    SEXO_FEMENINO = 'F'

    SEXO_CHOICES = [
        (SEXO_MASCULINO, 'Masculino'),
        (SEXO_FEMENINO, 'Femenino'),
    ]

    dpi = models.CharField(max_length=20, unique=True, verbose_name='DPI')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField()

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.dpi})'

    def edad_en(self, fecha):
        años = fecha.year - self.fecha_nacimiento.year
        if (fecha.month, fecha.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            años -= 1
        return años


class TipoEstudio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

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

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_AGENDADA = 'agendada'
    ESTADO_EN_PROCESO = 'en_proceso'
    ESTADO_PROCESADA = 'procesada'
    ESTADO_AUSENTE = 'ausente'
    ESTADO_RECHAZADA = 'rechazada'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente de confirmación'),
        (ESTADO_AGENDADA, 'Agendada'),
        (ESTADO_EN_PROCESO, 'En proceso'),
        (ESTADO_PROCESADA, 'Procesada'),
        (ESTADO_AUSENTE, 'Ausente'),
        (ESTADO_RECHAZADA, 'Rechazada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='citas')
    tipo_estudio = models.ForeignKey(TipoEstudio, on_delete=models.PROTECT, related_name='citas')
    radiologo = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='citas_asignadas',
    )
    convenio = models.CharField(max_length=20, choices=CONVENIO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    fecha = models.DateField()
    hora = models.TimeField()
    fecha_sugerida = models.DateField(null=True, blank=True)
    hora_sugerida = models.TimeField(null=True, blank=True)
    hora_llegada = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citas_creadas'
    )
    creada_en = models.DateTimeField(auto_now_add=True)
    revisada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='citas_revisadas',
    )
    revisada_en = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)

    class Meta:
        db_table = 'citas'
        verbose_name = 'cita'
        verbose_name_plural = 'citas'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f'{self.paciente} - {self.fecha} {self.hora}'

    @property
    def esta_tarde(self):
        if self.estado != self.ESTADO_AGENDADA or self.hora_llegada:
            return False
        hora_cita = timezone.make_aware(datetime.datetime.combine(self.fecha, self.hora))
        limite = hora_cita + datetime.timedelta(minutes=MINUTOS_TOLERANCIA_LLEGADA)
        return timezone.now() > limite

    @classmethod
    def marcar_ausentes_vencidas(cls):
        """Pasa a AUSENTE toda cita AGENDADA cuyo día ya pasó, o que es de hoy
        pero ya son las 18:00 y nadie la marcó ausente/llegada."""
        ahora = timezone.localtime()
        hoy = ahora.date()
        fecha_limite = hoy if ahora.time() >= datetime.time(18, 0) else hoy - datetime.timedelta(days=1)
        return cls.objects.filter(
            estado=cls.ESTADO_AGENDADA, fecha__lte=fecha_limite
        ).update(estado=cls.ESTADO_AUSENTE)


class OrdenTrabajo(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.PROTECT, related_name='orden_trabajo')
    motivo = models.TextField(verbose_name='motivo / indicación clínica')
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ordenes_trabajo_creadas'
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    informe_texto = models.TextField(blank=True, verbose_name='informe (texto)')
    informe_archivo = models.FileField(
        upload_to='informes/%Y/%m/', blank=True, null=True, verbose_name='informe (archivo)'
    )
    informe_creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='informes_creados',
    )
    informe_creado_en = models.DateTimeField(null=True, blank=True)

    @property
    def tiene_informe(self):
        return bool(self.informe_texto or self.informe_archivo)

    @property
    def tiene_imagenes(self):
        return self.imagenes.exists()

    class Meta:
        db_table = 'ordenes_trabajo'
        verbose_name = 'orden de trabajo'
        verbose_name_plural = 'órdenes de trabajo'
        ordering = ['creada_en']

    def __str__(self):
        return f'Orden #{self.id} - {self.cita.paciente}'

    @property
    def edad_paciente(self):
        return self.cita.paciente.edad_en(self.cita.fecha)


class ImagenEstudio(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='imagenes')
    archivo = models.FileField(upload_to='imagenes_estudio/%Y/%m/')
    subida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='imagenes_subidas'
    )
    subida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imagenes_estudio'
        verbose_name = 'imagen de estudio'
        verbose_name_plural = 'imágenes de estudio'
        ordering = ['subida_en']

    def __str__(self):
        return f'Imagen #{self.id} - Orden #{self.orden_id}'


class Ticket(models.Model):
    """Turno de la fila de recepción para pacientes que llegan sin cita
    agendada (walk-in). Por ahora solo se usa desde la pantalla de
    Emergencia IGSS, pero el campo `servicio` queda abierto para reusar
    este mismo sistema de turnos en COEX/Privado más adelante."""

    SERVICIO_COEX = 'coex'
    SERVICIO_PRIVADO = 'privado'
    SERVICIO_EMERGENCIA_IGSS = 'emergencia_igss'

    SERVICIO_CHOICES = [
        (SERVICIO_COEX, 'COEX'),
        (SERVICIO_PRIVADO, 'Privado'),
        (SERVICIO_EMERGENCIA_IGSS, 'Emergencia IGSS'),
    ]

    PREFIJO_TURNO = {
        SERVICIO_COEX: 'COEX',
        SERVICIO_PRIVADO: 'PRIV',
        SERVICIO_EMERGENCIA_IGSS: 'EMER',
    }

    PRIORIDAD_NORMAL = 1
    PRIORIDAD_URGENTE = 2
    PRIORIDAD_CRITICA = 3

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_NORMAL, 'Normal'),
        (PRIORIDAD_URGENTE, 'Urgente'),
        (PRIORIDAD_CRITICA, 'Crítica'),
    ]

    ESTADO_EN_ESPERA = 'en_espera'
    ESTADO_EN_ATENCION = 'en_atencion'
    ESTADO_ATENDIDO = 'atendido'
    ESTADO_AUSENTE = 'ausente'

    ESTADO_CHOICES = [
        (ESTADO_EN_ESPERA, 'En espera'),
        (ESTADO_EN_ATENCION, 'En atención'),
        (ESTADO_ATENDIDO, 'Atendido'),
        (ESTADO_AUSENTE, 'Ausente'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='tickets')
    cita = models.ForeignKey(
        'Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_origen',
        help_text='Cita/orden de trabajo generada al procesar este ticket (si ya se procesó).',
    )
    servicio = models.CharField(max_length=20, choices=SERVICIO_CHOICES)
    prioridad = models.PositiveSmallIntegerField(choices=PRIORIDAD_CHOICES, default=PRIORIDAD_NORMAL)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_EN_ESPERA)
    numero = models.PositiveIntegerField(editable=False, default=0)
    turno = models.CharField(max_length=20, editable=False, blank=True)
    motivo = models.CharField(max_length=255, blank=True, verbose_name='motivo de la visita')
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tickets_registrados',
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    atendido_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tickets'
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'
        ordering = ['-prioridad', 'creado_en']

    def __str__(self):
        return f'{self.turno} - {self.paciente}'

    def save(self, *args, **kwargs):
        if self.turno:
            super().save(*args, **kwargs)
            return

        fecha = timezone.localdate()
        with transaction.atomic():
            # DailySequence garantiza un solo contador por (servicio, fecha),
            # incluso si dos recepcionistas registran un ticket al mismo tiempo.
            secuencia, _ = DailySequence.objects.select_for_update().get_or_create(
                servicio=self.servicio, fecha=fecha,
            )
            secuencia.ultimo += 1
            secuencia.save(update_fields=['ultimo'])
            self.numero = secuencia.ultimo
            self.turno = f'{self.PREFIJO_TURNO.get(self.servicio, self.servicio.upper())}-{self.numero:03d}'
            super().save(*args, **kwargs)


class Notificacion(models.Model):
    """Aviso interno para un usuario (con sonido en el navegador) cuando el
    flujo de trabajo le asigna algo nuevo: una cita, una orden, un estudio
    listo para informar, o un informe ya terminado."""

    TIPO_CITA_ASIGNADA = 'cita_asignada'
    TIPO_ORDEN_PENDIENTE = 'orden_pendiente'
    TIPO_ESTUDIO_LISTO_INFORMAR = 'estudio_listo_informar'
    TIPO_ESTUDIO_COMPLETADO = 'estudio_completado'

    TIPO_CHOICES = [
        (TIPO_CITA_ASIGNADA, 'Nueva cita asignada'),
        (TIPO_ORDEN_PENDIENTE, 'Nueva orden de trabajo pendiente'),
        (TIPO_ESTUDIO_LISTO_INFORMAR, 'Estudio listo para informar'),
        (TIPO_ESTUDIO_COMPLETADO, 'Estudio completado'),
    ]

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones',
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    mensaje = models.CharField(max_length=255)
    cita = models.ForeignKey(
        Cita, on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones',
    )
    url = models.CharField(max_length=255, blank=True, verbose_name='enlace')
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'notificación'
        verbose_name_plural = 'notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f'{self.destinatario} - {self.mensaje}'

    @classmethod
    def notificar(cls, *, destinatario, tipo, mensaje, cita=None, url=''):
        return cls.objects.create(
            destinatario=destinatario, tipo=tipo, mensaje=mensaje, cita=cita, url=url,
        )

    @classmethod
    def notificar_a_varios(cls, *, usuarios, tipo, mensaje, cita=None, url=''):
        usuarios = list(usuarios)
        if not usuarios:
            return []
        return cls.objects.bulk_create([
            cls(destinatario=usuario, tipo=tipo, mensaje=mensaje, cita=cita, url=url)
            for usuario in usuarios
        ])


class DailySequence(models.Model):
    """Contador diario por servicio para generar el número de turno de los
    tickets (ver Ticket.save). Una fila por (servicio, fecha)."""

    servicio = models.CharField(max_length=20)
    fecha = models.DateField()
    ultimo = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'secuencias_diarias_tickets'
        verbose_name = 'secuencia diaria de tickets'
        verbose_name_plural = 'secuencias diarias de tickets'
        unique_together = ('servicio', 'fecha')

    def __str__(self):
        return f'{self.servicio} {self.fecha} -> {self.ultimo}'
