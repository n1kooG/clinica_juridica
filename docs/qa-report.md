# QA Report — Clínica Jurídica Django
**Fecha:** 2026-04-14 | **Status: FAIL / NEEDS_WORK**
**Cobertura de tests estimada: 0%** — No existe ningún archivo tests.py en ninguna de las dos apps.

---

## BUGS CRÍTICOS

### BUG-01 — URLs duplicadas para audiencias
**`apps/gestion/urls.py:24-27`**
`audiencias/` definida dos veces, `audiencia_crear` registrado dos veces con paths distintos.  
`{% url 'gestion:audiencia_crear' %}` resuelve a `audiencias/crear/` pero `/audiencias/nueva/` queda sin name.  
**Fix:** Eliminar líneas 24-25, dejar solo 26-27.

### BUG-02 — URL duplicada para causa_persona_crear
**`apps/gestion/urls.py:19 y 35`**
Mismo name `causa_persona_crear` con dos paths distintos. Django resuelve al último (`relaciones/nueva/`).  
**Fix:** Eliminar línea 35 o darle name distinto.

### BUG-03 — @login_required duplicado
**`apps/gestion/views.py:439-440`**
`causa_persona_crear` tiene el decorador dos veces.  
**Fix:** Eliminar línea 439.

### BUG-04 — Orden incorrecto de decoradores
**`apps/gestion/views.py:208-210` y múltiples instancias**
`@permiso_requerido` ya incluye `@login_required` internamente. El `@login_required` externo es redundante.  
**Fix:** Eliminar todos los `@login_required` que acompañen a `@permiso_requerido`.

### BUG-05 — Documento creado con estado 'PENDIENTE' inválido
**`apps/gestion/views.py:736`**
```python
estado=request.POST.get('estado', 'PENDIENTE')
```
`'PENDIENTE'` no existe en `Documento.ESTADO_CHOICES` (válidos: BORRADOR, FINAL, ANULADO).  
**Fix:** Cambiar default a `'FINAL'`.

### BUG-06 — AttributeError: causa.supervisor no existe
**`apps/gestion/permissions.py:556`**
```python
return causa.responsable == usuario or causa.supervisor == usuario
```
El modelo `Causa` no tiene campo `supervisor`. Cada vez que un SUPERVISOR intenta editar una causa ajena lanza `AttributeError` → HTTP 500.  
**Fix:** Eliminar `or causa.supervisor == usuario`.

### BUG-07 — Open Redirect en login
**`apps/cuentas/views.py:80-81`**
Ver CRITICAL-04 del Security Report.

### BUG-08 — AttributeError: obtener_intentos() no existe en RateLimiter
**`apps/cuentas/views.py:85`**
El método `obtener_intentos` no está definido en `RateLimiter`. Lanza `AttributeError` en cada login fallido con intentos disponibles → HTTP 500.  
**Fix:** Agregar el método o reemplazar por:
```python
intentos = cache.get(login_limiter.get_cache_key(ip_address, action), 0)
```

### BUG-09 — LogAuditoria con modelo='USER' inválido
**`apps/cuentas/views.py:66 y 111`**
`modelo='USER'` no existe en `LogAuditoria.MODELO_CHOICES` (correcto: `'USUARIO'`).  
**Fix:** Cambiar `modelo='USER'` a `modelo='USUARIO'` en ambas líneas.

### BUG-10 — Doble registro de login en auditoría
**`apps/cuentas/views.py:63-69` y `apps/gestion/signals.py:320-331`**
El login se registra dos veces en `LogAuditoria`: una en la vista, otra por el signal.  
**Fix:** Eliminar el bloque `LogAuditoria.objects.create(...)` de cuentas/views.py.

### BUG-11 — Template usa campo inexistente causa.fecha_actualizacion
**`templates/gestion/causa_detalle.html:71`**
El modelo `Causa` no tiene `fecha_actualizacion`. Muestra siempre "Sin actualizar".  
**Fix:** Agregar `fecha_actualizacion = models.DateTimeField(auto_now=True)` al modelo, o eliminar del template.

### BUG-12 — admin_catalogo ordena EstadoCausa por 'nombre' en vez de 'orden'
**`apps/gestion/views.py:1718`**
`EstadoCausa` tiene campo `orden` para flujo procesal. El panel admin los muestra en orden alfabético.  
**Fix:** Respetar el `Meta.ordering` del modelo para EstadoCausa.

### BUG-13 — Doble importación en signals.py
**`apps/gestion/signals.py:1 y 5`**
Doble `from django.db.models.signals import post_save, post_delete`.  
**Fix:** Eliminar la línea duplicada.

### BUG-14 — PersonaForm.clean_run duplica validación más débil que el modelo
**`apps/gestion/forms.py:33-38`**
El regex en `clean_run` no valida dígito verificador. El modelo ya tiene `validar_rut_chileno`.  
**Fix:** Invocar `validar_rut_chileno(run)` dentro del `clean_run` o eliminarlo.

### BUG-15 — Sin verificación de doble revocación de consentimiento
**`apps/gestion/views.py:1996`**
No hay chequeo si el consentimiento ya está revocado antes de volver a revocarlo.  
**Fix:** `if consentimiento.fecha_revocacion: messages.warning(...); return redirect(...)`

### BUG-16 — auditoria_lista tiene doble verificación de permisos inconsistente
**`apps/gestion/views.py:870-878`**
Decorador `@permiso_requerido` + verificación manual interna con lista de roles distinta.

### BUG-17 — puede_editar_causa inconsistente con PERMISOS_POR_ROL
**`apps/gestion/permissions.py:536-559`**
La función acepta solo ADMIN/SUPERVISOR pero la matriz dice ESTUDIANTE tiene `puede_editar_causa=True`.

### BUG-18 — _pre_save_data dict global — race condition multi-thread
**`apps/gestion/signals.py:140`**
```python
_pre_save_data = {}
```
Dict global compartido entre threads. En producción multi-proceso los datos de auditoría se mezclan.  
**Fix:** Usar `threading.local()`.

### BUG-19 — validar_archivo no verifica magic bytes del archivo
**`apps/gestion/validators.py:276-283`**
Solo verifica extensión y content_type (ambos manipulables por el cliente).  
**Fix:** Usar `python-magic` para leer los primeros bytes.

### BUG-20 — validar_rut_chileno retorna True en vez de None
**`apps/gestion/validators.py:96`**
Convención Django: los validadores retornan `None` (no retornan nada) cuando son válidos.  
**Fix:** Cambiar `return True` por `return`.

### BUG-21 — guardar_perfil_usuario hace UPDATE innecesario en cada save de User
**`apps/cuentas/models.py:88-91`**
`instance.perfil.save()` en cada `post_save` de User genera escritura innecesaria en DB.

---

## Cobertura de Tests: 0%

Funcionalidades críticas sin ningún test:
- Validadores (RUT, teléfono, RIT, RUC)
- Sistema de permisos por rol
- CRUD de Personas, Causas, Audiencias, Documentos
- Login / Rate limiting / Session timeout
- Consentimientos
- Reportes Excel y PDF

---

## Prioridad de corrección

| Prioridad | Bugs |
|-----------|------|
| P0 — Antes de deploy | BUG-06, BUG-08, BUG-07, BUG-05 |
| P1 — Importante | BUG-01, BUG-02, BUG-09, BUG-10, BUG-18 |
| P2 — Medio plazo | BUG-03, BUG-04, BUG-11 a BUG-17 |
| P3 — Deuda técnica | BUG-19 a BUG-21 |
