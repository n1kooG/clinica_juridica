"""
Middleware de seguridad para el Sistema Clínica Jurídica
Cumple con ISO/IEC 27001 - Seguridad de la Información
"""

import re
from django.utils.deprecation import MiddlewareMixin


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    Middleware para detectar y registrar intentos de ataques XSS.
    
    NOTA: Django ya escapa automáticamente el contenido en los templates,
    por lo que no es necesario modificar los datos de entrada.
    Este middleware solo detecta y registra intentos sospechosos.
    """
    
    # Campos que NO deben ser verificados
    CAMPOS_EXCLUIDOS = [
        'password',
        'password1',
        'password2',
        'password_actual',
        'password_nueva',
        'password_confirmar',
        'csrfmiddlewaretoken',
        'token',
    ]
    
    # Patrones peligrosos a detectar
    PATRONES_PELIGROSOS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
    ]
    
    def contiene_patron_peligroso(self, valor):
        """Detecta si un valor contiene patrones peligrosos."""
        if not isinstance(valor, str):
            return False
        
        valor_lower = valor.lower()
        
        for patron in self.PATRONES_PELIGROSOS:
            if re.search(patron, valor_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def process_request(self, request):
        """Detecta posibles ataques XSS y los registra (sin modificar datos)."""
        
        # Verificar GET
        if request.GET:
            for key, value in request.GET.items():
                if key not in self.CAMPOS_EXCLUIDOS:
                    if self.contiene_patron_peligroso(value):
                        self.log_intento_xss(request, key, value)
        
        # Verificar POST
        if request.POST:
            for key, value in request.POST.items():
                if key not in self.CAMPOS_EXCLUIDOS:
                    if self.contiene_patron_peligroso(value):
                        self.log_intento_xss(request, key, value)
        
        return None
    
    def log_intento_xss(self, request, campo, valor):
        """Registra un intento de ataque XSS."""
        import logging
        logger = logging.getLogger('seguridad')
        
        logger.warning(
            f"Posible intento XSS detectado - "
            f"IP: {self.get_client_ip(request)}, "
            f"Usuario: {request.user}, "
            f"Campo: {campo}, "
            f"Valor: {valor[:100]}..."
        )
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad HTTP.
    """
    
    def process_response(self, request, response):
        # Prevenir clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevenir MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Habilitar protección XSS del navegador
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (básico)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        
        return response
