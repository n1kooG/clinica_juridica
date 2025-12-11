"""
Sistema de permisos granulares según ISO/IEC 27001
Requisitos: A.9.2.3 - Gestión de derechos de acceso de usuarios
"""

# Matriz de permisos por rol
PERMISOS_POR_ROL = {
    'ADMIN': {
        # Causas
        'puede_ver_causas': True,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_eliminar_causa': True,
        'puede_asignar_causa': True,
        
        # Personas
        'puede_ver_personas': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_eliminar_persona': True,
        
        # Audiencias
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': True,
        
        # Documentos
        'puede_ver_documentos': True,
        'puede_subir_documento': True,
        'puede_eliminar_documento': True,
        'puede_ver_documentos_confidenciales': True,
        
        # Reportes y Auditoría
        'puede_ver_reportes': True,
        'puede_exportar_reportes': True,
        'puede_ver_auditoria': True,
        
        # Administración
        'puede_gestionar_usuarios': True,
        'puede_gestionar_catalogos': True,
        'puede_ver_configuracion': True,
    },
    
    'DIRECTOR': {
        # Causas
        'puede_ver_causas': True,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': True,
        
        # Personas
        'puede_ver_personas': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_eliminar_persona': False,
        
        # Audiencias
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': False,
        
        # Documentos
        'puede_ver_documentos': True,
        'puede_subir_documento': True,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': True,
        
        # Reportes y Auditoría
        'puede_ver_reportes': True,
        'puede_exportar_reportes': True,
        'puede_ver_auditoria': True,
        
        # Administración
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': True,
        'puede_ver_configuracion': True,
    },
    
    'SUPERVISOR': {
        # Causas
        'puede_ver_causas': True,
        'puede_crear_causa': True,
        'puede_editar_causa': True,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': True,
        
        # Personas
        'puede_ver_personas': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_eliminar_persona': False,
        
        # Audiencias
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': False,
        
        # Documentos
        'puede_ver_documentos': True,
        'puede_subir_documento': True,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,
        
        # Reportes y Auditoría
        'puede_ver_reportes': True,
        'puede_exportar_reportes': False,
        'puede_ver_auditoria': False,
        
        # Administración
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_configuracion': False,
    },
    
    'ABOGADO': {
        # Causas
        'puede_ver_causas': True,
        'puede_crear_causa': False,
        'puede_editar_causa': True,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        
        # Personas
        'puede_ver_personas': True,
        'puede_crear_persona': True,
        'puede_editar_persona': True,
        'puede_eliminar_persona': False,
        
        # Audiencias
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': True,
        'puede_editar_audiencia': True,
        'puede_eliminar_audiencia': False,
        
        # Documentos
        'puede_ver_documentos': True,
        'puede_subir_documento': True,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,
        
        # Reportes y Auditoría
        'puede_ver_reportes': False,
        'puede_exportar_reportes': False,
        'puede_ver_auditoria': False,
        
        # Administración
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_configuracion': False,
    },
    
    'ALUMNO': {
        # Causas (solo las asignadas)
        'puede_ver_causas': True,
        'puede_crear_causa': False,
        'puede_editar_causa': False,
        'puede_eliminar_causa': False,
        'puede_asignar_causa': False,
        
        # Personas
        'puede_ver_personas': True,
        'puede_crear_persona': False,
        'puede_editar_persona': False,
        'puede_eliminar_persona': False,
        
        # Audiencias
        'puede_ver_audiencias': True,
        'puede_crear_audiencia': False,
        'puede_editar_audiencia': False,
        'puede_eliminar_audiencia': False,
        
        # Documentos
        'puede_ver_documentos': True,
        'puede_subir_documento': False,
        'puede_eliminar_documento': False,
        'puede_ver_documentos_confidenciales': False,
        
        # Reportes y Auditoría
        'puede_ver_reportes': False,
        'puede_exportar_reportes': False,
        'puede_ver_auditoria': False,
        
        # Administración
        'puede_gestionar_usuarios': False,
        'puede_gestionar_catalogos': False,
        'puede_ver_configuracion': False,
    },
}


def tiene_permiso(usuario, permiso):
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        usuario: Instancia de User
        permiso: String con el nombre del permiso
    
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    # Superusuarios tienen todos los permisos
    if usuario.is_superuser:
        return True
    
    # Obtener rol del usuario
    if not hasattr(usuario, 'perfil') or not usuario.perfil:
        return False
    
    rol = usuario.perfil.rol
    
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
    if usuario.is_superuser:
        # Superusuarios tienen todos los permisos
        return {k: True for k in PERMISOS_POR_ROL['ADMIN'].keys()}
    
    if not hasattr(usuario, 'perfil') or not usuario.perfil:
        return {}
    
    rol = usuario.perfil.rol
    return PERMISOS_POR_ROL.get(rol, {})