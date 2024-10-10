# forms.py
from django import forms
from .models import Paciente, Municipio
from django.utils import timezone

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido', 'id_partida_nacimiento', 'fecha_nacimiento', 'genero',
            'estado_activo', 'domicilio', 'departamento', 'municipio', 'diagnostico_medico',
            'servicios', 'medicamentos',
            'responsable_nombre', 'responsable_apellido', 'responsable_parentesco', 'responsable_telefono'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d'
            ),
            'estado_activo': forms.CheckboxInput(attrs={'class': 'toggle-switch'}),
            'servicios': forms.CheckboxSelectMultiple(),
            'medicamentos': forms.Textarea(attrs={'placeholder': 'Lista los medicamentos separados por comas'}),
            'departamento': forms.Select(attrs={
                'hx-get': '/pacientes/cargar-municipios/',
                'hx-target': '#id_municipio',
                'hx-trigger': 'change'
            }),
            'responsable_telefono': forms.TextInput(attrs={'placeholder': 'Formato: 0000-0000'}),
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        if 'departamento' in self.data:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['municipio'].queryset = Municipio.objects.none()
        elif self.instance.pk:
            self.fields['municipio'].queryset = self.instance.departamento.municipio_set.order_by('nombre')
        else:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        return fecha
