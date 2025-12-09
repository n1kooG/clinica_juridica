from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


# =============================================================================
# DEFINICIÓN DE PERMISOS POR ROL
# =============================================================================

PERMISOS_POR_ROL = {
    'ADMIN': {
        'puede_ver_todo': True,
        'puede_crear_usuario': True,
        'puede_editar_usuario': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_asignar_causa': True,
        'puede_subir_documento': True,
        'puede_ver_documento_sensible': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_ver_reportes': True,
        'puede_ver_auditoria': True,
    },
    'DIRECTOR': {
        'puede_ver_todo': True,
        'puede_crear_usuario': False,
        'puede_editar_usuario': False,
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_asignar_causa': True,
        'puede_subir_documento': False,
        'puede_ver_documento_sensible': True,
        'puede_crear_audiencia': False,
        'puede_editar_audiencia': False,
        'puede_ver_reportes': True,
        'puede_ver_auditoria': True,
    },
    'SUPERVISOR': {
        'puede_ver_todo': False,
        'puede_crear_usuario': False,
        'puede_editar_usuario': False,
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_asignar_causa': False,
        'puede_subir_documento': True,
        'puede_ver_documento_sensible': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_ver_reportes': True,
        'puede_ver_auditoria': False,
    },
    'ESTUDIANTE': {
        'puede_ver_todo': False,
        'puede_crear_usuario': False,
        'puede_editar_usuario': False,
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_crear_causa': False,
        'puede_editar_causa': True,  # Solo las asignadas
        'puede_asignar_causa': False,
        'puede_subir_documento': True,
        'puede_ver_documento_sensible': False,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_ver_reportes': False,
        'puede_ver_auditoria': False,
    },
    'SECRETARIA': {
        'puede_ver_todo': False,
        'puede_crear_usuario': False,
        'puede_editar_usuario': False,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_asignar_causa': False,
        'puede_subir_documento': True,
        'puede_ver_documento_sensible': False,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_ver_reportes': False,
        'puede_ver_auditoria': False,
    },
    'EXTERNO': {
        'puede_ver_todo': False,
        'puede_crear_usuario': False,
        'puede_editar_usuario': False,
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_asignar_causa': False,
        'puede_subir_documento': False,
        'puede_ver_documento_sensible': False,
        'puede_crear_audiencia': False,
        'puede_editar_audiencia': False,
        'puede_ver_reportes': False,
        'puede_ver_auditoria': False,
    },
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def obtener_rol_usuario(user):
    """Obtiene el rol del usuario desde su perfil."""
    if not user.is_authenticated:
        return None
    if hasattr(user, 'perfil'):
        return user.perfil.rol
    return None


def usuario_tiene_permiso(user, permiso):
    """Verifica si el usuario tiene un permiso específico."""
    if not user.is_authenticated:
        return False
    
    # Superusuario tiene todos los permisos
    if user.is_superuser:
        return True
    
    rol = obtener_rol_usuario(user)
    if not rol:
        return False
    
    permisos_rol = PERMISOS_POR_ROL.get(rol, {})
    return permisos_rol.get(permiso, False)


def usuario_es_rol(user, roles):
    """Verifica si el usuario tiene uno de los roles especificados."""
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    rol = obtener_rol_usuario(user)
    if isinstance(roles, str):
        roles = [roles]
    
    return rol in roles


# =============================================================================
# DECORADORES PARA VISTAS
# =============================================================================

def permiso_requerido(permiso):
    """
    Decorador que verifica si el usuario tiene un permiso específico.
    
    Uso:
        @permiso_requerido('puede_crear_causa')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not usuario_tiene_permiso(request.user, permiso):
                raise PermissionDenied("No tienes permiso para realizar esta acción.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def rol_requerido(*roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles especificados.
    
    Uso:
        @rol_requerido('ADMIN', 'DIRECTOR')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not usuario_es_rol(request.user, roles):
                raise PermissionDenied("No tienes el rol necesario para acceder.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# MIXINS PARA VISTAS BASADAS EN CLASES
# =============================================================================

class PermisoRequeridoMixin:
    """
    Mixin para vistas basadas en clases que requieren un permiso.
    
    Uso:
        class MiVista(PermisoRequeridoMixin, View):
            permiso_requerido = 'puede_crear_causa'
    """
    permiso_requerido = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if self.permiso_requerido and not usuario_tiene_permiso(request.user, self.permiso_requerido):
            raise PermissionDenied("No tienes permiso para realizar esta acción.")
        
        return super().dispatch(request, *args, **kwargs)


class RolRequeridoMixin:
    """
    Mixin para vistas basadas en clases que requieren un rol específico.
    
    Uso:
        class MiVista(RolRequeridoMixin, View):
            roles_permitidos = ['ADMIN', 'DIRECTOR']
    """
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if self.roles_permitidos and not usuario_es_rol(request.user, self.roles_permitidos):
            raise PermissionDenied("No tienes el rol necesario para acceder.")
        
        return super().dispatch(request, *args, **kwargs)