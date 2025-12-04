from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    run = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.run})"

class Causa(models.Model):
    rit = models.CharField(max_length=50, blank=True, null=True)
    ruc = models.CharField(max_length=50, blank=True, null=True)
    tribunal = models.CharField(max_length=100)
    materia = models.CharField(max_length=100)
    caratula = models.CharField(max_length=200)
    estado = models.CharField(max_length=50, default='En estudio')
    fecha_creacion = models.DateField(auto_now_add=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='causas')

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.caratula} ({self.rit or self.ruc or self.id})"

class CausaPersona(models.Model):
    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='personas_en_causa')
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='causas_relacionadas')
    rol_en_causa = models.CharField(max_length=50)

    class Meta:
        unique_together = ('causa', 'persona', 'rol_en_causa')

    def __str__(self):
        return f"{self.persona} como {self.rol_en_causa} en {self.causa}"

class Audiencia(models.Model):
    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='audiencias')
    fecha_hora = models.DateTimeField()
    tipo = models.CharField(max_length=50)
    lugar = models.CharField(max_length=150, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.tipo} - {self.fecha_hora} ({self.causa})"

class Documento(models.Model):
    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='documentos')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=50)
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"
