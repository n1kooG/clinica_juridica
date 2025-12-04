from django.contrib import admin
from .models import Persona, Causa, CausaPersona, Audiencia, Documento

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('run', 'nombres', 'apellidos', 'email', 'telefono')
    search_fields = ('run', 'nombres', 'apellidos')

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
    list_display = ('causa', 'tipo', 'fecha_hora', 'lugar')
    list_filter = ('tipo',)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'causa', 'usuario', 'fecha_subida')
    search_fields = ('titulo', 'tipo')
