"""
Validadores de contraseñas según ISO/IEC 27001
Requisitos: A.9.4.3 - Sistema de gestión de contraseñas
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class PasswordStrengthValidator:
    """
    Valida que la contraseña cumpla con requisitos mínimos de seguridad.
    
    Requisitos ISO 27001:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Opcional: un carácter especial
    """
    
    def __init__(self, min_length=8):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        errores = []
        
        if len(password) < self.min_length:
            errores.append(
                f"La contraseña debe tener al menos {self.min_length} caracteres."
            )
        
        if not re.search(r'[A-Z]', password):
            errores.append(
                "La contraseña debe contener al menos una letra mayúscula."
            )
        
        if not re.search(r'[a-z]', password):
            errores.append(
                "La contraseña debe contener al menos una letra minúscula."
            )
        
        if not re.search(r'\d', password):
            errores.append(
                "La contraseña debe contener al menos un número."
            )
        
        if errores:
            raise ValidationError(errores)
    
    def get_help_text(self):
        return _(
            f"Tu contraseña debe tener al menos {self.min_length} caracteres, "
            "incluyendo mayúsculas, minúsculas y números."
        )


class NoCommonPasswordValidator:
    """
    Valida que la contraseña no sea una contraseña común.
    """
    
    COMMON_PASSWORDS = [
        '12345678', 'password', '123456789', '12345', '1234567',
        'password1', 'qwerty', 'abc123', '111111', '123123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890',
        'chile123', 'chile2024', 'santiago', 'admin123',
    ]
    
    def validate(self, password, user=None):
        if password.lower() in self.COMMON_PASSWORDS:
            raise ValidationError(
                "Esta contraseña es muy común. Por favor elige una más segura.",
                code='password_too_common',
            )
    
    def get_help_text(self):
        return _("Tu contraseña no puede ser una contraseña común.")


class NoUserAttributeSimilarityValidator:
    """
    Valida que la contraseña no sea similar a información del usuario.
    """
    
    def validate(self, password, user=None):
        if not user:
            return
        
        password_lower = password.lower()
        
        # Verificar contra username
        if user.username and user.username.lower() in password_lower:
            raise ValidationError(
                "La contraseña no puede contener tu nombre de usuario.",
                code='password_too_similar',
            )
        
        # Verificar contra nombre
        if user.first_name and len(user.first_name) > 3:
            if user.first_name.lower() in password_lower:
                raise ValidationError(
                    "La contraseña no puede contener tu nombre.",
                    code='password_too_similar',
                )
        
        # Verificar contra apellido
        if user.last_name and len(user.last_name) > 3:
            if user.last_name.lower() in password_lower:
                raise ValidationError(
                    "La contraseña no puede contener tu apellido.",
                    code='password_too_similar',
                )
        
        # Verificar contra email
        if user.email:
            email_parts = user.email.split('@')[0].lower()
            if email_parts in password_lower:
                raise ValidationError(
                    "La contraseña no puede ser similar a tu correo electrónico.",
                    code='password_too_similar',
                )
    
    def get_help_text(self):
        return _(
            "Tu contraseña no puede ser similar a tu información personal."
        )


class PasswordHistoryValidator:
    """
    Valida que la contraseña no sea igual a las últimas N contraseñas.
    
    Nota: Requiere implementar historial de contraseñas en el modelo.
    Por ahora solo verifica que no sea igual a la actual.
    """
    
    def validate(self, password, user=None):
        if user and user.pk:
            # Verificar que no sea la misma contraseña actual
            if user.check_password(password):
                raise ValidationError(
                    "No puedes usar tu contraseña actual. Elige una diferente.",
                    code='password_used_before',
                )
    
    def get_help_text(self):
        return _(
            "Tu contraseña no puede ser igual a contraseñas anteriores."
        )