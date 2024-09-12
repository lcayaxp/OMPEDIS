from django.urls import path
from .views import lista_pacientes_view, CrearPacienteView, EditarPacienteView, cargar_municipios, PacienteDetailView

app_name = 'pacientes'

urlpatterns = [
    path('', lista_pacientes_view, name='lista_pacientes'),
    path('crear/', CrearPacienteView.as_view(), name='crear_paciente'),
    path('editar/<int:pk>/', EditarPacienteView.as_view(), name='editar_paciente'),
    path('cargar-municipios/', cargar_municipios, name='cargar_municipios'),
    path('detalle/<int:pk>/', PacienteDetailView.as_view(), name='detalle_paciente'),
]