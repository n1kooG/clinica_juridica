"""
Rate Limiting para protección contra ataques de fuerza bruta
Cumple con ISO/IEC 27001 - Control de Acceso
"""

from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
import time


class RateLimiter:
    """
    Limitador de tasa de peticiones basado en cache.
    """
    
    def __init__(self, max_intentos=5, periodo_bloqueo=300, periodo_ventana=60):
        """
        Args:
            max_intentos: Número máximo de intentos permitidos
            periodo_bloqueo: Tiempo de bloqueo en segundos (default: 5 minutos)
            periodo_ventana: Ventana de tiempo para contar intentos (default: 1 minuto)
        """
        self.max_intentos = max_intentos
        self.periodo_bloqueo = periodo_bloqueo
        self.periodo_ventana = periodo_ventana
    
    def get_cache_key(self, identifier, action='default'):
        """Genera la clave de cache."""
        return f'rate_limit:{action}:{identifier}'
    
    def get_block_key(self, identifier, action='default'):
        """Genera la clave de bloqueo."""
        return f'rate_block:{action}:{identifier}'
    
    def esta_bloqueado(self, identifier, action='default'):
        """Verifica si el identificador está bloqueado."""
        block_key = self.get_block_key(identifier, action)
        return cache.get(block_key) is not None
    
    def tiempo_restante_bloqueo(self, identifier, action='default'):
        """Retorna el tiempo restante de bloqueo en segundos."""
        block_key = self.get_block_key(identifier, action)
        ttl = cache.ttl(block_key) if hasattr(cache, 'ttl') else None
        
        if ttl is None:
            # Fallback si el backend no soporta TTL
            block_data = cache.get(block_key)
            if block_data:
                return max(0, block_data.get('hasta', 0) - time.time())
        
        return ttl or 0
    
    def registrar_intento(self, identifier, action='default'):
        """
        Registra un intento y retorna si debe bloquearse.
        
        Returns:
            tuple: (bloqueado, intentos_restantes, tiempo_bloqueo)
        """
        # Verificar si ya está bloqueado
        if self.esta_bloqueado(identifier, action):
            tiempo = self.tiempo_restante_bloqueo(identifier, action)
            return True, 0, int(tiempo)
        
        cache_key = self.get_cache_key(identifier, action)
        
        # Obtener intentos actuales
        intentos = cache.get(cache_key, 0)
        intentos += 1
        
        # Guardar nuevo conteo
        cache.set(cache_key, intentos, self.periodo_ventana)
        
        # Verificar si excedió el límite
        if intentos >= self.max_intentos:
            # Bloquear
            block_key = self.get_block_key(identifier, action)
            cache.set(block_key, {
                'intentos': intentos,
                'hasta': time.time() + self.periodo_bloqueo
            }, self.periodo_bloqueo)
            
            # Limpiar contador
            cache.delete(cache_key)
            
            return True, 0, self.periodo_bloqueo
        
        return False, self.max_intentos - intentos, 0
    
    def limpiar(self, identifier, action='default'):
        """Limpia los contadores para un identificador (ej: después de login exitoso)."""
        cache_key = self.get_cache_key(identifier, action)
        block_key = self.get_block_key(identifier, action)
        cache.delete(cache_key)
        cache.delete(block_key)


# Instancia global del rate limiter para login
login_limiter = RateLimiter(
    max_intentos=5,        # 5 intentos
    periodo_bloqueo=300,   # 5 minutos de bloqueo
    periodo_ventana=60     # En una ventana de 1 minuto
)


def rate_limit_login(get_identifier=None):
    """
    Decorador para aplicar rate limiting a vistas de login.
    
    Args:
        get_identifier: Función que extrae el identificador del request
                       (default: usa IP del cliente)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Obtener identificador
            if get_identifier:
                identifier = get_identifier(request)
            else:
                identifier = get_client_ip(request)
            
            # Verificar bloqueo
            if login_limiter.esta_bloqueado(identifier, 'login'):
                tiempo = login_limiter.tiempo_restante_bloqueo(identifier, 'login')
                minutos = int(tiempo / 60) + 1
                
                from django.contrib import messages
                messages.error(
                    request, 
                    f'Demasiados intentos fallidos. Intenta nuevamente en {minutos} minuto(s).'
                )
                
                # Retornar a la página de login con el mensaje
                from django.shortcuts import render
                return render(request, 'registration/login.html', {
                    'bloqueado': True,
                    'tiempo_restante': tiempo,
                })
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_client_ip(request):
    """Obtiene la IP real del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')