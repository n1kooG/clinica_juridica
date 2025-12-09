from django.contrib import admin
from .models import Persona, Causa, CausaPersona, Audiencia, Documento, Tribunal, Materia, TipoDocumento, EstadoCausa, Consentimiento, LogAuditoria

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['run', 'nombres', 'apellidos', 'tipo_persona', 'telefono', 'es_vulnerable', 'activo']
    list_filter = ['tipo_persona', 'es_vulnerable', 'activo', 'region']
    search_fields = ['run', 'nombres', 'apellidos', 'email', 'telefono']
    ordering = ['apellidos', 'nombres']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('run', 'nombres', 'apellidos', 'tipo_persona')
        }),
        ('Datos personales', {
            'fields': ('fecha_nacimiento', 'genero', 'nacionalidad', 'estado_civil', 'ocupacion')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion', 'comuna', 'region')
        }),
        ('Vulnerabilidad', {
            'fields': ('es_vulnerable', 'vulnerabilidad'),
            'classes': ('collapse',)
        }),
        ('Representante legal', {
            'fields': ('requiere_representante', 'representante_nombre', 'representante_run', 'representante_telefono'),
            'classes': ('collapse',)
        }),
        ('Otros', {
            'fields': ('observaciones', 'activo'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Causa)
class CausaAdmin(admin.ModelAdmin):
    list_display = ('caratula', 'tribunal', 'rit', 'ruc', 'estado', 'fecha_creacion', 'responsable')
    search_fields = ('caratula', 'rit', 'ruc')
    list_filter = ('estado', 'tribunal')

@admin.register(CausaPersona)
class CausaPersonaAdmin(admin.ModelAdmin):
    list_display = ('causa', 'persona', 'rol_en_causa')
    search_fields = ('causa__caratula', 'persona__nombres', 'persona__apellidos', 'rol_en_causa')

@admin.register(Audiencia)
class AudienciaAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'tipo_evento', 'causa', 'estado', 'lugar', 'asistio_cliente', 'asistio_estudiante']
    list_filter = ['tipo_evento', 'estado', 'fecha_hora', 'asistio_cliente']
    search_fields = ['causa__caratula', 'lugar', 'observaciones']
    ordering = ['-fecha_hora']
    date_hierarchy = 'fecha_hora'
    
    fieldsets = (
        ('Información del evento', {
            'fields': ('causa', 'tipo_evento', 'fecha_hora', 'duracion_estimada', 'lugar', 'sala')
        }),
        ('Estado', {
            'fields': ('estado', 'motivo_suspension', 'audiencia_anterior')
        }),
        ('Asistencia', {
            'fields': ('asistio_cliente', 'asistio_estudiante', 'asistio_supervisor'),
            'classes': ('collapse',)
        }),
        ('Resultado', {
            'fields': ('resultado', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Recordatorios', {
            'fields': ('recordatorio_enviado', 'fecha_recordatorio'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'causa', 'folio', 'fecha_emision', 'version', 'estado', 'es_confidencial', 'fecha_subida']
    list_filter = ['tipo', 'estado', 'es_confidencial', 'fecha_subida']
    search_fields = ['titulo', 'descripcion', 'numero_documento', 'causa__caratula']
    ordering = ['-fecha_subida']
    date_hierarchy = 'fecha_subida'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('causa', 'tipo', 'titulo', 'descripcion', 'archivo')
        }),
        ('Metadatos judiciales', {
            'fields': ('folio', 'fecha_emision', 'numero_documento', 'emisor'),
            'classes': ('collapse',)
        }),
        ('Versionado', {
            'fields': ('version', 'documento_padre'),
            'classes': ('collapse',)
        }),
        ('Control', {
            'fields': ('estado', 'es_confidencial', 'usuario'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Tribunal)
class TribunalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'ciudad', 'region', 'activo']
    list_filter = ['tipo', 'region', 'activo']
    search_fields = ['nombre', 'ciudad', 'comuna']
    ordering = ['region', 'ciudad', 'nombre']
    
@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_tribunal', 'activo']
    list_filter = ['tipo_tribunal', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['tipo_tribunal', 'nombre']
    
@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'requiere_folio', 'requiere_fecha_emision', 'activo']
    list_filter = ['categoria', 'activo', 'requiere_folio']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']
    
@admin.register(EstadoCausa)
class EstadoCausaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'color', 'es_final', 'activo']
    list_filter = ['es_final', 'activo', 'color']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden']
    list_editable = ['orden', 'color', 'es_final']
    
@admin.register(Consentimiento)
class ConsentimientoAdmin(admin.ModelAdmin):
    list_display = ['persona', 'tipo', 'otorgado', 'fecha_otorgamiento', 'fecha_revocacion', 'esta_vigente']
    list_filter = ['tipo', 'otorgado']
    search_fields = ['persona__nombres', 'persona__apellidos', 'persona__run']
    ordering = ['-fecha_registro']
    
    def esta_vigente(self, obj):
        return obj.esta_vigente()
    esta_vigente.boolean = True
    esta_vigente.short_description = '¿Vigente?'

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'usuario', 'accion', 'modelo', 'objeto_repr', 'ip_address']
    list_filter = ['accion', 'modelo', 'fecha', 'usuario']
    search_fields = ['usuario__username', 'objeto_repr', 'descripcion']
    ordering = ['-fecha']
    date_hierarchy = 'fecha'
    readonly_fields = [
        'usuario', 'accion', 'modelo', 'objeto_id', 'objeto_repr',
        'datos_anteriores', 'datos_nuevos', 'ip_address', 'user_agent',
        'descripcion', 'fecha'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
