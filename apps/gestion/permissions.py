"""
Sistema de Permisos Unificado - Clínica Jurídica USS
====================================================

Basado en la matriz de permisos del documento oficial:
- L = Lectura
- ✔ = Lectura/Escritura  
- L* = Solo lo que le compartan explícitamente
- — = Sin acceso

ISO/IEC 27001 - A.9.2.3 Gestión de derechos de acceso
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger('seguridad')


# =============================================================================
# DEFINICIÓN DE ROLES (según documento del profesor)
# =============================================================================

ROLES = {
    'ADMIN': 'Administrador',
    'DIRECTOR': 'Director/a Clínica',
    'SUPERVISOR': 'Abogado/a Supervisor/a',
    'ESTUDIANTE': 'Estudiante/Clínico',
    'SECRETARIA': 'Secretaría/Apoyo',
    'EXTERNO': 'Persona Atendida (externo)',
}


# =============================================================================
# MATRIZ DE PERMISOS (según documento del profesor)
# =============================================================================
"""
Tabla del profesor:
| Funcionalidad          | Admin | Director | Supervisor | Estudiante | Secretaría | Externo |
|------------------------|-------|----------|------------|------------|------------|---------|
| Crear/editar persona   |   ✔   |    L     |     L      |     L      |     ✔      |    —    |
| Crear/editar causa     |   ✔   |    L     |     ✔      |     L      |     —      |    —    |
| Subir documentos       |   ✔   |    L     |     ✔      |     ✔      |     ✔      |   L*    |
| Ver docs sensibles     |   ✔   |    L     |     ✔      |     L      |     L      |    —    |
| Agenda (crear/editar)  |   ✔   |    L     |     ✔      |     ✔      |     ✔      |    —    |
| Reportes globales      |   ✔   |    ✔     |     L      |     —      |     —      |    —    |
"""

PERMISOS_POR_ROL = {
    'ADMIN': {
        # === PERSONAS ===
        'puede_ver_personas': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_eliminar_persona': True,
        
        # === CAUSAS ===
        'puede_ver_causas': True,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_eliminar_causa': True,
        'puede_asignar_causa': True,
        'puede_reasignar_causa': True,
        
        # === DOCUMENTOS ===
        'puede_ver_documentos': True,
        'puede_subir_documento': True,
        'puede_editar_documento': True,
        'puede_eliminar_documento': True,
        'puede_ver_documentos_confidenciales': True,
        
        # === AUDIENCIAS/AGENDA ===
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': True,
        
        # === REPORTES ===
        'puede_ver_reportes': True,
        'puede_exportar_reportes': True,
        'puede_ver_reportes_globales': True,
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': True,
        'puede_exportar_auditoria': True,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': True,
        'puede_gestionar_catalogos': True,
        'puede_ver_panel_admin': True,
        'puede_configurar_sistema': True,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,
        'puede_gestionar_consentimientos': True,
    },
    
    'DIRECTOR': {
        # === PERSONAS ===
        'puede_ver_personas': True,
        'puede_crear_persona': False,  # Solo lectura
        'puede_editar_persona': False,
        'puede_eliminar_persona': False,
        
        # === CAUSAS ===
        'puede_ver_causas': True,
        'puede_crear_causa': False,  # Solo lectura
        'puede_editar_causa': False,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': True,  # Puede reasignar
        'puede_reasignar_causa': True,
        
        # === DOCUMENTOS ===
        'puede_ver_documentos': True,
        'puede_subir_documento': False,  # Solo lectura
        'puede_editar_documento': False,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': True,
        
        # === AUDIENCIAS/AGENDA ===
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': False,  # Solo lectura
        'puede_editar_audiencia': False,
        'puede_eliminar_audiencia': False,
        
        # === REPORTES ===
        'puede_ver_reportes': True,
        'puede_exportar_reportes': True,
        'puede_ver_reportes_globales': True,  # Tiene acceso completo a reportes
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': True,
        'puede_exportar_auditoria': True,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_panel_admin': True,  # Puede ver pero no modificar
        'puede_configurar_sistema': False,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,
        'puede_gestionar_consentimientos': False,
    },
    
    'SUPERVISOR': {
        # === PERSONAS ===
        'puede_ver_personas': True,
        'puede_crear_persona': False,  # Solo lectura
        'puede_editar_persona': False,
        'puede_eliminar_persona': False,
        
        # === CAUSAS ===
        'puede_ver_causas': True,
        'puede_crear_causa': True,  # ✔ Crear/editar casos asignados
        'puede_editar_causa': True,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        'puede_reasignar_causa': False,
        
        # === DOCUMENTOS ===
        'puede_ver_documentos': True,
        'puede_subir_documento': True,  # ✔ Aprobar documentos
        'puede_editar_documento': True,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': True,
        
        # === AUDIENCIAS/AGENDA ===
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,  # ✔
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': False,
        
        # === REPORTES ===
        'puede_ver_reportes': True,  # Solo lectura
        'puede_exportar_reportes': False,
        'puede_ver_reportes_globales': False,
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': False,
        'puede_exportar_auditoria': False,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_panel_admin': False,
        'puede_configurar_sistema': False,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,
        'puede_gestionar_consentimientos': True,
    },
    
    'ESTUDIANTE': {
        # === PERSONAS ===
        'puede_ver_personas': True,
        'puede_crear_persona': False,  # No crea personas
        'puede_editar_persona': False,
        'puede_eliminar_persona': False,
        
        # === CAUSAS ===
        # "Crear/editar dentro de su ámbito; sin acceso global"
        'puede_ver_causas': True,  # Solo casos asignados (filtrado en vista)
        'puede_crear_causa': True,  # ✔ Puede crear causas
        'puede_editar_causa': True,  # ✔ Puede editar (solo las asignadas - filtrado en vista)
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        'puede_reasignar_causa': False,
        
        # === DOCUMENTOS ===
        # "sube documentos"
        'puede_ver_documentos': True,
        'puede_subir_documento': True,  # ✔ Puede subir
        'puede_editar_documento': True,  # ✔ Puede editar sus documentos
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,
        
        # === AUDIENCIAS/AGENDA ===
        # "agenda entrevistas"
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,  # ✔ Puede agendar
        'puede_editar_audiencia': True,  # ✔ Puede editar
        'puede_eliminar_audiencia': False,
        
        # === REPORTES ===
        'puede_ver_reportes': False,  # Sin acceso global
        'puede_exportar_reportes': False,
        'puede_ver_reportes_globales': False,
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': False,
        'puede_exportar_auditoria': False,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_panel_admin': False,
        'puede_configurar_sistema': False,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,
        'puede_gestionar_consentimientos': False,
    },
    
    'SECRETARIA': {
        # === PERSONAS ===
        'puede_ver_personas': True,
        'puede_crear_persona': True,  # ✔ Gestiona recepción
        'puede_editar_persona': True,
        'puede_eliminar_persona': False,
        
        # === CAUSAS ===
        'puede_ver_causas': True,  # Solo lectura
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        'puede_reasignar_causa': False,
        
        # === DOCUMENTOS ===
        'puede_ver_documentos': True,
        'puede_subir_documento': True,  # ✔ Registra docs entrantes
        'puede_editar_documento': False,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,  # Solo lectura normal
        
        # === AUDIENCIAS/AGENDA ===
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,  # ✔ Gestiona agenda
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': False,
        
        # === REPORTES ===
        'puede_ver_reportes': False,
        'puede_exportar_reportes': False,
        'puede_ver_reportes_globales': False,
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': False,
        'puede_exportar_auditoria': False,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_panel_admin': False,
        'puede_configurar_sistema': False,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,
        'puede_gestionar_consentimientos': True,  # Puede registrar consentimientos
    },
    
    'EXTERNO': {
        # === PERSONAS ===
        'puede_ver_personas': False,  # Solo su propia info
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_eliminar_persona': False,
        
        # === CAUSAS ===
        'puede_ver_causas': False,  # Solo sus propias causas (portal)
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        'puede_reasignar_causa': False,
        
        # === DOCUMENTOS ===
        'puede_ver_documentos': False,  # Solo docs compartidos explícitamente (L*)
        'puede_subir_documento': False,  # Carga limitada en portal
        'puede_editar_documento': False,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,
        'puede_subir_documento_portal': True,  # Permiso especial para portal
        
        # === AUDIENCIAS/AGENDA ===
        'puede_ver_audiencias': False,  # Solo sus recordatorios
        'puede_crear_audiencia': False,
        'puede_editar_audiencia': False,
        'puede_eliminar_audiencia': False,
        
        # === REPORTES ===
        'puede_ver_reportes': False,
        'puede_exportar_reportes': False,
        'puede_ver_reportes_globales': False,
        
        # === AUDITORÍA ===
        'puede_ver_auditoria': False,
        'puede_exportar_auditoria': False,
        
        # === ADMINISTRACIÓN ===
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_panel_admin': False,
        'puede_configurar_sistema': False,
        
        # === CONSENTIMIENTOS ===
        'puede_ver_consentimientos': True,  # Puede ver sus propios consentimientos
        'puede_gestionar_consentimientos': False,
        
        # === PORTAL EXTERNO ===
        'puede_acceder_portal': True,
        'puede_ver_documentos_compartidos': True,
        'puede_ver_recordatorios': True,
    },
}


# =============================================================================
# FUNCIONES DE VERIFICACIÓN DE PERMISOS
# =============================================================================

# Mapeo de roles antiguos a nuevos (compatibilidad)
ROLES_ALIAS = {
    'ALUMNO': 'ESTUDIANTE',
    'ABOGADO': 'SUPERVISOR',
}

def obtener_rol_usuario(usuario):
    """
    Obtiene el rol del usuario desde su perfil.
    Incluye mapeo de roles antiguos para compatibilidad.
    
    Args:
        usuario: Instancia de User
    
    Returns:
        str: Rol del usuario o None
    """
    if not usuario.is_authenticated:
        return None
    
    if hasattr(usuario, 'perfil') and usuario.perfil:
        rol = usuario.perfil.rol
        # Mapear roles antiguos a nuevos
        return ROLES_ALIAS.get(rol, rol)
    
    return None


def tiene_permiso(usuario, permiso):
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        usuario: Instancia de User
        permiso: String con el nombre del permiso
    
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    # Usuarios no autenticados no tienen permisos
    if not usuario.is_authenticated:
        return False
    
    # Superusuarios tienen todos los permisos
    if usuario.is_superuser:
        return True
    
    # Obtener rol del usuario
    rol = obtener_rol_usuario(usuario)
    if not rol:
        return False
    
    # Verificar permiso en la matriz
    permisos_rol = PERMISOS_POR_ROL.get(rol, {})
    return permisos_rol.get(permiso, False)


def obtener_permisos_usuario(usuario):
    """
    Obtiene todos los permisos de un usuario.
    
    Args:
        usuario: Instancia de User
    
    Returns:
        dict: Diccionario con todos los permisos del usuario
    """
    if not usuario.is_authenticated:
        return {}
    
    if usuario.is_superuser:
        # Superusuarios tienen todos los permisos del ADMIN
        return {k: True for k in PERMISOS_POR_ROL['ADMIN'].keys()}
    
    rol = obtener_rol_usuario(usuario)
    if not rol:
        return {}
    
    return PERMISOS_POR_ROL.get(rol, {}).copy()


def usuario_es_rol(usuario, roles):
    """
    Verifica si el usuario tiene uno de los roles especificados.
    
    Args:
        usuario: Instancia de User
        roles: String o lista de roles permitidos
    
    Returns:
        bool: True si el usuario tiene uno de los roles
    """
    if not usuario.is_authenticated:
        return False
    
    if usuario.is_superuser:
        return True
    
    rol = obtener_rol_usuario(usuario)
    
    if isinstance(roles, str):
        roles = [roles]
    
    return rol in roles


def es_admin(usuario):
    """Verifica si el usuario es administrador."""
    return usuario.is_superuser or obtener_rol_usuario(usuario) == 'ADMIN'


def es_director(usuario):
    """Verifica si el usuario es director."""
    return obtener_rol_usuario(usuario) == 'DIRECTOR'


def es_supervisor(usuario):
    """Verifica si el usuario es supervisor."""
    return obtener_rol_usuario(usuario) == 'SUPERVISOR'


def es_estudiante(usuario):
    """Verifica si el usuario es estudiante."""
    return obtener_rol_usuario(usuario) == 'ESTUDIANTE'


def es_secretaria(usuario):
    """Verifica si el usuario es secretaria."""
    return obtener_rol_usuario(usuario) == 'SECRETARIA'


def es_externo(usuario):
    """Verifica si el usuario es externo (persona atendida)."""
    return obtener_rol_usuario(usuario) == 'EXTERNO'


def puede_ver_causa(usuario, causa):
    """
    Verifica si un usuario puede ver una causa específica.
    Considera restricciones por rol y asignación.
    
    Args:
        usuario: Instancia de User
        causa: Instancia de Causa
    
    Returns:
        bool: True si puede ver la causa
    """
    if usuario.is_superuser:
        return True
    
    rol = obtener_rol_usuario(usuario)
    
    # Admin, Director y Supervisor ven todas
    if rol in ['ADMIN', 'DIRECTOR', 'SUPERVISOR']:
        return True
    
    # Estudiante solo ve las que tiene asignadas
    if rol == 'ESTUDIANTE':
        return causa.responsable == usuario
    
    # Secretaria ve todas (lectura)
    if rol == 'SECRETARIA':
        return True
    
    # Externo solo ve sus propias causas
    if rol == 'EXTERNO':
        # Verificar si está relacionado con la causa
        from .models import CausaPersona, Persona
        try:
            persona = Persona.objects.get(email=usuario.email)
            return CausaPersona.objects.filter(causa=causa, persona=persona).exists()
        except Persona.DoesNotExist:
            return False
    
    return False


def puede_editar_causa(usuario, causa):
    """
    Verifica si un usuario puede editar una causa específica.
    
    Args:
        usuario: Instancia de User
        causa: Instancia de Causa
    
    Returns:
        bool: True si puede editar la causa
    """
    if usuario.is_superuser:
        return True
    
    rol = obtener_rol_usuario(usuario)
    
    # Solo Admin y Supervisor pueden editar causas
    if rol in ['ADMIN', 'SUPERVISOR']:
        # Supervisor solo edita las asignadas o donde es supervisor
        if rol == 'SUPERVISOR':
            return causa.responsable == usuario or causa.supervisor == usuario
        return True
    
    return False


# =============================================================================
# DECORADORES PARA VISTAS
# =============================================================================

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
            if not tiene_permiso(request.user, permiso):
                # Registrar intento de acceso denegado
                logger.warning(
                    f"Acceso denegado - Usuario: {request.user.username}, "
                    f"Permiso: {permiso}, "
                    f"Rol: {obtener_rol_usuario(request.user)}, "
                    f"Vista: {view_func.__name__}"
                )
                
                # Registrar en auditoría
                _registrar_acceso_denegado(request, permiso, view_func.__name__)
                
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
                    f"Acceso AJAX denegado - Usuario: {request.user.username}, "
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
            
            # Verificar que tenga perfil
            rol = obtener_rol_usuario(request.user)
            if not rol:
                messages.error(request, 'No tienes un rol asignado en el sistema.')
                return redirect('gestion:dashboard')
            
            # Verificar rol
            if rol not in roles_permitidos:
                logger.warning(
                    f"Acceso denegado por rol - Usuario: {request.user.username}, "
                    f"Rol: {rol}, Roles permitidos: {roles_permitidos}"
                )
                
                messages.error(
                    request,
                    'No tienes el rol necesario para acceder a esta sección.'
                )
                return redirect('gestion:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def solo_admin(view_func):
    """Decorador para vistas solo de administrador."""
    return solo_roles_permitidos('ADMIN')(view_func)


def solo_internos(view_func):
    """Decorador para vistas solo de usuarios internos (no externos)."""
    return solo_roles_permitidos('ADMIN', 'DIRECTOR', 'SUPERVISOR', 'ESTUDIANTE', 'SECRETARIA')(view_func)


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
        
        if self.permiso_requerido and not tiene_permiso(request.user, self.permiso_requerido):
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


# =============================================================================
# CONTEXT PROCESSOR PARA TEMPLATES
# =============================================================================

def permisos_context_processor(request):
    """
    Context processor para hacer disponibles los permisos en los templates.
    
    Uso en template:
        {% if permisos.puede_crear_causa %}
            <a href="...">Crear Causa</a>
        {% endif %}
    """
    if not request.user.is_authenticated:
        return {'permisos': {}, 'rol_usuario': None}
    
    return {
        'permisos': obtener_permisos_usuario(request.user),
        'rol_usuario': obtener_rol_usuario(request.user),
        'es_admin': es_admin(request.user),
        'es_externo': es_externo(request.user),
    }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def _registrar_acceso_denegado(request, permiso, vista):
    """Registra un intento de acceso denegado en la auditoría."""
    try:
        from .models import LogAuditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='OTRO',
            modelo='OTRO',
            descripcion=f'Acceso denegado: permiso "{permiso}" en vista "{vista}"',
            ip_address=_obtener_ip_cliente(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    except Exception as e:
        logger.error(f"Error al registrar acceso denegado: {e}")


def _obtener_ip_cliente(request):
    """Obtiene la IP real del cliente considerando proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
