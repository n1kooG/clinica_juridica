from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from .models import Persona, Causa, Audiencia, Documento, CausaPersona, LogAuditoria, EstadoCausa, Materia, Tribunal, TipoDocumento
from .forms import (
    PersonaForm, CausaForm, AudienciaForm,
    DocumentoForm, CausaPersonaForm
)
from apps.cuentas.permisos import permiso_requerido, rol_requerido, usuario_tiene_permiso

from datetime import datetime, timedelta, date
from django.utils import timezone

import calendar

# =============================================================================
# DASHBOARD
# =============================================================================

@login_required
def dashboard(request):
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_mes = hoy.replace(day=1)
    
    # Estadísticas generales
    total_causas = Causa.objects.count()
    total_personas = Persona.objects.count()
    total_documentos = Documento.objects.count()
    
    # Causas activas (no finalizadas)
    causas_activas = Causa.objects.exclude(
        estado__es_final=True
    ).count()
    
    # Causas finalizadas
    causas_finalizadas = Causa.objects.filter(
        estado__es_final=True
    ).count()
    
    # Tasa de cierre
    tasa_cierre = round((causas_finalizadas / total_causas * 100) if total_causas > 0 else 0)
    
    # Causas por estado
    causas_por_estado = []
    for estado in EstadoCausa.objects.filter(activo=True).order_by('orden'):
        count = Causa.objects.filter(estado=estado).count()
        causas_por_estado.append({
            'estado': estado,
            'count': count,
            'porcentaje': round((count / total_causas * 100) if total_causas > 0 else 0, 1)
        })
    
    # Audiencias de esta semana
    audiencias_semana = Audiencia.objects.filter(
        fecha_hora__date__gte=inicio_semana,
        fecha_hora__date__lte=fin_semana,
        estado__in=['PROGRAMADA', 'CONFIRMADA']
    ).select_related('causa').order_by('fecha_hora')[:10]
    
    # Audiencias de hoy
    audiencias_hoy = Audiencia.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['PROGRAMADA', 'CONFIRMADA']
    ).select_related('causa').order_by('fecha_hora')
    
    # Próximas audiencias (próximos 7 días)
    proximas_audiencias = Audiencia.objects.filter(
        fecha_hora__date__gte=hoy,
        fecha_hora__date__lte=hoy + timedelta(days=7),
        estado__in=['PROGRAMADA', 'CONFIRMADA']
    ).select_related('causa').order_by('fecha_hora')[:5]
    
    # Causas recientes (últimas 5 creadas)
    causas_recientes = Causa.objects.select_related(
        'tribunal', 'materia', 'estado'
    ).order_by('-fecha_creacion')[:5]
    
    # Personas recientes
    personas_recientes = Persona.objects.order_by('-fecha_registro')[:5]
    
    # Personas del mes
    personas_mes = Persona.objects.filter(fecha_registro__gte=inicio_mes).count()
    
    # Documentos recientes
    documentos_recientes = Documento.objects.select_related(
        'causa', 'tipo', 'usuario'
    ).order_by('-fecha_subida')[:5]
    
    # Actividad reciente (logs)
    actividad_reciente = LogAuditoria.objects.select_related(
        'usuario'
    ).order_by('-fecha')[:10]
    
    # Causas creadas este mes
    causas_mes = Causa.objects.filter(fecha_creacion__gte=inicio_mes).count()
    
    # Audiencias realizadas este mes
    audiencias_realizadas_mes = Audiencia.objects.filter(
        fecha_hora__date__gte=inicio_mes,
        estado='REALIZADA'
    ).count()
    
    context = {
        # Estadísticas
        'total_causas': total_causas,
        'total_personas': total_personas,
        'total_documentos': total_documentos,
        'causas_activas': causas_activas,
        'causas_finalizadas': causas_finalizadas,
        'tasa_cierre': tasa_cierre,
        'causas_mes': causas_mes,
        'personas_mes': personas_mes,
        'audiencias_realizadas_mes': audiencias_realizadas_mes,
        
        # Causas por estado
        'causas_por_estado': causas_por_estado,
        
        # Audiencias
        'audiencias_hoy': audiencias_hoy,
        'audiencias_semana': audiencias_semana,
        'proximas_audiencias': proximas_audiencias,
        
        # Recientes
        'causas_recientes': causas_recientes,
        'personas_recientes': personas_recientes,
        'documentos_recientes': documentos_recientes,
        'actividad_reciente': actividad_reciente,
        
        # Fechas
        'hoy': hoy,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
    }
    return render(request, 'gestion/dashboard.html', context)


# =============================================================================
# PERSONAS
# =============================================================================

@login_required
def personas_lista(request):
    personas = Persona.objects.all()
    context = {
        'personas': personas,
        'puede_crear': usuario_tiene_permiso(request.user, 'puede_crear_persona'),
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_persona'),
    }
    return render(request, 'gestion/personas_lista.html', context)


@permiso_requerido('puede_crear_persona')
def persona_crear(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona creada exitosamente.')
            return redirect('gestion:personas_lista')
    else:
        form = PersonaForm()
    return render(request, 'gestion/persona_form.html', {'form': form})


@permiso_requerido('puede_editar_persona')
def persona_editar(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona actualizada exitosamente.')
            return redirect('gestion:persona_detalle', pk=pk)
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'gestion/persona_form.html', {'form': form, 'persona': persona})

@login_required
def persona_detalle(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    
    causas_vinculadas = CausaPersona.objects.filter(
        persona=persona
    ).select_related('causa', 'causa__estado')
    
    actividad = LogAuditoria.objects.filter(
        modelo='PERSONA',
        objeto_id=persona.pk
    ).select_related('usuario').order_by('-fecha')[:5]
    
    context = {
        'persona': persona,
        'causas_vinculadas': causas_vinculadas,
        'actividad': actividad,
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_persona'),
    }
    return render(request, 'gestion/persona_detalle.html', context)


# =============================================================================
# CAUSAS
# =============================================================================

@login_required
def causas_lista(request):
    filtro = request.GET.get('filtro', 'activas')
    
    causas = Causa.objects.select_related(
        'tribunal', 'materia', 'estado', 'responsable'
    ).all()
    
    # Aplicar filtro
    if filtro == 'activas':
        causas = causas.exclude(estado__es_final=True)
    elif filtro == 'archivadas':
        causas = causas.filter(estado__es_final=True)
    # 'todas' no filtra
    
    causas = causas.order_by('-fecha_creacion')
    
    context = {
        'causas': causas,
        'filtro': filtro,
        'puede_crear': usuario_tiene_permiso(request.user, 'puede_crear_causa'),
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_causa'),
    }
    return render(request, 'gestion/causas_lista.html', context)


@permiso_requerido('puede_crear_causa')
def causa_crear(request):
    if request.method == 'POST':
        form = CausaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Causa creada exitosamente.')
            return redirect('gestion:causas_lista')
    else:
        form = CausaForm()
    
    context = {
        'form': form,
        'tribunales': Tribunal.objects.filter(activo=True).order_by('nombre'),
        'materias': Materia.objects.filter(activo=True).order_by('nombre'),
        'estados': EstadoCausa.objects.filter(activo=True).order_by('orden'),
        'responsables': User.objects.filter(is_active=True).order_by('first_name', 'username'),
    }
    return render(request, 'gestion/causa_form.html', context)


@permiso_requerido('puede_editar_causa')
def causa_editar(request, pk):
    causa = get_object_or_404(Causa, pk=pk)
    if request.method == 'POST':
        form = CausaForm(request.POST, instance=causa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Causa actualizada exitosamente.')
            return redirect('gestion:causa_detalle', pk=pk)
    else:
        form = CausaForm(instance=causa)
    
    context = {
        'form': form,
        'causa': causa,
        'tribunales': Tribunal.objects.filter(activo=True).order_by('nombre'),
        'materias': Materia.objects.filter(activo=True).order_by('nombre'),
        'estados': EstadoCausa.objects.filter(activo=True).order_by('orden'),
        'responsables': User.objects.filter(is_active=True).order_by('first_name', 'username'),
    }
    return render(request, 'gestion/causa_form.html', context)


@login_required
def causa_detalle(request, pk):
    causa = get_object_or_404(Causa, pk=pk)
    
    personas_asociadas = CausaPersona.objects.filter(
        causa=causa
    ).select_related('persona')
    
    audiencias = Audiencia.objects.filter(
        causa=causa
    ).order_by('-fecha_hora')
    
    documentos = Documento.objects.filter(
        causa=causa
    ).select_related('tipo', 'usuario').order_by('-fecha_subida')
    
    actividad = LogAuditoria.objects.filter(
        modelo='CAUSA',
        objeto_id=causa.pk
    ).select_related('usuario').order_by('-fecha')[:5]
    
    # Próxima audiencia
    proxima_audiencia = Audiencia.objects.filter(
        causa=causa,
        fecha_hora__gte=timezone.now(),
        estado__in=['PROGRAMADA', 'CONFIRMADA']
    ).order_by('fecha_hora').first()
    
    # Días desde ingreso
    dias_desde_ingreso = (date.today() - causa.fecha_creacion).days if causa.fecha_creacion else 0
    
    context = {
        'causa': causa,
        'personas_asociadas': personas_asociadas,
        'audiencias': audiencias,
        'documentos': documentos,
        'actividad': actividad,
        'proxima_audiencia': proxima_audiencia,
        'dias_desde_ingreso': dias_desde_ingreso,
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_causa'),
    }
    return render(request, 'gestion/causa_detalle.html', context)

@login_required
def causa_persona_crear(request):
    causa_preseleccionada = request.GET.get('causa', '')
    
    if request.method == 'POST':
        form = CausaPersonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona asociada a la causa exitosamente.')
            # Redirigir a la causa si venía de ahí
            causa_id = request.POST.get('causa')
            if causa_id:
                return redirect('gestion:causa_detalle', pk=causa_id)
            return redirect('gestion:causas_lista')
    else:
        form = CausaPersonaForm()
    
    context = {
        'form': form,
        'causas': Causa.objects.exclude(estado__es_final=True).order_by('-fecha_creacion'),
        'personas': Persona.objects.filter(activo=True).order_by('apellidos', 'nombres'),
        'causa_preseleccionada': causa_preseleccionada,
    }
    return render(request, 'gestion/causa_persona_form.html', context)


# =============================================================================
# AUDIENCIAS
# =============================================================================

@login_required
def audiencias_lista(request):
    filtro = request.GET.get('filtro', 'proximas')
    
    audiencias = Audiencia.objects.select_related(
        'causa', 'causa__tribunal'
    ).all()
    
    # Aplicar filtro
    if filtro == 'proximas':
        audiencias = audiencias.filter(
            fecha_hora__gte=timezone.now(),
            estado__in=['PROGRAMADA', 'CONFIRMADA']
        )
    elif filtro == 'realizadas':
        audiencias = audiencias.filter(estado='REALIZADA')
    elif filtro == 'suspendidas':
        audiencias = audiencias.filter(estado__in=['SUSPENDIDA', 'CANCELADA'])
    # 'todas' no filtra
    
    audiencias = audiencias.order_by('fecha_hora')
    
    context = {
        'audiencias': audiencias,
        'filtro': filtro,
        'puede_crear': usuario_tiene_permiso(request.user, 'puede_crear_audiencia'),
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_audiencia'),
    }
    return render(request, 'gestion/audiencias_lista.html', context)


@login_required
def audiencia_detalle(request, pk):
    audiencia = get_object_or_404(Audiencia, pk=pk)
    
    context = {
        'audiencia': audiencia,
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_audiencia'),
    }
    return render(request, 'gestion/audiencia_detalle.html', context)


@permiso_requerido('puede_crear_audiencia')
def audiencia_crear(request):
    causa_preseleccionada = request.GET.get('causa', '')
    
    if request.method == 'POST':
        form = AudienciaForm(request.POST)
        if form.is_valid():
            audiencia = form.save(commit=False)
            audiencia.creado_por = request.user
            audiencia.save()
            messages.success(request, 'Audiencia creada exitosamente.')
            return redirect('gestion:audiencias_lista')
    else:
        form = AudienciaForm()
    
    context = {
        'form': form,
        'causas': Causa.objects.exclude(estado__es_final=True).order_by('-fecha_creacion'),
        'causa_preseleccionada': causa_preseleccionada,
    }
    return render(request, 'gestion/audiencia_form.html', context)


@permiso_requerido('puede_editar_audiencia')
def audiencia_editar(request, pk):
    audiencia = get_object_or_404(Audiencia, pk=pk)
    
    if request.method == 'POST':
        form = AudienciaForm(request.POST, instance=audiencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Audiencia actualizada exitosamente.')
            return redirect('gestion:audiencia_detalle', pk=pk)
    else:
        form = AudienciaForm(instance=audiencia)
    
    context = {
        'form': form,
        'audiencia': audiencia,
        'causas': Causa.objects.all().order_by('-fecha_creacion'),
    }
    return render(request, 'gestion/audiencia_form.html', context)

# =============================================================================
# DOCUMENTOS
# =============================================================================

@login_required
def documentos_lista(request):
    filtro = request.GET.get('filtro', 'todos')
    
    documentos = Documento.objects.select_related(
        'causa', 'tipo', 'usuario'
    ).all()
    
    # Aplicar filtro por categoría del tipo
    if filtro == 'judicial_entrada':
        documentos = documentos.filter(tipo__categoria='JUDICIAL_ENTRADA')
    elif filtro == 'judicial_salida':
        documentos = documentos.filter(tipo__categoria='JUDICIAL_SALIDA')
    elif filtro == 'interno':
        documentos = documentos.filter(tipo__categoria='INTERNO')
    # 'todos' no filtra
    
    documentos = documentos.order_by('-fecha_subida')
    
    context = {
        'documentos': documentos,
        'filtro': filtro,
        'puede_crear': usuario_tiene_permiso(request.user, 'puede_subir_documento'),
    }
    return render(request, 'gestion/documentos_lista.html', context)


@login_required
def documento_detalle(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    
    context = {
        'documento': documento,
    }
    return render(request, 'gestion/documento_detalle.html', context)


@permiso_requerido('puede_subir_documento')
def documento_crear(request):
    causa_preseleccionada = request.GET.get('causa', '')
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.usuario = request.user
            documento.save()
            messages.success(request, 'Documento subido exitosamente.')
            # Redirigir a la causa si venía de ahí
            if causa_preseleccionada:
                return redirect('gestion:causa_detalle', pk=causa_preseleccionada)
            return redirect('gestion:documentos_lista')
    else:
        form = DocumentoForm()
    
    context = {
        'form': form,
        'causas': Causa.objects.all().order_by('-fecha_creacion'),
        'tipos_documento': TipoDocumento.objects.filter(activo=True).order_by('nombre'),
        'causa_preseleccionada': causa_preseleccionada,
    }
    return render(request, 'gestion/documento_form.html', context)


# =============================================================================
# RELACIÓN CAUSA - PERSONA
# =============================================================================

@permiso_requerido('puede_editar_causa')
def causa_persona_crear(request):
    if request.method == 'POST':
        form = CausaPersonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona asociada a la causa correctamente.')
            return redirect('gestion:causas_lista')
        else:
            messages.error(request, 'No se pudo asociar la persona. Revisa los errores del formulario.')
    else:
        form = CausaPersonaForm()
    return render(request, 'gestion/causa_persona_form.html', {'form': form, 'titulo': 'Asociar persona a causa'})


# =============================================================================
# BÚSQUEDA
# =============================================================================

@login_required
def buscar(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', 'todo')
    estado = request.GET.get('estado', '')
    materia = request.GET.get('materia', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    causas = []
    personas = []
    audiencias = []
    documentos = []
    
    if query or tipo != 'todo' or estado or materia or fecha_desde or fecha_hasta:
        # Búsqueda de causas
        if tipo in ['todo', 'causas']:
            causas = Causa.objects.select_related('tribunal', 'materia', 'estado', 'responsable')
            
            if query:
                causas = causas.filter(
                    Q(caratula__icontains=query) |
                    Q(rit__icontains=query) |
                    Q(ruc__icontains=query)
                )
            if estado:
                causas = causas.filter(estado_id=estado)
            if materia:
                causas = causas.filter(materia_id=materia)
            if fecha_desde:
                causas = causas.filter(fecha_creacion__gte=fecha_desde)
            if fecha_hasta:
                causas = causas.filter(fecha_creacion__lte=fecha_hasta)
            
            causas = causas[:50]
        
        # Búsqueda de personas
        if tipo in ['todo', 'personas']:
            personas = Persona.objects.all()
            
            if query:
                personas = personas.filter(
                    Q(nombres__icontains=query) |
                    Q(apellidos__icontains=query) |
                    Q(run__icontains=query) |
                    Q(email__icontains=query)
                )
            
            personas = personas[:50]
        
        # Búsqueda de audiencias
        if tipo in ['todo', 'audiencias']:
            audiencias = Audiencia.objects.select_related('causa')
            
            if query:
                audiencias = audiencias.filter(
                    Q(causa__caratula__icontains=query) |
                    Q(lugar__icontains=query)
                )
            if fecha_desde:
                audiencias = audiencias.filter(fecha_hora__date__gte=fecha_desde)
            if fecha_hasta:
                audiencias = audiencias.filter(fecha_hora__date__lte=fecha_hasta)
            
            audiencias = audiencias[:50]
        
        # Búsqueda de documentos
        if tipo in ['todo', 'documentos']:
            documentos = Documento.objects.select_related('causa', 'tipo')
            
            if query:
                documentos = documentos.filter(
                    Q(titulo__icontains=query) |
                    Q(descripcion__icontains=query) |
                    Q(numero_documento__icontains=query)
                )
            if fecha_desde:
                documentos = documentos.filter(fecha_subida__date__gte=fecha_desde)
            if fecha_hasta:
                documentos = documentos.filter(fecha_subida__date__lte=fecha_hasta)
            
            documentos = documentos[:50]
    
    # Obtener opciones para filtros
    estados = EstadoCausa.objects.filter(activo=True)
    materias = Materia.objects.filter(activo=True)
    
    total_resultados = len(causas) + len(personas) + len(audiencias) + len(documentos)
    
    context = {
        'query': query,
        'tipo': tipo,
        'causas': causas,
        'personas': personas,
        'audiencias': audiencias,
        'documentos': documentos,
        'estados': estados,
        'materias': materias,
        'total_resultados': total_resultados,
        'filtros': {
            'estado': estado,
            'materia': materia,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'gestion/buscar.html', context)

@rol_requerido('ADMIN', 'DIRECTOR')
def auditoria_lista(request):
    logs = LogAuditoria.objects.select_related('usuario').all()
    
    # Filtros
    usuario_id = request.GET.get('usuario', '')
    accion = request.GET.get('accion', '')
    modelo = request.GET.get('modelo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    if accion:
        logs = logs.filter(accion=accion)
    if modelo:
        logs = logs.filter(modelo=modelo)
    if fecha_desde:
        logs = logs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(fecha__date__lte=fecha_hasta)
    
    # Limitar a últimos 500 registros
    logs = logs[:500]
    
    # Obtener usuarios para el filtro
    usuarios = User.objects.filter(
        logs_auditoria__isnull=False
    ).distinct().order_by('username')
    
    context = {
        'logs': logs,
        'usuarios': usuarios,
        'acciones': LogAuditoria.ACCION_CHOICES,
        'modelos': LogAuditoria.MODELO_CHOICES,
        'filtros': {
            'usuario': usuario_id,
            'accion': accion,
            'modelo': modelo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'gestion/auditoria_lista.html', context)


@rol_requerido('ADMIN', 'DIRECTOR')
def auditoria_detalle(request, pk):
    log = get_object_or_404(LogAuditoria, pk=pk)
    context = {
        'log': log
    }
    return render(request, 'gestion/auditoria_detalle.html', context)

@login_required
def causa_linea_tiempo(request, pk):
    causa = get_object_or_404(Causa, pk=pk)
    
    eventos = []
    
    # Función auxiliar para convertir date a datetime
    def to_datetime(fecha):
        if isinstance(fecha, datetime):
            return fecha
        # Si es date, convertir a datetime al inicio del día
        return timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
    
    # Evento: Creación de la causa
    eventos.append({
        'fecha': to_datetime(causa.fecha_creacion),
        'tipo': 'CREACION',
        'titulo': 'Causa creada',
        'descripcion': f'Se registró la causa {causa.caratula}',
        'icono': '📁'
    })
    
    # Eventos: Documentos
    for doc in causa.documentos.all():
        eventos.append({
            'fecha': to_datetime(doc.fecha_subida),
            'tipo': 'DOCUMENTO',
            'titulo': f'Documento: {doc.titulo}',
            'descripcion': f'Tipo: {doc.tipo}' + (f' - Folio: {doc.folio}' if doc.folio else ''),
            'icono': '📄',
            'objeto': doc
        })
    
    # Eventos: Audiencias
    for aud in causa.audiencias.all():
        estado_texto = f' ({aud.get_estado_display()})' if aud.estado != 'PROGRAMADA' else ''
        eventos.append({
            'fecha': to_datetime(aud.fecha_hora),
            'tipo': 'AUDIENCIA',
            'titulo': f'{aud.get_tipo_evento_display()}{estado_texto}',
            'descripcion': f'Lugar: {aud.lugar or "Por definir"}',
            'icono': '📅',
            'objeto': aud
        })
    
    # Eventos: Logs de auditoría relacionados con la causa
    logs = LogAuditoria.objects.filter(
        modelo='CAUSA',
        objeto_id=causa.pk,
        accion__in=['EDITAR', 'CAMBIO_ESTADO', 'ASIGNAR']
    )
    for log in logs:
        eventos.append({
            'fecha': to_datetime(log.fecha),
            'tipo': 'CAMBIO',
            'titulo': log.get_accion_display(),
            'descripcion': log.descripcion or 'Modificación en la causa',
            'icono': '✏️'
        })
    
    # Ordenar por fecha descendente
    eventos.sort(key=lambda x: x['fecha'], reverse=True)
    
    context = {
        'causa': causa,
        'eventos': eventos,
        'puede_editar': usuario_tiene_permiso(request.user, 'puede_editar_causa'),
    }
    return render(request, 'gestion/causa_linea_tiempo.html', context)

@login_required
def calendario(request):
    # Obtener mes y año de los parámetros o usar el actual
    hoy = date.today()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))
    
    # Validar rango
    if mes < 1:
        mes = 12
        anio -= 1
    elif mes > 12:
        mes = 1
        anio += 1
    
    # Obtener primer y último día del mes
    primer_dia = date(anio, mes, 1)
    if mes == 12:
        ultimo_dia = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
    
    # Obtener audiencias del mes
    audiencias = Audiencia.objects.filter(
        fecha_hora__date__gte=primer_dia,
        fecha_hora__date__lte=ultimo_dia
    ).select_related('causa').order_by('fecha_hora')
    
    # Agrupar audiencias por día
    audiencias_por_dia = {}
    for aud in audiencias:
        dia = aud.fecha_hora.day
        if dia not in audiencias_por_dia:
            audiencias_por_dia[dia] = []
        audiencias_por_dia[dia].append(aud)
    
    # Generar calendario
    cal = calendar.Calendar(firstweekday=0)  # Lunes como primer día
    semanas = cal.monthdayscalendar(anio, mes)
    
    # Nombre del mes en español
    meses_es = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    # Navegación
    mes_anterior = mes - 1 if mes > 1 else 12
    anio_anterior = anio if mes > 1 else anio - 1
    mes_siguiente = mes + 1 if mes < 12 else 1
    anio_siguiente = anio if mes < 12 else anio + 1
    
    context = {
        'semanas': semanas,
        'audiencias_por_dia': audiencias_por_dia,
        'mes': mes,
        'anio': anio,
        'nombre_mes': meses_es[mes],
        'hoy': hoy,
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente,
        'puede_crear': usuario_tiene_permiso(request.user, 'puede_crear_audiencia'),
    }
    return render(request, 'gestion/calendario.html', context)

# =============================================================================
# REPORTES
# =============================================================================

@rol_requerido('ADMIN', 'DIRECTOR', 'SUPERVISOR')
def reportes(request):
    """Vista principal de reportes con filtros."""
    # Filtros
    estado_id = request.GET.get('estado', '')
    materia_id = request.GET.get('materia', '')
    tribunal_id = request.GET.get('tribunal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    responsable_id = request.GET.get('responsable', '')
    
    # Query base
    causas = Causa.objects.select_related(
        'tribunal', 'materia', 'estado', 'responsable'
    ).all()
    
    # Aplicar filtros
    if estado_id:
        causas = causas.filter(estado_id=estado_id)
    if materia_id:
        causas = causas.filter(materia_id=materia_id)
    if tribunal_id:
        causas = causas.filter(tribunal_id=tribunal_id)
    if fecha_desde:
        causas = causas.filter(fecha_creacion__gte=fecha_desde)
    if fecha_hasta:
        causas = causas.filter(fecha_creacion__lte=fecha_hasta)
    if responsable_id:
        causas = causas.filter(responsable_id=responsable_id)
    
    causas = causas.order_by('-fecha_creacion')
    
    # Estadísticas del reporte
    total = causas.count()
    por_estado = {}
    for estado in EstadoCausa.objects.filter(activo=True):
        por_estado[estado.nombre] = causas.filter(estado=estado).count()
    
    # Opciones para filtros
    estados = EstadoCausa.objects.filter(activo=True)
    materias = Materia.objects.filter(activo=True)
    tribunales = Tribunal.objects.filter(activo=True)
    responsables = User.objects.filter(is_active=True).order_by('first_name', 'username')
    
    context = {
        'causas': causas[:100],  # Limitar vista previa
        'total': total,
        'por_estado': por_estado,
        'estados': estados,
        'materias': materias,
        'tribunales': tribunales,
        'responsables': responsables,
        'filtros': {
            'estado': estado_id,
            'materia': materia_id,
            'tribunal': tribunal_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'responsable': responsable_id,
        }
    }
    return render(request, 'gestion/reportes.html', context)


@rol_requerido('ADMIN', 'DIRECTOR', 'SUPERVISOR')
def exportar_causas_excel(request):
    """Exporta causas a Excel con los filtros aplicados."""
    # Aplicar mismos filtros que en la vista de reportes
    estado_id = request.GET.get('estado', '')
    materia_id = request.GET.get('materia', '')
    tribunal_id = request.GET.get('tribunal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    responsable_id = request.GET.get('responsable', '')
    
    causas = Causa.objects.select_related(
        'tribunal', 'materia', 'estado', 'responsable'
    ).all()
    
    if estado_id:
        causas = causas.filter(estado_id=estado_id)
    if materia_id:
        causas = causas.filter(materia_id=materia_id)
    if tribunal_id:
        causas = causas.filter(tribunal_id=tribunal_id)
    if fecha_desde:
        causas = causas.filter(fecha_creacion__gte=fecha_desde)
    if fecha_hasta:
        causas = causas.filter(fecha_creacion__lte=fecha_hasta)
    if responsable_id:
        causas = causas.filter(responsable_id=responsable_id)
    
    causas = causas.order_by('-fecha_creacion')
    
    # Crear libro Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Causas"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Encabezados
    headers = [
        'RIT', 'RUC', 'Carátula', 'Tribunal', 'Materia', 
        'Estado', 'Responsable', 'Fecha Creación'
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Datos
    for row, causa in enumerate(causas, 2):
        ws.cell(row=row, column=1, value=causa.rit or '-').border = thin_border
        ws.cell(row=row, column=2, value=causa.ruc or '-').border = thin_border
        ws.cell(row=row, column=3, value=causa.caratula).border = thin_border
        ws.cell(row=row, column=4, value=str(causa.tribunal) if causa.tribunal else '-').border = thin_border
        ws.cell(row=row, column=5, value=str(causa.materia) if causa.materia else '-').border = thin_border
        ws.cell(row=row, column=6, value=causa.estado.nombre if causa.estado else '-').border = thin_border
        ws.cell(row=row, column=7, value=causa.responsable.get_full_name() if causa.responsable else '-').border = thin_border
        ws.cell(row=row, column=8, value=causa.fecha_creacion.strftime('%d/%m/%Y') if causa.fecha_creacion else '-').border = thin_border
    
    # Ajustar anchos de columna
    column_widths = [15, 20, 40, 30, 25, 15, 25, 15]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    
    # Preparar respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=causas_{date.today().strftime("%Y%m%d")}.xlsx'
    
    wb.save(response)
    return response

@rol_requerido('ADMIN', 'DIRECTOR', 'SUPERVISOR')
def exportar_causas_pdf(request):
    """Exporta causas a PDF con los filtros aplicados."""
    # Aplicar mismos filtros
    estado_id = request.GET.get('estado', '')
    materia_id = request.GET.get('materia', '')
    tribunal_id = request.GET.get('tribunal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    responsable_id = request.GET.get('responsable', '')
    
    causas = Causa.objects.select_related(
        'tribunal', 'materia', 'estado', 'responsable'
    ).all()
    
    if estado_id:
        causas = causas.filter(estado_id=estado_id)
    if materia_id:
        causas = causas.filter(materia_id=materia_id)
    if tribunal_id:
        causas = causas.filter(tribunal_id=tribunal_id)
    if fecha_desde:
        causas = causas.filter(fecha_creacion__gte=fecha_desde)
    if fecha_hasta:
        causas = causas.filter(fecha_creacion__lte=fecha_hasta)
    if responsable_id:
        causas = causas.filter(responsable_id=responsable_id)
    
    causas = causas.order_by('-fecha_creacion')[:100]  # Limitar a 100 para PDF
    
    # Crear respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=causas_{date.today().strftime("%Y%m%d")}.pdf'
    
    # Crear documento
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    elements.append(Paragraph("Reporte de Causas - Clínica Jurídica USS", title_style))
    
    # Fecha de generación
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=20
    )
    elements.append(Paragraph(f"Generado el {date.today().strftime('%d/%m/%Y')}", date_style))
    elements.append(Spacer(1, 20))
    
    # Datos de la tabla
    data = [['RIT', 'Carátula', 'Tribunal', 'Materia', 'Estado', 'Responsable', 'Fecha']]
    
    for causa in causas:
        data.append([
            causa.rit or '-',
            (causa.caratula[:30] + '...') if len(causa.caratula) > 30 else causa.caratula,
            (str(causa.tribunal)[:20] + '...') if causa.tribunal and len(str(causa.tribunal)) > 20 else str(causa.tribunal or '-'),
            (str(causa.materia)[:15] + '...') if causa.materia and len(str(causa.materia)) > 15 else str(causa.materia or '-'),
            causa.estado.nombre if causa.estado else '-',
            (causa.responsable.get_full_name()[:15] + '...') if causa.responsable and len(causa.responsable.get_full_name()) > 15 else (causa.responsable.get_full_name() if causa.responsable else '-'),
            causa.fecha_creacion.strftime('%d/%m/%Y') if causa.fecha_creacion else '-'
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[60, 120, 100, 80, 70, 90, 60])
    
    # Estilos de tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=1
    )
    elements.append(Paragraph(f"Total: {len(data) - 1} causas", footer_style))
    
    # Construir PDF
    doc.build(elements)
    
    return response

