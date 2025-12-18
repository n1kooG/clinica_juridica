"""
Módulo de compatibilidad para permisos.
Importa todo desde el sistema unificado en apps.gestion.permissions

NOTA: Este archivo existe solo para mantener compatibilidad con imports antiguos.
      Usar directamente apps.gestion.permissions para nuevos desarrollos.
"""

from apps.gestion.permissions import (
    # Constantes
    ROLES,
    PERMISOS_POR_ROL,
    
    # Funciones de verificación
    obtener_rol_usuario,
    tiene_permiso,
    obtener_permisos_usuario,
    usuario_es_rol,
    es_admin,
    es_director,
    es_supervisor,
    es_estudiante,
    es_secretaria,
    es_externo,
    puede_ver_causa,
    puede_editar_causa,
    
    # Decoradores
    permiso_requerido,
    permiso_requerido_ajax,
    solo_roles_permitidos,
    solo_admin,
    solo_internos,
    
    # Mixins
    PermisoRequeridoMixin,
    RolRequeridoMixin,
    
    # Context processor
    permisos_context_processor,
)

# Alias para compatibilidad con código antiguo
usuario_tiene_permiso = tiene_permiso
rol_requerido = solo_roles_permitidos
