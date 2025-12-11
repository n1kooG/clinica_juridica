"""
Decoradores para control de permisos y accesos
ISO/IEC 27001 - A.9.2.3 Gestión de derechos de acceso
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .permissions import tiene_permiso
from .models import LogAuditoria
import logging

logger = logging.getLogger('seguridad')


def permiso_requerido(permiso):
    """
    Decorador para verificar permisos antes de ejecutar una vista.
    
    Uso:
        @permiso_requerido('puede_crear_causa')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Verificar si el usuario tiene el permiso
            if not tiene_permiso(request.user, permiso):
                # Registrar intento de acceso denegado
                logger.warning(
                    f"Acceso denegado - "
                    f"Usuario: {request.user.username}, "
                    f"Permiso requerido: {permiso}, "
                    f"Rol: {request.user.perfil.rol if hasattr(request.user, 'perfil') else 'Sin rol'}, "
                    f"Vista: {view_func.__name__}"
                )
                
                # Registrar en auditoría
                try:
                    LogAuditoria.objects.create(
                        usuario=request.user,
                        accion='ACCESO_DENEGADO',
                        modelo='PERMISO',
                        descripcion=f'Intento de acceso sin permiso: {permiso} en {view_func.__name__}'
                    )
                except:
                    pass
                
                messages.error(
                    request,
                    'No tienes permisos para realizar esta acción.'
                )
                return redirect('gestion:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def permiso_requerido_ajax(permiso):
    """
    Decorador para verificar permisos en vistas AJAX.
    Retorna JSON en vez de redireccionar.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not tiene_permiso(request.user, permiso):
                logger.warning(
                    f"Acceso AJAX denegado - "
                    f"Usuario: {request.user.username}, "
                    f"Permiso: {permiso}"
                )
                
                return JsonResponse({
                    'error': True,
                    'mensaje': 'No tienes permisos para realizar esta acción.'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def solo_roles_permitidos(*roles_permitidos):
    """
    Decorador para restringir acceso solo a ciertos roles.
    
    Uso:
        @solo_roles_permitidos('ADMIN', 'DIRECTOR')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Superusuarios siempre pueden acceder
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar rol
            if not hasattr(request.user, 'perfil') or not request.user.perfil:
                messages.error(request, 'No tienes un rol asignado.')
                return redirect('gestion:dashboard')
            
            if request.user.perfil.rol not in roles_permitidos:
                logger.warning(
                    f"Acceso denegado por rol - "
                    f"Usuario: {request.user.username}, "
                    f"Rol: {request.user.perfil.rol}, "
                    f"Roles permitidos: {roles_permitidos}"
                )
                
                messages.error(
                    request,
                    'No tienes permisos para acceder a esta sección.'
                )
                return redirect('gestion:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator