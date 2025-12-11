"""
Validadores Sistema Clínica Jurídica
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# =============================================================================
# VALIDADOR DE RUT CHILENO
# =============================================================================

def limpiar_rut(rut):
    """
    Limpia un RUT eliminando puntos, guiones y espacios.
    Retorna el RUT en formato sin puntos ni guión (ej: 12345678K)
    """
    if not rut:
        return ''
    return rut.replace('.', '').replace('-', '').replace(' ', '').upper()


def calcular_digito_verificador(rut_sin_dv):
    """
    Calcula el dígito verificador de un RUT chileno usando el algoritmo Módulo 11.
    """
    try:
        rut_numero = int(rut_sin_dv)
    except ValueError:
        return None
    
    suma = 0
    multiplicador = 2
    
    for digito in reversed(str(rut_numero)):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    
    resto = suma % 11
    dv = 11 - resto
    
    if dv == 11:
        return '0'
    elif dv == 10:
        return 'K'
    else:
        return str(dv)


def validar_rut_chileno(rut):
    """
    Valida un RUT chileno completo (con dígito verificador).
    Acepta formatos: 12.345.678-9, 12345678-9, 123456789
    """
    if not rut:
        return True  # Permitir vacío, usar required=True si es obligatorio
    
    rut_limpio = limpiar_rut(rut)
    
    if len(rut_limpio) < 2:
        raise ValidationError(
            _('El RUT debe tener al menos 2 caracteres.'),
            code='rut_muy_corto'
        )
    
    # Separar número y dígito verificador
    rut_numero = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    
    # Validar que el número sea numérico
    if not rut_numero.isdigit():
        raise ValidationError(
            _('El RUT debe contener solo números y un dígito verificador.'),
            code='rut_formato_invalido'
        )
    
    # Validar rango (1.000.000 - 99.999.999)
    rut_int = int(rut_numero)
    if rut_int < 1000000 or rut_int > 99999999:
        raise ValidationError(
            _('El RUT debe estar entre 1.000.000 y 99.999.999.'),
            code='rut_fuera_de_rango'
        )
    
    # Calcular y comparar dígito verificador
    dv_calculado = calcular_digito_verificador(rut_numero)
    
    if dv_ingresado != dv_calculado:
        raise ValidationError(
            _('El dígito verificador del RUT es inválido.'),
            code='rut_dv_invalido'
        )
    
    return True


def formatear_rut(rut):
    """
    Formatea un RUT al formato estándar: 12.345.678-9
    """
    rut_limpio = limpiar_rut(rut)
    
    if len(rut_limpio) < 2:
        return rut
    
    rut_numero = rut_limpio[:-1]
    dv = rut_limpio[-1]
    
    # Formatear con puntos
    rut_formateado = ''
    for i, digito in enumerate(reversed(rut_numero)):
        if i > 0 and i % 3 == 0:
            rut_formateado = '.' + rut_formateado
        rut_formateado = digito + rut_formateado
    
    return f'{rut_formateado}-{dv}'


# =============================================================================
# VALIDADOR DE TELÉFONO CHILENO
# =============================================================================

def validar_telefono_chileno(telefono):
    """
    Valida un número de teléfono chileno.
    Formatos aceptados:
    - +56 9 1234 5678
    - +56912345678
    - 912345678
    - 9 1234 5678
    """
    if not telefono:
        return True
    
    # Limpiar el teléfono
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    
    # Patrones válidos
    patrones = [
        r'^\+569\d{8}$',      # +56912345678
        r'^569\d{8}$',        # 56912345678
        r'^9\d{8}$',          # 912345678
        r'^\+562\d{8}$',      # +5621234567 (fijo Santiago)
        r'^2\d{8}$',          # 212345678 (fijo Santiago)
    ]
    
    for patron in patrones:
        if re.match(patron, telefono_limpio):
            return True
    
    raise ValidationError(
        _('Ingresa un número de teléfono chileno válido (ej: +56 9 1234 5678).'),
        code='telefono_invalido'
    )


def formatear_telefono(telefono):
    """
    Formatea un teléfono al formato estándar: +56 9 1234 5678
    """
    if not telefono:
        return ''
    
    telefono_limpio = re.sub(r'[\s\-\(\)\+]', '', telefono)
    
    # Si empieza con 56, ya tiene código de país
    if telefono_limpio.startswith('56'):
        telefono_limpio = telefono_limpio[2:]
    
    # Celular (9 dígitos empezando con 9)
    if len(telefono_limpio) == 9 and telefono_limpio.startswith('9'):
        return f'+56 {telefono_limpio[0]} {telefono_limpio[1:5]} {telefono_limpio[5:]}'
    
    # Fijo Santiago (9 dígitos empezando con 2)
    if len(telefono_limpio) == 9 and telefono_limpio.startswith('2'):
        return f'+56 {telefono_limpio[0]} {telefono_limpio[1:5]} {telefono_limpio[5:]}'
    
    return telefono


# =============================================================================
# VALIDADOR DE EMAIL
# =============================================================================

validar_email = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message=_('Ingresa una dirección de correo electrónico válida.'),
    code='email_invalido'
)


# =============================================================================
# VALIDADOR DE RIT/RUC
# =============================================================================

def validar_rit(rit):
    """
    Valida el formato de un RIT (Rol Interno del Tribunal).
    Formato esperado: C-1234-2024, V-567-2023, etc.
    """
    if not rit:
        return True
    
    patron = r'^[A-Za-z]{1,3}-\d{1,6}-\d{4}$'
    
    if not re.match(patron, rit.upper()):
        raise ValidationError(
            _('El RIT debe tener el formato: X-1234-2024 (letra-número-año).'),
            code='rit_formato_invalido'
        )
    
    return True


def validar_ruc(ruc):
    """
    Valida el formato de un RUC (Rol Único de Causa).
    Formato esperado: 2400123456-7
    """
    if not ruc:
        return True
    
    ruc_limpio = ruc.replace('-', '').replace(' ', '')
    
    # El RUC tiene 10 o 11 dígitos
    if not ruc_limpio.isdigit() or len(ruc_limpio) < 10 or len(ruc_limpio) > 11:
        raise ValidationError(
            _('El RUC debe tener entre 10 y 11 dígitos.'),
            code='ruc_formato_invalido'
        )
    
    return True


# =============================================================================
# VALIDADOR DE ARCHIVOS
# =============================================================================

ALLOWED_EXTENSIONS = {
    'documento': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
    'imagen': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'pdf': ['pdf'],
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validar_archivo(archivo, tipo='documento', max_size=None):
    """
    Valida un archivo subido por tipo y tamaño.
    """
    if not archivo:
        return True
    
    # Validar tamaño
    tamaño_maximo = max_size or MAX_FILE_SIZE
    if archivo.size > tamaño_maximo:
        tamaño_mb = tamaño_maximo / (1024 * 1024)
        raise ValidationError(
            _(f'El archivo no puede superar los {tamaño_mb:.0f} MB.'),
            code='archivo_muy_grande'
        )
    
    # Validar extensión
    extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
    extensiones_permitidas = ALLOWED_EXTENSIONS.get(tipo, ALLOWED_EXTENSIONS['documento'])
    
    if extension not in extensiones_permitidas:
        raise ValidationError(
            _(f'Tipo de archivo no permitido. Extensiones válidas: {", ".join(extensiones_permitidas)}.'),
            code='archivo_tipo_invalido'
        )
    
    # Validar que el contenido coincida con la extensión (básico)
    content_type = getattr(archivo, 'content_type', '')
    tipos_sospechosos = ['application/x-executable', 'application/x-msdownload']
    
    if content_type in tipos_sospechosos:
        raise ValidationError(
            _('El tipo de archivo no está permitido por razones de seguridad.'),
            code='archivo_peligroso'
        )
    
    return True


# =============================================================================
# VALIDADOR DE FECHAS
# =============================================================================

from datetime import date, timedelta


def validar_fecha_no_futura(fecha):
    """
    Valida que una fecha no sea futura.
    """
    if not fecha:
        return True
    
    if fecha > date.today():
        raise ValidationError(
            _('La fecha no puede ser futura.'),
            code='fecha_futura'
        )
    
    return True


def validar_fecha_no_muy_antigua(fecha, años=100):
    """
    Valida que una fecha no sea muy antigua.
    """
    if not fecha:
        return True
    
    fecha_limite = date.today() - timedelta(days=años * 365)
    
    if fecha < fecha_limite:
        raise ValidationError(
            _(f'La fecha no puede ser anterior a {años} años.'),
            code='fecha_muy_antigua'
        )
    
    return True


def validar_fecha_nacimiento(fecha):
    """
    Valida una fecha de nacimiento (no futura, no mayor a 120 años).
    """
    validar_fecha_no_futura(fecha)
    validar_fecha_no_muy_antigua(fecha, años=120)
    return True


def validar_fecha_audiencia(fecha):
    """
    Valida una fecha de audiencia (puede ser futura, pero no muy antigua).
    """
    if not fecha:
        return True
    
    # No puede ser más de 2 años en el pasado
    fecha_limite = date.today() - timedelta(days=2 * 365)
    
    if fecha < fecha_limite:
        raise ValidationError(
            _('La fecha de audiencia no puede ser tan antigua.'),
            code='fecha_audiencia_antigua'
        )
    
    return True


# =============================================================================
# SANITIZACIÓN DE TEXTO (XSS Prevention)
# =============================================================================

import html


def sanitizar_texto(texto):
    """
    Sanitiza texto para prevenir XSS.
    Escapa caracteres HTML peligrosos.
    """
    if not texto:
        return ''
    
    return html.escape(str(texto))


def sanitizar_html_basico(texto):
    """
    Sanitiza HTML permitiendo solo tags básicos seguros.
    """
    if not texto:
        return ''
    
    # Tags permitidos
    import re
    
    # Primero escapamos todo
    texto_escapado = html.escape(texto)
    
    # Luego permitimos algunos tags específicos
    tags_permitidos = ['b', 'i', 'u', 'strong', 'em', 'br', 'p']
    
    for tag in tags_permitidos:
        # Restaurar tags de apertura
        texto_escapado = re.sub(
            f'&lt;{tag}&gt;',
            f'<{tag}>',
            texto_escapado,
            flags=re.IGNORECASE
        )
        # Restaurar tags de cierre
        texto_escapado = re.sub(
            f'&lt;/{tag}&gt;',
            f'</{tag}>',
            texto_escapado,
            flags=re.IGNORECASE
        )
    
    return texto_escapado


# =============================================================================
# VALIDADOR DE CONTRASEÑA SEGURA
# =============================================================================

def validar_password_seguro(password):
    """
    Valida que una contraseña cumpla con requisitos de seguridad.
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    """
    if not password:
        raise ValidationError(
            _('La contraseña es requerida.'),
            code='password_vacio'
        )
    
    errores = []
    
    if len(password) < 8:
        errores.append('Mínimo 8 caracteres')
    
    if not re.search(r'[A-Z]', password):
        errores.append('Al menos una mayúscula')
    
    if not re.search(r'[a-z]', password):
        errores.append('Al menos una minúscula')
    
    if not re.search(r'\d', password):
        errores.append('Al menos un número')
    
    if errores:
        raise ValidationError(
            _('La contraseña debe tener: ') + ', '.join(errores),
            code='password_debil'
        )
    
    return True