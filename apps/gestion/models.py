from django.db import models
from django.contrib.auth.models import User
from .validators import (
    validar_rut_chileno,
    validar_telefono_chileno,
    validar_rit,
    validar_ruc,
    validar_fecha_nacimiento,
)

# CATÁLOGOS 
class Tribunal(models.Model):
    TIPO_CHOICES = [
        # Tribunales Ordinarios
        ('JUZ_CIVIL', 'Juzgado de Letras en lo Civil'),
        ('JUZ_LABORAL', 'Juzgado de Letras del Trabajo'),
        ('JUZ_COBRANZA', 'Juzgado de Cobranza Laboral y Previsional'),
        ('JUZ_FAMILIA', 'Juzgado de Familia'),
        ('JUZ_GARANTIA', 'Juzgado de Garantía'),
        ('TOP', 'Tribunal de Juicio Oral en lo Penal'),
        ('JUZ_LETRAS', 'Juzgado de Letras (Competencia Común)'),
        
        # Tribunales Superiores
        ('CORTE_AP', 'Corte de Apelaciones'),
        ('CORTE_SUPREMA', 'Corte Suprema'),
        
        # Tribunales Especiales
        ('JPL', 'Juzgado de Policía Local'),
        ('TRIB_MILITAR', 'Tribunal Militar'),
        ('TRIB_AMBIENTAL', 'Tribunal Ambiental'),
        ('TRIB_CONTRATACION', 'Tribunal de Contratación Pública'),
        ('TRIB_TRIBUTARIO', 'Tribunal Tributario y Aduanero'),
        ('TRIB_PROPIEDAD', 'Tribunal de Propiedad Industrial'),
        
        # Otro
        ('OTRO', 'Otro'),
    ]
    
    REGION_CHOICES = [
        ('RM', 'Región Metropolitana'),
        ('BIOBIO', 'Región del Biobío'),
        ('LOS_RIOS', 'Región de Los Ríos'),
        ('LOS_LAGOS', 'Región de Los Lagos'),
    ]
    
    # Campos obligatorios
    nombre = models.CharField(max_length=150, verbose_name='Nombre del tribunal')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de tribunal')
    region = models.CharField(max_length=20, choices=REGION_CHOICES, verbose_name='Región')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    # Campos opcionales
    codigo = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código interno')
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dirección')
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comuna')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo electrónico')
    sitio_web = models.URLField(blank=True, null=True, verbose_name='Sitio web')

    class Meta:
        ordering = ['region', 'ciudad', 'tipo', 'nombre']
        verbose_name = 'Tribunal'
        verbose_name_plural = 'Tribunales'
        indexes = [
            models.Index(fields=['tipo'], name='tribunal_tipo_idx'),
            models.Index(fields=['region'], name='tribunal_region_idx'),
            models.Index(fields=['ciudad'], name='tribunal_ciudad_idx'),
            models.Index(fields=['activo'], name='tribunal_activo_idx'),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"

class Materia(models.Model):
    TIPO_TRIBUNAL_CHOICES = [
        ('JUZ_CIVIL', 'Civil'),
        ('JUZ_LABORAL', 'Laboral'),
        ('JUZ_COBRANZA', 'Cobranza Laboral'),
        ('JUZ_FAMILIA', 'Familia'),
        ('JUZ_GARANTIA', 'Penal (Garantía)'),
        ('TOP', 'Penal (Juicio Oral)'),
        ('JUZ_LETRAS', 'Competencia Común'),
        ('CORTE_AP', 'Corte de Apelaciones'),
        ('CORTE_SUPREMA', 'Corte Suprema'),
        ('JPL', 'Policía Local'),
        ('TRIB_MILITAR', 'Militar'),
        ('TRIB_AMBIENTAL', 'Ambiental'),
        ('TRIB_CONTRATACION', 'Contratación Pública'),
        ('TRIB_TRIBUTARIO', 'Tributario y Aduanero'),
        ('TRIB_PROPIEDAD', 'Propiedad Industrial'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100, verbose_name='Nombre de la materia')
    tipo_tribunal = models.CharField(
        max_length=20, 
        choices=TIPO_TRIBUNAL_CHOICES, 
        verbose_name='Tipo de tribunal'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        ordering = ['tipo_tribunal', 'nombre']
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        indexes = [
            models.Index(fields=['tipo_tribunal'], name='materia_tipo_idx'),
            models.Index(fields=['activo'], name='materia_activo_idx'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_tribunal_display()})"
    
class TipoDocumento(models.Model):
    CATEGORIA_CHOICES = [
        ('JUDICIAL_ENTRADA', 'Judicial (recibido del tribunal)'),
        ('JUDICIAL_SALIDA', 'Judicial (presentado al tribunal)'),
        ('INTERNO', 'Documento interno'),
        ('PRUEBA', 'Medio de prueba'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIA_CHOICES, 
        verbose_name='Categoría'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    requiere_folio = models.BooleanField(default=False, verbose_name='Requiere folio')
    requiere_fecha_emision = models.BooleanField(
        default=False, 
        verbose_name='Requiere fecha de emisión'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        indexes = [
            models.Index(fields=['categoria'], name='tipo_doc_cat_idx'),
            models.Index(fields=['activo'], name='tipo_doc_activo_idx'),
        ]

    def __str__(self):
        return f"{self.nombre}"
    
class EstadoCausa(models.Model):
    COLOR_CHOICES = [
        ('gray', 'Gris'),
        ('blue', 'Azul'),
        ('yellow', 'Amarillo'),
        ('green', 'Verde'),
        ('red', 'Rojo'),
        ('orange', 'Naranjo'),
        ('purple', 'Morado'),
    ]

    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='gray',
        verbose_name='Color'
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden en el flujo procesal (menor = más temprano)'
    )
    es_final = models.BooleanField(
        default=False,
        verbose_name='Es estado final',
        help_text='Marca si este estado cierra/archiva la causa'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        ordering = ['orden']
        verbose_name = 'Estado de Causa'
        verbose_name_plural = 'Estados de Causa'
        indexes = [
            models.Index(fields=['orden'], name='estado_orden_idx'),
            models.Index(fields=['activo'], name='estado_activo_idx'),
            models.Index(fields=['es_final'], name='estado_final_idx'),
        ]

    def __str__(self):
        return self.nombre
    
# MODELOS PRINCIPALES
class Persona(models.Model):
    TIPO_PERSONA_CHOICES = [
        ('ATENDIDO', 'Persona atendida'),
        ('CONTRAPARTE', 'Contraparte'),
        ('TESTIGO', 'Testigo'),
        ('PERITO', 'Perito'),
        ('TERCERO', 'Tercero interesado'),
        ('OTRO', 'Otro'),
    ]

    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('NI', 'No informa'),
    ]

    ESTADO_CIVIL_CHOICES = [
        ('SOLTERO', 'Soltero/a'),
        ('CASADO', 'Casado/a'),
        ('DIVORCIADO', 'Divorciado/a'),
        ('VIUDO', 'Viudo/a'),
        ('CONVIVIENTE', 'Conviviente civil'),
        ('SEPARADO', 'Separado/a'),
        ('NI', 'No informa'),
    ]

    REGION_CHOICES = [
        ('RM', 'Región Metropolitana'),
        ('BIOBIO', 'Región del Biobío'),
        ('LOS_RIOS', 'Región de Los Ríos'),
        ('LOS_LAGOS', 'Región de Los Lagos'),
        ('OTRA', 'Otra región'),
    ]

    # Identificación básica
    run = models.CharField(
        'RUN', 
        max_length=12, 
        unique=True,
        validators=[validar_rut_chileno],
        help_text='Formato: 12.345.678-9'
    )
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    tipo_persona = models.CharField(
        max_length=20,
        choices=TIPO_PERSONA_CHOICES,
        default='ATENDIDO',
        verbose_name='Tipo de persona'
    )

    # Datos personales
    fecha_nacimiento = models.DateField(
        'Fecha de nacimiento', 
        null=True, 
        blank=True,
        validators=[validar_fecha_nacimiento]
    )
    genero = models.CharField(
        max_length=2,
        choices=GENERO_CHOICES,
        default='NI',
        verbose_name='Género'
    )
    nacionalidad = models.CharField(max_length=50, default='Chilena', verbose_name='Nacionalidad')
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        default='NI',
        verbose_name='Estado civil'
    )
    ocupacion = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ocupación')

    # Contacto
    email = models.EmailField(blank=True, null=True, verbose_name='Correo electrónico')
    telefono = models.CharField(
        'Teléfono', 
        max_length=20, 
        blank=True,
        validators=[validar_telefono_chileno],
        help_text='Formato: +56 9 1234 5678'
    )
    
    # Dirección
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dirección')
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comuna')
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        blank=True,
        null=True,
        verbose_name='Región'
    )

    # Vulnerabilidad
    es_vulnerable = models.BooleanField(default=False, verbose_name='¿Es vulnerable?')
    vulnerabilidad = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción de vulnerabilidad',
        help_text='Describir situación de vulnerabilidad si aplica'
    )

    # Representación legal
    requiere_representante = models.BooleanField(
        default=False,
        verbose_name='¿Requiere representante?',
        help_text='Marcar si es menor de edad o tiene incapacidad'
    )
    representante_nombre = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del representante'
    )
    representante_run = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name='RUN del representante'
    )
    representante_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono del representante'
    )

    # Administrativos
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        indexes = [
            models.Index(fields=['run'], name='persona_run_idx'),
            models.Index(fields=['nombres', 'apellidos'], name='persona_nombre_idx'),
            models.Index(fields=['email'], name='persona_email_idx'),
            models.Index(fields=['tipo_persona'], name='persona_tipo_idx'),
            models.Index(fields=['activo'], name='persona_activo_idx'),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.run})"

    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def edad(self):
        if self.fecha_nacimiento:
            from datetime import date
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

class Consentimiento(models.Model):
    TIPO_CHOICES = [
        ('DATOS_PERSONALES', 'Tratamiento de datos personales'),
        ('NOTIFICACIONES', 'Recibir notificaciones'),
        ('COMPARTIR_INFO', 'Compartir información con terceros'),
        ('USO_ACADEMICO', 'Uso del caso con fines académicos'),
        ('GRABACION', 'Grabación de entrevistas'),
        ('OTRO', 'Otro'),
    ]

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='consentimientos',
        verbose_name='Persona'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de consentimiento'
    )
    otorgado = models.BooleanField(
        default=False,
        verbose_name='¿Consentimiento otorgado?'
    )
    fecha_otorgamiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de otorgamiento'
    )
    fecha_revocacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de revocación'
    )
    documento_respaldo = models.FileField(
        upload_to='consentimientos/',
        blank=True,
        null=True,
        verbose_name='Documento de respaldo',
        help_text='Consentimiento firmado escaneado'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Registrado por'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Consentimiento'
        verbose_name_plural = 'Consentimientos'
        unique_together = ['persona', 'tipo']

    def __str__(self):
        estado = "Otorgado" if self.otorgado else "No otorgado"
        return f"{self.get_tipo_display()} - {self.persona} ({estado})"

    def esta_vigente(self):
        """Retorna True si el consentimiento está otorgado y no ha sido revocado."""
        return self.otorgado and self.fecha_revocacion is None
    
class Causa(models.Model):
    rit = models.CharField(
        'RIT', 
        max_length=20, 
        blank=True,
        validators=[validar_rit],
        help_text='Formato: C-1234-2024'
    )
    ruc = models.CharField(
        'RUC', 
        max_length=20, 
        blank=True,
        validators=[validar_ruc],
        help_text='Formato: 2400123456-7'
    )
    tribunal = models.ForeignKey(
        Tribunal,
        on_delete=models.PROTECT,
        related_name='causas',
        verbose_name='Tribunal'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        related_name='causas',
        verbose_name='Materia'
    )
    caratula = models.CharField(max_length=200, verbose_name='Carátula')
    descripcion = models.TextField(
        'Descripción del caso',
        blank=True,
        help_text='Antecedentes y contexto del caso'
    )
    observaciones = models.TextField(
        'Observaciones internas',
        blank=True,
        help_text='Notas internas para el equipo de la clínica jurídica'
    )
    estado = models.ForeignKey(
        EstadoCausa,
        on_delete=models.PROTECT,
        related_name='causas',
        verbose_name='Estado'
    )
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de creación')
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='causas',
        verbose_name='Responsable'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Causa'
        verbose_name_plural = 'Causas'
        indexes = [
            models.Index(fields=['rit'], name='causa_rit_idx'),
            models.Index(fields=['ruc'], name='causa_ruc_idx'),
            models.Index(fields=['caratula'], name='causa_caratula_idx'),
            models.Index(fields=['estado'], name='causa_estado_idx'),
            models.Index(fields=['tribunal'], name='causa_tribunal_idx'),
            models.Index(fields=['materia'], name='causa_materia_idx'),
            models.Index(fields=['responsable'], name='causa_responsable_idx'),
            models.Index(fields=['fecha_creacion'], name='causa_fecha_idx'),
            models.Index(fields=['-fecha_creacion'], name='causa_fecha_desc_idx'),
        ]

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
    TIPO_EVENTO_CHOICES = [
        ('AUDIENCIA_JUDICIAL', 'Audiencia judicial'),
        ('ENTREVISTA_CLIENTE', 'Entrevista con cliente'),
        ('REUNION_EQUIPO', 'Reunión de equipo'),
        ('REUNION_SUPERVISOR', 'Reunión con supervisor'),
        ('COMPARENDO', 'Comparendo'),
        ('MEDIACION', 'Mediación'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
        ('SUSPENDIDA', 'Suspendida'),
        ('REPROGRAMADA', 'Reprogramada'),
        ('CANCELADA', 'Cancelada'),
    ]

    # Relaciones
    causa = models.ForeignKey(
        Causa,
        on_delete=models.CASCADE,
        related_name='audiencias',
        verbose_name='Causa'
    )
    audiencia_anterior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reprogramaciones',
        verbose_name='Audiencia anterior',
        help_text='Si es reprogramación, indicar la audiencia original'
    )

    # Información del evento
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        default='AUDIENCIA_JUDICIAL',
        verbose_name='Tipo de evento'
    )
    fecha_hora = models.DateTimeField(verbose_name='Fecha y hora')
    duracion_estimada = models.PositiveIntegerField(
        default=60,
        verbose_name='Duración estimada (minutos)'
    )
    lugar = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Lugar'
    )
    sala = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Sala',
        help_text='Número de sala si aplica'
    )

    # Estado y control
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PROGRAMADA',
        verbose_name='Estado'
    )
    motivo_suspension = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de suspensión/reprogramación'
    )

    # Asistencia
    asistio_cliente = models.BooleanField(
        default=False,
        verbose_name='¿Asistió el cliente?'
    )
    asistio_estudiante = models.BooleanField(
        default=False,
        verbose_name='¿Asistió el estudiante?'
    )
    asistio_supervisor = models.BooleanField(
        default=False,
        verbose_name='¿Asistió el supervisor?'
    )

    # Resultado
    resultado = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resultado',
        help_text='Descripción de lo ocurrido en la audiencia'
    )

    # Recordatorios
    recordatorio_enviado = models.BooleanField(
        default=False,
        verbose_name='Recordatorio enviado'
    )
    fecha_recordatorio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de envío de recordatorio'
    )

    # Notas
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audiencias_creadas',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Audiencia'
        verbose_name_plural = 'Audiencias'
        indexes = [
            models.Index(fields=['causa'], name='audiencia_causa_idx'),
            models.Index(fields=['fecha_hora'], name='audiencia_fecha_idx'),
            models.Index(fields=['-fecha_hora'], name='audiencia_fecha_desc_idx'),
            models.Index(fields=['estado'], name='audiencia_estado_idx'),
            models.Index(fields=['tipo_evento'], name='audiencia_tipo_idx'),
            models.Index(fields=['fecha_hora', 'estado'], name='audiencia_fecha_estado_idx'),
        ]

    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} ({self.causa})"

    def esta_pendiente(self):
        """Retorna True si la audiencia está pendiente de realizar."""
        from django.utils import timezone
        return self.estado in ['PROGRAMADA', 'CONFIRMADA'] and self.fecha_hora > timezone.now()

    def fue_reprogramada(self):
        """Retorna True si esta audiencia tiene reprogramaciones."""
        return self.reprogramaciones.exists()

class Documento(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('FINAL', 'Final'),
        ('ANULADO', 'Anulado'),
    ]

    # Relaciones
    causa = models.ForeignKey(
        Causa,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Causa'
    )
    tipo = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name='documentos',
        verbose_name='Tipo de documento'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Subido por'
    )

    # Información del documento
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    archivo = models.FileField(upload_to='documentos/%Y/%m/', verbose_name='Archivo')
    
    # Metadatos judiciales
    folio = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Folio',
        help_text='Número de folio en el expediente'
    )
    fecha_emision = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de emisión',
        help_text='Fecha del documento (ej: fecha de la resolución)'
    )
    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de documento',
        help_text='Número de oficio, resolución, rol, etc.'
    )
    emisor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Emisor',
        help_text='Tribunal, institución o persona que emite el documento'
    )

    # Versionado
    version = models.PositiveIntegerField(
        default=1,
        verbose_name='Versión'
    )
    documento_padre = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versiones',
        verbose_name='Documento original',
        help_text='Si es una nueva versión, indicar el documento original'
    )

    # Control
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='FINAL',
        verbose_name='Estado'
    )
    es_confidencial = models.BooleanField(
        default=False,
        verbose_name='¿Es confidencial?',
        help_text='Marcar si contiene información sensible'
    )
    
    # Auditoría
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última modificación')

    class Meta:
        ordering = ['-fecha_subida']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['causa'], name='documento_causa_idx'),
            models.Index(fields=['tipo'], name='documento_tipo_idx'),
            models.Index(fields=['usuario'], name='documento_usuario_idx'),
            models.Index(fields=['titulo'], name='documento_titulo_idx'),
            models.Index(fields=['fecha_subida'], name='documento_fecha_idx'),
            models.Index(fields=['-fecha_subida'], name='documento_fecha_desc_idx'),
            models.Index(fields=['estado'], name='documento_estado_idx'),
        ]

    def __str__(self):
        return f"{self.titulo} (v{self.version})"

    def extension(self):
        """Retorna la extensión del archivo."""
        if self.archivo:
            import os
            return os.path.splitext(self.archivo.name)[1].lower()
        return None

    def es_pdf(self):
        return self.extension() == '.pdf'

    def es_imagen(self):
        return self.extension() in ['.jpg', '.jpeg', '.png', '.gif']
    
class LogAuditoria(models.Model):
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
        ('VER', 'Ver'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('SUBIR_DOC', 'Subir documento'),
        ('DESCARGAR_DOC', 'Descargar documento'),
        ('CAMBIO_ESTADO', 'Cambio de estado'),
        ('ASIGNAR', 'Asignar responsable'),
        ('OTRO', 'Otro'),
    ]

    MODELO_CHOICES = [
        ('CAUSA', 'Causa'),
        ('PERSONA', 'Persona'),
        ('DOCUMENTO', 'Documento'),
        ('AUDIENCIA', 'Audiencia'),
        ('CONSENTIMIENTO', 'Consentimiento'),
        ('USUARIO', 'Usuario'),
        ('OTRO', 'Otro'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name='Usuario'
    )
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción'
    )
    modelo = models.CharField(
        max_length=20,
        choices=MODELO_CHOICES,
        verbose_name='Modelo afectado'
    )
    objeto_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='ID del objeto'
    )
    objeto_repr = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Representación del objeto'
    )
    datos_anteriores = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos anteriores',
        help_text='Estado del objeto antes del cambio'
    )
    datos_nuevos = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos nuevos',
        help_text='Estado del objeto después del cambio'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Dirección IP'
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora'
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        indexes = [
            models.Index(fields=['usuario'], name='log_usuario_idx'),
            models.Index(fields=['accion'], name='log_accion_idx'),
            models.Index(fields=['modelo'], name='log_modelo_idx'),
            models.Index(fields=['fecha'], name='log_fecha_idx'),
            models.Index(fields=['-fecha'], name='log_fecha_desc_idx'),
            models.Index(fields=['objeto_id'], name='log_objeto_idx'),
            models.Index(fields=['modelo', 'objeto_id'], name='log_modelo_objeto_idx'),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.get_accion_display()} {self.modelo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"  
    
