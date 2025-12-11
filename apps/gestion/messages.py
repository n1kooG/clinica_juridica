"""
Mensajes del sistema - Centralizados para consistencia
Cumple con ISO/IEC 25010 - Usabilidad
"""

# =============================================================================
# MENSAJES DE ÉXITO
# =============================================================================

SUCCESS_MESSAGES = {
    # Personas
    'persona_creada': 'La persona ha sido registrada exitosamente.',
    'persona_actualizada': 'Los datos de la persona han sido actualizados.',
    'persona_eliminada': 'La persona ha sido eliminada del sistema.',
    
    # Causas
    'causa_creada': 'La causa ha sido creada exitosamente.',
    'causa_actualizada': 'Los datos de la causa han sido actualizados.',
    'causa_eliminada': 'La causa ha sido eliminada del sistema.',
    
    # Audiencias
    'audiencia_creada': 'La audiencia ha sido programada exitosamente.',
    'audiencia_actualizada': 'Los datos de la audiencia han sido actualizados.',
    'audiencia_eliminada': 'La audiencia ha sido eliminada.',
    
    # Documentos
    'documento_subido': 'El documento ha sido subido exitosamente.',
    'documento_actualizado': 'El documento ha sido actualizado.',
    'documento_eliminado': 'El documento ha sido eliminado.',
    
    # Usuarios
    'usuario_creado': 'El usuario ha sido creado exitosamente.',
    'usuario_actualizado': 'Los datos del usuario han sido actualizados.',
    'usuario_activado': 'El usuario ha sido activado.',
    'usuario_desactivado': 'El usuario ha sido desactivado.',
    'password_cambiado': 'Tu contraseña ha sido actualizada exitosamente.',
    'perfil_actualizado': 'Tu perfil ha sido actualizado.',
    
    # Sesión
    'login_exitoso': 'Has iniciado sesión correctamente.',
    'logout_exitoso': 'Has cerrado sesión correctamente.',
}


# =============================================================================
# MENSAJES DE ERROR
# =============================================================================

ERROR_MESSAGES = {
    # Validación
    'campo_requerido': 'Este campo es obligatorio.',
    'rut_invalido': 'El RUT ingresado no es válido.',
    'email_invalido': 'El correo electrónico no es válido.',
    'telefono_invalido': 'El número de teléfono no es válido.',
    'fecha_invalida': 'La fecha ingresada no es válida.',
    
    # Archivos
    'archivo_muy_grande': 'El archivo excede el tamaño máximo permitido (10 MB).',
    'tipo_archivo_invalido': 'El tipo de archivo no está permitido.',
    'archivo_requerido': 'Debes seleccionar un archivo.',
    
    # Autenticación
    'credenciales_invalidas': 'Usuario o contraseña incorrectos.',
    'cuenta_inactiva': 'Tu cuenta está desactivada. Contacta al administrador.',
    'sesion_expirada': 'Tu sesión ha expirado. Inicia sesión nuevamente.',
    'demasiados_intentos': 'Demasiados intentos fallidos. Intenta más tarde.',
    
    # Permisos
    'sin_permiso': 'No tienes permisos para realizar esta acción.',
    'acceso_denegado': 'Acceso denegado a este recurso.',
    
    # Contraseñas
    'password_actual_incorrecto': 'La contraseña actual es incorrecta.',
    'passwords_no_coinciden': 'Las contraseñas no coinciden.',
    'password_muy_corto': 'La contraseña debe tener al menos 8 caracteres.',
    'password_sin_mayuscula': 'La contraseña debe tener al menos una mayúscula.',
    'password_sin_minuscula': 'La contraseña debe tener al menos una minúscula.',
    'password_sin_numero': 'La contraseña debe tener al menos un número.',
    
    # Datos
    'registro_no_encontrado': 'El registro solicitado no existe.',
    'registro_duplicado': 'Ya existe un registro con estos datos.',
    'no_se_puede_eliminar': 'No se puede eliminar este registro porque tiene datos asociados.',
    
    # Sistema
    'error_servidor': 'Ha ocurrido un error. Intenta nuevamente.',
    'operacion_fallida': 'No se pudo completar la operación.',
}


# =============================================================================
# MENSAJES DE ADVERTENCIA
# =============================================================================

WARNING_MESSAGES = {
    'sin_resultados': 'No se encontraron resultados para tu búsqueda.',
    'datos_incompletos': 'Algunos datos están incompletos.',
    'confirmar_eliminacion': '¿Estás seguro de que deseas eliminar este registro?',
    'cambios_sin_guardar': 'Tienes cambios sin guardar. ¿Deseas continuar?',
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_success_message(key, **kwargs):
    """Obtiene un mensaje de éxito formateado."""
    message = SUCCESS_MESSAGES.get(key, 'Operación completada exitosamente.')
    return message.format(**kwargs) if kwargs else message


def get_error_message(key, **kwargs):
    """Obtiene un mensaje de error formateado."""
    message = ERROR_MESSAGES.get(key, 'Ha ocurrido un error.')
    return message.format(**kwargs) if kwargs else message


def get_warning_message(key, **kwargs):
    """Obtiene un mensaje de advertencia formateado."""
    message = WARNING_MESSAGES.get(key, 'Atención.')
    return message.format(**kwargs) if kwargs else message