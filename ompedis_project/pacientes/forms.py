from django import forms
from .models import Paciente, Departamento, Municipio, Responsable, Servicio

class ResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        fields = ['nombre', 'apellido', 'parentesco', 'telefono']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Formato: 0000-0000'}),
        }

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido', 'id_partida_nacimiento', 'fecha_nacimiento', 'genero',
            'estado_activo', 'domicilio', 'departamento', 'municipio', 'diagnostico_medico', 'servicios', 'medicamentos'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'estado_activo': forms.CheckboxInput(attrs={'class': 'toggle-switch'}),
            'servicios': forms.CheckboxSelectMultiple(),
            'medicamentos': forms.Textarea(attrs={'placeholder': 'Lista los medicamentos separados por comas'}),
        }

    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), empty_label="Seleccione un Departamento")
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(), empty_label="Seleccione un Municipio")

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        if 'departamento' in self.data:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['municipio'].queryset = self.instance.departamento.municipio_set.order_by('nombre')
