from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('DIRECTOR', 'Director/a Clínica'),
        ('SUPERVISOR', 'Abogado/a Supervisor/a'),
        ('ESTUDIANTE', 'Estudiante/Clínico'),
        ('SECRETARIA', 'Secretaría/Apoyo'),
        ('EXTERNO', 'Persona Atendida'),
    ]

    SEDE_CHOICES = [
        ('SANTIAGO', 'Santiago - Campus Bellavista'),
        ('CONCEPCION', 'Concepción - Campus Las Tres Pascualas'),
        ('VALDIVIA', 'Valdivia - Campus General Lagos'),
        ('PUERTO_MONTT', 'Puerto Montt - Campus Pichi Pelluco'),
        ('OSORNO', 'Osorno - Campus Osorno'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='ESTUDIANTE',
        verbose_name='Rol'
    )
    sede = models.CharField(
        max_length=20,
        choices=SEDE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Sede USS'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el usuario puede acceder al sistema'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_rol_display()}"


# Signal para crear perfil automáticamente cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()