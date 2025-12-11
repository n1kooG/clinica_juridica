"""
Vistas de autenticación del Sistema Clínica Jurídica
"""
from apps.gestion.models import LogAuditoria
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .rate_limit import login_limiter, get_client_ip


# =============================================================================
# PERFIL (existente)
# =============================================================================

@login_required
def perfil(request):
    return render(request, 'cuentas/perfil.html')


# =============================================================================
# AUTENTICACIÓN CON RATE LIMITING
# =============================================================================

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    # Obtener identificador (IP)
    ip_address = get_client_ip(request)
    action = 'login'
    
    # Verificar si está bloqueado
    if login_limiter.esta_bloqueado(ip_address, action):
        tiempo_restante = login_limiter.tiempo_restante_bloqueo(ip_address, action)
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        
        context = {
            'bloqueado': True,
            'tiempo_restante': tiempo_restante,
            'minutos': minutos,
            'segundos': segundos,
        }
        return render(request, 'registration/login.html', context)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login exitoso
            login(request, user)
            
            # Limpiar intentos fallidos
            login_limiter.limpiar(ip_address, action)
            
            # Registrar login en auditoría
            LogAuditoria.objects.create(
                usuario=user,
                accion='LOGIN',
                modelo='USER',
                objeto_id=user.id,
                descripcion=f'Inicio de sesión exitoso desde IP: {ip_address}'
            )
            
            # Inicializar sesión
            from django.utils import timezone
            request.session['last_activity'] = timezone.now().isoformat()
            request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            request.session['ip_address'] = ip_address
            request.session['login_time'] = timezone.now().isoformat()
            
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            
            next_url = request.GET.get('next', 'gestion:dashboard')
            return redirect(next_url)
        else:
            # Login fallido
            login_limiter.registrar_intento(ip_address, action)
            intentos = login_limiter.obtener_intentos(ip_address, action)
            intentos_restantes = login_limiter.max_intentos - intentos
            
            if intentos_restantes > 0:
                messages.error(
                    request, 
                    f'Usuario o contraseña incorrectos. Te quedan {intentos_restantes} intentos.'
                )
            else:
                messages.error(
                    request, 
                    'Demasiados intentos fallidos. Tu acceso ha sido bloqueado temporalmente.'
                )
    
    context = {
        'bloqueado': False,
    }
    return render(request, 'registration/login.html', context)


def logout_view(request):
    if request.user.is_authenticated:
        # Registrar logout en auditoría
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='LOGOUT',
            modelo='USER',
            objeto_id=request.user.id,
            descripcion=f'Cierre de sesión desde IP: {get_client_ip(request)}'
        )
    
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


def get_client_ip(request):
    """Obtiene la IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')