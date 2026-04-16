# Security Audit Report — Clínica Jurídica
**Fecha:** 2026-04-14 | **Auditor:** Security Engineer — DevTeam OS | **Stack:** Django 4.2.30 · SQLite · Python 3.13

## STATUS GENERAL: WARNING

No hay vulnerabilidades que bloqueen el ambiente de desarrollo académico actual, pero existen 5 hallazgos CRITICAL que deben resolverse obligatoriamente antes de cualquier despliegue en producción.

---

## Conteo de hallazgos

| Severidad | Cantidad |
|-----------|----------|
| CRITICAL  | 5        |
| WARNING   | 9        |
| INFO      | 3        |

---

## CRITICAL — Bloquean producción

### [CRITICAL-01] SECRET_KEY hardcodeada
**OWASP A02/A05 | `clinica_juridica/settings.py:5`**

```python
SECRET_KEY = 'cambia-esta-clave-en-produccion'
```
Valor predecible permite forjar cookies de sesión, tokens CSRF y password-reset links.  
**Fix:** `SECRET_KEY = os.environ['DJANGO_SECRET_KEY']`

---

### [CRITICAL-02] DEBUG=True y ALLOWED_HOSTS=[]
**OWASP A05 | `clinica_juridica/settings.py:7-9`**

`DEBUG=True` expone stack traces completos con SQL queries, variables de entorno y rutas del servidor.  
**Fix:** Condicionar ambos a variables de entorno.

---

### [CRITICAL-03] SESSION_COOKIE_SECURE=False
**OWASP A07 | `clinica_juridica/settings.py:55`**

Cookies de sesión transmitidas en claro sobre HTTP. También faltan `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` y `SECURE_HSTS_SECONDS`.  
**Fix:** `SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT = not DEBUG`

---

### [CRITICAL-04] Open Redirect en login — parámetro `next` sin validar
**OWASP A01 | `apps/cuentas/views.py:80-81`**

```python
next_url = request.GET.get('next', 'gestion:dashboard')
return redirect(next_url)
```
Acepta URLs absolutas externas: `/login/?next=https://evil.com`.  
**Fix:**
```python
from django.utils.http import url_has_allowed_host_and_scheme
next_url = request.GET.get('next', '')
if not url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
    next_url = 'gestion:dashboard'
```

---

### [CRITICAL-05] IDOR en vistas de consentimiento sin verificación de propiedad
**OWASP A01 | `apps/gestion/views.py` — consentimiento_detalle, consentimiento_editar, consentimiento_revocar**

Solo tienen `@login_required`. Un ESTUDIANTE puede iterar `/consentimiento/1/`, `/consentimiento/2/`... y ver/modificar consentimientos de personas ajenas.  
**Fix:** Agregar verificación de que la persona del consentimiento esté vinculada a una causa asignada al usuario.

---

## WARNING — Deben corregirse

### [WARNING-01] Logout acepta GET sin protección CSRF
`apps/cuentas/views.py:105` — Agregar `@require_POST`.

### [WARNING-02] Rate limiting solo por IP; cache in-memory no persiste reinicios
`apps/cuentas/rate_limit.py:17` — Complementar con username; migrar a Redis.

### [WARNING-03] Validación de archivos solo por extensión; upload de consentimientos sin validar
`apps/gestion/validators.py:267-283` — Usar python-magic para magic bytes. Aplicar `validar_archivo()` en consentimientos.

### [WARNING-04] IDOR en persona_detalle — ESTUDIANTE puede ver cualquier persona
`apps/gestion/views.py:238-268` — Agregar filtro por rol.

### [WARNING-05] IDOR en audiencia_detalle — ESTUDIANTE puede ver audiencias ajenas
`apps/gestion/views.py:551-559` — Agregar verificación de propiedad.

### [WARNING-06] Headers de producción ausentes: HSTS, SECURE_SSL_REDIRECT
`clinica_juridica/settings.py` — Configurar bloque completo de settings de producción.

### [WARNING-07] CSP con `unsafe-inline` — protección XSS anulada
`apps/gestion/middleware.py:113-114` — Implementar nonces para scripts inline.

### [WARNING-08] perfil_cambiar_password no usa AUTH_PASSWORD_VALIDATORS
`apps/gestion/views.py:1493-1498` — Llamar a `validate_password(password_nueva, user=request.user)`.

### [WARNING-09] ADMIN puede crear superusuarios desde la UI
`apps/gestion/views.py:1610` — Restringir a `request.user.is_superuser`.

---

## INFO

### [INFO-01] @login_required duplicado
`apps/gestion/views.py:439-440` — Sin impacto de seguridad.

### [INFO-02] Bug funcional: `login_limiter.obtener_intentos()` no existe
`apps/cuentas/views.py:85` — Genera AttributeError (HTTP 500) en login fallido.

### [INFO-03] Valores XSS se loguean — logs deben tener permisos restringidos
`apps/gestion/middleware.py:83`

---

## Verificaciones CORRECTAS

| Control | Estado |
|---------|--------|
| SQL Injection | LIMPIO — Solo ORM Django |
| Command Injection | LIMPIO — Sin os.system/subprocess/eval |
| SSRF | LIMPIO — Sin requests a URLs externas |
| CSRF en login | LIMPIO — @csrf_protect aplicado |
| XSS en templates | LIMPIO — Django auto-escapa |
| Hashing de contraseñas | LIMPIO — PBKDF2 + validators |
| Auditoría/Logging | LIMPIO — Signals completos + logs rotativos |
| Session timeout | LIMPIO — 30 min + expire at browser close |
| Componentes (A06) | LIMPIO — Sin CVEs conocidos |
| Permisos en causas (ESTUDIANTE) | LIMPIO |
| X-Frame-Options, X-Content-Type | LIMPIO |
