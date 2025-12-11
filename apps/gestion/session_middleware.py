"""
Middleware de gestión de sesiones según ISO/IEC 27001
Requisitos: A.9.4.2 - Procedimiento seguro de entrada al sistema
"""

from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging

logger = logging.getLogger('seguridad')


class SessionTimeoutMiddleware:
    """
    Middleware para manejar timeout de sesión por inactividad.
    """
    
    # Tiempo máximo de inactividad (30 minutos)
    TIMEOUT_SECONDS = 1800
    
    # Tiempo de advertencia antes de expirar (2 minutos)
    WARNING_SECONDS = 120
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            
            # Obtener última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Convertir a datetime
                from datetime import datetime
                last_activity_time = datetime.fromisoformat(last_activity)
                last_activity_time = timezone.make_aware(last_activity_time) if timezone.is_naive(last_activity_time) else last_activity_time
                
                # Calcular tiempo inactivo
                inactive_seconds = (now - last_activity_time).total_seconds()
                
                # Si excede el timeout, cerrar sesión
                if inactive_seconds > self.TIMEOUT_SECONDS:
                    logger.info(
                        f"Sesión expirada por inactividad - "
                        f"Usuario: {request.user.username}, "
                        f"Inactividad: {int(inactive_seconds/60)} minutos"
                    )
                    
                    logout(request)
                    messages.warning(
                        request, 
                        'Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.'
                    )
                    return redirect(reverse('login'))
            
            # Actualizar última actividad
            request.session['last_activity'] = now.isoformat()
        
        response = self.get_response(request)
        return response


class SessionSecurityMiddleware:
    """
    Middleware para seguridad adicional de sesiones.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Verificar que la sesión tenga un user_agent consistente
            current_user_agent = request.META.get('HTTP_USER_AGENT', '')
            session_user_agent = request.session.get('user_agent', '')
            
            # Primera vez, guardar user_agent
            if not session_user_agent:
                request.session['user_agent'] = current_user_agent
                request.session['ip_address'] = self.get_client_ip(request)
                request.session['login_time'] = timezone.now().isoformat()
            else:
                # Verificar cambio de user_agent (posible secuestro de sesión)
                if session_user_agent != current_user_agent:
                    logger.warning(
                        f"Cambio de User-Agent detectado - "
                        f"Usuario: {request.user.username}, "
                        f"IP: {self.get_client_ip(request)}, "
                        f"Original: {session_user_agent[:50]}..., "
                        f"Actual: {current_user_agent[:50]}..."
                    )
                    
                    # Opcional: cerrar sesión por seguridad
                    # logout(request)
                    # return redirect(reverse('login'))
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')