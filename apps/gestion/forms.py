from django import forms
from .models import Persona, Causa, Audiencia, Documento, CausaPersona
import re
from django.core.exceptions import ValidationError

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['run', 'nombres', 'apellidos', 'email', 'telefono']
        widgets = {
            'run': forms.TextInput(attrs={'placeholder': '12.345.678-9', 'class': 'form-input'}),
            'nombres': forms.TextInput(attrs={'placeholder': 'Nombre(s)', 'class': 'form-input'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellido(s)', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.cl', 'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+56 9 1234 5678', 'class': 'form-input'}),
        }

    def clean_run(self):
        run = self.cleaned_data.get('run', '').strip()
        # Simple Chilean RUT pattern: digits with dots optional and dash + verifier
        pattern = r'^\d{1,3}(?:\.\d{3})*-?[0-9kK]$'
        if not re.match(pattern, run):
            raise ValidationError('Formato RUT inválido. Ej: 12.345.678-9')
        return run

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            # Allow digits, spaces, + and -
            if not re.match(r'^[\d\s\+\-\(\)]+$', telefono):
                raise ValidationError('Teléfono contiene caracteres inválidos.')
        return telefono

class CausaForm(forms.ModelForm):
    class Meta:
        model = Causa
        fields = ['rit', 'ruc', 'tribunal', 'materia', 'caratula', 'estado', 'responsable']

class AudienciaForm(forms.ModelForm):
    class Meta:
        model = Audiencia
        fields = ['causa', 'fecha_hora', 'tipo', 'lugar', 'observaciones']

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['causa', 'tipo', 'titulo', 'archivo', 'descripcion']

class CausaPersonaForm(forms.ModelForm):
    class Meta:
        model = CausaPersona
        fields = ['causa', 'persona', 'rol_en_causa']
