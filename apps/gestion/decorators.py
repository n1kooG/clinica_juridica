"""
Módulo de compatibilidad para decoradores.
Importa todo desde el sistema unificado en apps.gestion.permissions

NOTA: Este archivo existe solo para mantener compatibilidad con imports antiguos.
      Usar directamente apps.gestion.permissions para nuevos desarrollos.
"""

from .permissions import (
    # Decoradores
    permiso_requerido,
    permiso_requerido_ajax,
    solo_roles_permitidos,
    solo_admin,
    solo_internos,
    
    # Funciones auxiliares que pueden necesitar los decoradores
    tiene_permiso,
    obtener_rol_usuario,
)

# Re-exportar todo para compatibilidad
__all__ = [
    'permiso_requerido',
    'permiso_requerido_ajax',
    'solo_roles_permitidos',
    'solo_admin',
    'solo_internos',
    'tiene_permiso',
    'obtener_rol_usuario',
]
