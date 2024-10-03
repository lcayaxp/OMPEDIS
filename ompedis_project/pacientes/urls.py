from django.urls import path
from . import views
from .views import exportar_pacientes_excel

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista_pacientes_view, name='lista_pacientes'),
    path('crear/', views.CrearPacienteView.as_view(), name='crear_paciente'),
    path('editar/<int:pk>/', views.EditarPacienteView.as_view(), name='editar_paciente'),
    path('cargar-municipios/', views.cargar_municipios, name='cargar_municipios'),
    path('detalle/<int:pk>/', views.PacienteDetailView.as_view(), name='detalle_paciente'),
    path('pacientes/cambiar-estado/', views.cambiar_estado_paciente_view, name='cambiar_estado_paciente'),
    path('confirmar-cambio-estado/<int:pk>/', views.confirmar_cambio_estado, name='confirmar_cambio_estado'),
    path('exportar/', exportar_pacientes_excel, name='exportar_pacientes'),
]