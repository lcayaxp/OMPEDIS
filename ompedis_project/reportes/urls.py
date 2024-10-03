from django.urls import path
from .views import registrar_sesion_view, ver_estadisticas_view, ver_listado_sesiones_view
from .views import generar_reporte_view, exportar_excel_view, historial_sesiones_view, SesionTerapiaUpdateView, SesionTerapiaDeleteView

urlpatterns = [
    path('registrar-sesion/', registrar_sesion_view, name='registrar_sesion'),
    path('estadisticas/', ver_estadisticas_view, name='ver_estadisticas'),
    path('estadisticas/listado-sesiones/', ver_listado_sesiones_view, name='listado_sesiones'),
    path('reportes/generar/', generar_reporte_view, name='generar_reporte'),
    path('exportar-excel/', exportar_excel_view, name='exportar_excel'),
    path('historial-sesiones/', historial_sesiones_view, name='historial_sesiones'),
    path('editar-sesion/<int:pk>/', SesionTerapiaUpdateView.as_view(), name='editar_sesion'),
    path('eliminar-sesion/<int:pk>/', SesionTerapiaDeleteView.as_view(), name='eliminar_sesion'),
]