# Code Review — Clínica Jurídica USS
**Decisión: CHANGES_REQUESTED**
**Fecha:** 2026-04-14 | **Revisor:** Code Reviewer Senior — DevTeam OS

---

## Resumen Ejecutivo

El proyecto tiene una base arquitectónica razonable para un sistema interno universitario. Se aprecian esfuerzos genuinos en seguridad (rate limiting, auditoría, session middleware, cabeceras HTTP, validadores de contraseñas). Sin embargo, contiene issues de seguridad que deben resolverse antes de producción y deuda técnica estructural que impediría escalar a SaaS.

**Decisión NO es REJECTED** porque ningún issue es directamente explotable con el stack Django (ORM parameterizado, templates con escape automático, CSRF habilitado). Son configuraciones inseguras para producción y bugs latentes.

---

## CRITICAL — Bloquean producción

| ID | Archivo:Línea | Descripción |
|----|---------------|-------------|
| C-1 | `settings.py:5` | SECRET_KEY hardcodeada en repositorio |
| C-2 | `settings.py:7,9` | DEBUG=True, ALLOWED_HOSTS=[] |
| C-3 | `cuentas/views.py:80-81` | Open Redirect — parámetro `next` sin validar |
| C-4 | Toda la app | 0% cobertura de tests en sistema con datos sensibles |
| C-5 | `settings.py:55` | SESSION_COOKIE_SECURE=False hardcodeado |

---

## MAJOR — Changes Required

| ID | Archivo:Línea | Descripción |
|----|---------------|-------------|
| M-1 | `permissions.py:556` | `causa.supervisor` no existe → AttributeError para rol SUPERVISOR |
| M-2 | `views.py:99-108` | N+1 query en dashboard (query SQL por cada estado) |
| M-3 | `views.py:208-210, 324-326` | Decorators inconsistentes — causa_crear sin @permiso_requerido |
| M-4 | `urls.py:24-27` | 2 URL patterns duplicados (audiencias, causa_persona_crear) |
| M-5 | `signals.py:140` | `_pre_save_data` dict global no thread-safe → race condition en producción |
| M-6 | `views.py:682-764` | documento_crear ignora DocumentoForm; estado='PENDIENTE' inválido |
| M-7 | 6 archivos | `get_client_ip()` duplicada 6 veces (DRY violation) |
| M-8 | `views.py:1990` | consentimiento_revocar sin @permiso_requerido |
| M-9 | `views.py:472-499` | causa_persona_editar/eliminar sin autorización de objeto |
| M-10 | `settings.py` | MEDIA_ROOT y MEDIA_URL no configurados |
| M-11 | `signals.py:320` + `cuentas/views.py:63` | Login duplicado en LogAuditoria |
| M-12 | `settings.py:256` | LocMemCache incompatible con rate limiting multi-proceso |
| M-13 | Todos | Ausencia total de type annotations en Python 3.13 |
| M-14 | `views.py:1745, 1784` | int() sin try/except → ValueError no controlado |

---

## MINOR — Aprobados con comentarios

| ID | Archivo | Descripción |
|----|---------|-------------|
| m-1 | `messages.py` | Dead code — existe pero no se usa en las vistas |
| m-2 | `logging_utils.py` | Logging en archivo y LogAuditoria en DB no coordinados |
| m-3 | `views.py:969+` | Emojis hardcodeados en lógica de negocio (no en templates) |
| m-4 | `signals.py:93` | AuditoriaMiddleware vive en signals.py, no en middleware.py |
| m-5 | `decorators.py` | Módulo pass-through sin utilidad real |
| m-6 | `views.py:1615` | `rol` en admin_usuario_crear no validado contra ROL_CHOICES |

---

## Evaluación Arquitectónica

### ¿Sólido para SaaS multi-tenant?
**NO.** No hay concepto de tenant en los modelos. El campo `sede` en `Perfil` no propaga a `Causa`, `Persona`, `Audiencia`, `Documento`. Requiere modelo `Organizacion` con FK en todos los modelos de negocio y un `TenantMiddleware`.

### ¿Sistema de permisos robusto?
**PARCIALMENTE.** La matriz `PERMISOS_POR_ROL` es clara, los decoradores están bien implementados. Problemas: no se aplica consistentemente (ver M-3, M-8, M-9), `puede_editar_causa` referencia campo inexistente (M-1), sin tests de cobertura de permisos.

### ¿Queries eficientes?
**MAYORMENTE SÍ.** `select_related()` consistente en listas y detalles. Índices bien diseñados. Problema principal: N+1 en dashboard (M-2). Cache de catálogos bien diseñado pero no usado en causa_crear/editar.

### ¿Exportaciones Excel/PDF correctas?
**SÍ.** Correctamente implementadas con openpyxl y reportlab. Bien protegidas con @solo_roles_permitidos.

---

## Roadmap para convertir a SaaS

1. **Tenant Isolation** — Modelo `Organizacion` + `TenantMiddleware` + managers con filtro automático
2. **Settings por entorno** — `settings/base.py`, `settings/dev.py`, `settings/prod.py` con django-environ
3. **SQLite → PostgreSQL** — SQLite no soporta concurrencia write
4. **LocMemCache → Redis** — Necesario para rate limiting y cache multi-proceso
5. **Permisos por objeto** — django-guardian para permisos a nivel de instancia por tenant
6. **Tests mínimos viables** — Permisos por rol, validadores, login rate limiting, acceso por rol a causas
7. **Manejo de errores centralizado** — ErrorHandlerMixin en vez de try/except dispersos
8. **DRF + JWT** — Para app móvil o integración con sistemas del Poder Judicial

---

## Must Fix Before Deploy

1. Externalizar SECRET_KEY a variable de entorno
2. Condicionar DEBUG y ALLOWED_HOSTS a env vars
3. Corregir `causa.supervisor` → AttributeError en permissions.py:556
4. Corregir open redirect en login con url_has_allowed_host_and_scheme
5. Corregir `obtener_intentos()` no existe → HTTP 500 en login fallido
6. Corregir estado='PENDIENTE' inválido en documento_crear
7. Activar SESSION_COOKIE_SECURE condicionalmente
8. Configurar MEDIA_ROOT y MEDIA_URL
9. Agregar @permiso_requerido en consentimiento_revocar, causa_persona_editar/eliminar
10. Corregir URLs duplicadas en urls.py
