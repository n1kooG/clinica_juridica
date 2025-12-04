from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Persona, Causa, Audiencia, Documento, CausaPersona
from .forms import (
    PersonaForm, CausaForm, AudienciaForm,
    DocumentoForm, CausaPersonaForm
)

@login_required
def dashboard(request):
    causas = Causa.objects.all()[:5]
    personas = Persona.objects.all()[:5]
    audiencias = Audiencia.objects.all()[:5]
    context = {
        'total_causas': Causa.objects.count(),
        'total_personas': Persona.objects.count(),
        'total_audiencias': Audiencia.objects.count(),
        'causas_recientes': causas,
        'personas_recientes': personas,
        'audiencias_recientes': audiencias,
    }
    return render(request, 'gestion/dashboard.html', context)

# PERSONAS

@login_required
def personas_lista(request):
    personas = Persona.objects.all()
    return render(request, 'gestion/personas_lista.html', {'personas': personas})

@login_required
def persona_crear(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona creada correctamente.')
            return redirect('gestion:personas_lista')
        else:
            # informar al usuario que el formulario tiene errores
            messages.error(request, 'No se pudo crear la persona. Revisa los errores del formulario.')
    else:
        form = PersonaForm()
    return render(request, 'gestion/persona_form.html', {'form': form, 'titulo': 'Nueva persona'})

@login_required
def persona_editar(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados en la persona.')
            return redirect('gestion:personas_lista')
        else:
            messages.error(request, 'No se pudieron guardar los cambios. Revisa los errores del formulario.')
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'gestion/persona_form.html', {'form': form, 'titulo': 'Editar persona'})

# CAUSAS

@login_required
def causas_lista(request):
    causas = Causa.objects.all()
    return render(request, 'gestion/causas_lista.html', {'causas': causas})

@login_required
def causa_crear(request):
    if request.method == 'POST':
        form = CausaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion:causas_lista')
    else:
        form = CausaForm()
    return render(request, 'gestion/causa_form.html', {'form': form, 'titulo': 'Nueva causa'})

@login_required
def causa_editar(request, pk):
    causa = get_object_or_404(Causa, pk=pk)
    if request.method == 'POST':
        form = CausaForm(request.POST, instance=causa)
        if form.is_valid():
            form.save()
            return redirect('gestion:causa_detalle', pk=causa.pk)
    else:
        form = CausaForm(instance=causa)
    return render(request, 'gestion/causa_form.html', {'form': form, 'titulo': 'Editar causa'})

@login_required
def causa_detalle(request, pk):
    causa = get_object_or_404(Causa, pk=pk)
    relaciones = CausaPersona.objects.filter(causa=causa)
    audiencias = causa.audiencias.all()
    documentos = causa.documentos.all()
    return render(request, 'gestion/causa_detalle.html', {
        'causa': causa,
        'relaciones': relaciones,
        'audiencias': audiencias,
        'documentos': documentos,
    })

# AUDIENCIAS

@login_required
def audiencias_lista(request):
    audiencias = Audiencia.objects.select_related('causa')
    return render(request, 'gestion/audiencias_lista.html', {'audiencias': audiencias})

@login_required
def audiencia_crear(request):
    if request.method == 'POST':
        form = AudienciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion:audiencias_lista')
    else:
        form = AudienciaForm()
    return render(request, 'gestion/audiencia_form.html', {'form': form, 'titulo': 'Nueva audiencia'})

# DOCUMENTOS

@login_required
def documentos_lista(request):
    documentos = Documento.objects.select_related('causa', 'usuario')
    return render(request, 'gestion/documentos_lista.html', {'documentos': documentos})

@login_required
def documento_crear(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.usuario = request.user
            doc.save()
            return redirect('gestion:documentos_lista')
    else:
        form = DocumentoForm()
    return render(request, 'gestion/documento_form.html', {'form': form, 'titulo': 'Subir documento'})

# RELACIÓN CAUSA - PERSONA

@login_required
def causa_persona_crear(request):
    if request.method == 'POST':
        form = CausaPersonaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion:causas_lista')
    else:
        form = CausaPersonaForm()
    return render(request, 'gestion/causa_persona_form.html', {'form': form, 'titulo': 'Asociar persona a causa'})

# BÚSQUEDA

@login_required
def buscar(request):
    query = request.GET.get('q', '').strip()
    causas = []
    personas = []
    if query:
        causas = Causa.objects.filter(
            Q(caratula__icontains=query) |
            Q(rit__icontains=query) |
            Q(ruc__icontains=query)
        )
        personas = Persona.objects.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(run__icontains=query)
        )
    context = {
        'query': query,
        'causas': causas,
        'personas': personas,
    }
    return render(request, 'gestion/buscar.html', context)
