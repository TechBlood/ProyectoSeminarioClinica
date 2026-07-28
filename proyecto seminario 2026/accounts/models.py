from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Usuario(AbstractUser):
    ROL_ADMINISTRADOR = 'administrador'
    ROL_RECEPCIONISTA = 'recepcionista'
    ROL_TECNICO_IMAGENES = 'tecnico_imagenes'
    ROL_MEDICO_RADIOLOGO = 'medico_radiologo'
    ROL_MEDICO_REMITENTE = 'medico_remitente'

    ROL_CHOICES = [
        (ROL_ADMINISTRADOR, 'Administrador'),
        (ROL_RECEPCIONISTA, 'Recepcionista'),
        (ROL_TECNICO_IMAGENES, 'Técnico de imágenes'),
        (ROL_MEDICO_RADIOLOGO, 'Médico radiólogo'),
        (ROL_MEDICO_REMITENTE, 'Médico remitente'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=ROL_ADMINISTRADOR,
        verbose_name='rol',
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='grupos',
        blank=True,
        related_name='usuario_set',
        related_query_name='usuario',
        db_table='usuarios_grupos',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permisos',
        blank=True,
        related_name='usuario_set',
        related_query_name='usuario',
        db_table='usuarios_permisos',
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
