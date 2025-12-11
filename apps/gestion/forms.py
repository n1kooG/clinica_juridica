from django import forms
from .models import Persona, Causa, Audiencia, Documento, CausaPersona
import re
from django.core.exceptions import ValidationError

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'run', 'nombres', 'apellidos', 'tipo_persona',
            'fecha_nacimiento', 'genero', 'nacionalidad', 'estado_civil', 'ocupacion',
            'email', 'telefono', 'direccion', 'comuna', 'region',
            'es_vulnerable', 'vulnerabilidad',
            'requiere_representante', 'representante_nombre', 'representante_run', 'representante_telefono',
            'observaciones'
        ]
        widgets = {
            'run': forms.TextInput(attrs={'placeholder': '12.345.678-9', 'class': 'form-input'}),
            'nombres': forms.TextInput(attrs={'placeholder': 'Nombre(s)', 'class': 'form-input'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellido(s)', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.cl', 'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+56 9 1234 5678', 'class': 'form-input'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle, número, depto.', 'class': 'form-input'}),
            'comuna': forms.TextInput(attrs={'placeholder': 'Comuna', 'class': 'form-input'}),
            'vulnerabilidad': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'representante_nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo', 'class': 'form-input'}),
            'representante_run': forms.TextInput(attrs={'placeholder': '12.345.678-9', 'class': 'form-input'}),
            'representante_telefono': forms.TextInput(attrs={'placeholder': '+56 9 1234 5678', 'class': 'form-input'}),
        }

    def clean_run(self):
        run = self.cleaned_data.get('run', '').strip()
        pattern = r'^\d{1,3}(?:\.\d{3})*-?[0-9kK]$'
        if not re.match(pattern, run):
            raise ValidationError('Formato RUT inválido. Ej: 12.345.678-9')
        return run

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            if not re.match(r'^[\d\s\+\-\(\)]+$', telefono):
                raise ValidationError('Teléfono contiene caracteres inválidos.')
        return telefono

class CausaForm(forms.ModelForm):
    class Meta:
        model = Causa
        fields = ['rit', 'ruc', 'tribunal', 'materia', 'caratula', 'estado', 'responsable', 'descripcion', 'observaciones']

class AudienciaForm(forms.ModelForm):
    class Meta:
        model = Audiencia
        fields = [
            'causa', 'tipo_evento', 'fecha_hora', 'duracion_estimada',
            'lugar', 'sala', 'estado', 'observaciones'
        ]
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-input'},
                format='%Y-%m-%dT%H:%M'
            ),
            'duracion_estimada': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minutos'}),
            'lugar': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Juzgado de Familia de Santiago'}),
            'sala': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Sala 3'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora'].input_formats = ['%Y-%m-%dT%H:%M']

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            'causa', 'tipo', 'titulo', 'descripcion', 'archivo',
            'folio', 'fecha_emision', 'numero_documento', 'emisor',
            'estado', 'es_confidencial'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Título del documento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 1234-2024'}),
            'emisor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 1° Juzgado de Familia'}),
            'folio': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Número de folio'}),
        }
        
class CausaPersonaForm(forms.ModelForm):
    class Meta:
        model = CausaPersona
        fields = ['causa', 'persona', 'rol_en_causa']
