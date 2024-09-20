from django import forms
from .models import SesionTerapia
from pacientes.models import Paciente

class SesionTerapiaForm(forms.ModelForm):
    class Meta:
        model = SesionTerapia
        fields = ['paciente', 'diagnostico', 'area', 'fecha_sesion']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-control select2', 
                'style': 'width: 100%;',  # Asegura que el select tenga un ancho adecuado
                'data-live-search': 'true'  # Habilita el buscador
            }),
            'diagnostico': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.Select(choices=[('Neurología', 'Neurología'), ('Traumatología', 'Traumatología')], attrs={'class': 'form-control'}),
            'fecha_sesion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ReporteGeneracionForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    paciente = forms.ModelChoiceField(queryset=Paciente.objects.all(), required=False, label="Paciente")
