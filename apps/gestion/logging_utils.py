"""
Utilidades de logging para el Sistema Clínica Jurídica
Cumple con ISO/IEC 27001 - Trazabilidad y Auditoría
"""

import logging
from functools import wraps

# Loggers
logger_seguridad = logging.getLogger('seguridad')
logger_auditoria = logging.getLogger('auditoria')
logger_app = logging.getLogger('apps')


def log_seguridad(mensaje, nivel='INFO', **kwargs):
    """
    Registra un evento de seguridad.
    """
    extra = {
        'ip': kwargs.get('ip', 'N/A'),
        'user': kwargs.get('user', 'N/A'),
    }
    
    if nivel == 'WARNING':
        logger_seguridad.warning(mensaje, extra=extra)
    elif nivel == 'ERROR':
        logger_seguridad.error(mensaje, extra=extra)
    elif nivel == 'CRITICAL':
        logger_seguridad.critical(mensaje, extra=extra)
    else:
        logger_seguridad.info(mensaje, extra=extra)


def log_auditoria(usuario, accion, modelo, objeto_id=None, descripcion=''):
    """
    Registra un evento de auditoría.
    """
    mensaje = f"Usuario: {usuario} | Acción: {accion} | Modelo: {modelo}"
    
    if objeto_id:
        mensaje += f" | ID: {objeto_id}"
    
    if descripcion:
        mensaje += f" | {descripcion}"
    
    logger_auditoria.info(mensaje)


def log_error(mensaje, exception=None, **kwargs):
    """
    Registra un error de la aplicación.
    """
    if exception:
        logger_app.exception(f"{mensaje}: {str(exception)}")
    else:
        logger_app.error(mensaje)


def log_view_access(view_name):
    """
    Decorador para loggear acceso a vistas sensibles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user.username if request.user.is_authenticated else 'Anónimo'
            ip = get_client_ip(request)
            
            log_seguridad(
                f"Acceso a vista: {view_name}",
                ip=ip,
                user=user
            )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_client_ip(request):
    """Obtiene la IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')