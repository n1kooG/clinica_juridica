"""
Utilidades de caché para optimización de rendimiento
Cumple con ISO/IEC 25010 - Eficiencia de Desempeño
"""

from django.core.cache import cache
from django.conf import settings
from .models import (
    Tribunal, Materia, EstadoCausa, TipoDocumento
)
from django.contrib.auth.models import User


# Claves de caché
CACHE_KEY_TRIBUNALES = 'catalogos:tribunales:activos'
CACHE_KEY_MATERIAS = 'catalogos:materias:activos'
CACHE_KEY_ESTADOS = 'catalogos:estados:activos'
CACHE_KEY_TIPOS_DOC = 'catalogos:tipos_documento:activos'
CACHE_KEY_RESPONSABLES = 'catalogos:responsables:activos'


def get_tribunales_activos():
    """Obtiene tribunales activos desde caché."""
    tribunales = cache.get(CACHE_KEY_TRIBUNALES)
    
    if tribunales is None:
        tribunales = list(
            Tribunal.objects.filter(activo=True).order_by('nombre').values(
                'id', 'nombre', 'ciudad', 'tipo'
            )
        )
        cache.set(
            CACHE_KEY_TRIBUNALES, 
            tribunales, 
            settings.CACHE_CATALOGOS_TIMEOUT
        )
    
    return tribunales


def get_materias_activas():
    """Obtiene materias activas desde caché."""
    materias = cache.get(CACHE_KEY_MATERIAS)
    
    if materias is None:
        materias = list(
            Materia.objects.filter(activo=True).order_by('nombre').values(
                'id', 'nombre', 'tipo_tribunal'
            )
        )
        cache.set(
            CACHE_KEY_MATERIAS, 
            materias, 
            settings.CACHE_CATALOGOS_TIMEOUT
        )
    
    return materias


def get_estados_activos():
    """Obtiene estados activos desde caché."""
    estados = cache.get(CACHE_KEY_ESTADOS)
    
    if estados is None:
        estados = list(
            EstadoCausa.objects.filter(activo=True).order_by('orden').values(
                'id', 'nombre', 'color', 'orden', 'es_final'
            )
        )
        cache.set(
            CACHE_KEY_ESTADOS, 
            estados, 
            settings.CACHE_CATALOGOS_TIMEOUT
        )
    
    return estados


def get_tipos_documento_activos():
    """Obtiene tipos de documento activos desde caché."""
    tipos = cache.get(CACHE_KEY_TIPOS_DOC)
    
    if tipos is None:
        tipos = list(
            TipoDocumento.objects.filter(activo=True).order_by('nombre').values(
                'id', 'nombre', 'categoria'
            )
        )
        cache.set(
            CACHE_KEY_TIPOS_DOC, 
            tipos, 
            settings.CACHE_CATALOGOS_TIMEOUT
        )
    
    return tipos


def get_responsables_activos():
    """Obtiene usuarios activos desde caché."""
    responsables = cache.get(CACHE_KEY_RESPONSABLES)
    
    if responsables is None:
        responsables = list(
            User.objects.filter(is_active=True).order_by('first_name', 'username').values(
                'id', 'username', 'first_name', 'last_name', 'email'
            )
        )
        cache.set(
            CACHE_KEY_RESPONSABLES, 
            responsables, 
            settings.CACHE_CATALOGOS_TIMEOUT
        )
    
    return responsables


def invalidar_cache_tribunales():
    """Invalida el caché de tribunales."""
    cache.delete(CACHE_KEY_TRIBUNALES)


def invalidar_cache_materias():
    """Invalida el caché de materias."""
    cache.delete(CACHE_KEY_MATERIAS)


def invalidar_cache_estados():
    """Invalida el caché de estados."""
    cache.delete(CACHE_KEY_ESTADOS)


def invalidar_cache_tipos_documento():
    """Invalida el caché de tipos de documento."""
    cache.delete(CACHE_KEY_TIPOS_DOC)


def invalidar_cache_responsables():
    """Invalida el caché de responsables."""
    cache.delete(CACHE_KEY_RESPONSABLES)


def invalidar_todos_catalogos():
    """Invalida todos los cachés de catálogos."""
    invalidar_cache_tribunales()
    invalidar_cache_materias()
    invalidar_cache_estados()
    invalidar_cache_tipos_documento()
    invalidar_cache_responsables()