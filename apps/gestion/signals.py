from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from .cache_utils import (
    invalidar_cache_tribunales,
    invalidar_cache_materias,
    invalidar_cache_estados,
    invalidar_cache_tipos_documento,
)

from .models import Causa, Persona, Documento, Audiencia, Consentimiento, LogAuditoria, Tribunal, Materia, EstadoCausa, TipoDocumento


# =============================================================================
# UTILIDADES
# =============================================================================

def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    if request is None:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtiene el User Agent desde el request."""
    if request is None:
        return None
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def objeto_a_dict(obj, campos_excluidos=None):
    """Convierte un objeto de modelo a diccionario para guardar en JSON."""
    if obj is None:
        return None
    
    campos_excluidos = campos_excluidos or ['_state']
    datos = {}
    
    for field in obj._meta.fields:
        nombre = field.name
        if nombre in campos_excluidos:
            continue
        
        valor = getattr(obj, nombre, None)
        
        # Convertir tipos no serializables
        if hasattr(valor, 'isoformat'):  # datetime, date
            valor = valor.isoformat()
        elif hasattr(valor, 'pk'):  # ForeignKey
            valor = str(valor)
        elif hasattr(valor, 'url'):  # FileField
            # Verificar si el archivo realmente existe antes de acceder a url
            try:
                if valor and valor.name:
                    valor = valor.url
                else:
                    valor = None
            except (ValueError, AttributeError):
                valor = None
        
        datos[nombre] = valor
    
    return datos


# =============================================================================
# VARIABLE THREAD-LOCAL PARA REQUEST
# =============================================================================

import threading
_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


class AuditoriaMiddleware:
    """Middleware para capturar el request actual."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response


# =============================================================================
# FUNCIÓN PARA REGISTRAR LOG
# =============================================================================

def registrar_log(accion, modelo, objeto=None, objeto_id=None, objeto_repr=None,
                  datos_anteriores=None, datos_nuevos=None, descripcion=None):
    """Función central para registrar logs de auditoría."""
    
    request = get_current_request()
    usuario = get_current_user()
    
    if objeto:
        objeto_id = objeto.pk
        objeto_repr = str(objeto)[:200]
    
    LogAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        objeto_repr=objeto_repr,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        descripcion=descripcion
    )


# =============================================================================
# ALMACÉN TEMPORAL PARA DATOS ANTERIORES
# =============================================================================

_pre_save_data = {}


# =============================================================================
# SIGNALS PARA CAUSA
# =============================================================================

@receiver(pre_save, sender=Causa)
def causa_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Causa.objects.get(pk=instance.pk)
            _pre_save_data[f'causa_{instance.pk}'] = objeto_a_dict(original)
        except Causa.DoesNotExist:
            pass


@receiver(post_save, sender=Causa)
def causa_post_save(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            accion='CREAR',
            modelo='CAUSA',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Causa creada: {instance.caratula}'
        )
    else:
        key = f'causa_{instance.pk}'
        datos_anteriores = _pre_save_data.pop(key, None)
        registrar_log(
            accion='EDITAR',
            modelo='CAUSA',
            objeto=instance,
            datos_anteriores=datos_anteriores,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Causa editada: {instance.caratula}'
        )


@receiver(post_delete, sender=Causa)
def causa_post_delete(sender, instance, **kwargs):
    registrar_log(
        accion='ELIMINAR',
        modelo='CAUSA',
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        datos_anteriores=objeto_a_dict(instance),
        descripcion=f'Causa eliminada: {instance.caratula}'
    )


# =============================================================================
# SIGNALS PARA PERSONA
# =============================================================================

@receiver(pre_save, sender=Persona)
def persona_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Persona.objects.get(pk=instance.pk)
            _pre_save_data[f'persona_{instance.pk}'] = objeto_a_dict(original)
        except Persona.DoesNotExist:
            pass


@receiver(post_save, sender=Persona)
def persona_post_save(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            accion='CREAR',
            modelo='PERSONA',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Persona creada: {instance.nombre_completo()}'
        )
    else:
        key = f'persona_{instance.pk}'
        datos_anteriores = _pre_save_data.pop(key, None)
        registrar_log(
            accion='EDITAR',
            modelo='PERSONA',
            objeto=instance,
            datos_anteriores=datos_anteriores,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Persona editada: {instance.nombre_completo()}'
        )


@receiver(post_delete, sender=Persona)
def persona_post_delete(sender, instance, **kwargs):
    registrar_log(
        accion='ELIMINAR',
        modelo='PERSONA',
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        datos_anteriores=objeto_a_dict(instance),
        descripcion=f'Persona eliminada: {instance.nombre_completo()}'
    )


# =============================================================================
# SIGNALS PARA DOCUMENTO
# =============================================================================

@receiver(post_save, sender=Documento)
def documento_post_save(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            accion='SUBIR_DOC',
            modelo='DOCUMENTO',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Documento subido: {instance.titulo}'
        )
    else:
        registrar_log(
            accion='EDITAR',
            modelo='DOCUMENTO',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Documento editado: {instance.titulo}'
        )


@receiver(post_delete, sender=Documento)
def documento_post_delete(sender, instance, **kwargs):
    registrar_log(
        accion='ELIMINAR',
        modelo='DOCUMENTO',
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        descripcion=f'Documento eliminado: {instance.titulo}'
    )


# =============================================================================
# SIGNALS PARA AUDIENCIA
# =============================================================================

@receiver(post_save, sender=Audiencia)
def audiencia_post_save(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            accion='CREAR',
            modelo='AUDIENCIA',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Audiencia creada: {instance}'
        )
    else:
        registrar_log(
            accion='EDITAR',
            modelo='AUDIENCIA',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Audiencia editada: {instance}'
        )


# =============================================================================
# SIGNALS PARA CONSENTIMIENTO
# =============================================================================

@receiver(post_save, sender=Consentimiento)
def consentimiento_post_save(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            accion='CREAR',
            modelo='CONSENTIMIENTO',
            objeto=instance,
            datos_nuevos=objeto_a_dict(instance),
            descripcion=f'Consentimiento registrado: {instance}'
        )


# =============================================================================
# SIGNALS PARA LOGIN/LOGOUT
# =============================================================================

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LogAuditoria.objects.create(
        usuario=user,
        accion='LOGIN',
        modelo='USUARIO',
        objeto_id=user.pk,
        objeto_repr=str(user),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        descripcion=f'Inicio de sesión: {user.username}'
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        LogAuditoria.objects.create(
            usuario=user,
            accion='LOGOUT',
            modelo='USUARIO',
            objeto_id=user.pk,
            objeto_repr=str(user),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            descripcion=f'Cierre de sesión: {user.username}'
        )
        
# =============================================================================
# SIGNALS PARA INVALIDAR CACHÉ
# =============================================================================



@receiver(post_save, sender=Tribunal)
@receiver(post_delete, sender=Tribunal)
def invalidar_cache_tribunal_signal(sender, instance, **kwargs):
    """Invalida caché cuando se modifica un tribunal."""
    invalidar_cache_tribunales()


@receiver(post_save, sender=Materia)
@receiver(post_delete, sender=Materia)
def invalidar_cache_materia_signal(sender, instance, **kwargs):
    """Invalida caché cuando se modifica una materia."""
    invalidar_cache_materias()


@receiver(post_save, sender=EstadoCausa)
@receiver(post_delete, sender=EstadoCausa)
def invalidar_cache_estado_signal(sender, instance, **kwargs):
    """Invalida caché cuando se modifica un estado."""
    invalidar_cache_estados()


@receiver(post_save, sender=TipoDocumento)
@receiver(post_delete, sender=TipoDocumento)
def invalidar_cache_tipo_doc_signal(sender, instance, **kwargs):
    """Invalida caché cuando se modifica un tipo de documento."""
    invalidar_cache_tipos_documento()